# Item 87: Astra reviewer swap with Sol as the explicit alternate — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the primary cross-vendor reviewer lane from GPT-5.6 Sol to
GPT-6 Astra at effort `high`, keep Sol reachable as an alternate that runs
only when the user names it, and rename the lane everywhere its label is a
live name rather than a historical citation.

**Architecture:** Three independent edits. Task 1 files backlog item 87
with the probe that justifies the swap. Task 2 changes the pins first, then
rewrites the reviewer-lane section of the one file every runtime parser
reads, so the swap is complete for the executables the moment that section
changes. Task 3 renames the lane's label in the documents and the one test
fixture that name it. Nothing here changes the transport, the flags, the
per-round evidence, the dispatch tool, or any lane's identity evidence.

**Tech Stack:** Markdown skill and reference bodies, Python 3.12 with
pytest, the backlog lint.

**Spec:** The design approved in chat on 2026-09-04 and restated in the
backlog item Task 1 files. The probe evidence is in that item. There is no
separate spec file: the change is bounded, and the item carries the case.

## Global Constraints

- **`SKILL.md` MUST STAY UNDER ITS HARD CEILING OF 6500 TOKENS.** Measured
  2026-09-04 before this branch: 414 lines and roughly 6456 tokens, so the
  headroom is about 44 tokens. Task 3 changes ONE word in `SKILL.md`, from
  `Sol` to `Astra`, and nothing else. Re-run
  `python evals/tools/skill_lint.py skills/multi-model-verify --strict`
  after the edit and record the reported count. If it reports an ERROR or
  the count reaches 6500, STOP and report rather than trimming unrelated
  text.
- **The canonical reviewer model id may appear as a literal ONLY in
  `skills/multi-model-verify/references/model-prompting-notes.md`.**
  `test_reviewer_id_has_single_source` sweeps every other skill, command,
  tool, eval, README, CLAUDE.md and hook file for the id parsed from the
  notes and for the flag shape `-m <vendor>-<digit>`. So no test in this
  plan writes `gpt-6-astra`; tests compare with `startswith("gpt-6-")`.
  The alternate id `gpt-5.6-sol` is NOT the canonical id once Task 2's
  notes edit lands, so a test may name it, but ONLY from Task 2's step 3
  onward: in Task 2's red phase that sweep reports the test file, and the
  plan names that failure as expected.
- **Tests change first.** The reviewer lane's declarations are a
  live-verified contract; every pin edit precedes the text edit it locks.
- **Pin integrity.** A pin matching RAW file text needs its phrase
  unbroken on ONE PHYSICAL LINE; a pin built on the whitespace-normalized
  read does not. `test_seat_reshuffle.py:131-134` pins `panels.md` on the
  RAW read, and lines 12 and 14 of `panels.md` are single physical lines
  for that reason: keep them single lines. The `background-task-naming`
  region pin at `test_multi_model_verify.py:1322-1340` is a NORMALIZED
  read, so the region may wrap.
- **Contract regions.** `background-task-naming` keeps its id, so
  `DECLARED_REGIONS` in `test_contract_coverage.py` does not change. Its
  text changes, so its pin changes FIRST, and the pin must hold the whole
  region in one literal.
- **Historical citations stay.** A parenthetical such as
  `(Sol review 2026-07-12)`, a probe record naming `gpt-5.6-sol` with a
  date, a round table with a `Sol` column, and every file under
  `docs/superpowers/plans/rounds/` record which model said or did a thing
  and are NOT renamed. The rename covers live labels only: the seat
  table, panel compositions, the task-name convention, the lane transport
  list, the fallback class prose, and the behavioural fixture header.
- **Claims no wider than evidence.** The OpenAI GPT-6 guidance page was
  fetched 2026-09-04 and no longer carries the six-element sentence, the
  migration-plan review example, or the lean-prompt advice that the 5.6
  bullets cite. The rewrite says so and keeps those practices as THIS
  repo's convention. Whether Astra asks for clarification under
  `codex exec`, and whether the model cache's persistent-mode block
  applies there, are UNMEASURED and are written as the guide's claim and
  as an observation of the cache, never as a measurement of the lane.
