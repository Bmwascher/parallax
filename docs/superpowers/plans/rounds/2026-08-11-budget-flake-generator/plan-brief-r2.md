Round 2. Evidence rules, verdict grammar and boundaries as before.

Your round 1: FIX on all six claims. I re-ran every one against the repo
myself rather than accepting it, and all six hold. Accepted in full. Below
is what changed, one correction I owe you, the reproduction inputs you
asked for, and three new questions the accepted fixes create.

## Accepted, with my own verification

**Claim 1 — accepted, my history claim was false.** I recomputed the same
snapshots with the lint's own formula:

```
91278a1  5120    ee40db5  5120    2e39414  5117
d2ed202  5129    83fe146  5404    HEAD     5404
```

It SHRANK once (5120 to 5117) and has been FLAT at 5404 for two releases.
The entire rise is one step in 0.21.0, +275 tokens. "Grown every cycle" and
"never shrunk" are both withdrawn. The surviving claim is narrower and I
will state only this: the budget has never been enforced, and the body is
5404 against a 5000 budget.

**Claim 2 — accepted, both corrections.** Lines 93-125 measure 2192
characters / 548 estimated tokens, not the 1780/445 I published; I had
sliced the wrong line range when I estimated. And `backup-lane.md:441-451`
does not merely permit the short-path rule to live in both files, it
REQUIRES it, and records that 0.21.0 introduced exactly the contradiction
my move would have recreated, in both directions across two debate rounds.
Moving that sentence would have re-opened a closed defect. Withdrawn.

**Claim 3 — accepted.** "Cannot pass in a realistic run" is withdrawn and
replaced with: expectation 1 can become UNOBSERVABLE and fail independently
of product behaviour, and its observability is path-length-sensitive under
the current rendering.

You asked for the inputs. Here they are, so the number is reproducible
rather than asserted. The two substituted strings were:

```
override = C:\Users\Brandon\AppData\Local\Temp\claude\C--Users-Brandon-Documents-parallax\a29d60ea-aa36-4cc1-806e-3a7a85997dab\scratchpad\debate23\override-verified.txt
brief    = C:\Users\Brandon\AppData\Local\Temp\claude\C--Users-Brandon-Documents-parallax\a29d60ea-aa36-4cc1-806e-3a7a85997dab\scratchpad\debate23\plan-brief-r1.md
sha      = 180f09f50d282b5603f1c0d0621f2913ff66c8b7798e7a2f3b7fe8d41f432bb8
model    = gpt-5.6-sol      effort = high
```

with `<reply-file>` and `<transcript-file>` derived from the brief path by
replacing the basename with `plan-reply-r1.txt` and `plan-transcript-r1.txt`,
the five lines joined by `\n`, and the whole thing JSON-encoded as
`{"command": <cmd>, "description": "Dispatch plan debate round 1"}`. That
yields json len 1327, `codex exec` at 790, `--sandbox read-only` at 801,
`-m gpt-5.6-sol` at 867. Treat it as reproducible now or say it still is
not.

**Claim 4 — accepted, both parts.** I had repeated the code's own comment
that keeping lines whole keeps call/result PAIRS whole. It does not: the
middle-evidence loop can exhaust its budget having kept one half, and its
actual safety property is that the loss is explicit. The narrowed claim is
"indivisible records plus explicit loss". And the plan was missing the
fail-first regression; it now has one as a required step.

**Claim 5 — accepted.** "Currently untested" is false. I read the tests you
named: coloured header and wrong route, a payload line supplying a missing
field, escape-stripping manufacturing a label, duplicate valid fields, a
missing block, and a parameterized malformed-duplicate matrix. What is
absent is GENERATED combinatorial coverage. "Highest-value" and "denser"
are withdrawn as unmeasured; the honest word is CHEAPEST FIRST TARGET.

**Claim 6 — accepted, and this was the most useful finding.** My oracle
would have generated cases whose correct answer I had not decided. Three
or more rules are valid input, ANSI inside a real label had no declared
expectation, and surrounding value whitespace is accepted by the existing
strip. The grammar gets frozen before any case is generated.

## The correction I owe you, found before your reply arrived

My claim 2 said the move was cheap because no contract region sits in
93-125. True, but incomplete in a way that matters: SIX ordinary pins cover
that paragraph, all inside
`evals/multi-model-verify/test_backup_lane.py::test_skill_preflight_names_the_remediation`,
and one of them (`so commit the removal inside the mirror`) exists because
a 0.14.2 review found the observations pinned and the imperative not. Any
relocation retargets that function. I should have said so.

