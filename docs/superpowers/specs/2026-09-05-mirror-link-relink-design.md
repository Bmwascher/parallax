# Review mirror: re-link directory links instead of copying through them - design

Date: 2026-09-05. Decided in conversation with the user after a
second-opinion poll of GPT-6 Astra (brief and reply retained under
`docs/superpowers/plans/rounds/2026-09-05-mirror-link-poll/`). Every
choice below is the user's or was presented and approved.

## Problem

The user's addon repos link a shared World of Warcraft API reference
checkout into their tree. Measured 2026-09-05 on this machine:

- `KitnEssentials`, `KitnUI`, `KitnUI_Lite` and `KitnVanguard` each carry
  `.wow-api-reference`, a directory SYMBOLIC LINK (not a junction) onto
  `C:\Users\Brandon\Documents\WoW-Dev\wow-api-reference`, which is its
  own git checkout holding 14,884 files. Three of the four links are
  gitignored in their parent repo.
- `tools/new-review-mirror.ps1` copies with `robocopy /E`, which walks
  through the link and writes the target's 14,884 files into the mirror
  as ordinary files. The path-budget walk before the copy also descends
  through it. The addon itself is about 14k files, so the mirror is
  built at twice the size the addon needs.

The reviewer must still be able to read the reference through the same
relative path, and the identity gate must still refuse a round when any
review input, the reference included, changes after construction.

## What was measured before deciding

All on 2026-09-05, Windows 11, Git for Windows with `core.symlinks=false`
at both system and repo scope, Windows PowerShell 5.1 and PowerShell 7.

1. **git lists the link as ONE entry.** In `KitnEssentials`,
   `git status --porcelain --ignored -uall -z` names
   `.wow-api-reference` once, with no trailing slash, out of 27,192
   entries. In a fixture, a JUNCTION onto a directory that holds its own
   `.git` is also one entry (`?? jlink/`, or `!! ign/` when ignored):
   git treats a nested repository as a single untracked path and does
   not descend. A junction onto a PLAIN folder is walked file by file,
   which is the general case for other users.
2. **Both hosts hash THROUGH the link today.** `Get-ContentManifest`
   expands a directory subject with `Get-ChildItem -Recurse -File -Force`,
   and on both hosts that call followed the symbolic link and returned
   all 14,884 files, `.git` internals included. So every source and
   mirror fingerprint already reads the whole reference, and every build
   reads it four times (status before the copy, status after, the mirror
   baseline, and the copy itself) and writes it once.
3. **`robocopy /E /XJD` skips directory links entirely.** The fixture's
   junction was absent from the destination; ordinary files copied.
4. **A junction can be created without elevation on both hosts.**
   `New-Item -ItemType Junction` succeeded under 5.1 and 7 in this
   session, while `mklink /D` (a symbolic link) was refused for lack of
   privilege. The mirror therefore re-links as a JUNCTION whatever kind
   of link the source has.
5. **A recursive delete does not reach through a junction on either
   host.** `Remove-Item -Recurse -Force` on a directory holding a
   junction removed the directory and left every file in the junction's
   target in place, on 5.1 and on 7. The `-Force` rebuild path is safe.
6. **A junction in the mirror reads as the same single entry.** After
   re-creating the junction in the `/XJD` copy, `git status` in the copy
   listed `?? jlink/`, so the manifest expands it exactly as it expands
   the source's link.

## Decision

Exclude directory links from the copy and re-create each one inside the
mirror as a junction at the same relative path onto the same resolved
absolute target. Nothing else in the identity contract changes.

**Why no new record fields.** Measurement 2 shows the existing
fingerprints already cover the reference by content on both sides, and
measurement 6 shows the mirror's own status names the junction as a
subject that the manifest expands through. A change to any reference
file after construction moves the source status hash and the mirror
state hash, and a junction redirected at different content moves the
mirror state hash. Astra's poll asked for the link path, target, HEAD and
a content hash to be bound; the link path is in the status listing, the
content is in the manifest, and the target's `.git/HEAD` and refs are
manifest entries too, so all four are already bound by the digest the
dispatch tool already carries. The receipt schema, the wrapper, and
`-VerifyIdentity` are untouched.

