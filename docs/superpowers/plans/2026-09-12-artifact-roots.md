# Artifact Roots Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** One declaration of every path a multi-model-verify round writes into a consumer repository, one override rule applied by one tool, a preflight step that prints the resolved set, and an eval that goes red when a writer or a skill sentence names a root outside it.

**Architecture:** The declaration is eight `Canonical ... :` lines inside a contract region in `references/model-prompting-notes.md`, the same swap-by-one-edit shape as the model declarations. `tools/artifact-roots.ps1` is the only reader: it parses the region at runtime, resolves the two `<docs-root>` rows by the existence rule, prints the set, and answers `-Assert` for a retention destination. `evals/multi-model-verify/test_artifact_roots.py` pins the region, sweeps the plugin surface for a hand-named root, and drives the three real writers in a disposable repo under both PowerShell hosts.

**Tech Stack:** PowerShell 5.1 and 7 (ASCII-only tools), Python 3 pytest evals, GitHub Actions `powershell-hosts` job.

**Spec:** `docs/superpowers/specs/2026-09-12-artifact-roots-design.md` (Fable pre-read applied at commit 29d2376; the round is retained under `docs/superpowers/plans/rounds/2026-09-12-artifact-roots/`).

## Global Constraints

- Tools under `tools/` are ASCII ONLY and run under BOTH Windows PowerShell 5.1 and PowerShell 7. Never run a native `git` call under `$ErrorActionPreference = 'Stop'`; drop to `Continue` around it and read `$LASTEXITCODE`.
- `SKILL.md` is at 6497 of `skill_lint.py`'s 6500-token ceiling (`len(body) // 4`, so 26000 characters). Task 3 makes EXACTLY the two edits it quotes and nothing else in that file. If `python evals/tools/skill_lint.py skills/multi-model-verify --strict` reports an ERROR afterwards, STOP and report to the user; do not trim other text.
- A contract region must sit WHOLE inside ONE pin in `evals/multi-model-verify/`, the pin being a plain string literal in `"literal" in body` form (adjacent literals fold; a variable does not count). Do not reflow any existing paragraph in `skills/`: raw-text pins break on a rewrap.
- No path literal in `skills/`, `agents/`, `commands/`, `hooks/` or `tools/` may name a round root except the declaration lines themselves. Cite the declaration instead. In prose, do not write the strings `review-sources`, `dev/docs/superpowers` or `superpowers/rounds/`; Task 3's sweep forbids them.
- Stage by explicit path (`git add <file> <file>`); `git add -A` is refused by the family git guard. Commit messages are lowercase imperative with no AI attribution, and must not contain a token that looks like a PowerShell flag (`-Prepare`, `-Assert`): the commit-msg guard reads it as an option.
- New tests select the host through `PARALLAX_PS_HOST` and skip off Windows, the same way `test_dispatch_round.py:29-35` does. Run the PowerShell-facing module under both hosts before calling a task done: `$env:PARALLAX_PS_HOST = "powershell.exe"` and then `"pwsh.exe"`.
- Full gate before the final commit: the six CI commands in `CLAUDE.md` (skill_lint strict, skill_scanner, check_exact_line_oracles, run_trigger_evals, pytest, backlog_lint).

---

### Task 1: The declaration region, its registration, and its pin

**Files:**
- Modify: `skills/multi-model-verify/references/model-prompting-notes.md` (insert before the line `## The scope guard (every brief, every lane)`, currently line 768)
- Modify: `evals/multi-model-verify/test_contract_coverage.py:769-773` (the `DECLARED_REGIONS` set, after `"back-channel-auto-mirror",`)
- Create: `evals/multi-model-verify/test_artifact_roots.py`

**Interfaces:**
- Produces: the contract region `artifact-roots` holding exactly eight lines with these labels, which Task 2's tool parses by label: `Canonical docs root`, `Canonical docs root override`, `Canonical frozen plan path`, `Canonical rounds root`, `Canonical SDD ledger root`, `Canonical review mirror root`, `Canonical attestation root`, `Canonical checkpoint root`.
- Produces: the module `test_artifact_roots.py` with helpers `read(path)`, `REPO`, `NOTES`, `TOOL`, `POWERSHELL`, `needs_host` that Tasks 2 and 4 extend.

- [ ] **Step 1: Register the region so the coverage suite goes red**

In `evals/multi-model-verify/test_contract_coverage.py`, inside `DECLARED_REGIONS`, after the line `"back-channel-auto-mirror",` and before the closing `}`, add:

```python
    # 0.34.0, backlog item 100. One consumer repository held rounds,
    # ledgers and a mirror under four roots because every writer read the
    # repo-side override on its own. The region holds EXACTLY the eight
    # declaration lines tools/artifact-roots.ps1 parses; the prose that
    # says why two rows are overridable and four are fixed sits outside
    # the markers, because a region must fit one pin.
    "artifact-roots",
```

- [ ] **Step 2: Run the coverage suite and confirm the red names the region**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py -q -k declared_regions_match`
Expected: FAIL with `declared region(s) not found in any document: ['artifact-roots']`

- [ ] **Step 3: Write the declaration pin test**

Create `evals/multi-model-verify/test_artifact_roots.py`:

```python
"""Contract pins and behavioural checks for the artifact-roots declaration
(BACKLOG item 100; spec docs/superpowers/specs/2026-09-12-artifact-roots-design.md).

Three groups. DECLARATION: the eight canonical lines sit in one contract
region in model-prompting-notes.md, behind the primary model id, under
one whole-region pin. SWEEP: no path literal in the plugin surface names
a round root the declaration does not, and the sweep prints the shapes
it searched for. WRITERS: the real tools, run in a disposable repository
under whichever host PARALLAX_PS_HOST names, create nothing inside the
repository but the attestation, and a stub writer shows the diff logic
can fail.

WINDOWS ONLY for the resolver and writer groups: they drive
artifact-roots.ps1, new-review-mirror.ps1 and dispatch-round.ps1, which
target the Windows PowerShell hosting model. The declaration and sweep
groups are pure text and run everywhere. A green run on one host proves
ONE interpreter; the powershell-hosts CI job runs both.
"""
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
NOTES = REPO / "skills" / "multi-model-verify" / "references" / "model-prompting-notes.md"
TOOL = REPO / "tools" / "artifact-roots.ps1"
ATTEST = REPO / "tools" / "write-attestation.ps1"
MIRROR_TOOL = REPO / "tools" / "new-review-mirror.ps1"

POWERSHELL = (os.environ.get("PARALLAX_PS_HOST")
              or shutil.which("powershell") or shutil.which("pwsh"))

needs_host = pytest.mark.skipif(
    os.name != "nt" or POWERSHELL is None,
    reason="artifact-roots.ps1 and the writers it covers are Windows "
           "PowerShell tools")


