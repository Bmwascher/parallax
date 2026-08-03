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
repointed at it. `_norm` itself is unchanged and no other pin is affected.

**AMENDED after the Fable review.** The sentence above originally read "`_norm`
is unchanged and no other pin is affected", which the reviewer correctly read
as a claim that nothing ELSE in this task departed from the frozen text. That
was false: three further departures went unrecorded, and they are now D4, D5
and D6 below. The claim is narrowed to what it can support — the shared `_norm`
helper is untouched and no OTHER test's pin changed — and the completeness
claim is withdrawn. A ledger the diff debate adjudicates from cannot carry a
false statement of its own completeness.

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

## D4 — Task 1 Step 1: the frozen test read the workflow through `_norm`, which cannot work

**Task:** 1. **Step:** 1. **Class:** plan defect, repaired silently by the
session and recorded only after the Fable review named it. **Found by:**
`agents/fable-reviewer.md`, range `e94c0b5..fbefa66`.

**What the plan froze** (plan line 173):

```python
workflow = _norm(REPO / ".github" / "workflows" / "skill-evals.yml")
```

**Why it cannot work.** `_norm` is `" ".join(text.split())`, which destroys
every newline. The step slicing immediately below it splits on
`"\n      - name:"`. Measured directly against the real workflow: under `_norm`,
`"\n" in workflow` is `False` and `"\n      - name:" in workflow` is `False`.
Both host slices would therefore run to end of file, the `powershell.exe` slice
would contain BOTH steps, and `step.count(rel) == 1` would fail against the
CORRECT workflow.

**What shipped:** `_read`, the raw reader, at `test_backup_lane.py:1520`.

**Why this is the serious one.** Plan Step 2 names this exact branch as a STOP:
"If it fails on the per-step slicing instead, STOP: the workflow is not what
this plan measured." Under the frozen form the first run would have taken that
branch. The session substituted `_read` while writing the test, so the STOP
was never reached and the substitution was never recorded — a zero-judgment
implementer made a judgment call, and the ledger the diff debate adjudicates
from did not carry it.

**Disposition.** The substitution is correct on the merits and rides. The defect
recorded here is the SILENCE, not the code.

---

## D5 — Task 1 Step 4: the mirror header was not replaced verbatim

**Task:** 1. **Step:** 4. **Class:** unrecorded departure from frozen text.
**Found by:** the Fable review.

Step 4 directs that `test_review_mirror.py:31-34` — the "Guarding only on a
PowerShell host being present..." paragraph — be REPLACED with a `COVERAGE`
block whose text includes "See the probe suite's header for the full sequence."

What shipped instead: the "Guarding only..." paragraph was RETAINED, its closing
clause reworded to end at "sequence.", and the `COVERAGE` block was added below
it WITHOUT the "See the probe suite's header" sentence. Every fact the frozen
text carries is present, and the reviewer confirmed the resulting header claims
exactly what is true. It is nonetheless not the frozen text.

**Disposition.** Rides. Recorded so the diff debate adjudicates a departure it
can see rather than discovering one it cannot.

---

## D6 — Task 1 Step 5: the backlog carries a fourth paragraph

**Task:** 1. **Step:** 5. **Class:** unrecorded addition to frozen text.
**Found by:** the Fable review.

Step 5 freezes a three-paragraph insert under item 10's new heading. A fourth
paragraph was added, "One thing that oracle taught, worth keeping," recording
D1's vacuous-assertion defect in the backlog itself.

**Disposition.** Rides. The addition is accurate and the reviewer verified it
does not trip the new oracle, which scans only the two module bodies. Recorded
because "verbatim" admits no additions either.

---

## D7 — Task 1 Step 7: the job-name clause was unwatched, and is now watched

**Task:** 1. **Step:** 7. **Class:** plan scope gap, closed. **Found by:** the
Fable review.

The plan's three mutations cover the staleness clauses and the per-step parity
clause. They do not touch `assert "powershell-hosts" in body`
(`test_backup_lane.py:1533-1534`), and the initial failing run stopped at an
earlier assert, so that clause had never been watched to fail. By this plan's
own Global Constraint an unwatched assertion is not yet evidence.

**Closed.** Two further mutations were run, one per covered module, each
replacing the job name in that module's header:

- `M4a probe header` — fails with `evals/multi-model-verify/test_codex_context_probe.py must name the CI job that covers it`
- `M4b mirror header` — fails with `evals/multi-model-verify/test_review_mirror.py must name the CI job that covers it`

Both reverted; the post-revert run is clean. **D3's lesson was applied here:**
this harness reads and writes BYTES rather than text, so the revert cannot
rewrite line endings. The working tree was verified clean afterwards, where the
Step 7 harness had left a whole-file line-ending change.

---

## Commit-trailer check, closing the reviewer's named gap

The Fable review could not verify commit bodies from the diff package and named
that as a gap rather than assuming. Closed by the session:
`git log e94c0b5..fbefa66 --format=%B` searched for `Claude-Session` returns 0
across all three full commit bodies. The authorized-debt decision permits
exactly three such trailers in this repo's history; a fourth would be a defect,
and this range adds none.

---

## Task 2 — three platform facts the plan could not have known

None of these is a departure from frozen text. Each is a defect found by
running the suite, and each is the case-insensitivity or environment class this
repo already tracks. They are recorded here because the next task's implementer
will hit the same ground.

### P1 — `Get-FileHash` disappears under an inherited PowerShell 7 `PSModulePath`

The first draft hashed with `Get-FileHash`. Run by hand from a PowerShell 7
shell it worked; run as a Windows PowerShell 5.1 child of a Python process it
died with `The term 'Get-FileHash' is not recognized`.

