# kimi-code swap — probe record (backlog item 13)

Probed 2026-07-31 on Windows, kimi-code 0.31.1, against `kimi-cli` 1.49.0 as
the incumbent. Repo at `6201e30`, clean, no branch cut yet. This file is
UNTRACKED scratch evidence, written into the tree deliberately so it survives
the session (the 0.17.x cycles lost round artifacts to the scratchpad).

Everything below was measured by running it. Three model calls were spent, all
in an isolated home against a throwaway git workspace, none in the real tree.

## Summary — the lane gets simpler, not harder

The new CLI writes a PER-SESSION structured log and a per-session wire
transcript. That removes the single fact every hard rule in
`references/backup-lane.md` was built around: that `~/.kimi/logs/kimi.log` is
one user-global append stream. With it go the byte-offset rule, the rotation
guard, session-block attribution and `tools/kimi-lane-lock.ps1`.

Backlog item 16 does not need fixing. It disappears.
Backlog item 8 does not reproduce, and becomes a measurable check.
Backlog item 6's residual question is answered YES.

## State before, and rollback

- `kimi-cli` 1.49.0, pip, at `...\Python312\Scripts\kimi.exe`.
- `tools/drift-snapshot.json` records `"kimi": "1.49.0"`, updated 2026-07-28.
- `~/.kimi` backed up to `C:\Users\Brandon\.kimi.backup-20260731`, 402 files,
  42.95 MB, count-identical at copy time. A SHA-256 manifest of all 404 files
  (two added by a concurrent round) is at
  `scratchpad/kimicode-probe/kimi-home-before-migrate.sha256`.
- `~/.kimi-code/config.toml` as it existed before login is saved at
  `scratchpad/kimicode-probe/kimi-code-config.orca-original.toml`.
- Rollback: `pip install kimi-cli==1.49.0` restores the package. `~/.kimi` was
  never written by this work.

## The install

Official Windows installer, downloaded and READ IN FULL before running
(`scratchpad/kimicode-probe/install.ps1`, 15891 bytes) rather than piping the
network into `iex`.

- Installed **0.31.1** — the npm registry agrees; the backlog's 0.30.0 is one
  release behind.
- Manifest-driven download with an enforced SHA-256 checksum. Verified.
- Landed at `C:\Users\Brandon\.kimi-code\bin\kimi.exe`, 133023744 bytes, a
  single self-contained binary with no Node dependency.
- Prepended `C:\Users\Brandon\.kimi-code\bin` to the USER PATH, now first.

### The legacy migration, which failed and then succeeded

The installer carries its own kimi-cli migration: it scans every PATH
directory for a `kimi` executable whose bytes contain the marker `kimi_cli`,
renames THE FIRST to `kimi-legacy.exe` so a fallback survives, and deletes
later duplicates so the new CLI is not shadowed. It does not touch pip's
metadata.

First attempt failed — `The process cannot access the file because it is being
used by another process` — because a live old-CLI round was running (PID 22828,
image `...\Python312\Scripts\kimi.exe`). Re-run after that round finished:
renamed successfully. `kimi-legacy --version` reports `kimi, version 1.49.0`,
so the rollback binary works and `kimi` is now unambiguous.

Standing note: do not `pip uninstall kimi-cli`. The rename already removed the
shadowing problem, which was the only reason removal was attractive, and
uninstalling would delete the Python module that `kimi-legacy.exe` launches.

## The two CLIs do not share a home

| | old | new |
| --- | --- | --- |
| home | `~/.kimi/` | `~/.kimi-code/` |
| binary | `Scripts/kimi.exe` (now `kimi-legacy.exe`) | `~/.kimi-code/bin/kimi.exe` |
| log | `~/.kimi/logs/kimi.log`, user-global | per-session, see below |

Migration is an explicit `kimi migrate` subcommand, NOT automatic. The kimi-cli
project page's claim that installing "automatically migrates your configuration
and sessions" is not what this installer does. `kimi migrate` was NOT run: a
fresh `kimi login` was chosen instead, so the new home contains only what we
put there.

## `KIMI_CODE_HOME` works, and credentials are portable

`KIMI_CODE_HOME` relocates the entire data directory. Verified: with it set to
a scratch directory holding a hand-written `config.toml` and a copy of
`credentials/kimi-code.json`, `kimi doctor` validated the scratch config and
`kimi provider list` reported `managed:kimi-code type=kimi models=1
source=oauth`, then three real model calls succeeded from that home.

So credentials live at `<home>/credentials/kimi-code.json` and copy across.
An isolated per-round home is therefore buildable.

