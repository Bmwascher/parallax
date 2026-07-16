# Model prompting notes

## Fable 5 (the session side)

From Anthropic's Fable 5 prompting guide (distilled 2026-07; re-check the
guide when it updates):

- **Ground progress claims**: state what was actually run and observed, not
  what should have happened — the guide's grounding pattern nearly eliminated
  fabricated status reports in Anthropic's evals. In debate terms: your
  PASS/FIX verdicts cite the evidence you actually read this session.
- **State the boundaries**: tell the model what is out of scope explicitly.
  The debate brief states what is NOT under debate (already-decided user
  directives, e.g. equal-weight advisors, the chosen reference addon).
- **Fresh-context verification beats self-critique**: Fable reviewing its own
  plan in the same context rubber-stamps. That is the reason Sol exists in
  this loop — and the reason degraded mode (fallbacks.md) must run the
  skeptic pass in a FRESH subagent, not inline.

## The reviewer lane (currently GPT-5.6 Sol via the codex CLI)

THE single source for the reviewer transport. Swapping the reviewer model
is a one-line edit HERE and nowhere else: the executable surfaces (the
behavioral runner's grader, the drift watch's cross-review) PARSE these
two declarations at runtime and fail loud when they are missing, and the
instruction surfaces (SKILL.md transport commands, /crosscheck:doctor's
probe, /crosscheck:drift-triage's example) direct the agent to read the
values from this file rather than type a remembered id. The consistency
test forbids a hardcoded `-m` model literal anywhere else in the repo.

Canonical model id: `gpt-5.6-sol`

Canonical reasoning effort: `high`

- **Outcome-oriented briefs**: tell Sol the outcome to verify, not the steps
  to take. Its codex harness plans its own file reads. OpenAI's GPT-5.6
  guidance (developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6,
  2026-07-09): "state the goal, relevant context, constraints, required
  evidence, success criteria, and output format." Its own review-task
  example maps directly onto our debate briefs: "Review this database
  migration plan for failure modes... For each finding, cite the relevant
  step, estimate impact and likelihood, and recommend a specific
  mitigation."
- **Six-element shape — goal, context, constraints, required evidence,
  success criteria, output format** (the 5.6 framing; use only the parts
  that help). The XML-style tags below map onto it: task=goal,
  claims=context+evidence, rules=success criteria+output format,
  boundaries=constraints. The tags themselves are OUR convention, not
  OpenAI's — 5.6 prescribes no tags for review tasks — kept because the
  strike rule needs addressable sections to strike against.
- **Lean briefs, rules stated ONCE** (5.6 guidance; leaner prompts scored
  10-15% better in OpenAI's own coding-agent evals): state the evidence
  rules and verdict grammar in full in round 1; later rounds REFERENCE
  them ("evidence rules and verdict grammar as before"), never restate.
  Avoid repeated negations ("do not mutate" three ways) — 5.6 reads
  repetition as noise and it can trigger needless approval requests.
  Prefer decision rules over ALWAYS/NEVER except for true invariants
  (read-only sandbox, the strike rule, the verdict grammar).
- **Final check** (from the guide's review-task pattern): every brief ends by
  asking Sol to flag information it could NOT verify — those flags feed the
  strike rule instead of masquerading as findings.
- **Structure the brief with XML-style tags**:

  ```text
  <role>Adversarial reviewer, equal weight, in a two-model debate.</role>
  <task>Refute or confirm each numbered claim about the port plan below.</task>
  <rules>Cite References/<addon>/<file>:<line> for every claim you make or
  contest; uncited claims will be struck. Do not manufacture objections:
  if a claim stands, say PASS and move on. End with PASS, FIX (with the
  specific fix), or ESCALATE per claim.</rules>
  <claims>...numbered claims with Fable's citations...</claims>
  <boundaries>...what is already decided and not under debate...</boundaries>
  <final-check>List any claim you could not verify against files you read,
  as UNVERIFIED — do not fold unverified material into your verdict.</final-check>
  ```

- **Effort**: pin `-c model_reasoning_effort=<canonical effort above>` per
  call. Do not raise it to ultra/xhigh for debate rounds — Sol propagates
  its effort to every subagent it spawns, which burns tokens without
  changing verdicts. The same value is set in `~/.codex/config.toml`, but
  pin it per call anyway so the debate is config-independent. (The doctor's
  transport probe deliberately uses `low` — it is a reachability check, not
  a review.) 5.6 migration advice: "preserve your current reasoning effort
  as the baseline, then compare one level lower" — `medium` is a tuning
  candidate, but only via a full behavioral-suite pass at both levels;
  never silently downgrade the review lane.
- **Session resume, not context re-send**: capture the `session id:` from
  round 1 and resume it (flags before the subcommand). 5.6 persists its
  reasoning state across turns of a resumed session — re-sending the full
  context each round both wastes tokens and discards that state. NEVER
  `resume --last` — it grabs whatever codex session ran most recently,
  which may be a concurrent /codex:review, not your debate.
- **Fabrication counter**: Sol's METR/system-card record means "I verified X"
  claims from Sol get the same strike rule as everything else — quoted
  file:line or it did not happen.

## Reusable recipes

The installed codex plugin ships prompt recipes and antipatterns under its
`gpt-5-4-prompting` skill (plugin cache, `skills/gpt-5-4-prompting/`). They
were written for GPT-5.4-era codex: the structural advice (tight task
framing, no chain-of-thought micromanagement) still applies to Sol, but
verify any model-specific flag or behavior claim against current OpenAI docs
before relying on it.
