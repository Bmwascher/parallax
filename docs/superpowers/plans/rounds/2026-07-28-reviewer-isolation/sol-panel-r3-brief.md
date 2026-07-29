Panel round 3 (your round 11). THE SUBJECT REVISION HAS MOVED.

New head: `42c942143b7c3d1c319e407c542991bb8fa0637c`
Fix range: `50c82029f178c747467e5a597b281731f70e4188..42c9421`
Base of the whole branch is unchanged: `e2e9242c6153d69e9a4f0c49055e7bf8c81a1dd0`

Your round-10 FIX has been applied. A terminal verdict now counts only
when it cites the new head.

## What was applied

Five fixes, all from the panel. Read the current code yourself; this list
tells you where to look, not what you will find.

1. The suppression pass keeps its own instruction report and blocks on a
   project doc. Placed AFTER the two suppression rules, which is the
   precedence you recommended.
2. Skills-block PRESENCE is judged on the masked structural text; entries
   are still parsed from the raw text. This closes a defect ANOTHER lane
   raised: on a machine whose global `AGENTS.md` names
   `<skills_instructions>` in prose, the suppression proof read that as a
   surviving block and stopped every review with "suppression did not
   take". The branch's own
   `test_a_known_literal_quoted_in_the_global_body_does_not_block`
   declares that configuration legitimate, but its suppression fixture
   carried no quote, so no test reached the second render.
3. The `--- project-doc ---` delimiter is matched only where it stands
   alone on its own line. Masking is not available there, because the
   real delimiter lives inside the same body being masked.
4. `global_agents_md` now reports whether the resolved global file
   exists. It previously carried the instructions block's presence, which
   `Test-PromptShape` already refuses to let be false, so the field was a
   constant with a measurement's name.
5. Finding B: both mirror captures now run through one helper that passes
   `-c core.quotepath=false` and pins `[Console]::OutputEncoding` to
   UTF-8 with a `finally` restore. A path that STILL arrives quoted is an
   explicit stop in both consumers rather than a trim-and-resolve.

I did NOT take your option 7 (`-z` with raw byte capture). Reason:
`git status --porcelain -z` emits a rename as two NUL-separated fields in
reverse order with no ` -> ` separator, which would rewrite the rename
and copy rules that are themselves pinned by probed behaviour. Refute
that reasoning if it is wrong.

## Evidence already gathered (verify, do not trust)

- Both hosts: 422 passed / 1 skipped, up from 411.
- Live probe both hosts: exit 0, clean, 29 -> 0, override sha256
  `180f09f50d282b5603f1c0d0621f2913ff66c8b7798e7a2f3b7fe8d41f432bb8`,
  unchanged across every round of this cycle.
- Live mirror build on both hosts with an accented back-channel planted:
  the back-channel is deleted, the accented subject file reaches the
  baseline and the manifest with hash `6a51a698...`, the real tree is
  untouched.
- Each script was reverted to its pre-fix state and the new cases re-run
  against it, so the regressions are red-before-green rather than assumed.

## Your task this round

1. Verify each of the five fixes does what it claims, at the code.
2. **Attack fix 2 hardest.** It moves a check from raw text to masked
   text, which is the direction that can pay for a false block with a
   false clean. Can any input now reach a `clean` report while a real
   skills container survives suppression? The masking function is
   `Hide-KnownContainer`; presence goes through `Get-StructuralText`.
3. Attack fix 3 the same way: can a real project doc now go unseen?
4. Confirm fix 5 closes the silent manifest-collision path you found, and
   that the console-encoding restore cannot leak state on either host.
5. Look for a defect INSIDE any of the five fixes. Every round of this
   cycle but one has found the previous round's fix carrying the next
   round's defect.
6. Terminal verdict against head `42c942143b7c3d1c319e407c542991bb8fa0637c`.

Cite `path:line`. Anything you did not check goes under `## Unverified`.
