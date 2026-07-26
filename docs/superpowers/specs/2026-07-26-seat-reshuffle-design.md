# 0.14.0 Seat reshuffle, panels, README restructure — design

Date: 2026-07-26. Approved scope (user, this session): all three streams
together — seat reshuffle, panel modes, README restructure. Builds on
the Pipeline 2.0 rulings recorded 2026-07-25 (reference basis:
fable-advisor v4.0.0's architect move + mandatory end-review, adopted
while KEEPING Sol as reviewer and Flash as implementer — no vendor
grades its own homework). REVISED 2026-07-26 after a dual blind
advisory (Sol RETHINK + Kimi SOUND-WITH-FIXES; seven convergent
findings; all nine resolutions user-approved — see section 16).

## 1. Goal

Codify the post-0.13.0 seat lineup: any Claude model can drive the
session (Opus 5 after ship), a required Fable whole-branch review gates
mode diff, a Fable escalation implementer serves judgment-heavy and
blocked tasks, and multi-reviewer panels (any combination of Sol, Kimi,
Fable containing at least one cross-vendor lane) become invocable — plus
a full README restructure for a public audience.

## 2. Seats after 0.14.0

| Seat | Model | Basis |
|---|---|---|
| Session driver — debates, adjudicates, merges | Any Claude model (user `/model`; Opus 5 planned post-ship) | rules attach to the seat (debate-protocol.md) |
| Reviewer, primary | GPT-5.6 Sol via codex CLI | unchanged |
| Reviewer, backup (consent-gated) | Kimi K3 via kimi-cli | unchanged (0.13.0), + sanctioned panel route (section 6) |
| Reviewer, panel lane (Claude) | agents/fable-panel-reviewer.md (`model: fable`) | NEW — panels only |
| Final whole-branch reviewer | agents/fable-reviewer.md (`model: fable`) | NEW — required mode-diff input |
| Implementer, mechanical | Gemini 3.6 Flash via agy (flash-implementer) | unchanged |
| Implementer, transcription | Claude tier — implementer.md (frontmatter default `sonnet`; haiku per dispatch) | unchanged |
| Implementer, escalation | agents/escalation-implementer.md (`model: fable`) | NEW |

Cross-vendor independence is invariant: Sol/Kimi still gate every
merge; Fable seats never replace the cross-vendor gate.

## 3. agents/fable-reviewer.md

- Frontmatter: `model: fable`; tools Read, Grep, Glob — NO Bash and no
  write tools. The controller builds the diff package
  (scripts/review-package or equivalent git output redirected to one
  file) and hands the path; the agent's entire view is files it is
  given plus the repo read-only. Dropping Bash removes the
  prose-over-live-tools class entirely (the 0.13.0 lesson: prose
  refusal under live tools is priming, not containment).
- Role: the whole-branch pre-merge review — reads the frozen plan, the
  SDD ledger's deferred minors, and the controller-built diff package;
  returns Strengths / Issues (Critical, Important, Minor) /
  ledger-minors triage / Ready-to-merge verdict.
- OUTPUT IS A RETAINED, RANGE-BOUND ARTIFACT: the controller saves the
  raw reply to the cycle's rounds directory
  (docs/superpowers/plans/rounds/<cycle>/fable-review.md) together
  with the base/head SHAs it reviewed. Summary-only provenance is
  rejected, same as every other lane.
- Runs as a fresh subagent regardless of the driver model
  (fresh-context verification beats self-critique — notes.md). With
  Opus driving it is also cross-tier. It is NOT the cross-vendor gate
  and its verdict never substitutes for the diff debate.

## 4. Required mode-diff step (enforcement choice A)

