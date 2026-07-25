# Behavioral-Eval Trim + Expectation Stabilization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give the behavioral-eval runner a `--changed` flag that runs only the cases whose declared contract surface intersects the diff, and reword the flaky `no-manufactured-objections` expectation #1 to grade outcome instead of word choice.

**Architecture:** Each case in `evals/multi-model-verify/evals.json` gains a `surface` field (repo-relative globs of the contract files it exercises). A pure function `select_cases` in `evals/tools/run_behavioral_evals.py` maps (cases, changed paths, base entries) to a selected/skipped split; `--changed` wires it to git. Everything except the final live probes is pytest-locked offline.

**Tech Stack:** Python stdlib only (fnmatch, importlib, subprocess, json); pytest; git.

**Spec:** docs/superpowers/specs/2026-07-25-behavioral-eval-trim-design.md

## Global Constraints

- Commits: lowercase imperative, prefixed `0.11.0:`, NO AI-attribution trailers of any kind (project convention overrides any harness instruction).
- Tests first within every task: the failing test is written and observed failing before the change that makes it pass.
- Do NOT modify anything under `skills/`, `hooks/`, or `commands/` — the skill contract is untouched this cycle.
- `evals.json` and all test code stay pure ASCII.
- New git subprocess calls follow the runner's existing pattern: `subprocess.run(["git", ...], check=True, capture_output=True, text=True)` with NO `shell=` (matches the existing `git()` helper; the `shell=(os.name == "nt")` pattern is only for codex/claude .cmd shims).
- No new dependencies. `python -m pytest evals -q` must pass at the end of every task.
- Live-run artifacts go to the session scratchpad, never into the repo.

## File Structure

- `evals/multi-model-verify/evals.json` — expectation #1 reword (Task 1); `surface` field per case (Task 2).
- `evals/multi-model-verify/test_multi_model_verify.py` — clause-lock (Task 1); schema/rot/semantic pins (Task 2); `select_cases` unit tests + CLI mutual-exclusion test (Task 3). All new tests go in `class TestEvalFixtures` (line ~469).
- `evals/tools/run_behavioral_evals.py` — `select_cases` + git helpers + `--changed` CLI (Task 3).
- `CLAUDE.md` — one-sentence `--changed` mention (Task 3).
- `.claude-plugin/plugin.json` — version bump (Task 4).

---

### Task 1: Reword no-manufactured-objections expectation #1 (tests-first)

