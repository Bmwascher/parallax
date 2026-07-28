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
- Zero matching new lines, anything other than exactly one of each inside this round's block, a wrong id, a wrong agent path, or any extra tool entry is a route-attribution failure: the reply is DISCARDED unread and the failure goes to the fallbacks.md consent gate.
- **Attribute by session block, not by position in the window.** Counting
  matches across the whole post-offset window makes any concurrent kimi
  session fatal, which is what discarded two of six dispatched rounds on
  2026-07-27.
  <!-- contract:start id=session-block-attribution -->
  The three evidence lines carry no session id of their
  own, so bind them by ORDER instead: locate the one
  `Created new session: <id>` or `Resuming session: <id>` line past the
  offset whose id is THIS round's, and read only the lines from it up to the
  next session event of any id. Require exactly one of each of the three
  inside that block. Session events belonging to other ids are ignored, not
  counted.
  <!-- contract:end -->
  Verified against the live log 2026-07-28 over a window holding two foreign
  startup blocks: the old whole-window rule reported two of each and failed,
  while block attribution resolved both sessions to exactly one of each.
  <!-- contract:start id=session-block-kind -->
  The block's own kind is
  evidence too: a fresh call must show `Created new session` and a resume
  must show `Resuming session` carrying the id being resumed. A resume that
  silently started a new session has lost the reviewer's debate state, and
  the kind line is where that surfaces.
  <!-- contract:end -->
  <!-- contract:start id=session-block-residual -->
  Residual, accepted: a foreign session that starts INSIDE this round's
  startup block truncates it, and the round still fails. That window is
  under a second rather than the whole call, so collisions become rare
  rather than routine. They are not eliminated.
  <!-- contract:end -->
- **Serialize parallax's own dispatches.** Ordering handles foreign
  sessions; it cannot stop this plugin colliding with itself.
  <!-- contract:start id=lane-lock -->
  Before dispatching any
  round, acquire the lane lock with `tools/kimi-lane-lock.ps1 -Acquire
  -Label "<debate>"`, and release it with the SAME label after the round's
  evidence is read. A BUSY result means another parallax debate holds the
  lane: do not dispatch, because a concurrent round breaks attribution. The
  lock is advisory and breaks after 45 minutes, so a crashed driver stalls
  the lane for at most that long.
  <!-- contract:end -->
- **Rotation guard.** The offset rule assumes an append-only file, and
  the kimi client does not guarantee one.
  <!-- contract:start id=rotation-guard-detection -->
  Before trusting the offset,
  confirm the stream did not rotate under the call: if after the call the
  file is SMALLER than the captured offset, or absent, it was rotated or
  replaced and every byte position from the earlier measurement is
  meaningless.
  <!-- contract:end -->
  <!-- contract:start id=rotation-guard-disposition -->
  That is a route-attribution failure — and specifically
  **not a reason to re-read from zero**, which is the tempting wrong
  answer: the new file's opening lines may belong to any session, so
  reading it attributes nothing while looking like evidence.
  <!-- contract:end -->
  Rotation SUCCEEDS on this client. Observed 2026-07-27 (kimi-cli 1.49.0,
  Windows) during a live write-probe, and still on disk 2026-07-28:
  `kimi.log` was renamed to `kimi.2026-07-25_14-01-45_182023.log`
  (459709 bytes, created 2026-07-25 14:01:45) and a fresh `kimi.log` took
  its place (created 2026-07-27 15:34:43). The guard fired on its first
  real trigger and classed it correctly. An earlier note here recorded the
  opposite — that rotation attempts fail with
  `PermissionError: [WinError 32]` because the log is still open, and that
  offsets therefore held by accident rather than by design. Both halves
  were true when observed on 2026-07-26 and are false now. Do not restore
  them.
  <!-- contract:start id=rotation-guard-identity -->
  Because rotation succeeds, the size test alone is not enough: a
  replacement file that grew back PAST the captured offset inside the same
  call would pass it. So capture the file's CREATION TIME alongside the
  byte offset, and treat any later creation time as rotation whatever the
  length says.
  <!-- contract:end -->
  This supersedes the earlier judgement that a second mechanism was not
  worth building. That judgement rested entirely on rotation always
  failing, and the paragraph holding it named its own trigger: compare
  file identity if rotation ever starts succeeding here. It has.
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
  contained agent to create a named marker file. PASS requires all of: explicit refusal in the reply, marker absent on disk, mirror status delta empty (the status command above — a bare-porcelain probe would miss a marker written to an ignored path).
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
  rounds. Record a round with no contemporaneous config evidence as
  having NO VERIFIED EFFORT PIN — not as provider-default: absence of
  evidence for an override establishes neither an override nor
  provider-default operation, and writing either into the record
  manufactures a fact the lane never observed.
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
- **THE STATUS COMMAND — `git status --porcelain --ignored -uall`, every
  capture without exception** (baseline, per-round, and the write-probe
  delta). The flags are load-bearing, not tidiness: bare
  `git status --porcelain` OMITS ignored paths entirely and COLLAPSES an
  untracked directory to a single entry. Probed 2026-07-26 in a scratch
  repo with `ign/` gitignored — bare porcelain printed only `?? untr/`,
  hiding both `ign/secret.txt` and the two files under `untr/sub/`,
  while `--ignored -uall` printed all three. Ignored content is the
  entire reason this workspace is a mirror, so a bare-porcelain check is
  blind to precisely the class the mirror exists to carry: a contained
  reviewer writing to any ignored path would not appear.
