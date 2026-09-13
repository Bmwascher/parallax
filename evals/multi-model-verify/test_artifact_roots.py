"""Contract pins and behavioural checks for the round-artifact-roots declaration
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
        "<!-- contract:start id=round-artifact-roots -->\n"
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
        "contract:start id=round-artifact-roots")


def test_fixed_rows_state_their_reason_outside_the_region():
    notes = read(NOTES)
    tail = notes[notes.index("contract:start id=round-artifact-roots"):]
    assert "Superpowers owns it" in tail
    assert "never inside the reviewed repository" in tail
    assert "git rev-parse --git-common-dir" in tail


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
def test_docsroot_with_a_dot_segment_prints_the_canonical_spelling(tmp_path):
    repo = make_repo(tmp_path)
    got = resolved(repo, "-DocsRoot", "./other/root")
    assert norm(got["docsRoot"]) == norm(repo / "other/root")
    proc = run_resolver("-RepoRoot", str(repo), "-DocsRoot", "./other/root",
                        "-Assert", str(repo / "other/root/plans/rounds/2026-09-12-x/r1.md"))
    assert proc.returncode == 0, proc.stdout + proc.stderr


@needs_host
def test_reporoot_may_be_a_subdirectory_of_the_working_tree(tmp_path):
    # `git rev-parse --git-common-dir` prints a path relative to the
    # directory git ran in (`../.git` from a subdirectory); the resolver
    # must join it there, as the attestation emitter does.
    repo = make_repo(tmp_path)
    sub = repo / "skills"
    sub.mkdir()
    got = resolved(sub)
    assert norm(got["repo"]) == norm(repo)
    assert norm(got["attestation"]) == norm(repo / ".git/parallax/attestations")
    assert norm(got["rounds"]) == norm(
        repo / "docs/superpowers/plans/rounds/<date>-<topic>")


@needs_host
def test_relative_reporoot_resolves_against_powershells_location(tmp_path):
    # The process cwd is tmp_path; PowerShell's location is the repo.
    # PowerShell starts git in its own location, so git answers for the
    # repo; the RELATIVE common-dir answer then reaches .NET GetFullPath,
    # which resolves against the process cwd, so an unresolved `.` prints
    # tmp_path/.git/... Same shape as test_review_mirror.py's
    # provider-path case.
    repo = make_repo(tmp_path)
    script = (
        f"Set-Location -LiteralPath '{repo.as_posix()}'; "
        f"& '{TOOL.as_posix()}' -RepoRoot . -Json; "
        "exit $LASTEXITCODE"
    )
    proc = subprocess.run(
        [POWERSHELL, "-NoProfile", "-NonInteractive", "-Command", script],
        capture_output=True, text=True, cwd=str(tmp_path), timeout=60)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    got = json.loads(proc.stdout)
    assert norm(got["repo"]) == norm(repo)
    assert norm(got["attestation"]) == norm(repo / ".git/parallax/attestations")


@needs_host
@pytest.mark.parametrize("bad", ["../x", "a/../b", "C:/abs/root", "/rooted"])
def test_docsroot_refuses_escapes_and_rooted_values(tmp_path, bad):
    repo = make_repo(tmp_path)
    proc = run_resolver("-RepoRoot", str(repo), "-DocsRoot", bad)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert proc.stdout.startswith("ERROR:"), proc.stdout


@needs_host
@pytest.mark.parametrize("args", [
    ("-RepoRoot", "NoSuchArtifactDrive:/repo"),
    ("-RepoRoot", "{repo}", "-Assert", "NoSuchArtifactDrive:/x"),
    ("-RepoRoot", "{repo}", "-DocsRoot", "bad|root"),
    ("-RepoRoot", "{repo}", "-DocsRoot", "bad<root"),
    ("-RepoRoot", "{repo}", "-Assert", "bad|x"),
    ("-RepoRoot", "{repo}", "-Assert", "{repo}/docs/superpowers/plans/rounds/<date>-<topic>/r1.md"),
])
def test_unresolvable_paths_are_parameter_faults_not_throws(tmp_path, args):
    # The exit contract: 2 for a parameter fault, with an ERROR: line.
    # An unknown drive makes the provider throw; a forbidden character
    # makes IsPathRooted throw on 5.1 and print garbage on 7. Both are
    # routed through Fail (measured 2026-09-12 by the R3 reviewer).
    repo = make_repo(tmp_path)
    proc = run_resolver(*[a.replace("{repo}", str(repo)) for a in args])
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
    ("an attestation or checkpoint root spelled under .git/ instead of the git common dir",
     re.compile(r"\.git/parallax/")),
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
    hits = [label for label, rx in FORBIDDEN_SHAPES
            if rx.search("the ledger at .superpowers/sdd/plan/progress.md")]
    assert hits == ["a ledger root that is neither the declaration nor a dated citation"]
    hits = [label for label, rx in FORBIDDEN_SHAPES
            if rx.search("It writes `.git/parallax/attestations/<head-sha>.json`")]
    assert hits == ["an attestation or checkpoint root spelled under .git/ instead of the git common dir"]

