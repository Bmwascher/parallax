# parallax

**Cross-model verification for Claude Code.** Two equal-weight frontier
models — the session model and a cross-vendor reviewer (via the OpenAI
codex CLI; the current reviewer lane is declared in the skill's
model-prompting-notes.md) —
verify and refute each other's claims with file:line evidence *before* a
cheaper implementer touches code, and again *before* the result merges.
Neither vendor grades its own homework.

Companion to [superpowers](https://github.com/obra/superpowers), not a
replacement: it fills the cross-model review gap superpowers rules out of
scope.

## How it works

```mermaid
flowchart LR
    A[superpowers<br/>brainstorm] --> B{{"mode plan debate<br/>session ⇄ reviewer"}}
    B -->|converged| C["frozen plan<br/>+ debate record"]
    B -->|escalated| U[user decides]
    C --> D["implementer subagent<br/>(zero judgment calls)"]
    D --> E{{"mode diff debate<br/>spec + port fidelity"}}
    E -->|PASS| F([merge])
    E -->|FIX| D
    E -->|ESCALATE| U
```

- **Mode `plan`** — after brainstorming, before the implementation plan is
  written. The two models debate the approach, port-fidelity claims, and the
  API/behavior risk register until convergence or the round cap, then the
  converged plan is frozen with a full debate record
  (participants, rounds, resolved/struck/escalated points, verification
  status).
- **Mode `diff`** — after implementation, alongside superpowers code review.
  A PostToolUse hook fingerprints the superpowers code-reviewer dispatch and
  injects the diff-mode reminder with the same base/head SHAs, so both
  reviews always look at the same range. Verdicts are PASS / FIX / ESCALATE
  from *each* side.

The debate rules that keep this honest
(`skills/multi-model-verify/references/debate-protocol.md`):

- **Strike rule** — every externally checkable claim carries a citation the
  other side can read (`References/<addon>/<file>:<line>`, API docs, a dated
  probe). Uncited claims are struck, not debated.
- **Equal weight** — disagreements resolve by evidence, never by which model
  said it. Unresolvable points escalate to the user with both positions.
- **Round cap** — 4 exchanges by default; convergence in one round on a
  sound plan is the system working, and manufactured objections are a
  protocol violation, not diligence.
- **Session continuity** — the reviewer keeps debate state across rounds via
  `codex exec … resume <SESSION_ID>`; the full context is sent once.
- **Final adjudication** — the session always has the last step: it
  verifies the reviewer's final round against the repo and emits the
  terminal verdict itself. A reviewer PASS/FIX is input, never the
  decision; genuine deadlocks escalate to the user. The rule attaches to
  the *role*, not the model — it holds whoever fills the session seat.

## What's in the box

| Piece | What it does |
|---|---|
| `skills/multi-model-verify/` | The debate skill: both modes, debate protocol, frozen-plan format, model prompting notes, fallbacks/consent gate |
| `skills/multi-model-verify/references/backup-lane.md` | The cross-vendor backup reviewer lane: consent-gated substitution when codex is down — the gate's "run backup lane" option (backup model pinned in model-prompting-notes.md) |
| `hooks/` | PostToolUse + PostToolUseFailure hook (matcher `Task\|Agent`): fingerprints the superpowers code-reviewer dispatch, injects the mode-`diff` reminder with matching SHAs; inert everywhere else |
| `agents/implementer.md` | Zero-judgment direct-typing executor for frozen-plan tasks (model pinned in the file's frontmatter) |
| `agents/flash-implementer.md` | Zero-judgment Flash lane: haiku wrapper drives Gemini Flash through the Antigravity CLI headlessly; route + authorship evidence checked every run (model literal pinned in the file) |
| `commands/drift-triage.md` | `/parallax:drift-triage` — reads the newest drift report, verifies each finding against the live contract surfaces, repairs on a branch |
| `commands/doctor.md` | `/parallax:doctor` — operational health check: checkout-vs-installed version, hook registration, superpowers fingerprint, codex transport round-trip, drift task + pending entries. Reports, never fixes |
| `commands/intake.md` | `/parallax:intake` — external-reference intake: clone read-only as untrusted subject data, ground every claimed delta on both sides, probe-gate behavior claims, rank dispositions for the user's scope pick, then hand into the multi-model-verify debate |
| `evals/` | Four gate tiers for the skill itself — see [Verify](#verify) |
| `tools/check-drift.ps1` | Weekly drift watch over the three upstreams the contract depends on — see [Drift protection](#drift-protection) |
| `tools/write-attestation.ps1` · `tools/verify-attestation.ps1` | SHA-bound review attestations — see [Attestation lane](#attestation-lane) |
| `.githooks/pre-push` | Non-blocking attestation check on `main` pushes (`git config core.hooksPath .githooks` to enable) |

## Fails loud, never silent

The governing rule
(`skills/multi-model-verify/references/fallbacks.md`): **no transition that reduces
vendor diversity, evidence quality, or conversation continuity happens
without explicit user consent.**

```mermaid
flowchart TD
    X[codex failure] --> R{one same-parameters retry}
    R -->|recovered| OK[debate continues]
    R -->|still failing| G["CONSENT GATE banner:<br/>what failed · what degraded mode<br/>would and would NOT verify"]
    X -. "quota-exhausted:<br/>skip the retry" .-> G
    X -. "missing-rollout resume:<br/>skip the retry" .-> G
    G -->|fix codex| OK
    G -->|run backup lane| BK["cross-vendor backup reviewer<br/>(FULL, lane substitution recorded)"] --> OK
    G -->|run degraded| D["single-vendor, visibly flagged;<br/>DEGRADED plan poisons any diff PASS"]
    G -->|abort or unattended| B2[BLOCKED / DEGRADED-NOT-AUTHORIZED]
```

- One same-parameters retry is the **only** automatic recovery; every other
  transition stops at the consent gate. Unattended runs fail closed.
  (Pre-dispatch failures retry free; a post-dispatch retry is the bounded
  re-spend — never a loop.)
- Session/weekly usage limits get a dedicated `quota-exhausted` class: no
  retry (quota windows don't clear in seconds), and the banner quotes
  codex's reset time verbatim. A resume failing with the missing-rollout
  signature ("no rollout found ... code -32600", probed 2026-07-24) also
  skips the retry — the rollout is gone; straight to the session-loss
  consent gate.
- **Effective-route check (0.6.0; `sandbox:` line added in 0.8.0)**: every
  codex call's startup header
  (`model:` / `provider:` / `reasoning effort:` / `sandbox: read-only`,
  plus the `session id:` on
  resume) is verified against the canonical declarations — a config.toml
  override or profile silently swapping the reviewer is a named
  `route-mismatch` class: no retry, reply discarded, consent gate.
  (Sandbox mode has no continuity across resumes — an omitted flag falls
  back to the config default, probed 2026-07-24.) The
  call itself runs with reroute-capable env vars stripped
  (`CODEX_API_KEY`, `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `CODEX_HOME`) after a
  `codex login status` preflight that requires the first-party ChatGPT
  state, not merely exit 0.
- A DEGRADED-frozen plan cannot produce an ordinary diff PASS: mode `diff`
  must first retrospectively cross-verify the plan's claims, and if
  cross-vendor is *still* unavailable the only terminal state is
  `ESCALATE — CROSS-VENDOR GATE UNSATISFIED`.
- Missing reference material for a port is a **hard stop** (ask the user),
  never a degraded mode — a debate about remembered code is two models
  fabricating at each other.

## Swapping lanes

Every role is a plug — the contracts attach to roles, not models. Today's
lineup (session / cross-vendor reviewer / cheap implementer) is one
configuration:

- **Implementer, Claude tier** — edit one line: `model:` in
  `agents/implementer.md` frontmatter (any Claude tier is a drop-in). The contract (zero judgment calls, INPUT GAP rule, structured
  report) stays identical whoever fills it.
- **Implementer, cross-vendor** (the fable-advisor v3 Grok pattern) —
  agent frontmatter only accepts Claude tiers, so a vendor swap uses the
  supervisor pattern `agents/flash-implementer.md` implements (documented in `agents/implementer.md`'s Lane note): a cheap Claude
  model supervises, delegates the body of work to the vendor CLI, and
  re-runs verification itself.
- **Cross-vendor reviewer** — a ONE-LINE swap: the canonical model id and
  reasoning effort live solely in
  `skills/multi-model-verify/references/model-prompting-notes.md`. The
  behavioral runner and the drift watch parse those declarations at
  runtime (failing loud if they vanish), and every instruction surface
  (SKILL.md transport commands, doctor, drift-triage) reads them from
  there; a consistency test forbids a hardcoded `-m` literal anywhere
  else.
- **Session** — whatever model runs the session; the debate rules and
  final adjudication follow the seat automatically.

## Requirements

- Claude Code on a current frontier model; superpowers plugin enabled
- OpenAI codex CLI 0.144+ authenticated via ChatGPT sign-in, on a plan with
  access to the canonical reviewer model (id, effort, and tier notes:
  `skills/multi-model-verify/references/model-prompting-notes.md`)
- `pwsh` (PowerShell 7) for the hook; Windows PowerShell 5.1 for the drift
  watch scheduled task; Python 3.10+ for the evals

## Install

Stable (any machine with git auth for this private repo):

```
claude plugin marketplace add Bmwascher/parallax
claude plugin install parallax@parallax
```

Dev loop — Claude Code copies installs into a **versioned cache**, so
checkout edits are NOT live until re-synced:

```
claude plugin marketplace add <path-to-this-checkout>
claude plugin install parallax@parallax
# after edits: bump .claude-plugin/plugin.json version, then
claude plugin update parallax@parallax   # qualified name required
# restart the Claude Code session to re-register hooks/skills
```

Forgetting a step here is the failure mode that looks like a plugin bug: a
stale cache runs yesterday's skill, a missed restart leaves the hook
unregistered. `/parallax:doctor` reports both, plus the fingerprint, the
codex transport, quota headroom (best-effort, experimental), and any
unresolved drift — in one table.

## Verify

| Tier | Gate | Command | Runs |
|---|---|---|---|
| 1 — structure | Spec lint + security scan | `python evals/tools/skill_lint.py skills/multi-model-verify --strict` · `python evals/tools/skill_scanner.py skills` | CI + local |
| 2 — routing | Trigger/routing evals | `python evals/tools/run_trigger_evals.py` | CI + local |
| 2.5 — contract | Structural pytest suite (hook e2e under pwsh, pinned superpowers template fixture, transport/fallback/status-field pins) | `python -m pytest evals -q` | CI + local |
| 3 — behavior | Real headless `claude -p` executor runs each case in a throwaway workspace (synthetic `References/DemoWidget` fixture; codex stripped from PATH for degraded cases), graded expectation-by-expectation by the cross-vendor reviewer — the executor's vendor never grades itself | `python evals/tools/run_behavioral_evals.py` | local only |

Tier 3 tests the **installed** plugin, not the checkout — run the dev-loop
re-sync first. Lint/scan/trigger/pytest run in CI on every push.

Both modes are executed, not just described: the diff-mode case builds a real
two-commit git history in the workspace (frozen plan → implementation with a
planted throttle deviation from the reference) and hands the run the actual
base/head SHAs, so a pass means the debate found the drift in a real diff.

The drift script has its own offline state machine —
`evals/tools/drift_statemachine_tests.ps1` drives the **real**
`tools/check-drift.ps1` through thirteen scenarios against stub CLIs and a
throwaway clone: probe-failure carry-forward, the verdict trust matrix
(`BLOCKED`, no verdict, trusted `NO-ACTION`), both halves of the toast
matrix (CRITICAL dismissal toasts VERIFY, WARN-only dismissal toasts
nothing), the pytest gate (a stub fix that *breaks the suite* must never
commit), commit failure, off-grammar cross-review, an effective-route
mismatch and a failed auth preflight (both read UNAVAILABLE, never a
verdict), pending lifecycle, and the hung-agent kill. Slow and opt-in —
run it whenever `check-drift.ps1` changes:

```powershell
.\evals\tools\drift_statemachine_tests.ps1
# or through pytest:
$env:PARALLAX_STATEMACHINE = "1"; python -m pytest evals -q
```

## Drift protection

parallax's contract points at three moving targets it does not control.
`tools/check-drift.ps1` watches all three; a clean run raises no toast
(the report is still archived under `tools/drift-reports/` — gitignored,
machine-local).

| Upstream | Risk | Check |
|---|---|---|
| superpowers | Template rewrite rots the hook fingerprint (`Senior Code Reviewer` / `Git Range to Review`) or the `Base:`/`Head:` extraction | Every run: hash the installed template against the pinned fixture; CRITICAL if the fingerprints are gone |
| Claude Code | Surface changes — the Task→Agent tool rename (v2.1.63) silently killed the hook matcher once already | On version change: fetch the changelog slice between versions and grep for hook/plugin/matcher/skill/tool-rename keywords |
| codex CLI | `exec` transport flags the skill's commands depend on | Every run: probe `--sandbox`, `--output-last-message`, model/config flags, and the `exec resume` subcommand |

```
powershell tools/check-drift.ps1            # one-shot
powershell tools/check-drift.ps1 -Register  # weekly scheduled task (Tue 13:17)
powershell tools/check-drift.ps1 -TestNotify  # toast wiring check
```

An unfetchable or not-yet-published changelog never advances the version
snapshot — the watch retries next run rather than skipping past a version it
could not inspect.

Findings don't wait for a human: on a findings-week the script feeds the
report and the triage guide into a **headless Claude Code run**. Because
the report embeds raw upstream text (changelog lines), that agent is
treated as untrusted: it works in a **disposable git worktree** the script
creates, and its isolation is two-layer — `--tools` makes shell, network,
and subagent tools **unavailable** (so ambient settings can't resurrect
them; even `python -c` would be arbitrary execution), while `--allowedTools`
scopes write **approvals** to the worktree — and it is killed after 30
minutes. The script then inspects the diff itself, re-runs the pytest
gate, and only commits (on a `drift/<runid>` branch, never merged) when
the gate is green and the commit verifiably landed. The toast reflects the verified outcome,
so the only interruptions are actionable ones:

A `FIXES-APPLIED` diff also gets a **script-side cross-vendor review**
(read-only, bounded) before the toast — preceded by the auth preflight,
run with the env denylist, and accepted only when the codex header echoes
the canonical route and the strict `REVIEW:` line closes the reply; the
reviewer stays in the loop even unattended, and a failed review reads
"cross-review UNAVAILABLE", never implied-reviewed. The final reviewer is the session, deferred to pickup:
the merge happens in a session that adjudicates the cross-review verdict
and the diff first (debate-protocol.md, Final adjudication), with the
user's approval — nothing merges on the external reviewer's word alone.

| Outcome | Toast |
|---|---|
| `FIXES-APPLIED` + non-empty diff + gates green | "fix ready on `drift/<runid>` (gates green; cross-review: …) — review and merge" |
| `NO-ACTION`, WARN-only noise, no diff | none (verdict archived in the report) |
| `NO-ACTION` but a CRITICAL finding | "verify dismissal by hand" — a CRITICAL is never silently dismissed |
| Gate failed, verdict/diff mismatch, timeout, `BLOCKED` | falls back to the manual toast: run `/parallax:drift-triage` yourself |

`-NoAutoTriage` disables the headless run (detection + manual toast only).
`/parallax:drift-triage` remains available interactively — same guide the
headless run follows.

Unresolved weeks can't fall out of the lifecycle: any run that ends in the
manual toast or an open fix branch writes `tools/drift-pending.json`, and
every later run re-toasts it until the branch is merged/discarded
(auto-clears) or `/parallax:drift-triage` records a disposition —
findings never depend on one noticed toast.

## Attestation lane

A mode-`diff` terminal verdict is also recorded mechanically (0.6.0):
after the session's final adjudication — never from the reviewer's reply
alone — `tools/write-attestation.ps1` writes a SHA-bound JSON record
(repo, base/head SHAs, verdict, rounds, participants, route note) under
the reviewed repo's `.git/parallax/attestations/`. The git dir, not the
working tree: recording the verdict cannot move HEAD out from under its
own SHA, and the record never ships in a commit.

`tools/verify-attestation.ps1` is the consumer: a `main` push is attested
when the pushed sha carries a gate-satisfying record (fast-forward), or
when a merge commit's parent2 carries one **against parent1 as its base**
— extra commits, a rebase, or a squash after the review all break the
match and correctly force re-review. Gate-satisfying means verdict PASS
**and** `verification_status: FULL` **and** the confirmed route note — a
DEGRADED or unconfirmed-route PASS is rejected mechanically, not just in
skill prose. The pre-push hooks (this repo's `.githooks/pre-push`;
adapters in consuming repos) call it and **warn, never block** in v1 —
the warning stream is how the lane earns a blocking future.

Enforcement is deliberately **local pre-push lanes only** (re-adjudicated
2026-07-19 after the reviewer flagged the gap): the records live under
`.git` and never ship, so a GitHub-CI check would need an attestation
carrier (git note, PR metadata, or an uploaded artifact) — deferred until
a PR-based merge flow exists; today both repos merge locally, so pre-push
IS the integration boundary.

## Application checkpoint

The debate has a hard contract; without one, the **application phase**
reverts to act-immediately bias — a verdict lands and the session starts
editing with no record between "review concluded" and "diffs happening"
(0.7.0, from a live failure observed in a distilled-skill setting). The
checkpoint (`skills/multi-model-verify/references/application-checkpoint.md`)
makes the missing transitions explicit —
`reviewed → dispositioned → authorized → applied → reverified` — and is
what authorizes touching files, not the verdict.

Before the first fix edit the session writes a checkpoint artifact under
the reviewed repo's `.git/parallax/application-checkpoints/`: the reviewed
range and outcome, a disposition per finding, one row per exact file with
its intended **postcondition** (outcomes, never pseudocode), the
verification plan, and an authorization line that either stops for the
user or **quotes the pre-authorizing instruction verbatim**. Scope growth
invalidates the authorization until the checkpoint is amended. At
attestation time `-CheckpointFile` binds the artifact's hash plus the
emitter-computed changed-path set into the record, and the verifier
rejects a record whose path set no longer matches its range. The
behavioral suite grades the contract end-to-end: a mutation-enabled eval
lane (Edit/Write, deliberately no shell) checks the checkpoint precedes
the first edit, refuted findings get no file plan, and the applied edits
match the stated postconditions.

## Pattern lineage

Advisor/evals ideas from
[awesome-llm-apps agent_skills](https://github.com/Shubhamsaboo/awesome-llm-apps);
plugin + self-marketplace shape from
[fable-advisor](https://github.com/DannyMac180/fable-advisor); vendored eval
tooling attribution in `evals/tools/LICENSE-THIRD-PARTY.md`. MIT licensed.