def read(path):
    assert path.is_file(), f"missing file: {path}"
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------
# Group 1: the declaration
# ---------------------------------------------------------------------
def test_declaration_region_is_pinned_whole():
    # ONE pin over the whole region: the coverage checker folds a region
    # into one body, and a pin that stops mid-region locks nothing
    # (test_contract_coverage.py:537-553). Every line must stay on one
    # physical line in the notes, because this is a raw-text pin.
    notes = read(NOTES)
    assert (
        "<!-- contract:start id=artifact-roots -->\n"
        "Canonical docs root: `docs/superpowers`\n"
        "Canonical docs root override: `dev/docs/superpowers`\n"
        "Canonical frozen plan path: `<docs-root>/plans/<date>-<topic>.md`\n"
        "Canonical rounds root: `<docs-root>/plans/rounds/<date>-<topic>/`\n"
        "Canonical SDD ledger root: `.superpowers/sdd/<plan-basename>/`\n"
        "Canonical review mirror root: `<TEMP>/<short-name>/`\n"
        "Canonical attestation root: `<git-common-dir>/parallax/attestations/`\n"
        "Canonical checkpoint root: `<git-common-dir>/parallax/application-checkpoints/`\n"
        "<!-- contract:end -->"
    ) in notes


def test_primary_model_declaration_precedes_the_artifact_roots():
    # Two runtime parsers match the FIRST `Canonical model id:` occurrence
    # (model-prompting-notes.md, backup lane block); nothing in this
    # region may sit ahead of it.
    notes = read(NOTES)
    assert notes.index("Canonical model id:") < notes.index(
        "contract:start id=artifact-roots")


def test_fixed_rows_state_their_reason_outside_the_region():
    notes = read(NOTES)
    tail = notes[notes.index("contract:start id=artifact-roots"):]
    assert "Superpowers owns it" in tail
    assert "never inside the reviewed repository" in tail
    assert "git rev-parse --git-common-dir" in tail
```

- [ ] **Step 4: Run the new module and confirm both pins are red**

Run: `python -m pytest evals/multi-model-verify/test_artifact_roots.py -q`
Expected: 3 FAILED (`ValueError: substring not found` on the index test; the `in notes` assertions fail).

- [ ] **Step 5: Write the declaration section into the notes**

In `skills/multi-model-verify/references/model-prompting-notes.md`, insert the following block immediately BEFORE the line `## The scope guard (every brief, every lane)`. The eight lines between the markers must be byte-identical to Step 3's pin, each on one physical line.

```markdown
## Artifact roots (every path a round writes)

THE single source for where a debate lands in the reviewed repository,
in the same swap-by-one-edit shape as the model declarations above.
`tools/artifact-roots.ps1` parses the eight lines below at runtime and
fails loud when one is missing; nothing else in the plugin names a
round root by hand, and `evals/multi-model-verify/test_artifact_roots.py`
sweeps the plugin surface for one that does. Item 100 (2026-09-12) is
the record of why: one consumer repository held rounds, ledgers and a
mirror under four roots, because each writer read the repo-side
override on its own.

<!-- contract:start id=artifact-roots -->
Canonical docs root: `docs/superpowers`
Canonical docs root override: `dev/docs/superpowers`
Canonical frozen plan path: `<docs-root>/plans/<date>-<topic>.md`
Canonical rounds root: `<docs-root>/plans/rounds/<date>-<topic>/`
Canonical SDD ledger root: `.superpowers/sdd/<plan-basename>/`
Canonical review mirror root: `<TEMP>/<short-name>/`
Canonical attestation root: `<git-common-dir>/parallax/attestations/`
Canonical checkpoint root: `<git-common-dir>/parallax/application-checkpoints/`
<!-- contract:end -->

The override rule, applied to exactly the rows that carry
`<docs-root>`: the docs root is the override value when that directory
exists under the repo root, else the default; `-DocsRoot` names it
explicitly and wins over both, and the tool prints which of the three
fired as `docs-root source`. A repository carrying both directories
resolves to the override silently, which is what the printed source
line is for.

The other rows are FIXED, each for a reason the row cannot carry:

- SDD ledger: Superpowers owns it. Its subagent-driven-development
  `scripts/sdd-workspace` creates the directory and its self-ignoring
  `.gitignore`, and its ledger check reads `<workspace>/progress.md`
  back, so the plugin cites the path and never relocates it.
- Review mirror: never inside the reviewed repository.
  `tools/new-review-mirror.ps1` refuses a path equal to, inside, or
  containing the repo; `<TEMP>` is the controller host's temp
  directory, and references/preflight-mirror.md owns the short-name
  and path-budget rules.
- Attestation and checkpoint: under the git COMMON dir, so recording a
  verdict cannot move `HEAD` out from under its own SHA and every
  worktree sees one record; `tools/verify-attestation.ps1` re-hashes the
  checkpoint there. `<git-common-dir>` is what
  `git rev-parse --git-common-dir` prints, which in a linked worktree is
  not `.git`.

The operating rule, which SKILL.md's preflight step 4 points at:

- Run the tool once per debate, before round 1, against the reviewed
  repository (the REAL repo, not the mirror: the mirror is where the
  reviewer reads, the repo is where the record lands). Write its output
  to session scratch OUTSIDE the repository, beside the briefs. It is a
  retained artifact: it enters the rounds root as `artifact-roots.txt`
  when the other round files do, after the last wrapper exits, so the
  quiet period in references/preflight-mirror.md is never touched.
- Every later act that names one of these paths uses the printed value:
  the frozen plan save, the rounds retention, the ledger path handed to
  agents/fable-reviewer.md, the attestation the emitter is expected to
  write.
- Before the retention copy, run the tool with `-Assert <destination>`;
  exit 0 is the only clean answer. The ledger and mirror rows are not
  in the assert set, because the session never copies into them.
- Dispatch directories, receipts, briefs, prior-state files and the
  probe's override file are session scratch outside the repository for
  the whole round; only their retained copies enter the rounds root.
- A controller other than Claude Code is outside this contract. The
  2026-09-07 record in item 100 is of one that wrote a 54 MB copy of a
  worktree under a root of its own naming; the plugin binds its own
  tools and the prose the Claude controller follows, not a foreign one.

```

(The block ends with one blank line so the existing `## The scope guard` heading keeps a blank line above it.)

- [ ] **Step 6: Run the declaration tests and the coverage suite**

Run: `python -m pytest evals/multi-model-verify/test_artifact_roots.py evals/multi-model-verify/test_contract_coverage.py -q`
Expected: all PASS, including `test_every_marked_region_is_locked_by_a_pin` (the whole-region pin in Step 3 locks it).

