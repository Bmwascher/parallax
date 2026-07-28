# Model prompting notes

## The session driver seat

The driver seat is whatever Claude model runs the session — the debate
rules, final adjudication, and grounding discipline attach to the SEAT
(debate-protocol.md), not the model. Seat-invariant rules, present in
both official Anthropic guides (fetched 2026-07-26; re-check when they
update):

- **Ground progress claims**: state what was actually run and observed,
  not what should have happened — the guides' grounding pattern nearly
  eliminated fabricated status reports in Anthropic's evals. In debate
  terms: your PASS/FIX verdicts cite the evidence you actually read
  this session.
- **State the boundaries**: tell the model what is out of scope
  explicitly. The debate brief states what is NOT under debate
  (already-decided user directives, e.g. equal-weight advisors, the
  chosen reference addon).
- **Fresh-context verification beats self-critique**: a driver
  reviewing its own plan in the same context rubber-stamps. That is
  the reason the cross-vendor reviewer exists in this loop — and the
  reason degraded mode (fallbacks.md) must run the skeptic pass in a
  FRESH subagent, not inline. It is also why the required whole-branch
  review (agents/fable-reviewer.md) runs as a fresh subagent even when
  Fable itself drives.

### Fable 5

From the official Fable 5 guide
(platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5,
fetched 2026-07-26) — the three seat-invariant rules above appear in
it near-verbatim; Fable-specific additions:

- Bug-finding recall is a documented strength — the basis for the
  fable-reviewer seat.
- Effort is the primary dial: high default; medium/low viable where
  quality holds (reviewer dispatches may sweep effort with evals,
  never silently).
- Over-prescriptive skill text DEGRADES Fable 5 output — the Fable
  seat agent files state contracts and invariants, not step-by-step
  choreography.
- Never instruct a Fable seat to echo or transcribe its internal
  reasoning (the reasoning_extraction refusal class): report
  contracts ask for evidence and decisions, never thinking.
- Same-harness Fable seats (panel lane, whole-branch reviewer,
  escalation) resume probe, 2026-07-26, Claude Code 2.1.220:
  conversation state persists across resume and the resume surface
  carries no model parameter — full record with literal payloads at
  docs/superpowers/plans/rounds/2026-07-26-seat-reshuffle/subagent-resume-probe.md;
  the dead-agent case is narrowed to the 0.14.0 smoke's observation
  scope.

### Opus 5

From the official Opus 5 guide
(platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5,
fetched 2026-07-26), for when Opus 5 takes the driver seat:

- Strongest when given the complete task specification up front and
  left to run — the frozen-plan discipline is already this shape.
- Review dispatches: never instruct "only report high-severity
  issues" — it complies literally and under-reports; ask for
  everything and filter in adjudication (converges with the existing
  no-pre-judging dispatch rule).
- Effort economics: low/medium strong — re-run an effort sweep rather
  than carrying prior defaults; xhigh for the hardest work only.
- Over-verification: remove explicit "verify your work" instructions —
  Opus 5 verifies unprompted and such instructions compound into
  wasted tokens.
- Delegation appetite: it spawns subagents readily — dispatch prompts
  carry explicit delegation guidance and caps.
- Scope control for narrow tasks: instruct "deliver what was asked,
  at the scope intended" — it can otherwise widen tasks on its own
  judgment.
- 1M-token context window with consistent instruction following
  throughout.

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
  <claims>...numbered claims with the session's citations...</claims>
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
  `CODEX_API_KEY`, `OPENAI_API_KEY`, `OPENAI_BASE_URL`, and `CODEX_HOME`
  FIRST, then run the `codex login status` preflight, then dispatch —
  all in that same sanitized environment (a preflight in ambient env can
  pass or fail on overrides the dispatch never sees). The first two vars
  can flip auth to API-key billing, the base URL can reroute even
  ChatGPT-authenticated traffic. The preflight must report `Logged in
  using ChatGPT` — exit 0 alone also passes an API-key login. `CODEX_HOME`
  redirects auth.json and config.toml wholesale (see its probe bullet
  below); clearing it reverts codex to the default home, so a legitimately
  relocated home fails the auth preflight LOUDLY instead of silently
  rerouting the lane.
