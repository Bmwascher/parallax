# 0.23.0 — the budget, the flaky gate, the generators, and a UTF-8 brief

**Status: FROZEN.** Debate terminal at round 6, then REOPENED during the
build when a measurement falsified a number the freeze rested on, and
terminal again at round 12 (adjudicated dry round). Twelve rounds plus one
void one; every round found something real and none was contested. Changes
require reopening the debate and appending a round to the record.

## Goal

Close four things:

1. **Backlog item 19** — `SKILL.md` has been over its token budget for
   several cycles and nothing forces it.
2. **Backlog item 18** — the `plan-mode-debate-runs` behavioural case fails
   about two runs in three, and one of its expectations fails for a reason
   that is not about the plugin.
3. **Backlog item 9** — reviewers are the discovery mechanism for mechanical
   parser faults.
4. **NEW, found during this debate** — the documented codex dispatch
   corrupts a non-ASCII brief on Windows PowerShell 5.1.

## Architecture

Four independent surfaces, in a deliberate order:

- `skills/multi-model-verify/SKILL.md` and three reference files — text
  relocation only; no behaviour changes.
- `evals/tools/skill_lint.py` — a soft threshold, a hard ceiling, and the
  vendored-provenance obligations that follow from editing a vendored file.
- `evals/tools/run_behavioral_evals.py` — one cap change in
  `compact_stream`, plus a generated-shape suite against `header_block` and
  `effective_route_ok`.
- `tools/codex-context-probe.ps1` — no production change; a generated-shape
  suite driven from Python through the existing `run_functions` helper.

**Ordering is load-bearing.** Tasks 1 and 2 both change `SKILL.md`'s size,
so Task 3 (measure, then set thresholds) must run after both. Task 8 (the
twelve live runs) must run after the version bump and cache update, because
the behavioural executor loads the INSTALLED plugin.

## Tech stack

Python 3 stdlib, pytest, PowerShell (both Windows PowerShell 5.1 and
PowerShell 7). No new dependencies.

## Global constraints

Copy into every task's context.

- **The three invariants.** A claim may never be wider than its evidence.
  An unmade, failed, or unreadable measurement is never a clean one. A test
  is not evidence until it has been watched to FAIL for the reason it
  claims. A FIX is new code and gets no discount from any of them.
- **Contract regions.** Text inside `contract:start`/`contract:end` markers
  must sit WHOLE inside a SINGLE pin, in one of exactly three assertion
  clause forms (see `CLAUDE.md`). Moving a region between files is allowed;
  moving it out from under its pin is not. `DECLARED_REGIONS` in
  `evals/multi-model-verify/test_contract_coverage.py` must stay accurate.
- **Bump the version LAST**, except where Task 8 explicitly requires the
  bump first — see that task's note, which is the one authorized exception
  and its reason.
- **Both PowerShell hosts.** Set `PARALLAX_PS_HOST` to test the other one.
  A green suite on one host proves ONE interpreter.
- **Staging.** Never `git add -A`, never `git add -u`. Stage by explicit
  path. No AI attribution in commit messages.
- **Dispatch detached** from the first attempt; the foreground tool ceiling
  is 600 seconds.
- **The repo is public.** No raw recordings; hand-normalized synthetic
  fixtures only.

---

## Task 1 — Relocate three branch-taken passages out of `SKILL.md`

Three moves, each with an independent ownership reason. No fourth
relocation is authorized: the debate ruled that a relocation chosen to make
arithmetic green recreates the pressure the backlog item forbids.

### 1a. The tracked-versus-untracked explanation and the hook paragraph

**Files:** `skills/multi-model-verify/SKILL.md`,
`skills/multi-model-verify/references/backup-lane.md`,
`evals/multi-model-verify/test_backup_lane.py`

**Move OUT of `SKILL.md`** the text currently at lines 109-125, beginning
`Whether the removal needs a commit branches on tracked-ness` and ending
`never as a finding about the reviewed work.` Place it in
`backup-lane.md` in the section that already owns mirror construction.

**KEEP in `SKILL.md`**, and this list is exhaustive — the debate named each
one as load-bearing:

- the STOP itself;
- "only on the user's choice, never automatically";
- the SHORT-path requirement, including the `kerev<n>` example.
  `backup-lane.md:441-451` states that this rule lives in BOTH files and
  must be changed in both, and records that 0.21.0 introduced the exact
  contradiction a one-sided move would recreate;
- the `tools/new-review-mirror.ps1 -RepoRoot <repo> -MirrorPath <scratch>`
  imperative;
- that the mirror becomes the reviewed tree for every lane in that debate;
- `empty enumeration output is the evidence`.

