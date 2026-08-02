Round 34. **The live gate passes on BOTH hosts with ZERO skipped.** Task 7's
step 2 is satisfied. Tasks 8, 9 and 11 are built, and Task 10 is done except
its last step, which the user has decided against on evidence I did not have
when the plan froze it.

Commits: Task 8 `89bcab4`, Task 9 `ac6e6d8`, Task 7 finished `480d210`, Task 10
partial `4fd5b23`. Task 11 shipped earlier at `a5e3b83`.

## Task 7: measurement 5 finally has evidence

```
powershell.exe: 63 passed in 166.90s
pwsh.exe:       63 passed in 137.01s
```

Zero skipped, zero failed, both modules collected, on both hosts.

Your five-step oracle worked. Step 4 carries its own instruction — either
success REFUTES measurement 5 and that is a finding, not a test to fix — and it
failed on both runs on both hosts. So an absolute `oauth.key` genuinely does not
resolve, and we now know it rather than assuming it. The old oracle had asserted
that for months without being able to observe it.

The probe record and every piece of its machinery are gone: zero references in
all three modules. The seven oracles missing from the partial commit are
written — four locking the metadata exclusion, including the one proving it can
never become an allowlist, and three locking the strict decode.

## Task 8, 9, 11: built, and two things I want on the record

**Task 8.** Fifteen pins from the implementer, all verified. The pinned recovery
command is byte-identical to the plan's frozen line AND to the builder's stored
template, 1589 characters each, and the doctor emits it verbatim.

I added two the implementer missed. The plan asks for two fixtures proving the
acceptance boundary in BOTH directions and only presence was asserted, with no
mutation. Each of four new mutations was shown to bite: remove the exit-0
requirement, soften the unmeasured case to `N/A`, map `absent` to `BROKEN`, or
hash an absent credential, and the pin stops matching.

**Task 9, and a conflict the plan did not anticipate.** You told me at step 3
that the region id `lane-lock` is REUSED and to amend the comment so it does not
read as narrating this region's deletion. Done. But there was a second instance
of the same collision one layer down, and it failed the suite:

`test_deleted_machinery_does_not_return` asserted the string
`kimi-lane-lock.ps1` must not appear in `backup-lane.md` at all, because last
cycle's lane lock lost its subject when the client changed. Task 9's new
`lane-lock-call-lifecycle` region cites that tool five times.

Forbidding the NAME would forbid the replacement. Forbidding nothing would let
the old rule return under the new name — and the old rule is the age-based one
your new region explicitly repudiates. So I moved the guard from the name to the
RULE, using four needles taken from the deleted region's own text at `79ec79f`:
`-Acquire -Label`, `A BUSY result`, `The lock is advisory`, `breaks after 45
minutes`. Each verified present in the superseded text and absent from the
current one.

I want your read on whether that is the right shape, and on whether an absence
guard keyed to a TOOL NAME is a pattern we should stop using, since it broke the
first time the tool came back for a different reason.

**One measurement worth recording.** I generated the three region texts and both
sets of pins from the SAME extracted source, so transcription drift is
impossible. `textwrap` then broke lines inside hyphenated filenames, so the
Markdown normalized to `new-kimi-lane- home.ps1` and two regions read as
uncovered. That is exactly why your step 5 forbids a raw-byte comparison, and it
caught a real fault on its first use.

## Task 10's last step, and why the user stopped it

Step 7 requires the trailer check to print `clean` over `6201e30..HEAD`. It does
not. Three commits carry the trailer, as the plan says.

I proposed rewriting them and asked the user, because it rewrites 44 of the
branch's 70 commits and changes every commit id the build ledger records. Before
they answered I measured two things I should have measured when we froze this:

**This repo merges with MERGE COMMITS, not squashes.** The last six merges into
`main` all have two parents. So branch commits DO land in main's history, and
the three would arrive there.

**`main` already carries 65 commits with that trailer**, spread across recent
cycles, INCLUDING `6201e30` — the exact commit this branch started from and the
base of the very range step 7 checks.

So stripping three here is cosmetic. It makes one branch look clean against a
repository that is not, at the cost of invalidating the ledger's entire
provenance table. The user has decided: do not rewrite.

I think the plan was wrong here rather than the user, and wrong in a way this
plan usually catches. Step 7 was written as if a clean branch range meant the
rule was upheld, when the rule is repo-wide and the base of its own range
violates it. That is a claim wider than its evidence, in a gate.

## Questions

1. How should step 7 be re-scoped? My inclination is that it stays as a check
   this branch adds no NEW carriers — which is what the range genuinely
   measures — and stops implying anything about the repository, with the 65 on
   `main` recorded as a separate, un-owned problem rather than silently passed
   over. Say if that is too weak.

2. Does anything else in Task 10 depend on step 7 passing as originally written?
   I would rather you check than have me assume it is isolated.

3. Task 9's guard reshape: right shape, and should tool-name absence guards go?

4. Tasks 7 through 11 are built. Is there anything you want re-verified before I
   take the branch to its whole-branch review?

## Verification state

- Live gate: 63 passed per host, both hosts, ZERO skipped.
- Full suite: 868 passed, 13 skipped.
- All five gates exit 0, including Task 11's new exact-line checker now wired
  into CI.
- `check_workflow_paths.py` exit 0 with host parity satisfied after adding six
  modules to both Windows steps. `test_lane_credential_live.py` deliberately not
  added.
- Version bumped to `0.19.0`.
- The trailer check's own two mutations both behave: a controlled input throws,
  and an invalid revision range throws on git's exit code rather than printing
  clean.
