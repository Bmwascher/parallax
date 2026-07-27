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
  has no override sub-table — so the pin had never been set and every
  round to date ran at provider default.
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
- After every round, `git status --porcelain` in the mirror must list exactly the expected untracked set - the brief plus any review inputs copied in, enumerated before the round - and nothing else; any other delta quarantines that round's reply (integrity failure class). Keying off a declared set is what keeps the check exact once inputs are copied in.
- The mirror's `git rev-parse HEAD` is recorded in the debate record
  alongside its path.
- The brief is retained as evidence per the raw-rounds convention.
- Never run `kimi export` inside a repo — it writes a session zip into the current directory; export only from a scratch directory. Nothing in this lane uses export.

## Failure handling

All failure classes, retries, and consent-gate dispositions live in
fallbacks.md (the single failure-class namespace) — this file defines
none of its own. Record fields for a substituted debate live in
frozen-plan-format.md.
