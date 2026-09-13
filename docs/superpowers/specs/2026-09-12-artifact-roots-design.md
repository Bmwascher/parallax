# Design: one declaration of every path a round writes

**Filed 2026-09-12** for BACKLOG item 100. A KitnEssentials cleanup on
this date found parallax round artifacts across four roots in one
repository, written by different plugin versions and by writers that
honoured the repo's `docs/superpowers -> dev/docs/superpowers` override
inconsistently. KitnEssentials archives its own history by hand; this
design makes the plugin stop adding to the spread.

## The measured facts

1. The plugin has no single statement of where a debate writes. The
   frozen plan and the rounds root are named in
   `skills/multi-model-verify/references/frozen-plan-format.md:27` and
   `:85`, with the KitnEssentials override written as an inline example
   in both places and again at `skills/multi-model-verify/SKILL.md:322`.
   The attestation root is named once, in `SKILL.md:389`, and the
   checkpoint root only inside `tools/write-attestation.ps1:99`. The
   mirror root is prose in `references/preflight-mirror.md` ("a SHORT
   `<scratch>` directly under the temp directory"). The SDD ledger root
   is not named by the plugin at all; `agents/fable-reviewer.md:18` takes
   it as an argument.
2. The SDD ledger root is not the plugin's to place. Superpowers
   `subagent-driven-development/scripts/sdd-workspace` hard-codes
   `<repo-root>/.superpowers/sdd/<plan-basename>/` and writes a
   self-ignoring `.gitignore` beside it. Its own ledger check reads that
   path back, so a plugin that moved the ledger would break the skill it
   is built on.
3. The review mirror must sit outside the reviewed repository.
   `tools/new-review-mirror.ps1:1460` already refuses a `-MirrorPath`
   equal to, inside, or containing the repo, and
   `evals/multi-model-verify/test_review_mirror.py:565` pins the refusal.
4. Two of the four KitnEssentials roots were not written by any parallax
   writer. `dev/docs/superpowers/rounds/` has no source in this repo's
   history at any version (`git log -S'superpowers/rounds' --all` finds
   only the backlog filing). The 54 MB
   `.superpowers/review-sources/dt-diag-2766cd59/` was written on
   2026-09-07 by a Codex controller session that invented a "preparation
   copy" of a worktree; its rollout log says so in its own words. The
   plugin binds its own tools and the prose the Claude controller
   follows. It cannot bind a foreign controller, and this design does
   not claim to.
5. The repo-side override has no mechanical form. KitnEssentials
   declares it as a prose line in its `CLAUDE.md` ("wherever a plugin
   skill says `docs/superpowers/...`, read it as
   `dev/docs/superpowers/...`"). A tool cannot read that reliably, and a
   session reading it per writer is the drift the item describes.

## Decisions taken in brainstorming (2026-09-12)

- **Override discovery is existence-based, with an explicit escape.**
  The docs root is `dev/docs/superpowers` when that directory exists
  under the repo root, else `docs/superpowers`; a `-DocsRoot` argument
  overrides both, and the printed line names which rule fired. No
  consumer setup is needed and KitnEssentials resolves correctly today.
- **The ledger and mirror roots are declared FIXED, with their reasons,
  and item 100's closing criteria are edited in place to match.** The
  backlog asked for the mirror and ledger roots to be gitignored by the
  same entry as the rounds. Facts 2 and 3 make that impossible without
  forking the vendor script or moving the mirror into the repo, and
  neither trade is worth the single gitignore line.

## The declaration

A new section in
`skills/multi-model-verify/references/model-prompting-notes.md`, placed
AFTER the backup reviewer lane block (the primary model declarations
must stay first, because two runtime parsers match the first
`Canonical model id:` occurrence). It is wrapped in
`<!-- contract:start id=artifact-roots -->` / `contract:end` so the
coverage checker in `test_contract_coverage.py` requires a pin, and it
is registered in that file's `DECLARED_REGIONS`.

The machine-read lines, in the same one-value-per-line style as the
model declarations:

```
Canonical docs root: `docs/superpowers`
Canonical docs root override: `dev/docs/superpowers`
Canonical frozen plan path: `<docs-root>/plans/<date>-<topic>.md`
Canonical rounds root: `<docs-root>/plans/rounds/<date>-<topic>/`
Canonical SDD ledger root: `.superpowers/sdd/<plan-basename>/`
Canonical review mirror root: `<TEMP>/<short-name>/`
Canonical attestation root: `.git/parallax/attestations/`
Canonical checkpoint root: `.git/parallax/application-checkpoints/`
```

The prose around them states, for each fixed row, why it is fixed:

- SDD ledger: Superpowers-owned; its `sdd-workspace` script writes the
  directory and the self-ignoring `.gitignore`; the plugin cites it and
  never relocates it.
- Review mirror: never inside the reviewed repository; the tool refuses
  an in-repo path; `<TEMP>` is `$env:TEMP` on the controller host.
- Attestation and checkpoint: under the repo's git common dir so that
  recording a verdict cannot move `HEAD`; the verifier re-hashes the
  checkpoint there.

And two rules that are prose because no tool can enforce them:

- Dispatch directories, receipts, briefs, prior-state files and the
  probe's override file live in session scratch OUTSIDE the repository
  for the whole round (the quiet period in
  `references/preflight-mirror.md` forbids in-repo writes anyway). Only
  their retained COPIES enter the rounds root, and only after the
  wrapper exits.
- A controller other than Claude Code is outside this contract. Fact 4
  is the record of what one wrote.

The two overridable rows are exactly the ones containing `<docs-root>`.
The resolver finds them by that placeholder, so adding an overridable
row later is one declaration line, not a tool edit.

## The resolver

`tools/artifact-roots.ps1`, new, following the conventions the other
tools already carry (both PowerShell hosts, literal paths, no `Stop`
preference around native calls, `-Json` output shape).

```
-RepoRoot <path>            required; must be a git working tree
-DocsRoot <relative path>   optional; explicit override, relative to the
                            repo root, no `..` segment, no rooted path
-Assert <path>              optional; exit 0 when the path (existing or
                            not) lies inside one of the retained in-repo
                            roots, 1 otherwise
-Json                       optional
```

Behaviour:

1. Read the declaration from the plugin's own
   `references/model-prompting-notes.md`, located relative to
   `$PSScriptRoot`. Every one of the eight `Canonical ... :` lines must
   be present inside the `artifact-roots` region; a missing line, a
   missing region, or a duplicate line is an ERROR with exit 2. A
   remembered path is never substituted.
2. Resolve `<docs-root>`: `-DocsRoot` if given; else the override value
   if `<RepoRoot>/<override>` exists as a directory; else the default.
   Record the source as one of `-DocsRoot`, `override directory
   exists`, `default`.
3. Substitute `<docs-root>` in the two overridable rows and `<TEMP>` in
   the mirror row. Leave `<date>-<topic>`, `<plan-basename>` and
   `<short-name>` as printed placeholders: they are named per debate.
4. Print one line per row, `name: <absolute path>`, then
   `docs-root source: <source>`. With `-Json`, emit one object with the
   same keys plus `source`. The absolute path for a placeholder-bearing
   row is the row's PARENT resolved plus the placeholder tail, e.g.
   `C:/repo/dev/docs/superpowers/plans/rounds/<date>-<topic>/`.
5. `-Assert`: canonicalize the path (full path, forward slashes, no
   trailing separator) and test membership under the frozen-plan
   parent, the rounds root, the attestation root and the checkpoint
   root, each with its placeholder tail removed. Exit 0 on membership,
   1 otherwise, printing which root matched or `outside every retained
   root`. The mirror and ledger roots are NOT in the `-Assert` set: the
   session never copies into them.

Exit map: 0 resolved (or asserted inside), 1 asserted outside, 2 for a
parameter fault, an unreadable declaration, or a `-RepoRoot` that is not
a git working tree. The map mirrors `tools/dispatch-round.ps1`'s so a
caller reads one convention.

## Skill and agent edits

- `SKILL.md` preflight gains step 4, both modes: run the resolver
  against the reviewed repo, retain its output as `artifact-roots.txt`
  in the rounds folder, and use the printed paths for every later act
  that names one: the frozen plan save, the rounds retention, the ledger
  citation in the fable-reviewer dispatch, the attestation emitter's
  expected output. Before the retention copy, `-Assert` the destination.
- `SKILL.md:322-324` (mode plan step 5) and
  `frozen-plan-format.md:27-28` and `:85` stop naming the KitnEssentials
  path by hand and cite the declaration's frozen-plan and rounds rows.
- `references/preflight-mirror.md` and `references/backup-lane.md` cite
  the mirror row where they describe the scratch location; the
  operational text (short name, path budget) stays where it is.
- `agents/fable-reviewer.md:18` cites the ledger row so the dispatcher
  knows where the path it is handing over comes from.
- `commands/doctor.md` is NOT extended. The resolver is a per-debate
  preflight, not a health probe.

No pin-bearing sentence is reflowed; the edits are additions and
citation swaps, checked against `test_contract_coverage.py` and the raw
pins in `test_multi_model_verify.py` before the wording is settled.

## The eval

`evals/multi-model-verify/test_artifact_roots.py`, new, added to BOTH
host steps of the `powershell-hosts` job (the workflow-path checker in
`evals/tools/check_workflow_paths.py` covers the listing).

Three groups:

1. **Declaration.** The region exists, carries all eight lines, and the
   primary `Canonical model id:` still precedes it. A pin per line, in
   the `"literal" in body` form the coverage checker recognizes.
2. **Static consistency sweep**, the same shape as the no-hardcoded-`-m`
   test. Every path literal in `skills/`, `agents/`, `commands/`,
   `hooks/` and `tools/` that names a round-artifact root must be one
   the declaration states. The forbidden shapes are enumerated so the
   sweep reports what it searched for: `superpowers/rounds/` not preceded
   by `plans/`, `review-sources`, `dev/docs/superpowers` outside the
   declaration line and outside a dated historical citation, a bare
   `.superpowers/sdd/` that is not the declared row or a dated
   citation. A historical citation is a path under `docs/superpowers/
   plans/rounds/<date>-` naming a retained record; those resolve under
   the declared rounds root and pass.
3. **Behavioural, real tools, both hosts.** In a disposable repository
   with two commits:
   - the resolver prints the default set; after `mkdir
     dev/docs/superpowers`, it prints the override set with source
     `override directory exists`; with `-DocsRoot other/root` it prints
     that with source `-DocsRoot`; `-DocsRoot ../x` and a rooted value
     exit 2; a `-RepoRoot` that is not a git tree exits 2.
   - `-Assert` exits 0 for a path under the resolved rounds root and the
     attestation root, 1 for `<repo>/rounds/x`, `<repo>/.superpowers/
     review-sources/x`, and a path outside the repo.
   - the writers: snapshot the repo tree (every path, ignored ones
     included), run `tools/write-attestation.ps1` for the two commits,
     run `tools/dispatch-round.ps1 -Prepare` through the
     `build_real_mirror` and `prepare_default` fixtures already in
     `test_dispatch_round.py` with the dispatch directory and receipt
     outside the repo, and run `tools/new-review-mirror.ps1` to a temp
     path; diff the tree; assert every path that APPEARED inside the
     repo satisfies `-Assert`, and that the set is exactly the
     attestation file. A tool that writes anywhere else inside the repo
     turns this red.
   - the mirror tool still refuses an in-repo `-MirrorPath` (the
     existing pin stays; this test cites the declaration row in its
     name).

The behavioural group depends on the fixtures in `test_dispatch_round.py`
being importable from a sibling module; pytest's default import mode
puts the test directory on `sys.path`, which is how the existing
`test_lane_credential_live.py` reaches its support module.

## What the eval does not prove

The rounds retention is a session act, a copy from scratch into the
rounds root at the end of a debate. The eval proves the resolver names
the right destination and the skill text sends the session there; it
cannot prove a session obeyed. The `-Assert` step before the copy is the
mechanical half of that act, and the behavioural runner
(`evals/tools/run_behavioral_evals.py`) is where obedience is measured.

## Backlog

Item 100's "What closing it means" paragraph is edited in place, dated
2026-09-12, to state the ledger and mirror roots as fixed with their
reasons and to drop the shared-gitignore sentence. Status stays OPEN
until the diff debate closes it.

## Out of scope

- Migrating any consumer tree. KitnEssentials archives by hand.
- The plugin's own `tools/drift-reports/` and `drift-snapshot.json`.
  They are plugin-side state in the plugin checkout, not consumer-repo
  artifacts.
- Binding a Codex or other foreign controller.
- Extending `/parallax:doctor`.
