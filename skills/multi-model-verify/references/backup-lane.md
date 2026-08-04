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
  Build the DEBATE home ONCE, before round 1, with
  `tools/new-kimi-lane-home.ps1`, and set `KIMI_CODE_HOME=<debate-home>`
  on EVERY call of that debate, fresh and resumed alike. Two directories
  matter here and the shipped text must not blur them: the DEBATE home
  is this debate's throwaway `KIMI_CODE_HOME`, and the LANE home is the
  persistent directory holding the lane's own login and the lock. Two
  INDEPENDENT reasons, either one sufficient: the real user-global
  `~/.kimi-code/config.toml` can carry lifecycle hooks that run a shell
  command on the reviewer's own approval path, and the home is where
  this lane's effort pin and this debate's session evidence live. One
  debate is ONE home: that debate's ROUNDS are one session, and the only
  other session the home may hold is the write-probe's own disposable
  one, created before round 1 and therefore already in the inventory the
  freshness rule captures. A home is never reused across DEBATES,
  because a reused home carries another debate's sessions into this
  one's evidence. The home holds NO COPY of any credential. Its
  `credentials` directory is a JUNCTION to a DEDICATED LANE LOGIN,
  distinct from the user's ordinary login, so a refresh writes THROUGH
  to one file and no copy can go stale; the lane never falls back to the
  ordinary credential. A home that cannot be built, or a lane credential
  that is absent, unreadable or structurally invalid, makes the lane
  UNAVAILABLE, never a reason to dispatch from the real home. Remove the
  home with `-Remove` when the debate ends. The lock protocol every one
  of those calls follows is the call-lifecycle region below.
  <!-- contract:end -->
- **The persistent lane lock.**
  <!-- contract:start id=lane-lock -->
  The lane home is shared between debates and sessions, so one
  PERSISTENT lock file beside the credential guards it. That file is
  NEVER unlinked: acquire, reclaim and release are all state transitions
  written IN PLACE, each under one exclusive handle that serializes
  every writer. Staleness is LIVENESS and never a clock. A holder is
  stale only when no process carries its recorded id, or a process
  carries it with a different start time, which is the identity-reuse
  guard. A predecessor of this lock decided staleness by AGE, so a live
  round past the threshold became breakable by anyone; nothing here has
  a time-based expiry, and a wait budget bounds only caller patience and
  never widens what counts as stale. What cannot be evaluated is HELD: a
  record naming another machine, an unreadable file, a zero-length file,
  a file that is not a JSON object, or a JSON object that does not
  exactly satisfy the record schema — version 1, one of the two state
  literals, that state's exact field set, and every field's type and
  validation rule — are each held and reported rather than reclaimed,
  because an unmade measurement is never a clean one. A DEAD-holder
  reclaim reports the holder it replaced. An exhausted wait reports the
  LIVE or UNMEASURABLE holder it refused, or reports handle contention
  when no record could be read. Each confirmed override reports the
  record or bytes it displaced. Contention WAITS up to the
  caller-supplied budget and then refuses; a zero budget refuses at
  once, and no budget ever breaks a holder. Two human overrides exist
  because one cannot cover both states: a well-formed HELD record is
  freed by confirming its complete recorded identity, machine name
  included, and a record too damaged to trust its identity is freed by
  confirming the exact hash of its current bytes. Both are guarded human
  overrides, not authentication, and both leave the file in place.
  <!-- contract:end -->
