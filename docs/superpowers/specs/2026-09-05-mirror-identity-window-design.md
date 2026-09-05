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
command. That is refused on two grounds:

- It closes the first of three windows and leaves the largest one open. A
  round that takes ten minutes still voids if an ignored file moves while
  the reviewer reads.
- It is not constructible. The build runs the client context probe, the
  probe writes the verified override file, and the wrapper body embeds
  that file's SHA256 (`skills/multi-model-verify/SKILL.md`, the
  `verified-override-dispatch` region). The build must finish before the
  wrapper body can exist, and the wrapper body must exist before
  `-Prepare` can install it.

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

**D3. The quiet period ships in the skill.** A contract region states it,
covering build through wrapper exit, so it travels with the plugin.

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