- **Never `git add -A` and never `git add -u`.** Stage by explicit path.
- Files under `skills/multi-model-verify/references/` use forward slashes
  in every path.
- **Commit messages must not contain a token that reads as a git flag**,
  such as `-Prepare`, `-m`, or `-c`. The guard reads them as flags. Write
  the words out.
- **Do not bump `.claude-plugin/plugin.json`.** The bump happens AFTER the
  diff debate, never as a build task.
- Gate, all six: `python evals/tools/skill_lint.py skills/multi-model-verify --strict`,
  `python evals/tools/skill_scanner.py skills`,
  `python evals/tools/check_exact_line_oracles.py`,
  `python evals/tools/run_trigger_evals.py`, `python -m pytest evals -q`,
  `python evals/tools/backlog_lint.py`.

## Measured facts the plan is built on

1. **Astra is reachable on this account.** 2026-09-04, codex-cli 0.153.4,
   from a scratch git fixture, with the dispatch's isolation flags
   (`--disable plugins --disable apps --disable memories -c mcp_servers.node_repl.enabled=false`),
   `--sandbox read-only`, and `--output-last-message`: the prompt
   `Reply with exactly: TRANSPORT-OK` returned exit 0 and the exact reply
   at effort `low` and again at effort `high`. The resolved header read
   `model: gpt-6-astra`, `provider: openai`, `sandbox: read-only`, and the
   pinned effort each time. The first attempt failed with
   `Not inside a trusted directory` because it ran from `$env:TEMP`, which
   is a probe-setup fact and not a model fact.
2. **The model cache lists Astra** with the same six effort levels Sol has
   (`low`, `medium`, `high`, `xhigh`, `max`, `ultra`), a `fast` service
   tier at "2x speed", and a `persistent_instructions` block Sol's entry
   lacks. Whether `codex exec` applies that block is unmeasured.
3. **The user's `~/.codex/config.toml` read `model = "gpt-6-astra"` and
   `model_reasoning_effort = "xhigh"` on 2026-09-04.** The notes currently
   say the canonical effort "is set in `~/.codex/config.toml`" too. That
   sentence is false today, and the per-call pin is the rule that makes
   the difference not matter.
4. **The GPT-6 guidance page, fetched 2026-09-04,** says Astra "is more
   likely to ask for clarification where earlier models would make
   assumptions", that migrations should "preserve your current effective
   reasoning effort", and that `none` is not a supported effort. It does
   NOT carry the six-element sentence, the migration-plan review example,
   the lean-prompt figure, or any repetition or negation advice.
5. **Every executable reads the id at runtime.** `run_behavioral_evals.py:813`,
   `tools/check-drift.ps1:1010`, and the doctor's probe all parse
   `Canonical model id:` from the notes. The dispatch tool and the
   attestation writer carry no model id at all.

## File Structure

- `BACKLOG.md` — item 87 added, ranked.
- `evals/multi-model-verify/test_multi_model_verify.py` — one new pin
  function; the `background-task-naming` region pin edited.
- `evals/multi-model-verify/test_seat_reshuffle.py` — the two composition
  pins edited.
- `skills/multi-model-verify/references/model-prompting-notes.md` — the
  reviewer-lane section rewritten; the task-naming region edited.
- `skills/multi-model-verify/references/panels.md` — lane label.
- `skills/multi-model-verify/references/fallbacks.md` — lane label.
- `skills/multi-model-verify/references/frozen-plan-format.md` — example.
- `skills/multi-model-verify/SKILL.md` — one word.
- `README.md` — seat table, diagram, panel prose.
- `CLAUDE.md` — task-name example.
- `evals/tools/run_behavioral_evals.py` — fixture header.

---

### Task 1: file backlog item 87

**Files:**
- Modify: `BACKLOG.md` (append the item after item 86; add `- 87` to the
  ranking)

