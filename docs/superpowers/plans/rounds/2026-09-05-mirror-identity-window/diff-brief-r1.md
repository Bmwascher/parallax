# Mode-diff debate, round 1: the review mirror's identity window

You are the cross-vendor reviewer in a two-advisor adversarial debate. We
carry equal weight. Your job is to REFUTE, not to ratify. A round that
finds nothing is a round that cost quota for nothing, so look hard, but
do not manufacture findings either: say "I found nothing in area X" where
that is the honest answer.

## The strike rule, which binds both of us

Every claim cites a path and line you actually read this session. A claim
without a citation is STRUCK from the record, however plausible it
sounds. This applies to my claims below as much as to yours: if I assert
something and you check it and I am wrong, say so plainly and cite what
you read.

If you find yourself reasoning about what a file "probably" contains,
stop and open it.

## The range

Base `0f485cca16487ff83eee7529787bd9bf3049c66c`, head
`79ab77f53c964e81253ebcdb6d4b5b9933a2177a`, on branch
`mirror-identity-window`. The code diff is about 1,476 insertions across
ten files. `git diff 0f485cc..79ab77f` in your working directory shows it
all; the bulk of the branch's raw line count is Astra round transcripts
under `docs/superpowers/plans/rounds/`, which you can ignore unless you
want to check a claim about what an earlier round said.

## The defect this branch fixes

A session running this plugin against a DIFFERENT repository hit repeated
`BLOCKED: the source status changed since construction` refusals and
could not tell why. The cause: the review mirror's identity digest covers
ignored working state - `.claude/`, `.codex/`, `dev/docs/` - which moves
on its own between the build and the round's end. The refusal named the
CLASS of change and stopped, so the session could not distinguish a cache
write from a planted file.

That session's proposed fix was "build and prepare in one command". I
refused it and the design says why: fusing the two is CONSTRUCTIBLE, but
it closes only the build-to-prepare gap and leaves the round-length
window - the larger one - wide open.

## What shipped instead, in three parts

1. **The build writes a source content manifest** to a sidecar beside the
   mirror directory, `<mirror path>.source-manifest`, under the same
   destination guards `-OverrideOut` already carried.
   `tools/new-review-mirror.ps1`.

2. **The refusal reads that sidecar** and names what ENTERED manifest
   coverage, LEFT it, or CHANGED content. Same file,
   `Write-SourceDriftExplanation` and `Get-ManifestDrift`.

3. **The skill states the quiet period**: a new `mirror-quiet-period`
   contract region and a `BUILD THE MIRROR LAST` timing rule, in
   `skills/multi-model-verify/references/preflight-mirror.md`.

The identity GATE is deliberately unchanged. The sidecar is ADVISORY: it
is read only after the comparison has already decided to block.

## My position, which you should try to break

**Claim 1: no state of the sidecar can change a verdict.** The file sits
OUTSIDE the mirror and nothing hashes it, so treat it as attacker
controlled. I claim that absent, malformed, truncated, oversized, and
hostile-but-well-formed all produce the same exit code as before, and
that a clean verify never opens it at all.

**Claim 2: no refusal deletes before it decides.** Task 1 added
construction-time refusals that exit 2 for destinations the build
previously accepted: a pre-existing sidecar, a sidecar under a directory
link, an extra input colliding with it, a root mirror path, and a
trailing dot or space on a path component. I claim every lexical and
alias check runs before the single `Remove-Item`, so a build heading for
a refusal deletes nothing.

**Claim 3: every untrusted string reaches the terminal through
`Format-AdvisoryName`**, which escapes by Unicode CATEGORY rather than by
numeric range, and bounds its OUTPUT at 200 characters including the
truncation marker.

**Claim 4: the record is honest.** Several plan defects were found by
executing the plan rather than reading it, and are written up in
`docs/superpowers/plans/rounds/2026-09-05-mirror-identity-window/README.md`
and `gate-results.md`.

## Where I am weakest, stated rather than hidden

I would rather you spend your effort here than rediscover what I already
know.

- **The quiet period cannot be enforced.** It is prose in a reference
  file. Nothing checks it, and it cannot bind a SECOND session writing to
  the same repository. During this very debate, a concurrent session
  modified two files mid-round and voided it.
- **The behavioural eval suite was NOT run.** Skill text changed in Task
  3, so it applies. The user chose to keep the quota for this debate.
  `gate-results.md` records it as a deliberate gap. If you think that
  invalidates a claim I make, say so.
- **There is no SDD ledger for this branch.** I dispatched implementer
  subagents directly instead. So there is no per-task artifact to check
  the work against beyond the commits and the tests.
- **Four separate backslash-doubling incidents** occurred on this branch,
  the last found by the whole-branch review: `Format-AdvisoryName` built
  its escape as a doubled `\\u` in PowerShell, where backslash is not an
  escape character, so it emitted two. Tests passed either way. If a
  fifth instance is still in the tree, I want to know.
- **Item 93's twelvefold PowerShell 7 slowdown did not reproduce.** I
  measured 1.08, 1.13 and 1.15 across three trees and amended the item
  rather than closing it. Check whether my amendment overstates what I
  measured.

## What I want from you

Go after Claims 1 through 4 in that order of value. Concretely:

1. Trace every path by which the sidecar's CONTENT can influence control
   flow. If any state of that file can change an exit code, turn a block
   into a pass, or crash the verify in a way that reads as something
   other than a block, that is the finding of the round.
2. Check the refusal ORDERING against the actual statement order in the
   file, not against my description of it.
3. Attack `Format-AdvisoryName`: can anything reach the terminal
   unescaped, can the 200-character bound be exceeded, is the category
   set wrong in either direction?
4. Check the record against the diff. If a write-up claims something the
   code does not do, say which line of which document.

Then, and this matters as much: sweep for OTHER INSTANCES OF THE SAME
DEFECT CLASSES. Not the specific bugs above - the classes. An unmeasured
premise stated as fact. A test oracle that cannot fail. A count computed
inside the document that holds the things counted. A comment that claims
more than the code does. Report instances or an explicit "none found",
and say what shapes you searched for so I can tell what your sweep could
not have seen.

## Output

Number your findings. For each: the claim, the file and line, why it is
wrong, and what you would change. Mark each CONFIRMED (you read the code
and it is definitely wrong) or SUSPECTED (it looks wrong and here is the
check you could not complete). End with a verdict: PASS, FIX, or
ESCALATE, and one sentence saying what the verdict rests on.
