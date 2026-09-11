1. **CONFIRMED — the source root’s ancestors remain outside the alias guard.**  
   The script checks whether the source root **itself** is a reparse point, but checks ancestors only for the mirror, override, sidecar, extra inputs, and followed targets. A junction above an otherwise ordinary source directory therefore escapes protection. ([Source-root check](C:/Temp/pxd1/tools/new-review-mirror.ps1:1519), [output ancestor checks](C:/Temp/pxd1/tools/new-review-mirror.ps1:1748), [target check](C:/Temp/pxd1/tools/new-review-mirror.ps1:1777), [extra-input check](C:/Temp/pxd1/tools/new-review-mirror.ps1:1855))

   On **both hosts**, I executed the construction prefix with `Remove-Item` intercepted, using these paths through the existing `My Documents` junction:

   - RepoRoot: `C:\Users\Brandon\My Documents\parallax\skills`
   - MirrorPath: `C:\Users\Brandon\Documents\parallax\skills`

   Both reached the recursive-removal statement against the second path. The lexical overlap comparison accepts these different strings. **This proves unsafe reachability; I did not execute removal or demonstrate deletion.** ([Overlap comparison](C:/Temp/pxd1/tools/new-review-mirror.ps1:1378), [removal](C:/Temp/pxd1/tools/new-review-mirror.ps1:1918))

   **Change:** apply `Test-PathOrAncestorIsLink` to RepoRoot before destructive operations, with a regression placing the junction above the source root. The spelling helper covers this operand; the separate alias guard does not.

2. **CONFIRMED — the anchored regex still rejects names that cannot be 8.3 aliases.**  
   The pattern independently permits six characters before the tilde and six digits after it. On both hosts, the helper refused `backup~2026`, `ABCDEF~123456`, and `a b~1`. These violate the eight-character basename limit or the prohibition on spaces in an 8.3 name. ([Regex](C:/Temp/pxd1/tools/new-review-mirror.ps1:1347), [Microsoft’s 8.3 specification](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-fscc/18e63b13-ba43-4f5f-a5b7-11e871b71f14))

   Calling this helper on discovered targets extends that false refusal to an ordinary junction whose real target has one of those legitimate long names. That consequence follows directly from the unconditional target refusal; I did not create and build that junction fixture. ([Target validation](C:/Temp/pxd1/tools/new-review-mirror.ps1:1769))

   **Change:** bound the **whole basename** to eight characters and constrain short-name characters. Add accepted cases such as `backup~2026` and `a b~1`, alongside refused cases such as `ABCDE~10` and `ABCD~100`. Those latter two already matched in my probes. Your “more than six characters before the tilde” premise cannot describe an eight-character basename containing a tilde and at least one digit.

3. **SUSPECTED — short aliases without a tilde can bypass the spelling policy.**  
   The helper admits `LONGFILE.TXT`; its short-name checks require a tilde. Microsoft explicitly documents assigning `longfile.txt` as the short name of `longfilename.txt`. Thus “does not resemble the generated tilde form” does not establish that a spelling is comparable. ([Helper](C:/Temp/pxd1/tools/new-review-mirror.ps1:1347), [Microsoft’s `setshortname` example](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/fsutil-file))

   **Uncompleted check:** assign that alias to a disposable directory and demonstrate the overlapping construction invocation. This read-only session cannot perform the setup.

   **Change:** resolve short aliases before identity-sensitive comparisons, or establish an enforceable filesystem restriction. Further tilde-pattern refinement cannot distinguish an assigned plain short alias from an ordinary name.

4. **CONFIRMED — the stream-root test still records a false independent refusal mechanism.**  
   Its docstring says `Test-Path` raises `ItemExistsNotSupportedError` and that this alone is enough to refuse the input. For `C:\Temp\pxd1:$I30:$INDEX_ALLOCATION`, my direct probe returned **True on both hosts**. PowerShell 5.1 also printed that error and continued; PowerShell 7 printed no error. The script’s initial existence conditional therefore does not refuse this case. ([Docstring](C:/Temp/pxd1/evals/multi-model-verify/test_review_mirror.py:1952), [existence conditional](C:/Temp/pxd1/tools/new-review-mirror.ps1:1048))

   The positive test assertion correctly requires the colon diagnostic. **Change:** retain that assertion and describe the colon guard as the demonstrated refusal mechanism; remove “Either is enough.” ([Assertion](C:/Temp/pxd1/evals/multi-model-verify/test_review_mirror.py:1961))

5. **CONFIRMED — the doubled-backslash account and validation-order comment overclaim.**  
   “Every component check … was dead” is false. In an in-memory mutant restoring the doubled `Replace`, both hosts still refused `C:\Temp\mirror.` and `C:/Temp/ABC~1`. Splitting an unchanged string still produces a component, and existing forward slashes still split. The demonstrated failure is loss of interior backslash-separated component checking. ([Code comment](C:/Temp/pxd1/tools/new-review-mirror.ps1:1322), [debate account](C:/Temp/pxd1/docs/superpowers/plans/rounds/2026-09-05-mirror-identity-window/diff-debate.md:245))

   “Nothing else would have” is also too strong: the dotted-ancestor override regression exercises precisely that lost check and positively requires its diagnostic. ([Regression](C:/Temp/pxd1/evals/multi-model-verify/test_review_mirror.py:2002))

   Separately, followed-target validation does **not** precede “any comparison”: target equality, containment, and duplicate-target checks occur earlier. ([Claim](C:/Temp/pxd1/tools/new-review-mirror.ps1:1763), [earlier comparisons](C:/Temp/pxd1/tools/new-review-mirror.ps1:1655))

   **Change:** narrow the incident description, remove the exclusive test-catcher claim, and either validate immediately after target resolution or say “before the destination-overlap comparisons.”

