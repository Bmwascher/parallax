# Fable whole-branch review 2 — range `ef428c3..710d74f`

RAW REPLY, retained verbatim as a range-bound artifact. Not edited, not
summarized.

- Lane: `agents/fable-reviewer.md`.
- Range: `ef428c3..710d74f`, the FULL branch including the two commits
  that review 1 did not cover: `3b2c49d` (retaining review 1) and
  `710d74f` (its six fixes). Mode diff requires the whole-branch review to
  cover the same range the debate covers; a review of an older head is not
  a review of this branch, and a FIX is new code that gets no discount.
- Review 1, over `ef428c3..5133f98`, is retained beside this file.
- Verdict: **ready to merge, YES.** No Critical, no Important, four Minor,
  two of which are pre-existing and outside the plan's surface.

---

### Strengths

- Minor 3 fix lands on BLOCKED by construction: the new not-started return (`C:\Users\Brandon\Documents\parallax\tools\codex-tool-surface-probe.ps1:253-263`) feeds `Test-Transport`, whose first check (`:404-407`) writes BLOCKED and exits 1 on `Started = $false`. There is exactly one caller, no path treats a not-started pass as anything else, and the kill-then-return shape matches the existing preamble-block path (`:264-271`), so no new process-leak direction was introduced.
- Minor 4 fix is safe on both hosts: `Get-Surface` assigns `Tools` unconditionally as `@()` or a filtered array (`:382-397`), including when a server reports no `tools` key at all, so `$_.Tools.Count` (`:466`) is always a real array count and never a null property walk (the script sets no StrictMode either). The new test (`evals\multi-model-verify\test_codex_tool_surface_probe.py:158-176`) is the exact split-fixture that passed pre-fix, so it discriminates.
- Minor 5 fix counts the same set the allowlist walked: the count (`probe:522-523`) flattens `$surface2` Tools, already name-filtered in `Get-Surface`, and the allowlist loop (`:490-495`) iterates the identical flattened set; anything not allowlisted blocked before the count is taken, so every counted tool is a named one. The test pins the one-allowed-tool clean run at `dispatch_tools == 1`, and its comment records the 5.1 `-AllowTool a,b,c` splatting trap as failing safe rather than papering over it.
- Important 2 fix is exhaustive over reachable states (`tools\check-drift.ps1:158-183`): exit nonzero (including the catch's -1, and a hypothetical `$null` since `$null -ne 0` is true) fires a finding and discards the parsed value; exit 0 with no parse fires the other finding; exit 0 with a parse records. No state reaches neither a finding nor a correct recorded version. The discard plus the version carry-forward (`:405, :411`) keeps last-known-good, and the change note (`:462`) correctly stays silent on a discarded value.
- Minor 6 fix traces clean on every path I could construct: settings file missing (`:227`, CRITICAL, parsed stays false, value carried), unparseable (`:233`, same), agy absent entirely (`:156`, note, value carried), parsed-with-key (saved directly), parsed-without-key (note at `:480-483`, key dropped at `:528-533`). The last-known value survives every unmeasured path and each survival is audible; only a measured absence drops it.
- The `agy-allow-removed` scenario genuinely discriminates: the seeded snapshot HAS the key (`evals\tools\drift_statemachine_tests.ps1:507-511`, used at `:1000`), so a watcher that crashed, never ran, or never rewrote the snapshot fails the absence assertion, and pre-fix the carry-forward restored the key, failing both assertions. `Reset-State` clears `AGY_STUB_MODE` (`:495`), so neither new scenario inherits the other's stub mode.
- The proxy caveat is consistent in substance across all five surfaces (README.md:206-214, probe header `:34-40`, model-prompting-notes.md:155-161 sitting outside the pinned regions and before `contract:start`, backlog item 7 addendum, item 39): every instance says different subcommand, independent resolution, exec measured only to accept the flags, clean pass 2 is a proxy. README alone omits the item-39 pointer and the "never probed for its own tool surface" clause, but its claim is neither wider nor narrower.
- The fix comment's claim that the kimi block "had required exit 0 all along" is true: `check-drift.ps1:356` gates on `$versionExit -ne 0`.

### Issues

#### Critical

None.

#### Important

None.

#### Minor

1. **Important 2's class survives two blocks above the fix.** `check-drift.ps1:111-117` (claude) and `:119-125` (codex) never read an exit code at all: a `--version` that exits nonzero while printing a parseable version is recorded as measured and the run stays clean. For codex this is a live doctor-versus-drift disagreement of exactly the Important 2 kind, since doctor check 4 (`commands\doctor.md:50-53`) requires `codex --version` to pass; claude has no doctor counterpart. Both blocks are pre-existing and outside the frozen plan's surface, so item-31-style deferral is defensible, but the class the fix names is not closed in the file the fix touched. File it; do not merge-block on it.
2. **A settings file that parses to a falsy value measures nothing and says nothing.** `check-drift.ps1:229-250`: a settings.json containing literal `null` (or `false`) passes `ConvertFrom-Json` without exception, so the "did not parse" finding never fires, and `if ($agyCfg)` then skips every settings contract silently: no trustedWorkspaces finding, `$agySettingsParsed` stays false, the allow value carries forward with no audible companion. Doctor check 7 would call the missing `trustedWorkspaces` key BROKEN on the same file. This is in-range code from the original tasks that I did not flag on pass one; the input is pathological (hand corruption of one specific shape, since realistic corruption throws), which is why this is Minor. One-line fix: treat a successful parse yielding a falsy object as the unparseable finding.
3. **One `agy-version-fail-loud` assertion has an alternate satisfaction path.** `drift_statemachine_tests.ps1:988` (`$snapAfter.agy -eq "1.1.8"`) is also true if the snapshot was never rewritten: a watcher that died between the report write (`check-drift.ps1:506`) and the snapshot save (`:534`) leaves the seeded file intact, exits nonzero, and has already written the finding, satisfying all three assertions. It discriminated the target defect (watched red pre-fix, where 1.1.12 was saved), so the scenario did its job; asserting `updated` moved off the seeded `2026-01-01` value would close the residual hole. Contrast: `agy-allow-removed` already discriminates on rewrite.
4. **The Minor 3 fix path itself is verified by reading, not by a red-green test.** No harness case induces the Encoding-getter throw, and none realistically can from a subprocess. Recorded here so the verification record is not wider than the tests; no change requested.

### Ledger minors triage

- **Amendment 4 residual (exec surface unmeasured)**: RESOLVED. Propagated to four shipped surfaces plus item 39, wording consistent, item closure re-scoped to the proxy in the backlog itself.
- **Amendment 1 (128 to 133), disposition RECORD**: ride, unchanged by the fix commits; the allowlist design still makes the count non-load-bearing.
- **Amendment 5 (nothing live yet)**: ride, unchanged.
- **Task 3 closing sweep ("evidence, not proof")**: ride, unchanged.
- **Amendment 6 residual (repair claim bound to this probe)**: ride; the new preamble-fail guard tightens it further.
- **Out-of-surface item 31 sites (check-drift.ps1:700, doctor.md:70)**: ride, still untouched and still tracked.
- **Amendment 7 adjudications**: all six accepted findings verified fixed on this range; the two sharpenings (kimi exit 0, eleven-fact comparison) both check out in the code.

### Assessment

Ready to merge: **Yes.** All six fixes do what they claim, none introduces a regression I can find, the two new scenarios and two new tests discriminate against the pre-fix code, and every new finding on this pass is Minor, with two of the four pre-existing and out of the plan's surface. Two dependencies I rely on and did not measure: the full pytest suite on this exact tree is still running and must finish at its `5133f98` rate before attestation, and the Minor 3 fix path is verified by reading only.
