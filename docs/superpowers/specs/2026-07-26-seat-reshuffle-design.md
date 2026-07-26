# 0.14.0 Seat reshuffle, panels, README restructure — design

Date: 2026-07-26. Approved scope (user, this session): all three streams
together — seat reshuffle, panel modes, README restructure. Builds on
the Pipeline 2.0 rulings recorded 2026-07-25 (reference basis:
fable-advisor v4.0.0's architect move + mandatory end-review, adopted
while KEEPING Sol as reviewer and Flash as implementer — no vendor
grades its own homework).

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
| Reviewer, backup (consent-gated) | Kimi K3 via kimi-cli | unchanged (0.13.0) |
| Reviewer, panel lane (Claude) | Fable subagent, same-harness | NEW — panels only |
| Final whole-branch reviewer | agents/fable-reviewer.md (`model: fable`) | NEW — required mode-diff input |
| Implementer, mechanical | Gemini 3.6 Flash via agy (flash-implementer) | unchanged |
| Implementer, transcription | Claude Haiku tier (implementer.md) | unchanged |
| Implementer, escalation | agents/escalation-implementer.md (`model: fable`) | NEW |

Cross-vendor independence is invariant: Sol/Kimi still gate every
merge; Fable seats never replace the cross-vendor gate.

## 3. agents/fable-reviewer.md

- Frontmatter: `model: fable`; tools Read, Grep, Glob, Bash (Bash for
  read-only git inspection only; contract text forbids mutation).
- Role: the whole-branch pre-merge review this project has run
  informally since 0.12.0 — reads the frozen plan, the SDD ledger's
  deferred minors, and a controller-built diff package; returns
  Strengths / Issues (Critical, Important, Minor) / ledger-minors
  triage / Ready-to-merge verdict.
- Runs as a fresh subagent regardless of the driver model
  (fresh-context verification beats self-critique — notes.md). With
  Opus driving it is also cross-tier; with Fable driving it is
  same-model but fresh-context. Either way it is NOT the cross-vendor
  gate and its verdict never substitutes for the diff debate.

## 4. Required mode-diff step (enforcement choice A)

SKILL.md mode diff gains a pinned step before the round-1 brief: the
fable-reviewer whole-branch review runs first, and its findings enter
the diff-debate brief as dispositioned context (the 0.13.0 flow, made
contractual). The Sol/Kimi debate remains the merge gate; the Fable
review is its required input. Exact pinned sentence (single physical
line, test-enforced):

`Required before round 1: the agents/fable-reviewer.md whole-branch review runs on the same range, and its dispositioned findings enter the round-1 brief.`

Revisit note (user, 2026-07-26): the enforcement point is expected to
move when the project swaps off superpowers; the pin makes the current
location explicit so the future move is a deliberate edit, not drift.

## 5. agents/escalation-implementer.md

- Frontmatter: `model: fable`; full implementation toolset.
- Unlike the zero-judgment lanes, it MAY exercise implementation
  judgment within the task's stated intent — and must log every
  judgment call in a required `DECISIONS` report section, which the
  task review audits alongside the diff.
- Report contract otherwise mirrors implementer.md (STATUS / FILES
  CHANGED / VERIFICATION / DECISIONS / CONCERNS).
- Two entry routes, both explicit:
  1. Plan-time designation: the frozen plan marks a task
     judgment-heavy and names this lane — the frozen plan itself is
     the authorization (the debate reviewed that routing).
  2. Blocked-task reroute: a blocked Flash (or haiku-lane) task may be
     rerouted here ONLY with user consent per the 0.12.0 ruling — the
     driver and the user both see the failure, then decide. Unattended
     runs fail closed, mirroring fallbacks.md discipline.

## 6. references/panels.md

- Invocation: user-invoked only. Sol solo stays the default; Kimi solo
  stays the consent-gated backup lane (unchanged surfaces).
- Compositions: ANY combination of the three reviewer lanes {Sol,
  Kimi, Fable} with two or more members — Sol+Kimi, Sol+Fable,
  Kimi+Fable, Sol+Kimi+Fable — subject to the invariant below.
- Invariant (test-pinned, single physical line): every panel contains
  at least one cross-vendor lane (Sol or Kimi). An all-Claude panel is
  invalid by contract — the case that matters once Opus drives and a
  Fable lane exists.
- Topology: hub-and-spoke. The driver mediates; reviewer lanes never
  talk to each other directly; findings relay anonymously with their
  evidence (blind cross-examination — the 0.13.0 pattern that caught
  defects sequential review missed). The driver verifies claims
  against the repo before relaying.
