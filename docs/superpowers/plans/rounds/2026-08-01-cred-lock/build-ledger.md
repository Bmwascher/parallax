# Build ledger, 2026-08-01 lane credential and lock

Per-task record of WHO built each task, WHAT verification exists, and
WHOSE evidence it is. The last column matters: the session verifies every
task independently and never accepts an implementer's report as the
verdict, so where a report did not arrive the evidence is the session's
own and must not later be attributed to the implementer.

Plan: `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md`,
FROZEN at revision 37 after 40 cross-vendor rounds. Revision N was frozen
after round N+1, so the two numbers never match.

Building reopened the plan TWELVE times after its round-28 PASS. Round 29
froze the validator's CLI contract, which the plan had left for an
implementer to invent, and turned acceptance into the four-part rule.
Round 30 found the recovery command fail-open at its parse boundary, plus
four caller defects of the same family, one of which was the blank-line
class. Round 31 reopened Task 7 whole and returned ten findings, nine
confirmed and one refuted. Round 32 added Task 11, after the session found
a second Python instance of the blank-line class that three sweeps had
missed. Round 33 replaced Task 7's absolute-key oracle, which could never
have failed. Round 34 replaced Task 10's step 7 with the authorized-debt
guard and corrected this ledger's own provenance. Round 35 found that step
7 described a guard without containing one. Round 36 found that two of the
three details the new guard called load-bearing had no failing oracle, and
that a third was not load-bearing at all. Round 37 found the mutation
harness itself only described, and round 38 found that harness printing
where it should have asserted. Round 39 found the ledger still calling
the behavioral gate unrun after it had run. Round 40 was the terminal
PASS. The remediation rows below are the result.

