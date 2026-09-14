# Single zero-judgment implementer design (backlog item 110)

Written 2026-09-13 from backlog item 110, the user's decision on the
item 109 fix. Item 109 holds the measurement: between 2026-09-09 and
2026-09-13, 122 of 128 build dispatches went to `parallax:implementer`,
54 of 54 in this repo, because two zero-judgment implementer files
carried near-identical descriptions and the harness's first match won.
0.38.0 fixed the descriptions. This design removes the second file and
makes the routing mechanical.

## The problem

`agents/implementer.md` exists so a Claude tier can type a frozen-plan
task directly. Its two remaining uses are a consent-gated reroute of a
task the Flash lane blocked, and transcription tasks under a Haiku
override. Neither needs its own zero-judgment file:
`agents/escalation-implementer.md` already accepts consent-gated
reroutes by its own description, and the Flash lane types verbatim code
at least as well as a Claude tier while leaving route evidence. As long
as the file exists it is a second implementer a session can pick, and
nothing mechanical sees the pick.

The fallback cannot move INTO `flash-implementer.md`: that wrapper's tool
grant has no Edit or Write, and the grant is what makes the authorship
check mean anything. A fallback branch on the same agent would need Edit
and Write, and a "Flash" run that fell back to Claude would produce the
same diff with no route line.

## Decisions (user, 2026-09-13)

- `agents/implementer.md` is deleted. Two implementer seats remain: the
  Flash build lane (`agents/flash-implementer.md`, Sonnet wrapper over
  Gemini 3.8 Flash via agy) and the Fable escalation lane
  (`agents/escalation-implementer.md`).
- A consent-gated reroute of a task the Flash lane blocked goes to the
  escalation lane with an EMPTY envelope. Any DECISIONS entry on an
  empty envelope is drift, so mode diff adjudicates a rerouted task as
  zero-judgment.
- The hook stays silent for a consented reroute when the dispatch prompt
  carries a `Lane:` line quoting the ledger record (the same line shape
  a plan-named task carries). The ledger and mode diff stay the real
  gates; the hook is a warning.
- Dated records are not rewritten. The 2026-07-25 Flash design spec,
  whose Decision A kept `implementer.md` as the direct-typing lane,
  gets one dated superseded line at its head pointing at item 110. SDD
  briefs, round transcripts and the other plans and specs that name the
  file stay as written and are listed in the sweep as records.

## Design

### 1. Seats and the empty envelope

`agents/escalation-implementer.md` is the only implementer a frozen plan
can route a task to besides the Flash lane. Its entry route 2 (blocked-task
reroute) is reworded: the reroute carries an EMPTY envelope by
construction, because the task was frozen as zero-judgment and consent to
reroute it is not consent to redesign it. The consent is recorded in the
cycle's SDD ledger before the agent starts, as today.

The file gains the `<!-- shared-contract:start -->` / `<!-- shared-contract:end -->`
markers around a block byte-identical to the Flash file's, placed as
its own section "The contract (outside the envelope)" ahead of "The
decision envelope". The envelope section already states the one
carve-out ("Outside the enumerated envelope the zero-judgment contract
applies unchanged"), so the shared block IS that contract and the
envelope section names where it is suspended. The report list keeps its
numbered `1. STATUS - ...` shape; nothing parses it, and
`test_seat_reshuffle.py` pins `DEVIATIONS - must be \`none\`` in that
shape.

`references/frozen-plan-format.md` lines 10 to 28 are rewritten. The
build lane paragraph keeps its pinned sentences (`Build lane:
parallax:flash-implementer`; `no \`ROUTE:\` line is a lane violation`) on
their own physical lines and names the two exceptions as:

- Freeze time: the plan routes a task to the escalation lane with an
  enumerated decision envelope, and the task text carries the line
  `Lane: parallax:escalation-implementer`.
- Build time: the Flash lane blocks a task, the user consents, the
  session records the consent in the SDD ledger, and the dispatch prompt
  carries `Lane: parallax:escalation-implementer (consented reroute, <ledger path>)`
  with an EMPTY envelope. Any DECISIONS entry on an empty envelope is
  drift.

The 0.38.0 measurement sentence stays, reworded to name the deleted file
as history (`parallax:implementer`, deleted in 0.39.0) rather than as a
live path.

### 2. The vendor-swap Lane note moves

`implementer.md`'s Lane note holds the two swap paths (another Claude
tier by frontmatter; another vendor by the supervisor pattern). The
supervisor pattern IS `flash-implementer.md`, so that file's Lane note
absorbs the vendor-swap paragraph and drops the sentence that says
`implementer.md` pins its own lane's model. README's "Every role is a
plug" list loses the "Implementer, Claude tier" bullet and points the
cross-vendor bullet at the Flash file's Lane note alone. The
`gemini-3.8-flash` literal's allowed homes shrink to
`agents/flash-implementer.md` and `test_flash_implementer.py`.

