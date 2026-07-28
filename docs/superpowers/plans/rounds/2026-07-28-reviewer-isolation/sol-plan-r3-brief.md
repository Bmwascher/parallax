Round 3. Evidence rules and verdict grammar as before. Documents are at commit dca4cda on branch 0.17.0-reviewer-isolation; re-read both.

ACCEPTED, all eight FIXes from round 2, and your artifact-versus-wrapper analysis in full. Your closing paragraph named five specific weaknesses of the artifact handoff and all five are now closed. What changed:

Claim 4 and 12, the artifact nobody produced. You were right that it existed only as a parameter. Both preflight paths now pass it: the SKILL.md preflight command is `-WorkDir <dispatch cwd> -SuppressSkills -OverrideOut <verified-override-file> -Json` with a FRESH scratch path, and the mirror script now takes `-OverrideOut`, defaults it to `<MirrorPath>.skills-override.txt`, refuses an existing one for the same reason it refuses an existing mirror, and prints an `override:` line in its record. `-SuppressSkills` without `-OverrideOut` now blocks outright, with `test_suppress_without_an_override_target_blocks`.

Claim 5, byte identity. `Set-Content` is gone. The probe writes `[System.IO.File]::WriteAllBytes` with no terminator and reports `override_sha256`. The dispatch preamble reads the file once, recomputes the hash, throws on mismatch, and passes that in-memory `$override` to `codex exec` on dispatch and resume. The stub now logs each call as a JSON array instead of a space-joined string, and the test pulls the exact `-c` argument out of the second call and compares raw BYTES, asserting there is no trailing newline. `.strip()` and the substring match are both gone.

Claim 1 and 6, the parser. `Get-PromptText` now throws on any content chunk with no `text` field rather than skipping it, with `test_a_content_chunk_without_text_blocks` built from a fixture carrying one valid chunk plus one `input_image` chunk.

Claim 6's empty-result ambiguity. This was the sharpest of the three because the language is what causes it: a function returning a bare `@()` has the array unrolled, so the caller's variable becomes `$null` and a clean repo is indistinguishable from a failed git call. `Get-BackChannelEntry` returns `@{Ok=..; Entries=..}` and `Get-BaselineRaw` returns `@{Ok=..; Lines=..}`. Both call sites check `.Ok`. New `make_clean_repo` fixture with no back-channels, no untracked and no ignored files, plus `test_a_clean_repo_is_not_read_as_a_failed_enumeration` and `test_an_empty_baseline_is_a_legitimate_state`.

Claim 9. The `Get-BackChannelEntry` comment no longer says "at any depth". It states the asymmetry and points at the contract region, with an explicit note not to restate the corrected claim there.

Claim 11, the stale text. The `RECORDED_REPO_DIR` and `repo-agents.workdir` paragraph is deleted; every repo-scoped test calls `localized()`. Task 4 now expects four failures. Task 5's interface names four consumed region ids and five produced. Doctor reports four skill buckets including `unknown_scoped`.

Claim 14. `test_the_two_home_sources_are_counted_separately` asserts 24 user-directory and 5 built-in by path prefix, and the closing prose now says the split is asserted because it is.

Your UNVERIFIED list is accepted unchanged and is correct: you cannot run commands, so every live measurement stays outside your seat.

For this round, focus on three things:

1. Whether any of the round-2 fixes carries a new defect. Five of the last six rounds on this project found one, so this is the highest-yield question and I would rather you found it than the implementer.
2. Whether the hash check actually binds what it claims to. It verifies the FILE against the probe's report, then passes an in-memory value derived from that same read. Is there a gap between what is hashed and what is dispatched, and is the ASCII encoding assumption safe for every path a real machine could produce?
3. Whether the structured `@{Ok=..}` returns are complete. I changed two functions. If any other function in either script can return an empty collection that a caller reads as failure, or a `$null` a caller reads as success, name it.

Verdict per claim on the revised documents, then one overall verdict.
