Reviewed exact final head `c66b2c8478e8cc1efa08d8eb7935d29c07735405`.

## Verification

Both changes are correct.

`Get-AmbiguityReason` cleanly separates the two causes:

- With `AmbiguousCause`, it reports that no measurement or span was established, names the actual failure, and includes neither skills counts nor a skills-boundary claim (`tools/codex-context-probe.ps1:308-326`).
- Without a cause, it retains the genuine boundary/count diagnosis (`tools/codex-context-probe.ps1:327-334`).

I exercised both branches under both PowerShell hosts. The tests pin the same polarity, including the absence of “ambiguous” and “1 opening” from the cause branch (`evals/multi-model-verify/test_codex_context_probe.py:1594-1622`).

Extraction changes no reachable behavior: the existing ambiguity branch still calls `Write-Blocked`, preserving stdout reporting and exit 1 (`tools/codex-context-probe.ps1:793-799`). It merely delegates construction of the reason. The branch remains behind the earlier shape check as documented (`tools/codex-context-probe.ps1:317-320`).

The stale masking descriptions are corrected:

- The code says every known container is blanked (`tools/codex-context-probe.ps1:153-158`).
- The design states that the locator and shape scanner use exactly the same list and order (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:501-515`).
- Amendment 19 accurately records the final diagnostic and documentation changes (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:2735`).

## Sign-off

The sole blocker I named on `53a5652` is cleared. I found no new correctness, fidelity, or documentation defect on this head.

The other lane’s transport failure reduces independent corroboration but is not a defect in the subject revision; it is explicitly preserved in the amendment record (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:2735`). My verdict is based on the final on-disk code, the complete change, and direct cross-host checks of the corrected branches.

I would merge `c66b2c8478e8cc1efa08d8eb7935d29c07735405`.

## Unverified

- I did not rerun the reported 449/1 Python suite.
- I did not rerun the live probe or independently verify its reported hash.
- The cause of the other lane’s prompt truncation remains unexplained.

## Verdicts

1. Applied changes: **PASS**.
2. `Get-AmbiguityReason`: **PASS**.
3. Sign-off blocker: **PASS — cleared**.
4. Merge decision: **PASS — merge**.
5. Terminal verdict for `c66b2c8478e8cc1efa08d8eb7935d29c07735405`: **PASS**.

**OVERALL: PASS**

