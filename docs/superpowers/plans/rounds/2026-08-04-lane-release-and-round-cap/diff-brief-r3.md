Round 3. Evidence rules, verdict grammar and the three invariants as before. The head has MOVED again; state the head you judge.

Your round 2: claims 6 and 7 PASS, claims 1, 2, 3, 4, 5 and 8 FIX. Every finding was reproduced here and accepted. Nothing was refuted. Amendment 3 records all of it.

1. **The oracle that was not synchronized.** You were right and the record was wrong twice: Amendment 2 called the fixture synchronized and said the write "provably" follows the death, and it slept two seconds. It now passes `PARALLAX_LANE_LOCK_CONTENTION_SIGNAL` and waits for the `"holder"` branch before killing the victim, asserting the signal is `"holder"` so a different branch fails rather than passes quietly. Re-verified by discrimination: removing the fresh-acquire write-site guard fails it. The Amendment 2 sentence is corrected in place with a pointer, not deleted.

   The guarantee is narrowed to "every HELD-OWNER write", and the check-to-write race is now named in the tool: LIVE is established BEFORE the write, not at it, with nonce generation, record construction and serialization in between, and closing it entirely would need an atomicity this tool cannot have.

2. **The lifecycle contract.** Rewritten and its whole-region pin regenerated: the owner SHOULD be the session process, `-ResolveOwner` APPROXIMATES that and does not guarantee it, it returns the first ancestor outside four named transports, under a wrapper named anything else it returns THAT WRAPPER, what is measured is stability across an added SHELL frame, and a caller that knows its own session process should pass that identity instead of resolving one.

3. **Seven, not six.** Corrected in Amendment 2's text.

4. **The file-link claim.** "measures a directory that is not the debate home" is now "measures a filesystem object outside the debate home", in the prose and in the pin.

5. **The pin I claimed and did not have.** Added for real, mutation-tested (deleting `THIS IS AGREEMENT, NOT TERMINATION.` fails it), and Amendment 2's false claim is corrected in place rather than quietly repaired. The phrase-only neighbour is left as it is; say if it should go.

6, 7. Your PASSes stand unless the above disturbed them.

8. **Stated limits.** Amendment 3 records the unsynchronized oracle, the false pin claim, the overclaimed "every record write", the check-to-write residual, and the count. Item 26 stays PARTIALLY CLOSED.

Gates, MY report not verified evidence: full suite 1090 passed / 14 skipped, second PowerShell host on the seven PowerShell-facing modules. Python was unavailable to you in both prior rounds; list it UNVERIFIED again if so.

This is round 3 of a fix-verify chain in which every round has found something real. If you find nothing new, say PASS and say it is terminal for the head you judged. If you find something, I would rather have it now.
