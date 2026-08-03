# Execution deviations — home skills root probe

The frozen plan is `docs/superpowers/plans/2026-08-03-home-skills-root-probe.md`
at revision 6. A zero-judgment implementer makes no design decisions, so every
departure from the frozen text is recorded here as it happens, and the diff
debate adjudicates each one against the plan.

Nothing in this file amends the plan. The plan is frozen.

---

## D1 — Task 1 Step 1: the oracle's staleness clause could not fail as frozen

**Task:** 1. **Step:** 1. **Class:** plan defect, found by executing the plan's
own Step 2 check.

**What the plan froze.** The test body asserted the retired sentence's absence
against `_norm`, the suite's existing whitespace-normalizing reader:

```python
body = _norm(REPO / rel)
assert "CI does not exercise these 155 cases at all" not in body
```

**What running it showed.** `_norm` is `" ".join(text.split())`. It joins a
wrapped comment's lines but leaves each continuation line's `#` inside the
sentence, so the live text at `evals/multi-model-verify/test_codex_context_probe.py:50-51`
normalizes to:

```
CI is Linux, so CI does # not exercise these 155 cases at all.
```

The asserted string therefore never occurred in `body` under any state of the
file, and the clause was vacuously true — a check that could not fail, sitting
inside the fix for a false record of coverage. Confirmed directly:
`'CI does not exercise these 155 cases at all' in norm` returned `False`
against the UNCORRECTED file, where it must have returned `True`.

**How it was caught.** The plan's Step 2 names the clause the first run must
fail on. The run failed on the SECOND clause instead
(`"Backlog item 10 carries the fix"`, which happens to sit entirely on one
line and so survives the join). A test failing for a different reason than the
one claimed proves nothing, which is the rule that turned a green-looking
failure into this finding.

**The deviation.** A local helper was added inside the test, stripping Python
comment markers before normalizing, and the two staleness assertions were
repointed at it. `_norm` is unchanged and no other pin is affected.

```python
def uncommented(path):
    lines = [re.sub(r"^\s*#\s?", "", ln)
             for ln in path.read_text(encoding="utf-8").splitlines()]
    return " ".join(" ".join(lines).split())
```

**Verification after the change.** The test was re-run and failed on the FIRST
staleness clause, which is what the plan predicted and what the frozen form
could not do.

**Two reviewers read this assertion and neither caught it.** The Kimi lane
positively asserted the opposite — that `_norm`'s whitespace-join "makes the
expected failure fire, since the live text at
`test_codex_context_probe.py:50-51` normalizes into the asserted string"
(`kimi-r1-reply.md`, the "Verified sound" section). That claim is false, and
only executing it settled the question. Recorded because the debate record
should not read as though the plan arrived defect-free.

---

## D2 — Task 1 Step 7: mutation M3 named the other host

**Task:** 1. **Step:** 7. **Class:** prediction imprecision, no code change.

The plan predicts that moving both module occurrences into one host step
"must fail naming `pwsh.exe`". It failed naming `powershell.exe`, because the
mutation duplicated the entry in the 5.1 step and that step is checked first.

The property under test — the per-step parity clause fires while the total
occurrence count is still 2, which a count-based oracle would have passed — is
demonstrated either way. No change made. Recorded so the diff debate does not
read the transcript as a mismatch.

---

## D3 — Task 1 Step 7: the mutation harness rewrote line endings on revert

**Task:** 1. **Step:** 7. **Class:** driver tooling error, caught before commit,
no plan defect.

The mutation script read `.github/workflows/skill-evals.yml` with Python's
`read_text`, which converts CRLF to LF under universal newlines, and wrote the
original string back with `newline=""`, which writes exactly what it is given.
The revert therefore restored the CONTENT byte-for-byte while converting all
112 line endings from CRLF to LF. This repo checks out with `core.autocrlf=true`.

`git diff` reported no content change, because git normalizes line endings when
comparing, and printed only a warning. `git status --porcelain` DID list the
file as modified. It was not staged — Task 1 stages by explicit path — so
nothing entered the commit, and the file was restored with `git checkout --`
immediately afterwards. Verified after restore: 112 CRLF, 0 bare LF, working
tree clean, and the oracle still passes.

**Why this is recorded rather than dropped.** It is the same family as the
autocrlf blob trap this project hit in 0.14.2. A mutation harness that silently
rewrites every line ending of a file it was only supposed to read and restore
would, under `git add -A`, have produced a whole-file diff attributed to a
two-line test change. The standing rule against `git add -A` is what contained
it, which is worth having on the record as a control that actually fired.

---

## Verification state at this point

- `test_backup_lane.py`: 59 passed under `powershell.exe` AND under `pwsh.exe`.
- Full suite: 934 passed, 13 skipped (the 13 are the opt-in live lane gate).
  The baseline before Task 1 was 933; the new oracle is the one added case.
- Three mutations run, each watched to fail naming its own clause, each reverted,
  and the post-revert run clean.
