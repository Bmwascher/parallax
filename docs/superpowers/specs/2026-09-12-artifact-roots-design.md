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
   at `:28` and again at `skills/multi-model-verify/SKILL.md:323`.
   The attestation root is named in `SKILL.md:389` and computed in
   `tools/write-attestation.ps1:72` and `tools/verify-attestation.ps1:177`;
   the checkpoint root is computed in `tools/write-attestation.ps1:99`
   and `tools/verify-attestation.ps1:125` and named in
   `references/application-checkpoint.md:80`. The mirror root is prose in
   `references/preflight-mirror.md:12` ("a SHORT `<scratch>` directly
   under the temp directory"). The SDD ledger root is not named by the
   plugin at all; `agents/fable-reviewer.md:18` takes it as an argument.
2. The SDD ledger root is not the plugin's to place. Superpowers
   `subagent-driven-development/scripts/sdd-workspace:35-39` hard-codes
   `<repo-root>/.superpowers/sdd/<plan-basename>/` and writes a
   self-ignoring `.gitignore` beside it, and that skill's `SKILL.md:141`
   reads the ledger back from `<workspace>/progress.md`, so a plugin that
   moved the ledger would break the skill it is built on.
3. The review mirror must sit outside the reviewed repository.
   `tools/new-review-mirror.ps1:1460` already refuses a `-MirrorPath`
   equal to, inside, or containing the repo, and
   `evals/multi-model-verify/test_review_mirror.py:565` pins the refusal.
4. Two of the four KitnEssentials roots were not written by any parallax
   writer. `dev/docs/superpowers/rounds/` has no source in this repo's
   history at any version (`git log -S'superpowers/rounds' --all` finds
   only the backlog filing). The 54 MB
   `.superpowers/review-sources/dt-diag-2766cd59/` was written on
   2026-09-08 by a Codex controller session, started 2026-09-07, that
   invented a "preparation copy" of a worktree; its rollout log says so
   in its own words, at
   `~/.codex/sessions/2026/09/07/rollout-2026-09-07T20-53-38-01a07eb8-8a4c-7941-ba19-a542a5642dc9.jsonl`
   (record 3682 is the `exec_command` copying
   `.superpowers/worktrees/dt-diag` to that path; record 3684 is its
   successful execution, dated 2026-09-08). The session read it on
   2026-09-12 and the Astra R2 review verified the attribution and
   corrected the date; the 54 MB size is the KitnEssentials cleanup's
   own figure and is UNVERIFIED here. None of it bears on the verdict. The
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
`<!-- contract:start id=round-artifact-roots -->` / `contract:end` so
the coverage checker in `test_contract_coverage.py` requires a pin, and
it is registered in that file's `DECLARED_REGIONS`. The id carries the
`round-` prefix because `test_contract_coverage.py:795` reads every bare
occurrence of a declared id in `skills/`, `agents/` and `commands/` and
requires the `<file>.md's <id>` spelling; a region named `artifact-roots`
would make the tool's own file name an unresolvable citation (found by
the Astra R1 review). The region holds
EXACTLY the eight declaration lines below and nothing else, and ONE pin
in `test_artifact_roots.py` holds the whole region text: the checker
folds a region into one body and a pin that stops mid-region or two
pins that jointly span it leave it unlocked
(`test_contract_coverage.py:537-553`). The explanatory prose sits
outside the markers.

The machine-read lines, in the same one-value-per-line style as the
model declarations:

```
Canonical docs root: `docs/superpowers`
Canonical docs root override: `dev/docs/superpowers`
Canonical frozen plan path: `<docs-root>/plans/<date>-<topic>.md`
Canonical rounds root: `<docs-root>/plans/rounds/<date>-<topic>/`
Canonical SDD ledger root: `.superpowers/sdd/<plan-basename>/`
Canonical review mirror root: `<TEMP>/<short-name>/`
Canonical attestation root: `<git-common-dir>/parallax/attestations/`
Canonical checkpoint root: `<git-common-dir>/parallax/application-checkpoints/`
```

`<git-common-dir>` is what `git rev-parse --git-common-dir` returns for
the repo, which is what `tools/write-attestation.ps1:54-63` and
`tools/verify-attestation.ps1:125` already resolve, and what
`references/application-checkpoint.md:80` already writes. In a linked
worktree `.git` is a file and the common dir is elsewhere, so a row
spelled `.git/parallax/...` would name a path the emitter never writes.

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
- Implementation-time scratch is outside this contract: the rows name
  what a REVIEW ROUND writes. `agents/flash-implementer.md:67` writes a
  transient task brief into the checkout and `:79` deletes it before any
  evidence check; the SDD ledger is the one implementation artifact
  declared, because a round cites it. (Found by the Astra R1 class
  sweep.)