### 3. The hook

`hooks/superpowers-review-companion.ps1` already runs on every `Task|Agent`
call, for `PostToolUse` and `PostToolUseFailure`. It gains a first check,
ahead of the reviewer fingerprint:

- Read `tool_input.subagent_type`. Absent or empty: fall through (fails
  open, like the rest of the hook).
- If it matches `implementer` case-insensitively and is not exactly
  `parallax:flash-implementer`, the dispatch is an implementer dispatch
  to a lane other than the build lane. "During a build" is made
  mechanical as exactly this: an implementer dispatch IS the build, and
  no other state is consulted.
- Exemption: the prompt carries, on one line, `Lane:` followed by that
  exact `subagent_type` (`^\s*Lane:\s*<subagent_type>\b`, multiline, case
  sensitive on the type). The plan's task text carries that line at
  freeze time; a consented reroute pastes the ledger's line at build
  time. Silent.
- Otherwise inject `additionalContext` naming the rule: the build lane is
  `parallax:flash-implementer`; a task the plan routes elsewhere carries
  a `Lane:` line; a consented reroute carries the ledger's `Lane:` line;
  this dispatch carried neither, so either add the line from the plan or
  the ledger, or route the task to the Flash lane. Exit 0.

`PostToolUseFailure` matters here: after 0.39.0 a plan that still names
`parallax:implementer` fails at dispatch, and the failure event is where
the warning reaches the session.

### 4. Tests first

`evals/multi-model-verify/test_flash_implementer.py`:

- `CLASSIC` becomes `agents/escalation-implementer.md`; the parity test
  compares the shared block byte-for-byte as today.
- `test_flash_report_headings` pins the twin's heading words in its own
  shape: `STATUS -`, `FILES CHANGED -`, `VERIFICATION -`,
  `DEVIATIONS -`.
- `test_flash_lane_is_the_declared_default` drops the `implementer.md`
  frontmatter pins and pins: the Flash description no longer names a
  deleted agent; the escalation description still accepts
  consent-gated reroutes; `frozen-plan-format.md` carries
  `Lane: parallax:escalation-implementer`, the empty-envelope drift
  sentence, and no `agents/implementer.md` path.
- `test_classic_lane_note_retired_stale_claim` becomes a test that
  `agents/implementer.md` does not exist and that the Flash Lane note
  carries the vendor-swap paragraph.
- `ALLOWED` loses `CLASSIC`.
- A new test asserts the escalation file's entry route 2 says the
  envelope is empty.

`evals/multi-model-verify/test_multi_model_verify.py` `TestHook` gains
four cases through the existing `run_hook` helper: escalation dispatch
without a `Lane:` line warns; the same prompt with the line is silent;
`parallax:implementer` warns; `parallax:flash-implementer` is silent.
The existing reviewer-fingerprint cases stay unchanged and must stay
green, which is what proves the new check sits ahead of them without
swallowing them.

### 5. Sweep

Shapes searched: `implementer.md` not preceded by `flash-` or
`escalation-`; `parallax:implementer`; the bare word `implementer` in
`commands/`, `tools/`, `hooks/`, `README.md`, `skills/`. Live surfaces
found and edited: `README.md` lines 32, 99, 280; `frozen-plan-format.md`
lines 16, 18, 25; `flash-implementer.md` description and Lane note;
`test_flash_implementer.py`; BACKLOG item 110. Explicit none: doctor
check 7 and `tools/check-drift.ps1` name only `flash-implementer.md`.
Records listed, not edited: `CHANGELOG.md` v0.38.0, `.superpowers/sdd/`
briefs from July, `docs/superpowers/plans/rounds/*`, the seat-reshuffle
and contract-coverage plans and specs. The 2026-07-25 spec gets its
dated superseded line.

## Verification for this cycle

- The six gates in `CLAUDE.md`; the hook tests run under `pwsh`, which
  is the host `hooks.json` names.
- `python evals/tools/run_behavioral_evals.py --changed --head` for the
  reference and agent text changes.
- Live proof the build used the Flash lane: doctor check 7b's weekly
  Gemini figure read before and after the build.

## Non-goals

- Item 105's mechanical route check inside the Flash lane.
- Item 45 (moving the implementer lane) and item 55 (retiring the
  escalation implementer). Item 55's premise changes with this design:
  the escalation lane is now the only reroute target.
- A doctor row for the agent inventory; the doctor reads only the Flash
  file and that stays true.
