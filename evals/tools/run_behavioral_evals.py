#!/usr/bin/env python3
"""Tier 3 - behavioral evals runner. LOCAL-ONLY: needs an authenticated
`claude` CLI (executor) and codex CLI (cross-vendor grader) on PATH; CI has
neither, so CI only runs `--list` as a self-test.

Each case in evals/<skill>/evals.json runs in a throwaway workspace built
from its `setup` config (synthetic References/ fixture in, codex stripped
from PATH for degraded cases), executes headless via `claude -p` with a
scoped tool allowlist, and is then graded expectation-by-expectation by an
independent model (GPT-5.6 Sol via codex by default - the executor's vendor
never grades itself).

    python run_behavioral_evals.py --list                 # CI self-test
    python run_behavioral_evals.py                        # run all
    python run_behavioral_evals.py --case degraded-consent-gate
    python run_behavioral_evals.py --model fable          # full-realism run

Cases with setup.manual are reported SKIPPED(manual) - they need state a
fixture cannot fake (e.g. an implemented branch with a frozen plan).

IMPORTANT: the executor loads the INSTALLED plugin, not this checkout -
after editing the skill, bump .claude-plugin/plugin.json and run
`claude plugin update crosscheck@crosscheck` before re-running, or you will
behaviorally test the stale cached copy.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVALS_ROOT = HERE.parent
PLUGIN_ROOT = EVALS_ROOT.parent
SKILL = "multi-model-verify"
CASES_FILE = EVALS_ROOT / SKILL / "evals.json"
FIXTURE_REPO = EVALS_ROOT / SKILL / "fixtures" / "fixture-repo"

HARNESS_PREAMBLE = (
    "TEST HARNESS RUN. Follow the multi-model-verify skill exactly as"
    " written for the request below, with these test constraints: cap any"
    " debate at ONE exchange; do not create or modify files outside this"
    " workspace; report-only (no frozen plan file). This run is UNATTENDED:"
    " no user can answer questions during or after it. End with the skill's"
    " finish line.\n\nRequest: "
)

# Two layers (Sol reviews 2026-07-12/13). AVAILABLE_TOOLS (--tools) is
# availability: tools not listed (Write, Edit, Agent, WebFetch, ...) do
# not exist for the executor, so ambient user-scope allow rules cannot
# widen the harness. ALLOWED_TOOLS (--allowedTools) is approval within
# that set: direct codex invocations plus READ-ONLY git inspection - no
# cat/ls redirection (`cat x > fixture` could overwrite the evidence the
# agent then cites), no git write verbs; anything else falls to a
# permission prompt, which a headless run denies.
#
# The read-only git verbs are what make diff mode gradable AT ALL: without
# them the executor cannot open base..head, so a "reviewed the diff" claim
# could never be distinguished from a working-tree read (Sol review
# 2026-07-13). The diff case plants a decoy to force the distinction.
#
# Read is cwd-scoped with Read(**), mirroring the drift triage agent
# (tools/check-drift.ps1): THIS file ships in the installed plugin cache
# and contains the frozen plan and the planted implementation, so an
# unscoped Read let an executor learn the diff case's answer from the
# harness source instead of the committed range (Sol review 2026-07-16).
# Residual (accepted on the record, same as the drift agent): Grep approval
# is unscoped - the load-bearing counter is the diff case's expectation,
# which demands a range-read tool RESULT showing the planted line, so
# out-of-tree knowledge alone can no longer satisfy the grader.
AVAILABLE_TOOLS = "Skill,Read,Glob,Grep,Bash,PowerShell"
ALLOWED_TOOLS = (
    "Skill,Read(**),Glob,Grep,"
    "Bash(codex:*),PowerShell(codex:*),"
    "Bash(git diff:*),Bash(git log:*),Bash(git show:*)"
)

GRADER_PROMPT = """<role>Independent grader in a two-model verification
protocol. Judge ONLY from the transcript; do not assume unstated work
happened.</role>
<task>For each numbered expectation, decide from the transcript whether the
agent's behavior met it.</task>
<expectations>
{expectations}
</expectations>
<expected-outcome>{expected}</expected-outcome>
<transcript>
{transcript}
</transcript>
<output>Reply with ONLY a JSON array, one object per expectation, in order:
[{{"expectation": 1, "met": true, "evidence": "one line"}}, ...]</output>
"""


def load_cases():
    data = json.loads(CASES_FILE.read_text(encoding="utf-8"))
    return data["evals"]


FROZEN_PLAN = """# Port DemoWidget (frozen plan)

