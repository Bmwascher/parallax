# Backup reviewer lane: kimi-cli to kimi-code — design

Backlog item 13, taken with items 8 and 16 and item 6's residual question,
all of which resolve inside it. Written 2026-07-31 after a live probe of
kimi-code 0.31.1; every claim below that describes CLI behaviour was measured,
and the measurements are recorded in
`docs/superpowers/plans/rounds/2026-07-31-kimi-code-swap/probe-record.md`.

## The problem, restated after probing

Item 13 assumed a hard port: every route-evidence rule the backup lane has is
pinned to `kimi-cli` internals, so a swap means rebuilding them against the new
tool's surfaces, with the standing risk that a check ends up matching nothing
and reading as clean.

The probe shows something different. The rules are not merely repinnable; most
of them have nothing left to do. Every hard rule in `references/backup-lane.md`
— the byte-offset capture, the rotation guard, session-block attribution, and
`tools/kimi-lane-lock.ps1` — exists to solve ONE problem: `~/.kimi/logs/kimi.log`
is a single user-global append stream shared by every kimi session on the
machine, so attributing three log lines to one round is genuinely hard.

kimi-code writes a per-session log and a per-session structured transcript
inside a directory named after the session. There is no shared stream, so there
is nothing to attribute.

This design therefore deletes more than it adds.

## What resolves

| Item | Disposition |
| --- | --- |
| 13, the swap | Done here. |
| 8, truncated brief | Does not reproduce at 9033 chars. Replaced by a hash check that detects truncation anywhere in the chain. |
| 16, lock shorter than a round | Disappears. The lock is deleted. |
| 6, residual per-session-log question | Answered YES, natively, without needing `KIMI_CODE_HOME`. |

Item 15's kimi-cli removal is NOT done here and is explicitly deferred: the
installer renamed the old binary to `kimi-legacy.exe`, which removes the
shadowing hazard that made removal attractive while keeping the rollback.

## Architecture

Four components, each with one job.

### 1. The round home — `tools/new-kimi-lane-home.ps1` (new)

Builds an isolated `KIMI_CODE_HOME` for one round and prints its path.

Contents, all of them chosen rather than inherited:

- `config.toml`, rendered from a committed template. It declares the provider
  block, the one canonical model with its effort, `[thinking] enabled = true`,
  `extra_skill_dirs = []` and `telemetry = false`. It declares NO hooks.
- `credentials/kimi-code.json`, copied from the user's real home.
- `skills/`, empty, to be passed as `--skills-dir`.

Two independent reasons this is not optional:

- The user's real `~/.kimi-code/config.toml` carries seven Orca-managed
  lifecycle hooks, including `PreToolUse` and `PermissionRequest`, each running
  a shell script. That is a command-executing back-channel sitting on the
  reviewer's approval path — strictly stronger than the old lane's
  `merge_all_available_skills`, which could only add instructions. A hook block
  in the reviewer's config is not something to record and proceed past.
- Effort and thinking have no CLI flags on this tool. Writing the config
  ourselves turns the old lane's weakest evidence class — "effort is
  config-validation only, and a single later read cannot establish what the
  config held during the round" — into effort verifiable by construction, and
  then confirmed per round from the log.

The script FAILS if the real credentials file is absent. An unauthenticated
lane must stop, not degrade.

Relocating the home does not suppress `~/.agents/skills/`, which lives outside
it. `--skills-dir` is the lever for that, and it is a mitigation until probed
(see Open questions).

### 2. The agent — `references/kimi-reviewer-agent.md` (replaces two files)

The new agent format is Markdown with YAML frontmatter, and the body IS the
system prompt. So `kimi-reviewer-agent.yaml` and `kimi-reviewer-system.md`
collapse into one committed file:

```yaml
---
name: parallax-readonly-reviewer
description: ...
tools: [Read, Grep, Glob, ReadMediaFile, TodoList]
disallowedTools: [Bash, Write, Edit, WebSearch, FetchURL, Agent, AgentSwarm,
                  Skill, CronCreate, CronDelete, TaskStop, EnterPlanMode,
                  ExitPlanMode, AskUserQuestion, TaskList, TaskOutput]
subagents: []
---
<the existing reviewer system prompt, unchanged>
```

The five-tool allowlist maps one-to-one from the old lane: `ReadFile`→`Read`,
`SetTodoList`→`TodoList`, and `Grep`, `Glob`, `ReadMediaFile` unchanged.

Three deliberate additions over a straight port:

