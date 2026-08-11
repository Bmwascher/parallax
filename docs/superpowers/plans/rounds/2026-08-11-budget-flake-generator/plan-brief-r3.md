Round 3. Rules, verdict grammar and boundaries as before.

Your round 2: PASS on the offsets, the pin correction, the fourth item, Q4b
and Q4c; FIX on Q4a. All accepted. I verified the three load-bearing ones
myself rather than taking them:

- `test_multi_model_verify.py:150-175` really does demand TWO COMPLETE
  preambles, with `>= 2` counts on three separate literals and a fourth
  assertion forbidding an ASCII hash. Deduplicating would reopen that
  boundary for about 101 tokens. Candidate (a) is withdrawn and will not
  be revisited in this cycle.
- `test_multi_model_verify.py:460-487` pins the resume dispatch as a
  regex over the literal `Get-Content -Raw <brief-file> | codex exec ...
  resume <SESSION_ID> -` form, and it exists because 0.21.0 live-proved
  the positional form defective. So the encoding fix REPLACES that pin
  rather than adding beside it, exactly as you said, and the replacement
  must keep stdin while adding the two encoding guarantees.
- `run_behavioral_evals.py:99-103` exposes exactly `Bash` and
  `PowerShell` as the shell tools, both allowlisted only for `codex:*`.
  Your Q5 answer therefore names the complete set, not a sample.

## Two more claims of mine that were wider than their evidence

**"Worst realistic dispatch is 1327 characters."** Withdrawn. It is ONE
measured realistic dispatch. No corpus establishes a maximum, and the
2400 cap is therefore justified as comfortably clearing a measured real
case, not as proving nothing can exceed it. Your third mind-changer — a
required realistic invocation over 2400 — stays live as a real risk.

**The round-1 artifacts you could not verify.** Paths, so you can:

```
brief   ...\scratchpad\debate23\plan-brief-r1.md        (13363 bytes, UTF-8, no BOM, 45 non-ASCII bytes)
rollout C:\Users\Brandon\.codex\sessions\2026\08\11\rollout-2026-08-11T00-02-58-019fef33-d341-7881-8d6e-4f7437783b86.jsonl   (the CORRUPTED round)
rollout C:\Users\Brandon\.codex\sessions\2026\08\11\rollout-2026-08-11T00-14-45-019fef3e-9b6a-7a21-a49f-686e0d96ac53.jsonl   (the CLEAN re-dispatch, and this debate)
```

where `...` is
`C:\Users\Brandon\AppData\Local\Temp\claude\C--Users-Brandon-Documents-parallax\a29d60ea-aa36-4cc1-806e-3a7a85997dab`.
The corrupted rollout's second user record is 13365 characters against the
brief's 13333; the difference is 14 em dashes each becoming three
question marks. Verify or refuse it; you already reproduced the mechanism
independently, so nothing rests on my artifact.

## Decisions taken, so you can hold me to them

1. **Item 9: both generators execute in this release.** Your Q6 terms
   accepted. Item 9 is not marked closed on an unexecuted matrix.
2. **The encoding fix is a distinct fourth item** with your six acceptance
   criteria, including the fail-first `???` test on Windows PowerShell 5.1
   and no claim about the backup lane's argument path.
3. **Q5: the 2400 name-based cap for `Bash` and `PowerShell`,** with your
   five tests, including the evidence-budget exhaustion case.
4. **The user has authorized 12 unchanged-tree behavioural runs,** with the
   pass/fail rule predeclared and no post-hoc reinterpretation.
5. **Item 19 relocations: lines 109-125, Q4b and Q4c only.** Measure after
   those three. If the body is still over 5000 I put the soft threshold to
   the user rather than shave a fourth thing to hit a number.

## The one tension left, and I want your verdict on it

The fourth item makes item 19 harder, and I would rather name that now
than discover it mid-build.

The encoding guard has to appear in BOTH dispatch preambles, because
`test_multi_model_verify.py:150-175` forbids collapsing them and rounds
run in separate shells. Two extra lines each — a strict UTF-8 read and an
explicit `$OutputEncoding` — is roughly 400 characters, near 100 estimated
tokens ADDED to `SKILL.md`, in the same release whose other item is trying
to remove tokens from it.

So the arithmetic is roughly: 5404, minus about 275 for lines 109-125,
minus whatever Q4b and Q4c yield, plus about 100 for the encoding guard.

Three ways I can see, and I want you to name the failure mode of each
rather than just pick:

(a) accept that this release may land between 5000 and 5250, ship the hard
    5250 ceiling, and record explicitly that the soft warning is still
    firing and why — a stated, dated exception rather than a silent one;
(b) find a fourth relocation, which is the shaving pressure your own Q1
    table warned about;
(c) put the soft threshold itself to the user as a deliberate raise, with
    the encoding guard named as the reason it moved.

My inclination is (a): it keeps every sentence that a review demanded,
makes the hard stop real, and leaves a dated record saying the file is
knowingly over its soft budget rather than pretending otherwise. But (a)
also ships a warning that still fires on every clean run, which is the
precise complaint item 19 was filed about. Tell me whether that is
acceptable or self-defeating.

<final-check>
List anything you could not verify, as UNVERIFIED. If you have no new
substantive finding, say PASS and say whether it is terminal for this
plan as now specified.
</final-check>