**Goal:** port References/DemoWidget verbatim into this project.

**Global Constraints:**
- Verbatim port of `References/DemoWidget/Core.lua` - including the 0.2s
  reset-to-zero OnUpdate throttle (`Core.lua:16`) and the
  PLAYER_REGEN_ENABLED-then-PLAYER_REGEN_DISABLED registration order
  (`Core.lua:25-26`). The ONLY approved deviation is the frame rename.

## Tasks
- [ ] Create `Widgets/DemoWidget.lua` with Core.lua's body verbatim,
      renaming frame `DemoWidgetFrame` -> `DemoAddon_DemoWidget` (single
      site, `Core.lua:6`).
- [ ] Register `Widgets\\DemoWidget.lua` in `DemoAddon.toc` on a new line
      after `Widgets\\TargetGlow.lua`.

---

## Debate record

**Participants:** Fable 5 (session) / GPT-5.6 Sol (codex exec, session eval-fixture)
**Rounds used:** 1 of 4
**Outcome:** converged
**Verification status:** FULL
**Degradation:** none
**Authorized by:** n/a

### Resolved points
| # | Claim | Raised by | Outcome | Evidence |
|---|-------|-----------|---------|----------|
| 1 | throttle is 0.2s reset-to-zero | Fable | accepted | References/DemoWidget/Core.lua:16 |
| 2 | regen-ENABLED registered first | Sol | accepted | References/DemoWidget/Core.lua:25-26 |

### Escalated points (user-decided)
| # | Question | Fable position | Sol position | Owner's call |
|---|----------|----------------|--------------|--------------|
"""

# The port with ONE planted deviation from plan and reference: the
# OnUpdate throttle is 0.5, not the verbatim 0.2 the frozen plan pins.
# The `elapsed < 0.5` line is the single site build_diff_state's decoy
# rewrites with a literal .replace - keep the two in sync.
IMPLEMENTED_PORT = """local frame = CreateFrame("Frame", "DemoAddon_DemoWidget", UIParent)
frame:SetSize(160, 24)
frame:SetPoint("CENTER", 0, -180)

local text = frame:CreateFontString(nil, "OVERLAY", "GameFontNormal")
text:SetAllPoints(frame)

local elapsed = 0
frame:SetScript("OnUpdate", function(_, dt)
    elapsed = elapsed + dt
    if elapsed < 0.5 then return end
    elapsed = 0
    if UnitExists("target") then
        text:SetText(UnitName("target"))
    else
        text:SetText("")
    end
end)

