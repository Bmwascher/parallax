"""Deterministic structural tests for the multi-model-verify skill.

Tier 2b: no model calls, no network. Asserts the live-verified transport
contract and review findings (2026-07-12) so drift in the skill files fails
CI before it misleads a live debate.
"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = REPO_ROOT / "skills" / "multi-model-verify"
HOOKS_JSON = REPO_ROOT / "hooks" / "hooks.json"
HOOK_SCRIPT = REPO_ROOT / "hooks" / "superpowers-review-companion.ps1"
SKILL_MD = SKILL_DIR / "SKILL.md"
REFERENCES = SKILL_DIR / "references"
EVALS_DIR = Path(__file__).resolve().parent

REQUIRED_REFERENCE_FILES = [
    "debate-protocol.md",
    "frozen-plan-format.md",
    "model-prompting-notes.md",
    "fallbacks.md",
]


def read(path):
    assert path.is_file(), f"missing file: {path}"
    return path.read_text(encoding="utf-8")


def frontmatter(text):
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert match, "SKILL.md must start with YAML frontmatter"
    return match.group(1)


class TestSkillStructure:
    def test_skill_md_exists(self):
        assert SKILL_MD.is_file()

    def test_frontmatter_name_matches_directory(self):
        fm = frontmatter(read(SKILL_MD))
        name = re.search(r"^name:\s*(\S+)\s*$", fm, re.MULTILINE)
        assert name, "frontmatter needs a name field"
        assert name.group(1) == "multi-model-verify"
        assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name.group(1))

    def test_description_is_trigger_only(self):
        fm = frontmatter(read(SKILL_MD))
        desc = re.search(r"^description:\s*(.+)$", fm, re.MULTILINE)
        assert desc, "frontmatter needs a description field"
        text = desc.group(1).strip()
        assert text.startswith("Use when"), "description must start 'Use when'"
        assert len(text) <= 1024
        # Workflow summaries in descriptions shortcut the skill body
        # (superpowers writing-skills SDO finding) - keep them out.
        for banned in ("round", "codex exec", "session id", "freeze"):
            assert banned not in text.lower(), (
                f"description leaks workflow detail: {banned!r}"
            )

    def test_reference_files_exist(self):
        for name in REQUIRED_REFERENCE_FILES:
            assert (REFERENCES / name).is_file(), f"missing references/{name}"

    def test_no_backslash_paths_anywhere(self):
        for path in [SKILL_MD, *(REFERENCES / n for n in REQUIRED_REFERENCE_FILES)]:
            text = read(path)
            assert "\\" not in text, (
                f"{path.name} contains a backslash - use forward slashes and"
                " relative paths only"
            )


class TestTransportContract:
    """The codex invocation shapes were live-verified 2026-07-12 on 0.144.1.

    These strings are load-bearing: get them wrong and debates silently run
    on the wrong model, with write access, or lose cross-round state.
    """

    def test_model_pinned(self):
        text = read(SKILL_MD)
        assert "-m gpt-5.6-sol" in text

    def test_sandbox_read_only(self):
        text = read(SKILL_MD)
        assert "--sandbox read-only" in text

    def test_effort_pinned_high(self):
        joined = read(SKILL_MD) + read(REFERENCES / "model-prompting-notes.md")
        assert "model_reasoning_effort" in joined
        assert '"high"' in joined or "=high" in joined or "effort high" in joined

    def test_resume_flags_before_subcommand(self):
        text = read(SKILL_MD)
        # Model and effort must be re-pinned on EVERY call including resume -
        # a resume that falls back to config defaults silently changes the
        # debate's model (cross-review finding, 2026-07-12).
        assert re.search(
            r"codex exec --sandbox read-only -m gpt-5\.6-sol"
            r" -c model_reasoning_effort=high [^\n]*resume <SESSION_ID>", text
        ), "resume must re-pin model and effort, flags BEFORE the subcommand"
        assert "resume --last" not in text, (
            "resume --last is fragile under concurrent codex sessions and"
            " must not appear in SKILL.md (prohibition lives in"
            " model-prompting-notes.md)"
        )

    def test_session_id_capture_documented(self):
        text = read(SKILL_MD)
        assert "session id" in text.lower()

    def test_reply_captured_to_file(self):
        # codex exec prints a full multi-KB transcript; without this flag the
        # reply is buried at the bottom (live compliance-test finding).
        text = read(SKILL_MD)
        assert "--output-last-message" in text

    def test_versioned_reference_citations(self):
        # References/<addon>/ may hold version subdirectories (e.g. a v1.4/
        # next to a v1.1_old/) - the citation grammar must cover that.
        text = read(SKILL_MD)
        assert "<version>" in text


class TestDebateProtocol:
    def test_round_cap_default(self):
        text = read(REFERENCES / "debate-protocol.md")
        assert re.search(r"round cap.*4|4.*exchanges", text, re.IGNORECASE)

    def test_tri_state_verdict(self):
        text = read(REFERENCES / "debate-protocol.md")
        for verdict in ("PASS", "FIX", "ESCALATE"):
            assert verdict in text

    def test_evidence_grounding_rule(self):
        text = read(REFERENCES / "debate-protocol.md")
        assert "References/" in text
        assert re.search(r"file:line|file and line", text, re.IGNORECASE)

    def test_anti_manufactured_objection_rule(self):
        text = read(REFERENCES / "debate-protocol.md")
        assert re.search(r"manufacture", text, re.IGNORECASE)
        assert re.search(r"sound plan", text, re.IGNORECASE)

    def test_escalation_goes_to_user(self):
        text = read(REFERENCES / "debate-protocol.md")
        assert re.search(r"escalat", text, re.IGNORECASE)

    def test_converged_with_amendments_state(self):
        # A FIX accepted in the final round must not read as disagreement
        # (live compliance-test finding: strict both-PASS convergence
        # overstates conflict when the cap lands on an accepted FIX).
        text = read(REFERENCES / "debate-protocol.md")
        assert re.search(r"converged with amendments", text, re.IGNORECASE)

    def test_session_final_adjudication(self):
        # The chain never terminates on the external reviewer's verdict:
        # the session verifies the final round and emits the terminal
        # verdict itself (user directive, 2026-07-12).
        text = read(REFERENCES / "debate-protocol.md")
        assert re.search(r"final adjudication", text, re.IGNORECASE)
        assert re.search(r"session.{0,60}(final say|last step)",
                         text, re.IGNORECASE | re.DOTALL)
        assert re.search(r"(input|never).{0,40}(to this step|the decision)",
                         text, re.IGNORECASE)
        skill = read(SKILL_MD)
        assert re.search(r"final.adjudication", skill, re.IGNORECASE), (
            "the finish line must route through the adjudication step"
        )


class TestFallbacks:
    """Loud-degradation contract (Sol round-2 audit, 2026-07-12): degraded
    mode is consent-gated, structured, and poisons downstream PASSes. These
    pin the specific rules, not word presence."""

    def fallbacks(self):
        return read(REFERENCES / "fallbacks.md")

    def test_preflight_documented(self):
        assert "codex --version" in self.fallbacks()

    def test_consent_gate_principle(self):
        text = self.fallbacks()
        assert re.search(
            r"no transition that reduces vendor diversity,\s+evidence"
            r"\s+quality,\s+or\s+(conversation\s+)?continuity\s+.*?without"
            r"\s+explicit\s+.*?consent",
            text, re.IGNORECASE | re.DOTALL,
        ), "the governing consent-gate principle is missing"

    def test_no_automatic_degraded_entry(self):
        text = self.fallbacks()
        assert re.search(r"never enters? degraded mode (automatically|on its own)",
                         text, re.IGNORECASE)
        assert re.search(r"fix codex|run degraded|abort", text, re.IGNORECASE)

    def test_bounded_recovery_before_gate(self):
        text = self.fallbacks()
        assert re.search(r"one (automatic )?retry.*same (model|parameters)",
                         text, re.IGNORECASE)

    def test_unattended_fails_closed(self):
        text = self.fallbacks()
        assert "BLOCKED/DEGRADED-NOT-AUTHORIZED" in text
        assert re.search(r"never infer consent", text, re.IGNORECASE)

    def test_failure_class_catch_all(self):
        text = self.fallbacks()
        assert re.search(
            r"any (codex|transport) failure not (listed|named).*consent gate",
            text, re.IGNORECASE | re.DOTALL,
        ), "unlisted codex failure classes need the catch-all rule"

    def test_session_loss_is_gated(self):
        text = self.fallbacks()
        assert re.search(
            r"(session|continuity).{0,120}(consent gate|not automatic)",
            text, re.IGNORECASE | re.DOTALL,
        ), "losing session continuity must route through the consent gate"

    def test_quota_limit_is_named_class(self):
        # Session/weekly usage limits are not transport blips: no retry
        # (the window will not clear in seconds), straight to the consent
        # gate with codex's reset time surfaced.
        text = self.fallbacks()
        assert "quota-exhausted" in text
        assert re.search(r"(session|weekly).{0,60}(limit|quota|cap)",
                         text, re.IGNORECASE)
        assert re.search(r"skip the retry", text, re.IGNORECASE)
        assert re.search(r"reset time", text, re.IGNORECASE)

    def test_stale_evidence_is_struck(self):
        text = self.fallbacks()
        assert re.search(r"struck until re-verified", text, re.IGNORECASE)

    def test_missing_reference_refusal(self):
        joined = self.fallbacks() + read(SKILL_MD)
        assert re.search(r"References/", joined)
        assert re.search(r"hard stop", joined, re.IGNORECASE)


class TestDegradedStatusFields:
    """Structured degraded status (Sol round-2 fix B): parseable fields, not
    prose, so mode diff can enforce the poisoning rule."""

    def test_frozen_plan_has_verification_status_field(self):
        text = read(REFERENCES / "frozen-plan-format.md")
        assert "**Verification status:** FULL | DEGRADED" in text
        assert "**Degradation:**" in text
        assert "**Authorized by:**" in text

    def test_participants_not_hardcoded_when_degraded(self):
        text = read(REFERENCES / "frozen-plan-format.md")
        assert re.search(r"participants line must name\s+the actual",
                         text, re.IGNORECASE)

    def test_diff_mode_poisoning_rule(self):
        text = read(SKILL_MD)
        assert re.search(r"Verification status", text)
        assert re.search(
            r"DEGRADED.{0,400}(cannot|must not).{0,80}PASS",
            text, re.IGNORECASE | re.DOTALL,
        ), "a degraded-frozen plan must not produce an ordinary diff PASS"
        assert "CROSS-VENDOR GATE UNSATISFIED" in text
        assert re.search(r"re-?(open|verif).{0,120}plan.{0,240}"
                         r"(before|only then).{0,80}(implementation|diff)",
                         text, re.IGNORECASE | re.DOTALL), (
            "diff mode must retrospectively re-verify a degraded plan's"
            " claims before checking the implementation"
        )


class TestEvalFixtures:
    def test_trigger_cases_schema(self):
        data = json.loads(read(EVALS_DIR / "trigger-cases.json"))
        assert data["skill"] == "multi-model-verify"
        assert len(data["cases"]) >= 8
        ids = [c["id"] for c in data["cases"]]
        assert len(ids) == len(set(ids)), "case ids must be unique"
        triggers = [c["should_trigger"] for c in data["cases"]]
        assert any(triggers) and not all(triggers), (
            "need both should-trigger and should-not-trigger cases"
        )
        for case in data["cases"]:
            assert case["prompt"].strip()
            assert case["assert"].strip()

    def test_evals_schema(self):
        data = json.loads(read(EVALS_DIR / "evals.json"))
        assert data["skill_name"] == "multi-model-verify"
        assert len(data["evals"]) >= 4
        for entry in data["evals"]:
            assert entry["id"].strip()
            assert entry["prompt"].strip()
            assert entry["expected_output"].strip()
            assert len(entry["expectations"]) >= 3
            # Every case must be executable or explicitly manual - the
            # runner refuses to guess (Sol audit: dead-data finding).
            setup = entry.get("setup", {})
            assert setup.get("manual") or "with_reference" in setup, (
                f"case {entry['id']} needs a setup config for the runner"
            )

    def test_behavioral_runner_allows_skill_tool(self):
        # Without Skill in the executor allowlist the agent can never load
        # the plugin skill, so every behavioral case grades an agent flying
        # blind (root cause of the 2026-07-12 missing-reference regression).
        runner = read(REPO_ROOT / "evals" / "tools" / "run_behavioral_evals.py")
        allowlist = re.search(r"ALLOWED_TOOLS = \(([^)]*)\)", runner, re.S)
        assert allowlist, "ALLOWED_TOOLS block not found in runner"
        assert "Skill," in allowlist.group(1), (
            "executor allowlist must include the Skill tool"
        )

    def test_behavioral_runner_grades_tool_evidence(self):
        # Plain claude -p prints only the final message: the grader then
        # marks real tool work (the codex exec round) as absent. The
        # executor must stream events and the transcript must carry
        # tool_use evidence (first full-suite run, 2026-07-12).
        runner = read(REPO_ROOT / "evals" / "tools" / "run_behavioral_evals.py")
        assert "stream-json" in runner and "--verbose" in runner
        assert "tool_use" in runner, "transcript must include tool calls"
        assert "STDERR" in runner, "harness stderr must be labeled"
        # The prompt must travel via stdin: on Windows a multi-line argv
        # through cmd.exe is truncated at the first newline, silently
        # dropping the request and all flags after it.
        assert 'input=HARNESS_PREAMBLE + case["prompt"]' in runner
        assert re.search(r"shutil\.which\(.claude.\)", runner), (
            "executor must resolve the claude exe and run shell-free"
        )

    def test_behavioral_runner_self_test(self):
        # CI-safe: --list parses cases and checks the fixture, no model calls.
        proc = subprocess.run(
            [sys.executable, str(REPO_ROOT / "evals" / "tools" / "run_behavioral_evals.py"),
             "--list"],
            capture_output=True, text=True, timeout=60,
        )
        assert proc.returncode == 0, proc.stderr
        assert "degraded-consent-gate" in proc.stdout
        assert "fixture repo: True" in proc.stdout


class TestHook:
    """The auto diff-gate lives or dies on these. Claude Code renamed the
    Task tool to Agent in v2.1.63 - a bare "Task" matcher never fires and
    CI cannot see it without these tests (Sol cross-review finding,
    2026-07-12)."""

    def hook_entries(self):
        data = json.loads(read(HOOKS_JSON))
        return data["hooks"]["PostToolUse"]

    def test_matcher_covers_agent_tool(self):
        matchers = [e.get("matcher", "") for e in self.hook_entries()]
        assert any(re.fullmatch(m, "Agent") for m in matchers), (
            "no PostToolUse matcher matches the Agent tool - the diff gate"
            " is inert on current Claude Code"
        )

    def test_command_references_existing_script(self):
        cmd = self.hook_entries()[0]["hooks"][0]["command"]
        assert "${CLAUDE_PLUGIN_ROOT}" in cmd
        assert "superpowers-review-companion.ps1" in cmd
        assert HOOK_SCRIPT.is_file()

    def run_hook(self, payload):
        pwsh = shutil.which("pwsh")
        if not pwsh:
            pytest.skip("pwsh not on PATH")
        proc = subprocess.run(
            [pwsh, "-NoProfile", "-NonInteractive", "-File", str(HOOK_SCRIPT)],
            input=json.dumps(payload), capture_output=True, text=True,
            timeout=60,
        )
        return proc.stdout.strip(), proc.returncode

    def test_emits_context_on_review_dispatch(self):
        payload = {
            "tool_name": "Agent",
            "tool_input": {
                "description": "Review code changes",
                "prompt": (
                    "You are a Senior Code Reviewer with expertise in"
                    " software architecture.\n## Git Range to Review\n"
                    "**Base:** abc1234\n**Head:** def5678\n"
                ),
            },
        }
        out, rc = self.run_hook(payload)
        assert rc == 0
        data = json.loads(out)
        assert data["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
        ctx = data["hookSpecificOutput"]["additionalContext"]
        assert "abc1234" in ctx and "def5678" in ctx
        assert "multi-model-verify" in ctx

    def test_silent_on_other_dispatch(self):
        payload = {
            "tool_name": "Agent",
            "tool_input": {"description": "Explore",
                           "prompt": "Find all uses of FramePool."},
        }
        out, rc = self.run_hook(payload)
        assert rc == 0
        assert out == ""

    def test_failure_event_also_registered(self):
        # A failed review dispatch must also surface the gate reminder -
        # PostToolUse alone covers only successful calls (Sol round-2
        # additional finding #3).
        data = json.loads(read(HOOKS_JSON))
        assert "PostToolUseFailure" in data["hooks"], (
            "register the companion for PostToolUseFailure too"
        )
        matchers = [e.get("matcher", "")
                    for e in data["hooks"]["PostToolUseFailure"]]
        assert any(re.fullmatch(m, "Agent") for m in matchers)

    def test_pinned_template_fixture_end_to_end(self):
        """Layer-2 rot detection (Sol round-2 fix D): a pinned copy of the
        superpowers template, rendered with real SHAs and fed through the
        actual script - hermetic, runs in CI."""
        fixture = EVALS_DIR / "fixtures" / "superpowers-code-reviewer-6.1.1.md"
        assert fixture.is_file(), "pinned superpowers template fixture missing"
        template = fixture.read_text(encoding="utf-8")
        for literal in ("Senior Code Reviewer", "Git Range to Review"):
            assert literal in template
        rendered = (template
                    .replace("[DESCRIPTION]", "Ported the widget module")
                    .replace("[PLAN_OR_REQUIREMENTS]", "plan.md")
                    .replace("[BASE_SHA]", "abc1234")
                    .replace("[HEAD_SHA]", "def5678"))
        out, rc = self.run_hook({
            "tool_name": "Agent",
            "tool_input": {"description": "Review code changes",
                           "prompt": rendered},
        })
        assert rc == 0
        ctx = json.loads(out)["hookSpecificOutput"]["additionalContext"]
        assert "abc1234" in ctx and "def5678" in ctx

    def test_superpowers_fingerprint_canary(self):
        """Fails loudly when a superpowers update rots the fingerprint -
        otherwise the diff gate dies with zero signal. Skips where
        superpowers is not installed (CI)."""
        registry = Path.home() / ".claude" / "plugins" / "installed_plugins.json"
        if not registry.is_file():
            pytest.skip("no plugin registry on this machine")
        data = json.loads(registry.read_text(encoding="utf-8"))
        entries = [v for k, v in data.get("plugins", {}).items()
                   if k.startswith("superpowers@")]
        if not entries:
            pytest.skip("superpowers not installed")
        install = Path(entries[0][0]["installPath"])
        template = install / "skills" / "requesting-code-review" / "code-reviewer.md"
        assert template.is_file(), (
            "superpowers layout changed - re-fingerprint the hook"
        )
        text = template.read_text(encoding="utf-8")
        for literal in ("Senior Code Reviewer", "Git Range to Review"):
            assert literal in text, (
                f"fingerprint literal {literal!r} is gone from the installed"
                " superpowers code-reviewer template - the hook is now inert;"
                " re-fingerprint hooks/superpowers-review-companion.ps1"
            )


class TestDriftProtection:
    """tools/check-drift.ps1 watches the three upstreams crosscheck's
    contract depends on (superpowers template, Claude Code surface, codex
    exec flags). These pin its own contract so edits cannot quietly hollow
    it out."""

    DRIFT = REPO_ROOT / "tools" / "check-drift.ps1"

    def drift(self):
        return read(self.DRIFT)

    def test_is_pure_ascii(self):
        # The scheduled task runs Windows PowerShell 5.1, which reads
        # BOM-less files as ANSI: a UTF-8 em dash decodes into a smart
        # quote that silently terminates strings.
        raw = self.DRIFT.read_bytes()
        bad = [i for i, b in enumerate(raw) if b > 127]
        assert not bad, f"non-ASCII byte at offset {bad[0]} breaks PS 5.1"

    def test_superpowers_canary_contract(self):
        text = self.drift()
        for literal in ("Senior Code Reviewer", "Git Range to Review"):
            assert literal in text, "canary must check the hook fingerprints"
        assert "superpowers-code-reviewer-6.1.1.md" in text, (
            "canary must hash against the pinned fixture"
        )
        assert "installed_plugins.json" in text

    def test_codex_transport_probe(self):
        text = self.drift()
        for flag in ("--sandbox", "--output-last-message"):
            assert flag in text, f"transport probe must cover {flag}"
        assert "exec resume" in text, "resume subcommand must be probed"

    def test_changelog_watch(self):
        text = self.drift()
        assert "anthropics/claude-code" in text and "CHANGELOG.md" in text
        keywords = re.search(r"\$ChangelogKeywords = '([^']+)'", text)
        assert keywords, "keyword regex missing"
        for kw in ("hook", "plugin", "matcher", "renam"):
            assert kw in keywords.group(1)
        assert r"\bagents?\b" not in keywords.group(1), (
            "bare 'agent' keyword drowns findings in background-agent UI"
            " churn (48 hits vs 17 on the 2.1.202->207 slice)"
        )

    def test_fails_loud_not_silent(self):
        text = self.drift()
        assert "CRITICAL" in text and "Show-Toast" in text
        # Unfetchable/unsliceable changelog must retry next run, never
        # silently advance past a version we could not inspect.
        assert text.count("do not advance") >= 2

    def test_local_state_is_gitignored(self):
        ignore = read(REPO_ROOT / ".gitignore")
        assert "tools/drift-snapshot.json" in ignore
        assert "tools/drift-reports/" in ignore

    def test_auto_triage_contract(self):
        # Findings-weeks self-triage headless; the loud-failure doctrine
        # still holds: CRITICALs are never silently dismissed, and a failed
        # auto-triage falls back to the manual toast, never to silence.
        text = self.drift()
        assert "$NoAutoTriage" in text, "escape hatch missing"
        for verdict in ("NO-ACTION", "FIXES-APPLIED", "BLOCKED"):
            assert verdict in text
        assert "VERIFY dismissal" in text, (
            "a CRITICAL auto-dismissed as no-action must still toast"
        )
        assert re.search(r"fall(s)? (through|back) to (the )?manual toast",
                         text, re.IGNORECASE)

    def test_auto_triage_agent_is_untrusted(self):
        # The drift report embeds raw upstream changelog text, so the
        # headless agent is a prompt-injection target (Sol round-2
        # CRITICAL): it must have no git/codex, work in a disposable
        # worktree, run under a hard timeout, and the SCRIPT must re-run
        # the gate and own the commit.
        text = self.drift()
        args = re.search(r'\$claudeArgs = @\("-p", "--allowedTools",\s*\r?\n?\s*"([^"]+)"', text)
        assert args, "auto-triage agent allowlist not found"
        for tool in ("git", "codex", "python", "Bash", "PowerShell"):
            assert tool not in args.group(1), (
                f"the unattended agent must never hold {tool} - any shell"
                " is arbitrary execution (Sol round-3 CRITICAL)"
            )
        assert re.search(r"commitOk.*ahead|ahead.*commitOk", text, re.DOTALL), (
            "a commit must be verified (exit + branch ahead) before the"
            " success toast"
        )
        # Reviewer-in-the-loop: the SCRIPT cross-reviews the auto-fix diff
        # via Sol before toasting; a missing/failed review is labeled
        # UNAVAILABLE, never implied-reviewed.
        assert "REVIEW: PASS" in text and "cross-review UNAVAILABLE" in text
        assert re.search(r"Start-Job[\s\S]{0,400}codex exec --sandbox read-only", text), (
            "the cross-review must run script-side, bounded, read-only"
        )
        assert "worktree add" in text, "agent must work in a disposable worktree"
        assert "WaitForExit" in text, "headless run must have a hard timeout"
        assert "python -m pytest evals -q" in text, (
            "the script must re-run the gate itself before committing"
        )
        assert re.search(r"Count -eq 1.*\$verdictLine", text, re.DOTALL), (
            "exactly one strict verdict line must be required"
        )

    def test_snapshot_survives_probe_failure(self):
        # A transient claude/codex probe failure must carry the last
        # known-good version forward, or next week's change detection is
        # disabled and the interval is never inspected (Sol finding 5).
        text = self.drift()
        assert re.search(r"-not \$claudeVersionToSave -and \$snapshot\.claude",
                         text)
        assert re.search(r"-not \$codexVersionToSave -and \$snapshot\.codex",
                         text)

    def test_findings_route_to_triage_command(self):
        # A toast that only names a file is a report that rots unread: the
        # toast must point at the triage command, and the command must exist
        # in the plugin.
        assert "/crosscheck:drift-triage" in self.drift()
        command = REPO_ROOT / "commands" / "drift-triage.md"
        assert command.is_file(), "drift-triage plugin command missing"
        body = read(command)
        assert "drift-reports" in body
        assert re.search(r"schtasks /Query", body), (
            "the command must locate the checkout via the scheduled task,"
            " not assume the session cwd"
        )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
