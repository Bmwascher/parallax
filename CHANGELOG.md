# Changelog

This file has one section for each plugin version, newest first. Write
each section for the person who must decide if they update. Each
section starts with `## vX.Y.Z (YYYY-MM-DD)`, and the newest one must
name the version in `.claude-plugin/plugin.json`.

Write each section in ASD-STE100 Simplified Technical English.
`evals/tools/ste_lint.py` refuses these shapes, which STE forbids:

- a sentence of more than 25 words
- a paragraph of more than 6 sentences
- the passive voice
- an "-ing" verb form
- a contraction
- an unapproved modal
- an unapproved word on its list

The STE dictionary is not in this repository. The writer keeps the other
rules by hand. Use one approved meaning for each word, no noun cluster of
more than three nouns, and one topic for each sentence. Technical names
go in backticks. `evals/tools/ste_allow.txt` lists the technical names
that the checker must not question.

`evals/tools/check_changelog.py` runs both checks in CI, and the release
workflow publishes the section as the release page. A version bump with
no section fails on the branch, and a release never ships blank. Write
the section in the same commit as the version bump, after the diff
debate. Cite backlog items and round records, not commits, because a
reader can follow a record. Versions before 0.34.0 have no section and
no release; their records are the merge commits on main.

## v0.34.0 (2026-09-13)

### Artifact roots (item 100)

- **One declaration names each path that a round writes.** Before this
  version, a round put its rounds, ledgers and mirrors in three roots
  for each consumer repository. Each writer had resolved the repository
  override on its own. A cleanup of one consumer found 76 gate
  folders under the wrong root. The declaration now lives in one
  contract region of `references/model-prompting-notes.md`, and
  `tools/artifact-roots.ps1` is its only reader.
- **The resolver answers a membership question.** `-Assert` tells you
  if a path is in the retained root that a retention copy expects. The
  resolver refuses a copy next to the rounds root before the copy
  starts.
- **The exit map is the same on both hosts.** The resolver has no
  `param` block and parses its own command line, because typed binding
  did not give one exit map. A parameter with no value exited 1 from
  `-File` binding. `-Json:$true` exited 1 on Windows PowerShell 5.1 and
  0 on PowerShell 7. Each command-line fault now exits 2 on both
  hosts. The resolver refuses an empty inline value; it does not read
  the value as a default.
- **A sweep and an eval with real writers.** `test_artifact_roots.py`
  runs the three round writers in a disposable repository on both
  hosts. It also sweeps the skill for a root that a sentence names by
  hand and not through the declaration. The sweep includes the three
  placeholder roots that the guidance cites.

### Records

- `docs/superpowers/plans/rounds/2026-09-12-artifact-roots/` retains
  five diff-debate rounds and the Fable review of the full branch. A
  write into the reviewed tree during round 2 voided that round.