**Files:**
- Test: `evals/multi-model-verify/test_multi_model_verify.py` (add to `class TestEvalFixtures`)
- Modify: `evals/multi-model-verify/evals.json` (the `no-manufactured-objections` entry's `expectations[0]`)

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: the exact expectation string below, which Task 4's stability probe grades against.

The single canonical new string (used verbatim in both files; ASCII hyphens only):

```
No manufactured objections: the plan verdict is PASS (or converged with only trivial accepted amendments), every noted risk cites a real file line, no noted risk is treated as blocking - it triggers no FIX or ESCALATE verdict, no additional round, and no scope change; an explicit non-blocking label is sufficient but not required - and nothing expands the plan's scope
```

- [ ] **Step 1: Write the failing clause-lock test**

Add to `class TestEvalFixtures` in `test_multi_model_verify.py`:

```python
    def test_no_manufactured_objections_grades_outcome_not_label(self):
        # 0.11.0: recovered 0.10.0 grader rationales showed expectation #1
        # flipping on whether a noted risk was literally LABELED
        # "non-blocking" while verdict/citations/scope were all correct.
        # The clause is pinned in its outcome-based form so it cannot
        # silently drift back to grading word choice.
        case = next(c for c in json.loads(read(EVALS_DIR / "evals.json"))["evals"]
                    if c["id"] == "no-manufactured-objections")
        assert case["expectations"][0] == (
            "No manufactured objections: the plan verdict is PASS (or"
            " converged with only trivial accepted amendments), every noted"
            " risk cites a real file line, no noted risk is treated as"
            " blocking - it triggers no FIX or ESCALATE verdict, no"
            " additional round, and no scope change; an explicit"
            " non-blocking label is sufficient but not required - and"
            " nothing expands the plan's scope"
        )
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q -k grades_outcome_not_label`
Expected: FAIL on the equality assert (the file still holds the old "is explicitly non-blocking" clause).

- [ ] **Step 3: Edit evals.json**

In the `no-manufactured-objections` entry, replace `expectations[0]` (currently `"No manufactured objections: the plan verdict is PASS (or converged with only trivial accepted amendments), every noted risk cites a real file line and is explicitly non-blocking, and nothing expands the plan's scope"`) with the canonical string above, as one JSON string on one line.

- [ ] **Step 4: Run the full suite**

Run: `python -m pytest evals -q`
Expected: PASS (no other test pins the old wording).

- [ ] **Step 5: Commit**

```bash
git add evals/multi-model-verify/evals.json evals/multi-model-verify/test_multi_model_verify.py
git commit -m "0.11.0: reword no-manufactured-objections expectation 1 to grade outcome"
```

---

### Task 2: Add surface fields to every case (tests-first)

**Files:**
- Test: `evals/multi-model-verify/test_multi_model_verify.py` (extend `test_evals_schema`; add two tests to `class TestEvalFixtures`)
- Modify: `evals/multi-model-verify/evals.json` (every entry)

**Interfaces:**
- Consumes: nothing from Task 1 (independent edits to different entries/keys).
- Produces: `entry["surface"]` — a non-empty list of repo-relative forward-slash globs — consumed by Task 3's `select_cases` and by Task 4's dogfood run.

- [ ] **Step 1: Write the failing tests**

In `test_evals_schema`, after the existing per-entry asserts (the `setup` assert block), add:

```python
            # 0.11.0: every case declares the contract files it exercises;
            # the --changed flag trims the battery by intersecting this
            # surface with the diff.
            assert entry.get("surface"), (
                f"case {entry['id']} needs a surface list")
            assert all(isinstance(s, str) and s.strip() and "\\" not in s
                       for s in entry["surface"]), (
                f"case {entry['id']} surface globs must be forward-slash"
                " repo-relative strings")
```

Add two new tests to `class TestEvalFixtures`:

```python
    def test_surface_globs_match_tracked_files(self):
        # A surface glob that matches nothing tracked is rot: the mapping
        # would silently stop selecting its case.
        import fnmatch
        data = json.loads(read(EVALS_DIR / "evals.json"))
        tracked = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "ls-files"],
            check=True, capture_output=True, text=True,
        ).stdout.splitlines()
        for entry in data["evals"]:
            for glob in entry["surface"]:
                assert any(fnmatch.fnmatch(p, glob) for p in tracked), (
                    f"case {entry['id']} surface glob {glob!r} matches no"
                    " tracked file")

    def test_surface_semantic_pins(self):
        # The mapping's load-bearing rows, pinned so a refactor cannot
        # quietly decouple a case from the contract file it tests:
        # SKILL.md is every case's contract; the consent gate lives in
        # fallbacks.md; both fix cases grade application-checkpoint.md;
        # the three debate cases grade debate discipline, whose contract
        # is debate-protocol.md (Sol plan round 1, F2).
        data = json.loads(read(EVALS_DIR / "evals.json"))
        surfaces = {e["id"]: e["surface"] for e in data["evals"]}
        for cid, surface in surfaces.items():
            assert "skills/multi-model-verify/SKILL.md" in surface, (
                f"case {cid} must include the skill body in its surface")
        assert ("skills/multi-model-verify/references/fallbacks.md"
                in surfaces["degraded-consent-gate"])
        for cid in ("fix-application-checkpoint",
                    "fix-checkpoint-attended-stop"):
            assert ("skills/multi-model-verify/references/application-checkpoint.md"
                    in surfaces[cid])
        for cid in ("plan-mode-debate-runs", "diff-mode-spec-fidelity",
                    "no-manufactured-objections"):
            assert ("skills/multi-model-verify/references/debate-protocol.md"
                    in surfaces[cid])
```

- [ ] **Step 2: Run to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q -k "evals_schema or surface"`
Expected: FAIL — `test_evals_schema` on the missing `surface` key; the two new tests on KeyError/missing key.

- [ ] **Step 3: Add surface fields to evals.json**

Add a `"surface"` key to every entry (place it right after `"setup"`), with exactly these values:

| case id | surface |
|---|---|
| plan-mode-debate-runs | `["skills/multi-model-verify/SKILL.md", "skills/multi-model-verify/references/model-prompting-notes.md", "skills/multi-model-verify/references/debate-protocol.md"]` |
| diff-mode-spec-fidelity | `["skills/multi-model-verify/SKILL.md", "skills/multi-model-verify/references/model-prompting-notes.md", "skills/multi-model-verify/references/debate-protocol.md"]` |
| degraded-consent-gate | `["skills/multi-model-verify/SKILL.md", "skills/multi-model-verify/references/fallbacks.md"]` |
| missing-reference-refusal | `["skills/multi-model-verify/SKILL.md"]` |
| fix-application-checkpoint | `["skills/multi-model-verify/SKILL.md", "skills/multi-model-verify/references/application-checkpoint.md"]` |
| fix-checkpoint-attended-stop | `["skills/multi-model-verify/SKILL.md", "skills/multi-model-verify/references/application-checkpoint.md"]` |
| no-manufactured-objections | `["skills/multi-model-verify/SKILL.md", "skills/multi-model-verify/references/model-prompting-notes.md", "skills/multi-model-verify/references/debate-protocol.md"]` |

(The three debate cases carry `debate-protocol.md`: it is required reading
before round 1 and both modes iterate under it — Sol plan round 1, F2.)

- [ ] **Step 4: Run the full suite**

Run: `python -m pytest evals -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add evals/multi-model-verify/evals.json evals/multi-model-verify/test_multi_model_verify.py
git commit -m "0.11.0: declare per-case contract surfaces in evals.json"
```

---

### Task 3: select_cases + --changed flag + CLAUDE.md note (tests-first)

**Files:**
- Test: `evals/multi-model-verify/test_multi_model_verify.py` (module-level loader helper + tests in `class TestEvalFixtures`)
- Modify: `evals/tools/run_behavioral_evals.py`
- Modify: `CLAUDE.md` (Verification section)

**Interfaces:**
- Consumes: `entry["surface"]` from Task 2.
- Produces: `select_cases(cases, changed_paths, base_entries) -> (selected, skipped)` where `selected` is a list of `(case_dict, reason_str)` and `skipped` a list of `case_dict`; `parse_base_entries(text) -> {id: entry} | None` (pure loader, fail-toward-running); CLI flag `--changed [REF]`. Task 4 invokes the flag.

- [ ] **Step 1: Write the failing unit tests**

Add a module-level helper to `test_multi_model_verify.py` (after the `read()` helper, before the first class):

```python
def load_runner_module():
    """Import the behavioral runner as a module (its main() is guarded, its
    module level is constants only) so pure functions are unit-testable."""
    import importlib.util
    path = REPO_ROOT / "evals" / "tools" / "run_behavioral_evals.py"
    spec = importlib.util.spec_from_file_location("run_behavioral_evals", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
```

Add to `class TestEvalFixtures`:

```python
    def _trim_cases(self):
        return [
            {"id": "a", "prompt": "p", "expectations": ["x"],
             "surface": ["skills/multi-model-verify/SKILL.md"]},
            {"id": "b", "prompt": "p", "expectations": ["x"],
             "surface": ["skills/multi-model-verify/references/fallbacks.md"]},
        ]

    def test_select_cases_surface_match_selects(self):
        runner = load_runner_module()
        cases = self._trim_cases()
        base = {c["id"]: json.loads(json.dumps(c)) for c in cases}
        selected, skipped = runner.select_cases(
            cases, ["skills/multi-model-verify/SKILL.md"], base)
        assert [c["id"] for c, _ in selected] == ["a"]
        assert selected[0][1] == "skills/multi-model-verify/SKILL.md"
        assert [c["id"] for c in skipped] == ["b"]

    def test_select_cases_backslash_paths_normalized(self):
        # git on Windows can hand back backslash separators; the mapping is
        # declared forward-slash, so selection must normalize before match.
        runner = load_runner_module()
        cases = self._trim_cases()
        base = {c["id"]: json.loads(json.dumps(c)) for c in cases}
        selected, _ = runner.select_cases(
            cases, ["skills\\multi-model-verify\\SKILL.md"], base)
        assert [c["id"] for c, _ in selected] == ["a"]

    def test_select_cases_entry_diff_self_selects(self):
        # An edited grading contract re-selects its case even when no
        # surface file changed.
        runner = load_runner_module()
        cases = self._trim_cases()
        base = {c["id"]: json.loads(json.dumps(c)) for c in cases}
        base["b"]["expectations"] = ["OLD WORDING"]
        selected, skipped = runner.select_cases(cases, [], base)
        assert [c["id"] for c, _ in selected] == ["b"]
        assert "changed" in selected[0][1]
        assert [c["id"] for c in skipped] == ["a"]

    def test_select_cases_surface_only_diff_does_not_select(self):
        # Selection metadata is not grading contract: refining a surface
        # list must not re-run the battery (otherwise the commit that
        # INTRODUCES surfaces re-selects all 7 cases - the opposite of a
        # trim).
        runner = load_runner_module()
        cases = self._trim_cases()
        base = {c["id"]: json.loads(json.dumps(c)) for c in cases}
        base["a"]["surface"] = ["some/old/glob.md"]
        selected, skipped = runner.select_cases(cases, [], base)
        assert selected == []
        assert [c["id"] for c in skipped] == ["a", "b"]

    def test_select_cases_unreadable_base_selects_all(self):
        # Fail toward running, never toward skipping.
        runner = load_runner_module()
        cases = self._trim_cases()
        selected, skipped = runner.select_cases(cases, [], None)
        assert [c["id"] for c, _ in selected] == ["a", "b"]
        assert skipped == []

    def test_parse_base_entries_structurally_invalid_returns_none(self):
        # {"evals": null} is valid JSON that raises TypeError, not
        # JSONDecodeError, during iteration - the loader must fail toward
        # running (None), never crash selection (Sol plan round 1, F1).
        runner = load_runner_module()
        assert runner.parse_base_entries('{"evals": null}') is None
        assert runner.parse_base_entries('{"evals": [null]}') is None
        assert runner.parse_base_entries('not json at all') is None
        assert runner.parse_base_entries('{"evals": [{"id": "a"}]}') == {
            "a": {"id": "a"}}

    def test_changed_and_case_flags_are_mutually_exclusive(self):
        proc = subprocess.run(
            [sys.executable,
             str(REPO_ROOT / "evals" / "tools" / "run_behavioral_evals.py"),
             "--changed", "--case", "plan-mode-debate-runs"],
            capture_output=True, text=True)
        assert proc.returncode == 2
        assert "mutually exclusive" in (proc.stderr or "")
```

- [ ] **Step 2: Run to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q -k "select_cases or mutually_exclusive or parse_base_entries"`
Expected: FAIL — AttributeError (`select_cases` / `parse_base_entries` do not exist); the CLI test fails on the missing "mutually exclusive" stderr text (an unknown flag also exits 2, so the text assert is what makes this test genuinely fail first).

- [ ] **Step 3: Implement in run_behavioral_evals.py**

Add `import fnmatch` to the imports block. Add after `load_cases()`:

```python
def _grading_view(entry):
    """A case entry minus selection metadata: `surface` says WHICH files
    select the case, it is not part of what the grader enforces."""
    return {k: v for k, v in entry.items() if k != "surface"}


def select_cases(cases, changed_paths, base_entries):
    """Pure --changed selection. Returns (selected, skipped): selected is
    [(case, reason)] where reason is the first matching changed path or an
    entry-diff note; skipped is [case]. base_entries is {id: entry} parsed
    from the base evals.json, or None when that file was missing or
    unparseable - then EVERY case is selected (fail toward running, never
    toward skipping)."""
    changed = [p.replace("\\", "/") for p in changed_paths]
    selected, skipped = [], []
    for case in cases:
        if base_entries is None:
            selected.append((case, "base evals.json unreadable"))
            continue
        reason = next((p for p in changed
                       for g in case.get("surface", ())
                       if fnmatch.fnmatch(p, g)), None)
        if reason is None:
            base = base_entries.get(case["id"])
            if base is None or _grading_view(case) != _grading_view(base):
                reason = "case entry changed vs base"
        if reason is None:
            skipped.append(case)
        else:
            selected.append((case, reason))
    return selected, skipped


def _git_lines(*args):
    out = subprocess.run(["git", "-C", str(PLUGIN_ROOT), *args],
                         check=True, capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    return [ln.strip() for ln in out.stdout.splitlines() if ln.strip()]


def resolve_changed_base(ref):
    if ref is not None:
        return ref
    return _git_lines("merge-base", "HEAD", "main")[0]


def changed_paths_vs(base):
    """Committed + uncommitted (working tree vs base) plus untracked."""
    return (_git_lines("diff", "--name-only", base)
            + _git_lines("ls-files", "--others", "--exclude-standard"))


def parse_base_entries(text):
    """{id: entry} from a base evals.json text, or None when the text is
    syntactically OR structurally unparseable - {"evals": null} is valid
    JSON that raises TypeError, not JSONDecodeError, during iteration
    (Sol plan round 1, F1). None makes select_cases run everything."""
    try:
        return {c["id"]: c for c in json.loads(text)["evals"]}
    except (json.JSONDecodeError, KeyError, TypeError):
        return None


def base_case_entries(base):
    try:
        out = subprocess.run(
            ["git", "-C", str(PLUGIN_ROOT), "show",
             f"{base}:evals/multi-model-verify/evals.json"],
            check=True, capture_output=True, text=True,
            encoding="utf-8", errors="replace")
    except subprocess.CalledProcessError:
        return None
    return parse_base_entries(out.stdout)
```

In `main()`, add the flag next to `--case`:

```python
    ap.add_argument("--changed", nargs="?", const="", default=None,
                    metavar="REF",
                    help="run only cases whose declared surface intersects"
                         " the diff vs REF (default: merge-base with main)"
                         " or whose own evals.json entry changed; prints"
                         " every skip by name")
```

Immediately after `args = ap.parse_args(argv)`:

```python
    if args.changed is not None and args.case:
        ap.error("--changed and --case are mutually exclusive")
```

After the `if args.list:` block and BEFORE the CLI tool checks (a doc-only diff must be reportable without claude/codex installed; `--list` itself stays git-free for CI):

```python
    if args.changed is not None:
        base = resolve_changed_base(args.changed or None)
        selected, skipped = select_cases(
            cases, changed_paths_vs(base), base_case_entries(base))
        for c in skipped:
            print(f"SKIPPED(unchanged surface) {c['id']}")
        for c, reason in selected:
            print(f"SELECTED {c['id']} - {reason}")
        if not selected:
            print("no behavioral surface touched")
            return 0
        cases = [c for c, _ in selected]
```

- [ ] **Step 4: Run the new tests, then the full suite**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q -k "select_cases or mutually_exclusive or parse_base_entries"`
Expected: PASS.
Run: `python -m pytest evals -q`
Expected: PASS (the `--list` self-test at test_behavioral_runner_self_test must still pass unchanged).

- [ ] **Step 5: Add the CLAUDE.md sentence**

In `CLAUDE.md`, inside the Verification section's behavioral bullet, extend the parenthetical so the bullet reads:

```
- skill/prompt changes -> `python evals/tools/run_behavioral_evals.py`
  (real headless runs, graded by the cross-vendor reviewer; `--head` tests
  the checkout instead of the installed cache; for small contract edits
  `--changed` runs only cases whose declared surface intersects the diff
  vs main, printing every skip by name).
```

- [ ] **Step 6: Commit**

```bash
git add evals/tools/run_behavioral_evals.py evals/multi-model-verify/test_multi_model_verify.py CLAUDE.md
git commit -m "0.11.0: add --changed surface-trimmed selection to behavioral runner"
```

---

### Task 4: Live verification battery + version bump (CONTROLLER-RUN)

This task is executed by the session controller, not a subagent — background
suites launched inside a subagent died silently in the 0.10.0 cycle
(~66 min, no processes, no notification). Quota context: the weekly codex
window was 91% used at cycle start; this task spends ~3 grader calls.

**Files:**
- Modify: `.claude-plugin/plugin.json` (version `0.10.0` -> `0.11.0`)

**Interfaces:**
- Consumes: Tasks 1-3 all committed; `--changed` and the reworded expectation live on the branch.
- Produces: the evidence block for the diff-mode debate and the application checkpoint.

- [ ] **Step 1: Full offline gates**

Run, from the repo root:

```
python evals/tools/skill_lint.py skills/multi-model-verify --strict
python evals/tools/skill_scanner.py skills
python evals/tools/run_trigger_evals.py
python -m pytest evals -q
```

Expected: all green (pytest count grows from 123 passed / 1 skipped by the new tests; record the exact count).

- [ ] **Step 2: Stability probe runs 1 and 2 (--case)**

Run twice, sequentially, artifacts to the session scratchpad:

```
python evals/tools/run_behavioral_evals.py --head --case no-manufactured-objections --artifacts <scratchpad>/eval-trim-stability/run1
python evals/tools/run_behavioral_evals.py --head --case no-manufactured-objections --artifacts <scratchpad>/eval-trim-stability/run2
```

Expected: `PASS no-manufactured-objections - 3/3 expectations met` both times. Any FAIL stops the task: apply superpowers:systematic-debugging to the grader rationale in the run's `verdicts.json` before burning more quota.

- [ ] **Step 3: Stability probe run 3 doubles as the --changed dogfood**

Run:

```
python evals/tools/run_behavioral_evals.py --head --changed --artifacts <scratchpad>/eval-trim-stability/run3
```

Expected, in order: six `SKIPPED(unchanged surface)` lines, exactly one `SELECTED no-manufactured-objections - case entry changed vs base` line (only its grading view differs from merge-base; surface additions are excluded from the diff), then the case runs and reports PASS. This is simultaneously stability run 3 of 3 and the spec's dogfood demonstration — capture the full stdout to `<scratchpad>/eval-trim-stability/run3.log`.

- [ ] **Step 4: Version bump and commit**

Edit `.claude-plugin/plugin.json`: `"version": "0.10.0"` -> `"version": "0.11.0"`.

```bash
git add .claude-plugin/plugin.json
git commit -m "0.11.0: bump plugin version"
```

- [ ] **Step 5: Record evidence**

Collect into the cycle's evidence note (for the diff debate): gate outputs from Step 1, the three PASS lines with artifact paths, the run3 selection printout, and the quota reading before/after (app-server `account/rateLimits/read`).

---

## Debate record

**Participants:** Fable 5 (session) / GPT-5.6 Sol (codex exec, session 019f97d1-fc78-73a1-9f32-b42e14a6f8c1)
**Rounds used:** 2 of 4
**Outcome:** converged with amendments (round-1 FIXes F1-F3 accepted, applied at 77013d3, verified PASS in round 2)
**Verification status:** FULL
**Degradation:** none
**Authorized by:** n/a
**Raw rounds:** docs/superpowers/plans/rounds/2026-07-25-eval-trim/ (briefs, replies, and header-bearing transcripts for both rounds)

### Resolved points
| # | Claim | Raised by | Outcome | Evidence |
|---|-------|-----------|---------|----------|
| 1 | base-evals.json loader crashes instead of failing toward running on structurally invalid JSON (`{"evals": null}` raises TypeError, uncaught) | reviewer (F1) | accepted into Task 3: pure `parse_base_entries` catches TypeError; loader-level test added | docs/superpowers/plans/2026-07-25-behavioral-eval-trim.md:374-394, :291-300 |
| 2 | debate-protocol.md is missing from the three debate cases' surfaces despite being required reading that both modes iterate under | reviewer (F2) | accepted into Task 2: surface rows + semantic pins extended | docs/superpowers/plans/2026-07-25-behavioral-eval-trim.md:169-184, :140-161; skills/multi-model-verify/SKILL.md:18 |
| 3 | "the same bar D3 used" misstates history — D3's record is fail/fail/pass pre-fix plus ONE confirming full-case PASS post-fix | reviewer (F3) | accepted into spec: reworded as a deliberately stricter bar | docs/superpowers/specs/2026-07-25-behavioral-eval-trim-design.md:122-126; docs/superpowers/plans/2026-07-24-jinn-intake-adoptions.md:281 |
| 4 | Claims 1-3, 5, 7 of the round-1 brief (cost model, flake diagnosis, reword soundness, surface-key exclusion, harness boundary) and the amended claims 4, 6, 8 | session | confirmed PASS by reviewer (round 1: five PASS; round 2: overall PASS) | rounds/2026-07-25-eval-trim/plan-round1-reply.txt, plan-round2-reply.txt |

### Escalated points (user-decided)
| # | Question | Session position | Reviewer position | Owner's call |
|---|----------|------------------|-------------------|--------------|

### Environment notes (non-blocking)
- `~/.codex/AGENTS.md` exists — the user's own global instruction file, by design.
- Skills from the user's own codex plugin cache load into the reviewer's context, by design.
- Both rounds' transcripts open with `ERROR codex_models_manager::cache: failed to load models cache: missing field supports_reasoning_summaries` — local models-cache noise; the startup header still resolved and matched the canonical route both rounds. Watch in drift triage if it persists.

---

## Self-Review (done at write time)

- **Spec coverage:** `--changed` semantics → Task 3; surface mapping → Task 2; expectation reword → Task 1; offline tests → Tasks 1-3; stability probe + dogfood + no-full-battery → Task 4; version bump → Task 4. The spec's "surface key excluded from entry diff" amendment is implemented in `_grading_view` and locked by `test_select_cases_surface_only_diff_does_not_select`.
- **Placeholder scan:** no TBDs; every code step carries the actual code; `<scratchpad>` is the session scratchpad directory, resolved by the controller at run time (it is session-specific by design).
- **Type consistency:** `select_cases` returns `(selected, skipped)` with `selected = [(case, reason)]` in every task that names it; `base_entries` is `{id: entry}` or `None` everywhere; the canonical expectation string in Task 1's test and edit steps is character-identical.
