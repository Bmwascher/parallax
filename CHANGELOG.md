# Changelog

This file has one section for each plugin version, newest first. Write
each section for the person who uses the plugin and must decide if they
update, not for the person who maintains it. Each section starts with
`## vX.Y.Z (YYYY-MM-DD)`, and the newest one must name the version in
`.claude-plugin/plugin.json`.

Open each section with a lead paragraph in plain words that says what
changed for the user and what they must do. The lead paragraph has no
code, no file name and no link; the checker refuses those. Put the
maintainer detail, the file names and the records under a later title.
End each section with a `### Backlog` title and one bold line that names
the backlog items that the version closes.

Write each section in ASD-STE100 Simplified Technical English.
`evals/tools/ste_lint.py` refuses these shapes, which STE forbids:

- a sentence of more than 25 words
- a paragraph of more than 6 sentences
- the passive voice
- an "-ing" verb form
- a contraction
- an unapproved modal
- an unapproved word on its list

The STE dictionary is not in this repository. The writer keeps the other
rules by hand. Use one approved meaning for each word, no noun cluster of
more than three nouns, and one topic for each sentence. Technical names
go in backticks. `evals/tools/ste_allow.txt` lists the technical names
that the checker must not question.

`evals/tools/check_changelog.py` runs both checks in CI, and the release
workflow publishes the section as the release page. A version bump with
no section fails on the branch, and a release never ships blank. Write
the section in the same commit as the version bump, after the diff
debate. Cite backlog items and round records, not commits, because a
reader can follow a record. Versions before 0.34.0 have no section and
no release; their records are the merge commits on main.

## v0.39.0 (2026-09-14)

The plugin no longer ships the Claude implementer that typed frozen-plan
tasks directly, because a session picked it for 122 of 128 builds. When
the Flash lane blocks a task and you agree to a reroute, the task goes
to the escalation lane with an empty envelope. A task the plan sends to
that lane now carries a lane field in its text. The plugin warns you
when a build dispatch goes to another implementer without that field.
Update the plugin and restart the session, because a hook and the agent
set changed.

### What changed for you

- **The plugin deletes the direct Claude implementer.** A plan that
  still names it fails at dispatch, and the warning names the two
  routes that remain.
- **A consented reroute is zero-judgment.** The escalation lane accepts
  a task the Flash lane blocked with an empty envelope. Any decision
  entry on an empty envelope is drift, and the diff debate fails it.
- **The lane field.** A task the plan routes to the escalation lane
  carries `**Lane:** parallax:escalation-implementer` on one line. A
  consented reroute carries the ledger's line with the ledger path. The
  hook reads that field and stays silent when it names the dispatched
  agent.
- **The hook warns on every other implementer dispatch.** The warning
  names the agent, the build lane, and the field that silences it. It
  fires on the failure event too, so a stale plan sees it.

### Details for maintainers

- This version deletes `agents/implementer.md`.
  `agents/escalation-implementer.md` carries the shared-contract block
  and is the parity twin in `test_flash_implementer.py`. Its entry
  route 2 states the empty envelope and names the ledger's lane line.
- `references/frozen-plan-format.md` names the two routes away from the
  Flash lane, the lane field, and the empty-envelope rule.
- `hooks/superpowers-review-companion.ps1` checks `subagent_type` ahead
  of the reviewer fingerprint. Six new hook cases drive it under pwsh;
  `run_hook` returns raw stdout, so a silent case means empty output.
- The vendor-swap note moved into `agents/flash-implementer.md`. The
  Flash model literal has two homes: that file and its test.
- Record: `docs/superpowers/plans/2026-09-13-single-implementer.md`
  and its rounds root. Astra plan debate two rounds, Astra diff debate
  two rounds, both FULL. The plan's debate record holds the Fable
  review's two accepted findings as post-freeze amendments.
- Every build task went through the Flash lane. The Gemini weekly
  figure moved from 98 percent to 97 percent across the build. Task 1's
  first pass lost every inline comment and the wrapper's checks did not
  see it; backlog item 111 records that gap.
- Backlog item 110 is closed. Item 111 is new.

## v0.38.1 (2026-09-13)

The doctor now reads the Flash lane's quota. Before this version, the
doctor said that the quota was opaque. A person who watched the Gemini
usage page saw nothing move, because the Antigravity CLI keeps its own
pools. Run the doctor to see the percent that remains in each
pool and the time it resets. If the weekly Gemini figure does not move
across a build, the build did not go through Flash.