| Task | Commit | Implementer report | Session verification | Evidence provenance |
|---|---|---|---|---|
| 1 CI repair | `ac3e4d8`, `e6dc4fe` | full, accurate | ran the checker, all four then five host-discovery directions, both mutations | BOTH |
| 2 credential validator | `a5ec09f` | full, accurate | ran all four statuses, the seam, blank path, binding refusal, both hosts | BOTH |
| 3 lock tool | `5365bb0` | full, accurate | ran ResolveOwner, acquire, reclaim, contention, the wait clamp, status | BOTH |
| 4 live protocol gate | `00168a5` | full, accurate | read the acceptance and timeout paths, ran all three host modes | BOTH |
| 5 login wrapper | `74f57ab` | full, accurate | ran the non-directory row and the probe seam, checked the ACE shape, verified `kimi login` against the real client | BOTH |
| 6 builder stops copying | `165e809` | **NONE — agent returned twice with only "I'll wait for the notification"** | copy absence, junction, seam message, terminating deletion, deleted-test audit, first-use live test, both hosts, full suite | **SESSION ONLY** |
| 5+6 fail-closed remediation | `8e5dcaf` | full, accurate | byte-compared the stored template against the frozen line, re-ran the round-30 fail-closed reproduction on both hosts, read all four caller fixes, checked the nine-row matrix and row 9's fixture, 113 tests per host | BOTH |
| 7 live gates | `29f975b` | full, accurate | ran the support suite on both hosts, verified the helper imports with no live check, drove the refusal direction with the opt-in set, traced the guard ahead of the record write | **BOTH, live half UNRUN** |
| 7 r31 remediation | `fd712b1` | full, accurate | read the fixed capture order and its call sites, confirmed both new instances of the exact-line rule, ran the old-vs-new custody-line demonstration, listed the six pin oracles and six safety fixtures, 51 tests per host, full suite 840 | BOTH, plus **two session-only findings** |
| 7 r33 partial | `6a6a5f9` | terminated at the session limit | read the fixed capture order, ran the live gate before and after: 7 passed 5 failed -> 11 passed 1 failed | BOTH |
| 7 FINISHED | `480d210` | **NONE — agent stopped mid-flight waiting on a backgrounded suite** | read the five-step oracle and all seven new offline oracles, confirmed zero probe-record references remain, ran the live gate on BOTH hosts | **SESSION ONLY** |
| 8 doctor | `89bcab4` | full, accurate | verified the recovery command byte-identical to the plan AND the builder, listed all 15 pins, added the two missing boundary fixtures and showed all four mutations bite | BOTH, plus a session addition |
| 9 contract | `ac6e6d8` | n/a, session build | generated regions and pins from one extracted source, proved coverage via parse_regions/collect_pins, deleted a sentence and confirmed the region reads UNLOCKED | SESSION ONLY |
| 10 CI, version, gate | `ee40db5` | n/a, session build | ran all five gates, the workflow checker with host parity, and the trailer guard's three failure directions | SESSION ONLY |
| 11 exact-line gate | `a5e3b83` | **arrived late, after a premature idle notification** | ran the checker clean, reintroduced the defect into the REAL tree and confirmed it is caught, confirmed the legitimate filter in the same file is not flagged, 158 tests per host | BOTH |
| mirror utf-8 output **(OUTSIDE the eleven tasks — user-authorized 2026-08-02, see the plan's debate record)** | `51b4554` | n/a, session change | measured IBM437 on both hosts, showed the byte difference, 65 mirror tests per host, clean full suite | SESSION ONLY |

## Task 6, stated plainly

No implementer report exists. The agent spent roughly 313k tokens and
returned twice without evidence; a direct request for the eight
load-bearing points produced the same non-answer. The work itself is
sound, and every claim in the commit message rests on a check the
session ran and can name:

- no `Copy-Item` and no reference to the user's credential path anywhere
  in the builder
- `New-Item -ItemType Junction` replaces it
- `Remove-Item ... -ErrorAction Stop` followed by an absence verification
- the moved seam's message reads `simulated pre-emission failure`, no
  longer naming a credential copy that no longer exists
- first use live-tested: exit 6, the complete runnable login command, and
  no lane home, no lock and no debate home created
- 60 tests per host; 765 passing across the suite
- the two deleted tests audited individually and both confirmed
  superseded rather than dropped, one re-pointed at the fixture that
  replaced its subject

## Task 7, stated plainly

The offline half is fully verified: 51 tests per host after the round-31
remediation, driving the same production helper the live suite imports,
with no opt-in and no real credential.

The LIVE half has never run. It needs three pre-provisioned lane homes,
and `PARALLAX_LANE_LIVE_HOME_A`, `_B` and `_C` do not exist, because
creating them needs a one-time interactive login this suite is forbidden
to perform. **Task 7 step 2 requires all pass and ZERO skipped, so that
gate is UNSATISFIED.** Nothing in this branch may claim measurements 5,
6, 7, 10, 11, 16 or 17 are re-verified by an executed gate.

What IS verified is the refusal direction, which is the safe one: with
the opt-in set and the homes absent, all ten tests ERROR rather than
skip, naming the login wrapper and the missing variables. Without the
opt-in they skip.

The probe-record finding raised here is CLOSED at `fd712b1`: the record is
now a locking assertion with six oracles, and rewriting it needs an exact
opt-in.

## Round 31, and what each side caught

The reviewer read Task 7 whole and returned ten findings. Nine were
confirmed against the code by the session and fixed at `fd712b1`. Two of
them were serious in kind rather than in degree: a token issued by the
command being scanned could reach pytest output, and the live-home setup
had no check preventing the suite's own deliberate expiry from landing on
the user's real credential.

The tenth does not hold. It claimed the hostile `-Model` refusal fires
before any lock interaction, which would make the failed-build cleanup
test vacuous. The refusal is at `tools/new-kimi-lane-home.ps1:613`, inside
the main `try` and after the acquire at line 573. The reviewer appears to
have read the comment at line 610, "This runs before ANYTHING touches the
filesystem", and generalized it from filesystem to lock. That test is
unchanged.

Two findings are the session's own. The blank-line acceptance bug had a
SECOND instance neither the reviewer nor the round-30 remediation named:
the custody line, which carries the nonce the release is performed with.
And item 6's post-command merge still runs after its assertions rather
than inside the capture helper; that one is left as-is because those
homes are disposable and hold no real credential, and it is carried to
the next round rather than changed unilaterally.

Neither side's list contained the other's. That is the argument for
running both, stated as a fact about this round rather than as a slogan.

## The live gate HAS RUN. Rounds 32 and 33.

The user performed the three manual logins on 2026-08-01 and the live
suite executed against three real lane homes. This supersedes the "Task
7, stated plainly" section above, which was written when the gate was
unrunnable.

**FINAL live state: 63 passed on `powershell.exe`, 63 on `pwsh.exe`, ZERO
skipped and zero failed on both.** Task 7 step 2 is SATISFIED. Task 10
step 5 re-runs it at final HEAD.

Passing with live evidence: measurements 6 (junction read-through), 7
(refresh write-through and rotation), 10 (both delete paths, including
the r32 deletion oracle that is the only thing ever to exercise that
branch), 11 (coexistence), 16 and 17 (`provider list`).

**Measurement 5 now HAS live evidence, and it did not before.** Its old
oracle could never have produced any. That test built its "absolute" key with
`Path.resolve()`, which follows a junction on Windows, so the key named
the same credential the relative default already reached. Exit 0 with
`PROBE` was produced identically by "the absolute key resolved" and by
"it was ignored". Round 33 replaced it with a five-step three-state
oracle, built at `480d210`. Step 4 carries its own instruction — either
success REFUTES measurement 5 and that is a finding, not a test to fix —
and it failed on both runs on both hosts. So an absolute `oauth.key`
genuinely does not resolve, and that is now measured rather than
assumed.

**One fact worth recording on its own.** Three lane logins now coexist
with the user's own, and the user's real credential is untouched: still
`ok`, file unwritten since hours before the three logins. That is the
first direct evidence that this branch's fix works. Under the copy-based
approach a lane login could retire the real refresh token.

## The whole-branch review HAS RUN, and it found three things

Range `6201e30..098e3e1`, retained verbatim in
`fable-review-production.md` and `fable-review-tests.md`.

**The diff is 1.9 MB and does not fit one context.** It was split into a
production slice and a test slice, reviewed concurrently, each reviewer
holding the whole-branch commit list and stat so each could see what it
was not given. **Recorded as a deviation: no single reviewer saw the
whole diff at once.**

Both slices returned "ready to merge: with fixes", and between them named
three Important findings. All three are fixed at `3a7a133`, and each
carries an oracle that FAILS without the fix:

1. **The evidence validator enumerated the sessions root with
   `-ErrorAction SilentlyContinue`.** Rule 3 requires exactly one new
   session leaf, so an unreadable subtree holding a second concurrent
   session simply went uncounted. Measured by reverting the fix: on that
   layout the old code reported the round **clean**. The enumeration is
   now terminating and maps to `session-inventory-unreadable`.
2. **The lock classified records with case-insensitive comparisons.**
   `{"version":1,"state":"Free"}` and a field spelled `Version` both read
   as a well-formed FREE record, and an acquire then overwrote a record
   the tool had never recognized, against a shipped contract that says a
   record not exactly satisfying the schema is held and reported. All
   four case variants fail without the fix; the lower-case record is the
   positive control.
3. **Four asserts pinned `$ownerJson`**, which r29 replaced with
   `$ownerLines`, so they held whatever the builder printed — including a
   headline claim that validator failure fabricates no recovery command.
   The needle now comes from the shipped template, and a new test holds
   BOTH directions of it. Mutating the needle back to `$ownerJson` fails
   that test.

Two Minors are also fixed: the exact-line gate skipped files it could not
read or parse, and the workflow checker's comment said "exactly these
four" above a ten-entry list. The remaining Minors ride, with reasons in
the two artifacts.

**Re-verified after the fixes:** full suite 877 passed / 13 skipped; the
live gate 70 per host on BOTH hosts with zero skipped; and the user's own
credential still reads `ok`/`valid`, its file unwritten since before the
lane logins.

## Round 41, the diff debate, and the family behind one finding

The cross-vendor diff debate REJECTED the session's scope call on the
review's second finding, and it was right. Case-insensitive comparison
was not a lock defect; it ran through every foreign-data boundary in the
branch, and the lock was one instance:

- the credential validator matched required KEY NAMES case-insensitively,
  and PowerShell property access is case-insensitive too, so
  `Access_Token` satisfied the required `access_token` twice over;
- both callers accepted `OK`/`Valid` as the frozen `ok`/`valid` pair and
  then routed on a status the frozen table does not contain;
- the round validator accepted `AUTO` for `auto`, case-variant record
  types, and a tool named `read` where the allowlist says `Read`, because
  `Compare-Object` is case-INSENSITIVE without `-CaseSensitive`
  (measured).

The same round found a defect nobody had raised: the credential validator
decoded bytes with the REPLACEMENT fallback, so a corrupt byte inside a
token became U+FFFD, still parsed as JSON, and was accepted as
`ok`/`valid`. Bytes that are not a credential, read as a good one. The
decode is now strict and lands on the frozen `malformed`/`not-json` pair,
inventing no new vocabulary.

Hostname comparison and confirmation hashes stay case-insensitive on
purpose. They are not this class.

**It also found two of the session's OWN new oracles too weak**, which is
the part worth keeping: the lock case tests covered only FREE records, so
reverting the held-side comparisons alone left every one of them green;
and the exact-line gate test called `check_repository()` directly and
never proved the executable gate returns nonzero. Both are closed, the
first with a held record carrying a case-variant required key plus a
non-mutation assertion, the second by driving `main()` end to end on both
read branches.

All of it at `c34da9c`, and every fix has a mutation that fails without
it. Re-verified after: full suite **895 passed, 13 skipped**; live gate
**70 per host on BOTH hosts, zero skipped**; all five gates exit 0; and
the user's own credential still reads `ok`/`valid`.

## Rounds 42 to 47, and the FINAL verification totals

The debate did not stop at 41. Five more rounds ran, every one of them on
the evidence validator this branch carries but did not introduce, and
every one found something:

- **42** — the case family was still open at the boundaries that matter,
  and the credential validator decoded with the REPLACEMENT fallback, so
  a corrupt byte inside a token became U+FFFD, parsed, and was accepted
  as `ok`/`valid`. It also found two of the session's own new oracles
  unable to fail.
- **43** — the strict-decode oracles corrupted tokens the rules require
  later, so they measured which failure won rather than the danger. The
  fourth strict input had no oracle at all. `parsed()` took the LAST
  stdout line, so stray output before the JSON passed every test in that
  module.
- **44** — the resume side of the session binding had no case oracle, the
  BOM behaviour was now owned by this code without a control, and the
  prior-state decode case had no same-shape clean control.
- **45** — the three ordinal comparisons had no oracles of their own.
- **46** — the mutation audit's preamble claimed a precision its own
  table did not carry.
- **47** — **PASS. The diff debate is complete.**

One measurement from round 44 is worth keeping outside the table.
`String.StartsWith(string)` is CULTURE-SENSITIVE by default and silently
ignores zero-width characters, so a BOM-prefixed agent file satisfied a
check for how the file must OPEN. That was found only because a control
added that round failed to discriminate.

**FINAL verification, at `54e1742` unless noted:**

```
full suite                933 passed, 13 skipped
live gate powershell.exe  70 passed, ZERO skipped
live gate pwsh.exe        70 passed, ZERO skipped
skill_lint --strict       exit 0
skill_scanner             exit 0
run_trigger_evals         exit 0
check_exact_line_oracles  exit 0
check_workflow_paths      exit 0
behavioral --head         0 failures, 7 ran, 2 manual-only skipped
real credential           {"status":"ok","detail":"valid",...}
```

`fc6b6fa`, the terminal commit, changes one Markdown file; the three
modules that read the plan and the ledger were re-run there, 124 passed.

## Mutation audit, SESSION-MEASURED

Selected review mutations from rounds 41 through 46 are summarized below.
This is session-measured context, not a complete or independently
reproducible audit. Rows may group related replacements; Command entries
are selectors or per-case labels rather than copy-paste invocations;
Result entries identify a commit only where one is written.

| Reverted | Command | Result |
|---|---|---|
| `-ErrorAction Stop` -> `SilentlyContinue` in `Get-SessionLeaves` | `-k unreadable` | round reported **clean** at `3a7a133^` |
| all seven case-exact comparisons in `Get-Classification` | `-k case_variant` | 4 failed, control passed, `c34da9c` |
| held-side comparisons only | `-k case_variant` | 3 failed, `c34da9c` |
| strict decode at all four evidence inputs | `-k invalid_byte` | all four reported **`status: clean`**, `82c894e` |
| `Test-HasKey` made case-insensitive | `-k each_shape_branch` | 6 failed, `82c894e` |
| `kind` literals, fresh session id, resume session id | per-case | 1 failed each, controls passed, `cd75e2d` |
| property-set `-cne` in both callers | `-k case_variant_result_keys` | 6 failed (login), 3 failed (builder), `82c894e` |
| `-StripBom` on both whole-file readers | `-k bom_prefixed` | 2 failed, `cd75e2d` |
| each ordinal comparison, one at a time | per-case | 1 failed each, this round |
| `switch -CaseSensitive` | `-k first_record_type` | **0 failed** — recorded as defensive, not claimed |

The last row is the point of keeping this table: the final listed
mutation could not be shown to matter, and it is written down as such
rather than listed with the rest.

## What is NOT done

All eleven tasks are built. What remains is not build work:

- The mode-diff debate's next round, then the attestation.
- Remote CI. It has never run on this branch and is unverified until the
  pushed workflow completes.

## The behavioral evaluation HAS RUN. Task 10 step 6.

`python evals/tools/run_behavioral_evals.py --head`, against the checkout
rather than the installed cache, at `316da38`: **zero failures.** Seven
cases ran and every one met all of its expectations —
`plan-mode-debate-runs` 4/4, `diff-mode-spec-fidelity` 4/4,
`degraded-consent-gate` 4/4, `missing-reference-refusal` 3/3,
`fix-application-checkpoint` 4/4, `fix-checkpoint-attended-stop` 3/3,
`no-manufactured-objections` 3/3.

**TWO cases were SKIPPED as manual-only**, and one of them is this
branch's own subject: `backup-lane-consented-substitution`. The other is
`panel-blind-relay`. So this suite did NOT exercise the changed lane end
to end, and nothing here may be read as saying it did. What covers the
lane is the live gate, at 63 per host with zero skipped.

## The trailer waiver, recorded rather than buried

Three commits in this branch carry a `Claude-Session:` trailer that
`CLAUDE.md` forbids. They STAY, by the user's decision on 2026-08-02.

The original gate asked for the range to print `clean`. Two things were
measured before that was waived, and neither was known when the gate was
frozen: this repository merges with MERGE COMMITS rather than squashes,
so branch commits do reach `main`; and `main` already carries 65 such
commits, including `6201e30`, the base of the gate's own range. Removing
three would have rewritten 44 of this branch's 70 commits and
invalidated every commit id in the table above, to make one branch look
clean against a repository that is not.

The replacement guard names all three commit ids in full, fails on a
fourth, permits fewer than three, and reports authorized debt rather than
`clean`. Not claimed: that `main` is clean, or that anything beyond the
one literal `Claude-Session:` was scanned.

## Standing note for the whole-branch review

Do not read this ledger's "BOTH" rows as two independent verifications of
equal weight. The implementer runs first and the session checks it; they
share a machine, a working tree and an interpreter. Neither substitutes
for the cross-vendor lane or for CI.

The local suite is now CLEAN, which was Task 10's precondition. The one
former failure,
`test_review_mirror.py::test_a_non_ascii_baseline_entry_reaches_the_manifest`,
was recorded here as a local console-encoding artifact. It was not: the
mirror decoded git's pathnames as strict UTF-8 and then printed them in
the OEM code page, so an accented name reached the baseline and the
manifest as U+FFFD. Fixed at `51b4554`. The earlier reading was too
generous to the tool, and the order-dependence was the clue - ambient
console encoding varies, and another test in the same run could change
it.