- **BASELINE, captured after construction AND after any preflight-3 remediation, immediately before the brief is written**:
  the status command above, in the mirror. A clone would have guaranteed
  this empty; a file copy does NOT — the real tree's untracked files
  and uncommitted modifications ride along, and without a baseline
  every one of them quarantines every round of a review that never
  touched them. Tracked modifications especially cannot be absorbed by
  any "untracked set" wording. The timing is load-bearing: remediation
  deletes entries and in the tracked case commits, so a baseline taken
  before it fails every round of a remediated debate and pins a HEAD
  the mirror no longer has — and remediation is precisely the procedure
  the mirror exists to support.
- What the check does and does not see, stated exactly: with the flags
  above it detects any path that APPEARS IN OR DISAPPEARS FROM the
  mirror, ignored and untracked paths included. It remains PATH-level,
  so a path already present in the baseline shows the same entry however
  its CONTENT changes. That residue is bounded by the tool allowlist and
  the write-probe, which stay the load-bearing controls, and by the
  content manifest below for the inputs that matter.
- After every round, the status command in the mirror must equal the BASELINE plus exactly the expected untracked set — the brief plus any review inputs copied in, enumerated before the round — and nothing else; any other delta quarantines that round's reply (integrity failure class). Both halves are declared in advance, which is what keeps the check exact rather than adjudicated after the fact.
- The mirror's identity in the debate record is its path, its
  `git rev-parse HEAD`, its baseline, AND a CONTENT MANIFEST. HEAD binds
  tracked content only, and in this lane the inputs that matter are
  deliberately outside it, so without the manifest the record names what
  was reviewed without being able to reconstruct it.
- **The manifest, specified to be executable without judgment:**
  - **Universe first**: the mirror's WORKTREE files, excluding the root
    git administrative entry `.git` entirely (it may be a directory or,
    in a worktree or submodule checkout, a file — exclude it either
    way). The mirror preserves `.git` on purpose, and HEAD represents
    none of its contents, so without this exclusion the coverage test
    below would recursively hash repository metadata — objects, logs,
    index, hooks, config — which is volatile, potentially enormous, and
    identifies nothing about the reviewed material.
  - **Coverage within that universe is exactly the paths the BASELINE
    capture lists** — the same `--ignored -uall` output, so manifest and
    baseline describe one tree state and cannot disagree. Those are, by
    git's own reckoning, the files whose CURRENT worktree bytes HEAD
    does not account for — untracked, ignored, or modified-relative-to-
    HEAD (for a modified tracked file HEAD still binds its committed
    content; what it does not bind is what the reviewer will actually
    read). Do NOT
    define coverage as "bytes differ from the HEAD blob": git applies
    clean/smudge filters, so on a line-ending-normalizing checkout a
    file git calls CLEAN is not byte-identical to its blob. Probed
    2026-07-26 on this repo (`core.autocrlf=true`): `README.md` is
    25843 bytes in the worktree and 25417 in the blob, reported clean by
    `git status`; the byte rule classified 283 of 287 files as
    manifest-worthy against a 122-entry baseline, degenerating to the
    whole tree. Coverage by baseline admits the
    copied-in inputs, the gitignored subject material (frozen plan,
    spec, reference source), inherited untracked files whether ignored
    or not, and any tracked file modified relative to HEAD (which mode
    diff bars outright and other modes permit only with disclosure). An
    enumerated list would omit a class; this cannot.
  - **Directories expand RECURSIVELY to their files.** A directory
    subject such as `References/` is never one manifest entry; a hash
    over a directory name identifies nothing.
  - **Two baseline entry shapes are not hashable as written, and each
    has a defined action** — without these a driver hits an entry with
    no file to read and has to invent a rule:
    - **Deletion-only entries** (` D` / `D `): OMIT them. There are no
      bytes to hash, and nothing is lost — HEAD plus the baseline
      already bind the absence, which is the whole content of the fact.
    - **Rename or copy entries** (`R`/`C`, `old -> new`): hash the
      CURRENT DESTINATION path. The source path is a deletion and falls
      under the rule above.
  - **Entry format**: one line per file — the repo-relative path, a
    single space, then the SHA-256 of the file's raw bytes as lowercase
    hex. Fixing the separator and the encoding is what makes two
    captures byte-comparable instead of merely equivalent.
  - **Order**: sorted by path in byte order, so the manifest is
    deterministic and two captures are diffable.
  - **Captured at the same moment as the baseline** — after construction
    and any preflight-3 remediation, immediately before the brief is
    written — so the two describe the same tree state. The brief itself
    is written after both and is therefore not in either.
- If the baseline contains TRACKED modifications the reviewed content is
  not the committed range: disclose that in the record, and in mode diff
  take the mirror from a tree whose tracked files are clean instead.
- The brief is retained as evidence per the raw-rounds convention.
- Never run `kimi export` inside a repo — it writes a session zip into the current directory; export only from a scratch directory. Nothing in this lane uses export.

## Failure handling

All failure classes, retries, and consent-gate dispositions live in
fallbacks.md (the single failure-class namespace) — this file defines
none of its own. Record fields for a substituted debate live in
frozen-plan-format.md.