### What changed for you

- **Check 7b reads the quota.** The doctor runs the `/usage` slash
  command through print mode. The answer arrives in about one second,
  with no model call. It has four rows: the Gemini pool and the Claude
  and GPT pool, each with a weekly and a five-hour limit. The row is
  best effort, like 4b: an absent answer is N/A and never BROKEN.
- **Run it from PowerShell.** Git Bash rewrites the argument `/usage`
  to a path under its own install folder before the client sees it. The
  model then lists a directory. The doctor says so.

### Details for maintainers

- Measured 2026-09-13 on agy 1.2.2. The log line is `Print mode:
  running slash command /usage`, and no `sending message` line follows.
- `test_multi_model_verify.py` pins the section, the PowerShell form,
  the MSYS trap, and the N/A rule. It also pins that check 7 no longer
  calls the quota opaque.
- Backlog item 11 corrects its sentence about the quota in place.

## v0.38.0 (2026-09-13)

The Flash implementer is now the declared build lane for every task in a
frozen plan, and a Sonnet wrapper supervises it. Before this version,
both implementer agents described the same job, so a build session
picked the Claude lane and never touched Flash. You do not need to
change anything. When you start a build, dispatch the Flash lane for
each task, and put the build lane on the plan header.

### What changed for you

- **The Flash lane is the default by name.** The description of
  `agents/flash-implementer.md` now opens with the rule that it is the
  build lane for every frozen-plan task. The description of
  `agents/implementer.md` now says that it is never the default. Two
  cases route a task to it. The plan routes the task there by name, or
  the Flash lane blocked the task and the user agreed to reroute it.
- **The plan header names the lane.** A frozen plan now carries the
  line `Build lane: parallax:flash-implementer`. A task report with no
  `ROUTE:` line is a lane violation, unless the plan or a recorded
  consent routed that task elsewhere. Only the Flash lane writes one.
- **Sonnet supervises the Flash lane.** The wrapper seat moved from
  Haiku to Sonnet. Every control in that lane is a prose rule that the
  wrapper follows. The Antigravity CLI print mode changed between 1.1.7
  and 1.2.x, and 1.2.2 does not consult the trust list. The agent file
  and backlog item 105 record both. The seat must block on a lost log line
  and not explain a landed edit away.

### Details for maintainers

- `test_flash_implementer.py` pins the Sonnet seat, the two descriptions
  and the plan-format rule.
- The lane rule lives in `references/frozen-plan-format.md`, next to the
  escalation-lane envelope rule.
- The measurement: on 2026-09-13 a build session, told to use the
  parallax implementers, dispatched `parallax:implementer` four times
  and the Flash lane never. The newest Flash transcript on the machine
  was sixteen hours old.
- Backlog item 109 holds the record. Item 110, ranked first, retires the
  second implementer file and adds a hook that sees a dispatch to the
  wrong lane.

## v0.37.0 (2026-09-13)

The plugin now builds every review mirror under one short, fixed folder
on the drive. It refuses to remove a mirror from any other place.
Before this version, the canonical place was the temp folder. That long
path did not fit the review packets of a large project, so sessions
built mirrors on the drive root instead. Build each new mirror and each
clone bridge under the new folder.

A mirror that you built in the old places stays where it is, and the
attestation tool does not remove it; remove it by hand. The doctor now
counts the mirrors in the new folder and keeps a note about the old
places until they are empty.

### What changed for you

- **One declared parent for review mirrors.** The `Canonical review
  mirror root` row now reads `C:/pxm/<short-name>/`. Build a mirror at
  `C:/pxm/<tag>` and a clone bridge at `C:/pxm/kvs-<tag>`. The row is a
  declaration and not a computed value; a machine with a different
  system drive edits the row.
- **A check before the build.** `tools/artifact-roots.ps1 -RepoRoot <repo>
  -Assert <mirror-path> -Expect reviewMirror` answers 0 for a path under
  the parent and 1 for a path outside it. The parent itself answers 1,
  because the parent is never a mirror.
- **The attestation tool refuses a tree outside the parent.** The rule
  is the last rule of its identity guard, and it applies to the mirror
  and to the bridge. A refusal exits 2 and writes nothing.
- **The tool refuses an empty reap argument.** Before this version, an
  explicitly empty `-ReapMirror ""` or `-ReapBridge ""` wrote the
  attestation and removed nothing, with no message. The tool now refuses
  an empty value before it writes the record.
