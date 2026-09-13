# Fable whole-branch review fix wave report, 2026-09-13

Branch `mirror-reaper`, worktree `C:\Users\Brandon\Documents\_worktrees\parallax-mirror-reaper`.
Starting HEAD 6c38ec9, commit e9d2713bc6062a99f312f3065dbf691601a84f2e.

## A. Sidecar failure message and duplication (fable Minor 1 + ledger minor)

`tools/write-attestation.ps1`: `$bridgeNote` is now computed once, right
before `Invoke-Reap "mirror" ...`, and reused both in that call and in
the sidecar `catch` block's error message, so the sidecar failure line
now also names an unattempted bridge instead of dropping the note.

Covering test: `test_a_sidecar_failure_names_the_unattempted_bridge` in
`evals/multi-model-verify/test_mirror_reaper.py` (Group 5) - mirror and
bridge reaped normally, sidecar held open by the test process so its
delete fails; asserts exit 3, both the sidecar-failure and
bridge-not-attempted text in stdout, the attestation file present, the
mirror gone, and the bridge and sidecar still on disk.

## B. A `.git` that is a junction is not a directory (fable Minor 2)

`tools/write-attestation.ps1`, `Resolve-ReapPath`: after the existing
`.git`-is-a-file refusal, a new check refuses a `.git` directory entry
that also carries the ReparsePoint attribute (a directory junction),
exiting 2 before any git read through the link.

Covering test: `test_a_git_directory_that_is_a_junction_is_refused` -
a real mirror plus a second "fake" directory whose `.git` is a junction
to the real mirror's `.git`; asserts exit 2, "directory link" in stdout,
no attestation written, the fake directory left alone, and the real
mirror's `.git/HEAD` untouched.

## C. Three untested guard branches (fable Minor 3)

Three tests added to `test_mirror_reaper.py` (Group 5), no production
code changed:
- `test_a_bridge_with_a_remediation_commit_is_refused` - a bridge given
  the exact parallax@local single-parent-at-head commit shape that is
  allowed for the mirror; refused (bridge has no remediation allowance),
  exit 2, "not the attested head", no record, bridge left on disk.
- `test_a_read_only_root_is_removed` - a tree whose ROOT directory (not
  just a file inside it) is marked read-only via `attrib +R`, run
  through the group-1 harness; exit 0, tree fully removed.
- `test_a_relative_reap_path_is_refused` - `-ReapMirror "kv-relative"`
  (no leading root); exit 2, "absolute path" in stdout, no record.

## D. The plan-mode residual is stated (fable Important 1)

1. `docs/superpowers/specs/2026-09-13-mirror-reaper-design.md`: appended
   the stated-limit paragraph at the end of "## The reap point is the
   attestation", verbatim per the brief.
2. `BACKLOG.md`: item 101's "What closing it means" paragraph now reads
   "...never deletes. A plan-mode debate has no attestation, so its
   mirror keeps the hand route; that residual is item 102's. Item 98
   closes with it, ..."; item 102's first paragraph now ends "...hiding
   it. A plan-mode debate ends with a frozen plan and no attestation, so
   its mirror has no mechanical reap point either; a plan-mode terminal
   event recorded mechanically is the third follow-up." Both items
   re-attested via `python evals/tools/backlog_lint.py --digests
   BACKLOG.md`: item 101 -> `e0cdbd57d4f3`, item 102 -> `2c2c5eeaeebc`,
   written into their `Verified: 2026-09-13 <digest>` lines.
   `backlog_lint.py` (no args) prints clean.
3. `skills/multi-model-verify/references/preflight-mirror.md`: appended
   the "Two limits, stated." paragraph as a new final paragraph of the
   End of life section (also covers fable Minor 5), no existing lines
   touched.

Covering tests: no new test targets item D directly (it is prose-only,
per the brief); the existing Group 3 prose tests
(`test_preflight_mirror_reference_states_the_end_of_life_rule`, the
skill/doctor prose tests) and the full suite run below confirm nothing
else broke.

## Verification

Both hosts, foreground, same four test modules
(`test_mirror_reaper.py`, `test_attestation.py`,
`test_multi_model_verify.py`, `test_contract_coverage.py`):

- `powershell.exe` (Windows PowerShell 5.1): **302 passed, 1 skipped** in 56.66s.
- `pwsh.exe` (PowerShell 7): **302 passed, 1 skipped** in 66.65s.

(The 1 skip on both hosts is a pre-existing, unrelated skip in the
selected modules, not from this branch's changes.)

Lint:
- `python evals/tools/skill_lint.py skills/multi-model-verify --strict`
  -> `PASS - 0 error(s), 2 warning(s)` (both warnings pre-existing:
  SKILL.md body length/token-budget warnings, unrelated to this diff).
- `python evals/tools/skill_scanner.py skills` -> clean, 0 findings.
- `python evals/tools/backlog_lint.py` -> clean.

## Commit

`e9d2713bc6062a99f312f3065dbf691601a84f2e` - "apply the fable
whole-branch review: refuse a linked git dir, name the unattempted
bridge on a sidecar failure, cover three guard branches, and state the
plan-mode residual". Staged by explicit path: `tools/write-attestation.ps1
evals/multi-model-verify/test_mirror_reaper.py
docs/superpowers/specs/2026-09-13-mirror-reaper-design.md BACKLOG.md
skills/multi-model-verify/references/preflight-mirror.md`. Working tree
clean after commit.

## Concerns

None. All brief-specified changes applied as given; no deviations, no
prose reflowed, no files touched outside the five named.
