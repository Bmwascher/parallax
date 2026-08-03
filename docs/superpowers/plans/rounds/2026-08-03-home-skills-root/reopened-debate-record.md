# Reopened debate: the home skills root disposition

The frozen plan's Task 4 gate landed on SUPPRESSED BY THE FLAG and reserved that
branch to a reopened debate, because it is a contract change rather than a
disposition. This is that debate. **It settles text and scope. Nothing is
implemented, and the frozen plan is not yet amended.**

## Participants and evidence

| lane | model | transport | session | rounds |
|---|---|---|---|---|
| session | Opus 5 | - | - | driver and final adjudicator |
| primary reviewer | GPT-5.6 Sol | codex exec | `019fc8c0-5608-71d0-b32b-521248cbee24` | 4 |
| backup reviewer | Kimi K3 | kimi-code 0.31.1 | `session_feb0cc1b` write-probe, `session_2fff105c` rounds | 2 |

Both lanes were run. The backup lane was dispatched COLD from the same round-1
brief with no sight of the primary lane's answers, and the two were then
cross-examined against each other unattributed.

**Primary lane.** Preflight-3 enumeration over `*AGENTS.md`, `.agents/*` and
`.kimi-code/*` returned EMPTY, so the real tree was the reviewed tree. Context
probe `status: clean`, 29 advertised skills before and 0 after, `repo_scoped` 0,
`plugin_cache_scoped` 0, override SHA-256 `180f09f5...f432bb8`, verified
byte-identical before every dispatch. Route confirmed on every round:
`gpt-5.6-sol` / `openai` / `high` / `read-only`.

**One transport failure, recorded rather than hidden.** Round 1's first dispatch
exited 1 with `The 'gpt-5.6-codex' model is not supported when using Codex with a
ChatGPT account`. The cause was the driver's own: a REMEMBERED model id instead
of the canonical one read from `references/model-prompting-notes.md`. That is
exactly the failure the skill warns about, and it is why the reviewer id lives in
one file. Re-dispatched to FRESH round paths with `gpt-5.6-sol`. No reply file
was ever written by the failed call, so no stale reply could be read as a result.

**Backup lane.** Review mirror at HEAD `694f323`, 212-entry baseline captured
with the full status command. Write-probe PASS on all three legs in the SAME
debate home, before round 1: explicit refusal, marker absent, mirror delta 0.
Round evidence `status: clean` in FRESH form for round 1 and RESUME form for
round 2, so the session-scoped records were correctly absent from the resume and
it did not silently start a new session. `toolsHash` `3174a328...` and
`systemPromptHash` `f4410bdc...` matched round 1 byte for byte and match the
values this lane has recorded since the plan debate. Mirror delta 0 after both
rounds. Route line verified (client-side). Debate home removed, lane lock `free`,
lane credential re-reads `ok` / `valid`.

## What each lane got right, including against me

**The backup lane found a refutation neither the primary lane nor the session
made.** My claim that `--skills-dir` "suppresses all four roots" is not merely
unevidenced, it is INCOHERENT: the flag names `<debate-home>/skills/` as the
discovery root, so it cannot suppress its own target. It selects it. What it
suppresses is the other three. The primary lane accepted this on sight.

**The backup lane won the operational split.** The primary lane had recommended a
new `-CheckSkillsEmpty` parameter set run before EVERY fresh and resumed call.
The backup lane argued there is no measured writer to guard against, that a new
per-round check is itself a new false-clean surface needing pins and mutation
tests, and that the builder is the only writer so one postcondition inside it
covers the single moment content can enter. The session verified the crux
independently: `tools/new-kimi-lane-home.ps1:902` is the ONLY site in the whole
repository that writes to a debate-home skills directory, and it is the line that
creates it. The primary lane then CONCEDED in its own words: "I cannot name a
shipped writer after construction. My proposed per-call guard was therefore
against unknown or out-of-band mutation, not a measured writer."

**The primary lane won the locking split.** The backup lane had proposed ordinary
string pins and no contract regions. The primary lane showed that an ordinary
`"paragraph" in body` assertion catches edits INSIDE its literal but not a
weakening sentence appended after it, while a marked region fails coverage
because the pin must contain the region WHOLE. The session verified this in
`evals/multi-model-verify/contract_coverage.py:3` and `:390-396` before putting it
across, and the backup lane conceded: "I have no answer to the appended-sentence
case under my own proposal. Nothing in my mechanism catches it."