- **The lock's call lifecycle.**
  <!-- contract:start id=lane-lock-call-lifecycle -->
  Ownership is RESOLVED ONCE per debate and PASSED EXPLICITLY
  thereafter. The owner is the harness session process, not the shell,
  which exits between calls and would make every lock instantly stale;
  deriving it from the invoking shell's parent is correct only for a
  DIRECT invocation, and under any wrapper it names an intermediate
  process that also exits. So run `tools/kimi-lane-lock.ps1
  -ResolveOwner` once at the start of the debate, keep its `ownerPid`
  and `ownerStartTicksUtc`, generate one 32-character lowercase
  hexadecimal debate id, and hand all three to every later call. Build
  with `tools/new-kimi-lane-home.ps1 -Path <debate-home> -Model
  <canonical-backup-model-id> -Effort <canonical-backup-effort>
  -LaneHome <lane-home> -DebateId <id> -OwnerPid <pid>
  -OwnerStartTicksUtc <ticks>`; it acquires the lock before it validates
  the credential, because a login could otherwise write that credential
  in between, and it releases only when the build itself failed. Build
  prints one JSON line carrying `debateHome` and `nonce`: keep that
  nonce, because removal requires it and a hold nobody can release is a
  lane nobody else can use. Remove with `tools/new-kimi-lane-home.ps1
  -Path <debate-home> -Remove -LaneHome <lane-home> -DebateId <id>
  -OwnerPid <pid> -OwnerStartTicksUtc <ticks> -Nonce <nonce>`; it
  confirms the complete identity BEFORE it deletes anything, so a caller
  who cannot release also cannot destroy, and it releases only after the
  home is gone. Log the lane in with `tools/new-kimi-lane-login.ps1
  -LaneHome <lane-home> -OwnerPid <pid> -OwnerStartTicksUtc <ticks>
  -VerdictOut <path>`, passing the SAME lane home the build was given,
  because omitting it authenticates the default home while the debate
  dispatches from another; the wrapper generates its own debate id,
  takes the same lock with the lane home as its debate home, and
  releases it on the way out. A login outside that lock would be the one
  writer this protocol never sees. Only these filesystem interactions
  occur before lock acquisition, because the lock lives inside the lane
  directory: the login wrapper's fail-closed probe of the lane
  directory, the login wrapper creating that directory when the probe
  measured it missing, the login wrapper applying its access rules, and
  the builder's own read-only fail-closed probe of whether that
  directory is there. All four interactions are safe to repeat: both
  probes only read, and directory creation and ACL application are
  idempotent. The builder NEVER creates the directory: if it is missing
  the builder prints the login command and stops without taking the
  lock, and once the directory is confirmed the credentials directory
  and the credential file are both measured UNDER the lock. A debate
  that ends without removal leaves its home on disk and its record still
  HELD; that record is not freed by the session exiting, it merely
  becomes DEAD by liveness and is reclaimable at some later acquire.
  Read the state at any time with `tools/kimi-lane-lock.ps1 -Status
  -LaneHome <lane-home>`, which reports the holder and its liveness and
  reports LIVE to mean the process is running, never to mean the debate
  is still going.
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
  value leaves a driver to invent that step. "The brief" here means the
  payload of EVERY call in the debate, fresh and resumed alike: a
  resumed round's payload is a rebuttal rather than the opening brief,
  and it is bound by this same rule. Stating it removes an inference -
  a rule that named only round 1 would leave every later round's
  delivery unchecked, which is the gap this rule exists to close.
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
  and `AgentSwarm` happened to be denied. Each round's evidence checks
  these lists at the reach that check actually has, and the two reaches
  are not the same: the SESSION-CREATING call's slice compares the
  configured allowlist, the denylist and the resolved tool snapshot
  against this file by EXACT LIST EQUALITY, while a RESUMED call — whose
  slice carries none of those records at all — is covered instead by
  `toolCount` equality against this file's allowlist length and by
  `toolsHash` and `systemPromptHash` continuity with the call that was
  compared. Both are real checks; only the first is an exact-list
  comparison, and saying otherwise would claim a reach no round has.
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
  this lane's side of the fence. The home's own `extra_skill_dirs` is
  the key recorded alongside them: the builder writes it EMPTY, so a
  non-empty value in a debate's home was written by something other than
  the builder and is a finding about the home, not a note. Coverage is
  NOT uniform across the four roots, and the record must not read as
  though it were: preflight-3 remediation clears the two project roots
  because it operates on the MIRROR, and `<debate-home>/skills/` is
  created empty by the builder — but `~/.agents/skills/` lives in the
  user's own home, is not relocated by `KIMI_CODE_HOME`, and NOTHING
  this lane runs removes it.
  <!-- contract:start id=home-skill-root-disposition -->
  Enumerate that root before round 1 and record its COUNT, never its
  contents - the repo is public. MEASURED 2026-08-03 on kimi-code 0.31.1,
  and no longer unprobed: a canary skill planted in that root was
  REACHABLE when `--skills-dir` was omitted - the wire carried the
  invocation and a `skill_activation` message delivering the body - and
  was NOT found when the flag was passed, the lookup returning the
  calibrated not-found result exactly. Treat the enumeration as an
  environment record of reachable external instruction inventory, not as
  a control and not as evidence that any real skill was invoked. Record:
  docs/superpowers/plans/rounds/2026-08-03-home-skills-root/probe-record.md
  <!-- contract:end -->
  <!-- contract:start id=home-skill-root-disposition-limit -->
  The disposition is bound to what the probe reached: one skill, named
  exactly, at the home root, on kimi-code 0.31.1. Suppression was
  measured for that root ALONE; the two project roots were never
  canaried, and their exclusion rests on the client's own help text,
  which says the flag's target is used instead of auto-discovered
  directories - text evidence, never a measurement - and on preflight-3
  remediation clearing the project roots in the mirror regardless. No
  cell passed the flag against a POPULATED target, so what the flag does
  to its own target is unmeasured; suppression was measured only for
  `~/.agents/skills/`, with that target EMPTY, and that measurement
  holds only while `<debate-home>/skills/` stays empty: the builder
  creates it empty and asserts that as its own postcondition, and no
  per-round check re-verifies it at dispatch. On that client
  `systemPromptChars`
  equalled the LF-normalized agent body in every cell, including both
  loaded-canary cells, so the measured delivery path was
  `skill_activation` and not system-prompt injection: the deny list
  controls that measured path, and the lane's system-prompt equality
  checks, not the deny list, would have to reject any future injection
  path. A client whose skill delivery changes shape retires this
  measurement rather than inheriting it.
  <!-- contract:end -->
  The load-bearing control as the lane ships is the `Skill` deny list, and
  what is MEASURED of it is the TOOL SURFACE: cells A and B advertised five
  tools with `Skill` absent, and the round validator compares that snapshot
  against the agent file by exact list equality on every session-creating
  call. Those cells passed the flag as well, so they measure the
  COMPOSITION and cannot attribute their null result to either layer alone.
  Keep passing `--skills-dir` on every call, fresh and resumed, as a
  measured second layer, and claim for it exactly what was measured:
  suppression of the home root, conditional on an empty target, on 0.31.1.