**Retarget the pins.** `test_backup_lane.py::test_skill_preflight_names_the_remediation`
carries six `in skill` assertions. Four of them cover moved text and must
now read the reference instead:

| literal | after the move |
|---|---|
| `a TRACKED entry's deletion shows as ` D` in `git status --porcelain`` | assert against `backup-lane.md` |
| `` `nothing to commit` alongside an unchanged HEAD is the CORRECT observation there, not an inconsistency to chase `` | assert against `backup-lane.md` |
| `so commit the removal inside the mirror` | assert against `backup-lane.md` |
| `bars mode diff and breaks HEAD-identifies-content` | assert against `backup-lane.md` |
| `review mirror` | stays on `SKILL.md` |
| `empty enumeration output is the evidence` | stays on `SKILL.md` |

The imperative pin exists because a 0.14.2 review found the observations
pinned and the imperative not. Deleting any of the six instead of moving it
recreates that inadequacy and is a task failure.

**Verification:**

```
python -m pytest evals/multi-model-verify/test_backup_lane.py -q
python evals/tools/skill_lint.py skills/multi-model-verify --strict
python -m pytest evals/multi-model-verify/test_contract_coverage.py -q
```

**Expected:** all pass. The lint still WARNS (thresholds are Task 3).

**Fail-first:** before retargeting, run the pytest command with the text
moved and the pins untouched. Watch the four assertions FAIL for
`assert ... in skill`. Record the failure names.

### 1b. The checkpoint-binding explanation

**Files:** `skills/multi-model-verify/SKILL.md`,
`skills/multi-model-verify/references/application-checkpoint.md`

`application-checkpoint.md:73-90` already owns the hash, changed-path,
relocation and rejection contract.

**Move OUT** `SKILL.md:334-339`, the paragraph beginning `When an
application checkpoint governed fix application`.

**KEEP in `SKILL.md`** exactly one imperative sentence: when a checkpoint
governed application, pass it through `-CheckpointFile`. The existing
wiring test at `test_multi_model_verify.py:1652-1671` requires the
parameter's discoverability, not that the binding detail stay inline —
confirm that by running it.

**Verification:**

```
python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q -k checkpoint
```

**Expected:** pass, with `-CheckpointFile` still discoverable in `SKILL.md`.

### 1c. The resume rationale

**Files:** `skills/multi-model-verify/SKILL.md`,
`skills/multi-model-verify/references/model-prompting-notes.md`

`model-prompting-notes.md:149-168` and `:192-199` already own the measured
no-continuity result, the same-session check, the effective-route
requirements and the flags-before-resume rule.

**Move OUT** the historical rationale and detailed probe result at
`SKILL.md:253-266`.

**KEEP in `SKILL.md`** three imperatives:

- repeat the complete verification preamble every round;
- flags MUST precede the `resume` subcommand;
- the resumed session id and the effective route must both match.

**NOT AUTHORIZED:** collapsing the two dispatch code blocks into one.
`test_multi_model_verify.py:150-175` demands two COMPLETE preambles with
`>= 2` counts on three separate literals, because rounds run in separate
shells. The debate withdrew this candidate and it is not to be revisited in
this cycle.

**Verification:**

```
python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q
```

**Expected:** pass, including the two-preamble count assertions.

---

## Task 2 — Make the documented dispatch carry a non-ASCII brief intact

**Files:** `skills/multi-model-verify/SKILL.md`,
`evals/multi-model-verify/test_multi_model_verify.py`

### The defect

Measured 2026-08-11 on Windows PowerShell 5.1, during round 1 of this
debate. A 13,363-byte UTF-8 no-BOM brief holding 15 em dashes was
dispatched with the documented form. Every em dash reached the reviewer as
THREE question marks. `tools/read-codex-round-evidence.ps1 -Fresh` refused
the round; the reply was discarded unread and the round's quota was spent
for nothing.

Three question marks per character, not one, is the proof that two faults
fired in series:

1. `Get-Content -Raw` decodes a UTF-8 no-BOM file using the ANSI code page,
   splitting one 3-byte character into three;
2. `$OutputEncoding` defaults to ASCII on 5.1, flattening each of those
   three to `?` at the native-process boundary.

The reviewer independently reproduced both stages, observing the three
characters and the bytes `3F-3F-3F`, then `E2-80-94` after the fix.

### The change

Both dispatch blocks — round 1 at `SKILL.md:191-197` and the resume at
`SKILL.md:245-251` — gain two lines before the pipe:

```powershell
$OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$brief = [System.IO.File]::ReadAllText("<brief-file>", (New-Object System.Text.UTF8Encoding($false, $true)))
```

