`cce350c` is still `FIX`. I found no new executable-code defect, but the confirming documentation wave reproduced the same self-recording class again.

## Current findings

1. Task 10’s heading contradicts its completed result.

The introductory paragraph still says three items were observed on both hosts, one on one host, and one not at all (`benefit-measurement.md:37-41`). Item 6 now says all five are complete on both (`:73-92`).

Update the heading paragraph to the current result. The underlying screen observation is attributed honestly but remains externally unverified by me.

2. `Raw rounds` overstates plan-review bindings.

The appendix says the Sol, Fable, and Kimi plan reviews “each” have a `-binding.json` (`completion-coupled-dispatch.md:2489-2493`). Directory enumeration finds only:

- `sol-plan-review-r1-binding.json` through `r5-binding.json`
- No Fable plan-review bindings
- No Kimi plan-review binding

State that the five Sol reviews have bindings; list Fable and Kimi without claiming adjacent bindings. The three newly retained diff replies and bindings do exist; their JSON parses, reports `clean`/`sealed`, uses one session ID, and has monotonically increasing byte offsets (`sol-diff-debate-r1-binding.json:1`, `r2-binding.json:1`, `r3-binding.json:1`). I cannot independently verify the external rollout hashes from this mirror.

3. `Rounds used` omits diff round 1.

The field counts eight plan rounds plus two retrospective rounds (`completion-coupled-dispatch.md:2483-2484`), but the record relies on diff round 1 in resolved points 1–4 (`:2523-2526`) and retains diff rounds 1–3 (`:2492-2493`). Write this as eight plan rounds plus diff rounds 1–3, noting that rounds 2–3 were the retrospective verification.

4. Two smaller plan pointers are inaccurate.

Resolved point 5 cites “Task 1a below,” but Task 1a is above (`completion-coupled-dispatch.md:2527`; Task 1a begins at `:561`).

Task 1a says the collisions are refused “before anything is copied” (`:594-602`). The implementation checks after the mirror has been copied and remediated, but before any extra input is copied (`new-review-mirror.ps1:1272-1316`). Narrow the plan to “before any `-ExtraInput` is copied.”

These are mechanical corrections, not escalation issues.

## Four-class sweep

Using the same high prior:

- Control that controls nothing: PRESENT, knowingly carried. Task naming is explicitly unenforced (`model-prompting-notes.md:435-445`).
- Claim/evidence mismatch: PRESENT in the stale Task 10 heading and false plan-binding claim.
- Partial fix: PRESENT. The Task 10 completion updated items 5–6 but missed its heading; retaining raw rounds added an overbroad binding claim.
- Guard blind to written form: PRESENT, knowingly carried. The citation guard excludes docs and records that boundary (`test_contract_coverage.py:611-615`, `:863-877`).

No new false-success path appeared in `02c6eab..cce350c`.

## Round-2 merge floor

1. ExtraInput collision: substantively closed in plan, implementation, tests, and resolved record. Only the “anything” wording above needs narrowing.
2. Binder parity: closed by the recorded Task 5 interpretation (`completion-coupled-dispatch.md:2528-2545`).
3. Summary/Fable/citation corrections: closed.
4. Task 10: measurement record substantively closed; stale heading remains.
5. Retrospective review/appendix: reopening condition remains met. Required tables and artifacts now exist, but the rounds/binding claims need correction.

## What I would knowingly ship

I would ship these explicitly stated limits:

- The plan remains `DEGRADED` because its final revision was reviewed late, not before implementation (`completion-coupled-dispatch.md:2470-2488`, `:2554-2568`).
- Kimi lacks client-reported working-directory evidence; the indirect resume consequence is not live-client measured (`backup-lane.md:121-137`, `:156-177`).
- A filesystem owner can read the nonce or alter `wrapper.ps1`/`body.ps1`; neither script is sealed (`model-prompting-notes.md:370-387`).
- Git-clean hidden-byte changes and change-then-revert mutations remain invisible (`model-prompting-notes.md:362-369`, `:387-393`).
- Harness trailer format is version-measured rather than pinned, and hung rounds have no time bound (`model-prompting-notes.md:393-400`).
- Background task naming and citations outside `DOC_PATHS` remain unenforced.
- FAIL/KILL harness behavior was measured on one interpreter only, stated accurately (`benefit-measurement.md:164-176`).

The full suite at `cce350c` is unverified; your planned two-host run remains a pre-merge gate.

**FIX**