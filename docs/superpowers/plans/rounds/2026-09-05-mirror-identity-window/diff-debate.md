# Mode-diff debate: the mirror identity window

Separate from the PLAN debate recorded in `README.md`. That one argued
about a design; this one argues about the shipped diff.

Range: `0f485cca16487ff83eee7529787bd9bf3049c66c` to head.
Lane: `gpt-6-astra` at `high`, codex-cli 0.153.4.
Fix-verify budget declared before round 1: **3 dispatched exchanges.**

Preceded by the required whole-branch review from the fable-reviewer
seat, whose findings are applied in commit `79ab77f`.

## Preflight

`codex --version` 0.153.4, `codex login status` `Logged in using ChatGPT`.

**The back-channel sweep was NOT empty.** `git ls-files --cached --others
'*AGENTS.md' '.agents/*' '.kimi-code/*'` listed an UNTRACKED `AGENTS.md`
at the repository root - legitimate maintainer guidance for Codex
sessions working in this checkout, and a back-channel all the same,
because codex ingests it as instructions. Its content is not neutral for
this review either: it tells a Codex session that a Codex review cannot
satisfy a cross-vendor requirement, which is a claim about the reviewer's
own standing. The mirror removed it; being untracked, that needed no
commit. Re-enumeration against `C:\Temp\pxd1` came back empty and the
file is absent there.

Context probe: `status: clean`, 31 home-scoped skills before and **0
after**, 0 repo-scoped, 0 plugin-cache-scoped, `project_agents_md: false`.
The global `~/.codex/AGENTS.md` survives a clean probe and is recorded
here rather than removed, which is the whole of what a clean probe means.

The build printed `source_manifest: C:\Temp\pxd1.source-manifest`: this
branch's own feature ran in the mirror build for its own debate.

## Round 1 (`Astra D1`)

Wrapper exit 0, `reply-present`. Route verified from the transcript
header: `model: gpt-6-astra`, `provider: openai`, `reasoning effort:
high`, `sandbox: read-only`, `workdir: C:\Temp\pxd1`. Binder verdict
`clean`, `sealed: sealed`, so the reply is bound to the brief this side
sent.

Claim 1 SURVIVED: the reviewer traced the reader, the size refusal, the
parser, the renderer and the exception fallback, and found no path by
which sidecar content changes the verdict.

Five findings, all CONFIRMED, all applied.

**1. The overlap guard compares spelling, and a trailing dot defeats it.**
The one that matters. `-MirrorPath <repo>.` passes the equal, inside and
contains tests because they are string comparisons, while Windows strips
the trailing dot when it OPENS the path. The reviewer executed the
shipped construction prefix on both hosts with `Remove-Item` replaced by
an interceptor and reached the recursive deletion call.

**Its stated consequence is contested, and this side measured it.** The
reviewer reported the bypass as reaching recursive deletion of the
source. Measured 2026-09-05 on BOTH hosts: `Remove-Item` on a
trailing-dot path throws `PSArgumentException` and deletes NOTHING, on
`-LiteralPath` and `-Path` alike, and the victim survives. The reviewer's
interceptor made the deletion unobservable, so what its probe established
is REACHABILITY, not deletion, and the round-1 wording claims the latter.

That does not save the guard. The failed removal is NON-TERMINATING, this
script never sets `$ErrorActionPreference`, so the build carries on and
constructs a mirror at a path naming the tree under review. The fix is
the same either way and is the one the reviewer asked for: refuse the
spelling before any comparison, on BOTH operands, since both are
user-supplied. Two tests, one per operand, and the mirror-path test
asserts the source survives.

The defect is PRE-EXISTING, not introduced here. It is the same class the
branch already closed for `-ExtraInput`, left open on the destructive
path - a fix that did not sweep its own class.

**2. Two oracles go green without measuring anything.** The
control-character test and the trailing-newline test assert only an exit
code and the ABSENCE of a string. The reader's own failure fallback
prints `what moved: unknown` and satisfies both, so each passes when the
behaviour it names was never exercised. Both now assert the whole
rendered name positively and that `unknown` is absent. The substring form
also accepted a doubled escape prefix, which is exactly how the shipped
renderer emitted two backslashes through four rounds without a test
noticing.