## A transport defect this debate produced, and my proposal to fold it in

Round 1 of this debate was VOID and cost a full round of quota for nothing.
`tools/read-codex-round-evidence.ps1 -Fresh` refused it: the prompt the
client recorded was not the brief I sent.

The mechanism, measured by diffing the rollout's user record against the
brief on disk: every em dash in a 13,363-byte UTF-8 brief arrived as THREE
question marks, 14 spans in all. Three, not one, is the proof that two
independent faults fired in series on Windows PowerShell 5.1:

1. `Get-Content -Raw` read a UTF-8 no-BOM file using the ANSI code page,
   splitting one 3-byte character into three;
2. `$OutputEncoding` defaults to ASCII on 5.1, flattening each of those
   three to `?` on the way into the native client.

The dispatch it corrupted is the one `SKILL.md:196` documents, and
`SKILL.md:250` carries the same form for every resume. Re-dispatched on the
SAME host with `[System.IO.File]::ReadAllText` under a strict UTF-8 decoder
plus `$OutputEncoding` set to UTF-8, the identical brief bound CLEAN. Fail
then pass on one interpreter with one variable changed.

`tools/new-review-mirror.ps1:59-65` already carries a measured note about
`[Console]::OutputEncoding` defaulting to the OEM code page, so the repo
knows this hazard class in its tools and not in its shipped instructions.

I propose adding it to this release as a fourth work item, on the grounds
that the cycle is already editing those exact lines. The backup lane passes
its brief as a `-p` ARGUMENT rather than through a pipe, so this mechanism
does not apply there; whether that path has its own non-ASCII hazard on 5.1
is UNMEASURED and I am claiming nothing about it.

## New questions the accepted fixes create

**Q4 — your Q1 answer and your claim 2 answer are in tension, and I cannot
satisfy both as stated.** You recommend hard-failing at 5250 AND requiring
this release to land under 5000. But you also require the short-path rule,
the STOP, the user choice, the mirror imperative and "the mirror becomes the
reviewed tree" to STAY in `SKILL.md`. What is left to move is roughly lines
109-125 — the tracked-versus-untracked explanation and the hook paragraph —
about 1100 characters, near 275 tokens. That lands at about 5129, still over
5000.

To reach under 5000 I would have to move something else, and my candidates
are:

(a) the four-line override-verification preamble is duplicated VERBATIM in
    the round-1 block at `SKILL.md:191-197` and the resume block at
    `SKILL.md:245-251`; stating it once and showing only the differing
    `resume <SESSION_ID>` form saves about 430 characters, and it also
    removes a place where the two copies can drift apart;
(b) the `-CheckpointFile` paragraph at `SKILL.md:334-339`, read only when
    a checkpoint governed the fixes;
(c) the resume-rationale paragraph at `SKILL.md:253-266`, read only from
    round 2 onwards.

Which of these do you accept, and is (a) safe given that both blocks are
inside pinned contract text? If none of them gets there honestly, say so
and I will put the ceiling question to the user instead of shaving to hit
a number, which is the exact failure mode your Q1 table warns about.

**Q5 — for the rendering fix, I want to compare your bounded-window
proposal against a simpler one you did not name.** The simplest change that
satisfies all six of your conditions is to extend the EXISTING name-based
cap at `run_behavioral_evals.py:407` to the shell tools, so a shell
`tool_use` gets the same 2400 the mutation lane's `Edit`/`Write` already
get. The measured worst realistic dispatch is 1327 characters, so 2400
truncates nothing, no window is selected, and the harness never decides
which part of the input matters — which is my objection to bounded windows,
since choosing what the grader sees is a thumb on the scale even when the
source event is genuine. The cost is that a shell record carrying a large
heredoc grows the transcript and pushes against the elision budgets
(`limit=40000, head=15000, tail=25000, evidence=16000`). Which do you
prefer, and what would change your mind?

**Q6 — scope.** You said one Python parser does not close item 9 and named
`Get-SkillReport` plus `Hide-KnownContainer` as the minimum second target,
costed through the existing `run_functions` helper at
`test_codex_context_probe.py:73-96`, which I confirmed does exactly what
you describe. I accept both targets. That makes this release four items
rather than three. Is there a defensible smaller close — for instance,
landing the Python generator plus the FROZEN grammar and case matrix for
the PowerShell target, and executing the PowerShell half in 0.24.0 — or is
a half-landed generator worse than none?

<final-check>
List any claim you could not verify against files you read, as UNVERIFIED.
In particular, tell me whether the offsets in claim 3 are reproducible now
that the substituted strings are supplied.
</final-check>
