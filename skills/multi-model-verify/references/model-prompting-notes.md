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
instruction surfaces (SKILL.md transport commands, /parallax:doctor's
probe, /parallax:drift-triage's example) direct the agent to read the
values from this file rather than type a remembered id. The consistency
test forbids a hardcoded `-m` model literal anywhere else in the repo.

Canonical model id: `gpt-5.6-sol`

Canonical reasoning effort: `high`

- **Outcome-oriented briefs**: tell Sol the outcome to verify, not the steps
  to take. Its codex harness plans its own file reads. OpenAI's GPT-5.6
  guidance (developers.openai.com/api/docs/guides/prompt-guidance,
  fetched 2026-07-16; the review example also appears on
  /api/docs/guides/latest-model): "state the goal, relevant context, constraints, required
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
- **Final check** (OUR convention, not OpenAI's — the guide's review
  example asks for impact/likelihood/mitigation per finding, not an
  unverified-information pass): every brief ends by asking Sol to flag
  information it could NOT verify — those flags feed the strike rule
  instead of masquerading as findings.
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
- **Effective route confirmation (every call, fresh or resume)**: codex
  echoes the RESOLVED config in its startup header — capture stdout and
  check the first `model: `, `provider: `, and `reasoning effort: ` lines
  against the canonical declarations above (provider must be `openai`),
  the first `sandbox: ` line reads `read-only`, and on a resume that
  `session id: ` equals the id you resumed. A
  mismatch is a TRANSPORT failure (fallbacks.md consent gate), never a
  review result — a config.toml override or profile can silently swap the
  reviewer, and the header is where that surfaces. Vocabulary discipline:
  the header is CLIENT-RESOLVED metadata, so report "effective route
  confirmed", never "used and confirmed" (codex exposes no server-attested
  runtime identity); the reviewer's prose claiming a model name is never
  identity evidence. Probed 2026-07-19 (codex v0.144.1): fresh and resumed
  calls both emit the full header block. Probed 2026-07-24 (v0.144.1):
  sandbox mode has NO continuity across resumes — a resume WITHOUT
  `--sandbox read-only` resolved to the config default (`workspace-write`)
  on the SAME session id and a test write LANDED; with the flag before the
  `resume` subcommand the write was blocked and the header read
  `sandbox: read-only`. One omitted flag silently turns the read-only
  auditor into a writing agent; the `sandbox:` header line is the tripwire.
- **Env hygiene for the call — one sequence, one environment**: clear
  `CODEX_API_KEY`, `OPENAI_API_KEY`, and `OPENAI_BASE_URL` FIRST, then run
  the `codex login status` preflight, then dispatch — all in that same
  sanitized environment (a preflight in ambient env can pass or fail on
  overrides the dispatch never sees). The first two vars can flip auth to
  API-key billing, the base URL can reroute even ChatGPT-authenticated
  traffic. The preflight must report `Logged in using ChatGPT` — exit 0
  alone also passes an API-key login.
- **`CODEX_HOME` is reroute-capable**: probed 2026-07-24 (codex-cli
  0.144.1, Windows): with ambient `CODEX_HOME` pointed at an empty scratch
  directory, `codex login status` reported `Not logged in` (exit 1) while
  the real home reported `Logged in using ChatGPT` — the variable
  redirects auth.json and config.toml wholesale, so an ambient override
  can route a debate to a DIFFERENT ChatGPT account while every header
  line still reads clean (the header names model/provider, not account).
  Claim source: jinn (pinned 6c46f57) strips `CODEX_*` and re-pins
  `CODEX_HOME` per engine child (packages/jinn/src/shared/child-env.ts:31).
  Settles: `CODEX_HOME` is denylist-shaped; adoption pending the 0.10.0
  debate — the three-var denylist above is the live contract until then.
- **Session resume, not context re-send**: capture the `session id:` from
  round 1 and resume it (flags before the subcommand). OpenAI documents
  5.6 reasoning reuse across turns as CONDITIONAL (carried through
  previous_response_id-style continuation); whether `codex exec resume`
  engages it is not documented — the resume rule stands on token cost and
  preserved debate memory either way. NEVER `resume --last` — it grabs
  whatever codex session ran most recently, which may be a concurrent
  /codex:review, not your debate.
