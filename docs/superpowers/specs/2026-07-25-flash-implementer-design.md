# Flash implementer lane (Antigravity CLI) — design

**Date:** 2026-07-25 · **Cycle:** 0.12.0 · **Status:** approved (Brandon, 2026-07-25)

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
  → correct reply, exit 0; log carries route evidence:
  `Print mode: starting (... model="gemini-3.6-flash-low" ...)` and
  `Propagating selected model override to backend: label="Gemini 3.6 Flash (Low)"`.
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
- Environment note: an "Orca" app has pre-planted hooks in BOTH
  `~/.gemini/settings.json` (gemini-cli hook events) and agy's stop hooks
  (`jsonhook__orca-status_Stop_0_0` failed non-fatally in probe logs). Inert
  outside Orca sessions; watch in drift triage if it starts failing loudly.

## Decisions (user, 2026-07-25)

- Architecture **A**: new `agents/flash-implementer.md`; `implementer.md`
  untouched except a Lane-note pointer. Chosen over rewriting
  `implementer.md` wholesale (B) after weighing the fable-advisor reference
  (which added its vendor wrapper BESIDE the Claude lane), the untouched
  haiku transcription lane, and the instant sonnet fallback against B's
  single-file tidiness. C (controller shells the CLI directly) rejected:
  no isolation, no report anchor.
- True-Flash-only, fails loudly: the wrapper never types repo code itself
  and never completes work Flash failed.
- Consent-gated reroute: a blocked task surfaces to the session AND the user;
  rerouting to a Claude tier is an explicit user decision recorded in the
  plan's deviation table. No automatic degradation — same ethos as the
  debate lane's transport consent gate.
- **Sol check-off required before this branch closes**: plan debate before
  implementation, diff debate before merge. Codex weekly window is 100% used
  (rate_limit_reached, resets ~Jul 29) — both debates wait for the reset;
  spec and plan drafting proceed now.

## Design

### 1. Agent: `agents/flash-implementer.md`

`model: haiku` frontmatter (wrapper/supervisor). Same input contract as
`implementer.md` (ONE task's verbatim text + the plan's Global Constraints),
same report format (STATUS / FILES CHANGED / VERIFICATION / DEVIATIONS),
same INPUT GAP rule. The wrapper's own duties: brief handoff, dispatch,
route verification, tree verification, running the task's verification
commands itself, and honest reporting. It never edits repo files and never
substitutes its own implementation.

### 2. Dispatch recipe

- Preflight: `agy models` output must contain the pinned model ID; anything
  else (sign-out, missing binary, missing model) is `STATUS: blocked`.
- Dispatch: `agy -p <brief> --model gemini-3.6-flash-<effort>
  --add-dir <workdir> --log-file <fresh per-task log>`. Effort is the
  controller's dispatch-time choice: `medium` default, `low`/`high` when the
  task brief says so. Fresh log file per attempt; logs retained as task
  artifacts.
- Route check (every run): log must contain `Print mode: starting` with the
  pinned model ID AND the `Propagating selected model override` line; the
  task's changed files must exist in the real tree (`git status` /
  expected paths) — guards the internal-scratch diversion.
- Long-brief mechanics (argument vs stdin, quoting, size limits) are pinned
  by a probe task in the implementation plan before the agent body freezes.

### 3. One-time setup (documented in the agent file)

agy installed + signed in (done 2026-07-25). The repo root is trusted via
one interactive agy session (same mechanism as the probe dir). An
implementation task minimizes the settings left by tonight's probing:
remove the probe-dir `write_file` allow rule, and find the narrowest working
config for `allowNonWorkspaceAccess`. Trust is per-directory — a future
worktree-based cycle must re-trust its worktree path.

### 4. Failure handling — loud, never silent

`STATUS: blocked` with the exact output quoted, on: preflight failure, the
print-mode soft-deny line, nonzero exit, route mismatch or absent route
evidence, files diverted to internal scratch. `--dangerously-skip-permissions`
is forbidden by name in the agent body. Reroute is consent-gated per the
Decisions section.

### 5. Model literal placement

`gemini-3.6-flash` lives canonically in `agents/flash-implementer.md`.
README updates: repo-map row for the new agent + the role-plug section's
implementer entries. `references/frozen-plan-format.md`'s "Sonnet 5" literal
becomes a generic pointer to the implementer agents — after this cycle, no
implementer model literal exists outside the two agent files.

### 6. Verification for this cycle

- Offline pytest (zero quota, both vendors): contract pins on the new agent
  file — dispatch flags, route-check strings, forbidden-flag phrasing,
  report headings, `model: haiku` frontmatter — plus a parity test pinning
  the shared contract sections (INPUT GAP rule, report format) byte-identical
  across both agent files.
- Live agy verification (zero codex quota, runs before Jul 29): one
  end-to-end dry-run task through the real agent in a scratch repo, and a
  red probe (bad model ID must produce blocked, not output).
- Plan debate + diff debate (Sol): after the ~Jul 29 reset. The branch does
  not merge without the diff debate's terminal PASS.
- Behavioral battery: SKILL.md is untouched, so `--changed` selects nothing —
  the deliberate no-battery run, declared here for the debate to contest.
- State-machine suite: `tools/check-drift.ps1` untouched → skipped
  (CLAUDE.md opt-in rule).

### 7. Scope edges

Version 0.12.0. Doctor gains a minimal agy row (binary version + pinned
model present in `agy models`; no generation probe) — declared scope for the
debate to contest. Non-goals: reviewer lane untouched; no drift-watch agy
coverage this cycle; no CI changes; transcription tasks stay on
`implementer.md`/haiku; gemini-cli unused (uninstall + `GEMINI_API_KEY`
removal are optional user cleanup, not cycle scope).

## Risks

- **agy is young and Google moves fast**: v1.1.7, endpoint literally named
  `daily-cloudcode-pa.googleapis.com`, and its predecessor was killed with a
  month's notice. Mitigations: loud preflight, pinned-contract tests that
  fail on flag drift, sonnet one dispatch away behind the consent gate, and
  architecture A keeping the old lane intact.
- **Free-tier quota opacity**: agy AI-credit limits are undocumented for the
  free tier. A quota exhaustion mid-cycle surfaces as a loud dispatch
  failure → consent gate. No headroom probe exists yet; noted as an
  observability gap, not solved this cycle.
- **Print-mode permission model is under-documented**: today's working
  recipe is probe-verified, not doc-verified. The pinned-contract tests and
  the plan's probe task are the defense; doc drift lands in drift triage.

## Non-goals

- No reviewer-lane or debate-protocol changes; no eval-case changes.
- No attempt to use agy's Claude/gpt-oss models anywhere.
- No plugin runtime behavior change beyond the new agent (version bumps to
  0.12.0 per release convention).
