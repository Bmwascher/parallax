# Design: the review mirror's identity window

**Filed 2026-09-05.** Reported from a session running the plugin against
KitnEssentials, which hit repeated `BLOCKED: the source status changed
since construction` refusals and could not tell why.

## The measured facts

1. `Get-StatusSha256` (`tools/new-review-mirror.ps1:662`) fingerprints a
   repo as the fields of `git status --porcelain --ignored -uall -z`
   PLUS the content manifest of the paths that listing names. Not every
   path: `Get-ManifestSubject` omits a deletion-only entry, which has no
   bytes to hash.
   `Get-ContentManifest` (`:576`) expands a directory subject
   recursively, so a single `!! .claude/` status entry pulls the bytes of
   every file beneath it into the digest.
2. The content half is deliberate and the function says so: editing an
   already-ignored file leaves the status listing byte-identical, so a
   list-only digest would pass through exactly the tampering the check
   exists to catch.
3. The build-time `source_status_sha256` is re-checked at THREE points
   against the same recorded value:
   - `-Prepare` step 1a, `tools/dispatch-round.ps1:457`
   - the wrapper, before the client runs, `tools/dispatch-round.ps1:275`
   - the wrapper, after the client finishes,
     `tools/dispatch-round.ps1:310`, `throw 'the mirror changed while the
     round ran'`
4. Therefore the exposed window is **mirror build to wrapper exit**, not
   build to prepare. It spans the whole round.
5. The refusal names no path. `tools/new-review-mirror.ps1:846` prints the
   class of change and stops.
6. Nothing in `skills/` states the constraint. This repo's `CLAUDE.md`
   carries a quiet-period rule covering `-Prepare` to wrapper exit only,
   and says in its own text that no prose rule in `skills/` carries it.
   The plugin therefore does not take the rule to the repos it is
   installed into.

## What the reporting session proposed, and why it is not the fix

The report proposed fusing the mirror build and `-Prepare` into one
command. That fusion is CONSTRUCTIBLE: one script could build, read the
probe's reported override hash, generate the wrapper body from it, and
then prepare. An earlier draft of this document called it impossible,
which was wrong, and cross-vendor review of that draft said so.

It is refused on a different ground. It closes the first of three windows
and leaves the largest one open. A round that takes ten minutes still
voids if an ignored file moves while the reviewer reads. Buying the small
window at the cost of a more complex build, while the round-length window
stays exactly as it was, is not the trade this defect calls for.

The ordering the fusion would have to respect is real and worth writing
down, because it constrains any future attempt: the build runs the client
context probe, the probe writes the verified override file, and the
wrapper body embeds that file's SHA256
(`skills/multi-model-verify/SKILL.md`, the `verified-override-dispatch`
region). So the build must complete before the wrapper body can exist,
and the body must exist before `-Prepare` can install it.

The real constraint is a QUIET PERIOD over the reviewed repository, from
the build until the wrapper exits.

## Decisions

**D1. The gate does not change.** No path is removed from the digest, no
carve-out is added, and no re-mint or reseal mode is introduced. A
volatile-path allowlist was considered and rejected for this cycle: the
directories that move on their own (`.claude/`, `.codex/`) are instruction
surfaces, and excluding an instruction surface from the tamper net defeats
the check. It is recorded as an open backlog item, not built.

**D2. The refusal explains itself, advisorily.** The build writes the
SOURCE side's content manifest to a SIBLING of the mirror directory,
`<MirrorPath>.source-manifest`. On the source-status refusal path only,
`-VerifyIdentity` reads that file and names the paths whose content
changed and the paths that entered or left manifest coverage.

The advisory file is safe by construction and must stay that way:

- It is read ONLY after the comparison has already decided to block, so
  it can never turn a refusal into a pass. A missing, unreadable,
  truncated, or deliberately corrupted file changes the printed
  explanation and never the exit code.
- It is a sibling, not a child, of the mirror and lives outside the
  repository, so it enters neither `source_status_sha256` nor
  `mirror_state_sha256`.
- It pins nothing, which is why it may be a file at all. The header's
  rule that identity values are passed as arguments rather than re-read
  from a file the build wrote applies to values that PIN something; this
  one carries no authority.

