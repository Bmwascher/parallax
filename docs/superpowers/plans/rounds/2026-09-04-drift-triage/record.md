# Drift triage 2026-09-04: pending runs 2026-08-18 and 2026-08-25 (and the killed 2026-09-01 run)

Subject: branch `drift-repin-superpowers-6.3.0`, base `53de9cd` (main at 0.30.0), head `65b24a5`.
Finding class: `[WARN] installed superpowers code-reviewer.md (6.3.0) no longer matches the pinned fixture`, reported three weeks running; the headless auto-triage produced fix branches `drift/2026-08-18_131711-26643` and `drift/2026-08-25_131707-36771` (both: re-pin at 6.3.0, gates green, cross-review unavailable). The 2026-09-01 run was killed mid auto-triage (task last result 0xC000013A) and left nothing; filed as item 86.

Disposition: merged the 2026-08-25 fix branch, took the fuller state-machine literal update from the 2026-08-18 branch, deleted the retired 6.2.0 fixture, filed item 86. The changelog lines in all three reports were read against the four exposure surfaces (hook matcher and JSON, cache layout, Skill loading, headless runner): none touches a surface in a way that needs a change. Notable ones: 2.1.251 "hooks silently treating a stdout {..} object that is not valid JSON as plain text; now a hook error" (the backlog hooks print json.dumps output, valid by construction); 2.1.234 "plugin-cache cleanup" and 2.1.251 "duplicate SHA-named cache directories" (cache layout, informational, item 58 owns the pile); 2.1.251 PreModelSwitch/PostModelSwitch hook events (additive).

Review: Fable whole-branch review `fable-review-53de9cd..65b24a5.md`: Ready to merge Yes, no findings. Sol R1 (fresh, session 01a06ebe-b725-7ad3-b5c4-27e6cbe12433, mirror kerev417, probe clean, brief sha 34daf2ae, bound clean and sealed): PASS on all six claims and the range, no findings; sweep found no missed reader of the fixture name. Session adjudication: PASS, dry round, debate closed at round 1.

Gates: see the closing commit message and the attestation for this head.
