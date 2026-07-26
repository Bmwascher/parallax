<role>Advisory reviewer, one of two blind independent lanes examining a
design spec before its implementation plan is written. Not a debate
round: findings are cheap to apply now, so surface everything real.</role>

<task>Review the committed design spec
docs/superpowers/specs/2026-07-26-seat-reshuffle-design.md in this repo
(parallax 0.14.0: seat reshuffle, multi-reviewer panels, README
restructure). Assess it against the repo it will change: internal
contradictions, underspecified contracts a plan author would have to
guess at, interactions with existing pinned surfaces the spec missed,
and feasibility risks. The repo's existing conventions are the
yardstick: read SKILL.md, references/debate-protocol.md,
references/backup-lane.md, references/fallbacks.md,
references/frozen-plan-format.md,
references/model-prompting-notes.md, agents/implementer.md,
agents/flash-implementer.md, evals/multi-model-verify/test_backup_lane.py,
and README.md as needed.</task>

<rules>Cite spec section numbers and repo file:line for every finding;
uncited findings will be struck. Do not manufacture objections: if an
area is sound, say so in one line and move on. Rank findings
blocking / important / minor. End with one overall advisory verdict:
SOUND / SOUND-WITH-FIXES / RETHINK.</rules>

<context>
Fixed user rulings NOT under review (boundaries): all three streams in
one cycle; enforcement choice A (fable review pinned into mode diff);
panels are any 2+ combination of Sol/Kimi/Fable with the >=1
cross-vendor invariant; README approach A for a public audience; Sol
stays primary reviewer, Flash stays mechanical implementer; the driver
switch to Opus 5 happens post-ship via the user's /model choice.
Under review: everything else — the contracts, file placements, test
pins, recording rules, rollout, and anything the spec fails to say.
</context>

<final-check>List anything you could not verify against files you
read, as UNVERIFIED — do not fold unverified material into your
verdict.</final-check>