and the dispatch line becomes `$brief | codex exec ...`, keeping stdin and
keeping every existing flag in place.

**Acceptance criteria, frozen by the debate:**

- strict UTF-8-no-BOM decoding on BOTH the fresh and the resume brief;
- explicit UTF-8 `$OutputEncoding` at the native stdin boundary;
- the setting scoped or restored, never leaked into the caller's shell;
- both documented dispatch forms pinned;
- a Windows PowerShell 5.1 test watched to produce `???` BEFORE the fix and
  exact UTF-8 after;
- **no claim about the backup lane.** It passes its brief as a `-p`
  argument, not through a pipe, so this mechanism does not apply; whether
  that path has its own non-ASCII hazard is UNMEASURED and this release
  claims nothing about it.

### The pin that must be REPLACED, not supplemented

`test_multi_model_verify.py:460-487` pins the resume dispatch with a regex
over the literal `Get-Content -Raw <brief-file> | codex exec ... resume
<SESSION_ID> -` form. That pin exists because 0.21.0 live-proved the
positional form defective. Update the regex to the new `$brief | codex exec
... resume <SESSION_ID> -` form and KEEP the negative assertion forbidding
the positional form. Adding a second pin beside the old one would leave the
defective form pinned as correct.

### Fail-first test

New test, Windows-only, skipped elsewhere: write a UTF-8 no-BOM file
containing an em dash, run a 5.1 child that reads it the OLD way and pipes
to a stub that hexdumps stdin, and assert the bytes are `3F-3F-3F`. Then
run the same child the NEW way and assert `E2-80-94`. Watch the second
assertion fail before the fix lands.

**Verification:**

```
python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q
$env:PARALLAX_PS_HOST = "pwsh"; python -m pytest evals/multi-model-verify -q
```

**Expected:** pass on both hosts. The `???` case is a positive assertion
about the OLD form and must keep passing; it documents the defect.

---

## Task 3 — Measure, then set the thresholds, then honour the vendoring

Runs AFTER Tasks 1 and 2, because both change the body size.

**Files:** `evals/tools/skill_lint.py`, `evals/tools/LICENSE-THIRD-PARTY.md`,
`evals/multi-model-verify/test_skill_lint_budget.py`,
`evals/multi-model-verify/fixtures/skill_lint_pre_change.py`

**CORRECTED at diff round 3.** The freeze named
`test_multi_model_verify.py` as this task's test surface. The budget proof
was written in its own module instead, which is the better home and was
never adjudicated as a change; the fixture is the frozen pre-change linter
added at diff round 2. Both are recorded here rather than left as a
surface that does not match the tree, because the surface is what a later
debate adjudicates drift against.

### Step 1 — Measure

```
python evals/tools/skill_lint.py skills/multi-model-verify --strict
```

Record the exact token number.

**Arithmetic as frozen, and it was wrong:** 5404, minus about 275 for Task
1a, minus whatever 1b and 1c yield, plus **about 100** for Task 2's guard.

**CORRECTED AT ROUND 7 BY MEASUREMENT.** Task 2's guard cost about **420**,
not 100: it is three lines, and `test_multi_model_verify.py:150-175` forbids
collapsing the two dispatch blocks, so it lands twice — plus its contract
region. Measured: 5404 → 5069 after the three relocations → 5486 with the
guard and its region → 5200 after the region moved to
`model-prompting-notes.md`, which the file itself calls the single source
for the reviewer transport → **5227** with a one-line pointer back.

### Step 2 — Set the thresholds

**CORRECTED AT ROUND 7.** The frozen shape below assumed the body would
land near 5000, so it put the hard ceiling at 5250. At the measured 5227
that leaves 23 tokens of headroom and no honest place for a soft target,
which is the shaving pressure this item exists to prevent. The user was
given the choice and reopened the debate rather than let the session pick.

Three MUTUALLY EXCLUSIVE outcomes:

```
tokens <= 5250            clean
5250 < tokens <= 5500     warning
tokens > 5500             error   (error, never warning-and-error)
```

The soft target is **5250**, rebased from the measured 5227 baseline; the
ceiling is **5500**, preserving the 250-token warning band the debate
agreed on. The constant records the measurement, the encoding guard as the
reason the baseline moved, and an explicit statement that these do NOT
rebase automatically — a future release over the ceiling must relocate
text or change the numbers deliberately.

The hard-error message must name the two legitimate remedies — relocate
text to a reference, or change the ceiling deliberately — and must not
invite deleting load-bearing text.

**Boundary pins, four of them:** `5250`, `5251`, `5500`, `5501`.

### Step 3 — Honour the vendoring

