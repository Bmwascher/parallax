# Fable whole-branch review 1 — range `ef428c3..5133f98`

RAW REPLY, retained verbatim as a range-bound artifact. Not edited, not
summarized. The session's adjudications live in the build checkpoint
(amendment 7) and in the round-1 diff brief that cites this file.

- Lane: `agents/fable-reviewer.md` (Claude-side whole-branch reviewer).
- Range: `ef428c3..5133f98`. This artifact does NOT cover any commit after
  `5133f98`, including the commits that apply the fixes below.
- Dispatched 2026-08-11 with: the frozen plan, the build checkpoint, the
  debate record, and a controller-built diff package (code diff 3133
  lines, round artifacts 1836 lines, kept separate).
- Verdict: ready to merge WITH FIXES. No Critical, 2 Important, 4 Minor.

---

### Strengths

- The probe's blocked-by-default transport is genuinely thorough. `Test-Transport` (C:\Users\Brandon\Documents\parallax\tools\codex-tool-surface-probe.ps1:381-420) blocks separately on not-started, timeout, non-zero exit, RPC error, unreadable stream, no frames, and no answer, and the partial-stream rule (an unreadable frame blocks even when a later frame parsed, Get-LastStatusResponse plus the post-Result `Unreadable` check) closes the classic "skip the bad frame, report the rest" false-clean. Each direction has a matching test in evals/multi-model-verify/test_codex_tool_surface_probe.py.
- The stub is now stricter than the thing it stands in for, which is the correct direction: raw-byte stdin, hard exit 9 on a first frame not starting with `{` (evals/multi-model-verify/fixtures/stub-appserver/stub-appserver.ps1), watched to fail with the defect deliberately restored (checkpoint Amendment 6, with the failure text recorded).
- The `agy-contracts-clean` positive control discriminates. Its snapshot assertions (`agy == 1.1.12` reachable only through the `.cmd` lookup the old code lacked; `agyAllowNonWorkspaceAccess` recorded) cannot be satisfied by a watcher that never looked at agy, and every negative scenario asserts the exit code as well as the finding text (evals/tools/drift_statemachine_tests.ps1, agy block).
- The `Write-StubFile` guard logic is correct: every byte written ends in `\r\n` after normalization plus the appended terminator, so `lf -gt 0 -and lf -eq crlf` is exactly the all-CRLF test, and it runs before any scenario.
- The LOCALAPPDATA redirection note is right and load-bearing: without it every offline scenario would have made a real `agy models` network call (drift_statemachine_tests.ps1, agy stub setup).
- Clean-report wording holds the mitigation line everywhere I checked: the probe's own note, both contract regions in skills/multi-model-verify/references/model-prompting-notes.md:149-177, the rewritten `client-probe-scope-limit` region in SKILL.md, and README.md:196-203 all say mitigation, never removal, and the pins match the region text verbatim.
- Items 36, 37 and 38 are properly narrow; item 37 cites the counter-evidence to its own earlier wider drafts, and item 38 records the retraction instead of the claim.
- Amendment 4 is exemplary self-catching: the dispatch flag had been verified only on `app-server`, and the exec acceptance was then measured rather than assumed.

### Issues

#### Critical

None.

#### Important

1. **The exec-versus-app-server residual lives only in the ledger, and every shipped claim is wider than it.** Checkpoint Amendment 4 concedes: "`exec` was never probed, only `app-server` was, and the two resolve their MCP servers independently for all this cycle measured." But the shipped surfaces say the reviewer's tool surface IS measured: README.md:196-197 ("it is measured by a different probe"), backlog item 7 marked DONE (docs/superpowers/plans/2026-07-27-0150-backlog.md:526, 534-560), and the probe header. The reviewer runs under `codex exec`; the probe reads `codex app-server`'s resolved surface under the same flags and nothing shipped states that this is a proxy. This is precisely the propagation failure class this cycle's debate flagged three rounds running: the caveat exists where it was found (the checkpoint) and nowhere a later cycle reads. Fix is cheap: one sentence on a shipped surface or a named follow-up item; the contract regions themselves do not need reopening, since "pass 2 carries the dispatch flags" is not false.

