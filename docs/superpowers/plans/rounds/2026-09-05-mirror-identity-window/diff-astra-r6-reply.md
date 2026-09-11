1. **CONFIRMED — merge-blocking: wildcard resolution can change the validated mirror destination into the source.**  
   The overlap guard compares the supplied spelling, but after creation the script assigns `$MirrorPath` from non-literal `Resolve-Path`. Square brackets are interpreted as a wildcard there. ([Comparison](C:/Temp/pxd1/tools/new-review-mirror.ps1:1419), [reassignment](C:/Temp/pxd1/tools/new-review-mirror.ps1:1984))

   On **both hosts**, I executed the construction prefix with removal and creation intercepted, supplying:

   - RepoRoot: `C:\Temp\pxd1`
   - MirrorPath: `C:\Temp\pxd[1]`

   Execution passed the source measurements and reached the copy boundary with **both arguments equal to `C:\Temp\pxd1`**. The next statement copies using that reassigned destination. This establishes destination substitution after validation; **I performed no deletion, creation, or copy**. ([Copy statement](C:/Temp/pxd1/tools/new-review-mirror.ps1:2014))

   **Change:** use literal path semantics consistently, including source-root resolution, and fail on resolution errors. Add a regression with a bracketed destination and an existing sibling matching its wildcard spelling. This is more consequential than a bracket-name usability limitation. ([Source resolution](C:/Temp/pxd1/tools/new-review-mirror.ps1:1052))

2. **CONFIRMED — merge-blocking: both character classes omit the documented tilde.**  
   The comment lists `~`, but neither the basename character class nor the extension class includes it. The required separator outside the basename class does not cover another tilde within the name. ([Comment and predicates](C:/Temp/pxd1/tools/new-review-mirror.ps1:1384))

   I called Windows’ native short-name generator in memory on both hosts, then passed its output to the shipped helper:

   | Long name | Generated short name | Helper |
   |---|---|---|
   | `AB~CDELongName` | `AB~CDE~1` | Accepts |
   | `LongFilename.a~b` | `LONGFI~1.A~B` | Accepts |

   These are measured generated names, beyond the manually assigned aliases deferred in item 99. I did not install these aliases on disk or demonstrate an overlapping build through them. ([Native generator documentation](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntifs/nf-ntifs-rtlgenerate8dot3name), [helper predicates](C:/Temp/pxd1/tools/new-review-mirror.ps1:1386))

   **Change:** include `~` in both classes and test each declared character in both positions. My 156 such probes per host found only these two tilde omissions; apostrophe, backtick, caret, and hyphen behaved correctly.

3. **CONFIRMED — merge-blocking validation fix: the bracket exception is another negative-only oracle.**  
   Its sole assertion is that the short-name diagnostic is absent. Exit 2 with empty stdout passes without establishing that the spelling guard ran. The accompanying claim that this is “asserted at the guard” is therefore unsupported. ([Exception and assertion](C:/Temp/pxd1/evals/multi-model-verify/test_review_mirror.py:1988))

   **The narrower test scope is defensible; this oracle is not.** Extract the helper, require successful execution, and positively assert its `$null` result through an explicit acceptance marker. The seven buildable cases now correctly call `assert_built`. ([Fixed loop](C:/Temp/pxd1/evals/multi-model-verify/test_review_mirror.py:1983))

   I would also avoid treating brackets as an established robocopy limitation. List-only robocopy probes accepted bracketed destinations on both hosts. Those probes do not establish successful copying, but finding 1 identifies a concrete problem earlier in this script. Preserve the reported exit-16 observation while investigating its cause. ([Current attribution](C:/Temp/pxd1/docs/superpowers/plans/rounds/2026-09-05-mirror-identity-window/diff-debate.md:429))

4. **CONFIRMED — nonblocking editorial cleanup: the obsolete category-test explanation was not deleted.**  
   It still says the output assertion makes a doubled fixture impossible to pass, immediately before the correction saying that comment “used to” make the claim. The debate record nevertheless says it is gone. ([Surviving explanation](C:/Temp/pxd1/evals/multi-model-verify/test_review_mirror.py:2366), [adjacent correction](C:/Temp/pxd1/evals/multi-model-verify/test_review_mirror.py:2375), [record claim](C:/Temp/pxd1/docs/superpowers/plans/rounds/2026-09-05-mirror-identity-window/diff-debate.md:440))

   **Change:** remove the obsolete paragraph. The fixture read-back assertions themselves remain correct. ([Assertions](C:/Temp/pxd1/evals/multi-model-verify/test_review_mirror.py:2382))

The other requested editorial corrections hold: the doubled-backslash account is corrected in place, the round-4 split distinguishes refusal from accepted alias, item 98 narrows its claim, and item 99 records the outstanding experiment. ([Backslash account](C:/Temp/pxd1/docs/superpowers/plans/rounds/2026-09-05-mirror-identity-window/diff-debate.md:252), [round-4 summary](C:/Temp/pxd1/docs/superpowers/plans/rounds/2026-09-05-mirror-identity-window/diff-debate.md:312), [item 98](C:/Temp/pxd1/BACKLOG.md:4292), [item 99](C:/Temp/pxd1/BACKLOG.md:4327))

The sweep covered absence-only assertions, path resolution versus later mutation/copy operands, character-class escaping, and superseded measurement/count claims. Findings 1–4 are the instances found; I found no additional self-counting defect or escaping-created dead code.

I did not rerun pytest or CI, perform real filesystem mutations, reproduce the exact bracketed build failure, or exhaustively test OEM/non-ASCII aliases and network paths. PowerShell versions tested were **7.6.6 and 5.1.26100.9168**.

**Verdict: FIX — destination substitution, missed generated aliases, and the bracket oracle block merge; the remaining stale comment is nonblocking cleanup.**