- **`CODEX_HOME` is reroute-capable**: probed 2026-07-24 (codex-cli
  0.144.1, Windows): with ambient `CODEX_HOME` pointed at an empty scratch
  directory, `codex login status` reported `Not logged in` (exit 1) while
  the real home reported `Logged in using ChatGPT` — the variable
  redirects auth.json and config.toml wholesale, so an ambient override
  can route a debate to a DIFFERENT ChatGPT account while every header
  line still reads clean (the header names model/provider, not account).
  Claim source: jinn (pinned 6c46f57) strips `CODEX_*` and re-pins
  `CODEX_HOME` per engine child (packages/jinn/src/shared/child-env.ts:31).
  Settles: `CODEX_HOME` is in the env denylist (adopted 0.10.0, debate
  2026-07-24).
- **Session resume, not context re-send**: capture the `session id:` from
  round 1 and resume it (flags before the subcommand). OpenAI documents
  5.6 reasoning reuse across turns as CONDITIONAL (carried through
  previous_response_id-style continuation); whether `codex exec resume`
  engages it is not documented — the resume rule stands on token cost and
  preserved debate memory either way. NEVER `resume --last` — it grabs
  whatever codex session ran most recently, which may be a concurrent
  /codex:review, not your debate.
- **Concurrency: safe across DISTINCT sessions THAT ALSO USE DISTINCT
  FILES, never within one session.** This lane's route evidence is the
  calling process's OWN startup header plus its OWN
  `--output-last-message` file, so NO SHARED GLOBAL OUTPUT LOG is parsed
  for route attribution — the structural difference from the backup lane,
  whose evidence comes out of one user-global log and therefore needs
  `tools/kimi-lane-lock.ps1`. No such lock is needed here. codex does still
  share auth, config, session storage and quota; none of that is read as
  evidence.
  Distinct session ids are necessary and NOT sufficient. Each concurrent
  invocation must also write to its own transcript and reply paths: the
  round-numbered names the freshness rule requires are unique within a
  debate and NOT across two debates running at once, so two callers using
  `reply-r1.md` can truncate or overwrite each other and pair one session's
  header with another session's reply. Probed 2026-07-28 (codex-cli
  0.144.1) in exactly that distinct-path arrangement: three simultaneous
  `codex exec` calls, plus a fourth review already running, each returned
  its own `session id:` with the canonical model and effort and its own
  correct reply. Resuming the SAME session id twice at once is never safe —
  one conversation, one rollout, two writers — so run parallel rounds as
  separate debates, never as two turns of one. Quota is shared, which makes
  parallel rounds faster and not cheaper.
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
  Experimental capability — expect drift. The doctor's quota-headroom row
  (check 4b) reads this surface (adopted 0.10.0, debate 2026-07-24);
  complements, never replaces, the reactive quota-exhausted class.

## Reusable recipes

The installed codex plugin ships prompt recipes and antipatterns under its
`gpt-5-4-prompting` skill (plugin cache, `skills/gpt-5-4-prompting/`). They
were written for GPT-5.4-era codex: the structural advice (tight task
framing, no chain-of-thought micromanagement) still applies to Sol, but
verify any model-specific flag or behavior claim against current OpenAI docs
before relying on it.

## The backup reviewer lane (currently Kimi K3 via kimi-cli)

THE single source for the BACKUP reviewer's identity — the same
swap-by-one-edit rule as the primary declarations above, and the same
consistency-test enforcement (the backup literal is forbidden
everywhere else; command surfaces carry `<canonical-backup-model-id>`).
The primary declarations above MUST stay ahead of this block: both
runtime parsers match the first `Canonical model id:` occurrence, and
the drift script's PowerShell match is case-insensitive.

Canonical backup reviewer model id: `kimi-code/k3-256k`

Canonical backup thinking flag: `--thinking`

Everything else about the lane — transport, containment, per-round
evidence, client config surface, mirror isolation, failure routing —
lives in references/backup-lane.md. The lane enters through the fallbacks.md
consent gate, or via a user-invoked panel (references/panels.md).

Brief conventions for the backup lane (from Kimi's general prompt
best-practices guide, platform.kimi.ai/docs/guide/prompt-best-practice,
fetched 2026-07-26 — generic, not K3-specific): XML-style delimiters
suit Kimi briefs (the tag convention the 0.13.0 debates used); state
steps explicitly for complex review tasks; grounding instructions
carry an explicit cannot-find fallback (the UNVERIFIED discipline);
prefer paragraph/bullet-count length guidance over word counts. The K3
tool-calling guide
(platform.kimi.ai/docs/guide/kimi-k3-tool-calling-best-practice,
fetched 2026-07-26) was evaluated: API-integration guidance
inapplicable to the CLI-driven lane; its two applicable echoes are
already design facts — the minimal five-tool allowlist and reasoning
effort fixed before the session (the config.toml pin; mid-session
changes would also break prefix caching per the guide).
