FIX

### R1 — PASS

`header_block()` strips escapes, finds hyphen-only rules, and returns only the lines between the first two (`evals/tools/run_behavioral_evals.py:612`, `evals/tools/run_behavioral_evals.py:617`). The retained pre-banner models-cache error is one ordinary line; the eight-hyphen rules still enclose the header, with prompt text beginning only after the closing rule (`docs/superpowers/plans/rounds/2026-07-25-eval-trim/plan-round3-transcript.txt:1`, `docs/superpowers/plans/rounds/2026-07-25-eval-trim/plan-round3-transcript.txt:3`, `docs/superpowers/plans/rounds/2026-07-25-eval-trim/plan-round3-transcript.txt:12`).

An unexpected earlier rule could cause a false-negative, but agent-authored prompt/transcript text remains after the real closing rule and cannot enter the selected block (`evals/tools/run_behavioral_evals.py:597`, `evals/tools/run_behavioral_evals.py:609`).

### R2 — FIX

“Exactly once” counts only nonempty, correctly spaced `key: value` matches (`evals/tools/run_behavioral_evals.py:652`). Therefore this block passes:

```text
model: <expected>
model:
provider: openai
reasoning effort: high
sandbox: read-only
```

The malformed duplicate does not match `(.+)`, leaving one recognized model value and allowing the final comparison to succeed (`evals/tools/run_behavioral_evals.py:653`, `evals/tools/run_behavioral_evals.py:654`). `model: ` and `model:<value>` produce the same counting defect.

The regression test duplicates two valid values only, so it does not cover this boundary (`evals/multi-model-verify/test_multi_model_verify.py:707`, `evals/multi-model-verify/test_multi_model_verify.py:715`). Other header names such as `session id:` do not collide because matching is anchored to each exact expected key (`evals/tools/run_behavioral_evals.py:651`, `evals/tools/run_behavioral_evals.py:652`).

Specific fix: count every line beginning with the exact `key:` label separately from parsing its value. Require exactly one label occurrence and exactly one valid nonempty value. Add malformed-duplicate tests for `model:`, `model: `, and `model:<value>`.

### R3 — FIX

My predicted risk was delimiter selection; the retained real header format does not reproduce it (`docs/superpowers/plans/rounds/2026-07-25-eval-trim/diff-round1-transcript.txt:1`, `docs/superpowers/plans/rounds/2026-07-25-eval-trim/diff-round1-transcript.txt:3`). The introduced defect is the incomplete exactly-once loop described under R2 (`evals/tools/run_behavioral_evals.py:652`).

The adjacent merged-stream comment is also stale: it still explains safety through “first-match,” although route safety now depends on block selection (`evals/tools/run_behavioral_evals.py:715`, `evals/tools/run_behavioral_evals.py:717`). Update it with the parser fix.

### R4 — FIX

The amber is honestly recorded: it says **3/4, one MISS**, identifies the missed expectation, and does not relabel the behavioral gate green (`.git/parallax/application-checkpoints/2026-07-28-0330-efe4fa0c07d2.md:168`). The source also runs the executor before invoking the separate grader and route parser (`evals/tools/run_behavioral_evals.py:464`, `evals/tools/run_behavioral_evals.py:487`, `evals/tools/run_behavioral_evals.py:722`).

However, the record claims every expected field is required exactly once, and that a duplicated field fails closed; malformed duplicates refute both statements (`.git/parallax/application-checkpoints/2026-07-28-0330-efe4fa0c07d2.md:166`, `.git/parallax/application-checkpoints/2026-07-28-0330-efe4fa0c07d2.md:249`). Amend those statements after fixing and testing the parser.

### UNVERIFIED

The reported 277/1 pytest result, static gates, real-colored-output probe, live 3/4 result, and earlier 4/4 comparison were not independently runnable because Python and Codex are unavailable in this sandbox (`.git/parallax/application-checkpoints/2026-07-28-0330-efe4fa0c07d2.md:165`, `.git/parallax/application-checkpoints/2026-07-28-0330-efe4fa0c07d2.md:168`). They are excluded from the verdict.

Per-claim: **R1 PASS; R2 FIX; R3 FIX; R4 FIX.**

Overall: **FIX — count all exact field-label occurrences, reject malformed duplicates, add the three boundary tests, and correct the stale comment and exactly-once record.**