- [ ] **Step 7: Run the model-declaration guards that read this file**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py evals/multi-model-verify/test_backup_lane.py evals/multi-model-verify/test_seat_reshuffle.py -q`
Expected: all PASS (the region sits after the backup block, so every ordering pin holds, and it contains no `-m` model literal).

- [ ] **Step 8: Commit**

```bash
git add skills/multi-model-verify/references/model-prompting-notes.md evals/multi-model-verify/test_contract_coverage.py evals/multi-model-verify/test_artifact_roots.py
git commit -m "declare every artifact root a round writes in one contract region"
```

---

### Task 2: The resolver tool

**Files:**
- Create: `tools/artifact-roots.ps1`
- Modify: `evals/multi-model-verify/test_artifact_roots.py` (append the resolver group)

**Interfaces:**
- Consumes: the `artifact-roots` region and its eight labels from Task 1.
- Produces: `tools/artifact-roots.ps1 -RepoRoot <path> [-DocsRoot <rel>] [-Assert <path>] [-Json]`. Text output is nine `name: value` lines in this order: `repo`, `docs-root`, `docs-root source`, `frozen-plan`, `rounds`, `sdd-ledger`, `review-mirror`, `attestation`, `checkpoint`, then with `-Assert` one line `assert: inside <root name>: <path>` or `assert: outside every retained root: <path>`. JSON output is one object with keys `repo`, `docsRoot`, `source`, `frozenPlan`, `rounds`, `sddLedger`, `reviewMirror`, `attestation`, `checkpoint`, and with `-Assert` an `assert` object `{path, inside, root}`. Exit 0 resolved or asserted inside; 1 asserted outside; 2 parameter fault, unreadable declaration, or not a git tree. Task 4 calls `-Assert`.

- [ ] **Step 1: Append the resolver tests**

Append to `evals/multi-model-verify/test_artifact_roots.py`:

```python
# ---------------------------------------------------------------------
# Group 3a: the resolver
# ---------------------------------------------------------------------
def run_resolver(*args, tool=None):
    return subprocess.run(
        [POWERSHELL, "-NoProfile", "-NonInteractive", "-File",
         str(tool or TOOL), *args],
        capture_output=True, text=True, timeout=60)


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True, check=True).stdout


def make_repo(tmp_path, name="repo", commits=1):
    repo = tmp_path / name
    repo.mkdir()
    git(tmp_path, "init", "-q", str(repo))
    for i in range(commits):
        (repo / f"file{i}.txt").write_text(f"content {i}\n")
        git(repo, "add", f"file{i}.txt")
        git(repo, "-c", "user.email=t@t", "-c", "user.name=t",
            "commit", "-q", "-m", f"commit {i}")
    return repo


def norm(p):
    """Forward slashes, no trailing separator, case-folded: Windows
    paths compare case-insensitively and the tool prints forward
    slashes."""
    return str(p).replace("\\", "/").rstrip("/").lower()


def resolved(repo, *extra):
    proc = run_resolver("-RepoRoot", str(repo), *extra, "-Json")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return json.loads(proc.stdout)


@needs_host
def test_resolver_prints_the_default_set(tmp_path):
    repo = make_repo(tmp_path)
    got = resolved(repo)
    assert got["source"] == "default"
    assert norm(got["repo"]) == norm(repo)
    assert norm(got["docsRoot"]) == norm(repo / "docs/superpowers")
    assert norm(got["frozenPlan"]) == norm(
        repo / "docs/superpowers/plans/<date>-<topic>.md")
    assert norm(got["rounds"]) == norm(
        repo / "docs/superpowers/plans/rounds/<date>-<topic>")
    assert norm(got["sddLedger"]) == norm(
        repo / ".superpowers/sdd/<plan-basename>")
    assert norm(got["attestation"]) == norm(
        repo / ".git/parallax/attestations")
    assert norm(got["checkpoint"]) == norm(
        repo / ".git/parallax/application-checkpoints")
    # The mirror row resolves OUTSIDE the repo, under the host temp dir.
    assert norm(got["reviewMirror"]).endswith("/<short-name>")
    assert not norm(got["reviewMirror"]).startswith(norm(repo) + "/")


@needs_host
def test_resolver_text_output_names_each_root_then_the_source(tmp_path):
    repo = make_repo(tmp_path)
    proc = run_resolver("-RepoRoot", str(repo))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    keys = [ln.split(": ", 1)[0] for ln in proc.stdout.splitlines()
            if ": " in ln]
    assert keys == ["repo", "docs-root", "docs-root source", "frozen-plan",
                    "rounds", "sdd-ledger", "review-mirror", "attestation",
                    "checkpoint"]


@needs_host
def test_override_directory_selects_the_override_root(tmp_path):
    repo = make_repo(tmp_path)
    (repo / "dev" / "docs" / "superpowers").mkdir(parents=True)
    got = resolved(repo)
    assert got["source"] == "override directory exists"
    assert norm(got["rounds"]) == norm(
        repo / "dev/docs/superpowers/plans/rounds/<date>-<topic>")
    assert norm(got["frozenPlan"]) == norm(
        repo / "dev/docs/superpowers/plans/<date>-<topic>.md")
    # Fixed rows do not move with the docs root.
    assert norm(got["sddLedger"]) == norm(
        repo / ".superpowers/sdd/<plan-basename>")
    assert norm(got["attestation"]) == norm(
        repo / ".git/parallax/attestations")


@needs_host
def test_docsroot_argument_wins_over_both_rules(tmp_path):
    repo = make_repo(tmp_path)
    (repo / "dev" / "docs" / "superpowers").mkdir(parents=True)
    got = resolved(repo, "-DocsRoot", "other/root")
    assert got["source"] == "-DocsRoot"
    assert norm(got["frozenPlan"]) == norm(
        repo / "other/root/plans/<date>-<topic>.md")


@needs_host
@pytest.mark.parametrize("bad", ["../x", "a/../b", "C:/abs/root", "/rooted"])
def test_docsroot_refuses_escapes_and_rooted_values(tmp_path, bad):
    repo = make_repo(tmp_path)
    proc = run_resolver("-RepoRoot", str(repo), "-DocsRoot", bad)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert proc.stdout.startswith("ERROR:"), proc.stdout


@needs_host
def test_reporoot_must_be_a_git_working_tree(tmp_path):
    plain = tmp_path / "plain"
    plain.mkdir()
    proc = run_resolver("-RepoRoot", str(plain))
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "not a git" in proc.stdout


@needs_host
def test_missing_declaration_line_is_an_error_not_a_default(tmp_path):
    # The tool finds the notes relative to its own location, so a copy
    # of the tool beside a doctored copy of the notes exercises the
    # parse failure without touching the real declaration.
    fake = tmp_path / "plugin"
    (fake / "tools").mkdir(parents=True)
    notes_dir = fake / "skills" / "multi-model-verify" / "references"
    notes_dir.mkdir(parents=True)
    shutil.copy(TOOL, fake / "tools" / "artifact-roots.ps1")
    doctored = read(NOTES).replace(
        "Canonical rounds root: `<docs-root>/plans/rounds/<date>-<topic>/`\n", "")
    assert doctored != read(NOTES)
    (notes_dir / "model-prompting-notes.md").write_text(doctored, encoding="utf-8")
    repo = make_repo(tmp_path)
    proc = run_resolver("-RepoRoot", str(repo),
                        tool=fake / "tools" / "artifact-roots.ps1")
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "Canonical rounds root" in proc.stdout


@needs_host
@pytest.mark.parametrize("rel, expect", [
    ("docs/superpowers/plans/rounds/2026-09-12-x/brief.md", 0),
    ("docs/superpowers/plans/2026-09-12-x.md", 0),
    (".git/parallax/attestations/abc.json", 0),
    (".git/parallax/application-checkpoints/abc.md", 0),
    ("rounds/x", 1),
    (".superpowers/review-sources/x", 1),
    (".superpowers/sdd/plan/progress.md", 1),
    ("docs/superpowers/rounds/x", 1),
])
def test_assert_answers_membership_in_the_retained_set(tmp_path, rel, expect):
    repo = make_repo(tmp_path)
    proc = run_resolver("-RepoRoot", str(repo), "-Assert", str(repo / rel))
    assert proc.returncode == expect, proc.stdout + proc.stderr
    assert "assert: " in proc.stdout


