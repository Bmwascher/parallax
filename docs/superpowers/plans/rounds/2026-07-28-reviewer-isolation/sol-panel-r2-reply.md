## Findings

### Finding A — CONFIRMED

The false-clean path is real, and I missed it in round 9.

`Test-PromptShape` calculates and returns `ProjectDoc` at `tools/codex-context-probe.ps1:461-485`. Pass 1 retains that result and blocks at `tools/codex-context-probe.ps1:562,619-622`. Pass 2 discards it at `tools/codex-context-probe.ps1:667`; the following checks cover only the skills block at `tools/codex-context-probe.ps1:668-680`. The clean report then uses the stale pass-1 value at `tools/codex-context-probe.ps1:761-783`.

Therefore, a pass-2-only `--- project-doc ---` reaches `status: clean`, contradicting the clean-probe contract at `skills/multi-model-verify/SKILL.md:149-162` and the function’s both-render rule at `tools/codex-context-probe.ps1:456-460`.

Minimal correct fix:

- Capture pass 2: `$instructions2 = Test-PromptShape $text2 $Json`.
- Block if `$instructions2.ProjectDoc`, using the existing message from `tools/codex-context-probe.ps1:619-621`.
- Add a regression with a clean first fixture and a suppressed second fixture containing `--- project-doc ---`; the stub already supports distinct later-call fixtures at `evals/multi-model-verify/fixtures/stub-codex/stub-codex.ps1:20-22`.

I would keep this check at top level, after the existing pass-2 skills checks, to preserve current error precedence.

### Finding B — CONFIRMED

The quoting defect is real, but its stated fail-closed consequence is not universal.

Both path-producing commands use Git’s default quoting at `tools/new-review-mirror.ps1:39` and `tools/new-review-mirror.ps1:62`. Remediation treats that display representation as a filesystem path at `tools/new-review-mirror.ps1:236-249`; the manifest merely trims quotes without decoding the octal escapes at `tools/new-review-mirror.ps1:78-100`.

Ordinarily, a quoted back-channel survives deletion and is caught by the final enumeration at `tools/new-review-mirror.ps1:274-282`. An ordinary quoted baseline path fails to resolve and blocks at `tools/new-review-mirror.ps1:110-123,299-307`.

There is, however, a silent manifest-collision path. For example, Git’s representation of `café/input.txt` becomes `caf\303\251/input.txt`. After line 100 removes the quotes, Windows interprets those backslashes as separators. If a real `caf/303/251/input.txt` also exists, lines 110-119 resolve and accept that different file; lines 131-135 hash it successfully. The manifest can therefore cover the wrong file and still proceed. Finding B is not merely a misleading legitimate-run rejection—it can produce false manifest coverage.

Minimal correct fix:

- Run both path-producing Git calls with `-c core.quotepath=false`.
- Around each capture, save `[Console]::OutputEncoding`, set UTF-8, capture `$LASTEXITCODE`, and restore the encoding in `finally`. The probe already demonstrates the required PowerShell 5.1-safe pattern at `tools/codex-context-probe.ps1:495-520`.
- Add dual-host tests for Unicode tracked/ignored back-channels, a Unicode baseline manifest entry, and the escaped-path collision above.

## Numbered answers

1. **Yes, Finding A’s consequence is real.** No later check examines pass 2’s `ProjectDoc`; only pass-2 skills are checked before the clean report (`tools/codex-context-probe.ps1:667-680,761-783`).

2. **The trigger class is wider than a file-created-between-calls race.** The first call may omit the delimiter because of any transient renderer/filesystem difference. The generated override is also an input present only on the second rendering (`tools/codex-context-probe.ps1:488-492,649-656`); the script cannot assume that input has no other prompt-shaping effect.

3. **The proposed fix is sufficient.** Checking `$instructions2.ProjectDoc` closes the omission. Placing it immediately after `Test-PromptShape` makes the project-document message win when both a project document and surviving skills exist. Placing it after `tools/codex-context-probe.ps1:673-680` preserves the current suppression-error precedence. Both are safe; I recommend the latter.

4. **Moving it inside `Test-PromptShape` is harder to forget, but changes pass-1 ordering.** It would block before skill parsing and classification at `tools/codex-context-probe.ps1:562-617`. The existing repo-scoped test uses a fixture containing both a planted repo skill and a project document (`evals/multi-model-verify/fixtures/codex-prompt-input/repo-agents.json:8`) and expects the repo-skill wording at `evals/multi-model-verify/test_codex_context_probe.py:370-381`; moving the check inside would break that expectation. A top-level second-pass check plus a dedicated regression is the surgical fix.

5. **Back-channel remediation is ultimately fail-closed, but the manifest is not universally so.**

   - Failed tracked classification leaves the real entry behind; re-enumeration blocks at `tools/new-review-mirror.ps1:274-282`.
   - Deletion and pruning can silently do nothing at `tools/new-review-mirror.ps1:237-249`, but the same final recheck catches that.
   - Most quoted baseline entries block at `tools/new-review-mirror.ps1:120-123,304-307`.
   - The escaped-path collision described above can hash a different existing file and silently pass at `tools/new-review-mirror.ps1:110-135`.

6. **`core.quotepath=false` alone is insufficient on Windows PowerShell 5.1.** It replaces ASCII octal escapes with raw UTF-8, while the mirror has no output-decoding guard. The probe documents and implements the required UTF-8 console handling at `tools/codex-context-probe.ps1:495-520`. The correct cross-host change is the flag plus guarded UTF-8 output decoding.

7. **Yes.** Use Git’s NUL-delimited machine format and capture stdout as raw bytes through `System.Diagnostics.Process.StandardOutput.BaseStream`, then split on NUL and strict-decode UTF-8. That bypasses PowerShell’s native-output decoding entirely. Alternatively, retain Git’s ASCII C-quoted output and implement a complete Git path unquoter, though that is more bespoke and error-prone than raw `-z` processing.

## Unverified

- Whether the generated `skills.config` override currently causes Codex itself to change project-document rendering. The local code cannot establish that; the fix must not depend on it being impossible.
- I did not independently rerun the driver’s scratch-repository Git reproduction or the dual-host suite in this read-only round.

## Terminal verdict

- Finding A: **FIX** — capture and enforce pass 2’s `ProjectDoc`, with a pass-2-only regression.
- Finding B: **FIX** — implement cross-host-safe Git pathname decoding and add Unicode/collision regressions.
- **OVERALL: FIX — pinned head `50c82029f178c747467e5a597b281731f70e4188` is not mergeable until both findings are corrected.**

