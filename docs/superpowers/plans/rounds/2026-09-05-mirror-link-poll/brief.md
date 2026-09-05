You are a second-opinion design reviewer. Read-only. Do not edit anything.

CONTEXT
This repo (parallax) is a Claude Code plugin whose review flow builds a throwaway "review mirror" of a user's repo before every cross-vendor review round. The builder is tools/new-review-mirror.ps1. Read it, in particular the header comment, the path-budget walk around lines 920-1000 (which deliberately FOLLOWS directory junctions and symbolic links), the robocopy call near line 1100, and the fingerprinting helpers around lines 370-430 (git ls-files --cached --others -z with no exclude-standard, and git status --porcelain --ignored -uall -z). Also read tools/dispatch-round.ps1 lines 270-320 for how the mirror identity is re-verified before and after a round.

THE PROBLEM
The user's WoW addon repo has ~14k files. Inside it sits a directory symbolic link (or junction) pointing at a separate git checkout of the World of Warcraft API reference files, another ~14k files, used for verification and cited by reviews. robocopy /E follows the link, so the mirror carries ~28k files and the build takes roughly twice as long as it should. The reference files must still be readable by the reviewer, and the review's identity record must still detect drift in any review input during a round.

THE SESSION'S PROPOSAL (from the Claude session, for you to agree with or challenge)
1. Copy with the link excluded (robocopy /XJ or equivalent), then recreate the same junction at the same relative path inside the mirror, pointing at the same target.
2. Extend the mirror identity record with the reference checkout's HEAD sha and its own status hash, so a change in the reference during a round fails the post-round identity check the same way a change in the addon does.
3. Secondary note: the source fingerprint's ls-files --others walk may also be enumerating the 14k reference files on every verify if git walks the junction; the same change would remove that cost.
Alternatives considered and rejected: naming the target path in the brief with no link in the mirror (not self-contained, version unpinned); an exclude list of unused reference subfolders (fragile).

YOUR TASK
Answer these, concretely and grounded in the code you read:
A. Do you agree with the proposal? If not, what would you do instead and why?
B. What does the proposal get wrong or miss? Consider: how git on Windows treats a junction versus a symlink (core.symlinks), what the reviewer sandbox (codex exec --sandbox read-only, cwd = mirror) can read through a junction, whether the post-round mirror-state hash currently covers the linked content and what happens to that coverage after the change, cycle detection, and the -ExtraInput mechanism.
C. Is there a cheaper or safer option the session did not list?
D. Name any existing test in evals/ that pins the current follow-the-link behaviour and would go red.

Keep it under 700 words. Lead with a one-line verdict: AGREE, AGREE WITH CHANGES, or DISAGREE.
