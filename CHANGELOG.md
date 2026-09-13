# Changelog

One section per plugin version, newest first, written for the person
deciding whether to update. Each heading is `## vX.Y.Z (YYYY-MM-DD)` and
the newest one must name the version in `.claude-plugin/plugin.json`:
`evals/tools/check_changelog.py` enforces that in CI, and the release
workflow publishes the section as the release body, so a bump without an
entry fails on the branch and a release never ships blank. Write the entry
in the same commit as the version bump, after the diff debate; cite
backlog items and round records rather than commits, because the record is
what a reader can follow. Versions before 0.34.0 have no section and no
release; their records are the merge commits on main.

## v0.34.0 (2026-09-13)

### Artifact roots (item 100)

- **Every path a round writes is declared once.** Rounds, SDD ledgers and
  review mirrors had been landing in three roots per consumer repo
  because each writer read the repo-side override on its own; a cleanup
  of one consumer found 76 gate folders under the wrong root. The
  declaration now lives in one contract region of
  `references/model-prompting-notes.md`, and `tools/artifact-roots.ps1` is
  its only reader.
- **The resolver answers membership, not just location.** `-Assert`
  reports whether a path lies inside the retained root a retention copy
  expects, so a copy beside the rounds root is refused before it runs.
- **One exit map on both hosts.** The resolver has no `param` block and
  parses its own command line, because typed binding could not deliver
  one exit map: a missing value exited 1 from `-File` binding, and
  `-Json:$true` exited 1 on Windows PowerShell 5.1 and 0 on PowerShell 7.
  Every command-line fault now exits 2 on both hosts, and an empty inline
  value is refused rather than read as a default.
- **A sweep and a real-writer eval.** `test_artifact_roots.py` drives the
  three round writers inside a disposable repository under both hosts and
  sweeps the skill for any root named by hand instead of through the
  declaration, including the three placeholder roots the guidance cites.

### Records

- Five diff-debate rounds, one voided by a mid-round write into the
  reviewed tree, and the Fable whole-branch review are retained under
  `docs/superpowers/plans/rounds/2026-09-12-artifact-roots/`.
