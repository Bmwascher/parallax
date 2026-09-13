**FIX.** Two writer-test regressions and one resolver defect remain in `docs/superpowers/plans/2026-09-12-artifact-roots.md:1079` (abbreviated `plan` below).

**A.** All eight applications are present: registration and pin (`plan:50`, `:120`), resolver changes and regressions (`:378`, `:388`, `:593`, `:609`, `:627`), arithmetic (`:887`), positive sweep controls (`:826`), directory observation (`:1079`), implementation-scratch exclusion (`:228`), authorized Edit C (`:864`), and the rollout citation (`docs/superpowers/specs/2026-09-12-artifact-roots-design.md:42`).

The directory amendment leaves two tests failing. The real-writer test includes `.git/parallax` in `appeared`, then requires every entry to satisfy `-Assert` (`plan:1120`, `:1124`). That parent is outside the retained roots (`:676`); both hosts returned exit 1 in my probe. Keep the exact three-path assertion, assert membership for the attestation directory and file, and explicitly expect refusal for `.git/parallax`. Update the spec’s corresponding “every path” assertion (`docs/superpowers/specs/2026-09-12-artifact-roots-design.md:312`).

The existing negative control creates both `rounds` and `rounds/x`, but still expects only `{"rounds/x"}` (`plan:1137`, `:1141`). Change that expectation to `{"rounds", "rounds/x"}`. **FIX.**

**B.** Relative `-RepoRoot` remains incorrectly resolved when PowerShell’s location differs from the process working directory. The common-dir join can remain relative, and `GetFullPath` then uses the process directory (`plan:593`, `:595`).

On both hosts, starting in `C:/Temp`, changing PowerShell’s location to `C:/Temp/pxar1`, and invoking the extracted resolver with `-RepoRoot .` printed the correct repository but `C:/Temp/.git/parallax/attestations`. Normalize `$RepoRoot` through the existing `Resolve-Absolute` helper before invoking Git, and add a regression with differing PowerShell and process directories (`plan:526`, `:576`).

The amended absolute-subdirectory and `./other/root` cases passed on both hosts. Placeholder stripping remains compatible with the returned tails; the canonical docs-root prefix check rejects the toplevel itself, and override discovery uses `$toplevel` (`plan:610`, `:615`, `:638`, `:660`). **FIX.**

**C.** The quoted replacement strings match HEAD, including Edit C’s sentence within the paragraph (`skills/multi-model-verify/SKILL.md:321`, `:389`). Using the linter’s frontmatter stripping and LF joining, the arithmetic is:

`25987 − 232 + 118 + 123 − 11 = 25985`

That floors to 6,496 tokens (`evals/tools/skill_lint.py:182`, `:339`; `plan:844`, `:851`, `:860`, `:868`, `:876`). **PASS.**

**D.** The proposed Markdown contains seven occurrences: one marker and six qualified citations. All satisfy the existing citation matcher after whitespace normalization (`plan:172`, `:845`, `:905`, `:924`, `:949`, `:967`, `:981`; `evals/multi-model-verify/test_contract_coverage.py:832`, `:837`, `:847`). **PASS.**

**E.** Both class-sweep findings are addressed. Implementation-time scratch is explicitly excluded, and transient writes and dynamically assembled destinations are documented observation limits (`plan:228`, `:1075`; `docs/superpowers/specs/2026-09-12-artifact-roots-design.md:323`, `:358`). Edit C removes the stale attestation sentence, and the fifth pattern detects its return (`plan:786`, `:829`, `:876`). The amendments introduce no additional consumer-repository artifact root (`plan:173`, `:1119`). **PASS.**

### Final check

No A–E point remains unresolved against the files read. **UNVERIFIED:** the historical 54 MB size measurement; it contributes nothing to the verdict.

The copy attribution is now verified by `C:/Users/Brandon/.codex/sessions/2026/09/07/rollout-2026-09-07T20-53-38-01a07eb8-8a4c-7941-ba19-a542a5642dc9.jsonl:3682`. Its successful execution record at `:3684` is dated **2026-09-08**, so the copy date asserted in `docs/superpowers/specs/2026-09-12-artifact-roots-design.md:40` needs correction. This historical correction is excluded from the implementation verdict.

No file content caused a pause.

**Verdicts: A FIX; B FIX; C PASS; D PASS; E PASS. Plan blob `29cc87d63dedf7eb899286edf10cd67fee218c8e`: FIX.**