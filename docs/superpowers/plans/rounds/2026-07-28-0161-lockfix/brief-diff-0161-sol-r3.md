Round 3, mode diff. Fix re-review. Evidence rules and verdict grammar as before.

POSITION CHANGES. Your R2 scope finding ACCEPTED in full. You were right that I had claimed more than the selector delivered: `test_attestation.py` drives the same PowerShell scripts, hard-selected `powershell`, and ignored `PARALLAX_PS_HOST` — so my "284 passed on BOTH hosts" was one host twice for that module, and the Windows CI job covered only the lock. Both modules now honour the selector and both run under each interpreter in CI. The stale "CI has pwsh only" comment is corrected.

The hook tests in `test_multi_model_verify.py` deliberately stay pwsh-only, and I checked why rather than assuming: `hooks/hooks.json` invokes the hook as `pwsh -NoProfile -NonInteractive -File ...`, so that IS the production host and testing another would not match how it runs. Stated in both the comment and the workflow. Say if you disagree.

Checkpoint corrected: the full-suite host labels no longer claim more than the selector controlled.

NEW MATERIAL IN THIS RANGE, disclosed rather than slipped in. The user asked whether this lane can run several instances at once or whether the backup lane's collision problem applies. I probed it and recorded the answer in `references/model-prompting-notes.md`: this lane's route evidence is the calling process's OWN startup header plus its OWN `--output-last-message` file, so nothing shared is parsed and no lane lock is needed — the structural opposite of the backup lane, whose evidence comes out of one user-global log. Probe: three simultaneous `codex exec` calls, with a fourth review already running, each returning a distinct `session id:` with the canonical model and effort and its own correct reply. The unsafe case is resuming ONE session id twice at once, which the note states.

WHAT WAS APPLIED. Range `f527301..11f28ce`, one commit, 102 diff lines. Diff at C:\Users\Brandon\.claude\jobs\75fb2cba\tmp\diff-0161-r3.txt

284 passed, 1 skipped, default host. The two dual-host modules: 76 passed under PowerShell 7 and 76 under Windows PowerShell 5.1, run separately. Static gates clean. CI on the previous commit `f527301` went GREEN on both jobs — skill-evals and powershell-hosts — which is the first independent confirmation of the fix; this commit's run is not in yet.

Your R1, R3 PASSes and the R4 core-history PASS are not re-opened.

CLAIMS FOR THIS ROUND.

R1. THE HOST GAP IS NOW CLOSED FOR EVERY MODULE THAT SHOULD HAVE IT. Two modules honour the selector, one is exempt with a stated reason. Is the exemption right, and is there a fourth PowerShell-facing surface I have not enumerated — anything else in the suite that spawns a PowerShell host directly or indirectly?

R2. THE CONCURRENCY NOTE IS TRUE AND SUFFICIENTLY BOUNDED. Attack the claim, not the prose: is there ANY shared state a concurrent `codex exec` touches that this lane reads as evidence, and is "distinct sessions safe, same session unsafe" the correct line? I am asserting a negative from a three-call probe plus reading the transport, so treat it as the weakest claim in this range.

R3. THE FIX INTRODUCED NOTHING. Three of the last four rounds across these two releases found a defect inside the previous fix.

R4. THE RECORD MATCHES WHAT WAS ACTUALLY RUN. The checkpoint now separates full-suite runs from the dual-host module runs. Does any number in it still describe a run that did not happen as labelled?

If it holds, say PASS plainly and say it first.
