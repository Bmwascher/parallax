# Design: the review mirror's identity window

**Filed 2026-09-05.** Reported from a session running the plugin against
KitnEssentials, which hit repeated `BLOCKED: the source status changed
since construction` refusals and could not tell why.

## The measured facts

1. `Get-StatusSha256` (`tools/new-review-mirror.ps1:662`) fingerprints a
   repo as `git status --porcelain --ignored -uall -z` PLUS the content
   manifest of every path that listing names.
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
`-VerifyIdentity` reads that file and names the paths that appeared,
vanished, or changed content.

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

**D2a. Its DESTINATION carries the same guards `-OverrideOut` already
carries.** Cross-vendor review of the first draft found that writing to a
derived path with no guard is itself a write into an unknown file: a hard
link or symbolic link at that path would carry the write through to its
target, and a target inside the repository would be corrupted by the very
function that exists to explain a corrupted repository. The same review
found that an explicitly supplied `-OverrideOut <MirrorPath>.source-
manifest` passes today's checks and would then be overwritten, breaking
the wrapper's override hash.

The default override path is already a sibling of exactly this shape,
`<MirrorPath>.skills-override.txt` (`tools/new-review-mirror.ps1:956-973`),
and it is guarded for overlap with the repository and the mirror, for
pre-existence, and for the path budget. The sidecar takes the identical
guard set, plus an overlap check against the override path itself, plus a
refusal of a root-shaped mirror path such as `D:\`, which would otherwise
derive the drive-relative `D:.source-manifest`. The write itself uses
create-new semantics so that a file appearing between the guard and the
write cannot be clobbered either.

**D2b. The explanation states only what the comparison measures.** The
same review found three overstatements in the first draft, and the
corrected wording is part of this design rather than a detail of it:

- Manifest membership is not file existence. A deletion-only entry is
  omitted from the manifest by `Get-ManifestSubject`
  (`tools/new-review-mirror.ps1:460-463`), and a clean tracked file that
  becomes dirty ENTERS it. So the groups are named `entered coverage` and
  `left coverage`, never `appeared` and `vanished`.
- No content difference does not prove the status listing changed. A
  replaced sidecar produces the same empty result. The fallback says the
  advisory manifest did not identify the cause, and stops there.
- A malformed record is reported, never silently dropped, because a
  dropped record is a difference the explanation would then fail to
  mention.

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
- Deleting or corrupting the advisory manifest changes no exit code in
  any case, proven by test.
- `test_contract_coverage.py` reports the new region locked.
- All six CI tiers and both PowerShell hosts pass.
