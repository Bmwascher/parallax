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
        "Canonical review mirror root: `C:/pxm/<short-name>/`\n"
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
    assert "never under the controller host's temp directory" in tail
    assert "-Expect reviewMirror" in tail
    assert "git rev-parse --git-common-dir" in tail


# ---------------------------------------------------------------------
# Group 3a: the resolver
# ---------------------------------------------------------------------
def run_resolver(*args, tool=None, env=None):
    return subprocess.run(
        [POWERSHELL, "-NoProfile", "-NonInteractive", "-File",
         str(tool or TOOL), *args],
        capture_output=True, text=True, timeout=60, env=env)


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
    # The mirror row is FIXED and drive-rooted: the declared parent with
    # the per-debate placeholder appended, nowhere near the repo or TEMP.
    assert norm(got["reviewMirror"]) == "c:/pxm/<short-name>"
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
@pytest.mark.parametrize("args", [
    (),
    ("-RepoRoot", "{repo}", "-Bogus", "x"),
    ("-RepoRoot", "{repo}", "stray"),
    # The forms PowerShell's own binding used to own, each exit 1 with
    # host-specific text and no ERROR: line under a typed param block:
    # a missing value, a duplicate, a value on the switch that 5.1
    # rejected and 7 accepted (measured 2026-09-13 by the diff-debate
    # reviewer), a common parameter, and an abbreviated name.
    ("-RepoRoot",),
    ("-RepoRoot", "{repo}", "-Assert"),
    ("-RepoRoot", "{repo}", "-RepoRoot", "{repo}"),
    ("-RepoRoot", "{repo}", "-Json:invalid"),
    ("-RepoRoot", "{repo}", "-ErrorAction", "invalid"),
    ("-Repo", "{repo}"),
    # An EMPTY inline value: -File preprocessing drops `-Assert:` as the
    # last token and strips the colon from `-Json:` before $args exists,
    # on both hosts, so an intended assertion answered 0 with no
    # assertion line (measured 2026-09-13 by the diff-debate R4
    # reviewer). The parser reads the raw process command line instead.
    ("-RepoRoot", "{repo}", "-Assert:"),
    ("-RepoRoot", "{repo}", "-DocsRoot:"),
    ("-RepoRoot", "{repo}", "-Json:"),
    ("-RepoRoot", "{repo}", "-Assert:", "-Json"),
])
def test_every_command_line_fault_is_a_script_fault(tmp_path, args):
    # The script has no param block and parses the raw process command
    # line: every token reaches its own parser as a string on both
    # hosts, so there is no binding residual. Each case exits 2 with an
    # ERROR: line.
    repo = make_repo(tmp_path)
    proc = run_resolver(*[a.replace("{repo}", str(repo)) for a in args])
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert proc.stdout.startswith("ERROR:"), proc.stdout


@needs_host
def test_raw_command_line_keeps_a_path_with_spaces_whole(tmp_path):
    # The raw command line is split by the host's own rules; a quoted
    # path with spaces must arrive as one token, or the parser would
    # read its second word as a stray argument.
    repo = make_repo(tmp_path, name="repo with space")
    proc = run_resolver("-RepoRoot", str(repo), "-Assert",
                        str(repo / "docs" / "superpowers" / "plans" / "rounds" / "2026-09-13-x" / "r.md"),
                        "-Expect", "rounds")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "assert: inside rounds root" in proc.stdout


@needs_host
@pytest.mark.parametrize("flag,is_json", [
    ("-Json", True),
    ("-Json:$true", True),
    ("-Json:$false", False),
    ("-Json:true", True),
    ("-Json:false", False),
])
def test_json_switch_forms_select_the_format_on_both_hosts(tmp_path, flag, is_json):
    # -File splits `-Json:$true` into two tokens and PowerShell 7
    # evaluates the second to `True` while 5.1 leaves `$true`; the parser
    # accepts both spellings, so the same command line selects the same
    # format on both hosts.
    repo = make_repo(tmp_path)
    proc = run_resolver("-RepoRoot", str(repo), flag)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    if is_json:
        assert json.loads(proc.stdout)["source"] == "default"
    else:
        assert proc.stdout.startswith("repo: "), proc.stdout


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
def test_expect_refuses_a_rounds_copy_aimed_beside_the_rounds_root(tmp_path):
    # The KitnEssentials shape item 100 exists to refuse: a dated
    # directory beside plans/rounds/. The frozen plan parent contains
    # it, so a bare -Assert answers "inside" (see the next test); -Expect
    # names the root the copy is meant for and refuses any other.
    repo = make_repo(tmp_path)
    beside = repo / "docs/superpowers/plans/2026-09-12-x/r1.md"
    proc = run_resolver("-RepoRoot", str(repo), "-Assert", str(beside),
                        "-Expect", "rounds")
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "assert: inside frozen plan parent, expected rounds root" in proc.stdout
    got = json.loads(run_resolver("-RepoRoot", str(repo), "-Assert", str(beside),
                                  "-Expect", "rounds", "-Json").stdout)
    assert got["assert"]["inside"] is False
    assert got["assert"]["root"] == "frozen plan parent"
    assert got["assert"]["expected"] == "rounds root"


