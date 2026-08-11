Round 7. Rules and verdict grammar as before. This REOPENS the frozen plan
on one point, with the user's authorization, spending the last declared
budget unit. Ledger: 8 total, 7 spent through round 6, this is unit 8, 0
remaining. Any further round pauses for the user.

## Why I am reopening rather than deciding

Your Q1 answer froze `soft` at "the smallest declared value clearing the
measured body" and the HARD ceiling at 5250. I have now built Tasks 1 and 2
and measured. One number the freeze rested on was wrong, and it was mine.

**I estimated the encoding guard at ~100 tokens. It cost ~420.**

Measured, at `dd0db13`:

| step | body tokens |
|---|---|
| start | 5404 |
| after the three relocations (Task 1) | 5069 |
| after the encoding guard + its contract region (Task 2) | 5486 |
| after moving that region to `model-prompting-notes.md` | 5200 |
| after a one-line pointer back into `SKILL.md` | **5227** |

Where the 420 went: the guard is THREE lines, and
`test_multi_model_verify.py:150-175` forbids collapsing the two dispatch
blocks, so it lands twice. The contract region explaining it was the rest.

I moved that region to `model-prompting-notes.md`, which the file itself
calls "THE single source for the reviewer transport". I am claiming that as
a placement decision about NEW text, not as the fourth relocation of
pre-existing text you refused to authorize; if you disagree, say so and I
will treat it as an overrun.

## The problem the measurement creates

5227 against a hard ceiling of 5250 leaves **23 tokens**. Your own three-band
shape needs a warning band between `soft` and `hard`, and there is no honest
`soft` in a 23-token gap. The next sentence anyone adds — including a
correction a future review demands — trips a hard CI failure. That is the
pressure your Q1 table named as (i)'s failure mode, arriving through (iii).

The user was given this choice and chose to reopen rather than let me pick.

## Three shapes, and I am not asking you to rubber-stamp mine

(a) **soft 5250, hard 5500.** A real warning band with ~270 tokens of room.
    The cost is that it raises the hard ceiling above what this debate
    froze, which is the ratcheting you warned could become precedent.

(b) **soft 5230, hard 5250.** Honours the frozen ceiling exactly. The
    warning band is 20 tokens wide, so it is a warning in name only.

(c) **Something else you name**, including declaring that the encoding
    guard's real cost means the ceiling should be set from the measured
    body plus a stated allowance, with the allowance itself justified.

My inclination is (a) with the raise recorded AT the constant as "the
0.23.0 encoding guard cost 420 tokens against an estimate of 100; the
ceiling was set from the measured body, not from the estimate". But (a) is
also me asking to move a number I missed, one release after it was set,
which is exactly how ratchets start. Tell me if that is the right trade or
if I should live with (b) and take the CI failures as the intended signal.

## One more thing I got wrong, already fixed and pinned

My first encoding guard was inside a `& { }` block. I chose it because a
child scope provably cannot leak `$OutputEncoding` into the caller's shell,
and I MEASURED that it does not leak, on both hosts.

The test then failed. The native pipe reads `$OutputEncoding` from the
OUTER scope, so the guard never took effect and the em dash was still
flattened — to ONE `?` this time rather than three, because the strict
decoder half did work. I had measured that the setting was scoped and
assumed that meant it applied.

Shipped form is now a script-scope assignment restored in `finally`,
measured delivering `e2 80 94` on both hosts and restoring the prior value
even when the override hash check throws. The `& { }` failure is pinned by
its own test so it cannot come back.

This is offered as evidence about my Task 2 work, not as a question.

<final-check>
Answer the threshold question with a recommendation and the reason. If you
think my region placement was an unauthorized fourth relocation, say that
too. Anything you cannot verify, list as UNVERIFIED.
</final-check>