`skill_lint.py:3-6` says the file is "unmodified except this provenance
header" and instructs a re-diff against upstream before local editing.
`skill_lint.py:12-26` documents the token budget as a warning and exit 0 as
warnings-allowed. Step 2 falsifies all three statements.

Required, and item 19 is not complete without them:

- re-diff the vendored source against upstream as its own header directs;
  **NOT DONE ON THE FIRST BUILD. Found at round 1 of the DIFF debate.**
  The first attempt diffed only against this repo's own imported copy and
  said so in the header. The reviewer ruled that honest disclosure of a
  skipped step does not discharge a frozen task, which is correct: the
  question the step answers is whether UPSTREAM moved, and a local diff
  cannot answer it. Performed 2026-08-11 against live upstream; result
  recorded in the file header and pinned by
  `test_the_re_diff_is_recorded_with_its_scope`.
- update the provenance note to identify the local budget-enforcement
  delta specifically;
- update the documented checks list and the exit-code description;
- a fail-first test proving the PRE-CHANGE implementation does NOT fail
  above the ceiling (round-7 correction: **above 5500**, not 5250);
- the four boundary tests from Step 2;
- keep explicit that `BODY_TOKEN_BUDGET` is a GLOBAL linter policy, not a
  per-skill setting, even though only one tracked `SKILL.md` exists today.

**Verification:**

```
python evals/tools/skill_lint.py skills/multi-model-verify --strict
python -m pytest evals/multi-model-verify -q
```

**Expected:** lint exits 0. If the body is over `soft`, exactly one warning
and no error; if under, no warning.

---

## Task 4 — Make the dispatch observable to the behavioural grader

**Files:** `evals/tools/run_behavioral_evals.py`,
`evals/multi-model-verify/test_multi_model_verify.py`

### The change

`run_behavioral_evals.py:407` currently reads:

```python
cap = 2400 if block.get("name") in ("Edit", "Write") else 600
```

Extend the wide cap to the two shell tools:

```python
cap = 2400 if block.get("name") in ("Edit", "Write", "Bash", "PowerShell") else 600
```

`Bash` and `PowerShell` are exactly the shell tools the executor exposes
(`AVAILABLE_TOOLS` at `:99`), both allowlisted only for `codex:*`, so this
names the complete set rather than a sample.

Update the comment above it to record the new reason: a measured realistic
dispatch places `codex exec` at character 790, `--sandbox read-only` at
801 and `-m gpt-5.6-sol` at 867 of a 1327-character JSON-encoded input,
and expectation 1 grades on exactly those three. The 1327 figure is ONE
measured realistic dispatch, not an established maximum.

**Rejected alternative, recorded:** rendering bounded windows around the
three tokens. It would let the harness decide in advance which part of an
input deserves to be visible. The debate accepted that objection.

### Five tests, all required

1. the supplied 1327-character event retains all three needles;
2. an input over 2400 truncates at exactly the declared cap;
3. the record stays ONE physical line;
4. spoofed prose shaped like a tool marker is still neutralized;
5. several 2400-character shell records exhaust the evidence budget with
   the explicit exhaustion marker and without bisecting a record.

**Fail-first:** test 1 is written and watched to FAIL under the head-only
600 rendering before the cap changes.

### The claim that must be narrowed while here

The comment at `run_behavioral_evals.py:516-522` says keeping lines whole
keeps call/result PAIRS whole. It does not: the middle-evidence loop can
exhaust its budget having kept one half of a pair. Correct it to
"indivisible records, plus explicit loss when the budget runs out", which
is the property the code actually has.

**Verification:**

```
python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q
```

---

## Task 5 — Generated shape coverage for the route parser (item 9, part A)

**Files:** new `evals/multi-model-verify/test_route_parser_shapes.py`

### Step 1 — FREEZE the grammar before generating any case

The debate's central finding was that the first draft would have generated
cases whose correct answer had not been decided. This grammar is the
oracle. It is frozen here and the generator implements it; a case whose
expected result is not derivable from these seven rules is a plan defect.

1. ANSI escapes are removed from the WHOLE output BEFORE anything is
   located. An escape anywhere is presentation only and never makes a line
   malformed.
2. A DELIMITER RULE is a line whose stripped form is at least 8 characters
   and consists only of `-`.
3. The HEADER BLOCK is the lines strictly between the FIRST and the SECOND
   delimiter rule. Fewer than two rules means there is no block.
4. **Three or more rules is VALID input.** The first two select the block;
   everything from the second rule onward is ignored, however
   header-shaped. This is deliberate, not a tolerance.
