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
anything when the budget is blown.
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
