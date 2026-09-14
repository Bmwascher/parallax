# Brief sent to the fable-reviewer seat (whole-branch review, mode diff), 2026-09-13

Range: a48c35f..2df3d45 on branch mirror-parent (worktree
C:\Users\Brandon\Documents\_worktrees\parallax-mirror-parent; base is main
at 0.36.0). Three commits: 33ad108 (declaration row + resolver),
0111241 (emitter parent guard + reaper tests), 2df3d45 (doctor, prose,
item 107).

Inputs handed:
- the plan docs/superpowers/plans/2026-09-13-mirror-parent.md, whose
  "Decisions the handoff left open, settled here" section is the binding
  design authority (there is no separate spec; the plan extends
  docs/superpowers/specs/2026-09-13-mirror-reaper-design.md, "The identity
  guard", rule 6 of which the branch adds a seventh rule after), with its
  Global Constraints quoted verbatim;
- the SDD ledger .superpowers/sdd/2026-09-13-mirror-parent/progress.md
  (pre-flight scan, rulings, the three task reviews' deferred minors to
  triage);
- the diff package
  C:\Temp\parallax-scratch\2026-09-13-mirror-parent\diff\diff-package-a48c35f..2df3d45.md
  (commit list, stat, full diff with 10 lines of context).

Stated to the reviewer: the plan was NOT debated before the build (the
user directed it from the KitnEssentials handoff at
C:\Users\Brandon\Documents\KitnDev\KitnEssentials\dev\docs\handoffs\parallax-mirror-parent-handoff.md;
the mode-diff debate that follows this review is the first cross-vendor
gate), so a plan defect is as much a finding as an implementation defect.
One plan defect is already known: Task 3's doctor text cited
"the round-artifact-roots declaration" without the file prefix the
contract-coverage checker requires; the implementer added the prefix and
the ledger records the ruling.

The parent name `C:\pxm` was chosen by the user. `C:\pxm` already held
three directories from an older chat (`8904109a`, `k10392`, `k92104`);
they are never named or touched, and the tests use `C:\pxm\t-<8 hex>`.

Surfaces named as most consequential: the review-mirror row and the
"Review mirror:" bullet in
skills/multi-model-verify/references/model-prompting-notes.md;
tools/artifact-roots.ps1 (the `<TEMP>` removal, `-Expect reviewMirror`,
the mirror row in the assert set); tools/write-attestation.ps1
(`Resolve-MirrorParent` reading the parent through the roots tool
in-process, and the LAST rule of `Resolve-ReapPath`, mirror and bridge
alike); evals/multi-model-verify/test_artifact_roots.py (the pin, the
`<TEMP>` sweep shape, the parent-spelling binder);
evals/multi-model-verify/test_mirror_reaper.py (the `pxm` fixture that
builds under the REAL parent, the relocated success cases, Group 7);
commands/doctor.md check 10; the prose in SKILL.md (one line at the
6500-token ceiling), preflight-mirror.md and backup-lane.md; BACKLOG
item 107 (PARTIAL, follow-up 2 decided, 1 and 3 remaining).

Questions the reviewer was asked to answer with evidence, beyond the
standard report: (1) is any reader of the mirror location left on the
plugin surface that still points at the temp directory or the drive
root; (2) can the reap guard be satisfied by a tree outside `C:\pxm`
through any spelling the emitter accepts; (3) can a failure to read the
parent ever read as a parent; (4) do the tests that write under the real
`C:\pxm` leave anything behind or reach anything they did not create;
(5) is the prose that tells a session what to do executable as written.

Report format requested: Strengths / Issues (Critical, Important, Minor
with file:line) / Ledger minors triage / Assessment with Ready to merge.
