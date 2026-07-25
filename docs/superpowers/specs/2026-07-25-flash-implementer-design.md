# Flash implementer lane (Antigravity CLI) — design

**Date:** 2026-07-25 · **Cycle:** 0.12.0 · **Status:** approved (Brandon, 2026-07-25);
advisory-review amendments folded same day (see Review provenance)

## Problem

The per-task SDD implementer lane is pinned to Sonnet (`agents/implementer.md`,
`model: sonnet`). The user's roadmap (backlog item 4, order fixed 2026-07-25)
replaces that build-task lane with Gemini Flash — "it does nothing but EXACTLY
what you tell it to," a fit for a zero-judgment executor. Agent frontmatter
only accepts Claude models, so Flash arrives by delegation: a cheap Claude
tier holds the agent seat and drives a vendor CLI headlessly — the
fable-advisor v3 `grok-implementer` pattern already documented in
`implementer.md`'s Lane note.

## Transport decision: Antigravity CLI, not gemini-cli (user, 2026-07-25)

The obvious transport died during probing:

- gemini-cli 0.52.0 OAuth for individuals is server-side dead ("This client
  is no longer supported for Gemini Code Assist for individuals... migrate to
  the Antigravity suite"); six open issues confirm (primary #28229, P1).
  Google's transition post: free/consumer serving ended 2026-06-18; only
  paid/enterprise API keys remain supported.
- Worse: with a still-working consumer API key, gemini-cli **silently served
  gemini-3.5-flash when pinned to gemini-3.6-flash** (stats block evidence),
  while a garbage model ID errored loudly — a silent model substitution, the
  exact route-integrity failure the codex lane's effective-route check exists
  to reject.
- Antigravity CLI (`agy`) is the official successor (Google Developers Blog,
  "Transitioning Gemini CLI to Antigravity CLI"), installed and probed
  end-to-end the same night. gemini-cli plays no part in this design.

## Probe record (agy 1.1.7, Windows, 2026-07-25)

All probes ran headless in a scratch directory; log evidence retained in the
session scratchpad (`agy-probe/probe*.log`).

- Auth: Google Sign-In (system keyring), one-time interactive. `agy models`
  requires sign-in and lists `gemini-3.6-flash-{high,medium,low}` (plus 3.5
  variants, `gemini-3.1-pro-*`, `claude-sonnet-4-6`, `claude-opus-4-6-thinking`,
  `gpt-oss-120b-medium` — the CLI is multi-vendor).
- Pinned headless run: `agy -p "..." --model gemini-3.6-flash-low --log-file F`
  → correct reply, exit 0; log carries route-request evidence:
  `Print mode: starting (... model="gemini-3.6-flash-low" ...)` and
  `Propagating selected model override to backend: label="Gemini 3.6 Flash (Low)"`.
  Both lines are CLIENT-side (what the CLI requested and propagated), not
  server-side attribution of what was served.
- Unknown model: rejected loudly at the CLI layer before any API call
  ("invalid model selection ... not recognized"), available models listed.
- Write path: print mode cannot prompt, so unapproved tools soft-deny loudly
  ("jetski: ... auto-denied", tool confirmation "Edit"/CodeAction).
  `--mode accept-edits` does NOT apply in print mode. Without `--add-dir`,
  writes divert to the CLI's internal scratch workspace
  (`~/.gemini/antigravity-cli/scratch/`) — files never reach the real tree.
- Working combination (WRITE4-OK): one-time interactive trust of the target
  directory (persists to `trustedWorkspaces` in
  `~/.gemini/antigravity-cli/settings.json`; the interactive session also set
  `allowNonWorkspaceAccess: true`) + headless `--add-dir <dir>` binding →
  file created in the bound tree, no prompting.
- File-action evidence does NOT live in the `--log-file` log (probed
  2026-07-25, Sol primary check-off F1: the WRITE4 run's log contains zero
  mentions of the file it wrote). It lives in agy's internal brain
  transcript: parse `conversationID="<uuid>"` from the log's
  `Print mode: starting` line, then read
  `~/.gemini/antigravity-cli/brain/<conversationID>/.system_generated/logs/transcript_full.jsonl`
  (the WRITE4 file appears there in successful file-changing actions).
- `agy --help` (v1.1.7) lists `--dangerously-skip-permissions` ("Auto-approve
  all tool permission requests without prompting"). Whether it takes effect
  in print mode is UNPROBED (accept-edits provably does not).
- Environment note: an "Orca" app has pre-planted hooks in BOTH
  `~/.gemini/settings.json` (gemini-cli hook events) and agy's stop hooks
  (`jsonhook__orca-status_Stop_0_0` failed non-fatally in probe logs). Inert
  outside Orca sessions; watch in drift triage if it starts failing loudly.

## Review provenance

Same-vendor advisory review (Opus 5, dispatched 2026-07-25, two rounds):
initial verdict FIX with 8 blocking findings; after one factual correction
(the skip-permissions flag IS an agy flag, per `agy --help`) and the
amendments now folded into this text, revised verdict PASS conditional on
the amendments living in the spec, which this revision satisfies. This pass
is NOT cross-vendor verification and forms no part of the Sol gate: the
plan debate (before implementation) and diff debate (before merge) remain
required and are quota-gated to the ~Jul 29 codex reset.

Amended again 2026-07-25 after the PRIMARY reviewer's check-off (GPT-5.6
Sol, codex window reset early; round 1 FIX, five blocking findings, all
session-verified and accepted): F1 corroboration evidence source corrected
to the brain transcript (the log carries no file actions — probed); F2
brief-file lifecycle + clean-baseline preflight; F4 settings check made
conservative (ban the write_file rule class, no path matching); F5 red
probe split into raw-CLI and reachable-failure probes; F3 (debate-record
schema) lands in the plan's Debate record, not this spec. Full round
record in the plan's debate appendix.

## Decisions (user, 2026-07-25)

- Architecture **A**: new `agents/flash-implementer.md`; `implementer.md`
  kept as the direct-typing lane. Chosen over rewriting `implementer.md`
  wholesale (B) after weighing the fable-advisor reference (which added its
  vendor wrapper BESIDE the Claude lane), the untouched haiku transcription
  lane, and the instant sonnet fallback against B's single-file tidiness.
  C (controller shells the CLI directly) rejected: no isolation, no report
  anchor. Known cost, accepted with mitigation: the two agent files share
  contract sections that can drift; agent files cannot include each other,
  so a byte-identity parity test is the only available enforcement and is
  REQUIRED, not optional.
- True-Flash-only, fails loudly: the wrapper never types repo code itself
  and never completes work Flash failed. Enforced mechanically where
  possible (tools allowlist, log/tree corroboration — see §1, §2), by
  contract text where not.
- Consent-gated reroute: a blocked task surfaces to the session AND the user;
  rerouting to a Claude tier is an explicit user decision recorded in the
  frozen plan's **Escalated points (user-decided)** section — the existing
  artifact, not a new table. No automatic degradation — same ethos as the
  debate lane's transport consent gate.
- Scope: the Flash lane runs in the MAIN CHECKOUT ONLY this cycle. Trust is
  per-directory and grantable only interactively, so fresh worktrees are
  untrusted by construction; a worktree trust story is future-cycle work.
  Coupling made explicit: with no disposable worktree, the
  FILES-CHANGED-on-blocked rule (§4) is the recovery affordance for a
  partially written tree.
- Effort: ONE canonical variant this cycle, `gemini-3.6-flash-medium`. No
  per-task effort choice by any seat, no effort slot in the plan format —
  a zero-judgment lane gets zero dispatch-time judgment calls.
- **Sol check-off required before this branch closes**: plan debate before
  implementation, diff debate before merge, both after the ~Jul 29 reset;
  spec and plan drafting proceed now.

## Design

### 1. Agent: `agents/flash-implementer.md`

`model: haiku` frontmatter (wrapper/supervisor) plus an explicit `tools:`
allowlist — Read, Grep, Glob, Bash; **no Edit, no Write, no NotebookEdit** —
so the ergonomic path for the wrapper to type code itself does not exist.
(Bash remains a write primitive in principle; the log/tree corroboration in
§2 is the control that catches that path.) If the long-brief probe (§2)
forces brief-via-file, the brief is written with a Bash heredoc — Write
stays out of the allowlist.

Same input contract as `implementer.md` (ONE task's verbatim text + the
plan's Global Constraints), same INPUT GAP rule. Report format gains one
lane-specific line:

- **STATUS:** done | blocked | INPUT GAP: <what is missing>
- **ROUTE:** resolved model ID as requested-and-propagated, from the log,
  plus the retained log file's path
- **FILES CHANGED:** actual paths from `git status` — on `blocked` this
  MUST still list every path Flash already touched, so the session can
  revert a partial write
- **VERIFICATION:** each command run by the wrapper itself, with real output
- **DEVIATIONS:** must be "none" or an explanation of why the task could
  not be built as written

The parity test (§6) pins the shared sections (INPUT GAP rule, report
headings other than ROUTE) byte-identical across both agent files; ROUTE is
declared lane-specific and excluded from parity.

### 2. Dispatch recipe

- Preflight, all blocking, before any dispatch:
  1. `agy models` output contains `gemini-3.6-flash-medium` (also proves
     sign-in and binary presence);
  2. `~/.gemini/antigravity-cli/settings.json` `trustedWorkspaces` contains
     the workdir — if not, block with the exact re-trust instruction (one
     interactive `agy` session in the workdir);
  3. the same settings file carries NO file-writing per-tool allow rule
     AT ALL (any `write_file(` entry, whatever path it names) — the
     durable, call-site-invisible bypass class; this settings assertion is
     the LOAD-BEARING permission control (a flag is at least visible
     per-dispatch; a settings rule survives invisibly forever — tonight's
     probing itself left one behind). Conservative by amendment (Sol
     check-off F4): agy's path normalization is not offline-verifiable
     (trust entries and allow rules already disagree on drive-letter
     spelling on this machine), so the lane bans the rule CLASS rather
     than attempting workdir path-matching;
  4. `git status --porcelain` is EMPTY before dispatch (Sol check-off F2:
     without a pre-dispatch baseline, pre-existing changes are
     unattributable — a dirty tree is blocked, not absorbed).
- Dispatch: `agy -p <brief> --model gemini-3.6-flash-medium
  --add-dir <workdir> --log-file <fresh per-task log>`. Fresh log file per
  attempt, written under the session scratchpad (never the repo tree — no
  .gitignore dependency); each task's report carries its log path, and the
  SDD execution record (the `.superpowers/sdd/<date>-<topic>/` workspace
  the subagent-driven-development skill maintains) records per-task lane
  provenance, which the diff-debate brief then carries. Adding an
  implementer line to the frozen-plan debate record's Participants block is
  declared scope for the plan debate to settle.
- Brief-file lifecycle (Sol check-off F2): the brief is the SOLE transient
  file the wrapper may create in the repo tree — a declared exception to
  its never-write rule. Unique reserved name (`AGY-TASK-BRIEF-<unique>.md`,
  unique suffix from the dispatch's log-file basename); collision
  preflight (any existing `AGY-TASK-BRIEF-*` file in the workspace =
  stale state = blocked); deletion guaranteed after agy exits — success,
  failure, or interruption path alike — and always BEFORE any evidence
  check, so the brief never appears in the attribution set.
- Route check, every run, on the log file:
  1. `Print mode: starting` line present with `model="gemini-3.6-flash-medium"`
     (the RESOLVED ID is the comparand — same string §5 pins as canonical);
  2. `Propagating selected model override` line present (presence-only; its
     display label is a second namespace and is NOT matched);
  3. transcript/tree corroboration (evidence source corrected by Sol
     check-off F1 — the `--log-file` log carries NO file actions, probed):
     parse `conversationID="<uuid>"` from the log's `Print mode: starting`
     line, read the brain transcript at
     `~/.gemini/antigravity-cli/brain/<conversationID>/.system_generated/logs/transcript_full.jsonl`,
     and require every path `git status` reports changed to appear in that
     transcript as a successful file-changing action. A changed file the
     transcript never mentions means the wrapper (or something else) typed
     it — blocked regardless of test results. A missing transcript is
     blocked. The ROUTE report line carries the transcript path beside the
     log path.
  This evidence class is CLIENT-side: the check verifies the route was
  **requested and propagated**, never "used and confirmed" (the doctor
  check-4 language discipline, `commands/doctor.md`). Server-side
  substitution is undetectable with today's evidence — named in Risks.
- Probe task (pre-plan, throwaway harness, no agent file needed), pinned
  before the agent body freezes:
  1. long-brief mechanics — argument vs stdin vs file, quoting, size limits;
  2. does agy emit ANY response-side model attribution (log tail, response
     metadata; agy has no `--output-format` flag) — if yes, that artifact
     becomes the route check and the client-side lines demote to
     preconditions; the probe's answer is written into this section as the
     final route-check contract text;
  3. does `--dangerously-skip-permissions` take effect in print mode at all
     (accept-edits provably does not) — if inert, the settings assertion is
     the whole live defense, and §4's flag ban is belt-and-suspenders.

### 3. One-time setup (documented in the agent file)

agy installed + signed in (done 2026-07-25). The repo root is trusted via
one interactive agy session (same mechanism as the probe dir). An
implementation task minimizes tonight's probe leftovers in agy's settings:
remove the probe-dir `write_file` allow rule (required — §2's preflight
asserts its absence for workdirs), and attempt the narrowest working
`allowNonWorkspaceAccess` config with a DECLARED fallback: if narrowing
does not converge quickly, leave the value as-is and document it and why —
the task must not stall, and the setting is shared with the Orca app's
environment. Trust is per-directory; the main-checkout-only scope decision
above is the worktree story for this cycle.

### 4. Failure handling — loud, never silent

`STATUS: blocked` with the exact output quoted, on: any preflight failure
(sign-out, missing model, untrusted workdir, workdir allow rule present),
the print-mode soft-deny line, nonzero exit, route-check failure (missing
route lines, wrong resolved ID, log/tree corroboration mismatch), files
diverted to internal scratch. Forbidden by class in the agent body: the
`--dangerously-skip-permissions` flag by name, any `--mode`/approval bypass,
AND persisting any per-tool allow rule for the workdir in agy settings —
the durable settings-rule form is the load-bearing prohibition. On blocked,
FILES CHANGED lists Flash's partial writes (per §1) as the recovery
affordance. Reroute is consent-gated per Decisions.

### 5. Model literal placement

The canonical implementer-lane literal is the RESOLVED ID
`gemini-3.6-flash-medium`, living in `agents/flash-implementer.md` — the
same string the preflight and route check compare against, so no
requested/resolved ambiguity survives. After this cycle, no implementer
model literal exists outside the two agent files. That claim is made true
by enumerated edits, not assumption:

- `README.md` repo-map row (~line 66): "currently `model: sonnet`" literal
  replaced by a pointer to the agent files; new row for the Flash lane.
- `README.md` role-plug section (~lines 131-134): "`sonnet` today;
  `haiku`/`opus` are drop-ins" reworded to point at the agent files without
  naming tiers.
- `agents/implementer.md` Lane note: gains the pointer to
  `flash-implementer.md`; its "Nothing else in the plugin references the
  implementer's model" sentence is RETIRED (already false today — README:66,
  frozen-plan-format.md:4). Its own frontmatter/Lane-note literals stay:
  agent files are the allowed homes.
- `skills/multi-model-verify/references/frozen-plan-format.md` line 4:
  "Sonnet 5" literal becomes a generic reference to the implementer agents.

Enforced by a new sweep test mirroring
`test_reviewer_id_has_single_source`: scans the reviewer sweep's file set
PLUS `agents/*.md`, with exactly the two agent files as the allowed homes —
so a future third agent file is swept by default, not silently missed.

### 6. Verification for this cycle

- Offline pytest (zero quota, both vendors): contract pins on the new agent
  file — dispatch flags, resolved-ID comparand, route-check strings
  (including the log/tree corroboration rule), forbidden-class phrasing,
  report headings including ROUTE, `model: haiku` frontmatter, and the
  `tools:` allowlist (no Edit/Write/NotebookEdit) — plus the §1 parity test
  and the §5 implementer-literal sweep.
- Pre-plan probes (throwaway harness, no agent file): the §2 probe task.
  These are probes, not implementation — the plan-debate gate is not
  crossed.
- Live verification through the REAL agent happens during implementation,
  AFTER the plan debate: one end-to-end dry-run task in a scratch repo
  (trusted for the occasion), plus TWO failure probes (split by Sol
  check-off F5 — the earlier single disjunctive probe was vacuous: a
  wrapper refusing the contradictory brief would "pass" without ever
  exercising the failure path): (a) a RAW agy probe, no agent, proving
  the CLI's loud invalid-model rejection with no writes; (b) a
  reachable-failure probe through the REAL agent — plant a scratch-scoped
  `write_file` allow rule in agy settings, dispatch a trivial task,
  require preflight check 3 to block quoting the rule, then remove the
  planted rule. Dev-loop ordering applies and is part of the task:
  the agent is not live until `plugin.json` bumps,
  `claude plugin update parallax@parallax` runs, and the session restarts.
- Preflight cost: `agy models` is a network round-trip per task dispatch.
  Deliberate — per-task freshness over quota thrift; the wrapper is fresh
  per task, so there is no cheaper session-scoped cache to use.
- Plan debate + diff debate (Sol): after the ~Jul 29 reset. The branch does
  not merge without the diff debate's terminal PASS.
- Behavioral battery: deliberately not run. Honest framing: this cycle
  edits `references/frozen-plan-format.md`, a skill reference file that NO
  behavioral case declares in its surface (and `agents/*` appears in no
  surface either) — so `--changed` selects nothing by design, and the gap
  itself is declared here for the debate to contest, alongside whether an
  `agents/`-surfaced behavioral case (Flash-fails → wrapper reports
  blocked, never substitutes) is wanted this cycle or deferred.
- State-machine suite: `tools/check-drift.ps1` untouched → skipped
  (CLAUDE.md opt-in rule).

### 7. Scope edges

Version 0.12.0. Doctor gains a minimal agy row — binary version + pinned
model present in `agy models`, no generation probe — and follows doctor's
existing single-source discipline: the row PARSES the canonical ID out of
`agents/flash-implementer.md` under the installed copy's `installPath`,
carrying no literal of its own (the check-4 pattern). Drift-watch: the
drift snapshot gains the `agy --version` string as an informational row
(the snapshot already tracks the codex version — declining drift coverage
for the youngest dependency while naming it the top risk would be
inconsistent); full agy flag-surface drift coverage remains a non-goal this
cycle. Other non-goals: reviewer lane untouched; no CI changes;
transcription tasks stay on `implementer.md`/haiku; agy's Claude/gpt-oss
models unused; gemini-cli unused (uninstall + `GEMINI_API_KEY` removal are
optional user cleanup, not cycle scope).

## Risks

- **Server-side model substitution is undetectable today.** The route check
  proves requested-and-propagated, not served — the same epistemic gap the
  codex lane's header check has, handled with the same language discipline.
  If the §2 probe finds response-side attribution, the gap closes; if not,
  it is a NAMED residual risk. Mitigating context: the diff debate reads
  the code itself regardless of who wrote it — substitution degrades
  provenance, not the correctness gate.
- **agy is young and Google moves fast**: v1.1.7, endpoint literally named
  `daily-cloudcode-pa.googleapis.com`, predecessor killed with a month's
  notice. Mitigations: loud preflight, pinned-contract tests that fail on
  flag drift, the drift-snapshot version row, sonnet one dispatch away
  behind the consent gate, and architecture A keeping the old lane intact.
- **Free-tier quota opacity**: agy AI-credit limits are undocumented. A
  mid-plan exhaustion surfaces as a loud dispatch failure → consent gate;
  the partial-write listing (§1/§4) bounds the recovery cost. No headroom
  probe exists; observability gap, not solved this cycle.
- **Print-mode permission model is under-documented**: today's working
  recipe is probe-verified, not doc-verified. The pinned-contract tests and
  the §2 probe task are the defense; doc drift lands in drift triage.

## Non-goals

- No reviewer-lane or debate-protocol changes; no eval-case changes (the
  possible `agents/`-surfaced case is a declared debate question, not
  committed scope).
- No attempt to use agy's non-Gemini models anywhere.
- No plugin runtime behavior change beyond the new agent (version bumps to
  0.12.0 per release convention).