**Each lane refuted one of the other's supports.** The primary lane refuted the
backup lane's argument that per-round hashes already cover this: `toolsHash`,
`systemPromptHash`, `toolCount` and exact-list equality pin the effective CONTEXT
surface, not directory contents, so a populated skills directory with `Skill`
denied and no prompt change would move none of them. The backup lane's conclusion
survived on the no-shipped-writer argument alone, and it said so.

**Both lanes narrowed a claim of mine that the session had already published.**
Claim 4, that the lane has no hole today held by two INDEPENDENT things, is
narrowed: cells A and B ran with the deny list AND the flag both in force, so
they measure the conjunction. What is measured is that the shipped composition
showed no hole, not that either layer would suffice alone. The probe record
carries this as a dated correction at `7365299`.

## Settled

1. `~/.agents/skills/` is REACHABLE by kimi-code 0.31.1. Not unprobed.
2. `--skills-dir` REPLACES discovery with its target. Suppression is measured for
   the home root ALONE. The project roots were never canaried and rest on
   replacement semantics plus the client's help text; they are cleared by
   preflight-3 remediation in the mirror regardless. Both lanes agreed the narrow
   statement costs nothing, and the backup lane conceded it had stated the wide
   one from tidiness rather than evidence.
3. NO per-call emptiness check. ONE postcondition inside the builder, asserted
   immediately after it creates the directory, with a terminating enumeration
   including hidden entries and an exact zero-entry requirement, failing the build
   before custody JSON is emitted.
4. That postcondition is a self-check on the builder's own act, NOT a control
   against unknown writers, and the contract text must not imply otherwise. A
   fault seam can prove the detector fires for the reason it claims; it cannot
   prove the shipped lane can produce the state, and presenting it as threat
   evidence would be a claim wider than its evidence.
5. Both frozen region ids are used, `home-skill-root-disposition` and
   `home-skill-root-disposition-limit`, and both are added to `DECLARED_REGIONS`.
   The backup lane's proposed rename and the primary lane's earlier rename were
   both withdrawn.
6. `SKILL.md` says as little as possible and routes to the reference file, which
   is already required reading. That file is over its lint budget today, and the
   stale sentence there is pinned by nothing, so the correction is a shortening.
7. Scope: AMEND the frozen plan to revision 7 rather than start a new plan.
   Tasks 1 to 4 are complete and a new plan would orphan them. Task 5 is replaced
   outright, because it describes the NOT REACHABLE branch that did not occur and
   cannot be patched into correctness. Task 6 keeps its release role.
8. Verification status does not transfer silently. Revision 6 remains `FULL` for
   its own scope; revision 7 earns `FULL` only with this debate appended as the
   verification of the amendment.

## Open, and NOT the debate's to close

**User authorization for the scope in item 7.** The agreed change is roughly nine
files: two locked regions in `references/backup-lane.md`, a shortened paragraph in
`SKILL.md`, the builder postcondition and its dual-host tests, replacement pins
for four stale strings in `evals/multi-model-verify/test_backup_lane.py`, the
`DECLARED_REGIONS` additions, the plan amendment, the probe-record correction
already committed, and a `CLAUDE.md` line naming the new check. Tests change
FIRST throughout.

## Residual neither lane's mechanism closes

Raised by the backup lane, unprompted, against its own concession: a weakening
sentence appended AFTER a region's `contract:end` marker passes every check. The
region bounds in-region growth and marker deletion, not adjacency outside its own
markers. Every mechanism on the table shares this, and it is strictly smaller than
the plain-pin hole, so it changed nothing about the decision. Recorded because an
unrecorded known gap is how it becomes an unknown one.

## A note on the final text

Both lanes produced region bodies. They agree on substance and differ in
structure, and one measured finding appears in only one of them: the primary
lane's `systemPromptChars` sentence, which is the measured negative for the
system-prompt injection path and belongs in the limit region.

The text that goes into revision 7 is therefore a SESSION ADJUDICATION of both,
not either lane's wording verbatim, and it has not itself been through a round.
It will be reviewed as part of the amendment. Saying so here is the point: the
debate produced agreement on what must be true, and the exact sentences remain
reviewable rather than settled by assembly.

One practical caution for whoever implements it. Merging the two limit texts
makes that region longer than either lane sized, and a region must sit WHOLE
inside a SINGLE pin. Verify that it does before shipping it; if it does not, the
answer is not a looser pin, it is two regions, and a third region id is a scope
change this debate did not authorize.
