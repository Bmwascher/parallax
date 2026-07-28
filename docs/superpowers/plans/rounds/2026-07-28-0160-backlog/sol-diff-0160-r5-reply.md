FIX

### R1 — FIX

`effective_route_ok()` strips escapes across the entire combined output, then searches each expected field independently across that whole output (`evals/tools/run_behavioral_evals.py:612`, `evals/tools/run_behavioral_evals.py:615`). First-match-wins protects a field present in the real header, but not one omitted there.

Agent-authored text preserves physical lines, is embedded in the grader prompt, and therefore reaches the searched output (`evals/tools/run_behavioral_evals.py:394`, `evals/tools/run_behavioral_evals.py:660`, `evals/tools/run_behavioral_evals.py:685`). Consequently:

- A missing real `model:` can be supplied by a later `model: <expected>` payload line.
- A later `mo\x1b[31mdel: <expected>` line becomes a valid `model:` line only after global stripping (`evals/tools/run_behavioral_evals.py:589`, `evals/tools/run_behavioral_evals.py:612`).

The new test covers a complete colored header and a wrong-but-present model, not a missing field supplied later (`evals/multi-model-verify/test_multi_model_verify.py:653`, `evals/multi-model-verify/test_multi_model_verify.py:664`).

The escape regex also covers only CSI sequences with digit/semicolon parameters and an alphabetic final byte; it is not a general ANSI escape matcher (`evals/tools/run_behavioral_evals.py:589`).

Specific fix: extract the first startup-header block between its delimiter lines, strip escapes only in that block using a complete CSI pattern, and require each expected field exactly once there. Add missing-field-plus-later-payload tests, including the strip-created-line case.

### R2 — PASS

`Write` remains available while `Edit(**)` alone supplies mutation approval (`evals/tools/run_behavioral_evals.py:112`, `evals/tools/run_behavioral_evals.py:113`). Those constants are selected only for mutation cases and passed directly as `--tools` and `--allowedTools` (`evals/tools/run_behavioral_evals.py:440`, `evals/tools/run_behavioral_evals.py:457`).

The repository’s recorded CLI contract explicitly says `Write(**)` is rejected and `Edit(**)` covers Write (`tools/check-drift.ps1:490`, `tools/check-drift.ps1:495`). No load-bearing runner path was found.

### R3 — PASS

Acquire rejects blank labels, trims the credential, and then rejects every remaining character outside printable ASCII (`tools/kimi-lane-lock.ps1:204`, `tools/kimi-lane-lock.ps1:208`, `tools/kimi-lane-lock.ps1:215`). The normalized label is JSON-encoded and written as ASCII (`tools/kimi-lane-lock.ps1:235`, `tools/kimi-lane-lock.ps1:244`).

Release obtains the trimmed string owner and performs a case-sensitive comparison against the trimmed supplied label (`tools/kimi-lane-lock.ps1:174`, `tools/kimi-lane-lock.ps1:187`). Thus validation, storage, and comparison agree.

### R4 — FIX

The fix introduced the strip-created payload match described under R1 (`evals/tools/run_behavioral_evals.py:612`, `evals/tools/run_behavioral_evals.py:615`).

The record says a wrong model “still fails closed,” but its test establishes only the wrong-present-field case; the missing-field-plus-later-payload case passes (`.git/parallax/application-checkpoints/2026-07-28-0330-efe4fa0c07d2.md:217`, `evals/multi-model-verify/test_multi_model_verify.py:664`).

There is also a minor record overstatement: it says acquire refuses a label “containing any non-ASCII character,” while trimming occurs before that test, so edge Unicode whitespace is normalized away rather than refused (`.git/parallax/application-checkpoints/2026-07-28-0330-efe4fa0c07d2.md:194`, `tools/kimi-lane-lock.ps1:208`, `tools/kimi-lane-lock.ps1:215`). Change the record to “whose trimmed credential contains a non-printable-ASCII character.”

### UNVERIFIED

The reported 276/1 pytest result, live behavioral 4/4 result, static gates, and successful Write execution were not independently runnable from this seat (`.git/parallax/application-checkpoints/2026-07-28-0330-efe4fa0c07d2.md:155`, `.git/parallax/application-checkpoints/2026-07-28-0330-efe4fa0c07d2.md:158`). The historical `FORCE_COLOR=3` reproduction and claim that every graded case was inert are likewise runtime claims not independently verified here (`.git/parallax/application-checkpoints/2026-07-28-0330-efe4fa0c07d2.md:205`, `.git/parallax/application-checkpoints/2026-07-28-0330-efe4fa0c07d2.md:211`). They do not affect the verdict.

Per-claim: **R1 FIX; R2 PASS; R3 PASS; R4 FIX.**

Overall: **FIX — bind route parsing exclusively to the startup-header block, add missing-field/payload regression tests, and narrow the two record statements identified above.**