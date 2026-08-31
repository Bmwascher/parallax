## 1. Required changes

1. Mechanism-section loop — CLOSES

Each iteration now executes `grep -q ... || exit 1`; therefore any missing token terminates the block before a later successful iteration can conceal it. The current unreconciled mechanism section lacks those tool parameters, so it provides the intended red case. [plan:810](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:810) [plan:815](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:815) [design:136](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:136)

CLOSES.

2. Scope-table mapping — CLOSES

The oracle extracts the task value from all five numbered rows and compares the complete list with the exact required mapping. Missing rows, missing task numbers, or five incorrect-but-non-Task-5 values fail. The current table contains Task 4/Task 5 values, establishing the intended red input. [plan:782](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:782) [plan:784](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:784) [design:67](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:67)

CLOSES.

## 2. Sweep

The working base rate is twelve rounds out of twelve; the plan independently says to keep treating the completion class as open. [plan:25](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:25)

I found no new false-completion path after searching cross-act receipts, check ordering, PID reuse, live partial replies, malformed terminal artifacts, wrapper/host failure, and exit-code-only callers. Those shapes are covered by the ordered poll and their named tests. [plan:78](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:78) [plan:83](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:83) [plan:85](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:85) [plan:128](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:128)

I did find a new internal contradiction, making this thirteen rounds out of thirteen for the broader defect classes:

- The hard-kill test stops the tool after `Start-Process` but before `pid` publication and expects `launch-unknown`. [plan:102](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:102) [plan:104](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:104)
- At that point neither the marker nor the external receipt exists: pid and marker come first, and the receipt is published last. [plan:122](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:122) [plan:123](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:123)
- Polling an absent receipt must stop at `no-receipt`; it cannot reach the later `launch-unknown` check. [plan:130](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:130) [plan:132](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:132)

Thus the hard-kill test cannot pass against the specified transaction. `launch-unknown` remains reachable if a previously published receipt points to a directory whose marker subsequently disappears, but not from a kill before receipt publication. The region currently claims the latter. [plan:207](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:207) [plan:216](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:216)

I also found one unpinned transaction requirement. The implementation steps require refusing a pre-existing external receipt and using create-new semantics at final publication, but the receipt-path test covers only equality/containment, while the refused-launch regression deliberately supplies a fresh `R2`. [plan:72](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:72) [plan:77](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:77) [plan:117](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:117) [plan:123](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:123)

## 3. Mechanism revision

The two Round 12 oracle defects were narrowly confined and are closed. No redesign of the launch transaction is justified. The hard-kill contradiction requires aligning the state contract and test with the existing receipt-last mechanism, while receipt freshness needs tests for behavior the mechanism already specifies. [plan:7](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:7) [plan:117](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:117)

## 4. Freeze decision

The plan is not ready to freeze. Smallest sufficient changes:

- Change the hard-kill regression to require an absent receipt and `no-receipt`, never success. Redefine `launch-unknown` as a valid-receipt/missing-marker condition rather than the pre-publication hard-kill result. [plan:102](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:102) [plan:130](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:130)
- State that an interrupted `-Launch` with no receipt can still have left an untracked child, so `no-receipt` is not evidence that nothing started. The existing operation region already acknowledges that no on-disk pid can clear this case. [plan:264](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:264)
- Add tests proving an external receipt present before launch blocks before reservation, and a receipt created at the existing hold barrier is not overwritten—the create-new write must fail closed and kill the child. [plan:104](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:104) [plan:123](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:123)

**FIX**