- `disallowedTools` is a denylist applied AFTER the allowlist. The allowlist
  alone is sufficient on measured behaviour; the denylist is defence in depth
  against a future release adding a tool, or an allowlist that fails to parse.
  Omitting `tools:` entirely means ALL tools, so a silent parse failure is
  permissive — that is the failure direction the denylist covers.
- `subagents: []`. The probe found this defaulted to every subagent including
  `coder`. It was inert only because `Agent` and `AgentSwarm` were denied.
  Relying on that coincidence is exactly the class this repo removes.
- The tool surface is far larger than the old CLI's, so the allowlist carries
  more weight than before, not less.

Containment is unchanged in KIND. The docs state, and the wire record
`{"type":"permission.set_mode","mode":"auto"}` confirms, that `-p` mode skips
approval for regular tool calls. The allowlist remains the load-bearing
control, and the write-probe remains its acceptance test.

### 3. Dispatch and resume

Fresh round, with the working directory set to the review mirror and
`KIMI_CODE_HOME` set to the round home:

```
kimi -m <canonical-backup-model-id> --agent-file <committed agent .md>
     --skills-dir <round-home>/skills -p "<the whole brief>"
```

Resume, from the SAME working directory:

```
kimi -r <session-id> -p "<rebuttal>"
```

Nothing is re-pinned on resume. This inverts the old lane's most dangerous
rule, and the inversion is measured, not assumed:

- A resume from the wrong directory is REFUSED with exit 1 and dispatches
  nothing. The old CLI ran in the caller's directory, and once landed in the
  real tree. The binding is now enforced by the tool.
- A resume from the right directory inherits the agent, model, effort and
  system prompt, with `toolsHash` and `systemPromptHash` byte-identical to
  round 1.
- `--agent-file` CANNOT be combined with `--session`, so re-pinning is not
  merely unnecessary, it is rejected.

The brief is passed INLINE, not planted as a file. This matters for evidence:
if the brief is a file and `-p` is a pointer, the recorded prompt is the
pointer and hashing it proves nothing about the brief. Inline is what makes the
check in the next section meaningful.

### 4. Per-round evidence

Everything is read from this round's own session directory under
`<round-home>/sessions/wd_<workspace>/<session-id>/`.

From `logs/kimi-code.log`, the `llm config` line:

- `modelAlias` equals the canonical backup model id
- `thinkingEffort` equals the canonical effort
- `toolCount` equals 5

From `agents/main/wire.jsonl`:

- `config.update` — `profileName` equals `parallax-readonly-reviewer`, and
  `systemPrompt` equals the committed agent file's body EXACTLY
- `tools.set_active_tools` — `names` equals the allowlist exactly, and
  `disallowedNames` equals the denylist exactly
- `llm.tools_snapshot` — exactly the five allowlisted tool names
- `llm.request` — `provider`, `modelAlias` and `thinkingEffort` as declared
- `turn.prompt` — the received text hashes to the brief's hash, computed
  before dispatch

**Hashes are used for consistency WITHIN a debate, never against a committed
literal.** `toolsHash` and `systemPromptHash` are recorded in round 1 and every
later round must match round 1's. They are deliberately NOT pinned to a value
in the repo: the tools hash covers the tool SCHEMAS, so any CLI upgrade that
rewords a tool description would change it, and a committed literal would then
fail every round for a reason that is not a route problem. The upgrade-proof
assertions are the ones above, which compare against text this repo controls —
the allowlist and the system prompt body both live in the committed agent file.

Any of these missing, unreadable, or unequal is a route-attribution failure:
the reply is DISCARDED unread and the failure goes to the fallbacks.md consent
gate. This is the same disposition as today.

Why this is better in kind rather than merely in detail: the old
`Loaded tools:` grep could find no line and be read as "no extra tools", which
turned the lane's only read-only control into a check that cannot fail — the
exact hazard item 13 named. `toolCount=5` and a hash equality are positive
assertions. If the allowlist failed to apply, the count would be the full tool
set and the hash would differ. Absence is a failure by construction.

The client-side vocabulary discipline is unchanged: report "route line verified
(client-side)". These are client-resolved records; server-side substitution
remains undetectable from this class.

## What gets deleted

- `tools/kimi-lane-lock.ps1` and `evals/multi-model-verify/test_kimi_lane_lock.py`
  (41 tests). The lock serialized this plugin's own dispatches so two debates
  could not interleave in one shared log. With per-round homes there is no
  shared log and no interleaving.
- Contract regions `lane-lock`, `session-block-attribution`,
  `session-block-kind`, `session-block-residual`, `rotation-guard-detection`,
  `rotation-guard-disposition`, `rotation-guard-identity`, with
  `DECLARED_REGIONS` in `test_contract_coverage.py` updated so the removals are
  visible rather than silent.
