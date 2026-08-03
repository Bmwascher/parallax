# Execution deviations — home skills root probe

The frozen plan is `docs/superpowers/plans/2026-08-03-home-skills-root-probe.md`
at revision 7. This line said revision 6 until the mode-diff gate on
`e94c0b5..5b312d8`: the plan was amended to revision 7 by the reopened debate
and this header was not moved with it, so the ledger named the wrong version of
the document it adjudicates against.
A zero-judgment implementer makes no design decisions, so every
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

## D9 — Task 2: the state-file parser was a tier-1c instance that evaded tier 1c

**Task:** 2. **Class:** defect in the session's own new oracle. **Found by:**
`agents/fable-reviewer.md`, range `e94c0b5..d0e116a`. **FIXED.**

`read_state` built `[ln for ln in raw.split("\n") if ln.strip()]` and asserted
exactly one survivor. That is the "discard blank lines, then count survivors"
idiom CLAUDE.md names, which accepts `\n\n{json}\n\n` where the frozen interface
says the state file is ONE line of ASCII JSON.

**And it was spelled so the gate could not see it.**
`evals/tools/check_exact_line_oracles.py:89-91` matches on
`gen.iter.func.attr == "splitlines"`. This instance used `.split("\n")`, so
tier 1c stayed green on the exact idiom it exists to remove. CLAUDE.md records
that three hand sweeps each missed an instance of this class; this is a fourth
spelling, written by the session that knew the rule.

Now routed through `accept_exactly_one_nonempty_line()` in
`evals/tools/exact_line.py`. Watched: mutation N1 makes the tool append a
trailing blank line and `test_plant_state_file_shape` fails.

---

## D10 — the tier-1c sweep did not see `.split("\n")`

**Class:** gap in an existing CI gate, demonstrated by D9. **Status: FIXED,
USER-AUTHORIZED 2026-08-03, and OUTSIDE the frozen plan's six tasks.**

The checker keyed on the attribute name `splitlines` alone, so D9's instance —
the same discard-then-count idiom written `raw.split("\n")` — passed CI
untouched. A whole-branch review caught what the gate could not. Counting the
three hand sweeps already on this repo's record, that is four spellings of one
defect class that a sweep has missed.

**Widened on the SEPARATOR, not the method name.** A line split is now
`.splitlines()` OR `.split(<sep>)` where `<sep>` is a string literal EQUAL to
one of the three line terminators, `"\n"`, `"\r\n"` or `"\r"`. `.split(",")` is
deliberately not matched, and neither is a composite separator such as
`"\n\n"`: those are field and paragraph parses, no contract there promises one
LINE, and a gate that fires on correct code gets suppressed.

**CORRECTED at the mode-diff round 1 on `e94c0b5..5b312d8`.** This entry and
the checker's own docstring both said `<sep>` was any string literal
*containing* a newline. The code has always tested exact membership in
`_NEWLINE_SEPARATORS`, so both descriptions were wider than the thing they
described. The reviewer offered either direction; the words moved, because
exact membership is the reach the gate should have.

**Tests first, in three directions**, all watched to fail before the checker
changed: `.split("\n")` is flagged, `.split("\r\n")` is flagged, `.split(",")`
is NOT. Verified afterwards that the checker flags the EXACT source that shipped
at `d0e116a` — `find_violations` returns `[(3, 'lines')]` against it — and that
the fixed file is clean.

The checker's docstring records the miss and widens its stated LIMIT rather than
quietly growing its reach: a `for` loop that appends, a `filter()` call, a regex
split, or a separator built at runtime are all still invisible to it, and that
is now written down.

**This change is outside the frozen plan.** The user authorized it explicitly on
2026-08-03 after it was surfaced as an open decision, in the same shape as
`51b4554` in the 0.19.0 cycle. It is recorded here as authorized off-plan work
so the diff debate adjudicates it as such rather than as drift.

---

## D11 — Task 2: the fault seam could not prove what the plan froze it to prove

**Task:** 2. **Class:** plan defect. **Found by:** the Fable review. **FIXED.**

The plan froze the seam as the rollback's positive control: "assert the
directory existed mid-call, via a fault seam that fires after creation and
before the state write, or the test passes equally against an implementation
that never created anything."