SKILL.md mode diff gains a pinned step before the round-1 brief: the
fable-reviewer whole-branch review runs on the same range, the SESSION
adjudicates each of its findings with evidence (accept / refute /
defer — final-adjudication vocabulary, deliberately NOT the
application-checkpoint's "dispositioned"), and the round-1 brief cites
the retained review artifact path plus the adjudications. Exact pinned
sentence (single physical line, test-enforced):

`Required before round 1: the agents/fable-reviewer.md whole-branch review runs on the same range, its raw reply is retained as a range-bound artifact, and the round-1 brief cites that artifact with the session's per-finding adjudications.`

The Sol/Kimi debate remains the merge gate; the Fable review is its
required input. The debate record names the artifact path; the
attestation JSON is unchanged (section 8).

Revisit note (user, 2026-07-26): the enforcement point is expected to
move when the project swaps off superpowers; the pin makes the current
location explicit so the future move is a deliberate edit, not drift.

## 5. agents/escalation-implementer.md

- Frontmatter: `model: fable`; full implementation toolset.
- THE DECISION ENVELOPE: a frozen plan routing a task to this lane
  must ENUMERATE the task's open decision points (the judgment being
  delegated), each with the constraints that bound it. The lane's
  judgment is legitimate only inside that envelope.
- Report contract: STATUS / FILES CHANGED / VERIFICATION / DECISIONS /
  DEVIATIONS / CONCERNS. `DECISIONS` records one entry per enumerated
  decision point — the choice, why, and its evidence. `DEVIATIONS` is
  RETAINED with its existing meaning and must be `none`: anything
  outside the enumerated envelope is a deviation, exactly as in the
  zero-judgment lanes. Mode diff adjudicates DECISIONS against the
  envelope and treats envelope overruns as findings — judgment is
  authorized, drift is not.
- Two entry routes, both explicit:
  1. Plan-time designation: the frozen plan marks the task
     judgment-heavy, names this lane, and carries the envelope — the
     debate that froze the plan reviewed that routing.
  2. Blocked-task reroute: a blocked Flash (or Claude-lane) task may
     be rerouted here ONLY with user consent per the 0.12.0 ruling —
     the driver and the user both see the failure, then decide; the
     reroute message states the envelope. Unattended runs fail closed.

## 6. references/panels.md

- Invocation: user-invoked only. Sol solo stays the default; Kimi solo
  stays the consent-gated backup lane (unchanged).
- Compositions: ANY combination of the three reviewer lanes {Sol,
  Kimi, Fable} with two or more members — Sol+Kimi, Sol+Fable,
  Kimi+Fable, Sol+Kimi+Fable — subject to the invariant below.
- Invariant (test-pinned, single physical line): every panel contains
  at least one cross-vendor lane (Sol or Kimi). An all-Claude panel is
  invalid by contract.
- Topology: hub-and-spoke. The driver mediates; reviewer lanes never
  talk to each other directly; findings relay anonymously with their
  evidence (blind cross-examination). The driver verifies claims
  against the repo before relaying.