@needs_host
def test_assert_without_expect_accepts_the_same_path(tmp_path):
    # Unchanged behaviour, and the reason -Expect exists: without it the
    # frozen plan parent (<docs-root>/plans) accepts every dated
    # directory beside plans/rounds/, so exit 0 here is NOT a clean
    # answer for a rounds retention copy.
    repo = make_repo(tmp_path)
    beside = repo / "docs/superpowers/plans/2026-09-12-x/r1.md"
    proc = run_resolver("-RepoRoot", str(repo), "-Assert", str(beside))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "assert: inside frozen plan parent:" in proc.stdout


@needs_host
def test_expect_accepts_the_expected_root_and_reports_it(tmp_path):
    repo = make_repo(tmp_path)
    under = repo / "docs/superpowers/plans/rounds/2026-09-12-x/r1.md"
    proc = run_resolver("-RepoRoot", str(repo), "-Assert", str(under),
                        "-Expect", "rounds")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "assert: inside rounds root:" in proc.stdout
    got = json.loads(run_resolver("-RepoRoot", str(repo), "-Assert", str(under),
                                  "-Expect", "rounds", "-Json").stdout)
    assert got["assert"]["inside"] is True
    assert got["assert"]["root"] == "rounds root"
    assert got["assert"]["expected"] == "rounds root"


@needs_host
@pytest.mark.parametrize("args", [
    # An unknown value, and a case variant: the values are exact.
    ("-RepoRoot", "{repo}", "-Assert", "{repo}/x", "-Expect", "ledger"),
    ("-RepoRoot", "{repo}", "-Assert", "{repo}/x", "-Expect", "review-mirror"),
    ("-RepoRoot", "{repo}", "-Assert", "{repo}/x", "-Expect", "Rounds"),
    # -Expect without -Assert has nothing to check against.
    ("-RepoRoot", "{repo}", "-Expect", "rounds"),
])
def test_expect_parameter_faults_exit_2(tmp_path, args):
    repo = make_repo(tmp_path)
    proc = run_resolver(*[a.replace("{repo}", str(repo)) for a in args])
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert proc.stdout.startswith("ERROR:"), proc.stdout


@needs_host
def test_docsroot_may_not_be_the_repo_root_itself(tmp_path):
    repo = make_repo(tmp_path)
    proc = run_resolver("-RepoRoot", str(repo), "-DocsRoot", ".")
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert proc.stdout.startswith("ERROR:"), proc.stdout
    assert "may not be the repo root itself" in proc.stdout


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


@needs_host
def test_expect_review_mirror_answers_for_the_declared_parent(tmp_path):
    # The check a session runs BEFORE building a mirror (preflight-mirror.md):
    # the declared parent accepts a direct child and a deeper path, and
    # refuses the two places mirrors used to be built, the host temp
    # directory and the drive root. The paths need not exist.
    repo = make_repo(tmp_path)
    for inside in (r"C:\pxm\kv-t", "C:/pxm/kvs-t", r"C:\pxm\t-1\kv-t"):
        proc = run_resolver("-RepoRoot", str(repo), "-Assert", inside,
                            "-Expect", "reviewMirror")
        assert proc.returncode == 0, inside + ": " + proc.stdout + proc.stderr
        assert "assert: inside review mirror root:" in proc.stdout, proc.stdout
    temp_root = os.environ.get("TEMP") or tmp_path
    for outside in (str(Path(temp_root) / "kv-t"), r"C:\kv-t", r"C:\pxmx\kv-t"):
        proc = run_resolver("-RepoRoot", str(repo), "-Assert", outside,
                            "-Expect", "reviewMirror")
        assert proc.returncode == 1, outside + ": " + proc.stdout + proc.stderr
        assert "outside every retained root" in proc.stdout, proc.stdout
    got = json.loads(run_resolver("-RepoRoot", str(repo), "-Assert", r"C:\pxm\kv-t",
                                  "-Expect", "reviewMirror", "-Json").stdout)
    assert got["assert"] == {"path": "C:/pxm/kv-t", "inside": True,
                             "root": "review mirror root",
                             "expected": "review mirror root"}