`~/.agents/skills/` is NOT under the home, so relocating the home does not
suppress it. `--skills-dir` does: its help says it loads skills from the given
directory "instead of auto-discovered user and project directories". Both
levers are needed. Whether `--skills-dir` actually suppresses a planted
project skill is UNVERIFIED — it needs the same planted-canary probe codex got,
and until then it is a mitigation, not a control.

## The real home carries an execution back-channel

`~/.kimi-code/config.toml` existed before any of this work, created 2026-07-02
by an unrelated tool called Orca. It declares SEVEN lifecycle hooks —
`UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `PostToolUseFailure`,
`PermissionRequest`, `Stop`, `StopFailure` — each running
`C:/Users/Brandon/.orca/agent-hooks/kimi-hook.sh` with a 10s timeout. `kimi
login` rewrote the file and PRESERVED every hook.

The script is inert unless `ORCA_AGENT_HOOK_PORT`, `ORCA_AGENT_HOOK_TOKEN` and
`ORCA_PANE_KEY` are all set, in which case it POSTs the hook payload to
`http://127.0.0.1:<port>/hook/kimi`.

This is a stronger back-channel than anything on the old CLI.
`merge_all_available_skills` could only add instructions; a `PreToolUse` or
`PermissionRequest` hook EXECUTES A SHELL COMMAND and sits on the approval
path. It is the user's own tooling and not a stop, but it is an independent
second reason the lane must not run in the real home.

## The transport contract changed

| old lane contract | new CLI |
| --- | --- |
| `--agent-file <yaml>` | `--agent-file <path>`, **Markdown with YAML frontmatter**, exactly one |
| `-w <workspace>` | **gone** — the session binds to its creation directory, enforced |
| `--quiet` | **gone** |
| `--thinking` | **gone** as a flag; now `[thinking] enabled` and per-model `default_effort` in config |
| `-r <session-id>` | `-S/--session [id]`; `-r` survives as a hidden alias and is what the CLI itself prints |
| five-tool allowlist | `tools:` allowlist plus `disallowedTools:` denylist plus `subagents:` allowlist |

`--agent-file` CANNOT be combined with `--session`/`--continue`.
`--prompt` cannot be combined with `--yolo`, `--auto` or `--plan`.
The canonical model id `kimi-code/k3-256k` EXISTS unchanged on the new CLI,
with `support_efforts = ["low","high","max"]` and `default_effort = "high"`.
So `references/model-prompting-notes.md` needs no model-id change.

## Containment: verified, and the control is unchanged in kind

The docs state that in `-p` mode "approval for regular tool calls is skipped",
which the wire log confirms: `{"type":"permission.set_mode","mode":"auto"}`.
Exactly as on the old CLI, the tool allowlist is the load-bearing control.

Built an agent file with `tools: [Read, Grep, Glob, ReadMediaFile, TodoList]`
and `disallowedTools: [Bash, Write, Edit, WebSearch, FetchURL, Agent,
AgentSwarm, Skill, CronCreate, CronDelete, TaskStop]`. The old five-tool set
maps one-to-one: `ReadFile`→`Read`, `SetTodoList`→`TodoList`, the other three
unchanged.

**Write-probe PASSED on all three legs**: explicit refusal in the reply, marker
absent on disk, `git -c core.quotepath=false status --porcelain --ignored -uall`
delta empty.

The tool surface is much larger than the old CLI's — `Bash`, `Write`, `Edit`,
`WebSearch`, `FetchURL`, `Agent`, `AgentSwarm`, `Skill`, `CronCreate`,
`CronDelete`, `TaskList`, `TaskOutput`, `TaskStop`, `EnterPlanMode`,
`ExitPlanMode`, `AskUserQuestion`, `TodoList`, plus the five read-only ones —
so the allowlist carries more weight, not less.

**One containment gap found.** `state.json` records
`subagents: ["agent","coder","explore","plan","parallax-readonly-reviewer"]`.
The frontmatter has a `subagents:` allowlist and we did not set it, so it
defaulted to ALL — including `coder`. That is inert here only because `Agent`
and `AgentSwarm` are in `disallowedTools`; without them the reviewer could
delegate to a subagent that writes. Set `subagents: []` and verify it takes.

## Route evidence: strictly better than the old lane

Two per-session surfaces, both under
`<home>/sessions/wd_<workspace>/<session-id>/`:

**`logs/kimi-code.log`** — one line carries the whole route:

```
INFO  llm config  turnStep=0.1 provider=kimi model=k3-256k
      modelAlias=kimi-code/k3-256k thinkingEffort=high
      systemPromptChars=152 toolCount=5
```

