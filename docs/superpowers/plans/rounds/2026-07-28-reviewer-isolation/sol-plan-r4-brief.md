Round 4, the cap. Evidence rules and verdict grammar as before. Documents are at commit f6f7ba8 plus one uncommitted change described below; re-read both.

ACCEPTED, all five FIXes from round 3.

Claim 4, 5, 6 and 12, the ASCII defect. You were right and this was the sharpest find of the debate, because the hash made the corruption look verified. `Encoding]::ASCII` is gone. The probe writes with `New-Object System.Text.UTF8Encoding($false, $true)`, no BOM and throwOnInvalidBytes, hashes those raw bytes, and reports `override_sha256` over them. The dispatch preamble is now `ReadAllBytes`, hash the bytes, compare, then strict-decode the SAME bytes with the same UTF8Encoding. New `test_a_non_ascii_skill_path_survives_the_round_trip` uses a path containing `café-naïve`, asserts the UTF-8 bytes are present, asserts no `?` appears, and asserts the reported hash matches the file. A new pin forbids `Encoding]::ASCII.GetBytes($override)` from reappearing.

Claim 5's round-lifetime gap. Also correct: rounds are separate shells, so a `$override` from round 1 does not exist in round 3. Both transport blocks carry the whole preamble inline, and the pins now require two complete preambles rather than two uses of a variable: two `ReadAllBytes` calls, two hash comparisons, and two strict decodes.

Claim 11, the consumers. The shared `run_probe` helper now passes `-OverrideOut` alongside `-SuppressSkills`, and so do the live Task 2 command and doctor check 9. The design's doctor deliverable says four buckets. The probe now reports `global_agents_md_path`, resolved from `CODEX_HOME` or the conventional home location and reported ONLY when the file is actually there; doctor prints it when non-empty and otherwise says the prompt carries a global instruction block whose source the prompt does not name. It does not guess, because the reviewer's own self-report of that path was wrong on 2026-07-28.

Claim 11's override containment guard. Added, and placed with the mirror-path guard at the top of the script rather than beside the probe, because `-SkipProbe` would otherwise bypass it. Parametrized over same, inside and parent for both the repo and the mirror, with `test_an_overlapping_override_path_is_refused`. New `test_the_probe_runs_and_the_default_override_is_recorded` is the only mirror test that does not pass `-SkipProbe`, and it proves the default artifact is allocated, written, hashed and printed.

Claim 1 and 6, unknown instruction families. Accepted, and GENERALIZED beyond what you proposed, which is the one thing in this round I want you to attack rather than confirm. You suggested blocking unrecognized `*_instructions` blocks. That suffix does not cover the families we already measured: `recommended_plugins`, `environment_context` and `multi_agent_mode` all lack it, and `permissions instructions` uses a space rather than an underscore. So instead of a suffix rule there is now an ALLOWLIST of every top-level block observed in the real prompt on 2026-07-28, and `Get-UnknownPromptBlock` blocks on any tag opening at the start of a line that is not in it.

Attack that specifically:

1. Is the allowlist the right generalization, or does it trade one silent gap for a noisy one? A false positive here blocks a legitimate review, and the failure direction of THIS check is the opposite of every other check in the script.
2. `(?m)^<([A-Za-z][A-Za-z0-9_ ]*)>` matches an opening tag at line start. Reviewed material can contain such a line: this repo's own briefs use `<role>`, `<task>`, `<rules>` and `<claims>`. Those live in the brief, which the probe never renders, but is there a path where reviewed content reaches the rendered prompt and trips this? The AGENTS.md body does reach it, inside `<INSTRUCTIONS>`.
3. The accepted limit as I have written it is that a new surface delivered as untagged prose is invisible to any structural parser. Is that limit stated honestly, or does it excuse something the parser could reasonably catch?

Beyond that, the same standing question: does any round-3 fix carry a new defect? Six of the last seven rounds on this project found one, and this is the last round before the cap, so anything you leave unsaid ships.

Your UNVERIFIED list is accepted unchanged.

Verdict per claim, then one overall verdict. If your remaining objections are FIXes I can accept on the record rather than disputes, say so plainly, because at the cap an accepted FIX converges the plan and an unresolved one goes to the user.