@needs_host
def test_a_mirror_path_asserted_for_another_root_is_refused(tmp_path):
    # The mirror row is in the -Assert set, so a rounds retention copy
    # aimed at the mirror parent is refused by name, like one aimed at
    # the frozen plan parent.
    repo = make_repo(tmp_path)
    proc = run_resolver("-RepoRoot", str(repo), "-Assert", r"C:\pxm\kv-t",
                        "-Expect", "rounds")
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "assert: inside review mirror root, expected rounds root" in proc.stdout


# ---------------------------------------------------------------------
# Group 2: the static sweep
# ---------------------------------------------------------------------
PLUGIN_SURFACE = ("skills/**/*.md", "agents/*.md", "commands/*.md",
                  "hooks/**/*", "tools/*.ps1")

# A declaration line in the notes is the one place a root may be spelled,
# and only BETWEEN the round-artifact-roots contract markers: a line
# elsewhere in the file that merely looks like a declaration is swept.
DECLARATION_LINE = re.compile(r"^Canonical [a-zA-Z ]+: `[^`]+`\s*$")
REGION_START = "<!-- contract:start id=round-artifact-roots -->"
REGION_END = "<!-- contract:end -->"


def declaration_line_numbers():
    """1-based line numbers of the declaration lines inside the marked
    region of the notes, read once."""
    lines = read(NOTES).splitlines()
    start = lines.index(REGION_START)
    end = lines.index(REGION_END, start)
    return {n for n in range(start + 2, end + 1)
            if DECLARATION_LINE.match(lines[n - 1])}


# The shapes are ENUMERATED so the failure names what was searched for.
# A dated citation under the declared rounds root
# (docs/superpowers/plans/rounds/<date>-...) matches none of them; a
# dated ledger citation (.superpowers/sdd/<date>-...) is exempted by the
# lookahead, because one exists in the notes today. Every separator is
# `[/\\]` because tools/*.ps1 spell paths with backslashes. The
# lookbehind in the first shape only keeps a citation of a nested
# `plans/rounds/` path from being misread as a root beside plans/; the
# string `plans/superpowers/rounds/` does not occur in the tree.
# STATED LIMITS, the forms these shapes do not catch: a slashless
# spelling (`superpowers rounds`, `dev docs superpowers`), a ledger root
# with no separator after `sdd`, a root assembled from parts at runtime
# (`Join-Path $common "parallax"`), and any spelling on a surface the
# glob list above does not name. The writer test in Group 3b is what
# binds the runtime-assembled rows.
FORBIDDEN_SHAPES = [
    ("a rounds root beside plans/ instead of under it",
     re.compile(r"(?<!plans[/\\])superpowers[/\\]rounds[/\\]")),
    ("the foreign controller's mirror root",
     re.compile(r"review-sources")),
    ("the override docs root named by hand",
     re.compile(r"dev[/\\]docs[/\\]superpowers")),
    ("a ledger root that is neither the declaration nor a dated citation",
     re.compile(r"\.superpowers[/\\]sdd[/\\](?!\d{4}-\d{2}-\d{2}-)")),
    ("an attestation or checkpoint root spelled under .git/ instead of the git common dir",
     re.compile(r"\.git[/\\]parallax[/\\]")),
    ("the default docs root named by hand outside a dated citation",
     re.compile(r"docs[/\\]superpowers(?![/\\](plans[/\\](rounds[/\\])?|specs[/\\])\d{4}-\d{2}-\d{2}-)")),
    ("a common-dir row spelled by placeholder instead of cited",
     re.compile(r"<git-common-dir>[/\\]parallax[/\\]")),
    ("the retired temp-directory mirror root",
     re.compile(r"<TEMP>")),
]