@needs_host
def test_assert_rejects_a_path_outside_the_repo(tmp_path):
    repo = make_repo(tmp_path)
    proc = run_resolver("-RepoRoot", str(repo), "-Assert",
                        str(tmp_path / "elsewhere" / "x"))
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "outside every retained root" in proc.stdout


@needs_host
def test_assert_follows_the_override(tmp_path):
    repo = make_repo(tmp_path)
    (repo / "dev" / "docs" / "superpowers").mkdir(parents=True)
    inside = run_resolver("-RepoRoot", str(repo), "-Assert",
                          str(repo / "dev/docs/superpowers/plans/rounds/2026-09-12-x/r1.md"))
    assert inside.returncode == 0, inside.stdout
    stale = run_resolver("-RepoRoot", str(repo), "-Assert",
                         str(repo / "docs/superpowers/plans/rounds/2026-09-12-x/r1.md"))
    assert stale.returncode == 1, stale.stdout
```

- [ ] **Step 2: Run the resolver group and confirm it fails on the missing tool**

Run: `python -m pytest evals/multi-model-verify/test_artifact_roots.py -q -k "resolver or override or docsroot or reporoot or missing or assert"`
Expected: every test FAILS (PowerShell reports the script path does not exist; returncode is not 0).

- [ ] **Step 3: Write the tool**

Create `tools/artifact-roots.ps1`:

```powershell
# artifact-roots.ps1 - resolve every path a multi-model-verify round writes
# into a consumer repository, from the ONE declaration in
# skills/multi-model-verify/references/model-prompting-notes.md.
#
# Item 100 (2026-09-12): rounds, ledgers and mirrors landed in three roots
# per consumer repo because each writer read the repo-side override on
# its own. This tool is the only reader. It prints the resolved set for
# the debate record, and -Assert answers whether one path lies inside a
# retained in-repo root before a retention copy runs.
#
# The declaration is PARSED here, never remembered: a missing or doubled
# line is an error, not a default.
#
# Windows PowerShell 5.1 and PowerShell 7, ASCII ONLY.
#
# Exit codes: 0 resolved (or -Assert inside), 1 -Assert outside,
# 2 parameter fault, unreadable declaration, or -RepoRoot not a git
# working tree. The map mirrors dispatch-round.ps1.
param(
    [Parameter(Mandatory = $true)][string]$RepoRoot,
    [string]$DocsRoot = "",
    [string]$Assert = "",
    [switch]$Json
)

$ErrorActionPreference = "Stop"

function Fail($message) {
    Write-Output ("ERROR: " + $message)
    exit 2
}

function Normalize-Slashes($p) {
    return $p.Replace("\", "/").TrimEnd("/")
}

function Resolve-Absolute($p) {
    # Provider-relative, like new-review-mirror.ps1: a relative path
    # resolves against PowerShell's location, not the process cwd.
    $full = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($p)
    return Normalize-Slashes ([System.IO.Path]::GetFullPath($full))
}

# ---- the declaration ---------------------------------------------------
$NotesPath = Join-Path $PSScriptRoot "..\skills\multi-model-verify\references\model-prompting-notes.md"
if (-not (Test-Path -LiteralPath $NotesPath -PathType Leaf)) {
    Fail ("declaration file not found: " + $NotesPath)
}
$notes = [System.IO.File]::ReadAllText($NotesPath, (New-Object System.Text.UTF8Encoding($false)))
$regionMatch = [regex]::Match($notes,
    '<!-- contract:start id=artifact-roots -->(.*?)<!-- contract:end -->',
    [System.Text.RegularExpressions.RegexOptions]::Singleline)
if (-not $regionMatch.Success) {
    Fail ("artifact-roots region not found in " + $NotesPath)
}
$region = $regionMatch.Groups[1].Value

$labels = @(
    @{ Key = "docsRoot";         Label = "Canonical docs root" },
    @{ Key = "docsRootOverride"; Label = "Canonical docs root override" },
    @{ Key = "frozenPlan";       Label = "Canonical frozen plan path" },
    @{ Key = "rounds";           Label = "Canonical rounds root" },
    @{ Key = "sddLedger";        Label = "Canonical SDD ledger root" },
    @{ Key = "reviewMirror";     Label = "Canonical review mirror root" },
    @{ Key = "attestation";      Label = "Canonical attestation root" },
    @{ Key = "checkpoint";       Label = "Canonical checkpoint root" }
)
$declared = @{}
foreach ($l in $labels) {
    $pattern = '(?m)^' + [regex]::Escape($l.Label) + ': `([^`\r\n]+)`[ \t]*\r?$'
    $hits = [regex]::Matches($region, $pattern)
    if ($hits.Count -ne 1) {
        Fail ("declaration line '" + $l.Label + "' found " + $hits.Count +
            " times in the artifact-roots region; expected exactly 1")
    }
    $declared[$l.Key] = $hits[0].Groups[1].Value
}

# ---- the repository ----------------------------------------------------
if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) {
    Fail ("-RepoRoot is not a directory: " + $RepoRoot)
}
# Native git under Continue: a benign stderr line must not become a
# terminating error (CLAUDE.md, the dispatch traps).
$priorEap = $ErrorActionPreference
$ErrorActionPreference = "Continue"
$toplevel = (& git -C $RepoRoot rev-parse --show-toplevel 2>$null | Out-String).Trim()
$topExit = $LASTEXITCODE
$commonDir = (& git -C $RepoRoot rev-parse --git-common-dir 2>$null | Out-String).Trim()
$commonExit = $LASTEXITCODE
$ErrorActionPreference = $priorEap
if (($topExit -ne 0) -or -not $toplevel) {
    Fail ("-RepoRoot is not a git working tree: " + $RepoRoot)
}
if (($commonExit -ne 0) -or -not $commonDir) {
    Fail ("could not resolve the git common dir for " + $RepoRoot)
}
$top = Normalize-Slashes ([System.IO.Path]::GetFullPath($toplevel))
if (-not [System.IO.Path]::IsPathRooted($commonDir)) {
    $commonDir = Join-Path $toplevel $commonDir
}
$common = Normalize-Slashes ([System.IO.Path]::GetFullPath($commonDir))