- SUBJECT-REVISION RULE: the driver pins the subject revision (git
  SHA for diffs; the plan file's blob hash for plans) in every round
  brief of every lane. An accepted amendment that changes the subject
  re-opens all lanes: a terminal verdict counts only when it cites
  the FINAL subject revision — a verdict against a stale revision is
  input, never terminal. (The bilateral freeze rule and 0.13.0's
  post-convergence delta-confirmation round, generalized.)
- Lane transports, all pre-existing machinery:
  - Sol: codex exec sessions, header route checks — unchanged.
  - Kimi: backup-lane.md containment, per-round offset evidence, and
    the pre-round-1 WRITE-PROBE — all unchanged and all REQUIRED in
    panels too. Panel participation is a sanctioned SECOND entry
    route added to backup-lane.md (one short paragraph): the user's
    panel invocation is the consent; no fallbacks banner (nothing
    degraded) and no failure class recorded (nothing substituted).
  - Fable: agents/fable-panel-reviewer.md (`model: fable`; tools
    Read, Grep, Glob — no Bash, no writes), a fresh subagent at
    round 1, kept across rounds by resume. Per-round evidence class
    (recorded in these words): dispatch metadata — the round-1
    dispatch names the model pin; the resume surface carries NO model
    parameter (probed 2026-07-26, section 15), so the pin cannot be
    silently swapped mid-debate; round continuity is evidenced by
    transcript recall; the failure mode is agent death, which is loud
    (a harness notification), class `panel-lane-loss`. The agent's
    self-reported identity is priming-class and never evidence — the
    same vocabulary discipline as every other lane.
- Convergence: each lane reaches its own terminal verdict under its
  own round cap against the final subject revision; the session
  adjudicates across lanes (debate-protocol final adjudication,
  unchanged); convergent blind findings are counted once and recorded
  as convergent.
- Recording: section 8.

## 7. Failure handling: panel-lane-loss

fallbacks.md (single failure-class namespace) gains one row:
`panel-lane-loss`. A lane failing mid-panel first resolves through its
own transport classes (codex classes for Sol, kimi classes for Kimi; a
dead Fable subagent is directly this class). If the lane cannot
continue, the panel STOPS AT THE CONSENT GATE — no automatic
continuation, ever: continuing with fewer lanes reduces evidence
quality, and no such transition happens without explicit user consent
(the governing fallbacks rule, unchanged). The gate offers: continue
with the remaining lanes (a single-lane remainder proceeds as an
ordinary bilateral debate and is recorded as such, not as a panel);
substitute the lost lane (the existing kimi substitution machinery,
where applicable); or abort. The lost lane's unresolved findings carry
into the record as OPEN — adjudicated by the session or re-raised with
a substitute, never silently dropped. A lost lane's incomplete round
is never adjudicated.

## 8. Declarations, notes, and record format

- model-prompting-notes.md: the `## Fable 5 (the session side)` section
  generalizes to `## The session driver seat` — seat-attached rules
  (grounding, boundaries, fresh-context verification) stay at the top,
  with per-model subsections beneath: a re-distilled Fable 5
  subsection, and a NEW Opus 5 subsection distilled from the official
  guide
  (platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5,
  fetched 2026-07-26): complete-spec-up-front strength; review
  precision guidance (never instruct "only report high-severity" —
  report everything, filter separately; converges with the existing
  no-pre-judging dispatch rule); effort economics (low/medium strong —
  re-sweep effort defaults rather than carrying them over);
  over-verification warning (remove explicit "verify your work"
  instructions — they compound); delegation appetite (cap subagent
  spawning explicitly; delegation guidance belongs in dispatch
  prompts); scope-control snippet for narrow tasks; 1M-window
  consistency. No parser reads this section heading — but the rename
  is probed against both runtime parsers before freeze anyway (0.13.0
  probe class; the parsers match `Canonical model id:` labels, which
  are untouched).
- Fable 5 subsection re-distillation (official guide
  platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5,
  fetched 2026-07-26 — the existing three bullets all appear in it
  and are RETAINED with the official citation): grounding progress
  claims (audit each claim against a tool result); state the
  boundaries (assessment-not-fix default); fresh-context verifier
  subagents outperform self-critique. NEW points, curated for the
  three new Fable seats: bug-finding recall is a strength
  (fable-reviewer basis); effort is the primary dial — high default,
  medium/low viable where quality holds (reviewer dispatches may
  sweep); over-prescriptive skills DEGRADE Fable 5 output — the new
  agent files state contracts and invariants, not step-by-step
  choreography; never instruct a Fable seat to echo or transcribe its
  internal reasoning (reasoning_extraction refusal class — report
  contracts ask for evidence and decisions, never thinking); the
  no-unrequested-refactor snippet backs the escalation lane's
  DECISIONS discipline.
- Backup-lane brief conventions get a cited basis: one bullet in
  notes.md's backup section distilled from Kimi's general
  prompt-best-practices guide
  (platform.kimi.ai/docs/guide/prompt-best-practice, fetched
  2026-07-26; generic, not K3-specific — noted as such): XML-style
  delimiters suit Kimi briefs (confirming the tag convention the
  0.13.0 debates already used); state steps explicitly for complex
  review tasks; grounding instructions carry an explicit
  cannot-find fallback (maps onto the UNVERIFIED discipline); prefer
  paragraph/bullet-count length guidance over word counts. Also
  evaluated: the K3 tool-calling guide
  (platform.kimi.ai/docs/guide/kimi-k3-tool-calling-best-practice,
  fetched 2026-07-26) — API-integration guidance (dynamic tool
  injection, tool_choice, prefix caching) that does not apply to the
  CLI-driven lane; its two applicable echoes are already design
  facts: minimal declared toolset (the five-tool allowlist) and
  reasoning effort fixed before the session (the config.toml pin,
  now with a cache-behavior rationale on record).
- No new model-id declarations: Fable seats are same-harness subagents
  whose model is pinned in their own agent frontmatter (the
  flash-implementer precedent). No new transports, no doctor changes.
- frozen-plan-format.md: panel recording — the Participants field
  lists every lane with its transport; Rounds are counted per lane;
  convergent blind findings are marked convergent in resolved rows;
  the required fable-review artifact path is named in the record; the
  STATUS FIELDS for a completed panel: `Verification status: FULL`
  requires every participating lane's per-round evidence clean AND
  every terminal verdict bound to the final subject revision; a
  consented post-loss continuation records the panel-lane-loss class
  and the consent, mirroring the lane-substitution paragraph's shape.
  One added paragraph beside the 0.13.0 lane-substitution rule.
- ATTESTATION MAPPING (emitter and verifier UNCHANGED — the
  mechanical gate keeps its schema): for a panel-reviewed diff,
  `-Rounds` = the maximum lane round count; `-Participants` names the
  driver and every lane; `-RouteNote` is the existing literal
  `effective route confirmed` ONLY under the STRICTEST-LANE RULE —
  every lane's every-round evidence matched that lane's own canonical
  declarations; any lane's route-attribution failure fails the
  aggregate (the reply is discarded and the failure routes through
  fallbacks.md, exactly as bilateral). Per-lane evidence classes live
  in the debate-record prose, never in the JSON.

## 9. Routing

- SKILL.md: overview names the required fable review and panels; mode
  diff carries the section-4 pinned sentence; both mode sections gain
  a one-line panel pointer (`Panels: any reviewer-lane combination per
  references/panels.md.` — count == 2, the backup-lane pin pattern).
- references/backup-lane.md: the panel-participation paragraph
  (section 6) — its only edit.
- README.md: restructured per section 10.
- CLAUDE.md accuracy fix: the repo is public, not private — BOTH
  instances (CLAUDE.md's "private" and README.md's "git auth for this
  private repo" line).

## 10. README restructure (approach A, public audience)

New order: pitch paragraph → expanded Current lineup table (all seats
from section 2, driver row noting "any Claude model — rules attach to
the seat") → one unified workflow mermaid including the fable
end-review gate and the panel option → What's in the box (updated
rows: three new agents, panels.md) → Fails loud (+ panel-lane-loss) →
short Panels section → Swapping lanes (driver swap = `/model`;
escalation lane bullet) → Requirements → Install → Verify → Drift
protection → Attestation lane → Application checkpoint → Pattern
lineage. Every section gets a completeness-and-consistency pass in the
seat vocabulary; formatting normalized (consistent tables, heading
depth, wrap width). Existing test pins (mermaid edge prefix, backup
table-row prefix, single-source sweeps) are preserved or consciously
amended WITH their tests in the same task — never left to drift.

## 11. Contract tests (TDD-first)

evals/multi-model-verify/test_seat_reshuffle.py lands RED before any
artifact:
- fable-reviewer.md exists; frontmatter `model: fable`; the exact
  frontmatter tools line pinned (Read, Grep, Glob — the
  test_flash_implementer.py pattern); the retained-artifact sentence
  present.
- fable-panel-reviewer.md exists; frontmatter `model: fable`; exact
  tools line pinned (Read, Grep, Glob); the dispatch-metadata
  evidence sentence and the no-model-parameter-on-resume sentence
  present.
- escalation-implementer.md exists; frontmatter `model: fable`; the
  DECISIONS and DEVIATIONS sections BOTH required (`DEVIATIONS` must
  be `none` retained); the envelope sentence and consent-gate
  sentence present.
- SKILL.md carries the section-4 required-step sentence (exact,
  count == 1) and the panel pointer (count == 2).
- panels.md exists; the any-combination enumeration, the cross-vendor
  invariant sentence, and the subject-revision rule sentence pinned
  exactly; panels.md joins REQUIRED_REFERENCE_FILES.
- backup-lane.md carries the panel-participation paragraph (pinned
  sentence).
- fallbacks.md carries the panel-lane-loss row with the
  consent-gate-stop sentence.
- frozen-plan-format.md carries the panel recording paragraph
  including the strictest-lane FULL condition.
- notes.md carries `## The session driver seat` and both per-model
  subsections; both runtime parser regexes still resolve the primary
  declarations (executed against the amended text, 0.13.0-style).
- README pins: lineup rows for the new seats; panels section heading;
  no "private" claim remains.
- Existing suites stay green throughout.

## 12. Behavioral eval

One MANUAL evals.json case (`panel-blind-relay`): a Sol+Kimi panel on
a small fixture — expectations pin the invariant check, blind
anonymous relay language, subject-revision citation, per-lane evidence
classes, per-lane terminal verdicts, and convergent-finding recording.
Manual because panels are user-invoked and multi-billable (the
runner's unconditional manual-skip is by design, as with the 0.13.0
backup case — live coverage comes from section 13's attended smoke,
which exercises the lane the manual case does not).

## 13. Verification and rollout

- Build order: tests RED → agent files (all three) → panels.md +
  backup-lane paragraph + fallbacks row + format paragraph →
  notes/SKILL routing → README restructure → evals.json case →
  attended finish.
- Dogfooding: this cycle's own final review is dispatched through the
  new agents/fable-reviewer.md file with its retained artifact (live
  verification of the required step).
- Attended smoke: a one-round SOL+FABLE mini-panel on a scratch brief
  — it exercises the NEW lane live (dispatch metadata, resume, blind
  relay, subject-revision citation, artifact retention) while
  containing a cross-vendor lane; Kimi's panel mechanics are
  already-live-proven transport (0.13.0) plus the write-probe, so the
  smoke goes where the untested risk is. Budget: codex weekly window
  via doctor 4b; the Kimi dashboard is the authority for any Kimi
  budgeting (0.13.0 lesson — no new probe surface invented).
- The escalation lane cannot be forced live — contract covered by
  tests; first real dispatch is whenever a task actually blocks or a
  plan designates one.
- Ship flow: bump 0.14.0, dev loop (cache update + restart),
  fable-review + Sol mode-diff debate, attestation, merge, push. The
  user flips `/model` to Opus 5 AFTER ship so this cycle's debate
  record stays single-driver (the 0.12.0 precedent).
- Plan-authoring rule for this and future cycles (0.13.1 lesson,
  recurred 3x): every hardcoded commit subject in the plan is
  imperative mood.

## 14. Out of scope

- Swapping off superpowers (future; will relocate the section-4
  enforcement point).
- codex exec --json structured transport (backlog).
- Driver-model automation: the `/model` switch is a user action, never
  repo machinery.
- Quickstart section for the README (deferred until asked; "A to
  begin with").
- Attestation schema extension for per-lane fields (deliberately
  deferred: the strictest-lane mapping keeps the mechanical gate
  stable; revisit if panel adoption makes per-lane JSON fields worth
  a schema version bump).

## 15. Probe record

- 2026-07-26 (this session, Claude Code harness): same-harness
  subagent resume probe — a `model: fable` general-purpose subagent
  dispatched with a stored token, then resumed via the harness resume
  surface. RESULT: the resumed agent recalled the token exactly
  (conversation state persists across resume); the resume surface
  carries NO model parameter (only recipient and message — verified
  against the tool schema), so the round-1 model pin cannot be
  silently swapped by a resume call — the inverse of the kimi
  bare-resume hazard; a dead agent surfaces as a loud harness
  notification. Settles the dual-advisory UNVERIFIED (both lanes) on
  Fable panel-lane feasibility. Self-reported identity in the reply
  is priming-class and was not counted as evidence.

## 16. Advisory record

Dual blind advisory on the pre-revision spec (2026-07-26; hub-and-
spoke, findings relayed anonymously): Sol (codex session
019f9d9a-869a-79a2-b348-4334585617d4, effective route confirmed)
verdict RETHINK; Kimi (session 493c77f6-7a26-4139-a369-34a2126c0c04,
contained clone, route/agent/tools evidence clean, clone delta clean)
verdict SOUND-WITH-FIXES. Seven convergent findings (Fable-lane
contract unspecified + resume unprobed; escalation report
contradiction; Kimi-in-panel charter conflict; fable-reviewer
containment; lane-loss consent; attestation schema; adjudication step)
plus Sol-only (subject-revision binding; Fable-lane live coverage) and
Kimi-only minors (second private-claim instance; kimi budget
authority; implementer.md label). All nine resolutions user-approved
2026-07-26 and folded into this revision. Raw replies retained in the
session scratchpad; confirmation round pending on this revision.
