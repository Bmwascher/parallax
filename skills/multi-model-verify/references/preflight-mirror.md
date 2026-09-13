# Preflight: building the review mirror

Construction detail for SKILL.md's preflight item 3, "build the review
mirror" step. This is read only when the enumeration there actually found
an `AGENTS.md`, `.agents/*`, or `.kimi-code/*` entry and
SKILL.md's back-channel-auto-mirror requires the mirror — the operational
imperative and the do-not-ask rule stay in SKILL.md itself; this is the
how, not the whether.

Run
`tools/new-review-mirror.ps1 -RepoRoot <repo> -MirrorPath <scratch>`.
Build at a SHORT `<scratch>` directly under the temp directory, such
as a `kerev<n>` folder, never inside the session scratchpad: the
mirror re-roots every path, and the tool refuses before creating
anything when the budget is blown. That location is the
`Canonical review mirror root` row of references/model-prompting-notes.md's
round-artifact-roots declaration, fixed there because the tool refuses a
mirror inside the reviewed repository.
It builds the **review mirror** (references/backup-lane.md owns its
construction, its baseline, and its identity fields — a file copy
preserving `.git`, NOT a clone), deletes the offending entries THERE,
commits when any were tracked, re-runs the enumeration from SKILL.md's
preflight item 3 inside the mirror, captures the baseline and the
content manifest, runs the client probe from that same preflight step
with the mirror as the working directory, and prints the record block;
empty enumeration output is the evidence, and the mirror's identity
fields go in the debate record. The mirror is then the reviewed tree for
every lane in that debate — dispatch codex with the mirror as cwd, and
keep citations resolvable in the real repo. Whether the removal needs a
commit branches on tracked-ness, and the difference misreads as a
failure; references/backup-lane.md states that branch and the hook
behaviour that comes with it.

Files above the repo's git root are NOT ingested (same probe), and
`~/.codex/AGENTS.md` is the user's own
global instruction file — note it in the debate record if it exists,
but it is not a stop.

## The quiet period

<!-- contract:start id=mirror-quiet-period -->
NOTHING MAY WRITE INSIDE THE REVIEWED REPOSITORY from the moment the
mirror is built until the wrapper exits. The identity digest covers the
fields of `git status --porcelain --ignored` PLUS the content of the
paths that listing names, ignored ones included, with a directory
expanded to its files and a deletion-only entry contributing no bytes.
So a test-cache write, a plan-ledger append, a drift report or one new
untracked file is enough. The same recorded digest is compared against
the live source three times: at preparation, before the client runs,
and after it finishes. The last of those spans the whole round, so this
is a quiet period and not an ordering rule. Only that last one costs a
reviewer round; the two before it refuse before the client is invoked
and spend no quota. State the limits with the rule: the comparison
samples endpoints, so a change made and reverted inside the round is
not detected, and a tracked file git reports CLEAN is covered by
neither fingerprint. Queue every edit until the wrapper exits, however
small and however unrelated it looks.
<!-- contract:end -->

## Timing

BUILD THE MIRROR LAST. Every act that writes inside the reviewed
repository finishes first: the gates, the plan ledger, the scratch notes,
the formatter. From the build until the round's wrapper exits, the
repository is quiet, and preflight-mirror.md's mirror-quiet-period states
why. The identity digest covers the content of ignored paths, so a
pytest cache directory or a ledger append is enough to refuse the
dispatch.

A build that has gone stale is not repaired and cannot be re-blessed:
there is deliberately no re-mint or reseal mode. READ THE EXPLANATION
FIRST, then build again. Rebuilding replaces the evidence of what
changed, so a rebuild before reading turns a diagnosable refusal into an
unexplained one. The rebuild itself is cheap next to a spent round,
measured at about 92 seconds on a repo carrying a linked reference
checkout.

When a refusal names `the source status changed since construction`, the
lines beneath it name the paths whose content changed and the paths that
entered or left manifest coverage, read from the `source_manifest` file
the record block points at. That explanation is advisory: it can be
missing, incomplete or wrong, and the refusal stands either way.
Manifest coverage is not file existence, so a path listed as leaving
coverage has not necessarily been deleted.

The two refusals raised by the round wrapper itself print no explanation
to the console. The wrapper redirects both identity checks into
`mirror.verify` inside its dispatch directory and then throws a short
message, so that file is where the detail is.

## End of life

The attestation is the reap point. A round's `resume` re-verifies the
mirror's identity, so a mirror deleted mid-debate turns a resumable
round into a transport failure; the one terminal event the plugin
records mechanically is the attestation, so `tools/write-attestation.ps1`
removes the mirror when it is passed as `-ReapMirror <path>`, and the
clone bridge a linked worktree needed when it is passed as
`-ReapBridge <path>`. The reap is bound to that event and never an age:
no sweep exists, and the doctor only reports.

The emitter validates both paths BEFORE it writes the record, so a wrong
argument is refused at exit 2 with nothing written, and removes them
AFTER, so a removal that fails leaves the verdict standing and exits 3
naming the entry that stopped it. A path is accepted only when it
exists as a directory not reached through a link, does not overlap the
reviewed repository or its git common dir, holds a `.git` DIRECTORY
(a `.git` FILE marks a linked worktree, never a mirror or a bridge), and
its HEAD is the attested head. The mirror may instead sit exactly one
`parallax@local` remediation commit above that head, because that is the
commit construction makes over a tracked back-channel; the bridge must
match exactly, so a bridge left unfetched after a fix commit is refused
rather than deleted under a stale head. Measured 2026-09-13: 78 mirror
and bridge directories, 13.4 GB, in four review days, with nothing but
memory saying which of them a live chat could still resume. Another
chat's mirror is at another head and is refused by name.

The removal never recurses through a link: `tools/review-tree-removal.ps1`
walks the tree itself, removes each link as a link, clears the read-only
bit git puts on its objects, and re-examines the root afterwards. The
mirror tool's `-Force` rebuild uses the same function, which is what
closed backlog item 98.

An existing `-MirrorPath` without `-Force` is refused with the reap
route named. Build `kv-<tag>-2` beside a finished debate's mirror and
the count grows by one for every debate; reap the finished one instead,
and rebuild in place with `-Force` only for a debate that is still
running, because a resumed round needs the mirror at the path its
identity was recorded at.

The bridge is the session's. The plugin never created it and cannot
recognise one by shape, so the session that built it names it; the rule
"pass the bridge to the emitter" belongs beside the rule that builds it.