# ---- the docs root -----------------------------------------------------
if ($PSBoundParameters.ContainsKey("DocsRoot")) {
    $rel = $DocsRoot.Replace("\", "/").Trim("/")
    if (-not $rel) { Fail "-DocsRoot is empty" }
    if ([System.IO.Path]::IsPathRooted($DocsRoot)) {
        Fail ("-DocsRoot must be relative to the repo root: " + $DocsRoot)
    }
    if (@($rel.Split("/")) -contains "..") {
        Fail ("-DocsRoot may not contain a '..' segment: " + $DocsRoot)
    }
    $docsRel = $rel
    $source = "-DocsRoot"
} elseif (Test-Path -LiteralPath (Join-Path $toplevel $declared.docsRootOverride) -PathType Container) {
    $docsRel = $declared.docsRootOverride
    $source = "override directory exists"
} else {
    $docsRel = $declared.docsRoot
    $source = "default"
}

$tempRoot = $env:TEMP
if (-not $tempRoot) { $tempRoot = [System.IO.Path]::GetTempPath() }
$tempRoot = Normalize-Slashes ([System.IO.Path]::GetFullPath($tempRoot))

function Resolve-Row($value) {
    $v = $value.Replace("<docs-root>", $docsRel)
    $v = $v.Replace("<TEMP>", $tempRoot)
    $v = $v.Replace("<git-common-dir>", $common)
    if ([System.IO.Path]::IsPathRooted($v)) { return Normalize-Slashes $v }
    return ($top + "/" + (Normalize-Slashes $v))
}

$resolved = [ordered]@{
    repo         = $top
    docsRoot     = $top + "/" + $docsRel
    source       = $source
    frozenPlan   = Resolve-Row $declared.frozenPlan
    rounds       = Resolve-Row $declared.rounds
    sddLedger    = Resolve-Row $declared.sddLedger
    reviewMirror = Resolve-Row $declared.reviewMirror
    attestation  = Resolve-Row $declared.attestation
    checkpoint   = Resolve-Row $declared.checkpoint
}

# ---- -Assert -----------------------------------------------------------
function Strip-Placeholder($p) {
    # The retained root is the path up to the first per-debate
    # placeholder: ".../plans/<date>-<topic>.md" asserts under ".../plans".
    $i = $p.IndexOf("<")
    $head = if ($i -ge 0) { $p.Substring(0, $i) } else { $p }
    return $head.TrimEnd("/")
}

$assertResult = $null
$exitCode = 0
if ($PSBoundParameters.ContainsKey("Assert")) {
    if (-not $Assert) { Fail "-Assert is empty" }
    $target = Resolve-Absolute $Assert
    $cmp = [System.StringComparison]::OrdinalIgnoreCase
    # Rounds before the plan parent: the rounds root sits under it and
    # the more specific name is the useful answer.
    $retained = @(
        @{ Name = "rounds root";        Root = Strip-Placeholder $resolved.rounds },
        @{ Name = "frozen plan parent"; Root = Strip-Placeholder $resolved.frozenPlan },
        @{ Name = "attestation root";   Root = Strip-Placeholder $resolved.attestation },
        @{ Name = "checkpoint root";    Root = Strip-Placeholder $resolved.checkpoint }
    )
    $inside = $null
    foreach ($r in $retained) {
        if ($target.Equals($r.Root, $cmp) -or $target.StartsWith($r.Root + "/", $cmp)) {
            $inside = $r.Name
            break
        }
    }
    if ($inside) {
        $assertResult = [ordered]@{ path = $target; inside = $true; root = $inside }
        $exitCode = 0
    } else {
        $assertResult = [ordered]@{ path = $target; inside = $false; root = "" }
        $exitCode = 1
    }
}

# ---- output ------------------------------------------------------------
if ($Json) {
    $out = [ordered]@{}
    foreach ($k in $resolved.Keys) { $out[$k] = $resolved[$k] }
    if ($assertResult) { $out["assert"] = $assertResult }
    Write-Output (ConvertTo-Json $out -Depth 3)
} else {
    Write-Output ("repo: " + $resolved.repo)
    Write-Output ("docs-root: " + $resolved.docsRoot)
    Write-Output ("docs-root source: " + $resolved.source)
    Write-Output ("frozen-plan: " + $resolved.frozenPlan)
    Write-Output ("rounds: " + $resolved.rounds)
    Write-Output ("sdd-ledger: " + $resolved.sddLedger)
    Write-Output ("review-mirror: " + $resolved.reviewMirror)
    Write-Output ("attestation: " + $resolved.attestation)
    Write-Output ("checkpoint: " + $resolved.checkpoint)
    if ($assertResult) {
        if ($assertResult.inside) {
            Write-Output ("assert: inside " + $assertResult.root + ": " + $assertResult.path)
        } else {
            Write-Output ("assert: outside every retained root: " + $assertResult.path)
        }
    }
}
exit $exitCode
```

- [ ] **Step 4: Run the resolver group under both hosts**

Run: `$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals/multi-model-verify/test_artifact_roots.py -q`
Expected: all PASS.
Run: `$env:PARALLAX_PS_HOST = "pwsh.exe"; python -m pytest evals/multi-model-verify/test_artifact_roots.py -q`
Expected: all PASS.

- [ ] **Step 5: Confirm the model-literal sweep still passes over the new tool**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q -k "hardcoded or canonical"`
Expected: PASS (the tool carries no `-m` model literal).

- [ ] **Step 6: Commit**

```bash
git add tools/artifact-roots.ps1 evals/multi-model-verify/test_artifact_roots.py
git commit -m "add the artifact roots resolver and its host tests"
```

---

### Task 3: The static sweep, then the skill edits that make it green

**Files:**
- Modify: `evals/multi-model-verify/test_artifact_roots.py` (append the sweep group)
- Modify: `skills/multi-model-verify/SKILL.md` (insert step 4 after preflight item 3; replace mode plan step 5 at lines 320-323)
- Modify: `skills/multi-model-verify/references/frozen-plan-format.md:25-28` and `:84-87`
- Modify: `skills/multi-model-verify/references/preflight-mirror.md:10-15`
- Modify: `skills/multi-model-verify/references/backup-lane.md:664-666`
- Modify: `agents/fable-reviewer.md:18`

**Interfaces:**
- Consumes: the declaration labels from Task 1 and `tools/artifact-roots.ps1` from Task 2.
- Produces: SKILL.md preflight step 4 and the citation form `references/model-prompting-notes.md's artifact-roots declaration` used by every edited reference.

- [ ] **Step 1: Append the sweep test**

Append to `evals/multi-model-verify/test_artifact_roots.py`:

```python
# ---------------------------------------------------------------------
# Group 2: the static sweep
# ---------------------------------------------------------------------
PLUGIN_SURFACE = ("skills/**/*.md", "agents/*.md", "commands/*.md",
                  "hooks/*", "tools/*.ps1")

# A declaration line in the notes is the one place a root may be spelled.
DECLARATION_LINE = re.compile(r"^Canonical [a-zA-Z ]+: `[^`]+`\s*$")

# The shapes are ENUMERATED so the failure names what was searched for.
# A dated citation under the declared rounds root
# (docs/superpowers/plans/rounds/<date>-...) matches none of them; a
# dated ledger citation (.superpowers/sdd/<date>-...) is exempted by the
# lookahead, because one exists in the notes today.
FORBIDDEN_SHAPES = [
    ("a rounds root beside plans/ instead of under it",
     re.compile(r"(?<!plans/)superpowers/rounds/")),
    ("the foreign controller's mirror root",
     re.compile(r"review-sources")),
    ("the override docs root named by hand",
     re.compile(r"dev/docs/superpowers")),
    ("a ledger root that is neither the declaration nor a dated citation",
     re.compile(r"\.superpowers/sdd/(?!\d{4}-\d{2}-\d{2}-)")),
]


def test_no_round_root_is_named_outside_the_declaration():
    offenders = []
    for pattern in PLUGIN_SURFACE:
        for f in sorted(REPO.glob(pattern)):
            if not f.is_file():
                continue
            for lineno, line in enumerate(read(f).splitlines(), 1):
                if f == NOTES and DECLARATION_LINE.match(line):
                    continue
                for label, rx in FORBIDDEN_SHAPES:
                    if rx.search(line):
                        offenders.append(
                            f"{f.relative_to(REPO).as_posix()}:{lineno}: {label}")
    searched = "; ".join(label for label, _ in FORBIDDEN_SHAPES)
    assert not offenders, (
        "a round root is named outside the declaration (searched for: "
        + searched + "):\n" + "\n".join(offenders))


def test_sweep_can_fail(tmp_path):
    # The negative control: the same shapes against a line each of the
    # two KitnEssentials roots would produce.
    hits = [label for label, rx in FORBIDDEN_SHAPES
            if rx.search("see dev/docs/superpowers/rounds/2026-09-02-x/")]
    assert "a rounds root beside plans/ instead of under it" in hits
    assert "the override docs root named by hand" in hits
    hits = [label for label, rx in FORBIDDEN_SHAPES
            if rx.search(".superpowers/review-sources/dt-diag-2766cd59/")]
    assert hits == ["the foreign controller's mirror root"]
    assert not [label for label, rx in FORBIDDEN_SHAPES
                if rx.search("docs/superpowers/plans/rounds/2026-08-03-x/")]
    assert not [label for label, rx in FORBIDDEN_SHAPES
                if rx.search(".superpowers/sdd/2026-08-15-x/progress.md")]
```

- [ ] **Step 2: Run the sweep and confirm it is red on exactly the two hand-named roots**

Run: `python -m pytest evals/multi-model-verify/test_artifact_roots.py -q -k "sweep or named"`
Expected: `test_no_round_root_is_named_outside_the_declaration` FAILS naming exactly `skills/multi-model-verify/SKILL.md:323` and `skills/multi-model-verify/references/frozen-plan-format.md:28`, both `the override docs root named by hand`; `test_sweep_can_fail` PASSES.

- [ ] **Step 3: Edit SKILL.md, exactly these two edits**

Edit A. In `skills/multi-model-verify/SKILL.md`, the preflight list's item 3 ends with the `client-probe-scope-limit` region's `<!-- contract:end -->` line, followed by a blank line and `## Mode plan`. Insert this item between that `<!-- contract:end -->` line and the blank line:

```markdown
4. Run `tools/artifact-roots.ps1 -RepoRoot <repo>`; its artifact-roots
   rule is in references/model-prompting-notes.md.
```

Edit B. Replace these four lines (mode plan step 5):

```markdown
5. Freeze the converged plan per references/frozen-plan-format.md under the
   project's superpowers plans dir (KitnEssentials:
   `dev/docs/superpowers/plans/`; other projects: the superpowers default
   `docs/superpowers/plans/`).
```

with these two:

```markdown
5. Freeze the converged plan per references/frozen-plan-format.md at the
   frozen-plan path preflight step 4 printed.
```

- [ ] **Step 4: Measure SKILL.md against the ceiling**

Run: `python evals/tools/skill_lint.py skills/multi-model-verify --strict`
Expected: `PASS - 0 error(s)`, with the token warning reading roughly 6499 (measured 2026-09-12 on the pre-edit body: 25988 characters; the two edits remove 114 characters and add 122, leaving 25996, four characters under the 26000 ceiling). If it reports an ERROR, STOP: do not trim other text; report the measured count to the user.

- [ ] **Step 5: Edit frozen-plan-format.md**

Replace lines 25-28:

```markdown
defect, found in the debate, not in production. Save location: the
superpowers default
`docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`, unless the project
overrides it (example: KitnEssentials uses `dev/docs/superpowers/plans/`).
```

with:

```markdown
defect, found in the debate, not in production. Save location: the
frozen-plan path that `tools/artifact-roots.ps1` printed in preflight,
resolved from references/model-prompting-notes.md's artifact-roots
declaration (its `Canonical frozen plan path` row, with the repo-side
docs-root override applied by that one tool rather than by hand).
```

Replace lines 84-87:

```markdown
"gone". The canonical retained location is
`docs/superpowers/plans/rounds/<YYYY-MM-DD>-<topic>/` next to the frozen
plans (established by the 2026-07-24 jinn intake) — prefer it over ad-hoc
paths so retention survives scratchpad cleanup by default.
```

with:

```markdown
"gone". The canonical retained location is the rounds root that
`tools/artifact-roots.ps1` printed in preflight (references/model-prompting-notes.md's
artifact-roots declaration, `Canonical rounds root` row, next to the
frozen plans; established by the 2026-07-24 jinn intake) — run the tool
with `-Assert` on the destination before copying, so retention survives
scratchpad cleanup by default and never lands beside the root.
```

- [ ] **Step 6: Edit preflight-mirror.md, backup-lane.md and fable-reviewer.md**

In `skills/multi-model-verify/references/preflight-mirror.md`, replace lines 12-15:

```markdown
Build at a SHORT `<scratch>` directly under the temp directory, such
as a `kerev<n>` folder, never inside the session scratchpad: the
mirror re-roots every path, and the tool refuses before creating
anything when the budget is blown.
```

with:

```markdown
Build at a SHORT `<scratch>` directly under the temp directory, such
as a `kerev<n>` folder, never inside the session scratchpad: the
mirror re-roots every path, and the tool refuses before creating
anything when the budget is blown. That location is the
`Canonical review mirror root` row of references/model-prompting-notes.md's
artifact-roots declaration, fixed there because the tool refuses a
mirror inside the reviewed repository.
```

In `skills/multi-model-verify/references/backup-lane.md`, replace lines 664-666:

```markdown
- Reviews run in a THROWAWAY REVIEW MIRROR — never the real tree. Build
  it at a SHORT path directly under the temp directory, such as a
  `kerev<n>` folder, and never inside the session scratchpad, whose own
```

with:

```markdown
- Reviews run in a THROWAWAY REVIEW MIRROR — never the real tree. Build
  it at a SHORT path directly under the temp directory (the
  `Canonical review mirror root` row of model-prompting-notes.md's
  artifact-roots declaration), such as a
  `kerev<n>` folder, and never inside the session scratchpad, whose own
```

In `agents/fable-reviewer.md`, replace line 18:

```markdown
- The SDD ledger path - its deferred minors are yours to triage.
```

with:

```markdown
- The SDD ledger path (the `Canonical SDD ledger root` row of
  references/model-prompting-notes.md's artifact-roots declaration,
  which the dispatcher resolved) - its deferred minors are yours to
  triage.
```

- [ ] **Step 7: Run the sweep, the pin suites and the linters**

Run: `python -m pytest evals/multi-model-verify/test_artifact_roots.py evals/multi-model-verify/test_multi_model_verify.py evals/multi-model-verify/test_backup_lane.py evals/multi-model-verify/test_seat_reshuffle.py evals/multi-model-verify/test_contract_coverage.py -q`
Expected: all PASS (the sweep is green; no raw-text pin covered the replaced sentences, checked 2026-09-12 by grepping `evals/` for `superpowers plans dir`, `Save location`, `canonical retained location`, `SHORT path directly`, `SDD ledger path`, all absent).
Run: `python evals/tools/skill_lint.py skills/multi-model-verify --strict; python evals/tools/skill_scanner.py skills; python evals/tools/run_trigger_evals.py`
Expected: each exits 0.

- [ ] **Step 8: Commit**

```bash
git add evals/multi-model-verify/test_artifact_roots.py skills/multi-model-verify/SKILL.md skills/multi-model-verify/references/frozen-plan-format.md skills/multi-model-verify/references/preflight-mirror.md skills/multi-model-verify/references/backup-lane.md agents/fable-reviewer.md
git commit -m "point every round-root sentence at the artifact roots declaration and sweep for hand-named roots"
```

---

### Task 4: The real writers, both hosts, in CI

**Files:**
- Modify: `evals/multi-model-verify/test_dispatch_round.py:173-200` (`build_real_mirror` gains `source=None`)
- Modify: `evals/multi-model-verify/test_artifact_roots.py` (append the writer group)
- Modify: `evals/tools/check_workflow_paths.py:61-79` (`REQUIRED_DUAL_HOST_MODULES`)
- Modify: `.github/workflows/skill-evals.yml` (both host steps)

**Interfaces:**
- Consumes: `build_real_mirror(tmp_path, source=None)` returning `RealMirror` with `.path`, `.source`, `.source_head`, `.mirror_head`, `.source_status_sha256`, `.mirror_state_sha256`; `prepare_default(tmp_path, mirror=...)` returning a `subprocess.CompletedProcess`; `run_resolver`, `make_repo`, `git`, `norm` from Task 2.
- Produces: nothing later tasks consume.

- [ ] **Step 1: Extend the mirror fixture**

In `evals/multi-model-verify/test_dispatch_round.py`, replace the head of `build_real_mirror`:

```python
def build_real_mirror(tmp_path):
    """Build a real mirror with the real tool and return its path, its
    source, and its five identity values, read out of the printed
    record."""
    source = tmp_path / "mirror-src"
    source.mkdir()
    git(tmp_path, "init", "-q", str(source))
    (source / "only.txt").write_text("tracked\n")
    git(source, "add", "only.txt")
    git(source, "-c", "user.email=t@t", "-c", "user.name=t",
        "commit", "-q", "-m", "base")

    mirror_path = tmp_path / "real-mirror"
```

with:

```python
def build_real_mirror(tmp_path, source=None):
    """Build a real mirror with the real tool and return its path, its
    source, and its five identity values, read out of the printed
    record. Pass `source` to mirror a repository the caller prepared
    (test_artifact_roots.py needs two commits for the attestation
    emitter); by default a one-commit source is created here, so every
    existing caller is unchanged."""
    if source is None:
        source = tmp_path / "mirror-src"
        source.mkdir()
        git(tmp_path, "init", "-q", str(source))
        (source / "only.txt").write_text("tracked\n")
        git(source, "add", "only.txt")
        git(source, "-c", "user.email=t@t", "-c", "user.name=t",
            "commit", "-q", "-m", "base")

    mirror_path = tmp_path / "real-mirror"
```

- [ ] **Step 2: Confirm the existing dispatch-round suite is unchanged**

Run: `python -m pytest evals/multi-model-verify/test_dispatch_round.py -q -k prepare`
Expected: PASS, same count as before the edit.

- [ ] **Step 3: Append the writer tests**

Append to `evals/multi-model-verify/test_artifact_roots.py`:

```python
# ---------------------------------------------------------------------
# Group 3b: the real writers
# ---------------------------------------------------------------------
def tree_paths(root):
    """Every FILE under root as a repo-relative normalized path, .git
    included. A SET OF PATHS, not contents: the mirror tool's status
    capture rewrites .git/index in place (new-review-mirror.ps1, the
    status capture), so a content diff would fire on a correct tool and
    a path-set diff does not."""
    return {norm(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}


def new_paths(root, before):
    return tree_paths(root) - before


def write_attestation(repo, base, head):
    return subprocess.run(
        [POWERSHELL, "-NoProfile", "-NonInteractive", "-File", str(ATTEST),
         "-RepoRoot", str(repo), "-BaseSha", base, "-HeadSha", head,
         "-Verdict", "PASS", "-VerificationStatus", "FULL",
         "-RouteNote", "effective route confirmed", "-Rounds", "1",
         "-Participants", "t (session) / t (reviewer)"],
        capture_output=True, text=True, timeout=60)


@needs_host
def test_the_real_writers_create_nothing_in_repo_but_the_attestation(tmp_path):
    # The three tools that write during a round, run for real against a
    # disposable two-commit repository. The only path that may appear
    # inside the repository is the attestation, and it must satisfy the
    # resolver's own membership answer.
    from test_dispatch_round import build_real_mirror, prepare_default
    repo = make_repo(tmp_path, name="src", commits=2)
    base = git(repo, "rev-parse", "HEAD~1").strip()
    head = git(repo, "rev-parse", "HEAD").strip()
    before = tree_paths(repo)

    att = write_attestation(repo, base, head)
    assert att.returncode == 0, att.stdout + att.stderr
    mirror = build_real_mirror(tmp_path, source=repo)
    assert norm(mirror.source) == norm(repo)
    prep = prepare_default(tmp_path, mirror=mirror)
    assert prep.returncode == 0, prep.stdout + prep.stderr

    appeared = new_paths(repo, before)
    assert appeared == {f".git/parallax/attestations/{head}.json"}, sorted(appeared)
    for rel in appeared:
        proc = run_resolver("-RepoRoot", str(repo), "-Assert", str(repo / rel))
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert "assert: inside attestation root" in proc.stdout


@needs_host
def test_a_writer_that_strays_is_reported(tmp_path):
    # Negative control for the diff-and-assert logic above: a stub writer
    # that lands a round record beside the plans root is caught by the
    # same path-set diff and refused by the same membership answer.
    repo = make_repo(tmp_path)
    before = tree_paths(repo)
    stray = repo / "rounds" / "x"
    stray.parent.mkdir()
    stray.write_text("a round record in the wrong root\n")
    appeared = new_paths(repo, before)
    assert appeared == {"rounds/x"}, sorted(appeared)
    proc = run_resolver("-RepoRoot", str(repo), "-Assert", str(stray))
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "outside every retained root" in proc.stdout


@needs_host
def test_the_mirror_row_is_enforced_by_the_mirror_tool(tmp_path):
    # The declaration's `Canonical review mirror root` is fixed outside
    # the repository because the tool refuses anything else. The refusal
    # is pinned in test_review_mirror.py; this one cites the row.
    repo = make_repo(tmp_path)
    proc = subprocess.run(
        [POWERSHELL, "-NoProfile", "-NonInteractive", "-File", str(MIRROR_TOOL),
         "-RepoRoot", str(repo), "-MirrorPath", str(repo / "inside" / "mirror"),
         "-SkipProbe"],
        capture_output=True, text=True, timeout=120)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "inside the repo" in proc.stdout
```

- [ ] **Step 4: Run the writer group under both hosts**

Run: `$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals/multi-model-verify/test_artifact_roots.py -q`
Expected: all PASS.
Run: `$env:PARALLAX_PS_HOST = "pwsh.exe"; python -m pytest evals/multi-model-verify/test_artifact_roots.py -q`
Expected: all PASS.

If `test_the_real_writers_create_nothing_in_repo_but_the_attestation` reports an extra path, that path is a FINDING about the tool that wrote it, not a test defect: report it with the tool name and stop, do not widen the expected set.

- [ ] **Step 5: Lock the module into both CI host steps**

In `evals/tools/check_workflow_paths.py`, inside `REQUIRED_DUAL_HOST_MODULES`, after `"evals/multi-model-verify/test_lane_credential_live_support.py",` add:

```python
    # 0.34.0, backlog item 100. The resolver and the writer sweep are
    # PowerShell tools driven by path; a module in the workflow but not
    # in this list is not locked into both hosts.
    "evals/multi-model-verify/test_artifact_roots.py",
```

In `.github/workflows/skill-evals.yml`, in BOTH host steps (the `powershell.exe` step and the `pwsh.exe` step), replace the line

```yaml
          evals/multi-model-verify/test_lane_credential_live_support.py -q
```

with

```yaml
          evals/multi-model-verify/test_lane_credential_live_support.py
          evals/multi-model-verify/test_artifact_roots.py -q
```

- [ ] **Step 6: Run the workflow guard and its tests**

Run: `python evals/tools/check_workflow_paths.py; python -m pytest evals/multi-model-verify/test_backup_lane.py -q -k workflow`
Expected: the guard exits 0 naming both hosts; the tests PASS.

- [ ] **Step 7: Commit**

```bash
git add evals/multi-model-verify/test_dispatch_round.py evals/multi-model-verify/test_artifact_roots.py evals/tools/check_workflow_paths.py .github/workflows/skill-evals.yml
git commit -m "drive the three round writers in a disposable repo under both hosts and lock the module into ci"
```

---

### Task 5: The backlog entry and the full gate

**Files:**
- Modify: `BACKLOG.md:93-116` (item 100)

**Interfaces:**
- Consumes: nothing from code; the `Verified:` digest comes from `backlog_lint.py --digests`.
- Produces: item 100 with closing criteria that match what shipped, still OPEN (the diff debate closes it).

- [ ] **Step 1: Rewrite the closing paragraph in place**

In `BACKLOG.md`, item 100, replace the paragraph beginning `**What closing it means.**`:

```markdown
**What closing it means.** One declaration of every path a round writes
(rounds, SDD ledger, review mirror, attestation), resolved through one
repo-override rule, with the mirror and ledger roots gitignored by the
same entry as the rounds. A preflight step that prints the resolved set,
and an eval that fails when a round writes outside it. The declaration
belongs next to the canonical model declarations in
references/model-prompting-notes.md so a swap edits one file. Migration
of existing repos is the consumer's job (KitnEssentials archives by hand);
the plugin only has to stop adding to the spread.
```

with:

```markdown
**What closing it means.** One declaration of every path a round writes
(frozen plan, rounds, SDD ledger, review mirror, attestation,
checkpoint), resolved through one repo-override rule by one tool, a
preflight step that prints the resolved set, and an eval that fails
when a writer or a skill sentence names a root outside it. The
declaration sits next to the canonical model declarations in
references/model-prompting-notes.md so a swap edits one file.
Amended 2026-09-12, at brainstorming: the ledger and mirror roots are
declared FIXED rather than gitignored beside the rounds. The ledger
root belongs to Superpowers, whose sdd-workspace script hard-codes it
and reads it back; the mirror must sit outside the repository, which
the mirror tool already refuses to violate. The same date's survey also
found that two of the four KitnEssentials roots were not parallax
writers: the bare rounds directory has no source in this repo's
history, and the 54 MB copy was written by a Codex controller session
on 2026-09-07. The plugin binds its own tools and the Claude
controller's prose; a foreign controller is outside the contract.
Migration of existing repos is the consumer's job (KitnEssentials
archives by hand); the plugin only has to stop adding to the spread.
```

- [ ] **Step 2: Re-attest the item's digest**

Run: `python evals/tools/backlog_lint.py --digests BACKLOG.md | Select-String "^100 "`
Expected: one line `100 <12 hex>`. Replace item 100's `Verified:` line with `Verified: 2026-09-12 <that 12 hex>` (the date is the day the edit is made; if that is later than 2026-09-12, use the actual date).

- [ ] **Step 3: Run the backlog linter**

Run: `python evals/tools/backlog_lint.py`
Expected: exit 0, no rule failure for item 100.

- [ ] **Step 4: Run the full gate**

Run, in order:
```powershell
python evals/tools/skill_lint.py skills/multi-model-verify --strict
python evals/tools/skill_scanner.py skills
python evals/tools/check_exact_line_oracles.py
python evals/tools/run_trigger_evals.py
$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals -q
$env:PARALLAX_PS_HOST = "pwsh.exe"; python -m pytest evals -q
python evals/tools/backlog_lint.py
```
Expected: every command exits 0; both pytest runs report 0 failures. Record the pass counts of both host runs in the SDD ledger.

- [ ] **Step 5: Commit**

```bash
git add BACKLOG.md
git commit -m "restate what closes item 100 after the artifact roots survey"
```

---

## Self-review

**Spec coverage.** Declaration and region: Task 1. Resolver, override rule, `-Assert`, exit map: Task 2. SKILL.md step 4 and the step-5 payment, frozen-plan-format, preflight-mirror, backup-lane, fable-reviewer citations: Task 3. Static sweep with enumerated shapes and dated-citation exemptions: Task 3. Behavioural writers, path-set diff, negative control, mirror refusal, fixture extension, own skip mark, `REQUIRED_DUAL_HOST_MODULES`, both workflow steps: Task 4. Backlog rewrite: Task 5. The spec's "Out of scope" list has no task, by design. `commands/doctor.md` is untouched, as the spec says.

**Placeholders.** None. Every code step carries the code; the two "if it fails" notes in Tasks 3 and 4 direct the implementer to stop and report, which is the spec's rule for those two outcomes.

**Type consistency.** `run_resolver(*args, tool=None)`, `make_repo(tmp_path, name, commits)`, `norm`, `git`, `tree_paths`, `new_paths` are defined once in `test_artifact_roots.py` and used with those names in Tasks 2 and 4. `build_real_mirror(tmp_path, source=None)` matches its call `build_real_mirror(tmp_path, source=repo)`. The JSON keys the tool emits (`repo`, `docsRoot`, `source`, `frozenPlan`, `rounds`, `sddLedger`, `reviewMirror`, `attestation`, `checkpoint`, `assert`) match the keys the tests read. The text-line names match the `keys ==` list in `test_resolver_text_output_names_each_root_then_the_source`.
