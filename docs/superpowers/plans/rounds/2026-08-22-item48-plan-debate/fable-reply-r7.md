Round 7, Fable lane. Nonce: FABLE-I48-7QX2.

**Round-6 A1: conceded.** The live text carries the separators — alternative 3 reads `&amp;\s*['\"]?[\w\-/\\:.$()\[\]]*\.ps1` (line 406) — and both citations are forward-slashed (344, 351). My round-6 read was of the working tree mid-round, not the pinned blob, and I attributed it to the wrong object. Withdrawn.

**The four fixes, each verified against the live text:**

1. **Staging gates — correct at both sites.** Task 4 Step 7 (1325-1326) and Task 7 Step 5 (1821-1822) both carry `test "$(...)" -eq N || { echo STAGED_WRONG; exit 1; }` followed by `echo STAGED_OK`: the failure branch exits 1, the success path exits 0. The defective `&amp;&amp;`/`||` spelling survives only inside the explanatory warnings (1331-1337, 1826-1828), never as a live command.
2. **Scratch prose — matches the code.** The paragraph (1306-1311) now says `run.py` leaves the four `*-out.*` files on a FAILED run only, deleting them on success, "so that a stage-A adjudication still has the parent's output to read" — exactly what the cleanup block does (1232-1240) and exactly the distinction it should preserve. The count of 5 holds on both paths: the five sources are staged by name, `results.json` stays unstaged until Step 8, and scratch files are untracked on either path, so `git ls-files` never counts them.
3. **Identifier — no stale name survives.** A grep for `EXEMPT_FROM_PREFIX` returns nothing; all three sites read "the exemption in `survey.py`" (1295, 1357, 1807) and none misdescribes the mechanism. One cosmetic splice artifact within this fix's own edit: line 1295-1296 stutters "the exemption in `survey.py` in `survey.py` enforces it" — a duplicated phrase, meaning intact. Fold the two-word deletion into the merge; it gates nothing and is not worth a round.
4. **`first_difference` on named arms — correct for every reachable state.** The expression (1152-1156) returns the first parameter name whose bound value differs; when `child_bound` is not a dict (missing or unparseable) it returns the first name rather than `None`, so a non-measurement can never read as "nothing differed"; `None` occurs only when all three expected values compare equal — and since `child-named.ps1` writes exactly those three keys, a dict that equals on all three IS an arm that did not differ. The table instruction (1269-1274) states the index-vs-name semantics per arm type.

Scope respected: nothing outside the four fixes was swept, and nothing serious surfaced beside them.

PASS
