# Backup reviewer lane (cross-vendor substitution)

The backup lane substitutes a SECOND cross-vendor reviewer (currently
Kimi K3 via kimi-cli) when the primary reviewer transport is down. It
enters through the fallbacks.md consent gate — auto-qualified by the
classes named there, manual on user request — or via a user-invoked
panel (the participation paragraph below), and preserves
cross-vendor independence, so a backup-lane debate records
`Verification status: FULL` with the lane substitution noted per
frozen-plan-format.md. Same debate protocol, same brief conventions,
same strike rule as the primary; only the transport differs. The
canonical backup model id and thinking flag are declared ONLY in
model-prompting-notes.md — read them from there at dispatch; this file
uses placeholders.

Panel participation: a user-invoked panel per references/panels.md is a second sanctioned entry route - the invocation itself is the consent, with no fallbacks banner (nothing degraded); containment, per-round evidence, and the write-probe apply unchanged, and no failure class is recorded because nothing substituted.

## Transport

- **Environment — every call, fresh or resumed.** On a Windows driver,
  force UTF-8 for the kimi process: `PYTHONIOENCODING=utf-8` and
  `PYTHONUTF8=1`. kimi-cli is Python, so on a cp1252 console a reply
  containing any non-encodable character raises `UnicodeEncodeError`
  AFTER the model has already answered — the round completes, the
  quota is spent, and the review is lost on the way to disk. Arrows and
  em-dashes are routine in review prose, so this is a standing hazard,
  not an edge case. Observed 2026-07-26 (kimi-cli 1.49.0, Windows):
  `'charmap' codec can't encode character '→'`. Which of the two
  variables is load-bearing, and whether the same guard is needed for
  kimi's own session-log write, is UNVERIFIED — set both. The primary
  lane does not share this exposure (codex is not Python and writes the
  reply via `--output-last-message`), so the guard is lane-local.
- Dispatch (single line):
  `kimi --quiet --thinking -m <canonical-backup-model-id> --agent-file <plugin-checkout>/skills/multi-model-verify/references/kimi-reviewer-agent.yaml -w <review-mirror> -p "Read the file KIMI-REVIEW-BRIEF.md in this workspace and execute the review it describes."`
- Resume (single line — every flag below is load-bearing):
  `kimi --quiet -r <session-id> --agent-file <same yaml> -m <canonical-backup-model-id> --thinking -w <same mirror> -p "<rebuttal>"`
  A bare `kimi -r` loads the DEFAULT agent with full write and shell tools while the route line still reads clean (probed 2026-07-25: the behavioral refusal came from conversation priming with WriteFile and Shell live underneath); model and thinking inheritance come from CONFIG DEFAULTS, not the session, and the working directory does not inherit either — a resume without `-w` runs in the dispatching shell's current directory (caught live 2026-07-25: such a resume landed in the REAL tree; the containment allowlist held and the round was quarantined). Re-pin all four on every resumed call.