Measured 2026-08-03. The environment carries a `PSModulePath` seeded by
PowerShell 7 — `C:\Program Files\PowerShell\Modules` and
`c:\program files\powershell\7\Modules` ahead of the Windows PowerShell entry —
and under it a 5.1 child resolves `Microsoft.PowerShell.Utility` to the
PowerShell 7 copy. Enumerated directly: `ConvertTo-Json`, `ConvertFrom-Json`,
`Compare-Object`, `Sort-Object`, `Get-ChildItem` and `Set-Content` all resolve;
`Get-FileHash` alone does not.

**This is the environment the tests and the probe driver both use**, so a tool
that depends on it is a tool that works only when the right host seeded the
shell. Hashing is now `[System.Security.Cryptography.SHA256]` over
`[System.IO.File]::ReadAllBytes`, which depends on no module at all.

### P2 — a local `$state` silently became the `[string]$State` parameter

The state file was written as the literal text
`"System.Collections.Specialized.OrderedDictionary"`, and every Remove case
failed downstream on unreadable JSON.

PowerShell variable names are CASE-INSENSITIVE. The script declares
`[string]$State` for the Remove parameter set, so `$state = [ordered]@{...}` in
the Plant branch assigned to that same variable — whose `[string]` type
constraint coerced the hashtable through `ToString()`. The value was destroyed
before `ConvertTo-Json` ever saw it.

The three `ConvertTo-Json` call forms were checked and are all sound
(positional, pipeline and `-InputObject` each produce correct JSON on 5.1.26100).
The collision was the whole defect. The local is now `$stateObj`.

**This is the same family as the `Compare-Object` and allowlist-casing defects
already on this repo's record**, in a new place: not a comparison folding case,
but a NAME folding case, with a type constraint turning the collision into
silent data loss rather than an error.

### P3 — `-notmatch` accepted an uppercase nonce

`$Nonce -notmatch '\A[0-9a-f]{32}\z'` reads as lowercase-only and is not:
PowerShell's `-match`/`-notmatch` are case-INSENSITIVE by default, so
`0123456789ABCDEF0123456789ABCDEF` passed. The suite's uppercase case caught it.
Now `-cnotmatch`.

---

## D8 — Task 2: the exact-canary-path check guards less than the plan says

**Task:** 2. **Class:** plan rationale wider than the mechanism. No code change.

The plan justifies the exact path equality this way: "removal deletes that path
recursively, so anything short of exact equality lets a hand-edited state file
aim a recursive delete at a sibling directory the harness never created."

That attack is NOT reachable in the shipped tool, and was not reachable in any
draft of it. `Remove-Item` targets `$canaryPath`, which is derived from `-Root`
by `Join-Path $resolvedRoot $CANARY_NAME` — never from the state file. A state
file cannot aim the delete anywhere, because the delete never reads it.

What the check actually does, stated at its true reach: it refuses a state file
belonging to a DIFFERENT root, whose `before` list would otherwise be compared
against this root's contents and would report nonsense. That is worth having and
the check stays.

The mutation still fails the test it claims — relaxing equality to a
`StartsWith` prefix test lets the removal proceed and exit 0 where the test
requires 1 — so the guard is proven meaningful. Only the plan's stated reason for
it is wider than the code. Recorded rather than silently kept, per D4's lesson.

---

## Verification state at this point

- `test_backup_lane.py`: 59 passed under `powershell.exe` AND under `pwsh.exe`.
- Full suite: 934 passed, 13 skipped (the 13 are the opt-in live lane gate).
  The baseline before Task 1 was 933; the new oracle is the one added case.
- **FIVE mutations run**, each watched to fail naming its own clause, each
  reverted, and each post-revert run clean: the three the plan specifies, plus
  the two D7 adds. Every load-bearing assertion in the new oracle has now been
  watched to fail for the reason it claims.
- Whole-branch review by `agents/fable-reviewer.md` over `e94c0b5..fbefa66`,
  retained at `fable-review-e94c0b5-fbefa66.md`. Verdict at the time of issue:
  **Ready to merge: With fixes** — no Critical, one Important (this ledger being
  narrower than the diff), two Minor. Every finding was verified against the
  repo and accepted; D4, D5, D6 and D7 and the trailer check are those fixes.
- **What this review is NOT.** It is one Claude-family seat reviewing one task
  of six. It does not replace the cross-vendor gate, and no mode-diff debate has
  run on this range.

### Task 2

- `test_home_skill_canary.py`: 26 passed under `powershell.exe` AND under
  `pwsh.exe`. `tools/plant-home-skill-canary.ps1` is 0 non-ASCII bytes.
- Full suite: 960 passed, 13 skipped. The 26 new cases are the whole delta from
  Task 1's 934.
- **Step 2 watched with the script absent: 26 failed, 0 passed.** Every failure
  was on an exit-code assertion, because PowerShell returns `4294770688` for a
  missing `-File` target and not `1` — so no "refuses" case passed vacuously
  against a tool that did not exist yet.
- **All six guard mutations run**, each failing the test it claims, each
  reverted, post-revert module clean at 26 passed:
  M1 dropping `-CaseSensitive`; M2 overwriting a leftover canary silently;
  M3 removing the profile-root refusal; M4 removing the reparse-point scan;
  M5 relaxing exact path equality to a prefix test; M6 skipping the
  contents-and-hash check, which fails BOTH the extra-entry and changed-hash
  cases as the plan requires.
- **M3 really did plant a canary in the user's real home**, which is what makes
  that refusal load-bearing rather than decorative. The harness removed it in a
  `finally` and the absence was verified afterwards: no
  `%USERPROFILE%\parallax-home-root-canary`, and `~/.agents/skills/` still holds
  its 27 directories, untouched throughout.
- The Task 2 mutation harness reads and writes BYTES, per D3. The working tree
  after all six carried only the two intended new files.
