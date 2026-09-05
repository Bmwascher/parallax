1. **PASS** — The assertion now orders all four declarations plus the backup ID. In-memory evaluation returned True for shipped notes and False with the effort lines swapped. (`evals/multi-model-verify/test_multi_model_verify.py:1172`; `skills/multi-model-verify/references/model-prompting-notes.md:154`)

2. **PASS** — The new test isolates the entries-heading boundary. On both PowerShell hosts, its assertion passed with shipped code and failed with the widened slice; the outside-container sibling still passed. The probe’s Git blob is identical at both heads. (`evals/multi-model-verify/test_codex_context_probe.py:485`, `test_codex_context_probe.py:495`; `tools/codex-context-probe.ps1:275`)

3. **PASS** — Both accepted gaps are addressed, and the retained Fable review matches the stated minor findings. The external checkpoint and reported 135/135 results remain UNVERIFIED. (`evals/multi-model-verify/test_multi_model_verify.py:1172`; `evals/multi-model-verify/test_codex_context_probe.py:508`; `docs/superpowers/plans/rounds/2026-09-04-item87-astra-diff-round/fable-whole-branch-review.md:32`)

4. **PASS** — The delta contains exactly eight files: two tests, five retained artifacts, and the backlog date refresh. `Verified` is excluded from canonical bytes; recomputation still yields `48c9a1304996`. (`BACKLOG.md:3742`; `evals/tools/backlog_lint.py:202`, `backlog_lint.py:214`)

5. **PASS** — Both coverage gaps are closed, prior passing claims are unaffected, and no Important or Critical finding remains from this review. (`evals/multi-model-verify/test_multi_model_verify.py:1172`; `evals/multi-model-verify/test_codex_context_probe.py:495`; `docs/superpowers/plans/rounds/2026-09-04-item87-astra-diff-round/reply-astra-r1.md:1`)

UNVERIFIED:

- `.superpowers/sdd/2026-09-04-item87-astra-reviewer-swap/progress.md` and `.git/parallax/application-checkpoints/`—external ledger and checkpoint dispositions.
- Dual-host pytest logs and behavioral transcripts—filenames not supplied; the reported 135/135 counts were not independently verified.
- `evals/multi-model-verify/test_codex_context_probe.py:499`—“every test stayed green” overstates what R1 established; R1 exercised functions in memory and explicitly left full pytest execution unverified.
- `skills/multi-model-verify/references/model-prompting-notes.md:177`, `:209`, `:234`—underlying external guidance, cache and configuration observations remain unverified.

Overall: **PASS** — The fixes close both demonstrated coverage gaps without changing production behavior.