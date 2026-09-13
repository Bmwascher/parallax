# Fable R1 raw reply, range 2772e4e..2ff9e5f, 2026-09-13

(Retained verbatim from the agent's final message; the harness output file was empty.)

### Strengths

- The dispatch-line change is stated as a version-bound measurement, not a property of agy: `C:\Users\Brandon\Documents\parallax\agents\flash-implementer.md:82-88` names 1.2.0 and 1.2.2 and the exact denied `run_command` call, and the probe record's three runs (P1/P2/P3) support every clause of it.
- The carve-out sentence sits inside the ban paragraph it qualifies (`agents/flash-implementer.md:128-131`) and is pinned by exact fragment (`evals/multi-model-verify/test_flash_implementer.py:141`), so a reader of the ban cannot read the dispatch line as a violation and a regression cannot silently drop the qualification.
- The new mode-line route check turns the flag into evidence rather than configuration: `agents/flash-implementer.md:102-105` blocks a landed edit whose log lacks `Print mode: applying agent mode accept-edits`, which is the right direction for the lane's one write-enabling switch.
- The conversation-id fix closes a real false-block path and adds a wildcard guard in the same sentence: `agents/flash-implementer.md:106-110` names the empty `conversationID=""` field and states "an empty id is a missing transcript, not a wildcard". `test_flash_implementer.py:91-93` pins both the new source line and the absence of the old parse instruction.
- Backlog item 36 is updated without being closed: `C:\Users\Brandon\Documents\parallax\BACKLOG.md:1204-1215` records that `true` is not sufficient on 1.2.2, keeps necessity open as question 1, and `BACKLOG.md:1227-1230` adds new-file and delete writes as unmeasured, matching the record's Caveats exactly.
- `commands/doctor.md:176-180` states the measurement and explicitly says "this check does not assert it", so the doctor does not overreach into the agent file's contract.
- `tools/check-drift.ps1:135` replaces a line-number pointer with a section pointer, which is the right fix for a comment that was already three edits stale.
- The Windows-spelling log-path rule (`agents/flash-implementer.md:90-93`) comes from a real failure (P1 produced no log) and is pinned (`test_flash_implementer.py:55`).

### Issues

#### Critical

None.

#### Important

1. **The central pin does not lock the flag to the dispatch line.** `C:\Users\Brandon\Documents\parallax\evals\multi-model-verify\test_flash_implementer.py:50-51` asserts `"--mode accept-edits" in body` and `count >= 2`. The agent file carries the literal at lines 81 (dispatch line), 82 (prose) and 128 (carve-out). Deleting it from line 81 alone leaves two occurrences and every pin green, while the lane reverts to blocking on every dispatch. The comment at `test_flash_implementer.py:45-49` says the pin exists because the flag "is on the dispatch line where every reader sees it", but nothing asserts that. One additional pin on the single physical line 81, for example `--model gemini-3.8-flash-high --mode accept-edits --add-dir`, closes it. (Pre-existing `--add-dir` / `--log-file` pins share the weakness, but this branch's whole purpose is that one token on that one line.)

2. **"A listed parent covers its child worktrees" is stated as a measured mechanism from a run that does not isolate it.** `C:\Users\Brandon\Documents\parallax\agents\flash-implementer.md:39-43` and the Lane note at `:154-157` ("is enough for every worktree under it") rest on the commit-message measurement: parent listed, unlisted child, edit landed, settings unchanged. That run was made with `allowNonWorkspaceAccess=true` in place (the lane's carried value; the design spec at `docs/superpowers/specs/2026-07-25-flash-implementer-design.md:57-61` shows trust and `true` were set together from the start and never separated). The observation is equally explained by `true` permitting the write, or by headless 1.2.2 not consulting `trustedWorkspaces` against `--add-dir` at all. Item 36 question 2 (`BACKLOG.md:1227`) is literally "what does `true` permit OUTSIDE the workspace", and this run is a data point on it that item 36 does not mention. The discriminating run is one dispatch into a directory with NO listed ancestor, same flags. Failure direction if the claim is wrong is loud (preflight 2 passes, agy soft-denies, run blocks), so this is a contract-basis defect rather than a safety one, but the text promises the user an operational configuration on evidence that does not yet distinguish it. Fix: either run the control and cite it, or narrow lines 40-42 and 155-157 to what was observed ("an edit landed in an unlisted worktree under a listed parent, with `true` set; the mechanism is not isolated") and add the run to item 36.

#### Minor

3. **Ancestor comparison semantics are underspecified for a Bash-only Haiku wrapper.** `agents/flash-implementer.md:52-54` says "compared as normalized absolute paths" and no more. Unstated: case folding (NTFS is case-insensitive and agy writes entries with whatever casing the interactive cwd had), separator normalization (Git Bash `pwd` yields `/c/Users/...` while settings hold `C:\Users\...`, and the same file warns at line 91 that these spellings are not interchangeable to agy), trailing separators, and component-boundary matching (`C:\Users\Brandon\Documents\parallax` must not count as an ancestor of `...\parallax-2`; a bare string-prefix test accepts it). All four are implementable in Bash (`cygpath -m`, lowercase, append a separator before the prefix test), but the wrapper is zero-judgment by design and will pick one. Either false direction is loud, hence Minor.

4. **"Every write" generalizes one in-place edit per run.** `agents/flash-implementer.md:83` ("without it every write is soft-denied") and `commands/doctor.md:177` ("print mode denied every write") describe P3 and the 2026-09-12 block, each a single `ReplaceFileContent` denial. New-file writes and deletes are declared unmeasured under the flag at `BACKLOG.md:1228-1230`; they are equally unmeasured without it. "Every write" should read "the lane's edit" or "in-place edits".

5. **The design spec now asserts the opposite of the shipped contract and is not corrected in place.** `C:\Users\Brandon\Documents\parallax\docs\superpowers\specs\2026-07-25-flash-implementer-design.md:54` ("`--mode accept-edits` does NOT apply in print mode"), `:71` and `:241` ("accept-edits provably does not") were true on 1.1.7 and are false on 1.2.0+. No live pin references the spec (grep for `flash-implementer-design` outside plans: no matches), so nothing on the range breaks, but a refuted sentence left standing is the pattern the repo's own record practice forbids. A dated one-line correction at each of the three sites, pointing at the 1.2.2 probe record, is enough. Separately, this reversal is the strongest evidence the flag's behavior is version-dependent, and neither `agents/flash-implementer.md:82-85` nor item 36 records that it was once inert; worth one clause so a future agy drift note has context.

6. **The narrowing clause of the carve-out is unpinned.** `agents/flash-implementer.md:130-131` "No other `--mode` value is used in this lane" is what keeps the carve-out from becoming a general `--mode` allowance, and nothing in `test_flash_implementer.py` locks it. A pin on the dispatch line (finding 1) covers most of the risk; pinning this fragment too costs one line.

Named risk checks performed, one each: whole agent file read for any sentence contradicting the new mode (none found; lines 75-76 and 122-123 on command soft-deny remain true under the flag); repo-wide grep for "main checkout", "sole live-verification", "Task 6", "worktree trust story" outside plans (only the historical spec and the test comment); repo-wide grep for `conversationID` / `Print mode: starting` parse instructions (only the historical spec); grep for any live surface stating print mode denies all writes (none); contract markers in the agent file (only `shared-contract:start/end` at lines 19/34, which enclose no changed text).

### Ledger minors triage

No ledger for this branch (the brief states none exists); skipped.

### Assessment

Ready to merge: With fixes

The range is coherent and each measurement is version-bound and traceable to the probe record; the two Important items are a one-line pin that lets the branch's own central change regress unnoticed, and a mechanism claim in the agent text that the cited run does not isolate from `allowNonWorkspaceAccess=true`. Both are small edits (or one control run) and neither changes the dispatch line itself.