def test_no_round_root_is_named_outside_the_declaration():
    offenders = []
    exempt = declaration_line_numbers()
    assert exempt, "no declaration lines found between the region markers"
    for pattern in PLUGIN_SURFACE:
        for f in sorted(REPO.glob(pattern)):
            if not f.is_file():
                continue
            for lineno, line in enumerate(read(f).splitlines(), 1):
                if f == NOTES and lineno in exempt:
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
    # The sixth shape: the default docs root spelled by hand. A bare
    # rounds directory beside plans/ hits it AND the first shape; a
    # PowerShell backslash spelling hits it; a dated plan or spec
    # citation does not.
    hits = [label for label, rx in FORBIDDEN_SHAPES
            if rx.search("see docs/superpowers/rounds/")]
    assert "the default docs root named by hand outside a dated citation" in hits
    assert "a rounds root beside plans/ instead of under it" in hits
    hits = [label for label, rx in FORBIDDEN_SHAPES
            if rx.search(r"docs\superpowers\plans\x")]
    assert hits == ["the default docs root named by hand outside a dated citation"]
    assert not [label for label, rx in FORBIDDEN_SHAPES
                if rx.search("docs/superpowers/plans/2026-09-12-x.md")]
    assert not [label for label, rx in FORBIDDEN_SHAPES
                if rx.search("docs/superpowers/specs/2026-08-31-x.md")]
    # Backslash spellings of the other shapes, as tools/*.ps1 write them.
    hits = [label for label, rx in FORBIDDEN_SHAPES
            if rx.search(r"$x = '.git\parallax\attestations'")]
    assert hits == ["an attestation or checkpoint root spelled under .git/ instead of the git common dir"]
    hits = [label for label, rx in FORBIDDEN_SHAPES
            if rx.search(r"Join-Path $r '.superpowers\sdd\plan'")]
    assert hits == ["a ledger root that is neither the declaration nor a dated citation"]
    # The seventh shape: a row spelled with its placeholder root, which
    # three files did until 2026-09-13 (application-checkpoint.md and the
    # two attestation tools), found by the diff-debate R1 reviewer.
    hits = [label for label, rx in FORBIDDEN_SHAPES
            if rx.search("<git-common-dir>/parallax/application-checkpoints/<stamp>.md")]
    assert hits == ["a common-dir row spelled by placeholder instead of cited"]
    hits = [label for label, rx in FORBIDDEN_SHAPES
            if rx.search(r"# <git-common-dir>\parallax\attestations\<head-sha>.json")]
    assert hits == ["a common-dir row spelled by placeholder instead of cited"]
    hits = [label for label, rx in FORBIDDEN_SHAPES
            if rx.search("`<git-common-dir>` is what `git rev-parse --git-common-dir` prints")]
    assert hits == []
    # The eighth shape: the mirror row's form until 2026-09-13, when the
    # parent became C:/pxm (backlog item 107); the resolver no longer
    # substitutes it, so a row or a sentence that brings it back names a
    # root nothing resolves.
    hits = [label for label, rx in FORBIDDEN_SHAPES
            if rx.search("Canonical review mirror root: `<TEMP>/<short-name>/`")]
    assert hits == ["the retired temp-directory mirror root"]
    hits = [label for label, rx in FORBIDDEN_SHAPES
            if rx.search(r"$v = $v.Replace(" + '"<TEMP>"' + ", $tempRoot)")]
    assert hits == ["the retired temp-directory mirror root"]
    assert not [label for label, rx in FORBIDDEN_SHAPES
                if rx.search("Canonical review mirror root: `C:/pxm/<short-name>/`")]


def test_declaration_exemption_covers_only_the_marked_region():
    # The exemption is by line number inside the marker pair, so a
    # declaration-shaped line elsewhere in the notes is swept.
    lines = read(NOTES).splitlines()
    exempt = declaration_line_numbers()
    assert len(exempt) == 8, sorted(exempt)
    start = lines.index(REGION_START) + 1
    end = lines.index(REGION_END, start) + 1
    assert all(start < n < end for n in exempt), sorted(exempt)
    assert all(DECLARATION_LINE.match(lines[n - 1]) for n in exempt)


MIRROR_ROW = re.compile(r"^Canonical review mirror root: `([^`<]+)<short-name>/`$", re.M)
PARENT_SPELLING = re.compile(r"[A-Za-z]:[/\\]+pxm(?![A-Za-z0-9_.-])", re.I)


