# Spec pre-read: artifact roots design (item 100)

You are the Fable panel reviewer seat, dispatched for a single pre-read of
a DESIGN SPEC before its implementation plan is written. This is not a
cross-vendor gate and produces no attestation; a separate GPT-6 Astra
mode-plan debate follows on the plan. Your job is to find what in the
spec is wrong, unverifiable, or would fail to close the backlog item.

Repository: C:/Users/Brandon/Documents/parallax (branch artifact-roots).
Subject: docs/superpowers/specs/2026-09-12-artifact-roots-design.md
Subject revision: git blob ed8674b2143d94ea5bea636ee3ed78e1e8acdfa7

## Rules

- Equal weight, evidence over authority. Cite file:line for every claim
  you make or contest; an uncited claim is struck, mine included.
- Anything you cannot verify against a file you read is UNVERIFIED and
  stays out of your verdict.
- No manufactured objections: a spec section you find sound gets PASS.
- Read-only. Report evidence and conclusions, not deliberation.

## Files to read

- docs/superpowers/specs/2026-09-12-artifact-roots-design.md (the subject)
- BACKLOG.md, the "## 100." entry (what closing means)
- skills/multi-model-verify/SKILL.md (preflight section, mode plan step 5,
  the attestation paragraph near "It writes `.git/parallax/attestations")
- skills/multi-model-verify/references/frozen-plan-format.md
- skills/multi-model-verify/references/model-prompting-notes.md
  (the "Canonical model id" blocks, the backup lane block, and the
  contract:start / contract:end marker convention)
- skills/multi-model-verify/references/preflight-mirror.md
- agents/fable-reviewer.md
- tools/write-attestation.ps1
- tools/new-review-mirror.ps1 (the in-repo refusal near line 1460)
- tools/dispatch-round.ps1 (parameter block and exit convention)
- evals/multi-model-verify/test_contract_coverage.py (DECLARED_REGIONS and
  the pin-form rules in its module docstring)
- evals/multi-model-verify/test_dispatch_round.py (build_real_mirror,
  prepare_default)
- evals/multi-model-verify/test_review_mirror.py (around line 537-565)
- evals/multi-model-verify/test_multi_model_verify.py (the test that
  forbids a hardcoded -m model literal; grep "hardcoded")
- .github/workflows/skill-evals.yml (the powershell-hosts job)
- CLAUDE.md at the repo root (the pin rules and the skill editing rules)

## Claims (session position)

1. The plugin has no single statement of every path a round writes; the
   spec's "measured facts" section cites where each root is named today.
   Verify each citation resolves to what the spec says it does.
2. The SDD ledger root cannot be relocated by the plugin because
   Superpowers' sdd-workspace script hard-codes it. The spec quotes the
   path; the script lives outside this repo at
   C:/Users/Brandon/.claude/plugins/cache/claude-plugins-official/superpowers/6.3.0/skills/subagent-driven-development/scripts/sdd-workspace.
   If you cannot read it, mark the claim UNVERIFIED rather than accepted.
3. Declaring the eight `Canonical ... :` lines inside a contract region in
   model-prompting-notes.md, AFTER the backup lane block, is compatible
   with the existing runtime parsers and the coverage checker's pin rules.
4. The existence-based override rule (dev/docs/superpowers exists ->
   override; -DocsRoot escape) resolves KitnEssentials correctly and has
   no false-positive path in this repo or in the fixture repos the tests
   build.
5. The `-Assert` set (frozen-plan parent, rounds, attestation, checkpoint)
   is the right set: the session never copies into the ledger or mirror
   roots.
6. The behavioural eval's central assertion, "the set of paths that
   appeared inside the repo after running the three real writers is
   exactly the attestation file", can actually FAIL, and is achievable
   with the existing fixtures in test_dispatch_round.py (in particular:
   does build_real_mirror or prepare_default write anything inside the
   source repo that would make the assertion red on a correct tool?).
7. The static sweep's enumerated forbidden shapes are sufficient to catch
   the two KitnEssentials roots that were not parallax writers
   (`dev/docs/superpowers/rounds/` and `.superpowers/review-sources/`)
   if a future skill edit introduced them, and produce no false positive
   on the plugin's current text. Grep the plugin surface for the shapes
   and report what you find.
8. The spec's "what the eval does not prove" section states the limit
   correctly and nothing else in the spec overclaims.

## Requested output

For each claim: ACCEPT / REFUTE (with file:line evidence) / UNVERIFIED.
Then any finding the claims do not cover, each with evidence and a
severity (blocking / should-fix / note). End with one verdict on the spec
as a whole: PASS / FIX (specific) / ESCALATE, citing the subject revision
above.
