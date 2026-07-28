FIX.

R1 still needs two narrow documentation corrections.

1. Name all three caller-selected files. The transport reads `<brief-file>` and writes `<reply-file>` and `<transcript-file>` ([SKILL.md](/C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/SKILL.md:120)). Two debates sharing a brief path can overwrite the prompt before `Get-Content` reads it, even if their output paths are distinct.

   Required rule: each debate uses a unique scratch directory or unique `<brief-file>`, `<reply-file>`, and `<transcript-file>` paths. Later rounds use an inline rebuttal, so only their reply and transcript files require uniqueness.

2. “None of that is read as evidence” remains too broad ([model-prompting-notes.md](/C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/model-prompting-notes.md:200)). Shared auth is explicitly checked through `codex login status`, and shared config influences the client-resolved header used as route evidence ([model-prompting-notes.md](/C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/model-prompting-notes.md:150), [SKILL.md](/C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/SKILL.md:43)).

   Narrow it to: those stores are not shared global output logs and are not parsed to attribute one invocation’s transcript or reply to another.

The probe is now honestly bounded to distinct sessions with distinct paths, and the same-session prohibition is a sound operational rule. No lane lock is needed once all three files are isolated.

The supplied patch exactly matches `11f28ce..9ff5558`; only the note changed, `git diff --check` is clean, and the worktree is clean. Reported tests and CI were not independently rerun from this seat.