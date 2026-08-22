I found three merge-blocking record defects.

1. The new convention paragraph is itself the eleventh instance. It calls `50` “`entry-points.tsv`’s must-change bullet count” and then says it became `83` “by the time this sentence was written” ([record:653](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:653)). Mechanical reconstruction at `a13d3c3` shows:

   - TSV: 83 `must-change` rows.
   - Record: 50 must-change bullets.

   The later paragraph states that distinction correctly ([record:775](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:775)). Moreover, “83 by the time this sentence was written” is exactly the unbound live figure the paragraph prohibits. It should explicitly bind both sides: 83 TSV rows/50 record bullets at `a13d3c3`, then 83/83 at `b1e9cfa`.

2. The count convention remains incompletely applied. Bare inventory figures survive throughout the record, including `83`/`3` at lines 137–155, 407–409, 494–495, 2050, 2246, 2391, and 2444. These are not survey invariants: `survey.py` accepts any of the three migration values ([survey.py:169](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/survey.py:169)), while its exit predicate checks only unclassified, stale, and skipped files ([survey.py:361](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/survey.py:361)).

   One such figure is also factually wrong: “five dual-family rows” ([record:788](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:788)). The TSV contains five duplicated `path:line` groups comprising ten rows: `.githooks/pre-push:24`, `commands/doctor.md:340`, `stub-appserver.cmd:14`, `SKILL.md:326`, and `tools/check-drift.ps1:96`. The intended phrase is five dual-family pairs/source lines, ten TSV rows, explicitly bound—or the count should be removed.

3. All three backup-lane subgroup attributions land, but the first new description overstates the source. I checked all 16 citations: 5 belong to the parity-gap test, 2 to the renamed-variable test, and 9 to the duplicate-step test. However, the record says the first fixture asserts both hosts “exist with parity” ([record:832](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:832)). It deliberately omits the first required module from the `pwsh` step ([source:1330](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_backup_lane.py:1330)) and asserts that the resulting `pwsh.exe` parity error is reported ([source:1336](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_backup_lane.py:1336)). Both steps are discovered; parity is intentionally broken.

The `b1e9cfa` binding itself is valid: 83 TSV rows/83 bullets and 3 unknown rows/3 bullets. The current 83-bullet citation multiset matches the TSV exactly. I found no current live survey-hit figure and no regression in positional citations into editable files. The CONDITIONAL verdict remains sound.

FIX