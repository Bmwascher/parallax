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
7. **A junction is a container, and recursion enters a link only when
   the link is the starting path.** Measured after cross-vendor round 1
   asked: `Test-Path -PathType Container` on a junction is true on both
   hosts, so the manifest takes the directory branch. `Get-ChildItem
   -Recurse` started at a PARENT folder listed the junction as an entry
   and returned zero files beneath it on both hosts; started AT the
   junction it returned every target file (measurement 2). A junction
   onto a folder that holds a junction back onto itself returned one
   file and no error on both hosts: the nested link is not followed. Two
   consequences. A link nested under a collapsed status subject, such as
   an ignored directory that holds a link, is NOT hashed by a plain
   recursion from that subject, on the source side today and on the
   mirror side after this change, so the manifest must start a listing
   at each nested link itself. And a cycle behind a link does not hang
   the manifest; it silently narrows it, which is why the walk keeps
   validating links it reaches THROUGH links.

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
mirror state hash. What the digest binds is CONTENT: the status fields,
each relative file name and its byte hash. It does not carry the link's
resolved target path, so a junction redirected at a byte-identical
directory is indistinguishable from the original, and that is
acceptable because the reviewer then reads the same bytes. The target
checkout's `.git/HEAD` and refs are bound only as files the expansion
reaches, which measurement 2 shows it does. Cross-vendor round 1
corrected an earlier sentence here that claimed the target path was
bound. The record prints a `links:` block naming each link's target so
a human can see it; nothing verifies against that block. The receipt
schema, the wrapper, and `-VerifyIdentity` are untouched.

**Why the link targets become protected trees.** The overlap guard
compares the mirror path and the override path against the source root
only. A link target lives outside that root, so a mirror path placed at
the reference checkout with the force switch would delete the checkout,
and an override path inside it would write there. Cross-vendor round 1
named both. After the walk records each link's resolved target, the
build refuses a mirror path or override path that equals, sits inside,
or contains any target, before anything is created or deleted.

**Why the manifest expands nested links explicitly.** Measurement 7:
a recursion from a parent does not pass through a link. The old copy
materialised every linked file, so the mirror side hashed them by
ordinary recursion while the source side never did. After this change
both sides expand a directory subject by listing its files, then
listing every directory link beneath it and starting a fresh listing at
each link, with a visited set of resolved targets so a repeated or
cyclic target is a refusal rather than an unbounded walk. Coverage on
the source side widens to match the mirror's.

**Why re-link AFTER the final back-channel sweep, then check, never
delete.** Remediation removes instruction files it finds with
`Remove-Item`, and after re-linking that path would reach through a
junction into the user's real reference checkout. So the junctions are
created after the last writer and the last sweep, and a READ-ONLY
enumeration then runs once more: any back-channel entry that sits under a
re-linked path BLOCKS the build with the entry named. The build never
deletes through a link.

**Why the path-budget walk still descends through a link, but stops
counting.** The universe is what the copy creates. With `/XJD` the copy
creates nothing beneath a link, so the link is one destination and the
entries beneath it are not measured against the budget. The walk still
DESCENDS through the link, because the cycle refusal and the
two-links-one-target refusal apply to every link the manifest can reach,
and a link behind a link is reachable (measurement 7). Cross-vendor
round 1 showed that a walk which stops at the outer link never sees an
inner cycle. Only links that are not themselves behind another link are
recorded for re-linking; an inner link already exists in the target and
is reached through the outer junction.

## What changes

- `tools/new-review-mirror.ps1`: the path-budget walk records links and
  stops counting beneath them while still validating links it reaches
  through links; a guard refuses a mirror or override path that overlaps
  any link target; `robocopy` gains `/XJD`; the manifest expansion starts
  a listing at every directory link beneath a subject; a re-link step
  runs after the final sweep; a read-only link back-channel check follows
  it; the record prints a `links:` block naming each
  `<relative path> -> <target>`.
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

- **The read cost stays.** A build hashes the reference three times
  (the source status before the copy, again after it, and the mirror
  baseline), and the old copy read it a fourth time. Each identity
  verify hashes both sides, and a round runs three verifies (the
  dispatch tool's own, then the wrapper's before and after the client),
  so a round hashes the reference six times. Cross-vendor round 1
  corrected the counts this paragraph first carried. This change removes
  the copy's read and the pre-copy budget accounting only. Item 91 holds the follow-up: a
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
