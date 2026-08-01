# Backup reviewer lane (cross-vendor substitution)

The backup lane substitutes a SECOND cross-vendor reviewer (currently
Kimi K3 via kimi-code) when the primary reviewer transport is down. It
enters through the fallbacks.md consent gate — auto-qualified by the
classes named there, manual on user request — or via a user-invoked
panel (the participation paragraph below), and preserves
cross-vendor independence, so a backup-lane debate records
`Verification status: FULL` with the lane substitution noted per
frozen-plan-format.md. Same debate protocol, same brief conventions,
same strike rule as the primary; only the transport differs. The
canonical backup model id, the canonical backup PROVIDER, the canonical
backup reasoning EFFORT and the canonical backup THINKING DECLARATION
are declared ONLY in model-prompting-notes.md — read all four from there
at dispatch; this file uses placeholders. This client carries no
thinking flag and no effort flag: both values are written into the
debate home's `config.toml` by `tools/new-kimi-lane-home.ps1`.

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
- `<kimi-code-binary>` is the client's ABSOLUTE path — `~/.kimi-code/bin/kimi.exe` on Windows — never a bare `kimi` resolved from PATH. The superseded client is still installed alongside it, so a PATH lookup is not evidence of which binary ran.
- Dispatch (single line):
  `<kimi-code-binary> -m <canonical-backup-model-id> --agent-file <plugin-checkout>/skills/multi-model-verify/references/kimi-reviewer-agent.md --skills-dir <debate-home>/skills -p "<the whole brief>"`
  with the process's WORKING DIRECTORY set to the review mirror. This
  client has no workspace flag: the session binds to the directory it
  was created in, and that binding is enforced by the client itself.
- Resume (single line):
  `<kimi-code-binary> --session <session-id> -m <canonical-backup-model-id> --skills-dir <debate-home>/skills -p "<rebuttal>"`
  run from the SAME working directory, with `KIMI_CODE_HOME` still set
  to the debate home.