- A controller other than Claude Code is outside this contract. Fact 4
  is the record of what one wrote. The prose beside the declaration
  dates that record 2026-09-08.

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
3. Substitute `<docs-root>` in the two overridable rows, `<TEMP>` in
   the mirror row, and `<git-common-dir>` in the attestation and
   checkpoint rows from `git rev-parse --git-common-dir` run in
   `-RepoRoot` (a relative answer is joined to `-RepoRoot`, the
   directory git ran in, exactly as `tools/write-attestation.ps1:61`
   does; from a subdirectory git prints `../.git`). `-RepoRoot` itself
   is resolved through PowerShell's provider location before git sees
   it. PowerShell starts a native child in its own location, so git
   itself answers for the right directory; the fault is the RELATIVE
   answer git prints reaching .NET `GetFullPath`, which resolves against
   the process working directory and not PowerShell's location, so an
   unresolved `.` printed the launch directory's `.git` (found by the
   Astra R2 review on both hosts, mechanism corrected by R3; the same
   distinction `tools/new-review-mirror.ps1:1234` draws). Every path
   the tool resolves goes through one helper that turns a provider or
   .NET path failure (an unknown drive, a forbidden character) into
   exit 2 with an `ERROR:` line, and `-DocsRoot` is checked against one
   explicit forbidden-character set before any path API sees it,
   because 5.1 throws on `|` where 7 prints an unusable path (R3). Leave
   `<date>-<topic>`, `<plan-basename>` and `<short-name>` as printed
   placeholders: they are named per debate. The placeholder tail is
   split off BEFORE any path API sees the string: on Windows PowerShell
   5.1 `IsPathRooted` and `GetFullPath` throw on `<` (measured by the
   Astra R1 review), so the real parent is resolved and the tail is
   appended verbatim. An explicit `-DocsRoot` is canonicalized the same
   way, so `./other/root` prints and asserts as `other/root`.
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

- `SKILL.md` preflight gains step 4, both modes, as ONE line: run
  `tools/artifact-roots.ps1 -RepoRoot <repo>` and follow the operating
  rule in `references/model-prompting-notes.md`. That rule, written in
  prose beside the declaration, is: the resolver's output goes to
  session scratch OUTSIDE the repo (it is then a retained artifact like
  a brief, and enters the rounds root as `artifact-roots.txt` only after
  the wrapper exits, so the quiet period is untouched and no ordering
  rule against the mirror build is needed); every later act that names
  a path uses the printed one, the frozen plan save, the rounds
  retention, the ledger citation in the fable-reviewer dispatch, the
  attestation emitter's expected output; and the retention copy runs
  `-Assert` on its destination first.
- `SKILL.md` is at 6496 of `skill_lint.py`'s 6500-token ceiling
  (25987 body characters measured 2026-09-12 the linter's way;
  `BACKLOG.md:4219-4227` records the same). The one-line step is paid
  for by mode plan step 5 (`SKILL.md:321-324`), whose parenthetical
  naming the KitnEssentials and default plans directories is removed and
  replaced by "at the frozen-plan path preflight step 4 printed". A
  third edit, authorized by the user on 2026-09-12 after the Astra R1
  review, replaces the finish-line sentence at `SKILL.md:389` that names
  `.git/parallax/attestations/…` "inside the reviewed repo": that
  spelling is wrong in a linked worktree, where the emitter writes under
  the git common dir. The three edits together leave the body at 25985
  characters. The plan's task runs the linter after the edits; if the
  file is over the ceiling the task STOPS and asks the user what to
  remove, because that choice is the user's (the backlog entry says
  so), not the implementer's.
- `frozen-plan-format.md:27-28` and `:85` stop naming the KitnEssentials
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
host steps of the `powershell-hosts` job AND to
`REQUIRED_DUAL_HOST_MODULES` in `evals/tools/check_workflow_paths.py:61`
in the same act: that list is what locks a module into both steps, and
a module named in the workflow but absent from the list is not locked
(the comment at `:64-67` says so, and `test_dispatch_round.py` is an
existing example of the gap).

Three groups:

1. **Declaration.** The region exists, the primary `Canonical model id:`
   still precedes it, and one pin in the `"literal" in body` form holds
   the region's whole text, all eight lines as one folded literal.