5. For key K: a LABEL is a line matching `^K:`; a FIELD LINE is a line
   matching `^K: (.+)$`. K is ACCEPTED with value V iff the block holds
   EXACTLY ONE label and EXACTLY ONE field line for K, V being that line's
   capture stripped of surrounding whitespace.
6. **Surrounding whitespace in a value is normalization, not
   malformation.** `model:  gpt-5.6-sol ` accepts `gpt-5.6-sol`.
7. A bare `K:` or an empty `K: ` yields a label and no field line, so K is
   NOT accepted. The route is CLEAN iff all four of `model`, `provider`,
   `reasoning effort`, `sandbox` are accepted AND equal their canonical
   values.

**The invariant the suite asserts** — never a specific message: any input
that does not satisfy rule 7 for all four keys must NOT produce a clean
route. An unmade, failed or unreadable measurement is never a clean one.

### Step 2 — Enumerate

Two bounded sweeps, cross-multiplied by line ending (LF, CRLF):

**Sweep A, block location.** rule count in {0, 1, 2, 3, 4} x rule form in
{exactly 8 dashes, 3 dashes, 20 dashes, 8 dashes with a trailing space,
8 dashes with an ANSI escape inside}, with a well-formed field set inside
whichever block results, plus a header-shaped decoy line after the closing
rule in half the cases.

**Sweep B, per field.** For each of the four keys, with the other three
well-formed: presence in {absent, once, twice} x form in {`K: v`, `K:`,
`K: `, `K:v`, ` K: v`} x escape placement in {none, in label, in value}.

**NOT IMPLEMENTED AS FROZEN ON THE FIRST BUILD. Found at round 1 of the
DIFF debate; rebuilt.** The first implementation folded the escape
placements into the form table, never crossed presence with form at all,
and produced 88 cases where the product above is 4 x 3 x 5 x 3 x 2 = 360.
"All ten mutants killed" was therefore true of a matrix nobody had
specified — the same defect round 9 found in the PowerShell sweep, in the
module written to avoid it.

THREE readings the freeze does not settle. All three were decided at the
rebuild; only the first two were RECORDED then, and the third lived in
`render_field` alone until diff round 6 found it. (This sentence said
"two" for two rounds after the third was added to the list below it, and
also claimed all three had been recorded here from the start. Round 7
caught the count; the rest is corrected with it.)

- **`twice` crossed with form and escape** means TWO occurrences of the
  SAME form and placement. A mixed pair is a different combination that
  the product already covers cell by cell, and it is kept as a declared
  extra because it is the shape that separates counting labels from
  counting field lines.
- **`absent` crossed with form and escape** is degenerate: with the key
  omitted there is nothing for either axis to act on, so 30 of the 360
  cells per key render identical text. They are generated anyway. A
  quietly pruned product is a matrix nobody specified, which is the
  defect being corrected.
- **`escape in value` crossed with the two valueless forms** — `K:` and
  `K: ` — is the THIRD degenerate crossing. **ADDED at diff round 6**,
  which found it recorded in the code and not here, next to two readings
  that were. The escape is written WHERE THE VALUE WOULD HAVE BEEN, so
  `K:` renders as `K:` + ESC + RESET and `K: ` as `K: ` + ESC + RESET.
  After rule 1 strips the escapes both are byte-identical to their `none`
  siblings, so no expected verdict moves.

  **Why this one is not pruned to duplicates while `absent` is.** The two
  cases are different in kind, not in taste. With the key ABSENT there is
  no line at all, so there is no position an escape could occupy and no
  rendering to vary; the duplication is forced. With a valueless FORM the
  line exists and the value position exists, it is merely empty, so an
  escape can genuinely be placed there. Rendering it is the reading that
  keeps the axis meaning the same thing in every cell it appears in.
  Either reading is defensible; what was not defensible was deciding one
  of them in `render_field` and the other two here.

Cases beyond the 360 are permitted and are counted separately, so that
"how many cases" never has to mean "how many of them were specified".

Expected results come from the seven rules, computed by the generator, not
hand-written per case.

### Step 3 — Mutation-test it, which is the actual evidence

Ten source-level mutants, one per recorded defence. Remove or weaken ONE
clause, run the generated suite, and record which generated case killed it.
A mutant no case kills is a coverage hole and is reported as one.

| # | clause | mutation |
|---|---|---|
| 1 | ANSI stripped before rule location | remove the `sub` |
| 2 | rule length floor `>= 8` | drop the floor |
| 3 | rule is all `-` | loosen to `startswith("-")` |
| 4 | `len(rules) < 2` returns None | change to `< 1` |
| 5 | block is `rules[0]+1 : rules[1]` | change to the LAST two rules |
| 6 | label count `== 1` | drop the label count |
| 7 | value count `== 1` | drop the value count |
| 8 | `one_each` gates the value | take the first match instead |
| 9 | all four keys compared | drop `sandbox` |
| 10 | patterns anchored with `(?m)^` | drop the anchor |