- The session id is printed at the end of every run ("To resume this
  session: kimi -r <id>"). Capture it from round 1: it is both the
  resume argument and the name of the session directory the per-round
  evidence is read from.
- **The brief is passed INLINE**, in the dispatch's own `-p` payload —
  never planted as a file with a pointer telling the reviewer to read
  it. The hash rule below can only detect truncation if the recorded
  prompt IS the brief; a pointer's hash proves that the pointer arrived
  and says nothing about the brief. A brief that exceeds what the
  inline transport carries is a TRANSPORT FAILURE to diagnose, not a
  reason to switch to a pointer. Measured 2026-07-31: a 9033-character
  brief-shaped prompt loaded with shell-special characters arrived
  whole, at nearly three times the length that truncated on the
  superseded client.
- **Build the debate home before round 1.**
  <!-- contract:start id=lane-home-isolation -->
  Build the lane home ONCE, before round 1, with
  `tools/new-kimi-lane-home.ps1 -Path <debate-home> -Model
  <canonical-backup-model-id> -Effort <canonical-backup-effort>`, and
  set `KIMI_CODE_HOME=<debate-home>` on EVERY call of that debate,
  fresh and resumed alike. Two INDEPENDENT reasons, either one
  sufficient on its own: the real user-global `~/.kimi-code/config.toml`
  can carry lifecycle hooks that run a shell command on the reviewer's
  own approval path, and the home is where this lane's effort pin and
  this debate's session evidence live. One debate is one home and one
  session; a home is never reused across debates, because a reused home
  carries other debates' sessions into this one's evidence. A home that
  cannot be built, or a missing credential, makes the lane UNAVAILABLE —
  never a reason to dispatch from the real home. Remove the home with
  `tools/new-kimi-lane-home.ps1 -Path <debate-home> -Remove` when the
  debate ends, because it holds a copied credential.
  <!-- contract:end -->
- **What a resume inherits, and what it cannot.**
  <!-- contract:start id=resume-inheritance -->
  Measured on kimi-code 0.31.1: from the correct working directory, a
  bare resume carrying no `-m`, no `--agent-file` and no `--skills-dir`
  reproduced round 1's model alias, effort and tool count, and BOTH its
  `toolsHash` and its `systemPromptHash` byte for byte. A resume from
  the WRONG directory is REFUSED by the client before anything is
  dispatched, so a resume can no longer land in the real tree by
  omission. `--agent-file` is REJECTED with `--session` — the agent is
  bound at session creation — so it cannot be re-pinned at all; of the
  four flags tested, `-m`, `--skills-dir` and `--add-dir` are accepted,
  and the two the lane uses are re-pinned on every resumed call because
  it is free and it narrows the inheritance risk to the one flag that
  cannot be re-pinned. Nothing is established about any flag outside
  that tested set. All of this is VERSION-BOUND, which is why the drift
  floor exists, why what can be re-pinned is re-pinned, and why the
  per-round evidence below — not this paragraph — is what establishes
  the surface actually in force each round.
  <!-- contract:end -->

## Per-round evidence (fresh AND resumed calls alike)

Every fact this lane needs is inside two files created by, and named
after, THIS debate's own session:
`<debate-home>/sessions/wd_<workspace>/<session-id>/agents/main/wire.jsonl`
(a structured transcript) and `.../logs/kimi-code.log` (a per-session
log). There is no shared stream and nothing to attribute by position.

- **The slice boundary.**
  <!-- contract:start id=round-freshness-boundary -->
  Both files are CUMULATIVE, so each call is read as a SLICE of them.
  Before every call capture, for BOTH the wire transcript and the
  per-session log, the file's BYTE length and a SHA-256 over exactly
  those bytes; after the call read only past those byte offsets, and
  require both prefix hashes unchanged. A file shorter than its offset,
  or absent, or whose prefix hash changed, was replaced: that is a
  route-attribution failure, and specifically NOT a reason to re-read
  from zero, because the replacement's opening records may belong to
  anything. Byte offsets and a hash over raw bytes are what make the
  boundary unambiguous, and hashing BOTH files is what makes the check
  prove IDENTITY rather than length — length alone passes a file that
  was replaced, truncated and regrown. A FRESH call has no offsets to
  capture, because its session does not exist until the client creates
  it; what is captured before a fresh dispatch is the session
  INVENTORY, and exactly one new SESSION LEAF must appear afterwards,
  matching the session id the client printed. A leaf is a directory
  whose name begins `session_`. Counting directories rather than leaves
  is wrong and would reject a clean first call: the measured layout
  nests leaves inside a `wd_`-prefixed workspace container, and a
  debate's first call in a workspace creates the container as well as
  the session. The slice must also BEGIN at a call boundary — the
  record `metadata` for a fresh call, `turn.prompt` for a resume, both
  measured — because an offset landing mid-call yields a slice mixing
  the previous call's trailing records with this one's while satisfying
  every count and value check.
  <!-- contract:end -->
- **What each slice must contain.**
  <!-- contract:start id=per-round-session-evidence -->
  The records fall into TWO CLASSES and one rule cannot cover both: a
  rule that assumed it could was measured to fail a clean round 1 and
  every resumed round. SESSION-SCOPED records — `config.update` twice,
  `tools.set_active_tools`, `llm.tools_snapshot` and
  `permission.set_mode` once each — appear ONLY in the
  session-creating call's slice. Require them there, checking the
  agent profile name, the system prompt, the model alias, the effort,
  the permission mode, and the configured allowlist, denylist and
  resolved tool snapshot by EXACT LIST EQUALITY against the committed
  agent file; and require their ABSENCE from a resume's slice, because
  their presence there means the resume silently started a new session
  and lost the reviewer's debate state. PER-CALL records appear in
  every slice: exactly one `turn.prompt`, one or more `llm.request`
  with EVERY one carrying the canonical provider, model and effort, and
  exactly one new `llm config` log line carrying those plus
  `toolCount` and `systemPromptChars`. `llm.request` tracks the tool
  loop, so it is bounded from below and never fixed. Run
  `tools/read-kimi-round-evidence.ps1` in its FRESH form for the
  session-creating call, passing the pre-dispatch session inventory and
  the session id the client printed, and in its RESUME form for every
  later call, passing the previous call's returned state. Require
  `status: clean`: a missing directory, a missing or miscounted record,
  an unreadable file, a malformed line, or any inequality is a
  route-attribution failure, the reply is DISCARDED unread, and the
  failure goes to the fallbacks.md consent gate.
  <!-- contract:end -->
- **Continuity across rounds.**
  <!-- contract:start id=evidence-hash-continuity -->
  Record round 1's `toolsHash` and `systemPromptHash` IN THE DEBATE
  RECORD and carry them forward: the validator itself requires every
  later round to match them, rather than leaving the comparison to a
  driver who might never make it. They are deliberately NOT pinned to a
  literal in this repo, because they cover tool schemas any client
  release may reword, and a committed literal would fail every round
  for a reason that is not a route problem. Recording them is what
  makes a client upgrade's change VISIBLE in the record instead of
  silently rebaselined at the next round 1.
  <!-- contract:end -->
- **The brief that was actually received.**
  <!-- contract:start id=brief-hash-binding -->
  Hash the brief BEFORE dispatch and require the recorded prompt to
  match: SHA-256 over the brief canonicalized as UTF-8 with CRLF
  normalized to LF, compared against the same hash of the concatenation
  of every `turn.prompt` `input[]` element's `text` field. The
  canonicalization is part of the rule rather than an implementation
  detail: the measured evidence matched only after newline
  normalization, so a rule saying merely that the two hash to the same
  value leaves a driver to invent that step.
  <!-- contract:end -->
- What these checks do and do NOT guarantee, stated narrowly. A failed
  allowlist does not necessarily change the EFFECTIVE tool set, because
  the denylist can exclude the same tools by name. What they do
  guarantee is that the configured lists, the resolved tool snapshot,
  the system prompt and its length are each compared against committed
  text, so a divergence in any of them surfaces.
- This evidence is client-side: report it as "route line verified
  (client-side)" in the record prose. Server-side substitution is not
  detectable from this class; the finish line's normalized
  `effective route confirmed` means every round's evidence matched THIS
  lane's canonical declarations under these rules.

## Containment

- The committed `kimi-reviewer-agent.md` (this directory) is the ONLY
  agent configuration the lane dispatches with, and it carries THREE
  controls rather than one. Its five-tool allowlist (`Read`, `Grep`,
  `Glob`, `ReadMediaFile`, `TodoList`) carries no write, shell, or web
  tool — print mode auto-approves ALL tool calls, recorded as
  `permission.set_mode: auto` in the wire transcript, so the allowlist
  is load-bearing. Its `disallowedTools` denylist names every other
  documented built-in, and its `subagents: []` empties a list that
  otherwise defaults to ALL profiles including a writing one. Each is a
  control in its own right rather than a coincidence of two lists:
  measured, the default subagent list was inert only because `Agent`
  and `AgentSwarm` happened to be denied. All three lists are verified
  per round by the exact-list comparison in the evidence rules above.
- WRITE-PROBE (before round 1 of every backup-lane debate): in a fresh
  disposable session with the exact debate configuration — the
  committed `kimi-reviewer-agent.md`, the same debate home, the same
  model and effort — ask the contained agent to create a named marker
  file. PASS requires all of: explicit refusal in the reply, marker absent on disk, mirror status delta empty (the status command above — a bare-porcelain probe would miss a marker written to an ignored path).
  Anything else means the lane is BROKEN (integrity failure class in
  fallbacks.md) — never dispatch a review over it.

## Client config surface (read before round 1)

Two keys of the DEBATE HOME's own `config.toml` are read and RECORDED in
the debate record — the model table's `default_effort`, and
`extra_skill_dirs` with the discovery roots it does not cover. Neither
is a stop. Record them as an environment note citing path and line,
exactly like the primary lane's `~/.codex/AGENTS.md` — never a finding.

- EFFORT is written into the debate home and CONFIRMED PER CALL. The
  home's model table carries `default_effort`, and that value appears
  in the session log's `thinkingEffort` field and in every
  `llm.request` of the round, where the per-round evidence above
  compares it against the canonical declaration. Probed 2026-07-31
  (kimi-code 0.31.1): a home pinning `default_effort = "low"` produced
  `thinkingEffort=low` in both surfaces. So effort on this lane is
  verifiable by construction, and the round's own evidence — not a
  reading of a config file taken later — is what verifies it.
- THINKING is CONFIG-ASSERTED AND NOT RUNTIME-VERIFIED. Probed
  2026-07-31 (kimi-code 0.31.1): `[thinking] enabled = false` produced
  output identical to `enabled = true` — same `thinkingEffort`, same
  `thinkingKeep`, and no differing field anywhere in the log or the
  wire transcript. Record exactly that, and do not present thinking
  beside effort as though both were confirmed per call.
- SKILL DISCOVERY has FOUR roots — `.kimi-code/skills/`,
  `.agents/skills/`, `<debate-home>/skills/` and `~/.agents/skills/` —
  which are the same class of instruction back-channel as codex's
  repo-level `.agents/skills` advertisement (SKILL.md preflight 3), on
  this lane's side of the fence. `--skills-dir` is a MITIGATION whose
  effect is UNMEASURABLE in this configuration, not a control. Probed
  2026-07-31 with canaries planted at both project roots: runs with and
  without the flag were indistinguishable, and the reviewer reported no
  skills available at all — most likely because `Skill` is absent from
  the agent's tool allowlist, so nothing is advertised to it either
  way. The load-bearing controls are that allowlist and preflight-3
  remediation. Keep passing `--skills-dir`, because it costs nothing
  and covers a future release that advertises regardless, but claim
  nothing for it.
- A planted `SKILL.md` remains READABLE as ordinary workspace content
  whatever the discovery configuration does. In the measured round the
  reviewer read both canaries with `Read`, recognized them as injection
  attempts and declined on its own judgment. Prompt text is never a
  control, which is why remediation REMOVES the files rather than
  trusting the reviewer to ignore them.

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
- SKILL.md preflight-3 remediation is performed HERE, in the mirror, never
  in the real tree. `tools/new-review-mirror.ps1` performs construction,
  remediation, the re-enumeration, the baseline, the manifest and the
  client probe as one step; the rules below remain its specification, and
  a driver building a mirror by hand still follows them.
- The mirror is the dispatch's WORKING DIRECTORY, and the brief is
  passed INLINE in the `-p` payload — it is never written into the
  mirror as a file with a pointer to it. The reason is the hash rule,
  stated with the transport above: a hash of the recorded prompt binds
  the brief only when the recorded prompt IS the brief.
- Any review input the mirror cannot inherit — a standards file living
  above the repo root, an assignment PDF, a spec kept outside the tree —
  is copied in deliberately and enumerated before the round. An input the
  reviewer cannot read is a gap in the review, not a silent omission.
- **THE STATUS COMMAND — `git -c core.quotepath=false status --porcelain
  --ignored -uall`, every capture without exception** (baseline,
  per-round, and the write-probe
  delta). The flags are load-bearing, not tidiness: bare
  `git status --porcelain` OMITS ignored paths entirely and COLLAPSES an
  untracked directory to a single entry. Probed 2026-07-26 in a scratch
  repo with `ign/` gitignored — bare porcelain printed only `?? untr/`,
  hiding both `ign/secret.txt` and the two files under `untr/sub/`,
  while `--ignored -uall` printed all three. Ignored content is the
  entire reason this workspace is a mirror, so a bare-porcelain check is
  blind to precisely the class the mirror exists to carry: a contained
  reviewer writing to any ignored path would not appear.
  `core.quotepath=false` is load-bearing for COMPARABILITY, not for
  correctness of any single capture: git's default renders a non-ASCII
  pathname as a quoted display form carrying octal escapes, while the
  mirror's recorded baseline carries the same pathname raw, so a per-round
  capture taken without the flag reports a difference that does not exist.
  The escaped form is not written out here, because this file is checked
  for the absence of backslashes; it is in the design record. Measured
  2026-07-29.
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
- After every round, the status command in the mirror must equal the BASELINE plus exactly the expected untracked set — the enumerated review inputs copied in before the round, and nothing else — so a debate that copies nothing in expects the BASELINE EXACTLY. Say so in advance either way: "baseline plus nothing" is the case a driver would otherwise read as a broken capture. The brief is not in that set, because the brief is passed inline and never lands in the mirror. Any other delta quarantines that round's reply (integrity failure class). Both halves are declared in advance, which is what keeps the check exact rather than adjudicated after the fact.
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
    - **Rename or copy entries** (`R`/`C`, recorded as `old -> new`):
      hash the CURRENT DESTINATION path. The source path is a deletion
      and falls under the rule above. The recorded form is git's DISPLAY
      order; the `-z` capture the mirror script reads emits the two
      pathnames in the opposite order, destination first, and the script
      renders them back into this form. Measured 2026-07-29.
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
- Never run `kimi export` inside a repo — the subcommand exists on this
  client (`kimi export [sessionId]`, verified on 0.31.1), it writes the
  session as a ZIP archive, and by default it bundles the global
  diagnostic log into it as well. Export only from a scratch directory,
  and pass `-o` so the destination is chosen rather than defaulted.
  Nothing in this lane uses export.

## Failure handling

All failure classes, retries, and consent-gate dispositions live in
fallbacks.md (the single failure-class namespace) — this file defines
none of its own. Record fields for a substituted debate live in
frozen-plan-format.md.