- A planted `SKILL.md` remains READABLE as ordinary workspace content
  whatever the discovery configuration does. In the measured round the
  reviewer read both canaries with `Read`, recognized them as injection
  attempts and declined on its own judgment. Prompt text is never a
  control, which is why remediation REMOVES the files rather than
  trusting the reviewer to ignore them.

A config file that cannot be read is itself the note: record that and
proceed; do not infer either key's value.

## Workspace isolation and the brief

- Reviews run in a THROWAWAY REVIEW MIRROR — never the real tree. Build
  it at a SHORT path directly under the temp directory, such as a
  `kerev<n>` folder, and never inside the session scratchpad, whose own
  path is long enough to consume most of the budget before the copy
  starts. This sentence used to say "in the session scratchpad" and
  SKILL.md said the opposite, a contradiction 0.21.0 introduced and the
  mode-diff debate caught: an operator reading both could comply with
  neither. The rule is stated in BOTH files and must be changed in both:
  SKILL.md carries it inline because that is where preflight 3 acts, and
  a reader who never opens this file still has to know it. Saying it
  lives in one place would be the same false claim in the other
  direction, which round 2 of the same debate caught.
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
- **Mirror identity, and the gate that keeps it fresh.**
  <!-- contract:start id=mirror-identity-gate -->
  The record carries TWO identities and one fingerprint: `source_head`,
  `mirror_head` and `source_status_sha256`. The two heads differ whenever
  remediation committed, which is the ordinary case for a repo carrying a
  tracked back-channel, so a record printing one of them twice is wrong
  in the common case rather than the rare one. Construction is a
  six-step bridge. Capture the source head BEFORE the copy; copy;
  require the live source head still equals it; before remediation,
  require the COPIED tree's head equals it; remediate, then record
  `mirror_head`. Steps three and four are the bridge itself: without
  them the record can hold two individually valid commit ids while
  nothing proves the mirror was built FROM the recorded source commit,
  which is two true facts arranged to look like one. What the bridge
  proves is matching OBSERVED ENDPOINTS, and that is weaker than an
  uninterrupted construction: a source that moves away and back during
  the copy satisfies both the before-and-after head equality and the
  before-and-after fingerprint, while the copied worktree can still hold
  intermediate bytes. The debate named that gap and it is real; the only
  thing that would close it is building from an immutable snapshot,
  which this release does not do. Before every fresh
  and resumed dispatch, re-run the tool with `-VerifyIdentity` and the
  three recorded values. Missing, unreadable or unequal BLOCKS the
  round, and a value that was never recorded is never a value that
  matched. What the gate proves is narrow and stated so: the two-HEAD
  gate proves committed-HEAD freshness. Non-HEAD inputs are bound in the
  constructed mirror's manifest AT CONSTRUCTION TIME, and source-side
  changes after construction are detected by the source-status
  comparison below WHEN THEY ARE VISIBLE TO IT: that is, changes that
  move the status listing, or that alter the content of a path the
  listing names. A tracked file git reports CLEAN is in neither, so a
  raw-byte change that survives the clean filter unchanged - the
  autocrlf case measured below is the mild one, a content-stripping
  filter the severe one - moves neither HEAD nor this fingerprint and is
  NOT covered. Round 2 of the mode-diff debate found the unqualified
  claim. That comparison is a fingerprint over the status
  capture AND the content of every path status names, not the status
  listing alone: measured 2026-08-04, editing an already-ignored file
  leaves the listing byte-identical, so a listing-only fingerprint
  verified clean across exactly the drift this check exists to catch.
  Ignored and untracked content is the entire reason this workspace is a
  mirror, so a gate blind to its bytes would be blind in the middle of
  the feature.
  <!-- contract:end -->