The seam alone cannot establish that. A tool checking
`PARALLAX_CANARY_STATE_FAULT` BEFORE `New-Item` emits the same message, the same
exit code and the same unchanged root, and passes every case in the file. The
docstring claimed an observation no test made.

Replaced with a real observation. An INHERIT-ONLY deny of Delete on the root
lets creation succeed and blocks the rollback's delete, so the tool's
rollback-failure message names the surviving canary — reachable only if the
directory existed when the seam fired. Watched: mutation N5 relocates the seam
before `New-Item` and the test fails.

**Two platform facts this needed**, both measured 2026-08-03: denying
delete-child on the PARENT is not enough, because deleting a child also succeeds
via DELETE on the child itself; and in `icacls` the `(D)` right blocks it while
`(DE)` does not. The working spec is `(OI)(CI)(IO)(D)`.

---

## D12 — Task 2: two `-Force` claims carried no evidence

**Task:** 2. **Class:** unwatched assertion. **Found by:** the Fable review.
**FIXED.**

`Get-OrdinalNames` documents `-Force` as what makes a hidden intruder visible,
and the canary contents check relies on it too. No case planted anything hidden,
so dropping `-Force` from either site passed all 26 tests. Two cases added, one
per site; watched by mutations N3 and N4.

---

## D13 — Task 2: the blank-root guard was removable with no test failing

**Task:** 2. **Class:** unwatched assertion. **Found by:** the Fable review.
**FIXED.**

Both blank-root cases asserted only exit 1, and `Resolve-Path` on a blank path
falls into the root-does-not-exist refusal with the same exit code — so deleting
the guard changed nothing observable. The cases now assert the message. Watched
by mutation N2.

---

## D14 — Task 2: Plant overwrites an existing `-StateOut` without refusing

**Task:** 2. **Class:** accepted limit, no change. **Found by:** the Fable
review.

`Set-Content -LiteralPath $StateOut` clobbers whatever is at that path. It is
the one unguarded write the tool performs outside the canary directory. It is
non-recursive, driver-supplied, and Task 4 gives it a fresh scratch path per
run. Recorded as a known limit rather than guarded, because a refusal here would
add a failure mode to the probe driver for no measured risk.

---

## D15 — Task 3: the frozen test code repeats the D4 `_norm` defect, a third time

**Task:** 3. **Class:** plan defect. **Found by:** the session, before running
the step. **FIXED, and recorded rather than silently repaired — D4 is on this
ledger precisely because the silent repair was the fault.**

The plan's Task 3 Step 1 code reads both agent files with `_norm` and then pins
NEWLINE-ANCHORED needles against the result: `"\n  - Skill\n"`,
`"\ndisallowedTools:\n"`, and a `re.findall` over `^  - (\w+)$` in multiline
mode. `_norm` is `" ".join(text.split())`, which destroys every newline, so all
three can only ever be false or empty. Measured before the step ran, on the real
files: `"\n  - Skill\n" in _norm(text)` is **False**, and the `re.findall`
returns **[]**. Every pin in the step was vacuous.