**3. The item 93 amendment outran its evidence.** Written as "item 90 did
not close a gap" and "whatever produced it is not a property of the
tracked tree". Three fresh runs that do not hit whatever conditions
produced 18m42s exclude nothing about the code. Reworded in `BACKLOG.md`
and `gate-results.md` to say only that it did not reproduce, and that the
cause is unknown with no candidate favoured.

**4. The record claimed static review COULD NOT have caught the oracle
defects.** It said so on the grounds that no round ran the tests, in a
paragraph immediately followed by an explanation of a phrase mismatch
that is plain to read without executing anything. Discovery history is
not proof that earlier discovery was impossible. Reworded to "the reviews
missed them; implementation exposed them".

**5. A stale parser comment** still taught the trailing-newline
explanation that the implementation comment ten lines below it retracts.
Removed.

## Sweep

Asked for instances of the defect CLASSES rather than the specific bugs,
and for the shapes searched so the sweep's blind spots are visible. The
reviewer reported inspecting changed escape literals, negative-only
assertions, categorical measurement conclusions, adjacent comments and
self-count wording, and found no fifth backslash-doubling instance and no
unambiguous self-count error.

One limit it stated on its own claim: `Format-AdvisoryName` covers the
EXPLANATION's output, not all script output, because the construction
record prints the sidecar path directly. Recorded, not fixed - that path
is one this tool constructed and validated, not one read back from a
mutable file.

Verdict: **FIX**.

## Round 2 (`Astra D2`)

Resumed session `01a074f2`, so the reviewer argued against its own round
1 with that context intact. Wrapper exit 0, route verified, binder
`clean` and `sealed`. Mirror rebuilt at the SAME path with `-Force` from
head `b58bf25` and its identity re-recorded, because a resumed round
whose mirror moved is refused on `cwd` and lost.

**The rebuttal was accepted and the claim withdrawn.** "I did not
establish successful deletion and withdraw that implication." The
reviewer reproduced `PSArgumentException` on both hosts with
`Remove-Item -WhatIf`, corroborating this side's measurement, and stated
plainly that it could not supply a real deletion because its session is
read-only. That is the debate working in the direction it is supposed to
work in, and it cost one round to establish that a destructive claim was
overstated.

All five round-1 fixes verified present against the code rather than
against the summary.

Three residual findings, all CONFIRMED, all applied.

**1. The new guard still admitted three aliases.** The deeper point, and
the reviewer put it exactly right: rejecting trailing punctuation does
not establish filesystem identity, and every comparison in this tool is a
string comparison. Reachability demonstrated on both hosts, deletion
intercepted:

| source | mirror | reached delete on |
| --- | --- | --- |
| `<repo>\skills\multi-model-verify` | `<repo>\skills\MULTI-~1` | both hosts |
| `<repo>::$INDEX_ALLOCATION` | `<repo>` | PowerShell 7 |
| `<repo>` | `\\?\<repo>` | Windows PowerShell 5.1 |

It also confirmed with `Remove-Item -WhatIf` that the 8.3 short form
names the long directory on both hosts.