**Interfaces:**
- Consumes: nothing.
- Produces: item 87, which Task 2's test docstring and the debate record
  cite by number.

- [ ] **Step 1: Append the item**

Append this text to the END of `BACKLOG.md`, after item 86's last
paragraph, separated by one blank line. The `Verified` line is written
with a PLACEHOLDER digest on purpose; step 3 replaces it.

```markdown
## 87. The primary reviewer lane runs GPT-5.6 Sol while GPT-6 Astra is available on the account
Status: OPEN
Cost: the reviewer is the gate every cycle runs through, and the pin is one line, so the swap is cheap and the prose around it is the whole cost
Pairs: none
Verified: 2026-09-04 000000000000

**Asked for by the user 2026-09-04**, the day GPT-6 Astra appeared in the
codex model list. The lane's canonical declaration in
`skills/multi-model-verify/references/model-prompting-notes.md` still
names `gpt-5.6-sol` at effort `high`.

**Measured 2026-09-04, codex-cli 0.153.4.** A doctor-shaped probe from a
scratch git fixture, with the dispatch's own isolation flags and
`--sandbox read-only`, sent `Reply with exactly: TRANSPORT-OK` to
`gpt-6-astra` at effort `low` and again at `high`. Both returned exit 0
and the exact reply, and the resolved header read `model: gpt-6-astra`,
`provider: openai`, `sandbox: read-only` with the pinned effort. So the
account tier does not gate Astra, and item 66's open question about tier
width does not block this swap. The first attempt failed with
`Not inside a trusted directory` because it ran from the temp directory,
which is a probe-setup fact: run probes from a git repository.

**The swap is not the one line the notes promise.** The pin IS one line
and every executable parses it, but the section around it describes
GPT-5.6: its heading, three bullets citing 5.6 prompt guidance, and an
effort bullet whose reasons were measured on Sol. That is item 74's
class, for the codex seat. The OpenAI GPT-6 guidance page, fetched
2026-09-04, no longer carries the six-element sentence, the review-task
example, or the lean-prompt figure the bullets cite; it does say Astra
"is more likely to ask for clarification where earlier models would make
assumptions", which matters for a non-interactive `codex exec` round.

**Decided by the user 2026-09-04:** Astra is the default at effort `high`;
Sol stays declared as an alternate at `high` that runs only when the user
names it, on the same transport and evidence rules; and the lane is
renamed Astra wherever the label is live, while historical citations that
name Sol stay as they are.
```

- [ ] **Step 2: Add the ranking line**

In the `## Ranking` section, under `### Third - changes to the workflow
itself`, add `- 87` as the LAST line of that group, after `- 70`.

- [ ] **Step 3: Compute the digest and write it**

Run: `python evals/tools/backlog_lint.py --digests`

Find the line for item 87. It prints the twelve-hex digest the `Verified`
field must carry. Replace `000000000000` on item 87's `Verified` line with
that digest. Do not change any other item.

- [ ] **Step 4: Run the lint to verify it passes**

Run: `python evals/tools/backlog_lint.py`
Expected: exit 0 and no failure line naming item 87.

- [ ] **Step 5: Commit**

```bash
git add BACKLOG.md
git commit -m "file item 87: the reviewer lane runs Sol while Astra is available"
```

---

### Task 2: swap the declarations and rewrite the reviewer-lane section

**Files:**
- Modify: `evals/multi-model-verify/test_multi_model_verify.py` (the
  `background-task-naming` pin at lines 1322-1340; one new function
  directly after `test_fable_notes_are_51_and_keep_their_measurement_limits`)
- Modify: `skills/multi-model-verify/references/model-prompting-notes.md`
  (the `## The reviewer lane` section from its heading through the
  `**Effort**` bullet, currently lines 141-215; the `background-task-naming`
  region, currently near line 486)
- Read only, must stay green: `evals/multi-model-verify/test_seat_reshuffle.py:296-299`
  (canonical before backup ordering), `evals/multi-model-verify/test_route_parser_shapes.py:79`