This is the same defect as D4 (Task 1's workflow read) and the same root cause:
the plan reached for the one existing helper without checking that it preserves
what the needle anchors on. Third instance in one branch.

Fixed with a new `_lines()` helper that reads the file and folds CRLF to LF,
leaving newlines intact. Its docstring states its reach at true width and no
wider: the agent files ARE CRLF on disk (39 CRLF, 0 bare LF, measured
2026-08-03) and `read_text` already folds them through universal newlines, so
the explicit fold is belt-and-braces for a caller that switches to
`newline=""`, NOT what makes the pins work today.

**Two guards the frozen code also lacked**, both added: the tool-name lists are
asserted non-empty at their exact expected counts (5 for the reviewer, 6 for the
probe) and the reviewer's denied-tool list is asserted non-empty. Without them a
parse that silently matched nothing would pass a `Skill not in tools` check for
the wrong reason.

**Watched to fail.** The regression guard was mutated by moving `Skill` from
`disallowedTools` into `tools` in `kimi-reviewer-agent.md`; it failed with
`AssertionError: the review lane's agent must never offer Skill`, and the file
was restored byte-identical. The first mutation attempt silently changed
nothing, because it used LF byte patterns against a CRLF file — recorded here
because a mutation that does not mutate reads exactly like a test that cannot
fail, and it was only caught by checking the byte count changed.

---

## REFUTED — the empty-root Compare-Object claim

The Fable review stated that with an empty root, `Compare-Object
-ReferenceObject @()` "throws a binding error on both hosts", so the tool would
exit nonzero with a raw error AFTER a successful delete, misattributing success
as failure.

**Measured 2026-08-03 and refuted on both hosts.** `Compare-Object
-ReferenceObject @() -DifferenceObject @() -CaseSensitive` returns count 0
without throwing under `powershell.exe` AND `pwsh.exe`, and an end-to-end plant
then remove against an empty root exits 0 with the canary correctly gone under
both. No change made.

Recorded because a reviewer's claim is an input to adjudication, never its
verdict, and this one was wider than the behaviour.

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

**Task 2 Step 5 requires each observed failure message to be recorded. They are:**

| mutation | test | observed |
|---|---|---|
| M1 drop `-CaseSensitive` | `test_remove_comparison_is_case_sensitive` | 1 failed |
| M2 overwrite a leftover silently | `test_plant_refuses_a_leftover_canary` | 1 failed |
| M3 remove the profile-root refusal | `test_plant_refuses_the_profile_root` | 1 failed, canary really created in `%USERPROFILE%` and removed |
| M4 remove the reparse scan | `test_remove_refuses_a_reparse_point_inside_the_canary` | 1 failed |
| M5 exact path to prefix test | `test_remove_requires_the_exact_canary_path` | 1 failed |
| M6 skip contents+hash | `test_remove_refuses_an_extra_entry_in_the_canary` AND `test_remove_refuses_a_changed_skill_file` | 1 failed each |

### Task 2, after the whole-branch review

- Suite is now 29 cases: 29 passed under `powershell.exe` AND under `pwsh.exe`.
- Tier 1c (`check_exact_line_oracles.py`) exits 0.
- **Five further mutations**, one per guard the review's findings added, each
  failing its named test, each reverted, post-revert module clean at 29:

| mutation | test | observed |
|---|---|---|
| N1 state file gains a trailing blank line | `test_plant_state_file_shape` | 1 failed |
| N2 delete the blank-root guard | `test_plant_refuses_a_blank_root` | 2 failed |
| N3 drop `-Force` from the root enumeration | `test_the_before_list_sees_hidden_entries` | 1 failed |
| N4 drop `-Force` from the contents check | `test_remove_sees_a_hidden_entry_inside_the_canary` | 1 failed |
| N5 seam fires BEFORE creation | `test_the_fault_seam_really_fires_after_creation` | 1 failed |

- Whole-branch review retained at `fable-review-e94c0b5-d0e116a.md`. Verdict at
  issue: **Ready to merge: With fixes** — no Critical, one Important, five
  Minor, one named gap. Every finding adjudicated: seven accepted and applied,
  one REFUTED with measurement on both hosts, one (D10) held open for the user.
- Commit-trailer check extended to `e94c0b5..d0e116a`: zero `Claude-Session`
  trailers.

---

## Task 3 evidence

- `tools/kimi-probe-agent.md` is the reviewer agent with EXACTLY the frozen
  three changes, proven by diff rather than by claim: the only deletions are
  `name: parallax-readonly-reviewer` and the `- Skill` line under
  `disallowedTools`; the only additions outside the `# PROBE ONLY` block are
  `name: parallax-probe-agent` and the `- Skill` line under `tools`.
- Written UTF-8, not ASCII. The source agent carries U+2014 and the ASCII-only
  Global Constraint covers `tools/*.ps1`, not a Markdown agent file.
- Five-tier gate, whole repo: skill_lint PASS (0 errors, 1 pre-existing token
  budget warning), skill_scanner clean, tier 1c exit 0, trigger evals all clear,
  **968 passed / 13 skipped** in 429s.
- `test_backup_lane.py` alone: **61 passed**.

**Step 5, the leak guard watched to fail.** The guard SWEEPS three roots rather
than naming documents, so one mutation proves only one root. All three were
mutated, each by appending the probe path as bytes, each reverted to a
byte-identical file:

| root mutated | file | observed |
|---|---|---|
| `skills` | `skills/multi-model-verify/references/backup-lane.md` | exit 1, `... must not name the probe agent file` |
| `agents` | `agents/escalation-implementer.md` | exit 1, same assertion naming that file |
| `commands` | `commands/doctor.md` | exit 1, same assertion naming that file |

Post-revert module clean at 61, working tree carrying only this cycle's own
three paths.

### Task 3, after the per-task Fable review

Raw reply retained at `fable-review-d11be0c-c7a9c50.md`. **Ready to merge: Yes**
- no Critical, no Important, three Minors. Every finding adjudicated below, and
the reviewer's own backstop claim was re-verified by the session rather than
taken on trust.

**The backstop claim: VERIFIED, after one false negative of my own.** My first
check reported the "ONLY agent configuration" sentence ABSENT, because I searched
for it with a space where `backup-lane.md` wraps it across a line. It is present,
and `references/kimi-reviewer-agent.md` is named inside a contract pin. The
reviewer is right that the pinned dispatch template, not the new sweep, is the
containment gate.

**Minor 1 - sweep evasion surface. ACCEPTED AS A RECORDED LIMIT, no change.**
The sweep is a NAMING guard over `*.md` in three roots, and it is stated as such
rather than widened. Widening it to every spelling of a path is a losing race,
and the real gate is the pinned template. Carried into the diff debate as the
reviewer asked, so the record says which control does the work.

**Minor 2 - the total floor cannot see a vanished root. ACCEPTED AND FIXED.**
Confirmed by measurement: `rglob("*.md")` on a directory that does not exist
returns an empty list and raises nothing, and the roots hold 9 + 5 + 3, so losing
`agents` leaves 12 and losing `commands` leaves 14 - both over the old floor of
10. This is the check-that-cannot-fail class. Replaced with a per-root floor.
**Watched to fail, by really removing the root, not by faking a count:**

| mutation | observed |
|---|---|
| `commands/` renamed away | exit 1, `commands swept only 0 files; the root moved` |
| `agents/` renamed away | exit 1, `agents swept only 0 files; the root moved` |

Both restored; post-revert the case passes and the tree carries only the test
file's own edit.

**Minor 3 - the docstring's plural. ACCEPTED AND FIXED, and it was worse than
reported.** The reviewer said the probe file's endings were unrecorded.
Measured: the reviewer agent is **39 CRLF, 0 bare LF**; the probe agent is **0
CRLF, 53 bare LF**. So "the agent files ARE CRLF" was not merely unevidenced for
one file, it was FALSE for it. The docstring now states both measurements, notes
that git's eol normalization can flip either on a fresh checkout, and names
`read_text`'s universal-newline folding as the thing that actually makes the pins
match.

---

## D16 - Task 5: the frozen plan's builder snippet calls a function that does not exist

**Task:** 5. **Class:** plan defect. **Found by:** the session, while writing the
step; independently confirmed by the Fable review. **FIXED.**

Revision 7's Task 5 Step 5 writes `Fail (...)` for both refusal paths.
`tools/new-kimi-lane-home.ps1` has NO `Fail` function - the only match in the
whole file is the phrase "Fail closed" inside a comment. Followed verbatim the
build would have refused with a "term not recognized" error carrying the wrong
message, and the tests, which assert the message text, would have failed for a
reason unrelated to what they check.

Substituted `throw`, which is what that section of the script already uses and
is also the only correct choice: the postcondition sits inside the guarded
`try`, so throwing is what runs the catch that deletes the home and the finally
that releases the lock. A bare stderr write and exit would have left an
unreleasable lane. The reasoning is written into the code rather than left here.

---

## D17 - Task 5: the deny-list sentence cited cells that cannot carry it

**Task:** 5. **Class:** claim wider than its evidence. **Found by:** the Fable
review. **FIXED.**

The prose shipped as "the load-bearing control as the lane ships is the `Skill`
deny list - a discovered skill cannot be invoked, measured in cells A and B of
the same record."

Cells A and B BOTH passed `--skills-dir` at an empty target, so discovery was
already suppressed and no discovered skill was ever presented for the deny list
to block. Their null result is fully explained by the flag alone. Verified from
the cell results rather than argued: both record `skillsDirPassed: true`.

What A and B DO measure about the deny list is the TOOL SURFACE - `toolCount` 5
with `Skill` absent from the advertised snapshot, compared against the agent file
by exact list equality on every session-creating call. The text now says that,
and says plainly that the cells measure the composition.

**This is the FOURTH instance on this branch of a claim wider than its evidence,
and the THIRD about these same two cells.** The first two were caught by the
reopened debate and are already retracted in the probe record. That a fourth
survived into shipped contract text, one commit after the correction that named
the fault, is the finding worth carrying forward.

**Watched to fail:** reverting the prose to the overreaching wording fails
`test_backup_lane_client_config_sweep`; restored byte-identical.

---

## D18 - Task 5: the plan promised a pin its own step did not contain

**Task:** 5. **Class:** plan defect. **Found by:** the Fable review. **FIXED.**

Step 4's rationale states that the corrected `SKILL.md` sentence "gets one direct
pin added in Step 1". Step 1's code block contains no such pin, and the
implementer following the plan's literal code added none. The corrected sentence
therefore shipped unpinned, in a file whose PREVIOUS version of that sentence was
also unpinned - which is exactly how a falsified measurement stayed in a shipped
skill until a probe contradicted it.

Fixed with `test_the_confounded_flag_claim_stays_corrected` in
`test_multi_model_verify.py`. It pins the corrected sentence AND asserts the
falsified phrase is absent, so a restoration fails rather than merely not
matching.

**The pin normalizes whitespace, and that is the OPPOSITE reasoning to D4 and
D15.** Those two were defects because a newline-anchored needle was matched
against whitespace-collapsed text. This needle spans a line wrap and anchors on
no newline, so collapsing is what makes it match. The docstring says so, because
the two cases look identical from a distance.

**Watched to fail:** restoring `suppresses nothing observable` to `SKILL.md`
fails the new case; restored byte-identical.

---

## D19 - Task 5: three smaller departures, recorded rather than silent

**Task:** 5. **Class:** recorded deviation. **Found by:** the Fable review
(Minors 1 to 3).

- **The trailing prose said "measured: replacement".** The probe measured
  suppression of ONE root under one condition; "replacement" is the client's help
  text, which the probe record explicitly refuses to launder into a measurement.
  Changed to "suppression of the home root".
- **`SKILL.md`'s replacement is shorter than the frozen Step 4 block.** Same
  meaning, fewer words, for the lint budget the step itself cites. The plan
  claimed a SHORTENING and the first attempt was 21 characters LONGER, which is
  what prompted the tightening; measured after: 5120 tokens to 5117.
- **The builder's exit-code taxonomy did not list the new refusal.** Added - and
  the first attempt filed it under exit 2 with the parameter refusals, which is
  WRONG. Measured live: an uncaught `throw` in this script exits 1. Corrected,
  and the measurement is written into the header so the next reader does not have
  to repeat it.

---

## Task 5 evidence

- Every new assertion watched to FAIL before its implementation existed, and for
  the reason it claims: the four text pins failed on absent text (first failing
  assert named at `test_backup_lane.py:855`); `test_declared_regions_match_the_
  documents` failed with `declared region(s) not found in any document:
  ['home-skill-root-disposition', 'home-skill-root-disposition-limit']`; the
  three postcondition cases failed because the seam and check did not exist.
  `test_a_clean_build_still_succeeds_with_an_empty_skills_dir` PASSED at that
  point, which is correct - it is the positive control, not evidence.
- **Both hosts.** `test_kimi_lane_home.py` is 88 passed under `powershell.exe`
  and 88 passed under `pwsh.exe`.
- Full modules after the fixes: 331 passed, 1 skipped.
- Both contract regions confirmed COLLECTED and covered, by calling
  `contract_coverage.collect_regions` directly rather than inferring it from a
  green suite.

**Step 7's four coverage mutations, each reverted, each caught by the right
test:**

| mutation | caught by |
|---|---|
| M1 weakening sentence appended INSIDE region 2 | `test_every_marked_region_is_locked_by_a_pin` |
| M2 region 2's `contract:end` deleted | `test_declared_regions_match_the_documents` AND the pin test |
| M3 a sentence deleted from inside region 1 | the pin test AND `test_backup_lane_client_config_sweep` |
| M4 the limit id renamed in the DOCUMENT only | `test_declared_regions_match_the_documents` |

**M1 is the case the reopened debate turned on.** It leaves every pinned literal
byte-identical and would pass an ordinary pin. It fails the region check. That is
the argument the primary lane won, executed rather than asserted.

---

## D20 - Task 6: a behavioural gate failure I could NOT attribute, and did not pretend to

**Task:** 6. **Class:** pre-existing flaky case, NOT a regression. **Found by:**
the opt-in behavioural evals. **RESOLVED by measurement.**

`python evals/tools/run_behavioral_evals.py --changed --head` returned **1
failure of 7 cases**: `plan-mode-debate-runs`, on expectation 4, the finish line
naming both participating models.

**Nothing I changed touches that text.** Verified, not assumed: `git diff main
HEAD -- skills/multi-model-verify/SKILL.md` shows FIVE changed lines, all inside
the preflight-3 paragraph, and the finish-line instruction at `SKILL.md:330` is
untouched across the whole branch.

**So I measured instead of arguing.** Nine live runs:

| tree | runs | passes | expectations that failed |
|---|---|---|---|
| pre-change worktree at `74baa71` | 2 | **2** | none |
| HEAD, before the pointer fix | 4 | **0** | #4 x3, #3 x2 |
| HEAD, after the pointer fix | 3 | **1** | #1 x2, #3 x2 |

**What I concluded, and what I refused to conclude.** Zero of four looked like a
regression, and I acted on it: the edit had replaced a stated fact with `See
references/backup-lane.md for the measured discovery controls and their limits`,
an IMPERATIVE pointer inside preflight 3, which every mode-plan round performs -
including primary-lane rounds that need nothing from that 35 KB file. Sending
every run on that detour is a real mechanism, so the text became self-contained
again and cites the reference instead.

**That fix is NOT demonstrated to work.** One pass in three is not better than
zero in four in any way I can defend. It is kept because it is better on its own
terms, and it is recorded here as an unproven change rather than a repair.

**And the attribution does not hold up either.** The failures scatter across
THREE different expectations rather than repeating on one, which is not what a
broken instruction looks like. Two of the last three failures are expectation 1
reporting that the TRANSCRIPT WAS TRUNCATED before the grader could see the
codex invocation - a limit of the harness's own rendering, not of the plugin.
And two control runs is not a baseline; my clean control may simply have been
luck.

**The missing measurement is more CONTROL runs**, not more HEAD runs. Without
them, flaky-case and regression are indistinguishable, and this repo's own
invariant says an unmade measurement is never a clean one - which cuts against
me here as readily as for me. Escalated to the user with three options rather
than resolved by the session, because the next step costs real money and the
merge decision is theirs.

**Recorded against the plan's own claim:** Task 5 Step 4 says the `SKILL.md`
correction is a SHORTENING. After this second revision it is 5126 tokens against
the 5120 baseline - six tokens LONGER. The claim was true of the first version
and is false of the shipped one. Behaviour was the priority over the byte count,
and the plan's sentence is now inaccurate.

### D20 RESOLVED - the case is flaky and this branch is exonerated

The user authorized four more CONTROL runs, which was the missing measurement.
The unchanged tree at `74baa71` failed **all four**, on the SAME expectations
this branch failed on: expectation 1 (the transcript truncated before the grader
could see the codex invocation) and expectation 3 (reference claims in the final
plan not carrying a full first citation).

**Final tally, thirteen live runs:**

| tree | runs | passes | pass rate |
|---|---|---|---|
| unchanged, `74baa71` | 6 | 2 | 33% |
| this branch | 7 | 1 | 14% |

There is no meaningful difference between those, and the failure modes are
identical. `plan-mode-debate-runs` is an UNRELIABLE case under this executor;
it is not a regression, and my first two control runs passing was luck.

**Two things I got wrong, recorded because they are the useful part.**

1. **I read 0-of-4 as a regression on a 2-of-2 baseline.** Two runs is not a
   baseline, and I said so at the time and acted on the number anyway. The
   correct move at 0-of-4 was to widen the CONTROL, not to change the product.
2. **I changed shipped text on a theory that turned out to be false.** The
   pointer-versus-fact edit was made to fix this failure. It did not fix it,
   because there was nothing to fix.

**The edit is KEPT, on a different justification than the one that motivated
it.** Preflight 3 runs on every mode-plan round, including primary-lane rounds
that need nothing from a 35 KB reference, and a one-line fact belongs where it is
used rather than behind an instruction to go and read. That reasoning stands on
its own and does not depend on the eval. Reverting would mean a third rewrite of
one paragraph for no measured benefit. What is NOT claimed is that it repaired
anything.

**Left for a future cycle, not fixed here:** `plan-mode-debate-runs` fails about
two runs in three on an unchanged tree, and expectation 1 fails for a reason that
is not about the plugin at all - the harness's transcript rendering truncates the
dispatch before the grader can read it. A gate that fails two thirds of the time
teaches a reader to ignore it. Raise it as a backlog item rather than leaving it
to be rediscovered.

---

## D21 - Task 5: the frozen test code was not shipped verbatim, and nothing said so

**Task:** 5. **Class:** silent departure from frozen text, caught by review.
**Found by:** the whole-branch review of `e94c0b5..5b312d8`, finding Minor 4.
**RECORDED.**

Task 5 Step 1 freezes five test cases. What shipped in
`test_kimi_lane_home.py` differs in four ways: the cases are renamed, the
custody-order case asserts `proc.stdout == ""` instead of the frozen substring
absence, two cases gained `not target.exists()` and lock-state assertions, and
the positive control gained an emptiness check plus a second removal helper.

Every one of those departures makes the case STRICTER, which is why none of
them was noticed. That is exactly the reason to record it. D5 and D6 on this
same branch established that verbatim admits no silent departures, and a
departure that happens to strengthen is still a judgment call the implementer
was not authorized to make alone. The departures stand; the silence does not.

## D22 - Task 6: the frozen staging command omits a file Task 6 requires

**Task:** 6. **Class:** frozen text internally inconsistent; implementer chose
correctly and did not say so. **Found by:** the mode-diff reviewer lane, round 1,
claim 6. **RECORDED.**

Task 6's Files block lists `Modify: CLAUDE.md` and marks it "NOT conditional at
revision 7". Task 6 Step 5's frozen `git add` names only the backlog document
and `.claude-plugin/plugin.json`. The two disagree, and the implementer resolved
it by staging `CLAUDE.md` as the Files block requires.

That resolution is correct - a Files block entry the plan calls unconditional
outranks a staging line that forgot it - but resolving a contradiction in frozen
text is a judgment call, and the ledger is where judgment calls go. Recorded
rather than left to look like the plan and the branch agreed.

## D23 - Task 6: a heading shipped with a hyphen where the plan froze an em dash

**Task:** 6. **Class:** drift from frozen text. **Found by:** the mode-diff
reviewer lane, round 1, claim 6. **FIXED, not ridden.**

The plan freezes item 17's heading ending `— DONE, 0.20.0` with U+2014. The
heading shipped with an ASCII hyphen. Cause: several edit anchors on this branch
were rewritten to avoid em dashes after `str.replace` anchors failed against
terminal-rendered text, and this one carried the workaround into the product.

Fixed by restoring the frozen character rather than recording the drift, because
the surrounding file's own convention is the em dash, so the hyphen was
inconsistent with the plan AND with the document it landed in. Nothing was
gained by keeping it.

## D24 - the mode-diff gate found four more claims wider than their evidence

**Task:** whole branch. **Class:** the class this cycle exists to remove, still
producing instances at the merge gate. **Found by:** the whole-branch review and
the reviewer lane, round 1. **FIXED.**

Four instances were caught during the branch (D4, D17, D18, D19). The merge gate
found four more, and two of them were in my own repairs for the first two.

1. `SKILL.md` said the confounded 2026-07-31 comparison "measured the deny list,
   not the flag". Both arms ran with `Skill` denied and nothing loaded in
   either, so nothing separated denial from non-discovery; the 2026-07-31 record
   itself calls denial only "the plausible mechanism". **My own proposed repair
   was refuted for the same defect**: "so it could not observe the flag" still
   attributes the failure to observe to the deny list. Shipped wording:
   "`Skill` was denied in both arms, so the comparison did not isolate the flag."

2. The locked region `home-skill-root-disposition-limit` called the flag's
   replacement semantics MEASURED and asserted "it does not suppress its own
   target - it selects it". No cell ever passed the flag against a POPULATED
   target, and the probe record explicitly retracts the replacement reading as
   text evidence. **My proposed repair was refuted too**: it said suppression was
   measured for "the other roots", plural, when only `~/.agents/skills/` was
   measured.

3. The probe record said "Cell C is identical in every respect except that
   `--skills-dir` was passed". Every cell used its own freshly built debate home,
   as the frozen procedure requires, so the flag was the intended differing
   variable and not the only difference.

4. Three copies of one sentence claimed the builder's `New-Item` is the only site
   in the repository that writes into the lane's `skills/` directory:
   `CLAUDE.md`, the builder's own comment, and the backlog close-out. The same
   change that shipped the sentence added two `Set-Content` seam writers fifteen
   lines below it. The review cited two sites; grepping the branch found the
   third, which is recorded as amendment 1 on this cycle's application
   checkpoint.

**The lesson, and it is the same one the 0.19.0 cycle recorded at rounds 41-47.**
Once the feature is sound, the remaining defects are claims wider than their
evidence and checks that cannot fail, and they keep appearing inside the repairs
for earlier ones. Two of my four repairs at this gate carried the defect they
were repairing. Writing the narrowest sentence is harder than recognizing a wide
one, and a second reader is what catches the difference.

## D25 - a test that could not fail for the reason it claimed, next to its own replacement

**Task:** 2. **Class:** check that cannot fail. **Found by:** the mode-diff
reviewer lane, round 1, claim 5. **FIXED by deletion.**

`test_the_fault_seam_fires_after_the_canary_exists` asserted the seam message
and the canary's absence, and claimed in its docstring that "reaching the seam is
what proves creation happened first". It proves nothing of the kind: a tool that
checked the seam BEFORE `New-Item` emits the same message and leaves the same
unchanged root, so both assertions pass either way.

**What makes this instance worth reading twice.** The branch had already worked
this out. `test_the_fault_seam_really_fires_after_creation` sits forty lines
below it, and its docstring says in as many words that the seam is not proof of
ordering and that the directory must be observed instead. The session wrote the
correct replacement, left the broken case in place, and shipped both. A test that
a later test in the same file explicitly declares insufficient is a stronger
signal than any reviewer finding, and nothing on this branch read it.

Deleted, with a comment in its place naming what covers each of its two
assertions, so it cannot be re-added as a gap.

## D26 - the tier-1c checker's stated reach was wider than its code, in two places

**Task:** 3. **Class:** claim wider than evidence, in a gate's own description.
**Found by:** the mode-diff reviewer lane, round 1, claim 5. **FIXED by
narrowing the words.**

D10 and the `_is_line_split` docstring both said the checker matches
`.split(<sep>)` where the separator is a string literal CONTAINING a newline.
The code tests exact membership in three separators, so a composite separator
such as a doubled newline is not matched.

The reviewer offered either direction: implement the recorded predicate, or
correct the record. The words moved, because exact membership is the reach this
gate should have - a doubled newline is a paragraph split, and the same cry-wolf
argument that keeps `.split(",")` out keeps it out. Widening the code to match a
docstring would have made the gate fire on correct code, which is how gates get
suppressed.

Both descriptions now state the three separators explicitly, and say why a
composite one is deliberately out of reach.

## D27 - the backlog item kept its pre-measurement text in the present tense

**Task:** 6. **Class:** a resolved record contradicting itself. **Found by:** the
session, while applying the round-1 fixes. **FIXED.**

Item 17 closes with a Resolved block stating the measurement, and then retains
the original problem statement beneath it with nothing marking it as historical.
Read forward, the item asserts that the flag suppresses the home root and then,
forty lines later and in the present tense, that the flag is "a mitigation with
unmeasurable effect" that "claims nothing".

Fixed with a rule and a labelled boundary rather than by rewriting five
paragraphs: the retained text is marked as the item as written BEFORE the probe,
superseded by the Resolved block wherever the two disagree, with the two
falsified claims named. Keeping the question as it was asked has value; letting
it read as current does not.