The fix keeps this tool's existing stance rather than inventing a new
one: it REFUSES the spellings it cannot resolve. Device forms `\\?\`
and `\\.\`, NTFS stream syntax `::`, and 8.3 short-name components are
each refused with their own message. Resolving an alias to filesystem
identity needs an open handle, and this tool will not take one on a
destination it is about to delete.

**2. The guard shipped with the override operand missing.** An
`-OverrideOut` of `<repo>.\override.txt` passed every check and named a
location inside the tree under review, which the build then hands to the
probe's writer. This is finding 1 of round 1 on a third operand: the
first version of the guard covered two operands and stopped. Guarding
operands one at a time is how the class survived being fixed once
already, so the fix builds a subject list and the test says why.

**3. A third negative-only oracle.**
`test_an_unmeasurable_expected_digest_is_refused` asserted only
`returncode != 0`, which exit 2 with empty stdout satisfies. This
script's contract separates 1, blocked with a reason, from 2, a script or
environment error, so that oracle could not tell a working refusal from a
crash in the code meant to refuse. Now requires exit 1 and the named
diagnostic.

**What the sweep covered and what it could not.** Path aliases, omitted
guard operands, negative-only assertions and their helpers, amended
measurement conclusions, adjacent comments. It found no further
measurement overclaim and no self-count defect. Two stated limits, both
the reviewer's own: live UNC access was unavailable, so the guard's
component split is unverified end to end for UNC, and it did not re-run
the full pytest suite.

Verdict: **FIX**.

## Round 3 (`Astra D3`), and the budget is spent

Resumed, route verified, binder `clean` and `sealed`. Mirror rebuilt at
the same path from head `d80f0bc`.

**NOT A DRY ROUND.** Four more confirmed findings, all applied. Round 3
was dispatched as the confirming round of a declared budget of three, and
the debate therefore CANNOT terminate here on its own terms:
`debate-protocol.md` allows termination only on an adjudicated dry round.

**1. The colon rule was wrong.** `Contains("::")` catches an unnamed
stream and misses `<path>:$I30:$INDEX_ALLOCATION`, whose colons are
SEPARATED. On PowerShell 7 that path reports `Directory` and reached the
intercepted delete. The rule is positional now: one colon is legitimate,
the drive separator at index 1, and any other colon names a stream.

**2. The guard was still missing two operand sets**, and this is the
third time the same shape has been found. `ExtraInputPaths` and the
discovered `followedTargets` were both outside it. The reviewer supplied
THIS MIRROR'S OWN SIDECAR under its real short alias
`C:\Temp\PXD1~1.SOU` as an extra input; it passed
every check and reached the removal of
`C:\Temp\pxd1.source-manifest`, after which the
unchecked copy would leave a declared review input out of a mirror the
digest certifies.

The fix is not another operand. It is ONE HELPER,
`Test-UnresolvableSpelling`, that every operand calls. Naming subjects
inline is what failed twice; a caller that has to remember to add itself
to a list is the defect.

**3. The unchecked removal is filed as item 98**, on the reviewer's own
recommendation that the spelling work is not its remedy. Different class:
an ordinary path, an ordinary removal, an ordinary failure. It simulated
a non-terminating error on both hosts and reached `New-Item`; it did NOT
reproduce a contaminated build under real denial, and item 98 says so.

**4. A fourth negative-only oracle**,
`test_a_mirror_whose_current_state_cannot_be_measured_is_refused`,
directly beside the third. Accepted any nonzero exit and the generic
substring `could not be`, so changing the branch to exit 2 would have
left it green.

**The reviewer also refuted the guard in the other direction, which is
what it was asked to do.** The first 8.3 pattern matched `~[0-9]+$`
anywhere in a component, so it rejected `release~2026` - an ordinary
directory name - on both hosts, with a message telling the user to pass
the full name when that already was the full name. The shape is anchored
now, and `test_an_ordinary_name_holding_a_tilde_and_digits_is_accepted`
is the regression against tightening it back.

## Two errors of this side's own, both found by running things

**The helper shipped with a doubled backslash.** Generated as
`.Replace("\\", "/")`, which PowerShell reads as a literal
two-character string, so the split never fired and EVERY component check
in the new helper was dead code. The short-name test caught it; nothing
else would have. Seventh backslash-doubling incident on this branch.

**A test asserted the wrong conclusion and did not survive execution.** A
draft of `test_a_stream_form_repo_root_is_refused_too` claimed the stream
spelling was neutralized by `Resolve-Path` and the build proceeded
normally, inferred from one earlier run that predated the guard working
at all. It is refused. The test now records which mechanism refuses it.

Gate after the fixes: 164 passed and 1 skipped under BOTH hosts, full
`pytest evals` 2927 passed and 14 skipped, backlog lint clean, script
still pure ASCII.

## Budget

3 of 3 dispatched exchanges used. Round 3 found four real defects, so the
trend does not support declaring the work done: every round so far has
found something, and the last one found the guard broken in both
directions at once. Extending the budget is the USER'S decision and not
this session's to grant - the whole-branch review caught exactly that
omission in the plan debate's record, where a fifth exchange was
dispatched with no authorization line.

Verdict: **FIX**, budget exhausted, awaiting authorization.