**Interfaces:**
- Consumes: item 87's number from Task 1.
- Produces: the declarations `Canonical model id: \`gpt-6-astra\``,
  `Canonical reasoning effort: \`high\``,
  `Alternate codex reviewer model id: \`gpt-5.6-sol\``,
  `Alternate codex reviewer effort: \`high\``. Task 3's prose refers to
  "the alternate declared in model-prompting-notes.md" and relies on those
  exact labels.

- [ ] **Step 1: Edit the task-naming region pin**

In `evals/multi-model-verify/test_multi_model_verify.py`, inside the
assertion that begins `"Name the backgrounded call for the person watching
it. The reviewer "`, change the one literal line

```python
    "LANE and the ROUND lead the description, as in `Sol R1 debate round` "
```

to

```python
    "LANE and the ROUND lead the description, as in `Astra R1 debate round` "
```

Nothing else in that assertion changes.

- [ ] **Step 2: Add the new pin function**

Directly after `test_fable_notes_are_51_and_keep_their_measurement_limits`
add:

```python
def test_reviewer_lane_is_astra_with_sol_as_the_explicit_alternate():
    """0.31.0 item 87. The heading and the four declarations are the
    lane's identity, so each is pinned. The canonical id is compared by
    prefix, never spelled out: test_reviewer_id_has_single_source sweeps
    this file for the literal. Heading and declarations are RAW-read
    pins on single physical lines; the two sentences are normalized.
    """
    raw = read(REFERENCES / "model-prompting-notes.md")
    notes = " ".join(raw.split())
    assert "## The reviewer lane (currently GPT-6 Astra via the codex CLI)" in raw
    canonical = re.search(r"Canonical model id: `([^`\n]+)`", raw)
    assert canonical and canonical.group(1).startswith("gpt-6-")
    effort = re.search(r"Canonical reasoning effort: `([^`\n]+)`", raw)
    assert effort and effort.group(1) == "high"
    alternate = re.search(r"Alternate codex reviewer model id: `([^`\n]+)`", raw)
    assert alternate and alternate.group(1) == "gpt-5.6-sol"
    alt_effort = re.search(r"Alternate codex reviewer effort: `([^`\n]+)`", raw)
    assert alt_effort and alt_effort.group(1) == "high"
    # The parsers resolve the FIRST canonical declaration; the alternate
    # and the backup both sit behind it, alternate first.
    assert (raw.index("Canonical model id:")
            < raw.index("Alternate codex reviewer model id:")
            < raw.index("Canonical backup reviewer model id:"))
    # The alternate is opt-in by name, never a fallback class.
    assert ("It is never selected automatically: it runs only when the"
            " user names Sol for a debate or a panel seat") in notes
    # A codex exec round has no one to answer a question.
    assert ("Every brief states that the round is non-interactive, that no"
            " clarification can be answered") in notes
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `python -m pytest "evals/multi-model-verify/test_multi_model_verify.py" -q -k "astra or background_task_naming or single_source"`

Expected: `test_reviewer_lane_is_astra_with_sol_as_the_explicit_alternate`
FAILS on the heading assertion; the task-naming pin FAILS because the
notes still read `Sol R1`; and `test_reviewer_id_has_single_source` FAILS
naming `evals/multi-model-verify/test_multi_model_verify.py`, because the
notes still declare `gpt-5.6-sol` and the new test now spells it. All
three are the expected red. Any other failure is not, and stops the task.

- [ ] **Step 4: Rewrite the reviewer-lane section**

In `skills/multi-model-verify/references/model-prompting-notes.md`,
replace everything from the line `## The reviewer lane (currently GPT-5.6
Sol via the codex CLI)` through the end of the `**Effort**` bullet (the
bullet that ends `never silently downgrade the review lane.`) with the
text below. The bullets that follow it, from `**Tool surface**` onward,
are untouched.

```markdown
## The reviewer lane (currently GPT-6 Astra via the codex CLI)

THE single source for the reviewer transport. Swapping the reviewer model
is a one-line edit HERE and nowhere else: the executable surfaces (the
behavioral runner's grader, the drift watch's cross-review) PARSE these
two declarations at runtime and fail loud when they are missing, and the
instruction surfaces (SKILL.md transport commands, /parallax:doctor's
probe, /parallax:drift-triage's example) direct the agent to read the
values from this file rather than type a remembered id. The consistency
test forbids a hardcoded `-m` model literal anywhere else in the repo.
The prose around the declarations is NOT one line: it describes the
model, and item 87 is the record of it describing the wrong one.

Canonical model id: `gpt-6-astra`

Canonical reasoning effort: `high`

Alternate codex reviewer model id: `gpt-5.6-sol`

Alternate codex reviewer effort: `high`

The alternate is GPT-5.6 Sol, the model this lane ran until 0.31.0. It is
never selected automatically: it runs only when the user names Sol for a
debate or a panel seat, on the same transport, the same flags, and the
same per-round evidence as the canonical model, with the effective-route
check made against the alternate declarations instead of the canonical
ones. The lane is then labelled Sol wherever the label is live: the task
name, the debate record's Participants line, and the attestation's
Participants value, so the record shows which model ran. It is not a
fallbacks.md class and no consent gate offers it. Nothing that parses the
canonical declarations reads the alternate ones: the behavioural grader,
the drift watch and the doctor's probe run the canonical model only.

- **Outcome-oriented briefs**: tell Astra the outcome to verify, not the
  steps to take. Its codex harness plans its own file reads. The
  six-element shape below came from OpenAI's GPT-5.6 prompt guidance
  (developers.openai.com/api/docs/guides/prompt-guidance, fetched
  2026-07-16), whose review-task example mapped directly onto our debate
  briefs. The same page, re-fetched 2026-09-04 for GPT-6, no longer
  carries that sentence, the review example, or the lean-prompt advice
  below. The shape is therefore OUR convention now, kept on this repo's
  own evidence, which is the behavioural suite grading briefs of this
  shape, and not on OpenAI's current word.
- **Six-element shape — goal, context, constraints, required evidence,
  success criteria, output format** (use only the parts that help). The
  XML-style tags below map onto it: task=goal, claims=context+evidence,
  rules=success criteria+output format, boundaries=constraints. The tags
  themselves are OUR convention, not OpenAI's, kept because the strike
  rule needs addressable sections to strike against.
- **Lean briefs, rules stated ONCE**: state the evidence rules and verdict
  grammar in full in round 1; later rounds REFERENCE them ("evidence
  rules and verdict grammar as before"), never restate. Avoid repeated
  negations ("do not mutate" three ways). Prefer decision rules over
  ALWAYS/NEVER except for true invariants (read-only sandbox, the strike
  rule, the verdict grammar). The 5.6-era figure behind this, that leaner
  prompts scored 10-15% better in OpenAI's own coding-agent evals, is not
  on the GPT-6 page and has not been re-measured here.
- **Non-interactive round, verdict required**: the GPT-6 guidance, fetched
  2026-09-04, says Astra "is more likely to ask for clarification where
  earlier models would make assumptions". A `codex exec` round has no one
  to answer. Every brief states that the round is non-interactive, that no
  clarification can be answered, and that a claim the reviewer cannot
  resolve goes under UNVERIFIED in the final check rather than into a
  question. A reply that ends in a question instead of a verdict is a
  spent round: its content is input, and the next round re-sends with the
  ambiguity closed. Whether Astra does this under `codex exec` is
  UNMEASURED; this is the guide's claim, written down before the first
  debate rather than after. One more observation, not a measurement: the
  model cache's Astra entry carries a `persistent_instructions` block
  Sol's entry lacks, and whether `codex exec` applies it is unknown.
- **Final check** (OUR convention, not OpenAI's): every brief ends by
  asking Astra to flag information it could NOT verify — those flags feed
  the strike rule instead of masquerading as findings.
- **Structure the brief with XML-style tags**:

  ```text
  <role>Adversarial reviewer, equal weight, in a two-model debate.</role>
  <task>Refute or confirm each numbered claim about the port plan below.</task>
  <rules>Cite References/<addon>/<file>:<line> for every claim you make or
  contest; uncited claims will be struck. Do not manufacture objections:
  if a claim stands, say PASS and move on. End with PASS, FIX (with the
  specific fix), or ESCALATE per claim.</rules>
  <claims>...numbered claims with the session's citations...</claims>
  <boundaries>...what is already decided and not under debate...</boundaries>
  <final-check>List any claim you could not verify against files you read,
  as UNVERIFIED — do not fold unverified material into your verdict.</final-check>
  ```

- **Effort**: pin `-c model_reasoning_effort=<canonical effort above>` per
  call. Do not raise it to xhigh, max or ultra for debate rounds: on Sol
  the effort propagated to every subagent it spawned, which burnt tokens
  without changing verdicts, and the same has NOT been measured on Astra,
  so the ceiling stands until it is. `~/.codex/config.toml` may carry a
  DIFFERENT default (it read `xhigh` on 2026-09-04), which is exactly why
  the value is pinned per call and the debate is config-independent. (The
  doctor's transport probe deliberately uses `low` — it is a reachability
  check, not a review.) The GPT-6 migration advice, fetched 2026-09-04, is
  to preserve the current reasoning effort, and `none` is not supported;
  `high` is therefore carried over, and `medium` remains a tuning
  candidate only via a full behavioral-suite pass at both levels. Never
  silently downgrade the review lane.
```

- [ ] **Step 5: Edit the task-naming region**

In the same file, inside the `<!-- contract:start id=background-task-naming -->`
region, change `as in \`Sol R1 debate round\`` to
`as in \`Astra R1 debate round\``. The region may rewrap; its pin is a
normalized read. Nothing else in the region changes.

- [ ] **Step 6: Run the tests to verify they pass**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py evals/multi-model-verify/test_seat_reshuffle.py evals/multi-model-verify/test_route_parser_shapes.py evals/multi-model-verify/test_contract_coverage.py -q`

Expected: all pass. `test_seat_reshuffle.py::test_panels_reference_pins`
still passes here because `panels.md` is untouched until Task 3.

- [ ] **Step 7: Run the skill checks**

Run: `python evals/tools/skill_lint.py skills/multi-model-verify --strict`
and `python evals/tools/skill_scanner.py skills`
Expected: both PASS. The notes file has no token ceiling; only `SKILL.md`
does, and it is untouched here.

- [ ] **Step 8: Commit**

```bash
git add evals/multi-model-verify/test_multi_model_verify.py skills/multi-model-verify/references/model-prompting-notes.md
git commit -m "swap the reviewer lane to gpt-6-astra, declare sol as the explicit alternate"
```

---

### Task 3: rename the lane's live labels

**Files:**
- Modify: `evals/multi-model-verify/test_seat_reshuffle.py:131-134`
- Modify: `skills/multi-model-verify/references/panels.md:4,12,14,49`
- Modify: `skills/multi-model-verify/references/fallbacks.md:217,236`
- Modify: `skills/multi-model-verify/references/frozen-plan-format.md:103`
- Modify: `skills/multi-model-verify/SKILL.md:213`
- Modify: `README.md:27,48,66,258,267`
- Modify: `CLAUDE.md:134`
- Modify: `evals/tools/run_behavioral_evals.py:237`

**Interfaces:**
- Consumes: Task 2's alternate declaration labels, cited in the panels
  text below.
- Produces: nothing other tasks read.

- [ ] **Step 1: Edit the composition pins**

In `evals/multi-model-verify/test_seat_reshuffle.py`, inside
`test_panels_reference_pins`, change

```python
    assert ("Valid compositions: Sol+Kimi, Sol+Fable, Kimi+Fable, "
            "Sol+Kimi+Fable.") in body
    assert ("Every panel contains at least one cross-vendor lane "
            "(Sol or Kimi); an all-Claude panel is invalid.") in body
```

to

```python
    assert ("Valid compositions: Astra+Kimi, Astra+Fable, Kimi+Fable, "
            "Astra+Kimi+Fable.") in body
    assert ("Every panel contains at least one cross-vendor lane "
            "(Astra or Kimi); an all-Claude panel is invalid.") in body
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest evals/multi-model-verify/test_seat_reshuffle.py::test_panels_reference_pins -q`
Expected: FAIL on the compositions assertion.

- [ ] **Step 3: Edit panels.md**

Line 4: `user-invoked only, never automatic. Sol solo stays the default;`
becomes `user-invoked only, never automatic. Astra solo stays the default;`.

Line 12, kept as ONE physical line:
`Valid compositions: Astra+Kimi, Astra+Fable, Kimi+Fable, Astra+Kimi+Fable.`

Line 14, kept as ONE physical line:
`Every panel contains at least one cross-vendor lane (Astra or Kimi); an all-Claude panel is invalid.`

Lines 49-50, the first transport bullet, become:

```markdown
- Astra: codex exec sessions per SKILL.md - env hygiene, header route
  checks, session resume. Unchanged. Sol, the alternate declared in
  model-prompting-notes.md, takes this seat on the same transport only
  when the user names it, and the seat is then labelled Sol.
```

- [ ] **Step 4: Edit fallbacks.md**

Line 217: `Sol, the backup-lane classes for Kimi; for the Fable panel seat, a`
becomes `Astra, the backup-lane classes for Kimi; for the Fable panel seat, a`.

Line 236: `remains: a surviving cross-vendor lane (Sol or Kimi) clean on`
becomes `remains: a surviving cross-vendor lane (Astra or Kimi) clean on`.

- [ ] **Step 5: Edit frozen-plan-format.md**

Line 103: `counted per lane (e.g. \`Sol 3 of 4 / Kimi 2 of 4\`); convergent blind`
becomes `counted per lane (e.g. \`Astra 3 of 4 / Kimi 2 of 4\`); convergent blind`.

- [ ] **Step 6: Edit SKILL.md**

Line 213: `exists. \`<label>\` names the lane and the round, as in \`Sol R1\`.`
becomes `exists. \`<label>\` names the lane and the round, as in \`Astra R1\`.`

- [ ] **Step 7: Edit README.md**

Line 27: `| Cross-vendor reviewer (primary) | GPT-5.6 Sol | OpenAI codex CLI, \`exec\` read-only |`
becomes `| Cross-vendor reviewer (primary) | GPT-6 Astra (GPT-5.6 Sol as a named alternate) | OpenAI codex CLI, \`exec\` read-only |`.

Line 48, inside the mermaid node text: `Sol · Kimi · Fable` becomes
`Astra · Kimi · Fable`.

Line 66: `any combination of the Sol, Kimi, and Fable lanes that keeps at least`
becomes `any combination of the Astra, Kimi, and Fable lanes that keeps at least`.

Line 258: `the Sol, Kimi, and Fable lanes — Sol+Kimi, Sol+Fable, Kimi+Fable, or`
becomes `the Astra, Kimi, and Fable lanes — Astra+Kimi, Astra+Fable, Kimi+Fable, or`.

Line 267: `default remains the bilateral Sol debate.` becomes
`default remains the bilateral Astra debate.`

- [ ] **Step 8: Edit CLAUDE.md**

Line 134: `leads with its LANE and ROUND, as in \`Sol R1 debate round\` or`
becomes `leads with its LANE and ROUND, as in \`Astra R1 debate round\` or`.

- [ ] **Step 9: Edit the behavioural fixture header**

In `evals/tools/run_behavioral_evals.py` line 237:
`**Participants:** Fable 5 (session) / GPT-5.6 Sol (codex exec, session eval-fixture)`
becomes
`**Participants:** Fable 5 (session) / GPT-6 Astra (codex exec, session eval-fixture)`.

- [ ] **Step 10: Confirm no live label was missed**

Run: `grep -rnE "\bSol\b" README.md CLAUDE.md skills/multi-model-verify/SKILL.md skills/multi-model-verify/references/panels.md skills/multi-model-verify/references/fallbacks.md skills/multi-model-verify/references/frozen-plan-format.md`

Expected: the only matches are the alternate's own sentences in
`panels.md` (the transport bullet) and `README.md` line 27. Every other
match is a live label that was missed; fix it and re-run.

- [ ] **Step 11: Run the full gate**

Run each, in order:

```bash
python evals/tools/skill_lint.py skills/multi-model-verify --strict
python evals/tools/skill_scanner.py skills
python evals/tools/check_exact_line_oracles.py
python evals/tools/run_trigger_evals.py
python -m pytest evals -q
python evals/tools/backlog_lint.py
```

Expected: every one exits 0. Record the `SKILL.md` token count the lint
prints; it must be below 6500.

- [ ] **Step 12: Commit**

```bash
git add evals/multi-model-verify/test_seat_reshuffle.py skills/multi-model-verify/references/panels.md skills/multi-model-verify/references/fallbacks.md skills/multi-model-verify/references/frozen-plan-format.md skills/multi-model-verify/SKILL.md README.md CLAUDE.md evals/tools/run_behavioral_evals.py
git commit -m "rename the codex reviewer lane from sol to astra where the label is live"
```

---

## After the tasks

1. Run the behavioural evals, local-only and opt-in, required because this
   branch changes reference text the grader reads:
   `python evals/tools/run_behavioral_evals.py --changed --head`. Record
   every skip it prints by name. The grader parses the canonical id from
   the notes, so this is the first real Astra round the repo runs.
2. Whole-branch review via `agents/fable-reviewer.md` over the exact
   `base..head` range, retained as a range-bound artifact.
3. Mode-diff debate on the same range, citing that artifact. The
   INSTALLED plugin is 0.30.1 and still dispatches Sol, so Sol reviews
   its own replacement; the record says so.
4. **Close item 87 in the backlog, in the same commit that changes its
   heading.** Mark it DONE with `Closed: 0.31.0`, delete its ranking line,
   rewrite the present-tense description as what the defect WAS, add the
   `Record:` path, and refresh the digest with `--digests`.
5. **Then** bump `.claude-plugin/plugin.json` to 0.31.0, because the
   debate is what moves the tree after the last build task.
6. Dev loop: `claude plugin marketplace update parallax`, then
   `claude plugin update parallax@parallax`, then verify the install BY
   CONTENT, then restart the session because `skills/` changed. The next
   debate after the restart is the first one Astra drives from the
   installed copy.

---

## Debate record

**Participants:** Fable 5.1 (session) / no reviewer lane at plan time
**Rounds used:** 0 of 4
**Outcome:** not debated
**Verification status:** DEGRADED
**Degradation:** plan-not-debated: the change is bounded, not a port or an API-sensitive module, and the design was approved by the user in chat on 2026-09-04; mode diff must cross-verify the plan's claims before verifying the implementation against it, per the degraded-plan poisoning rule
**Authorized by:** user at design approval, 2026-09-04
**Raw rounds:** not retained

### Resolved points
| # | Claim | Raised by | Outcome | Evidence |
|---|-------|-----------|---------|----------|
| 1 | Astra is reachable on this account at `low` and `high` | session | measured | probe of 2026-09-04, recorded in item 87 |
| 2 | Every executable parses the id at runtime | session | verified | `evals/tools/run_behavioral_evals.py:813`, `tools/check-drift.ps1:1010` |
| 3 | The 5.6 guidance the bullets cite is no longer on the page | session | verified | fetch of 2026-09-04 |

### Escalated points (user-decided)
| # | Point | Decision |
|---|-------|----------|
| 1 | Rename the lane or keep the Sol label | rename to Astra; Sol stays as a named alternate at `high` |