- **The doctor inventories the parent.** Check 10 of `/parallax:doctor`
  counts the directories under `C:/pxm`, with their size and age, and
  marks them STALE at 5 GB or 3 days. A second line still counts the
  `kv*` directories on the drive root and in the temp folder as a note,
  until that line finds nothing. The doctor never deletes.

### Details for maintainers

- `tools/artifact-roots.ps1` no longer substitutes the temp folder, and
  the sweep in `test_artifact_roots.py` refuses the old `<TEMP>` form
  anywhere on the plugin surface. A second test binds every `pxm`
  example in the prose and the doctor to the declared row.
- `tools/write-attestation.ps1` reads the parent through
  `tools/artifact-roots.ps1` in the same process, never from a literal
  of its own. Each failure to read the parent exits 2 with nothing
  written. The tool tests each reap parameter for presence, not for a
  non-empty value.
- `test_mirror_reaper.py` builds each successful reap under a fresh
  `C:/pxm/t-<8 hex>` directory and removes it afterwards. Each refusal
  keeps its tree in the pytest temp directory, which proves that the
  parent rule runs last.
- The skill reference files spell the parent with forward slashes, because
  those files must not contain a backslash. The doctor spells it
  `C:\pxm`.
- The record is `docs/superpowers/plans/rounds/2026-09-13-mirror-parent/`,
  which retains the Fable review of the full branch and the Astra diff
  rounds. The Fable review found the notes' own command without its
  repository argument. The session's gate found backslashes in the skill
  references. Astra round 1 found the empty reap argument.
- Item 107 records follow-up 2 as decided and keeps follow-ups 1 and 3
  open. Item 108 records the same empty-argument shape on
  `-CheckpointFile`, which is outside this version's certification unit.

### Backlog

**This version closes follow-up 2 of item 107 and opens item 108.**

## v0.36.0 (2026-09-13)

The plugin now removes a review mirror when the review that used it
ends. Before this version, the plugin never removed a mirror, and one
review week left more than ten gigabytes of copies on the drive. You do
not have to change anything when you update. When you write the
attestation for a finished review, you can name the mirror and its clone
bridge, and the plugin removes both. The doctor now lists the mirrors
that are on the drive and tells you when they are old or large.

### What changed for you

- **A finished review removes its own mirror.** `tools/write-attestation.ps1`
  accepts `-ReapMirror` and `-ReapBridge`. It writes the attestation
  first, reads the record back, and then removes the two trees. If the
  record is not on disk, the tool removes nothing.
- **The tool refuses the wrong tree.** A tree must be at the attested
  head and must have a real `.git` directory. It must not be the
  reviewed repository, and its path must not go through a link. A tree
  that fails one of these rules stays, and the message names the rule.
- **A failed removal is loud.** The tool exits 3, names the tree, and
  tells you that it did not touch the bridge. The attestation stays.
- **The doctor shows the mirror inventory.** Check 10 of
  `/parallax:doctor` counts the `kv*` directories on the drive root and
  in the temp folder. It shows their size and age, and it marks them
  STALE at 5 GB or 3 days. It never deletes.
- **A mirror build no longer copies over a stale tree.** The build
  removes the old mirror with the same checked function and stops if
  the removal fails.

### Details for maintainers

- `tools/review-tree-removal.ps1` is the one removal function. It walks
  the tree in post-order and deletes a link as a link, never through it.
  It clears the read-only attribute on files and directories, and it
  reads the root back after the delete. `tools/new-review-mirror.ps1` and the
  emitter dot-source it.
- The emitter writes the record with `-LiteralPath`, then compares the
  bytes on disk with the serialized text with an ordinal comparison. A
  wildcard in a repository name and a case difference in the read-back
  both exit 2 with nothing removed.
- The emitter removes the sidecar `<mirror>.source-manifest` only when
  it is an ordinary file. An inspection error and a sidecar that survives the
  delete both exit 3.
- `test_mirror_reaper.py` drives real junctions, held handles, read-only
  trees, a bracketed repository name and a foreign clone at the attested
  head, on both PowerShell hosts.
- The record is `docs/superpowers/plans/rounds/2026-09-13-mirror-reaper/`,
  which retains four diff-debate rounds and the Fable review of the full
  branch. Round 1 found the wildcard write, round 2 found the
  case-insensitive comparison, and round 3 found one stale item number.
- Item 107 records the residuals. The guard cannot tell two trees at
  the same head apart. A plan-mode debate has no mechanical reap point.
  No test drives the post-delete sidecar read-back. The mirror parent is
  still the drive root.

