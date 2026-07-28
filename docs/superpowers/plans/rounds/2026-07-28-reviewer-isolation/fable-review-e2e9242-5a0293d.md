# Fable whole-branch review — parallax 0.17.0 reviewer isolation

**Seat:** agents/fable-reviewer.md (fresh subagent, read-only)
**Range:** `e2e9242c6153d69e9a4f0c49055e7bf8c81a1dd0..5a0293d6567ced3905710693d8163c422560c800`
**Branch:** `0.17.0-reviewer-isolation`
**Date:** 2026-07-28
**Frozen plan:** `docs/superpowers/plans/2026-07-28-reviewer-isolation.md` (frozen at `cd66546`)
**SDD ledger:** none — the plan was executed inline in the driver session.

This is the raw reply, retained verbatim as the range-bound artifact the
mode-diff round-1 brief cites.

---

### Strengths

- The load-bearing invariant is byte-anchored end to end. The probe writes the exact bytes it verified (`C:\Users\Brandon\Documents\parallax\tools\codex-context-probe.ps1:474-481`, strict no-BOM UTF-8, no terminator), the test proves byte identity between the artifact and the second probe call's actual `-c` argument (`evals\multi-model-verify\test_codex_context_probe.py`, `test_the_verified_override_is_written_out_for_the_dispatch`), and the SKILL.md preamble re-reads, re-hashes, and strict-decodes on round 1 AND every resume, with the "rounds are separate shells" rationale stated inline (`skills\multi-model-verify\SKILL.md:175-179, 220-228`). I found no path where the dispatched value can differ from the verified value without a hash mismatch or a thrown decode error.
- Fail-closed is real, not aspirational. Every blocked path in both scripts exits 1 with a reason; I traced the probe's top level and found no route to exit 0 without both passes completing and the second pass proving block ABSENCE, not zero count (`tools\codex-context-probe.ps1:453-462`). Parser edge cases that would otherwise read as clean (present-but-malformed block, chunk with no text field, truncated `(file: ...)` path producing a non-matching disable entry) all land on blocked, and each is test-locked.
- The failure-direction table in the design (`docs\superpowers\specs\2026-07-28-reviewer-isolation-design.md`, "Failure behaviour") maps nearly one-to-one onto tests, including the second-pass-only regressions (apps block reappearing, unknown block appearing only after suppression) that an earlier revision missed.
- Hard-won host lessons are encoded as tests, not comments: single-quote TOML literals because PS 5.1 strips embedded double quotes (`test_override_uses_forward_slashes_and_literal_strings`), console-encoding pinning before the child call (`tools\codex-context-probe.ps1:300-310`), join-not-Out-String against console wrapping with a fixture built to catch it (`test_a_long_skill_line_is_not_wrapped_on_the_way_in`), and the empty-array-unroll trap in the mirror's structured returns.
- Mirror safety is guarded before any mutation: repo/mirror overlap in all six relations, override-path overlap, stale-artifact refusal before the first codex call, and a `test_the_real_tree_is_never_written_to` proof (`tools\new-review-mirror.ps1:152-193`; `evals\multi-model-verify\test_review_mirror.py`).
- All six contract regions are pinned WHOLE, indentation included, in valid pin forms, and `DECLARED_REGIONS` gained exactly those six ids (`evals\multi-model-verify\test_contract_coverage.py:641-647`). I compared each pin against its region body character-shape by eye; they match.
- Documentation honesty holds. The tool-surface gap is named in four places with the same narrowed claim ("TOLD nothing extra, never that it can DO nothing extra"): the SKILL.md `client-probe-scope-limit` region, README.md:165-173, backlog item 7 with the observed `mcp: node_repl/js started` evidence, and the design's Accepted limits. I searched the whole diff for overclaiming language and found none.
- Both new .ps1 files are confirmed ASCII-only in the working tree (focused check: non-ASCII grep over both files, zero matches; named risk: the plan's ASCII constraint).

### Issues

#### Critical

None found.

#### Important

None found.

#### Minor

- `docs\superpowers\specs\2026-07-28-reviewer-isolation-design.md:344-347` says the codex-cli 0.144.1 floor is "recorded and enforced, in the shape 0.16.0 used for the Claude Code floor." No explicit floor check ships anywhere in the range (focused check: grep for version/floor enforcement in SKILL.md and the diff; SKILL.md:45 only requires `codex --version` to succeed). Enforcement is implicit: an older CLI fails the `--disable` flags or lacks `debug prompt-input`, which blocks. Fail-closed, but the spec sentence claims a control shape that does not exist.
- `commands\doctor.md:174-180`: check 9 runs the probe with `-WorkDir .`, so in any repo legitimately carrying a root AGENTS.md the probe exits 1 and doctor reports BROKEN with "a review dispatched from this machine right now would carry instruction sources the gate is supposed to have removed" - overstated, since a real review would remediate that in the mirror. A machine-health check that reads BROKEN in normally configured repos trains the user to ignore BROKEN.
- `tools\codex-context-probe.ps1:294-297` (probe args) vs `skills\multi-model-verify\SKILL.md:179`: the measurement runs `codex debug prompt-input` without `--sandbox read-only`, `-m`, or the effort override that the dispatch carries. Instrument/dispatch flag parity is assumed, not measured; no known skills-relevant effect, but the design's "same flags the dispatch will use" wording is slightly wider than the code.
- `tools\new-review-mirror.ps1:153` resolves `MirrorPath` with `[IO.Path]::GetFullPath` (process cwd) while later filesystem operations use the PowerShell provider location. Divergence needs an in-session caller that changed PS location and passed a relative path; all documented invocations use `-File` with paths, so theoretical.
- `docs\superpowers\plans\rounds\2026-07-28-reviewer-isolation\skills-override-used.txt:1` records a DOUBLE-quoted override, which the shipped generator now forbids (single-quote TOML literals). It is a verbatim historical record from the plan debate, but a future reader could take it as the format; a one-line note beside it would prevent that.

### Ledger minors triage

No SDD ledger exists for this branch (executed inline in the driver session); there are no deferred minors to triage. Judged against the plan's own checkbox steps, every task's deliverables are present in the range, including the two post-plan additions (the `client-probe-scope-limit` region and backlog item 7).

### Assessment

Ready to merge: Yes.

The invariant the branch exists for - the verified override is the dispatched override - holds under adversarial reading, every failure direction I could construct lands on BLOCKED, all six regions are whole-pinned, and the tool-surface gap is honestly scoped rather than papered over; the five minors are documentation-accuracy and hardening polish suitable for a rider or the next cycle. The 2 behavioral failures the dispatcher reported trace to the tool-surface exposure now recorded as backlog item 7, which predates this branch and is not widened by it.