**Verification:**

```
python -m pytest evals/multi-model-verify/test_route_parser_shapes.py -q
```

**Expected:** all generated cases pass against the real parser, and the
mutation run kills all ten. Retain the failing output naming the killing
case for each.

**The claim this task may make, and no wider:** generated shape coverage
now exists for ONE parser in ONE module. This is the cheapest first target,
not a proven highest-value one, and it does not by itself close item 9.

---

## Task 6 — Generated shape coverage for `Get-SkillReport` (item 9, part B)

**Files:** new `evals/multi-model-verify/test_skill_report_shapes.py`

Item 9's evidence is entirely PowerShell, so item 9 does not close without
this. `tools/codex-context-probe.ps1` gets NO production change; this task
adds tests only.

### Target and transport

`Get-SkillReport` and its `Hide-KnownContainer` dependency. Cases are
generated in Python and sent through the existing `run_functions` helper
(`test_codex_context_probe.py:73-96`), which dot-sources the production
function block from a file and runs a snippet — **one host process for the
whole matrix**, so the cost is one process per configured host. CI already
runs that module under both Windows PowerShell and pwsh.

### Frozen invariants

- `BlockPresent` and `Entries` are reported SEPARATELY: an absent container
  and a present-but-unparseable container are different facts and must not
  collapse.
- **CORRECTED at round 10.** TWO shapes are non-ambiguous: NO delimiters at
  all, representing an absent container, or EXACTLY ONE correctly ordered
  pair. Every other arrangement — opener-only, closer-only, two or more of
  either, closer before opener — is AMBIGUOUS. The frozen wording said the
  ordered pair was the ONLY non-ambiguous shape and then listed "none" as
  ambiguous, which contradicted itself; production and the generated
  oracle always behaved as stated here, so this is a specification
  correction and not a code change.
- The `### Available skills` heading is honoured only INSIDE the
  container's body. A heading anywhere else supplies no entries.
- Known/quoted containers are masked before scanning; a container that
  appears only inside a masked region is not a container.
- **ADDED at CYCLE EXCHANGE 13, which is DIFF ROUND 1.** `BlockPresent` is TRUE iff at
  least one OPENER survives masking. A closer with no opener reports the
  container ABSENT: an opener is what claims a container exists, a stray
  closer claims nothing. Presence is independent of ambiguity, so a
  three-opener arrangement is present AND ambiguous.
- **ADDED at CYCLE EXCHANGE 13, which is DIFF ROUND 1.** Entries are read ONLY from the
  body of an unambiguous single ordered pair. Every ambiguous arrangement
  reports ZERO entries even with a heading inside it, because ambiguity
  means there is no single body to read from. Reporting entries from a
  guessed body is the failure this rule forbids.
- **ADDED at CYCLE EXCHANGE 13, which is DIFF ROUND 1.** The entry grammar, as a truth
  table rather than a regex: an entry is ONE line,
  `- <name>: <description> (file: <path>)`. The file marker is the LAST
  such marker on the line, so a description that itself mentions
  `(file: x)` still parses and a path containing parentheses stays whole.
  Two entries joined onto one line is MALFORMED and yields no entry. A
  line with no file marker is MALFORMED and yields no entry. Malformed is
  reported, never silently dropped.

  **Why the three above are additions and not changes.** The generator was
  already computing all three fields, and no expected value moved when
  they were written down. The defect was that those expected values
  rested on agreement with the production code rather than on a decided
  rule, which makes a generated suite something other than independent
  evidence. The reviewer found the first instance; the cross-vendor lane
  found the other two in the same pass.

### Enumerate

openers in {0,1,2,3} x closers in {0,1,2,3} x closer-before-opener in
{yes,no} x heading placement in {inside, outside, both, absent} x quoted
container in {none, the only one, one of two} x line ending in {LF, CRLF}.

### Mutation-test

One mutant per defence named in the function's own comments, at minimum:
masked-versus-raw source selection, the span endpoints, the ambiguity
arithmetic, and the heading's search scope. Record the killing case for
each.

**Verification:**

```
python -m pytest evals/multi-model-verify/test_skill_report_shapes.py -q
$env:PARALLAX_PS_HOST = "pwsh"; python -m pytest evals/multi-model-verify/test_skill_report_shapes.py -q
```

**Expected:** green on both hosts; every mutant killed.