**D2a. Its DESTINATION joins BOTH of the guard blocks `-OverrideOut`
already sits in, and nothing is removed until they all pass.** Cross-vendor review of the first draft found that writing to a
derived path with no guard is itself a write into an unknown file: a hard
link or symbolic link at that path would carry the write through to its
target, and a target inside the repository would be corrupted by the very
function that exists to explain a corrupted repository. The same review
found that an explicitly supplied `-OverrideOut <MirrorPath>.source-
manifest` passes today's checks and would then be overwritten, breaking
the wrapper's override hash.

The default override path is already a sibling of exactly this shape,
`<MirrorPath>.skills-override.txt`. Its protection sits in TWO places,
and round 1 of this plan's debate found that a draft claiming to copy
"the override's whole guard set" had copied only the first:

- the LEXICAL block (`tools/new-review-mirror.ps1:951-1008`): overlap
  with the repository and the mirror, pre-existence, path budget;
- the ALIAS block (`:1258-1290`): walk the path's ancestors for a
  reparse point, and check it against every followed link target.

The sidecar joins both, plus an overlap check against the override path
and against every declared `-ExtraInput`.

**The extra-input check refuses what it cannot decide.** Spelling
equality is not filesystem identity. With `C:\alias` a junction to
`C:\out`, a mirror at `C:\out\mirror` and an extra input at
`C:\alias\mirror.source-manifest`, both output paths have ordinary
ancestors and pass their own alias checks, while the extra input keeps
the alias spelling and compares unequal. `-Force` would then remove the
file that extra input names. This tool cannot establish physical identity
there, so an extra input reached through a directory link is REFUSED
rather than compared.

**Validation completes before anything is removed.** The same round found
that a draft deleting a pre-existing sidecar under `-Force` inside the
lexical block would delete it BEFORE the alias block refuses an aliased
mirror path, so a build that was going to be rejected had already
destroyed a file. The removal moves after every check.

**A root and a resolution failure are different answers.** The helper
returns one of three kinds, `ok`, `root` or `error`. A draft returned the
same null for both, so both callers announced "filesystem root".
Measured 2026-09-05: Windows PowerShell 5.1's provider accepted a
278-character absolute path that `GetFullPath` refused with
`PathTooLongException`, while PowerShell 7 accepted it, so on 5.1 a
long-path build would have reported a filesystem root and never reached
the path-budget refusal that names the real problem.

**A root is detected through the framework, not through the leaf.**
Measured 2026-09-05: `Split-Path 'C:\' -Leaf` returns `C:\`, not `C:`, so
a regex on the leaf never fires for a drive root; and
`Split-Path '\\server\share\' -Leaf` returns `share` with parent
`\\server`, which rejoined would name a DIFFERENT SHARE. The two hosts
disagree on the UNC case. So `GetPathRoot` decides, and the suffix is
appended to the full path rather than rejoined to a parent.

**Create-new bounds the final component only.** It stops an overwrite and
a link substituted at that name. It cannot defend a DIRECTORY component:
an ancestor replaced by a junction before the open redirects creation
into that junction's target, and no open flag prevents it. The alias
block is what covers ancestors. The design states that division rather
than letting create-new appear to cover both.

**D2b. The explanation states only what the comparison measures, and the
reader enforces every bound it advertises.** Two rounds of review found
overstatements here, each one an instance of the very class this cycle
exists to remove. The corrected behaviour is part of this design rather
than a detail of it:

- Manifest membership is not file existence. A deletion-only entry is
  omitted from the manifest by `Get-ManifestSubject`
  (`tools/new-review-mirror.ps1:460-463`), and a clean tracked file that
  becomes dirty ENTERS it. So the groups are named `entered manifest
  coverage` and `left manifest coverage`, never `appeared` and
  `vanished`.
- No content difference does not prove the status listing changed. A
  replaced sidecar produces the same empty result. The fallback says the
  advisory manifest did not identify the cause, and stops there.
- A malformed record is reported, never silently dropped. That requires
  CHECKING THE GRAMMAR: a draft that only rejected a missing separator
  accepted `bad.txt not-a-hash` as an ordinary record, so a truncated
  digest became a reported difference instead of an admission of
  incompleteness. The hash field is validated, and duplicates and
  over-long records are counted.
