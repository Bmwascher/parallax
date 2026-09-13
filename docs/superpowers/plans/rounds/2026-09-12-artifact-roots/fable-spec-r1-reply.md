# Fable spec pre-read, round 1 (verbatim reply)

Lane: parallax:fable-panel-reviewer (same-harness, Claude Code 2.1.261, not cross-vendor).
Brief: brief-fable-spec-r1.md. Subject blob ed8674b2143d94ea5bea636ee3ed78e1e8acdfa7.
Dispatched 2026-09-12; 56 tool uses, 405 s.

---

# Fable spec pre-read, round 1

Subject: `docs/superpowers/specs/2026-09-12-artifact-roots-design.md` at blob `ed8674b2143d94ea5bea636ee3ed78e1e8acdfa7`. Paths below are relative to `C:/Users/Brandon/Documents/parallax` unless rooted.

## Claims

**1. Citations in "measured facts" resolve.** REFUTE on three qualifiers; the substantive point stands.
- Verified: `references/frozen-plan-format.md:26-28` (plan save path with the KE example), `:84-87` (rounds root), `SKILL.md:321-324` (KE literal is on `:323`, one line off), `SKILL.md:389` (attestation path), `tools/write-attestation.ps1:99` (checkpoint dir), `references/preflight-mirror.md:12-13` ("a SHORT `<scratch>` directly under the temp directory"), `agents/fable-reviewer.md:18` (ledger path as input).
- Refuted, spec:15-16 "override written as an inline example in both places": `frozen-plan-format.md:85-87` carries no KitnEssentials example; only `:28` does.
- Refuted, spec:17 "attestation root is named once": also `tools/write-attestation.ps1:72` and `tools/verify-attestation.ps1:177`.
- Refuted, spec:18 "checkpoint root only inside write-attestation.ps1:99": also `tools/verify-attestation.ps1:125`, `tools/write-attestation.ps1:32`, and `references/application-checkpoint.md:80` (`<git-common-dir>/parallax/application-checkpoints/<stamp>-<reviewed-head12>.md`). This matters because the spec's static sweep (spec:198-199) scans `tools/` and must know its baseline.

**2. SDD ledger root is hard-coded by Superpowers.** ACCEPT. Read `C:/Users/Brandon/.claude/plugins/cache/claude-plugins-official/superpowers/6.3.0/skills/subagent-driven-development/scripts/sdd-workspace:35-39`: `base="$root/.superpowers/sdd"`, `dir="$base/$slug"`, `printf '*\n' > "$base/.gitignore"`, with `slug=$(basename "$plan" .md)` at `:31`. The spec's quoted path and the self-ignoring `.gitignore` match. The sentence "Its own ledger check reads that path back" (spec:26) is UNVERIFIED: I read only `sdd-workspace`, not `task-brief` or `review-package`.