- **The path budget, checked BEFORE anything is created.**
  <!-- contract:start id=mirror-path-budget -->
  The mirror is a copy into a NEW root, so a destination that was legal
  in the source can be illegal in the mirror. That failure lands
  MID-COPY and leaves a partially populated tree that reads exactly like
  a complete one, which is why the check runs before the root is
  created rather than after the copy reports a count. The UNIVERSE it
  measures is every file and directory destination implied by the source
  AS ENUMERATED at pre-flight time, including tracked, untracked,
  ignored, and all `.git` content: a directory holding no files is still
  a destination, and `.git` is copied so `.git` counts. It is NOT a
  guarantee that this universe equals the one `robocopy /E` later walks.
  The enumeration finishes before the mirror root exists and the copy
  runs after it, so a path created in that window is in robocopy's
  universe and not in the measured one. The contract said "the exact
  `robocopy /E` operation" and that read as a guarantee; the mode-diff
  debate was right that it is not one. Closing the window needs
  construction from an immutable snapshot, which this release does not
  do. The ARITHMETIC is the resolved mirror-root
  length, plus a separator, plus the relative destination path length.
  The LIMIT is 260 characters as a conservative policy across both
  supported PowerShell hosts. It is a deterministic refusal threshold,
  not a claim about the maximum any host, API, OS configuration, or
  downstream client could support. Three requirements sit OUTSIDE that
  universe and bind equally. The `-OverrideOut` path is written beside
  the mirror by the tool rather than by robocopy, so the copy universe
  never covers it and it carries its own check. A source reparse point
  is REFUSED before measuring rather than measured through, because
  nothing has established that this enumerator and robocopy traverse an
  identical universe across one, and a budget computed over a universe
  the copy does not share is not a measurement of the copy. A source
  path that cannot be enumerated BLOCKS the build and is never skipped,
  the same hole semantics the manifest builder states: a path that
  cannot be measured is not a path known to fit. The refusal names the
  root length, the deepest relative destination length, their sum and
  the limit, because a refusal an operator cannot act on is a refusal
  they will work around.
  <!-- contract:end -->
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
- **BASELINE, captured after construction AND after any preflight-3 remediation, immediately before the first round is dispatched**:
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
    and any preflight-3 remediation, immediately before the first round
    is dispatched — so the two describe the same tree state. The brief
    appears in neither, because it is passed inline and never lands in
    the mirror at all.
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
