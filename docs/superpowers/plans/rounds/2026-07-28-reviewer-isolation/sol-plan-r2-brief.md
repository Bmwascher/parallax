Round 2. Evidence rules and verdict grammar as before.

ACCEPTED, all nine FIXes. Each is now in the documents at HEAD of branch 0.17.0-reviewer-isolation. Re-read both files and check whether the fixes hold, and whether any of them introduced a new defect. This project's history says four of its last five review rounds found a defect INSIDE the previous round's fix, so treat "the fix is clean" as the claim under test.

Your claim 4/5/12, the isolation handoff, was the decisive one and it was correct. Verified against my own plan text: the generated override existed only inside the probe's second call and the transport commands carried only the two feature flags, so the reviewer would have received all 29 home and built-in skills while the report said zero. What changed:

- The probe gains `-OverrideOut <file>`, writing the exact value the second pass verified, and reports `override_file`.
- Both transport commands now carry `-c "$(Get-Content -Raw <verified-override-file>)"`, dispatch and resume alike.
- New contract region `verified-override-dispatch` states that a dispatch omitting the override, or carrying a value the probe did not verify, is a transport failure.
- New test `test_the_verified_override_is_written_out_for_the_dispatch` asserts the written value is byte-identical to the one the second pass actually ran with, and `test_the_verified_override_is_what_gets_dispatched` pins the two occurrences in SKILL.md.
- Note: this very debate round was dispatched with `--disable plugins --disable apps` plus the generated override, so the mechanism is exercised, not only specified.

Claim 1, fail closed on unplaceable sources. `Get-SkillScope` no longer defaults to `home`. It returns `unknown` for an empty string, a non-rooted path, a UNC path, and any path containing `/../`, and the top level blocks on a non-empty unknown bucket. Parametrized cases added for all four shapes plus a new `unknown_scoped` report key.

Claim 6, the three false-clean paths.
- The adversarial fixture is replaced by two: `missing-block-plugins-off.json` has the plugin and apps blocks ABSENT so nothing else explains the missing skills block and the feature check cannot fire, and `malformed-block.json` has the block PRESENT with entry lines the parser cannot match, so it parses to zero.
- The first pass now blocks on a missing skills block, because 29 entries were measured in that state and absence proves suppression only on the SECOND pass.
- The second pass now requires `BlockPresent` to be FALSE, not merely a zero count.
- HEAD, baseline and manifest all have explicit failure checks; `Get-ContentManifest` returns an Error instead of silently skipping a path with no file behind it.

Claim 9, the contradiction. SKILL.md:69's "at any depth" is corrected in the same step rather than left standing beside the new limit. The ignored half is kept and dated; the depth half is split into a new contract region `enumeration-depth-asymmetry` stating that `*AGENTS.md` reaches any depth and `.agents/*` is root-anchored.

Claim 11, fixtures.
- Raw recordings now stay in the scratchpad. Committed fixtures are hand-normalized to fabricated paths under `C:/fixture/...` with the instruction body replaced. You were right that committing the raw prompt would put the author's global AGENTS.md and home skills layout into a public repo.
- `repo-agents.workdir` is gone. Tests rewrite the literal `C:/fixture/repo` to their own `tmp_path`, so nothing depends on a path that exists on one machine.
- `flagged.json` is in the Task 1 file list and the File Structure table.

Claim 13, the mirror script.
- `Get-BaselinePath` is split into `Get-BaselineRaw`, which returns the verbatim status capture including codes and is what the record prints as `baseline:`, and `Get-ManifestSubject`, which derives the manifest's paths. New test `test_the_baseline_is_the_raw_status_capture` requires `??` and `!!` prefixes in the printed block.
- Rename and copy are tested in BOTH status columns.
- Probed here rather than reasoned: `git mv a.txt b.txt` reports `R  a.txt -> b.txt`, and deleting the destination afterwards reports `RD a.txt -> b.txt`. An `RD` destination does not exist, so that entry now BLOCKS rather than being skipped, with `test_a_rename_whose_destination_was_deleted_blocks`.
- The overlap guard runs before anything is created or deleted and rejects a mirror path equal to, inside, or containing the repo root, parametrized over all three.

Claim 14, counts. All buckets are asserted, not the total alone: 60 total, 31 plugin-cache, 29 home, 0 repo, 0 unknown, plus per-fixture assertions for `flagged.json`, `repo-agents.json` and `malformed-block.json`. The live machine numbers are provenance in the design document, not test inputs.

Claim 12's control list. The design named three controls and the brief text named two. It now names three: the flags, the generated override the dispatch actually carries, and the second measurement.

Your UNVERIFIED list is accepted as correct and is not disputed. You cannot run commands, so every live measurement stays unverified from your seat. I am not asking you to take them on trust: attack the reasoning built on them.

Two things I did NOT change, and why:

1. I did not widen `.agents/*` to `*.agents/*`. The measurement says a nested entry is not advertised by codex-cli 0.144.1, so widening now would add enumeration cost for an unreachable case and would not be covered by any observation. It is recorded as an accepted limit with a test that fails if either half changes.
2. I did not fold the probe and the dispatch into one wrapper. The transport commands are a locked live-verified contract with their own test module, and a wrapper would become a second authority over them. The handoff is instead an artifact file plus a pinned contract region. Tell me if you think the artifact handoff is weaker than a wrapper, and why.

Verdict per claim on the revised documents, then one overall verdict.