**Why re-link AFTER the final back-channel sweep, then check, never
delete.** Remediation removes instruction files it finds with
`Remove-Item`, and after re-linking that path would reach through a
junction into the user's real reference checkout. So the junctions are
created after the last writer and the last sweep, and a READ-ONLY
enumeration then runs once more: any back-channel entry that sits under a
re-linked path BLOCKS the build with the entry named. The build never
deletes through a link.

**Why the path-budget walk stops at a link.** The universe is what the
copy creates. With `/XJD` the copy creates nothing beneath a link, so the
walk records the link (relative path and resolved absolute target) as a
single destination and does not descend. The cycle refusal and the
two-links-one-target refusal stay, because the manifest still walks
through every link and an unbounded walk there is the same unbounded
walk.

## What changes

- `tools/new-review-mirror.ps1`: the path-budget walk collects links
  instead of descending; `robocopy` gains `/XJD`; a re-link step runs
  after the final sweep; a read-only link back-channel check follows it;
  the record prints a `links:` block naming each `<relative path> -> <target>`.
- `skills/multi-model-verify/references/backup-lane.md`: the
  `mirror-path-budget` contract region's "FOLLOWED" clause becomes the
  re-link clause. Same region id, so `DECLARED_REGIONS` is unchanged.
- `evals/multi-model-verify/test_backup_lane.py`: the region pin.
- `evals/multi-model-verify/test_review_mirror.py`: the follow-the-link
  case becomes the re-link case; new cases for drift behind the link,
  a redirected mirror link, a `-Force` rebuild leaving the target intact,
  and a back-channel behind a link blocking without deletion.
- `BACKLOG.md`: item 90 (this work), item 91 (the remaining read cost),
  item 92 (the sweep's nested-repository blind spot, pre-existing).
- `.claude-plugin/plugin.json`: 0.32.0, bumped after the diff debate.

## What does not change

- The reviewer's view: the same relative path resolves to the same
  bytes, read through the junction.
- `-VerifyIdentity`, `tools/dispatch-round.ps1`, the receipt schema, the
  wrapper template, and every `-Prepare` argument.
- File links: `/XJD` excludes directory links only, so a file symbolic
  link still copies as its target's content, exactly as today.
- The cycle and overlap refusals in the path-budget walk.

## What this does NOT fix, filed rather than hidden

- **The read cost stays.** The reference is still hashed four times per
  build and twice per verify (measurement 2). This change removes the
  write and the pre-copy descent only. Item 91 holds the follow-up: a
  nested checkout could be bound by its HEAD plus its own status hash
  instead of a byte walk that includes its `.git` objects. That is a
  change to the identity contract and is out of this scope.
- **The back-channel sweep does not see inside a nested repository**
  (measurement 1). An `AGENTS.md` inside the linked reference checkout
  is not enumerated today, with the copy, and is not enumerated after
  this change either. Item 92 records it as pre-existing.
- **Two links onto one target still refuse.** `KitnEssentials` carried a
  second `.wow-api-reference` under `.superpowers/worktrees/...` on
  2026-09-05, which the walk refuses as "links overlap". This change
  keeps that refusal; the timing task reports if it fires.

## Rejected options

- **Name the target path in the brief, no link in the mirror.** Not
  self-contained, and nothing pins which reference the reviewer read.
- **Exclude reference subfolders by list.** Fragile; every new folder
  needs an edit.
- **A shared, sanitized reference snapshot keyed by content** (Astra's
  alternative). Safer against the sweep, but a second copy of the
  reference on disk and a second directory to manage; the sweep risk is
  closed by ordering instead.
- **Re-create the source's link kind.** A symbolic link needs a
  privilege this session does not hold (measurement 4). A junction is
  read identically and needs none.