- `references/kimi-reviewer-agent.yaml` and `references/kimi-reviewer-system.md`,
  superseded by the single agent Markdown file.
- The `PYTHONIOENCODING` / `PYTHONUTF8` environment guard. It exists because
  kimi-cli is Python and a cp1252 console raised `UnicodeEncodeError` AFTER the
  model had answered. kimi-code is a Node binary. Removal is gated on the
  encoding probe below; until that passes the guard stays.

Deleting a control needs the same care as adding one. Each removal above is
justified by a measured property of the new tool, and each is paired with a
test that fails if the property stops holding.

## What else changes

- **Preflight 3 grows a `.kimi-code/` sweep.** The reviewed tree can advertise
  agents from `.kimi-code/agents/` and `.agents/agents/`, and skills from
  `.kimi-code/skills/` and `.agents/skills/`. `.agents/*` is already swept;
  `.kimi-code/` is not. This touches SKILL.md's preflight text and
  `tools/new-review-mirror.ps1`.
- **Drift watching** moves from `kimi 1.49.0` to kimi-code 0.31.1 in
  `tools/drift-snapshot.json` and `tools/check-drift.ps1`. `kimi upgrade`
  self-updates, so the lane needs a version floor, not only a recorded string —
  the same treatment the Fable panel seat has.
- **`/parallax:doctor`** backup-lane section is rewritten against the new
  transport and the new evidence surfaces.
- **`references/model-prompting-notes.md`** keeps its canonical model id
  `kimi-code/k3-256k` unchanged — it exists on the new CLI with
  `support_efforts = ["low","high","max"]`. The canonical thinking flag
  declaration changes from `--thinking` to the config form.
- **`evals/multi-model-verify/test_backup_lane.py`** is rewritten. Per the
  repo's rule for live-verified contracts, the tests change FIRST.

## Error handling

The invariant is unchanged and governs every new check: an unmade, failed, or
unreadable measurement is never a clean one.

- Round home cannot be built, or credentials absent: the lane is UNAVAILABLE.
  Never dispatch.
- Session directory absent after a call, or any required record missing:
  route-attribution failure. Discard unread.
- Brief hash mismatch: transport failure, not a review result. Discard unread.
- Write-probe fails any of its three legs: lane BROKEN, integrity failure
  class. Never dispatch a review over it.
- Wrong-directory resume: the CLI refuses and exits 1. Treat as a driver
  error, correct the directory, re-run. No reply exists to quarantine.

All failure classes and consent-gate dispositions continue to live in
`fallbacks.md`. This design adds no new namespace.

## Testing

- `test_backup_lane.py` rewritten against the new transport, agent format and
  evidence records, with a fixture wire.jsonl and log captured from the probe.
- Every deletion above gets a test asserting the replacement property, so the
  removals cannot silently become gaps.
- `test_contract_coverage.py` `DECLARED_REGIONS` updated; the checker itself
  proves the new regions are pinned and the old ones are gone.
- The behavioral suite is local-only and opt-in, and this cycle changes skill
  and prompt text, so `run_behavioral_evals.py` must run by hand.
- `drift_statemachine_tests.ps1` runs if `check-drift.ps1` changes, which it
  will.

## Open questions, each a plan task with its own probe

None of these blocks the design; each blocks a specific claim from being made.

1. **Does `--skills-dir` actually suppress a planted project skill?** Needs the
   same canary probe codex got. Until measured it is a mitigation, not a
   control, and the record must say so.
2. **Does `subagents: []` empty the list?** Verify in `state.json`.
3. **Does the round config's effort pin override the model default?** Both read
   `high` today, so agreement proves nothing. Test with `low`.
4. **Are `.kimi-code/agents/` and `.kimi-code/skills/` inside a REVIEWED tree
   picked up?** Decides how much of preflight 3 changes.
5. **Does the per-session log rotate?** The global log has rotated `.1` files;
   per-session behaviour is unprobed.
6. **Does the Node CLI have any encoding hazard on a cp1252 console?** Gates
   deleting the UTF-8 guard.
7. **Is `--output-format stream-json` a cleaner reply capture than parsing
   stdout?** Optional; only adopt if it simplifies.

## Sequencing constraint

The install is the risky step and it is already done, deliberately, with
`~/.kimi` backed up and hash-manifested and the old binary preserved as
`kimi-legacy`. Do not run a debate round across another install or upgrade.
Take the drift snapshot update as part of this cycle's diff, not before it.