**3. Eight `Canonical ... :` lines after the backup block are compatible with parsers and pin rules.** ACCEPT for the runtime parsers, REFUTE for the pin rules as the spec states them.
- Parsers are label-anchored and unaffected by lines that follow the backup block: `tools/check-drift.ps1:1010-1011`, `evals/tools/run_behavioral_evals.py:813-814`, `evals/tools/lane_credential_live_support.py:129` (`re.escape(label) + ": `([^`]+)`"`). Ordering pins end at the backup id: `test_multi_model_verify.py:1206-1210`, `test_backup_lane.py:80-81`, `test_seat_reshuffle.py:298-299`. No `count("Canonical ...")` pin exists in `evals/`.
- Pin rules: spec:194-196 says "A pin per line, in the `"literal" in body` form the coverage checker recognizes." That does not lock the region. `contract_coverage.py:131` folds the whole region into one normalized body, and `test_contract_coverage.py:537-553` lock that a pin stopping mid-region or two pins jointly spanning it leave the region uncovered. Eight per-line pins leave `artifact-roots` red under `test_every_marked_region_is_locked_by_a_pin` (`:951-954`). The fix is one pin holding the whole region text; the spec must also say exactly which text sits between the markers (only the eight lines, or the bullets at spec:88-108 too), because `CLAUDE.md` holds that a region too long for one pin is two regions.

**4. Existence-based override resolves KE, no false positive here or in fixtures.** ACCEPT. No `dev/` directory in this repo (Glob `dev/**` empty). No fixture in `evals/` creates one: the only `dev/docs` hits are pins on backup-lane prose (`test_backup_lane.py:692`); `test_dispatch_round.py:177-183` builds a one-file repo. KE resolution: `BACKLOG.md:100` records 76 gate folders under `dev/docs/superpowers/plans/rounds/`, so the directory exists there. Note that the rule fires on directory existence alone, so a consumer carrying both roots gets the override silently; the printed `docs-root source` line (spec:145-146) is what makes that visible.

**5. The `-Assert` set is right.** ACCEPT for the set, with one row-shape defect. The retention copy targets the rounds root (spec:170); nothing in the skill copies into the ledger or mirror. But the attestation and checkpoint rows are declared as `.git/parallax/...` (spec:84-85), while the tools resolve `git rev-parse --git-common-dir` (`tools/write-attestation.ps1:54-63`, `:72`, `:99`; `tools/verify-attestation.ps1:125`, `:177`). In a linked worktree `.git` is a file and the common dir is elsewhere, so a resolver computing `<RepoRoot>/.git/parallax/attestations/` names a path the emitter never writes and `-Assert` on the real output answers `outside every retained root`. `references/application-checkpoint.md:80` already spells the row as `<git-common-dir>/...`; the declaration should match and the resolver should run the same `rev-parse`.

**6. The central assertion can FAIL and the fixtures fit.** ACCEPT that the fixtures write nothing in-repo; REFUTE that they fit the spec's description as written, and the can-fail property is asserted, not shown.
- Locations: source `tmp_path/mirror-src`, mirror `tmp_path/real-mirror` (`test_dispatch_round.py:177-188`); dispatch dir, receipt, body and prior all under `tmp_path` (`:230-235`, `:249-250`). Mirror sidecars land beside the mirror: `tools/new-review-mirror.ps1:1477-1478` (override file), `:743` (`.source-manifest`).
- Known in-repo write: git's index refresh during status capture rewrites `.git/index` (`tools/new-review-mirror.ps1:1665-1669`). It modifies, it does not add a path, so the path-set diff at spec:224-225 survives it; a content diff would not.
- Fixture mismatch: `build_real_mirror` creates its own one-commit source (`:177-183`) and takes no source argument. `write-attestation.ps1:67-70` exits 2 when base and head resolve to the same commit. So the spec's "disposable repository with two commits ... through the build_real_mirror and prepare_default fixtures" (spec:208-222) cannot run without extending the fixture; adding a commit after the build moves `source_head` and `-Prepare` blocks on identity (`tools/dispatch-round.ps1:96-100`).
- Can-fail: no negative control is specified. `frozen-plan-format.md:22-25` requires every verification to be able to fail; the eval needs a stub writer that creates `<repo>/rounds/x` and an assertion that the diff logic reports it.
- Also: `test_dispatch_round.py:32-35` skips at module level; that mark does not travel with an import, so the new module needs its own.

**7. Sweep shapes catch the two KE roots, no false positive today.** ACCEPT on sufficiency for the two roots; REFUTE on "no false positive".
- Grep over `skills/ agents/ commands/ hooks/ tools/`: `superpowers/rounds` and `review-sources` have zero hits; all seven `docs/superpowers/plans/rounds/` hits are preceded by `plans/` (`debate-protocol.md:75`, `backup-lane.md:618`, `frozen-plan-format.md:85`, `model-prompting-notes.md:109,111`, `panels.md:63,95`). `dev/docs/superpowers` hits only `SKILL.md:323` and `frozen-plan-format.md:28`, both of which spec:171-173 removes.
- False positive: `references/model-prompting-notes.md:87` cites `.superpowers/sdd/2026-08-15-resume-preamble-refresh/progress.md`. Spec:205-207 defines a historical citation as a path under `docs/superpowers/plans/rounds/<date>-` only, so this dated ledger citation fails the sweep as specified. The exemption needs a `.superpowers/sdd/<date>-` shape.
- Gap (note): `BACKLOG.md:95` names bare `rounds/` as one of the three roots; no sweep shape covers it, only `-Assert`.

**8. Limits stated correctly, nothing else overclaims.** REFUTE in part. The "does not prove" section is right. Elsewhere:
- spec:226-227 "A tool that writes anywhere else inside the repo turns this red": only a tool that creates a new path, only the three tools, only the exercised modes (`-SkipProbe`, `-NoWorkdirEvidence`).
- spec:188-190 "check_workflow_paths.py covers the listing": it locks only modules in `REQUIRED_DUAL_HOST_MODULES` (`evals/tools/check_workflow_paths.py:61-79`; the comment at `:64-67` says a module absent from the list is not locked). `test_dispatch_round.py` is in both workflow steps (`skill-evals.yml:134,155`) and absent from that list. The new module must be added to the list or the parity claim is empty.
- spec:232-235 credits `test_lane_credential_live.py` with sys.path sibling import; it uses `importlib.util.spec_from_file_location` (`test_lane_credential_live.py:27-37`). The mechanism is real, demonstrated by `test_contract_coverage.py:12` (`from contract_coverage import ...`) with no `conftest.py`, `pytest.ini` or `__init__.py` under `evals/`; wrong example.
- UNVERIFIED: spec:35-36 `git log -S` result (read-only seat, no git); spec:37-39 the Codex rollout log; spec:44-46 the KE `CLAUDE.md` quotation.

## Findings the claims do not cover

**F1, blocking: preflight step 4 writes into the repo during the quiet period.** Spec:165-167 places the resolver as preflight step 4, after step 3, and retains `artifact-roots.txt` "in the rounds folder", which is inside the reviewed repo. Step 3 builds the mirror (`SKILL.md:58`; `preflight-mirror.md:3`). The contract region at `preflight-mirror.md:39-54` forbids any in-repo write from mirror build to wrapper exit and says one new untracked file is enough; `:59-60` says "BUILD THE MIRROR LAST. Every act that writes inside the reviewed repository finishes first." The first debate under the new text refuses at `-Prepare` (`dispatch-round.ps1:96-100`). Fix: run the resolver before the mirror build, write its output to scratch, and copy it into the rounds root after the wrapper exits, which is what spec:101-106 already says for every other retained artifact.

**F2, should-fix: SKILL.md has no room for a step 4.** `BACKLOG.md:4219-4227`: about 6485 of a 6500 hard ceiling, "The next edit that needs room in SKILL.md has to remove something." `evals/tools/skill_lint.py:132-133`, `:340-351` make over-ceiling an ERROR; CI tier 1 runs `--strict` (`skill-evals.yml:29-35`). The spec adds a multi-sentence step (spec:165-170) and a citation swap at `:322-324`, with no accounting. It must say where the words come from, or put the step body in a reference file with a one-line pointer.

**F3, should-fix:** attestation and checkpoint rows as `<git-common-dir>`-relative (claim 5).

**F4, should-fix:** one whole-region pin, and an exact statement of the region's contents (claim 3).

**F5, should-fix:** sweep exemption for dated `.superpowers/sdd/` citations (claim 7).

**F6, should-fix:** extend `build_real_mirror` to accept a prepared two-commit source, or state the fixture edit (claim 6).

**F7, should-fix:** a negative control for the tree-diff assertion (claim 6).

**F8, should-fix:** add the new module to `REQUIRED_DUAL_HOST_MODULES` and say so (claim 8).

**F9, note:** fact 1's three qualifiers ("once", "only", "both places") and the `SKILL.md:322` line number (claim 1). Correct in place.

**F10, note:** bare `rounds/` has no static-sweep shape (claim 7).

## Verdict

FIX, on blob `ed8674b2143d94ea5bea636ee3ed78e1e8acdfa7`. The design's core decisions (fixed ledger and mirror rows with reasons, existence-based override with `-DocsRoot`, the `-Assert` set, the exit map mirroring `dispatch-round.ps1:124-126`) are sound and evidenced. The spec cannot go to a plan as written because F1 makes the shipped skill contradict its own quiet-period contract on the first real debate, and F2 through F8 each describe an eval or an edit that would go red on a correct implementation or lock nothing. All are specific edits to the spec text; none reopens a decision.

---

## Session adjudication (2026-09-12)

All ten findings verified against source by the session before any edit;
`skill_lint --strict` measured SKILL.md at 6496 tokens, worse than the
backlog's 6485. Every finding was applied to the spec in place, with one
change of remedy: F1's proposed ordering rule (resolver before the mirror
build) is not needed once the resolver writes to scratch and the copy
into the rounds root happens after the wrapper exits, like every other
retained artifact, so the spec takes that form and no ordering rule
against the build is added. F10 is recorded as a stated limit, not fixed:
a bare `rounds/` literal is too common to sweep and `-Assert` covers the
write. Claim 2's UNVERIFIED sentence now cites the Superpowers
`SKILL.md:141` ledger check the session read.