### Backlog

**This version closes items 98 and 106.**

## v0.35.0 (2026-09-13)

The Flash implementer lane can write files again. Since Antigravity CLI
1.1.28, the lane refused each task because the client denied each file
edit in headless mode. The lane now asks the client for its edit mode on
each dispatch, and the client applies the edits. The client still denies
each command, and the wrapper runs all verification itself. Update the
Antigravity CLI to 1.2.2 or later, and approve trust for your worktrees
folder once in an interactive session. You do not have to change a
setting.

### What changed for you

- **The lane writes files under the client's own edit mode.** The dispatch
  line carries `--mode accept-edits`. Without the flag, the client denied
  the lane's edit on 1.2.0 and on 1.2.2. With the flag, the edit landed and
  a command call stayed denied. The flag adds no rule to the client's
  settings file.
- **One trust entry for a folder of worktrees is sufficient.** The wrapper
  accepts a workspace when the trust list holds the workspace or a parent
  folder of it. Approve the parent folder once, and each worktree under it
  can run.
- **The trust list is the lane's own limit, not the client's.** Measured
  on 1.2.2, the client wrote the edit in a folder with no trust entry, with
  `allowNonWorkspaceAccess` at `true` and again at `false`. The wrapper's
  preflight is what keeps Flash inside a folder you trust. Backlog item
  105 holds the open work for a mechanical guard.
- **The authorship check reads the correct log line.** The startup line of
  the client log carries an empty conversation id on 1.2.0 and on 1.2.2.
  The wrapper now reads the id from the line that carries it. A good run
  no longer fails as a run with no transcript.
- **The `allowNonWorkspaceAccess` setting is not necessary.** The client
  removed a `false` value from the settings file on its own. The doctor and
  the drift watch report the value as information only.

### Details for maintainers

- `agents/flash-implementer.md` carries each measurement with its date and
  client version. The pins in `test_flash_implementer.py` lock the dispatch
  line as one fragment, the carve-out sentence, the ancestor comparison
  rule and the route checks.
- `commands/doctor.md` check 7 and the three agy strings in
  `tools/check-drift.ps1` state the same fact about the trust list.
- The 0.12.0 design spec has three dated corrections at the sentences that
  said the flag does not apply in print mode.
- The record is
  `docs/superpowers/plans/rounds/2026-09-13-flash-accept-edits/`, which
  retains the Fable review, one Astra round and the three probe logs. The
  Astra round found six of ten claims wider than their evidence. Each
  sentence now describes only the edit that the session measured.

### Backlog

**This version closes item 36 and opens item 105.**

## v0.34.0 (2026-09-13)

The plugin now keeps all the files that a review writes in one folder
for each project. Before this version, those files went to three
different folders, and it was hard to find a review or to clean up. You
do not have to change anything when you update. New reviews go to the
one folder, and old files stay where they are.

### What changed for you

- **One folder for each project.** A review writes its debate rounds,
  its ledger and its review mirror under one root. The skill declares
  that root in one place, and each tool reads that one declaration.
- **A tool shows you where the files are.** `tools/artifact-roots.ps1`
  prints the folders that a review uses in your project. It also refuses
  to copy a file to the wrong folder.
- **The same result on both PowerShell versions.** The tool gives the
  same exit code for the same error on Windows PowerShell 5.1 and on
  PowerShell 7. Before, the two versions gave different codes for the
  same mistake.

### Details for maintainers

- The declaration is one contract region of
  `references/model-prompting-notes.md`, and `tools/artifact-roots.ps1`
  is its only reader. `-Assert` answers if a path is inside the retained
  root that a retention copy expects.
- The resolver has no `param` block and parses its own command line,
  because typed binding did not give one exit map. A parameter with no
  value exited 1 from `-File` binding, and `-Json:$true` exited 1 on
  Windows PowerShell 5.1 and 0 on PowerShell 7. Each command-line fault
  now exits 2 on both hosts, and an empty inline value is a fault, not a
  default.
- `test_artifact_roots.py` runs the three round writers in a disposable
  repository on both hosts. It also sweeps the skill for a root that a
  sentence names by hand and not through the declaration.
- The record for item 100 is
  `docs/superpowers/plans/rounds/2026-09-12-artifact-roots/`, which
  retains five diff-debate rounds and the Fable review of the full
  branch. A write into the reviewed tree during round 2 voided that
  round.

### Backlog

**This version closes item 100.**