**`agents/main/wire.jsonl`** — a structured transcript. The records that matter:

- `tools.set_active_tools` — `names` and `disallowedNames`, the resolved lists.
- `llm.tools_snapshot` — a `hash` plus the exact tool schemas sent to the
  model. Five entries, matching the allowlist.
- `llm.request` — `provider`, `model`, `modelAlias`, `thinkingEffort`,
  `thinkingKeep`, `maxTokens`, `systemPromptHash`, `toolsHash`, `messageCount`.
- `turn.prompt` — the prompt **as received**, verbatim.
- `permission.set_mode` — `auto` in print mode.
- `usage.record` — per-turn token accounting.

Why this is better in kind, not just in detail: the old lane inferred route
from position in a shared stream, which is why one concurrent session could
destroy a round's attribution. Here every fact is inside a file created by and
named after this round's own session. There is nothing to attribute.

`toolCount=5` and the `toolsHash` are also positive checks that cannot silently
pass. If the allowlist failed to apply, the count would be the full tool set
and the hash would differ. The old `Loaded tools:` grep could match nothing and
read as clean, which is the exact failure item 13 named.

## Item 8 does not reproduce, and becomes measurable

Dispatched a 9033-character brief-shaped prompt — nearly three times the 3225
characters that truncated on 0.17.0 panel round 7 — loaded with shell-special
characters (`" & < > | ; $ % ( ) [ ] { } --`) and nonces at head, middle and
tail. All three nonces came back.

Verified against the wire log rather than the reply: `turn.prompt.input[0].text`
is 9033 characters and SHA-256 `227a6790…13f3`, identical to the string sent
after newline normalisation.

So the file-planted-brief workaround is not needed for length, and the
permanent detector is better than either candidate in item 8: hash the brief
before dispatch and compare it to the `turn.prompt` record. No nonce, no
echo-back, no cooperation from the reviewer required.

## Resume inverts the old lane's most dangerous rule

Old contract: a bare `kimi -r` loaded the DEFAULT agent with write and shell
tools while the route line still read clean, and the working directory did not
inherit — a resume without `-w` once landed in the REAL tree.

Measured on the new CLI:

- **Wrong directory is REFUSED.** A bare resume from a different directory
  exited 1 with `Session "…" was created under a different directory`, printed
  the correct `cd`, and dispatched nothing. No wire records were appended. The
  binding is enforced by the tool, not by driver discipline.
- **Correct directory inherits everything.** A bare `-r` with no `-m`, no
  `--agent-file` and no `--skills-dir` produced `llm.request` with
  `modelAlias=kimi-code/k3-256k`, `thinkingEffort=high`, and BOTH
  `toolsHash=3174a328…8777` and `systemPromptHash=982e6dea…5154` byte-identical
  to round 1. The per-session log again read `toolCount=5`. Asked which tools
  it held, the model answered "Read, Grep" and named Write, Edit and Bash as
  absent.

So the four flags the old lane re-pinned on every resumed call cannot be
re-pinned here — `--agent-file` is rejected with `--session` — and do not need
to be. The hashes are the per-round proof.

## Still unverified — do not treat these as settled

1. `--skills-dir` suppressing a planted project skill. Needs a canary probe.
2. `subagents: []` in frontmatter actually emptying the list.
3. Whether the per-round `config.toml` effort pin overrides the model's
   `default_effort`, rather than merely agreeing with it. Test with `low`.
4. Whether `.kimi-code/agents/` and `.kimi-code/skills/` inside a REVIEWED tree
   are picked up. The docs say they are project-level discovery paths, which
   would make them the same back-channel class as `.agents/skills/` and would
   extend SKILL.md preflight 3 and `tools/new-review-mirror.ps1`.
5. Per-session log rotation. `kimi export --no-include-global-log` mentions
   rotated `.1` files for the global log; per-session behaviour is unprobed.
6. `kimi upgrade` self-updates, which is a drift surface a pinned lane must
   account for.
7. `--output-format stream-json`, unexamined, and possibly a cleaner reply
   capture than parsing stdout.

## Files

All under `scratchpad/kimicode-probe/`: `install.ps1`, `install-output.txt`,
`help-root.txt`, `reviewer-agent.md`, `writeprobe-stdout.txt`,
`longprompt-stdout.txt`, `long-prompt.txt`, `isohome/` (the isolated home,
including both session directories), `ws/` (the throwaway git workspace).
These are session-scratch and will not survive; the durable record is this file.