frame:RegisterEvent("PLAYER_REGEN_ENABLED")
frame:RegisterEvent("PLAYER_REGEN_DISABLED")
frame:SetScript("OnEvent", function(_, event)
    if event == "PLAYER_REGEN_DISABLED" then
        frame:Show()
    else
        frame:Hide()
    end
end)
"""


def git(ws, *args):
    subprocess.run(["git", "-C", str(ws),
                    "-c", "user.name=crosscheck-eval",
                    "-c", "user.email=eval@localhost", *args],
                   check=True, capture_output=True)


def rev(ws, ref="HEAD"):
    out = subprocess.run(["git", "-C", str(ws), "rev-parse", "--short", ref],
                         check=True, capture_output=True, text=True)
    return out.stdout.strip()


def build_diff_state(ws):
    """Synthesize the state diff mode needs: base commit with the frozen
    plan, then an implementation commit carrying one planted deviation
    (throttle 0.5 vs the plan's verbatim 0.2).

    Then plant a DECOY: the working tree gets the compliant 0.2 version,
    uncommitted. Reading Widgets/DemoWidget.lua now shows a clean port -
    the planted defect exists ONLY in the committed base..head range. An
    agent that skips the diff and reads the file cannot find the drift, so
    a pass proves it actually opened the range (Sol review 2026-07-13:
    without this, 'reviewed the diff' was an ungradable claim).
    """
    git(ws, "add", "-A")
    git(ws, "commit", "-q", "-m", "base: project + reference")
    plan = ws / "docs" / "superpowers" / "plans" / "2026-07-13-demowidget-port.md"
    plan.parent.mkdir(parents=True, exist_ok=True)
    plan.write_text(FROZEN_PLAN, encoding="utf-8")
    git(ws, "add", "-A")
    git(ws, "commit", "-q", "-m", "freeze demowidget port plan")
    base = rev(ws)
    widget = ws / "Widgets" / "DemoWidget.lua"
    widget.write_text(IMPLEMENTED_PORT, encoding="utf-8")
    toc = ws / "DemoAddon.toc"
    toc.write_text(toc.read_text(encoding="utf-8")
                   + "Widgets\\DemoWidget.lua\n", encoding="utf-8")
    git(ws, "add", "-A")
    git(ws, "commit", "-q", "-m", "implement demowidget port")
    head = rev(ws)
    decoy = IMPLEMENTED_PORT.replace("elapsed < 0.5", "elapsed < 0.2")
    assert decoy != IMPLEMENTED_PORT, "decoy must actually rewrite the throttle"
    widget.write_text(decoy, encoding="utf-8")
    return {"{BASE_SHA}": base, "{HEAD_SHA}": head,
            "{PLAN_PATH}": "docs/superpowers/plans/2026-07-13-demowidget-port.md"}


def build_workspace(setup, tmp):
    ws = Path(tmp) / "workspace"
    ws.mkdir()
    if setup.get("with_reference"):
        shutil.copytree(FIXTURE_REPO, ws, dirs_exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=ws, check=True,
                   capture_output=True)
    subs = {}
    if setup.get("diff_state"):
        subs = build_diff_state(ws)
    return ws, subs


def env_without_codex():
    env = dict(os.environ)
    codex = shutil.which("codex")
    if not codex:
        return env
    drop = {str(Path(codex).parent).rstrip("\\/").lower()}
    parts = [p for p in env.get("PATH", "").split(os.pathsep)
             if p.rstrip("\\/").lower() not in drop]
    env["PATH"] = os.pathsep.join(parts)
    return env


def compact_stream(stdout):
    """Flatten claude -p stream-json events into a graded transcript: the
    agent's text verbatim, tool calls with their inputs (the evidence that
    e.g. codex exec actually ran), tool results truncated - without this
    the grader only sees the final message and marks real tool work as
    absent (first full-suite run, 2026-07-12)."""
    lines = []
    for raw in stdout.splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            event = json.loads(raw)
        except json.JSONDecodeError:
            lines.append(raw)
            continue
        etype = event.get("type")
        if etype == "result":
            lines.append("[final result]\n" + str(event.get("result", "")))
            continue
        for block in (event.get("message") or {}).get("content") or []:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "text":
                lines.append(block["text"])
            elif block.get("type") == "tool_use":
                args = json.dumps(block.get("input", {}))
                lines.append(f"[tool_use] {block.get('name')} {args[:600]}")
            elif block.get("type") == "tool_result":
                content = block.get("content")
                if isinstance(content, list):
                    content = " ".join(c.get("text", "") for c in content
                                       if isinstance(c, dict))
                # 1200, not 700: the diff case's grading requires the range
                # read's RESULT to visibly carry the planted throttle line,
                # which sits ~600 chars into a whole-range diff (toc hunk
                # first) - a 700 cap made that evidence a coin flip.
                lines.append(f"[tool_result] {str(content)[:1200]}")
    return "\n".join(lines)


def run_case(case, model, timeout, artifacts=None, head=False):
    setup = case.get("setup", {})
    if setup.get("manual"):
        return "SKIPPED(manual)", setup["manual"], []
    with tempfile.TemporaryDirectory(prefix="crosscheck-eval-") as tmp:
        ws, subs = build_workspace(setup, tmp)
        prompt = case["prompt"]
        for placeholder, value in subs.items():
            prompt = prompt.replace(placeholder, value)
        env = env_without_codex() if setup.get("no_codex") else dict(os.environ)
        # The prompt goes via STDIN and the executor runs WITHOUT a shell:
        # cmd.exe truncates a multi-line argv at the first newline, silently
        # eating the request AND every flag after it (--model, --allowedTools,
        # --output-format) - all early graded runs were invalid (2026-07-12).
        # --strict-mcp-config with no --mcp-config: zero MCP servers reach
        # the executor (--tools restricts built-ins only). No --bare here -
        # the executor must load the installed plugin's skill.
        cmd = [
            shutil.which("claude"), "-p",
            "--model", model,
            "--strict-mcp-config",
            "--tools", AVAILABLE_TOOLS,
            "--allowedTools", ALLOWED_TOOLS,
            "--output-format", "stream-json", "--verbose",
        ]
        if head:
            cmd += ["--plugin-dir", str(PLUGIN_ROOT)]
        try:
            proc = subprocess.run(
                cmd, cwd=ws, env=env, capture_output=True, text=True,
                encoding="utf-8", errors="replace",
                input=HARNESS_PREAMBLE + prompt,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return "FAIL", "executor timed out", []
        transcript = compact_stream(proc.stdout or "")
        if proc.stderr:
            # Labeled so the grader never mistakes harness noise for the
            # agent ending its run mid-thought.
            transcript += "\n=== EXECUTOR STDERR (harness, not agent output) ===\n" + proc.stderr
        if artifacts:
            artifacts.mkdir(parents=True, exist_ok=True)
            (artifacts / f"{case['id']}.transcript.txt").write_text(
                transcript, encoding="utf-8")
        # Any nonzero executor exit fails the case outright - a partial
        # transcript from a crashed run must never be graded into a PASS
        # (Sol review 2026-07-12).
        if proc.returncode != 0:
            return "FAIL", f"executor exit {proc.returncode}: {transcript[:400]}", []
    verdicts = grade(case, transcript)
    if artifacts:
        (artifacts / f"{case['id']}.verdicts.json").write_text(
            json.dumps(verdicts, indent=2), encoding="utf-8")
    if not verdicts:
        return "FAIL", "grader returned no parseable verdicts", []
    if len(verdicts) != len(case["expectations"]):
        return "FAIL", (f"grader verdict count mismatch: {len(verdicts)} verdicts"
                        f" for {len(case['expectations'])} expectations"), verdicts
    if any(not isinstance(v, dict) for v in verdicts):
        return "FAIL", "grader verdict entry is not an object", []
    # Positional numbering also rejects duplicates (four copies of
    # expectation 1 must not pass a four-expectation case).
    if [v.get("expectation") for v in verdicts] != list(
            range(1, len(verdicts) + 1)):
        return "FAIL", "grader verdict numbering mismatch", verdicts
    if any(not isinstance(v.get("met"), bool) for v in verdicts):
        return "FAIL", "grader verdict missing boolean 'met'", verdicts
    misses = [v for v in verdicts if not v["met"]]
    status = "PASS" if not misses else "FAIL"
    return status, f"{len(verdicts) - len(misses)}/{len(verdicts)} expectations met", verdicts


def grade(case, transcript):
    numbered = "\n".join(f"{i}. {e}" for i, e in enumerate(case["expectations"], 1))
    # Head+tail truncation: a tail-only cut discards the early tool calls
    # (the codex round-1 invocation) that expectations grade on.
    if len(transcript) > 40000:
        transcript = (transcript[:15000]
                      + "\n...[transcript middle elided by harness]...\n"
                      + transcript[-25000:])
    prompt = GRADER_PROMPT.format(
        expectations=numbered, expected=case["expected_output"],
        transcript=transcript,
    )
    with tempfile.TemporaryDirectory(prefix="crosscheck-grade-") as tmp:
        reply_file = Path(tmp) / "reply.txt"
        try:
            proc = subprocess.run(
                ["codex", "exec", "--sandbox", "read-only",
                 "-m", "gpt-5.6-sol", "-c", "model_reasoning_effort=high",
                 "--output-last-message", str(reply_file), "-"],
                input=prompt, capture_output=True, text=True, timeout=600,
                encoding="utf-8", errors="replace",
                shell=(os.name == "nt"),
            )
        except (subprocess.TimeoutExpired, OSError):
            return []
        if proc.returncode != 0:
            return []
        raw = reply_file.read_text(encoding="utf-8") if reply_file.is_file() else proc.stdout
    start, end = raw.find("["), raw.rfind("]")
    if start == -1 or end == -1:
        return []
    try:
        parsed = json.loads(raw[start:end + 1])
    except json.JSONDecodeError:
        return []
    return parsed if isinstance(parsed, list) else []


def main(argv=None):
    # Grader evidence may contain non-cp1252 chars (arrows, quotes); the
    # Windows console must not be able to crash the suite mid-run.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Behavioral (Tier 3) evals runner.")
    ap.add_argument("--case", action="append", help="run only these case ids")
    ap.add_argument("--list", action="store_true", help="list cases and exit (CI self-test)")
    ap.add_argument("--model", default="sonnet",
                    help="executor model (default sonnet; use fable for full realism)")
    ap.add_argument("--timeout", type=int, default=900,
                    help="seconds per case executor run (default 900)")
    ap.add_argument("--artifacts", type=Path,
                    help="persist per-case transcript + verdicts here"
                         " (debugging and grading disputes)")
    ap.add_argument("--head", action="store_true",
                    help="load the plugin from THIS checkout via"
                         " --plugin-dir instead of the installed cache -"
                         " skips the bump+update dance while iterating."
                         " Caveat: shadowing vs the installed copy of the"
                         " same plugin is unverified; the pre-merge run"
                         " should still use the installed cache")
    args = ap.parse_args(argv)

    cases = load_cases()
    if args.case:
        cases = [c for c in cases if c["id"] in set(args.case)]
        if not cases:
            print("no matching case ids")
            return 2

    if args.list:
        for c in cases:
            setup = c.get("setup", {})
            tags = [k for k, v in setup.items() if v] or ["default"]
            print(f"{c['id']:34} [{', '.join(tags)}]  {len(c['expectations'])} expectations")
        print(f"\n{len(cases)} case(s); fixture repo: {FIXTURE_REPO.is_dir()}")
        return 0

    for tool in ("claude", "codex"):
        if not shutil.which(tool):
            print(f"error: {tool} CLI not on PATH - this runner is local-only")
            return 2

    failures = 0
    for c in cases:
        status, summary, verdicts = run_case(c, args.model, args.timeout,
                                             artifacts=args.artifacts,
                                             head=args.head)
        print(f"{status:16} {c['id']} - {summary}")
        for v in verdicts:
            mark = "ok " if v.get("met") else "MISS"
            print(f"    {mark} #{v.get('expectation')}: {v.get('evidence', '')[:140]}")
        if status == "FAIL":
            failures += 1
    print(f"\n{failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
