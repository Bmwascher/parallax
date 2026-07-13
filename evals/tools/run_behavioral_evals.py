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
    python run_behavioral_evals.py --case degraded-mode-visible
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
SKILL = "multi-model-verify"
CASES_FILE = EVALS_ROOT / SKILL / "evals.json"
FIXTURE_REPO = EVALS_ROOT / SKILL / "fixtures" / "fixture-repo"

HARNESS_PREAMBLE = (
    "TEST HARNESS RUN. Follow the multi-model-verify skill exactly as"
    " written for the request below, with these test constraints: cap any"
    " debate at ONE exchange; do not create or modify files outside this"
    " workspace; report-only (no frozen plan file). End with the skill's"
    " finish line.\n\nRequest: "
)

ALLOWED_TOOLS = (
    "Skill,Read,Glob,Grep,"
    "Bash(codex:*),Bash(git:*),Bash(ls:*),Bash(cat:*),"
    "PowerShell(codex:*),PowerShell(git:*)"
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


def build_workspace(setup, tmp):
    ws = Path(tmp) / "workspace"
    ws.mkdir()
    if setup.get("with_reference"):
        shutil.copytree(FIXTURE_REPO, ws, dirs_exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=ws, check=True,
                   capture_output=True)
    return ws


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


def run_case(case, model, timeout):
    setup = case.get("setup", {})
    if setup.get("manual"):
        return "SKIPPED(manual)", setup["manual"], []
    with tempfile.TemporaryDirectory(prefix="crosscheck-eval-") as tmp:
        ws = build_workspace(setup, tmp)
        env = env_without_codex() if setup.get("no_codex") else dict(os.environ)
        cmd = [
            "claude", "-p", HARNESS_PREAMBLE + case["prompt"],
            "--model", model,
            "--allowedTools", ALLOWED_TOOLS,
        ]
        try:
            proc = subprocess.run(
                cmd, cwd=ws, env=env, capture_output=True, text=True,
                timeout=timeout, shell=(os.name == "nt"),
            )
        except subprocess.TimeoutExpired:
            return "FAIL", "executor timed out", []
        transcript = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
        if proc.returncode != 0 and not proc.stdout:
            return "FAIL", f"executor exit {proc.returncode}: {transcript[:400]}", []
    verdicts = grade(case, transcript)
    if not verdicts:
        return "FAIL", "grader returned no parseable verdicts", []
    misses = [v for v in verdicts if not v.get("met")]
    status = "PASS" if not misses else "FAIL"
    return status, f"{len(verdicts) - len(misses)}/{len(verdicts)} expectations met", verdicts


def grade(case, transcript):
    numbered = "\n".join(f"{i}. {e}" for i, e in enumerate(case["expectations"], 1))
    prompt = GRADER_PROMPT.format(
        expectations=numbered, expected=case["expected_output"],
        transcript=transcript[-24000:],
    )
    with tempfile.TemporaryDirectory(prefix="crosscheck-grade-") as tmp:
        reply_file = Path(tmp) / "reply.txt"
        proc = subprocess.run(
            ["codex", "exec", "--sandbox", "read-only",
             "-m", "gpt-5.6-sol", "-c", "model_reasoning_effort=high",
             "--output-last-message", str(reply_file), "-"],
            input=prompt, capture_output=True, text=True, timeout=600,
            shell=(os.name == "nt"),
        )
        raw = reply_file.read_text(encoding="utf-8") if reply_file.is_file() else proc.stdout
    start, end = raw.find("["), raw.rfind("]")
    if start == -1 or end == -1:
        return []
    try:
        return json.loads(raw[start:end + 1])
    except json.JSONDecodeError:
        return []


def main(argv=None):
    ap = argparse.ArgumentParser(description="Behavioral (Tier 3) evals runner.")
    ap.add_argument("--case", action="append", help="run only these case ids")
    ap.add_argument("--list", action="store_true", help="list cases and exit (CI self-test)")
    ap.add_argument("--model", default="sonnet",
                    help="executor model (default sonnet; use fable for full realism)")
    ap.add_argument("--timeout", type=int, default=900,
                    help="seconds per case executor run (default 900)")
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
        status, summary, verdicts = run_case(c, args.model, args.timeout)
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