- Each lane runs the EXISTING bilateral protocol and transport
  unchanged: Sol = codex exec sessions with header route checks; Kimi
  = backup-lane.md containment + per-round offset evidence; Fable = a
  fresh same-harness fable subagent kept across rounds via resume.
  Fable-lane evidence class is recorded honestly as same-harness
  dispatch metadata (no external transport; no route header exists) —
  the record prose names the class, mirroring the client-side
  vocabulary discipline of the other lanes.
- Convergence: each lane reaches its own terminal verdict under its
  own round cap; the session adjudicates across lanes (debate-protocol
  final adjudication, unchanged); convergent blind findings are
  counted once and recorded as convergent.
- Recording: see section 8.

## 7. Failure class

fallbacks.md (single failure-class namespace) gains one row:
`panel-lane-loss` — a lane failing mid-panel routes through its own
existing failure classes first (codex classes, kimi classes; a Fable
subagent death is a harness error); if the lane cannot continue, the
panel proceeds with the remaining lanes when the cross-vendor
invariant still holds, else it stops at the consent gate. The reply of
a lost lane's incomplete round is never adjudicated.

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
  paragraph/bullet-count length guidance over word counts.
- No new model-id declarations: Fable seats are same-harness subagents
  whose model is pinned in their own agent frontmatter (the
  flash-implementer precedent). No new transports, no doctor changes.
- frozen-plan-format.md: panel recording — the Participants field
  lists every lane with its transport, Rounds counts per lane,
  convergent blind findings are marked convergent in resolved rows.
  One added paragraph beside the 0.13.0 lane-substitution rule.

## 9. Routing

- SKILL.md: overview names the required fable review and panels; mode
  diff carries the section-4 pinned sentence; both mode sections gain
  a one-line panel pointer (`Panels: any reviewer-lane combination per
  references/panels.md.` — count == 2, the backup-lane pin pattern).
- README.md: restructured per section 10.
- CLAUDE.md accuracy fix (one line): the repo is public, not private.

## 10. README restructure (approach A, public audience)

New order: pitch paragraph → expanded Current lineup table (all eight
seats from section 2, driver row noting "any Claude model — rules
attach to the seat") → one unified workflow mermaid including the
fable end-review gate and the panel option → What's in the box
(updated rows: two new agents, panels.md) → Fails loud (+
panel-lane-loss) → short Panels section → Swapping lanes (driver swap
= `/model`; escalation lane bullet) → Requirements → Install → Verify
→ Drift protection → Attestation lane → Application checkpoint →
Pattern lineage. Every section gets a completeness-and-consistency
pass in the seat vocabulary; formatting normalized (consistent tables,
heading depth, wrap width). Existing test pins (mermaid edge prefix,
backup table-row prefix, single-source sweeps) are preserved or
consciously amended WITH their tests in the same task — never left to
drift.

## 11. Contract tests (TDD-first)

evals/multi-model-verify/test_seat_reshuffle.py lands RED before any
artifact:
- fable-reviewer.md exists; frontmatter `model: fable`; read-only
  contract sentence present.
- escalation-implementer.md exists; frontmatter `model: fable`;
  `DECISIONS` required-section text present; consent-gate sentence
  present.
- SKILL.md carries the section-4 required-step sentence (exact,
  count == 1) and the panel pointer (count == 2).
- panels.md exists; the any-combination enumeration and the
  cross-vendor invariant sentence pinned exactly; panels.md joins
  REQUIRED_REFERENCE_FILES.
- fallbacks.md carries the panel-lane-loss row.
- frozen-plan-format.md carries the panel recording paragraph.
- notes.md carries `## The session driver seat` and both per-model
  subsections; both runtime parser regexes still resolve the primary
  declarations (executed against the amended text, 0.13.0-style).
- README pins: lineup rows for the three new seats; panels section
  heading.
- Existing suites stay green throughout (154+1skip baseline grows by
  the new file's count).

## 12. Behavioral eval

One MANUAL evals.json case (`panel-blind-relay`): a Sol+Kimi panel on
a small fixture — expectations pin the invariant check, blind
anonymous relay language, per-lane evidence classes, per-lane terminal
verdicts, and convergent-finding recording. Manual because panels are
user-invoked and double-billable; the same treatment the
backup-lane case received in 0.13.0.

## 13. Verification and rollout

- Build order: tests RED → agent files → panels.md + fallbacks row +
  format paragraph → notes/SKILL routing → README restructure →
  evals.json case → attended finish.
- Dogfooding: this cycle's own final review is dispatched through the
  new agents/fable-reviewer.md file (live verification of the required
  step); the attended task adds a one-round Sol+Kimi mini-panel smoke
  on a scratch brief, budgeted against the Kimi 5-hour window and the
  codex weekly window (doctor 4b first).
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