def declared_mirror_parent():
    """The parent the declaration names, normalized: `C:/pxm/<short-name>/`
    gives `c:/pxm`."""
    m = MIRROR_ROW.search(read(NOTES))
    assert m, "the review mirror row is not in the declared shape"
    return norm(m.group(1))


def test_every_parent_spelling_on_the_surface_is_the_declared_one():
    # Prose and the doctor NAME the parent as an example (`C:\pxm\kv-<tag>`).
    # An example is not a second declaration only while it agrees with
    # the row: every drive-rooted `pxm` spelling on the plugin surface is
    # the declared parent, so a renamed row turns each stale example red.
    parent = declared_mirror_parent()
    assert parent == "c:/pxm", parent
    seen = 0
    for pattern in PLUGIN_SURFACE:
        for f in sorted(REPO.glob(pattern)):
            if not f.is_file():
                continue
            for lineno, line in enumerate(read(f).splitlines(), 1):
                for m in PARENT_SPELLING.finditer(line):
                    seen += 1
                    assert re.sub(r"[/\\]+", "/", m.group(0)).lower() == parent, (
                        f"{f.relative_to(REPO).as_posix()}:{lineno} names "
                        f"{m.group(0)}, not the declared parent")
    assert seen >= 4, "the notes, the prose examples and the doctor should name the parent"


def test_parent_spelling_regex_can_fail():
    assert PARENT_SPELLING.search(r"build at C:\pxm\kv-<tag>")
    assert PARENT_SPELLING.search("C:/pxm/<short-name>/")
    assert not PARENT_SPELLING.search(r"C:\pxmx\kv-t")
    assert not PARENT_SPELLING.search("the pxm parent")
    assert norm(PARENT_SPELLING.search(r"D:\PXM\x").group(0)) == "d:/pxm"
    assert not PARENT_SPELLING.search(r"C:\pxm.old")
    assert PARENT_SPELLING.search(r"C:\\pxm\\x")


# ---------------------------------------------------------------------
# Group 3b: the real writers
# ---------------------------------------------------------------------
def tree_paths(root):
    """Every file AND directory under root as a repo-relative normalized
    path, .git included. A SET OF PATHS, not contents: the mirror tool's
    status capture rewrites .git/index in place (new-review-mirror.ps1,
    the status capture), so a content diff would fire on a correct tool
    and a path-set diff does not. Directories are included so an empty
    directory a writer creates is observed. Stated limit: a path created
    and deleted again between the two snapshots is not observed, and the
    Flash implementer's transient brief (agents/flash-implementer.md) is
    a real example of that shape; this test samples endpoints."""
    return {norm(p.relative_to(root)) for p in root.rglob("*")}


def new_paths(root, before):
    return tree_paths(root) - before


def write_attestation(repo, base, head, checkpoint=None):
    args = [POWERSHELL, "-NoProfile", "-NonInteractive", "-File", str(ATTEST),
            "-RepoRoot", str(repo), "-BaseSha", base, "-HeadSha", head,
            "-Verdict", "PASS", "-VerificationStatus", "FULL",
            "-RouteNote", "effective route confirmed", "-Rounds", "1",
            "-Participants", "t (session) / t (reviewer)"]
    if checkpoint is not None:
        args += ["-CheckpointFile", str(checkpoint)]
    return subprocess.run(args, capture_output=True, text=True, timeout=60)


def run_the_real_writers(tmp_path, checkpoint):
    """The three tools that write during a round, run for real against a
    disposable two-commit repository: the attestation emitter (with
    -CheckpointFile when `checkpoint` is set), the review mirror tool and
    dispatch-round.ps1 -Prepare. Returns (repo, head, before, appeared).
    The snapshot is taken after the checkpoint file exists, so the
    appeared set is what the three writers created."""
    from test_dispatch_round import build_real_mirror, prepare_default
    repo = make_repo(tmp_path, name="src", commits=2)
    base = git(repo, "rev-parse", "HEAD~1").strip()
    head = git(repo, "rev-parse", "HEAD").strip()
    cp = None
    if checkpoint:
        # The checkpoint file at its canonical location (the same shape
        # as test_attestation.py's TestCheckpointBinding.make_checkpoint;
        # the emitter refuses any other location and hashes it there),
        # which creates `.git/parallax` and the checkpoint dir on the way
        # down, BEFORE the snapshot.
        cp_dir = repo / ".git" / "parallax" / "application-checkpoints"
        cp_dir.mkdir(parents=True)
        cp = cp_dir / "checkpoint.md"
        cp.write_text("# Application checkpoint\nfile1.txt | x present | F1\n",
                      encoding="utf-8")
    before = tree_paths(repo)

    att = write_attestation(repo, base, head, checkpoint=cp)
    assert att.returncode == 0, att.stdout + att.stderr
    mirror = build_real_mirror(tmp_path, source=repo)
    assert norm(mirror.source) == norm(repo)
    prep = prepare_default(tmp_path, mirror=mirror)
    assert prep.returncode == 0, prep.stdout + prep.stderr
    return repo, head, cp, before, new_paths(repo, before)