- **Lost-rollout resume failure is deterministic with a stable
  signature**: probed 2026-07-24 (codex-cli 0.144.1): `codex exec
  --sandbox read-only -m gpt-5.6-sol -c model_reasoning_effort=low
  --output-last-message <file> resume 00000000-0000-0000-0000-000000000000
  "<prompt>"` in a scratch fixture exited 1 with
  `Error: thread/resume: thread/resume failed: no rollout found for
  thread id <id> (code -32600)` and did NOT write the reply file.
  Settles: a missing-rollout resume is never transient — class
  missing-rollout in fallbacks.md skips the retry (adopted 0.10.0, debate
  2026-07-24). Claim source: jinn recognizes this same
  signature (packages/jinn/src/engines/codex.ts:363 @ 6c46f57) — its
  response (a warning-logged but automatic, unconsented fresh-thread
  restart) is the opposite of the consent gate and was not adopted.
- **AGENTS.md is an instruction back-channel**: codex auto-ingests a
  repo-root AGENTS.md into the reviewer's context. Probed 2026-07-24
  (v0.144.1): a planted AGENTS.md at the cwd repo root controlled the
  reply verbatim (an output-format directive was obeyed); an AGENTS.md in
  a non-git parent directory ABOVE the git root was NOT ingested. The
  preflight repo check in SKILL.md exists because of this. The user's own
  `~/.codex/AGENTS.md` (global instructions) is theirs by design —
  surfaced in the debate record when present, never a stop.
- **Repo-level `.agents/skills/` is a second instruction back-channel**:
  probed 2026-07-24 (codex-cli 0.144.1): in a scratch fixture repo whose
  only planted content was `.agents/skills/probe-skill/SKILL.md` (canary
  directives in both description and body), a fresh `codex exec` run's
  FIRST action was reading that file's full content at its exact path —
  no search preceded it, so the harness advertises repo-level
  `.agents/skills` entries to the model. The canary directive did not
  control that run's reply, but untrusted repo text entered the
  reviewer's context, which is the back-channel condition itself. The
  same run also loaded a skill from the user's own codex plugin cache
  (`~/.codex/plugins/cache/...`) — like `~/.codex/AGENTS.md`, the user's
  own by design: surface it in the debate record, never a stop.
  Settles: the preflight enumeration sweeps '.agents/*' alongside
  AGENTS.md (adopted 0.10.0, debate 2026-07-24). '.codex/' stays unswept
  — unprobed; probe before adding. Claim source: the jinn intake (pinned
  6c46f57; `.agents/skills/<name>` symlink convention at its repo root).
- **Fabrication counter**: Sol's METR/system-card record means "I verified X"
  claims from Sol get the same strike rule as everything else — quoted
  file:line or it did not happen.
- **Lane diagnostics (tier gating)**: a 400 "not supported when using
  Codex with a ChatGPT account" on the canonical id while `gpt-5.6-terra`
  responds confirms subscription tier-gating, not a CLI problem (free/Go
  tiers get Terra only; Plus and above get Sol — probed 2026-07-12). This
  feeds the consent gate in fallbacks.md; the ids live HERE because
  fallbacks.md never names models.
- **Structured quota state is locally readable (experimental)**: probed
  2026-07-24 (codex-cli 0.144.1): `codex app-server --stdio` with an
  NDJSON `initialize` (`capabilities.experimentalApi: true`, stdin held
  OPEN — the server exits when stdin closes) then
  `account/rateLimits/read` (id 2) answered in under 10s with per-limit
  windows (`usedPercent`, `windowDurationMins`, `resetsAt` epoch),
  `planType`, and credits. Handshake mirrored from jinn
  (packages/jinn/src/shared/engine-limits.ts:370-453 @ 6c46f57).
  Experimental capability — expect drift. Candidate /parallax:doctor
  quota-headroom line (adoption pending the 0.10.0 debate); complements,
  never replaces, the reactive quota-exhausted class.

## Reusable recipes

The installed codex plugin ships prompt recipes and antipatterns under its
`gpt-5-4-prompting` skill (plugin cache, `skills/gpt-5-4-prompting/`). They
were written for GPT-5.4-era codex: the structural advice (tight task
framing, no chain-of-thought micromanagement) still applies to Sol, but
verify any model-specific flag or behavior claim against current OpenAI docs
before relying on it.