**If this task cannot land:** item 9 stays OPEN and only a newly named
subitem closes — "The behavioural grader's effective-route parser lacks
generated shape coverage". Item 9 is NOT to be marked closed on an
unexecuted PowerShell matrix.

---

## Task 7 — Records

**Files:** `docs/superpowers/plans/2026-07-27-0150-backlog.md`,
`docs/superpowers/plans/rounds/2026-08-11-budget-flake-generator/` (already
written), `CLAUDE.md`

- Items 18, 19 and 9 marked with their real outcome, not their intended
  one. Item 9 closes only if Task 6 landed.
- A new backlog entry for the UTF-8 brief transport defect, marked closed
  by this release, carrying the measurement and the explicit note that the
  backup lane's argument path is UNMEASURED.
- `CLAUDE.md` gains one line under the long-running-commands section: the
  documented dispatch must read the brief as strict UTF-8 and set
  `$OutputEncoding`, because Windows PowerShell 5.1 silently corrupts a
  non-ASCII brief and the round-evidence tool is what catches it.

---

## Task 8 — The twelve live runs

**Runs LAST**, after every other task, after the version bump, and after
the cache update. This is the one authorized exception to "bump last": the
behavioural executor loads the INSTALLED plugin
(`run_behavioral_evals.py:21-24`), and `--head` is explicitly NOT
acceptable for a pre-merge sample because its shadowing against an
installed copy is unverified (`:772-775`).

**Before run 1:** finish the branch, bump `.claude-plugin/plugin.json`, run
`claude plugin update parallax@parallax`, restart, then RECORD the branch
SHA and the installed version. All twelve runs use that one installation.

```
python evals/tools/run_behavioral_evals.py --case plan-mode-debate-runs
```

### The decision rule — predeclared, and not reinterpretable afterwards

A RUN passes only when all four expectations are met. Per-expectation
verdicts are retained for every run.

**Aggregate bands** — these describe post-fix performance and make NO
causal claim, because a fixed-tree-only sample cannot prove which change
caused an improvement:

- **10 to 12 pass** — the post-fix case met its repair gate.
- **6 to 9 pass** — the post-fix case remains unreliable.
- **0 to 5 pass** — the post-fix case failed its repair gate.

**Item 18 closes only at 10-12 AND both of:**

- expectation 1 failed ZERO times; and
- every remaining failed expectation is grounded in real agent
  noncompliance, not in missing, truncated, elided or unbound harness
  evidence. A harness-caused miss in ANY expectation leaves item 18 open.

**Expectation 1 failing even once means the rendering change did not
deliver observability.** That is a failure of Task 4 regardless of where
the aggregate lands.

**Run accounting:**

- executor timeout or nonzero exit — a FAILED run, counted. The runner
  deliberately treats it that way (`:482-486`) so a partial transcript from
  a crash cannot be graded into success.
- grader auth, grader process, or grader route failure — NO expectation was
  measured; record and replace.
- missing or malformed grader verdict array — same; record and replace.
- **Replacement cap: 6.** Beyond six replacements the sample STOPS as
  blocked and the block is reported, rather than spending more live calls
  until the numbers look answerable.

**Not a control.** The historical 2-of-6 and 1-of-7 are two separate arms
whose failure modes the record found identical. They are described that
way and never as a baseline.

**Expectation 3 is not relaxed in this cycle.** It grades an instruction
`SKILL.md` really gives, and the measurement above is what decides whether
anything more is needed.

---

## Debate record

**Participants:** Claude Opus 5 (session) / gpt-5.6-sol (codex exec,
session `019fef3e-9b6a-7a21-a49f-686e0d96ac53`)
**Rounds used:** 12, plus one VOID round; 13 units consumed of 13
authorized (8 declared late at round 5, +2 by the user after round 7,
+3 after round 9)
**Outcome:** converged, terminal on an ADJUDICATED DRY ROUND at round 12
**Verification status:** FULL
**Degradation:** none
**Authorized by:** user at round 4 (twelve live behavioural runs)
**Raw rounds:** `docs/superpowers/plans/rounds/2026-08-11-budget-flake-generator/`

### Resolved points