- The session id is printed at the end of every run ("To resume this
  session: kimi -r <uuid>"). Capture it from round 1.
- Reviewer reasoning effort has NO CLI flag and NO log field: it is
  pinned via `[models.<id>.overrides]` in `~/.kimi/config.toml`
  (evidence class: config validation only — the consent banner names
  this gap when the backup option is offered).

## Per-round evidence (fresh AND resumed calls alike)

`~/.kimi/logs/kimi.log` is a shared, user-global append stream — a bare
"the line appears somewhere" check attributes nothing. The rule:

- Before every dispatch capture the byte length of `~/.kimi/logs/kimi.log`; after the call, past that offset, require all three: exactly one new `Using LLM model:` line carrying the canonical backup id, a `Loading agent:` line naming the committed yaml, and a `Loaded tools:` line equal to the allowlist exactly.
- Zero matching new lines, more than one, a wrong id, a wrong agent path, or any extra tool entry is a route-attribution failure: the reply is DISCARDED unread and the failure goes to the fallbacks.md consent gate.
- This evidence is client-side: report it as "route line verified
  (client-side)" in the record prose. Server-side substitution is not
  detectable from this class; the finish line's normalized
  `effective route confirmed` means every round's evidence matched THIS
  lane's canonical declarations under these rules.

## Containment

- The committed pair `kimi-reviewer-agent.yaml` +
  `kimi-reviewer-system.md` (this directory) is the ONLY agent
  configuration the lane dispatches with. The yaml's five-tool
  allowlist (SetTodoList, ReadFile, ReadMediaFile, Glob, Grep) carries
  no write, shell, or web tool — kimi print mode auto-approves ALL
  tools and `--plan` does not block writes (probed), so the allowlist
  is the load-bearing control and the per-round `Loaded tools:` check
  is its verification.
- WRITE-PROBE (before round 1 of every backup-lane debate): in a fresh
  disposable session with the exact debate configuration, ask the
  contained agent to create a named marker file. PASS requires all of: explicit refusal in the reply, marker absent on disk, mirror status delta empty.
  Anything else means the lane is BROKEN (integrity failure class in
  fallbacks.md) — never dispatch a review over it.

## Client config surface (read before round 1)

`~/.kimi/config.toml` is user-global and configures this lane's client.
Two keys are read and RECORDED in the debate record; neither is a stop,
and neither is observable from the per-round route evidence above.

- The effort override block for the canonical backup id,
  `[models."<canonical-backup-model-id>".overrides]`. Absent means the
  lane runs at PROVIDER DEFAULT with no verifiable effort evidence.
  The consent banner already declares effort to be config-validation
  only; this check is what makes that claim true rather than assumed.
  Probed 2026-07-26 (kimi-cli 1.49.0): the file carried ZERO
  `overrides` blocks — the model table for the canonical id exists but
  has no override sub-table — so the pin is not set. A single read of
  the current file cannot establish what the config held during earlier
  rounds; what it does establish is that nothing pins effort now, so
  treat any round without its own contemporaneous config evidence as
  provider-default.
- `merge_all_available_skills`, plus the SOURCES it merges from. The
  key is the same class of instruction back-channel as codex's
  repo-level `.agents/skills` advertisement (SKILL.md preflight 3), on
  this lane's side of the fence, and the key alone does not tell you
  whether anything is actually being merged — so enumerate the sources
  in the same breath: `extra_skill_dirs`, `~/.kimi/skills`,
  `~/.kimi/agents`, and any repo-local skill directory. Probed
  2026-07-26 (kimi-cli 1.49.0): the key was `true` at
  `~/.kimi/config.toml:10` while `extra_skill_dirs` was empty and none
  of those directories existed — a LATENT surface with nothing to
  merge, not an active one. What the key does once those directories
  are populated is UNVERIFIED; treat a true key with a NON-EMPTY
  source as unprobed territory and say so in the record rather than
  assuming the allowlist absorbs it. The standing mitigations are
  unchanged: the mirror carries no `.agents/` once preflight
  remediation has run, and the per-round `Loaded tools:` check is the
  load-bearing control. Record key and sources together as an
  environment note citing path and line, exactly like the primary
  lane's `~/.codex/AGENTS.md` — never a finding.

A config file that cannot be read is itself the note: record that and
proceed; do not infer either key's value.

## Workspace isolation and the brief

- Reviews run in a THROWAWAY REVIEW MIRROR in the session scratchpad —
  never the real tree.
- The mirror is a FILE COPY of the working tree that PRESERVES `.git`, not
  a `git clone`. This is not a preference: a clone carries TRACKED FILES ONLY,
  and the review inputs are routinely gitignored — a project's frozen
  plans under its docs dir, `References/` for port work. Probed live
  2026-07-26 in KitnEssentials, where `dev/docs/` and `References/` are both gitignored:
  a cloned workspace drops the frozen plan, the spec, AND the reference
  source, handing the reviewer a tree with nothing to review while every
  route and containment check stays green. `.git` rides along because the
  containment check below is a git command.
- SKILL.md preflight-3 remediation is performed HERE, in the mirror,
  never in the real tree — see that section for the procedure and for
  which cases need a commit inside the mirror.
- The brief is written into the mirror as the untracked
  `KIMI-REVIEW-BRIEF.md`; the `-p` pointer tells the reviewer to read
  it (headless stdin does not carry the brief).
- Any review input the mirror cannot inherit — a standards file living
  above the repo root, an assignment PDF, a spec kept outside the tree —
  is copied in deliberately and enumerated before the round. An input the
  reviewer cannot read is a gap in the review, not a silent omission.
- **BASELINE, captured immediately after construction and BEFORE the
  brief is written**: `git status --porcelain` in the fresh mirror. A
  clone would have guaranteed this empty; a file copy does NOT — the
  real tree's untracked files and uncommitted modifications ride along,
  and without a baseline every one of them quarantines every round of a
  review that never touched them. Tracked modifications especially
  cannot be absorbed by any "untracked set" wording.
- After every round, `git status --porcelain` in the mirror must equal the BASELINE plus exactly the expected untracked set — the brief plus any review inputs copied in, enumerated before the round — and nothing else; any other delta quarantines that round's reply (integrity failure class). Both halves are declared in advance, which is what keeps the check exact rather than adjudicated after the fact.
- The mirror's identity in the debate record is its path, its
  `git rev-parse HEAD`, AND its baseline. For a file copy HEAD alone
  does not identify the reviewed content, because uncommitted work rode
  in with it. If the baseline contains TRACKED modifications the
  reviewed content is not the committed range: disclose that in the
  record, and in mode diff take the mirror from a tree whose tracked
  files are clean instead.
- The brief is retained as evidence per the raw-rounds convention.
- Never run `kimi export` inside a repo — it writes a session zip into the current directory; export only from a scratch directory. Nothing in this lane uses export.

## Failure handling

All failure classes, retries, and consent-gate dispositions live in
fallbacks.md (the single failure-class namespace) — this file defines
none of its own. Record fields for a substituted debate live in
frozen-plan-format.md.
