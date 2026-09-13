# Changelog

This file has one section for each plugin version, newest first. Write
each section for the person who uses the plugin and must decide if they
update, not for the person who maintains it. Each section starts with
`## vX.Y.Z (YYYY-MM-DD)`, and the newest one must name the version in
`.claude-plugin/plugin.json`.

Open each section with a lead paragraph in plain words that says what
changed for the user and what they must do. The lead paragraph has no
code, no file name and no link; the checker refuses those. After the
lead, one bold line names the backlog items that the version closes. Put the
maintainer detail, the file names and the records under a later title.

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

The plugin now keeps all the files that a review writes in one folder
for each project. Before this version, those files went to three
different folders, and it was hard to find a review or to clean up. You
do not have to change anything when you update. New reviews go to the
one folder, and old files stay where they are.

**Backlog: this version closes item 100.**

### What changed for you

- **One folder for each project.** A review writes its debate rounds,
  its ledger and its review mirror under one root. The skill declares
  that root in one place, and each tool reads that one declaration.
- **A tool shows you where the files are.** `tools/artifact-roots.ps1`
  prints the folders that a review uses in your project. It also refuses
  to copy a file to the wrong folder.
- **The same result on both PowerShell versions.** The tool gives the
  same exit code for the same error on Windows PowerShell 5.1 and on
  PowerShell 7. Before, the two versions gave different codes for the
  same mistake.

### Details for maintainers

- The declaration is one contract region of
  `references/model-prompting-notes.md`, and `tools/artifact-roots.ps1`
  is its only reader. `-Assert` answers if a path is inside the retained
  root that a retention copy expects.
- The resolver has no `param` block and parses its own command line,
  because typed binding did not give one exit map. A parameter with no
  value exited 1 from `-File` binding, and `-Json:$true` exited 1 on
  Windows PowerShell 5.1 and 0 on PowerShell 7. Each command-line fault
  now exits 2 on both hosts, and an empty inline value is a fault, not a
  default.
- `test_artifact_roots.py` runs the three round writers in a disposable
  repository on both hosts. It also sweeps the skill for a root that a
  sentence names by hand and not through the declaration.
- The record for item 100 is
  `docs/superpowers/plans/rounds/2026-09-12-artifact-roots/`, which
  retains five diff-debate rounds and the Fable review of the full
  branch. A write into the reviewed tree during round 2 voided that
  round.
