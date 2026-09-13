# Mirror reaper design

Written 2026-09-13 from the KitnEssentials handoff
`dev/docs/handoffs/parallax-mirror-reaper-handoff.md` (outside this
repo). Backlog item 106 holds the measurement; item 98 is the paired
defect this design closes alongside.

## The problem

Nothing in the plugin deletes a review mirror. On 2026-09-13 the drive
root held 78 `kv-*` / `kvs-*` directories totalling 13.4 GB, every one
created between 2026-09-09 and 2026-09-13 by multi-model-verify rounds:
about 3 GB per active review day. `kv-<tag>` is the review mirror the
plugin builds; `kvs-<tag>` is the drive-root clone bridge a session
builds first when the reviewed tree is a linked worktree, so the mirror
never copies a `.git` pointer file. The count also grew because the
mirror tool's existing-path refusal suggests `-Force`, and a session
that did not want to rebuild in place built `kv-<tag>-2` beside it.

## The decision on the clone bridge

The plugin never created `kvs-*` and cannot recognise one by shape. Of
the three routes the handoff named:

- The mirror tool learning a `-SourceBridge` parameter would make it
  build clones, which its own header forbids for good reason (a clone
  carries tracked files only) and would move a KitnEssentials-only
  workaround into a project-agnostic tool. Rejected.
- A prose rule in the KitnEssentials memory alone is what exists today
  for every other artifact, and the measurement above is what a prose
  rule produces. Rejected as the only mechanism.
- **Chosen:** the attestation emitter accepts the bridge as an EXPLICIT
  argument, `-ReapBridge <path>`, beside `-ReapMirror <path>`. The
  session that built the bridge names it; the plugin removes what it is
  told under the same identity guard it applies to the mirror. The
  session-side rule "pass the bridge to the emitter" belongs in the
  KitnEssentials memory that describes the bridge, and this design
  records that as the consumer's follow-up rather than doing it here.

## The reap point is the attestation

A round's `resume` re-verifies the mirror's identity, so a mirror
deleted mid-debate turns a resumable round into a transport failure.
The one terminal event the plugin already records mechanically is the
attestation, so `tools/write-attestation.ps1` is the reaper: it
validates every reap path BEFORE writing the record, writes the record,
then removes the trees. No time-based sweep exists anywhere, and the
doctor only reports.

Stated limit: a PLAN-mode debate builds the same mirror through preflight
step 3 and ends with a frozen plan, not an attestation, so its mirror has
no mechanical reap point. Its removal is the hand route the doctor names
until a plan-mode terminal event is recorded mechanically; backlog item
107 carries that residual beside the same-head one.

## The identity guard

A reap path is accepted only when ALL of these hold, checked before the
attestation is written so a refused argument costs nothing:

1. It is rooted, resolves, and is not a filesystem root.
2. It exists and is a directory.
3. Neither it nor any existing ancestor is a reparse point (the mirror
   tool's own `Test-PathOrAncestorIsLink`, moved into a shared file and
   dot-sourced by both tools rather than copied).
4. It is not equal to, inside, or containing the reviewed repository's
   top level or its git common dir (the mirror tool's own overlap
   comparisons, same spelling rule).
5. Its `.git` entry is a DIRECTORY. A `.git` FILE is a linked worktree,
   which is never a mirror or a bridge, and deleting one corrupts the
   primary's worktree list.
6. Its `HEAD` resolves to the attested head. For the mirror only, a
   HEAD whose author email is `parallax@local` and whose single parent
   is the attested head is also accepted, because that is the
   remediation commit the mirror tool makes over a tracked back-channel.
   A bridge has no such commit and must match exactly.

Rule 6 is what binds the reap to the debate that just ended: another
chat's mirror at another head is refused by name, and a bridge the
session forgot to fetch after a fix commit is refused rather than
deleted under a stale head.

## The removal

One function, `Remove-ReviewTree`, in the shared file
`tools/review-tree-removal.ps1`, used by the emitter's reap and by the
mirror tool's `-Force` rebuild (item 98). It walks the tree itself in
post-order and never recurses through a reparse point: a directory link
is removed with `[System.IO.Directory]::Delete(link)` and a file link
with `[System.IO.File]::Delete(link)`, both of which remove the link and
never its target (measured 2026-09-13 on both hosts, intact and
dangling); an ordinary file has its read-only bit cleared first,
because git objects carry it; an ordinary directory is emptied then
removed with the non-recursive `Directory.Delete`, which throws when
anything survived. Every exception terminates the removal with the
entry's path in the reason. After the walk the root is re-examined and
must be gone. The function returns `@{ Ok = $true }` or
`@{ Ok = $false; Reason = <text> }`; it never exits the caller.

The mirror's `<mirror>.source-manifest` sibling, when it exists as an
ordinary file, is removed after the mirror.

## Exit codes and messages

- Emitter: `0` written (and reaped when asked); `2` argument or repo
  error, which now includes every reap-path refusal, made before the
  record is written; `3` the attestation was written and a reap failed,
  named on stdout as `ERROR: reap failed for <path>: <reason>`, with
  the record left standing.
- Mirror tool: an existing `-MirrorPath` without `-Force` is refused
  with a message that names `write-attestation.ps1 -ReapMirror` as the
  route for a finished debate and `-Force` as the in-place rebuild for
  a live one. A `-Force` removal that fails terminates with
  `ERROR: the existing mirror could not be removed: <reason>` and exit
  `2` before anything is created or copied.

## Doctor

`/parallax:doctor` gains check 10, an inventory of directories named
`kv*` directly under the system drive root and directly under
`$env:TEMP`: count, total size, oldest `LastWriteTime`. Under 5 GB and
under 3 days old it is a NOTE (OK); at or over either threshold it is
STALE and names the reap route. It never deletes.

## Out of scope

Deleting the ten directories that exist today: two other live chats own
them. The KitnEssentials memory edit that tells the bridge builder to
pass `-ReapBridge`. Item 99 (short-name aliases).