2. **Doctor and drift disagree on one version-check verdict.** commands/doctor.md:158-166: a client that "exits non-zero, or does not report a usable version, is BROKEN". tools/check-drift.ps1 (agy block, ~lines 156-170): `$agyVersionExit` is captured but only ever printed inside the finding message; the finding fires solely on the regex missing. So `agy --version` exiting non-zero while printing anything matching `\d+\.\d+\.\d+` is BROKEN per the doctor and clean per drift, with the version recorded as measured. The state-machine `version-fail` stub exits 1 with no output, so the divergent state is exactly the one no scenario covers. Either check the exit code in drift or narrow the doctor's wording; the branch's own stated rule is that two instruments disagreeing about the same fact are worse than one.

#### Minor

3. **The stdin preamble self-check has a silent-pass path.** tools/codex-tool-surface-probe.ps1:~239-248: `try { $preamble = $proc.StandardInput.Encoding.GetPreamble() } catch { }` leaves `$preamble` empty if the read throws, and the probe proceeds as verified. The comment above ("Left to the preamble check below, which BLOCKS. It is never silently accepted") is wider than the code: it is true only while the check itself can be made. Reachability is close to theoretical (a property read on a redirected-stdin writer), which is why this is Minor, but the guarded form (block when the preamble cannot be read) is one line and the script's contract is that every failure direction blocks. The restore path itself is correct on every exit: the `finally` fires whether `Process.Start` throws or returns, and the restore cannot affect the already-built writer.
4. **Calibration is weaker than its stated contract.** The blocked-reason and contract text say "no running MCP server with any tool"; the code (probe ~lines 437-444) requires at least one running server AND at least one tool anywhere, as two independent facts. A pass-1 record pairing a tool-less running server with a tools-carrying silent server would calibrate. No measured record has that shape (measured silence is zero tools), so this is wording-versus-code drift, not an observed false-clean.
5. **`dispatch_tools = 0` is hardcoded in the clean report** (probe ~line 488). Exact under the shipped empty allowlist; false the day a caller passes `-AllowTool`, when the reviewer holds allowed tools and the quoted record says zero. Make it the actual count or drop the field.
6. **Deletion of `allowNonWorkspaceAccess` is silently absorbed.** The carry-forward (tools/check-drift.ps1:~486-500) restores last week's value whenever the current read is empty, including when the key simply vanished from a parseable settings file, so the snapshot asserts a value the file no longer carries and no note fires. The claim "a change to it is watched" (backlog item 11 close, and the check-drift comment) is slightly wider than that: a value change is watched, a removal is not.

### Ledger minors triage

- **Amendment 1 (128 became 133 in an afternoon), disposition RECORD**: ride. The design compares an allowlist, not a count, and the probe record was amended.
- **Amendment 4 residual (exec tool surface unmeasured)**: fix before merge, as Important 1 above. The residual must land on a shipped surface, not only in the ledger.
- **Amendment 5 (nothing live yet)**: ride. Informational, and the cache check was made rather than assumed.
- **Task 3 closing sweep ("evidence, not proof" of no eighth surface)**: ride. The claim is bounded correctly and the search terms are recorded.
- **Amendment 6 residual (repair claim bound to this probe; check-drift.ps1:696 file-redirect swept and clear)**: ride. The sweep for `StandardInput`/`InputEncoding` was recorded.
- **Out-of-surface item 31 sites (tools/check-drift.ps1:700, commands/doctor.md:70)**: ride. Named in advance in checkpoint section 3, tracked as an open item, and the review confirms they were not touched.

### Assessment

Ready to merge: **With fixes.** The build is careful, the failure directions of the new probe genuinely all block on everything I could reach, and the debate's own findings propagated into the shipped text with one exception. That exception (Important 1) is the exact claim-wider-than-evidence class this cycle paid nineteen findings to learn, sitting in the closure of the item itself, and Important 2 is a concrete verdict disagreement between the two instruments the branch says were aligned deliberately. Both fixes are small and neither reopens contract regions. Separately: the checkpoint's section 7 (verification results) is still empty and the full pytest result is unconfirmed at review time, so attestation must wait on that write regardless of the debate's outcome.