2. **Static consistency sweep**, the same shape as the no-hardcoded-`-m`
   test. Every path literal in `skills/`, `agents/`, `commands/`,
   `hooks/` and `tools/` that names a round-artifact root must be one
   the declaration states. The forbidden shapes are enumerated so the
   sweep reports what it searched for: `superpowers/rounds/` not preceded
   by `plans/`, `review-sources`, `dev/docs/superpowers` anywhere but
   the declaration's override line, and `.superpowers/sdd/` anywhere but
   the declaration's ledger line or a dated citation, and
   `.git/parallax/` anywhere (the rows spell it
   `<git-common-dir>/parallax/`, and `SKILL.md:389` is the one stale
   spelling today). A dated citation is a path under
   `docs/superpowers/plans/rounds/<date>-` or `.superpowers/sdd/<date>-`
   naming a retained record (the plugin surface carries one of the
   latter today, at `references/model-prompting-notes.md:87`). The
   negative control asserts each shape fires on a KitnEssentials-form
   line and that each exemption holds. Measured 2026-09-12 by the
   Fable pre-read: the first two shapes have zero hits in the plugin
   surface, all seven `superpowers/plans/rounds/` hits are preceded by
   `plans/`, and the two `dev/docs/superpowers` hits are the ones this
   design removes. A bare `rounds/` literal has no static shape, because
   the word is too common to sweep; `-Assert` is what covers it.
3. **Behavioural, real tools, both hosts.** The module carries its own
   module-level skip when no PowerShell host is on PATH; the mark in
   `test_dispatch_round.py:32-35` does not travel with an import. The
   test builds a disposable source repository with TWO commits, because
   `write-attestation.ps1:67-70` refuses base and head that resolve to
   one commit, and `build_real_mirror` in `test_dispatch_round.py:173`
   creates its own one-commit source with no way to pass one in. So the
   plan extends that fixture with an optional `source` argument whose
   default keeps today's behaviour, and every existing caller is
   unchanged.
   - the resolver prints the default set; after `mkdir
     dev/docs/superpowers`, it prints the override set with source
     `override directory exists`; with `-DocsRoot other/root` it prints
     that with source `-DocsRoot`; `-DocsRoot ../x` and a rooted value
     exit 2; a `-RepoRoot` that is not a git tree exits 2.
   - `-Assert` exits 0 for a path under the resolved rounds root and the
     attestation root, 1 for `<repo>/rounds/x`, `<repo>/.superpowers/
     review-sources/x`, and a path outside the repo.
   - the writers: snapshot the repo tree as a SET OF PATHS, files AND
     directories (every path, ignored ones included; `.git/index` is
     rewritten by the status capture in `new-review-mirror.ps1:1665-1669`,
     so a content diff would fire on a correct tool and a path-set diff
     does not; directories are included so a writer that only creates
     an empty directory is observed), run
     `tools/write-attestation.ps1` for the two commits, run
     `tools/dispatch-round.ps1 -Prepare` through the extended
     `build_real_mirror` and `prepare_default` with the dispatch
     directory and receipt outside the repo, and run
     `tools/new-review-mirror.ps1` to a temp path with `-SkipProbe`;
     diff the sets; assert the set is exactly the attestation file
     plus the two directories the emitter creates for it, that the
     attestation directory and the file satisfy `-Assert`, and that the
     shared parent `parallax/` (created on the way down, not itself a
     declared root) is refused by `-Assert`; the exact-set assertion is
     what bounds that parent.
   - negative controls, so the diff logic is shown able to fail: a stub
     writer creates `<repo>/rounds/x`, and the same diff-and-assert
     reports it; a second stub only creates an empty
     `.superpowers/review-sources/` directory, and that is reported too.
   - the mirror tool still refuses an in-repo `-MirrorPath` (the
     existing pin stays; this test cites the declaration row in its
     name).

What group 3 proves is bounded: only a tool that CREATES a path is
caught, only the three tools are run, and only in the modes the test
exercises (`-SkipProbe`, and whatever `prepare_default` passes). A tool
that rewrites an existing in-repo file is outside it, and so is a path
created and deleted again between the two snapshots: the test samples
endpoints, and the Flash implementer's transient brief is a real example
of that shape (Astra R1 class sweep). The static sweep is bounded the
same way: it reads five literal shapes, and a destination assembled at
run time from pieces matches none of them.

The behavioural group imports the fixtures from `test_dispatch_round.py`
as a sibling module; pytest's default import mode puts the test
directory on `sys.path`, which is how `test_contract_coverage.py:12`
reaches `contract_coverage.py` with no `conftest.py` or package marker
under `evals/`.

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
- Implementation-time artifacts (the Flash implementer's transient
  brief, SDD task briefs and reports); the declaration names what a
  review round writes and cites the ledger because a round reads it.
- The plugin's own `tools/drift-reports/` and `drift-snapshot.json`.
  They are plugin-side state in the plugin checkout, not consumer-repo
  artifacts.
- Binding a Codex or other foreign controller.
- Extending `/parallax:doctor`.