def assert_attestation_paths_are_inside(repo, head, before, appeared):
    # The attestation root and the file under it are inside the retained
    # set. `.git/parallax` is the parent SHARED by the attestation and
    # checkpoint rows; it is not itself a declared root, so -Assert
    # refuses it, and the exact-set assertion in the caller is what
    # bounds it.
    for rel in (".git/parallax/attestations",
                f".git/parallax/attestations/{head}.json"):
        proc = run_resolver("-RepoRoot", str(repo), "-Assert", str(repo / rel),
                            "-Expect", "attestation")
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert "assert: inside attestation root" in proc.stdout
    proc = run_resolver("-RepoRoot", str(repo), "-Assert", str(repo / ".git" / "parallax"))
    assert proc.returncode == 1, proc.stdout + proc.stderr
    # Second snapshot AFTER the resolver calls: the resolver is a reader,
    # and this puts it inside the window it polices.
    assert new_paths(repo, before) == appeared, sorted(new_paths(repo, before))


@needs_host
def test_the_real_writers_create_nothing_in_repo_but_the_attestation(tmp_path):
    # The fresh case the plan's Task 4 specifies: nothing under
    # `.git/parallax` exists before the round, so the appeared set is the
    # attestation file and the TWO directories the emitter creates for it
    # (write-attestation.ps1: New-Item -Force on the attestation dir), and
    # nothing else. The only path that may appear inside the repository
    # is the attestation, and it must satisfy the resolver's own
    # membership answer.
    repo, head, _, before, appeared = run_the_real_writers(tmp_path, checkpoint=False)
    assert appeared == {
        ".git/parallax",
        ".git/parallax/attestations",
        f".git/parallax/attestations/{head}.json",
    }, sorted(appeared)
    assert_attestation_paths_are_inside(repo, head, before, appeared)


@needs_host
def test_the_checkpoint_bound_emitter_stays_inside_the_declared_rows(tmp_path):
    # The checkpoint-bound case, which is what binds the two common-dir
    # rows to the declaration: the emitter computes the attestation and
    # checkpoint locations for itself from `git rev-parse
    # --git-common-dir`, and the resolver's answer for each is checked
    # here with -Expect. `.git/parallax` pre-exists (the checkpoint was
    # written before the snapshot), so the appeared set is the
    # attestation dir and file only.
    repo, head, cp, before, appeared = run_the_real_writers(tmp_path, checkpoint=True)
    assert appeared == {
        ".git/parallax/attestations",
        f".git/parallax/attestations/{head}.json",
    }, sorted(appeared)
    # The checkpoint the emitter hashed sits inside the checkpoint row.
    proc = run_resolver("-RepoRoot", str(repo), "-Assert", str(cp),
                        "-Expect", "checkpoint")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "assert: inside checkpoint root" in proc.stdout
    assert_attestation_paths_are_inside(repo, head, before, appeared)


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
    assert appeared == {"rounds", "rounds/x"}, sorted(appeared)
    proc = run_resolver("-RepoRoot", str(repo), "-Assert", str(stray))
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "outside every retained root" in proc.stdout


@needs_host
def test_an_empty_directory_a_writer_creates_is_reported(tmp_path):
    # A writer that only mkdirs an undeclared root leaves no file for a
    # file-only snapshot to see; the snapshot includes directories so
    # this is observed too.
    repo = make_repo(tmp_path)
    before = tree_paths(repo)
    (repo / ".superpowers" / "review-sources").mkdir(parents=True)
    appeared = new_paths(repo, before)
    assert appeared == {".superpowers", ".superpowers/review-sources"}, sorted(appeared)
    proc = run_resolver("-RepoRoot", str(repo), "-Assert",
                        str(repo / ".superpowers" / "review-sources"))
    assert proc.returncode == 1, proc.stdout + proc.stderr


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