6. **CONFIRMED — the category test’s claimed protection against a doubled fixture escape is false.**  
   Its comment says a doubled escape in the fixture “could never pass.” The current assertions accept the literal text `odd\u0890name.txt`, however. On both hosts, I verified that the formatter produces identical output for that literal ASCII string and for a name containing actual U+0890. Doubling the fixture escape can therefore stop exercising Unicode classification while satisfying the output assertions. ([Fixture claim](C:/Temp/pxd1/evals/multi-model-verify/test_review_mirror.py:2288), [assertions](C:/Temp/pxd1/evals/multi-model-verify/test_review_mirror.py:2303), [formatter](C:/Temp/pxd1/tools/new-review-mirror.ps1:928))

   The current fixture is correctly spelled. **Change:** assert that the seeded/read-back fixture contains `chr(0x0890)` and lacks the literal escape, then retain the positive rendering assertions. Apply the same fixture check to the neighboring control-character test. ([Neighboring fixture](C:/Temp/pxd1/evals/multi-model-verify/test_review_mirror.py:2261))

7. **CONFIRMED — several record details remain inaccurate.**  
   Item 98 and the debate account attribute the non-terminating-removal simulation to both hosts in round 3. The retained invocation substantiates PowerShell 7 only. I completed that simulation on both hosts this round and observed continuation to the intercepted `New-Item`, so the behavior now has both-host evidence, but the historical attribution needs correction. ([Item 98](C:/Temp/pxd1/BACKLOG.md:4281), [debate account](C:/Temp/pxd1/docs/superpowers/plans/rounds/2026-09-05-mirror-identity-window/diff-debate.md:223), [retained invocation](C:/Temp/pxd1/docs/superpowers/plans/rounds/2026-09-05-mirror-identity-window/diff-astra-r3-transcript.txt:1442))

   The live-measurement test also calls itself the **third** oracle instance beside the **second**, whereas its neighbor identifies itself as third and the debate correctly identifies the live-measurement case as fourth. ([Stale comment](C:/Temp/pxd1/evals/multi-model-verify/test_review_mirror.py:3089), [neighbor](C:/Temp/pxd1/evals/multi-model-verify/test_review_mirror.py:3056), [record](C:/Temp/pxd1/docs/superpowers/plans/rounds/2026-09-05-mirror-identity-window/diff-debate.md:229))

   Finally, the round-1 account substitutes “control-character test” for the **runtime-category test** in the negative-only pair. The retained reply distinguishes that pair from the separate substring weakness. ([Account](C:/Temp/pxd1/docs/superpowers/plans/rounds/2026-09-05-mirror-identity-window/diff-debate.md:77), [original finding](C:/Temp/pxd1/docs/superpowers/plans/rounds/2026-09-05-mirror-identity-window/diff-astra-r1-reply.md:10))

   **Change:** correct the test name and measurement provenance; remove incidental ordinals from test comments.

The remaining fixes checked out: the helper now uses a single backslash, its colon rule handled the ordinary UNC/relative/drive-relative probes, and extra inputs and followed targets call it. The live-measurement oracle now requires exit 1 and its specific diagnostic. ([Helper](C:/Temp/pxd1/tools/new-review-mirror.ps1:1312), [split](C:/Temp/pxd1/tools/new-review-mirror.ps1:1326), [extra inputs](C:/Temp/pxd1/tools/new-review-mirror.ps1:1813), [targets](C:/Temp/pxd1/tools/new-review-mirror.ps1:1769), [oracle](C:/Temp/pxd1/evals/multi-model-verify/test_review_mirror.py:3092))

My sweep searched nonzero/absence-only assertions, mutation and copy destinations, helper call sites, lexical comparisons, escape literals, and measurement/count claims. I found no additional negative-only refusal oracle beyond the fixture weakness above, no additional shipped doubled-backslash defect, and no new self-counting-document defect. The item 93 amendment now appropriately limits its conclusion to the measured runs. ([Positive rendering oracles](C:/Temp/pxd1/evals/multi-model-verify/test_review_mirror.py:2248), [count policy](C:/Temp/pxd1/docs/superpowers/plans/rounds/2026-09-05-mirror-identity-window/gate-results.md:93), [measurement limits](C:/Temp/pxd1/BACKLOG.md:4005))

I did **not** rerun pytest or behavioral evals, perform real deletion/denial experiments, create junction or short-alias fixtures, or exhaustively test network shares and drive mappings. The filesystem remained unchanged.

**Verdict: FIX — the source-ancestor alias bypass and valid-name refusals are confirmed; the record and test-fixture claims also need correction.**