| # | Claim | Raised by | Outcome | Evidence |
|---|---|---|---|---|
| 1 | "The budget grew every cycle and never shrunk" | session | REFUTED | 5120, 5120, 5117, 5129, 5404, 5404 recomputed at release snapshots |
| 2 | The mirror paragraph is ~1780 bytes | session | REFUTED | 2192 characters, 548 est tokens |
| 3 | The short-path rule may move to the reference | session | REFUTED | `backup-lane.md:441-451` requires it in both files |
| 4 | Six ordinary pins cover the moved paragraph | session | accepted into Task 1a | `test_backup_lane.py:1000-1024` |
| 5 | Expectation 1 "cannot pass in a realistic run" | session | NARROWED | it can become unobservable and fail independently of behaviour |
| 6 | The dispatch offsets 790/801/867 | session | verified at round 2 | reproduced by the reviewer from the supplied inputs |
| 7 | Keeping lines whole keeps call/result PAIRS whole | session | REFUTED | the middle loop can keep one half; the property is explicit loss |
| 8 | The route parser is "currently untested" | session | REFUTED | six focused tests at `test_multi_model_verify.py:1216-1325` |
| 9 | The route parser is the "highest-value" target | session | NARROWED | cheapest first target; PowerShell remains the documented hotspot |
| 10 | The generator oracle as first drafted | session | REFUTED | three enumerated shapes had no decided answer; grammar frozen in Task 5 |
| 11 | Deduplicate the two dispatch preambles | session | REFUTED | `test_multi_model_verify.py:150-175` demands two complete copies |
| 12 | Move the checkpoint-binding explanation | session | accepted into Task 1b | `application-checkpoint.md:73-90` owns it |
| 13 | Move the resume rationale | session | accepted into Task 1c | `model-prompting-notes.md:149-168, 192-199` own it |
| 14 | Ship a permanent warning with a dated exception | session | REFUTED | it documents the contradiction without removing it |
| 15 | The vendored-provenance obligation | reviewer | accepted into Task 3 | `skill_lint.py:3-6, 12-26` |
| 16 | 14 corrupted em dashes | session | REFUTED | 15; 45 non-ASCII bytes, all em dashes |
| 17 | Twelve runs on the fixed tree, not split | session | accepted, with corrections | `run_behavioral_evals.py:21-24, 772-775` |
| 18 | Blanket discard of every executor nonzero | session | REFUTED | the runner classifies it as a case failure by design |
| 19 | "Worst realistic dispatch is 1327 characters" | session | NARROWED | one measured dispatch; no corpus establishes a maximum |
| 20 | Fix-verify ledger of 5 spent | session | REFUTED | a round consumes its unit on dispatch; 6 spent |
| 21 | The UTF-8 brief transport defect | session | accepted as work item 4 | reproduced independently by the reviewer |

### Rounds 7 to 12 — the plan was REOPENED after the build began

Round 6 was terminal. Building then produced a measurement that falsified a
number the freeze rested on, and the user chose to reopen rather than let
the session decide. Every one of the six further rounds found something
real, and none was contested.

| # | Finding | Raised by | Outcome |
|---|---|---|---|
| 22 | Task 2's guard cost ~420 tokens, not the ~100 I estimated; at 5227 a 5250 ceiling leaves 23 tokens | session | reopened the plan; user chose to reopen rather than accept a shave |
| 23 | Threshold shape: warn at 5250, error above 5500, four boundary pins | reviewer | adopted; Task 3 rewritten |
| 24 | Two new byte oracles could pass on EMPTY output | reviewer | accepted; both now compare the whole payload, both mutants killed |
| 25 | Asserting that three mutants survive locks in today's topology and proves nothing | reviewer | accepted; replaced with a declared fail-open FAULT MODEL, all three now die |
| 26 | Task 6 hand-picked 19 arrangements where the plan froze a Cartesian product | reviewer | accepted; 768 arrangement cases built, reaching kills the hand-picked set could not |
| 27 | Case count wrong in two places (768+12=780 generated, 791 tests) | reviewer | corrected in the plan and the backlog |
| 28 | The frozen ambiguity invariant contradicted itself about "none" | reviewer | corrected in both places; production and the oracle were always right, the SENTENCE was wrong |
| 29 | The frozen plan still carried the superseded 5250 ceiling after the code and backlog were amended | reviewer | corrected in place with round-7 markers |

**The class worth carrying forward.** Findings 27, 28 and 29 are all the
same shape: the CODE was right and the RECORD was wrong. A frozen plan is
what mode diff adjudicates drift against, so a stale plan does not merely
mislead a reader — it makes correct work read as drift, or gets taken as
authority and the correct work reverted.

### Escalated points (user-decided)

| # | Question | Session position | Reviewer position | Owner's call |
|---|---|---|---|---|
| 1 | How many live behavioural runs to authorize | 12, or fewer to save quota | 12, predeclared rule | **12, rule predeclared** |

### Process deviations

- The total fix-verify budget was declared at round 5, not before round 1
  as `debate-protocol.md:79-87` requires. Recorded rather than backdated.
- Round 1 was VOID on a brief-attribution failure and its quota is spent
  for nothing. It counts as a unit.