- An EMPTY line is a malformed record, with no special case. A draft
  skipped every empty string as "the trailing split artifact", which
  silently dropped leading and interior empty records too. Records are
  read with a `StringReader`, which returns nothing at all for a file
  ending in a newline, so the artifact does not exist to special-case.
  The fix removes the condition rather than refining it.
- TRUNCATION IS ITS OWN STATE, never a malformed count. A draft capped
  the record loop by incrementing the malformed counter once and
  abandoning the remainder, so 200,003 malformed records reported
  200,001 and a resource limit was reported as a grammar diagnosis. The
  reader reports truncation, and says the remainder was not examined.
- The cap applies DURING extraction. A `-split` materializes every line
  of a file whose size is someone else's choice before any later cap can
  matter, so the bound has to live in the reader that produces the
  records.
- The size limit bounds THE READ. A draft measured the file with
  `Get-Item` and then read it with a separate `ReadAllBytes`, which
  bounds nothing, and `Get-Item`'s failure is non-terminating in a script
  that never sets `$ErrorActionPreference`, so an unreadable file left
  the test unmade and carried on. One handle now measures and reads. The
  record count and record length are bounded too, because a byte limit
  alone does not bound the working set a split produces.
- Untrusted text is rendered by UNICODE CATEGORY, not by a numeric
  range. `[int]$ch -lt 32` passes the C1 controls U+0085 and U+009B,
  which are terminal escape introducers, and passes U+2028 and the
  bidirectional override U+202E. Control, Format, LineSeparator,
  ParagraphSeparator and Surrogate cover them by name, and the sidecar
  path and any exception message go through the same renderer.
- The reader does not resolve links, and the design says so rather than
  implying otherwise. Worst case it prints misleading names from an
  unrelated file, which is why every emitted comparison is introduced as
  unauthenticated and advisory, and why the refusal never depends on it.

**D3. The quiet period ships in the skill.** A contract region states it,
covering build through wrapper exit, so it travels with the plugin.

The region states the operational rule AND its measurement limits,
because a contract region that claims more than its mechanism delivers is
the defect class this whole cycle is about. Three limits, all found by
cross-vendor review of the first draft:

- The check samples endpoints. A change made and reverted inside the
  round is not detected, and no before-and-after check could detect it
  (`tools/dispatch-round.ps1:305-307` says so already).
- A tracked file that git reports CLEAN is covered by neither
  fingerprint, so a raw-byte change surviving the clean filter is not
  covered (`tools/new-review-mirror.ps1:726-731`).
- Only the THIRD comparison costs a reviewer round. The preparation check
  and the wrapper's pre-client check both run before the client is
  invoked, so tripping either wastes no quota. The first draft said a
  round that trips the rule always spends its quota for nothing, which is
  true only of the post-client check.

**D4. The build is ordered last.** `references/preflight-mirror.md` gains
a timing rule: every act that writes inside the reviewed repository
finishes before the mirror is built.

## Out of scope

- Any change to the digest's coverage (see D1).
- Item 91's cost question (the digest hashing a linked reference checkout
  repeatedly). Unrelated, already filed.
- Item 76's question about `.claude/skills` being materialised into the
  mirror. Unrelated, already filed.

## Success criteria

- An ignored-file edit between build and verify produces a refusal that
  NAMES the file, on both PowerShell hosts.
- Deleting the advisory manifest, and replacing it with invalid bytes,
  each leave the exit code unchanged. Two cases, not a universal proof:
  they establish those two states and the general property rests on the
  call site, where the explanation runs after the refusal is decided and
  its output is never read.
- A case-only rename is reported rather than collapsed.
- A record with a non-hash digest field is counted as unreadable, and a
  trailing newline is not.
- A C1 control and a bidirectional override in an advisory name reach the
  operator rendered, never raw.
- A file past the reader's limit is refused by the read itself.
- A destination collision with the override, with a declared extra input,
  or with a link ancestor is refused BEFORE anything is removed, proven
  by a test asserting the pre-existing file survives a refused build.
- A drive root and a UNC root both yield no sidecar, on both hosts.
- `test_contract_coverage.py` reports the new region locked.
- All six CI tiers and both PowerShell hosts pass.
