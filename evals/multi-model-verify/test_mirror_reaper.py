"""The review mirror reaper (BACKLOG items 106 and 98; spec
docs/superpowers/specs/2026-09-13-mirror-reaper-design.md).

Four groups. REMOVAL: tools/review-tree-removal.ps1's Remove-ReviewTree,
driven through a harness that dot-sources it, removes a tree with
read-only files and a junction whose target survives, and reports a
named failure on a held handle, a missing path and a link. EMITTER:
tools/write-attestation.ps1's reap parameters refuse every wrong tree
before writing the record and remove the right ones after. MIRROR: the
mirror tool's rebuild removal goes through the same function and its
existing-path refusal names the reap route. PROSE: the skill, the
reference and the doctor carry the rule.

WINDOWS ONLY: junctions and the held-handle sharing rule are Windows
semantics, and the mirror tool is a Windows tool. The powershell-hosts
CI job runs this module under BOTH powershell.exe and pwsh.exe; a green
run on one host proves ONE interpreter.
"""
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
REMOVAL = REPO / "tools" / "review-tree-removal.ps1"
WRITE = REPO / "tools" / "write-attestation.ps1"
MIRROR_TOOL = REPO / "tools" / "new-review-mirror.ps1"
SKILL = REPO / "skills" / "multi-model-verify" / "SKILL.md"
PREFLIGHT = REPO / "skills" / "multi-model-verify" / "references" / "preflight-mirror.md"
DOCTOR = REPO / "commands" / "doctor.md"

POWERSHELL = (os.environ.get("PARALLAX_PS_HOST")
              or shutil.which("powershell") or shutil.which("pwsh"))

pytestmark = pytest.mark.skipif(
    os.name != "nt" or POWERSHELL is None,
    reason="the reaper removes junction-bearing trees under a Windows "
           "PowerShell host")


def run_ps(script, *args):
    return subprocess.run(
        [POWERSHELL, "-NoProfile", "-NonInteractive", "-ExecutionPolicy",
         "Bypass", "-File", str(script), *args],
        capture_output=True, text=True, timeout=180)


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=reap-test",
         "-c", "user.email=t@localhost", *args],
        check=True, capture_output=True, text=True).stdout.strip()


def make_repo(tmp_path, name="repo"):
    """A repo with a base commit and a feature commit, returned with both
    SHAs, because an attestation needs a real base..head range."""
    repo = tmp_path / name
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo,
                   check=True, capture_output=True)
    (repo / "a.txt").write_text("a\n", encoding="utf-8")
    git(repo, "add", "a.txt")
    git(repo, "commit", "-q", "-m", "base")
    base = git(repo, "rev-parse", "HEAD")
    git(repo, "checkout", "-q", "-b", "feat")
    (repo / "b.txt").write_text("b\n", encoding="utf-8")
    git(repo, "add", "b.txt")
    git(repo, "commit", "-q", "-m", "feat")
    head = git(repo, "rev-parse", "HEAD")
    return repo, base, head


def make_mirror(repo, path):
    """A mirror the way the mirror tool makes one: a FILE COPY that keeps
    .git, so it carries git's read-only object files."""
    shutil.copytree(repo, path)
    return path


def make_bridge(repo, path, branch="feat"):
    """A clone bridge the way a KitnEssentials session makes one, checked
    out after a --no-checkout clone."""
    subprocess.run(["git", "clone", "-q", "--no-checkout", str(repo), str(path)],
                   check=True, capture_output=True)
    git(path, "checkout", "-q", branch)
    return path


def junction(link, target):
    subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)],
                   check=True, capture_output=True)


def read(path):
    assert path.is_file(), f"missing file: {path}"
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------
# Group 1: Remove-ReviewTree through a dot-sourcing harness
# ---------------------------------------------------------------------
HARNESS = (
    'param([string]$Target)\n'
    '. "{removal}"\n'
    '$r = Remove-ReviewTree $Target\n'
    'if ($r.Ok) {{ Write-Output "OK" ; exit 0 }}\n'
    'Write-Output ("FAIL: " + $r.Reason)\n'
    'exit 1\n'
)


def harness(tmp_path):
    h = tmp_path / "harness.ps1"
    h.write_text(HARNESS.format(removal=str(REMOVAL).replace("\\", "/")),
                 encoding="ascii")
    return h


def test_removal_file_is_ascii_and_defines_nothing_but_functions():
    raw = REMOVAL.read_bytes()
    raw.decode("ascii")
    body = raw.decode("ascii")
    assert "function Test-PathOrAncestorIsLink(" in body
    assert "function Remove-ReviewTree(" in body
    # No top-level statement: every non-blank, non-comment line outside
    # a function is a brace or a declaration. A dot-sourced file that
    # RUNS something would run it inside both callers.
    assert "param(" not in body
    assert "Remove-Item -Recurse" not in body and "-Recurse" not in body, (
        "the removal is explicit post-order, never Remove-Item -Recurse")


def test_removes_a_tree_with_read_only_files_and_keeps_a_junction_target(tmp_path):
    repo, base, head = make_repo(tmp_path)
    tree = make_mirror(repo, tmp_path / "tree")
    target = tmp_path / "target"
    target.mkdir()
    (target / "keep.txt").write_text("kept\n", encoding="utf-8")
    junction(tree / "linked", target)
    assert (tree / "linked" / "keep.txt").is_file()
    objects = list((tree / ".git" / "objects").rglob("*"))
    assert any(p.is_file() and not os.access(p, os.W_OK) for p in objects), (
        "the fixture must carry a read-only git object")
    proc = run_ps(harness(tmp_path), "-Target", str(tree))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert proc.stdout.strip() == "OK"
    assert not tree.exists()
    assert (target / "keep.txt").read_text(encoding="utf-8") == "kept\n", (
        "the junction's target must survive the removal")


def test_a_held_handle_fails_by_name_and_leaves_the_tree(tmp_path):
    repo, base, head = make_repo(tmp_path)
    tree = make_mirror(repo, tmp_path / "tree")
    held = tree / "held.txt"
    held.write_text("open\n", encoding="utf-8")
    with open(held, "r", encoding="utf-8"):
        proc = run_ps(harness(tmp_path), "-Target", str(tree))
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert proc.stdout.startswith("FAIL: "), proc.stdout
    assert str(held) in proc.stdout, (
        "the failure must name the entry that could not be removed")
    assert held.exists() and tree.exists()


def test_a_missing_path_and_a_file_are_refused(tmp_path):
    proc = run_ps(harness(tmp_path), "-Target", str(tmp_path / "absent"))
    assert proc.returncode == 1 and "does not exist" in proc.stdout, proc.stdout
    f = tmp_path / "plain.txt"
    f.write_text("x\n", encoding="utf-8")
    proc = run_ps(harness(tmp_path), "-Target", str(f))
    assert proc.returncode == 1 and "is a file, not a tree" in proc.stdout
    assert f.exists()


def test_a_link_as_the_root_is_refused_and_its_target_survives(tmp_path):
    target = tmp_path / "target"
    target.mkdir()
    (target / "keep.txt").write_text("kept\n", encoding="utf-8")
    link = tmp_path / "link"
    junction(link, target)
    proc = run_ps(harness(tmp_path), "-Target", str(link))
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "is a link" in proc.stdout, proc.stdout
    assert (target / "keep.txt").is_file()
    assert link.exists(), "a refused removal must not have removed the link either"


def test_a_filesystem_root_is_refused(tmp_path):
    root = os.path.splitdrive(str(tmp_path))[0] + "\\"
    proc = run_ps(harness(tmp_path), "-Target", root)
    assert proc.returncode == 1 and "filesystem root" in proc.stdout, proc.stdout


def test_a_dangling_junction_inside_the_tree_is_removed(tmp_path):
    tree = tmp_path / "tree"
    (tree / "sub").mkdir(parents=True)
    gone = tmp_path / "gone"
    gone.mkdir()
    junction(tree / "sub" / "dangling", gone)
    gone.rmdir()
    proc = run_ps(harness(tmp_path), "-Target", str(tree))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert not tree.exists()


def test_module_is_listed_in_both_host_steps():
    # The powershell-hosts job runs an EXPLICIT module list per host, and
    # test_backup_lane.py records why a module left off it silently
    # tested one interpreter. This module names itself in both.
    workflow = read(REPO / ".github" / "workflows" / "skill-evals.yml")
    rel = "evals/multi-model-verify/test_mirror_reaper.py"
    for host in ("powershell.exe", "pwsh.exe"):
        marker = "PARALLAX_PS_HOST: " + host
        assert marker in workflow
        step = workflow.split(marker, 1)[1].split("\n      - name:", 1)[0]
        assert step.count(rel) == 1, rel + " must appear once in the " + host + " step"


# ---------------------------------------------------------------------
# Group 2: the emitter's reap
# ---------------------------------------------------------------------
def attest(repo, base, head, mirror=None, bridge=None):
    args = [WRITE, "-RepoRoot", str(repo), "-BaseSha", base, "-HeadSha", head,
            "-Verdict", "PASS", "-VerificationStatus", "FULL",
            "-RouteNote", "effective route confirmed", "-Rounds", "1",
            "-Participants", "session/reviewer"]
    if mirror is not None:
        args += ["-ReapMirror", str(mirror)]
    if bridge is not None:
        args += ["-ReapBridge", str(bridge)]
    return run_ps(*args)


def att_file(repo, head):
    return repo / ".git" / "parallax" / "attestations" / (head + ".json")


def test_reaps_mirror_bridge_and_sidecar_after_writing(tmp_path):
    repo, base, head = make_repo(tmp_path)
    bridge = make_bridge(repo, tmp_path / "kvs-t")
    mirror = make_mirror(bridge, tmp_path / "kv-t")
    sidecar = tmp_path / "kv-t.source-manifest"
    sidecar.write_text("advisory\n", encoding="utf-8")
    target = tmp_path / "reference"
    target.mkdir()
    (target / "keep.txt").write_text("kept\n", encoding="utf-8")
    junction(mirror / ".wow-api-reference", target)
    proc = attest(repo, base, head, mirror=mirror, bridge=bridge)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert att_file(repo, head).is_file()
    lines = proc.stdout.splitlines()
    assert lines[0].startswith("attestation written: "), proc.stdout
    assert "reaped mirror: " + str(mirror) in proc.stdout
    assert "reaped sidecar: " + str(sidecar) in proc.stdout
    assert "reaped bridge: " + str(bridge) in proc.stdout
    assert not mirror.exists() and not bridge.exists() and not sidecar.exists()
    assert (target / "keep.txt").is_file(), "the junction target survives"
    assert (repo / "b.txt").is_file(), "the reviewed repo is untouched"


def test_a_remediation_commit_above_the_head_is_still_the_mirror(tmp_path):
    # The mirror tool commits its back-channel removal as parallax@local
    # with the source head as the single parent, so a mirror of a repo
    # with a TRACKED back-channel sits one commit above the attested head.
    repo, base, head = make_repo(tmp_path)
    mirror = make_mirror(repo, tmp_path / "kv-t")
    (mirror / "AGENTS.md").write_text("planted\n", encoding="utf-8")
    git(mirror, "add", "AGENTS.md")
    git(mirror, "commit", "-q", "-m", "planted")
    git(mirror, "rm", "-q", "AGENTS.md")
    subprocess.run(["git", "-C", str(mirror), "-c", "user.email=parallax@local",
                    "-c", "user.name=parallax", "commit", "-q", "-m",
                    "remove instruction back-channels for review"],
                   check=True, capture_output=True)
    # Two commits above head is NOT the remediation shape: refused.
    proc = attest(repo, base, head, mirror=mirror)
    assert proc.returncode == 2 and "not the attested head" in proc.stdout, proc.stdout
    assert not att_file(repo, head).exists(), "a refused argument writes nothing"
    assert mirror.exists()
    # Exactly one parallax@local commit whose parent is the head: accepted.
    mirror2 = make_mirror(repo, tmp_path / "kv-u")
    (mirror2 / "AGENTS.md").write_text("planted\n", encoding="utf-8")
    git(mirror2, "add", "AGENTS.md")
    subprocess.run(["git", "-C", str(mirror2), "-c", "user.email=parallax@local",
                    "-c", "user.name=parallax", "commit", "-q", "-m",
                    "remove instruction back-channels for review"],
                   check=True, capture_output=True)
    proc = attest(repo, base, head, mirror=mirror2)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert not mirror2.exists()


def test_a_bridge_at_a_stale_head_is_refused_by_name(tmp_path):
    repo, base, head = make_repo(tmp_path)
    bridge = make_bridge(repo, tmp_path / "kvs-t")
    (repo / "c.txt").write_text("c\n", encoding="utf-8")
    git(repo, "add", "c.txt")
    git(repo, "commit", "-q", "-m", "fix")
    head2 = git(repo, "rev-parse", "HEAD")
    proc = attest(repo, base, head2, bridge=bridge)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "not the attested head" in proc.stdout and head2 in proc.stdout
    assert bridge.exists() and not att_file(repo, head2).exists()


@pytest.mark.parametrize("shape", ["missing", "file", "inside-repo", "repo-itself",
                                   "contains-repo", "worktree", "no-git", "link"])
def test_every_wrong_tree_is_refused_before_the_record_is_written(tmp_path, shape):
    repo, base, head = make_repo(tmp_path)
    keep = None
    if shape == "missing":
        path = tmp_path / "absent"
    elif shape == "file":
        path = tmp_path / "plain.txt"
        path.write_text("x\n", encoding="utf-8")
    elif shape == "inside-repo":
        path = repo / "nested"
        make_mirror(repo / ".git", path / ".git")
    elif shape == "repo-itself":
        path = repo
    elif shape == "contains-repo":
        path = tmp_path
    elif shape == "worktree":
        path = tmp_path / "wt"
        git(repo, "worktree", "add", "-q", str(path), "main")
        assert (path / ".git").is_file()
    elif shape == "no-git":
        path = tmp_path / "bare"
        path.mkdir()
    else:
        keep = make_mirror(repo, tmp_path / "real")
        path = tmp_path / "link"
        junction(path, keep)
    proc = attest(repo, base, head, mirror=path)
    assert proc.returncode == 2, shape + ": " + proc.stdout + proc.stderr
    assert proc.stdout.startswith("ERROR:"), proc.stdout
    assert not att_file(repo, head).exists(), (
        shape + ": a refused reap path must be refused BEFORE the record is written")
    assert (repo / "b.txt").is_file()
    if shape not in ("missing",):
        assert path.exists(), shape + ": nothing was removed"
    if keep is not None:
        assert (keep / "b.txt").is_file(), "the link's target survives"


def test_a_held_handle_leaves_the_attestation_and_exits_three(tmp_path):
    repo, base, head = make_repo(tmp_path)
    mirror = make_mirror(repo, tmp_path / "kv-t")
    bridge = make_bridge(repo, tmp_path / "kvs-t")
    held = mirror / "held.txt"
    held.write_text("open\n", encoding="utf-8")
    with open(held, "r", encoding="utf-8"):
        proc = attest(repo, base, head, mirror=mirror, bridge=bridge)
    assert proc.returncode == 3, proc.stdout + proc.stderr
    assert att_file(repo, head).is_file(), "the verdict is recorded even when the reap fails"
    assert "ERROR: reap failed for " + str(mirror) in proc.stdout, proc.stdout
    assert str(held) in proc.stdout and "the attestation stands" in proc.stdout
    assert "the bridge was not attempted: " + str(bridge) in proc.stdout, proc.stdout
    assert held.exists()
    assert bridge.exists()


def test_without_the_parameters_the_emitter_removes_nothing(tmp_path):
    repo, base, head = make_repo(tmp_path)
    mirror = make_mirror(repo, tmp_path / "kv-t")
    proc = attest(repo, base, head)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "reaped" not in proc.stdout
    assert mirror.exists()


def test_emitter_header_declares_exit_three():
    body = read(WRITE)
    assert "Exit codes: 0 written, 2 argument/repo error, 3 written but a reap failed" in body


# ---------------------------------------------------------------------
# Group 3: the prose carries the rule
# ---------------------------------------------------------------------
def test_skill_finish_line_passes_the_reap_paths():
    body = read(SKILL)
    assert "[-ReapMirror <mirror>] [-ReapBridge <bridge>]" in body
    assert "the End of life section of references/preflight-mirror.md" in body
    assert body.count("write-attestation.ps1") >= 1


def test_preflight_mirror_reference_states_the_end_of_life_rule():
    body = read(PREFLIGHT)
    assert "## End of life" in body
    for anchor in (
        "The attestation is the reap point",
        "-ReapMirror",
        "-ReapBridge",
        "never an age",
        "HEAD is the attested head",
        "a `.git` FILE",
        "kv-<tag>-2",
    ):
        assert anchor in body, "end-of-life anchor missing: " + anchor


def test_doctor_inventories_the_mirrors_and_never_deletes():
    body = read(DOCTOR)
    assert "## 10. Review mirror inventory" in body
    for anchor in (
        "kv*",
        "$env:TEMP",
        "$env:SystemDrive",
        "5 GB",
        "3 days",
        "LastWriteTime",
        "-ReapMirror",
        "backlog item 106",
    ):
        assert anchor in body, "doctor inventory anchor missing: " + anchor
    section = body.split("## 10. Review mirror inventory", 1)[1]
    assert re.search(r"never delete", section, re.IGNORECASE), (
        "the inventory is observation, not action")
    assert "Remove-Item" not in section


def test_mirror_tool_refusal_and_emitter_agree_on_the_parameter_name():
    # One spelling in the tool that names the route and the tool that
    # implements it; a rename that misses one leaves a refusal pointing
    # at a parameter that does not exist.
    assert "write-attestation.ps1 -ReapMirror" in read(MIRROR_TOOL)
    assert "[string]$ReapMirror" in read(WRITE)
    assert "[string]$ReapBridge" in read(WRITE)


# ---------------------------------------------------------------------
# Group 4: the final-review fix wave (I1, I2, M1, M2)
# ---------------------------------------------------------------------
def test_a_failed_record_write_reaps_nothing(tmp_path):
    repo, base, head = make_repo(tmp_path)
    mirror = make_mirror(repo, tmp_path / "kv-t")
    # A DIRECTORY at the record's path: Set-Content cannot write there,
    # so the write must be refused before anything is reaped.
    att_file(repo, head).mkdir(parents=True)
    proc = attest(repo, base, head, mirror=mirror)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert proc.stdout.startswith("ERROR:"), proc.stdout
    assert "nothing was reaped" in proc.stdout, proc.stdout
    assert mirror.exists()
    assert "attestation written" not in proc.stdout


def test_an_empty_git_directory_does_not_borrow_a_parent_repos_head(tmp_path):
    repo, base, head = make_repo(tmp_path)
    path = tmp_path / "outer"
    make_mirror(repo, path)
    inner = path / "inner"
    (inner / ".git").mkdir(parents=True)
    proc = attest(repo, base, head, mirror=inner)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "no readable HEAD" in proc.stdout, proc.stdout
    assert not att_file(repo, head).exists()
    assert inner.exists() and (path / "b.txt").is_file()


def test_a_read_only_directory_is_removed(tmp_path):
    tree = tmp_path / "tree"
    (tree / "sub").mkdir(parents=True)
    (tree / "sub" / "file.txt").write_text("x\n", encoding="utf-8")
    subprocess.run(["attrib", "+R", str(tree / "sub")], check=True)
    proc = run_ps(harness(tmp_path), "-Target", str(tree))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert not tree.exists()


@pytest.mark.parametrize("shape", ["same", "nested"])
def test_overlapping_mirror_and_bridge_are_refused(tmp_path, shape):
    repo, base, head = make_repo(tmp_path)
    if shape == "same":
        one = make_bridge(repo, tmp_path / "kvs-t")
        mirror = one
        bridge = one
    else:
        mirror = make_mirror(repo, tmp_path / "kv-t")
        bridge = make_bridge(repo, mirror / "kvs-inner")
    proc = attest(repo, base, head, mirror=mirror, bridge=bridge)
    assert proc.returncode == 2, shape + ": " + proc.stdout + proc.stderr
    assert "overlap" in proc.stdout, proc.stdout
    assert not att_file(repo, head).exists()
    assert mirror.exists() and bridge.exists()


# ---------------------------------------------------------------------
# Group 5: pre-round-1 fable fix wave (2026-09-13)
# ---------------------------------------------------------------------
def test_a_sidecar_failure_names_the_unattempted_bridge(tmp_path):
    repo, base, head = make_repo(tmp_path)
    mirror = make_mirror(repo, tmp_path / "kv-t")
    bridge = make_bridge(repo, tmp_path / "kvs-t")
    sidecar = tmp_path / "kv-t.source-manifest"
    sidecar.write_text("advisory\n", encoding="utf-8")
    with open(sidecar, "r", encoding="utf-8"):
        proc = attest(repo, base, head, mirror=mirror, bridge=bridge)
    assert proc.returncode == 3, proc.stdout + proc.stderr
    assert "reap failed for " + str(sidecar) in proc.stdout, proc.stdout
    assert "the bridge was not attempted: " + str(bridge) in proc.stdout, proc.stdout
    assert att_file(repo, head).is_file()
    assert not mirror.exists()
    assert bridge.exists()
    assert sidecar.exists()


def test_a_git_directory_that_is_a_junction_is_refused(tmp_path):
    repo, base, head = make_repo(tmp_path)
    real = make_mirror(repo, tmp_path / "real")
    fake = tmp_path / "fake"
    fake.mkdir()
    (fake / "b.txt").write_text("b\n", encoding="utf-8")
    junction(fake / ".git", real / ".git")
    proc = attest(repo, base, head, mirror=fake)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "directory link" in proc.stdout, proc.stdout
    assert not att_file(repo, head).exists()
    assert fake.exists()
    assert (real / ".git" / "HEAD").is_file()


def test_a_bridge_with_a_remediation_commit_is_refused(tmp_path):
    # The remediation shape (a single parallax@local commit over the
    # attested head) is accepted for the mirror only; a bridge in that
    # same shape is not the attested head and is refused like any other.
    repo, base, head = make_repo(tmp_path)
    bridge = make_bridge(repo, tmp_path / "kvs-t")
    (bridge / "AGENTS.md").write_text("planted\n", encoding="utf-8")
    git(bridge, "add", "AGENTS.md")
    subprocess.run(["git", "-C", str(bridge), "-c", "user.email=parallax@local",
                    "-c", "user.name=parallax", "commit", "-q", "-m",
                    "remove instruction back-channels for review"],
                   check=True, capture_output=True)
    proc = attest(repo, base, head, bridge=bridge)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "not the attested head" in proc.stdout, proc.stdout
    assert not att_file(repo, head).exists()
    assert bridge.exists()


def test_a_read_only_root_is_removed(tmp_path):
    tree = tmp_path / "tree"
    (tree / "sub").mkdir(parents=True)
    (tree / "sub" / "f.txt").write_text("x\n", encoding="utf-8")
    subprocess.run(["attrib", "+R", str(tree)], check=True)
    proc = run_ps(harness(tmp_path), "-Target", str(tree))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert not tree.exists()


def test_a_relative_reap_path_is_refused(tmp_path):
    repo, base, head = make_repo(tmp_path)
    proc = attest(repo, base, head, mirror="kv-relative")
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "absolute path" in proc.stdout, proc.stdout
    assert not att_file(repo, head).exists()


# ---------------------------------------------------------------------
# Group 6: diff debate round 1 (Astra, R1-3a and R1-8)
# ---------------------------------------------------------------------
def test_the_record_lands_in_the_bracketed_repo_and_the_sibling_is_untouched(tmp_path):
    # Set-Content -Path expands wildcard characters, so a repo named
    # `repo[1]` with a matching plain-named sibling `repo1` could have its
    # record land in the sibling while the literal File.Exists read-back
    # accepted whatever old record already sat there. -LiteralPath plus a
    # content read-back closes that.
    repo, base, head = make_repo(tmp_path, name="repo[1]")
    sib = make_mirror(repo, tmp_path / "repo1")
    decoy_dir = sib / ".git" / "parallax" / "attestations"
    decoy_dir.mkdir(parents=True)
    decoy_file = decoy_dir / (head + ".json")
    decoy_bytes = json.dumps({"decoy": True}).encode("utf-8")
    decoy_file.write_bytes(decoy_bytes)
    # A stale record at the literal bracketed path: this is what e9d2713's
    # false-success branch would have accepted unread, since its File.Exists
    # check passed whatever record already sat there.
    att_file(repo, head).parent.mkdir(parents=True, exist_ok=True)
    att_file(repo, head).write_text(json.dumps({"stale": True}), encoding="utf-8")
    mirror = make_mirror(repo, tmp_path / "kv-t")
    proc = attest(repo, base, head, mirror=mirror)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert att_file(repo, head).is_file()
    record = json.loads(att_file(repo, head).read_text(encoding="utf-8"))
    assert record["head_sha"] == head
    assert "decoy" not in record
    assert "stale" not in record
    assert decoy_file.read_bytes() == decoy_bytes
    assert not mirror.exists()


def test_sidecar_success_is_read_back(tmp_path):
    repo, base, head = make_repo(tmp_path)
    mirror = make_mirror(repo, tmp_path / "kv-t")
    sidecar = tmp_path / "kv-t.source-manifest"
    sidecar.write_text("advisory\n", encoding="utf-8")
    proc = attest(repo, base, head, mirror=mirror)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "reaped sidecar: " + str(sidecar) in proc.stdout
    assert not sidecar.exists()
    # Pins that the success line comes AFTER the read-back: the read-back
    # failure text must appear earlier in the source than the print.
    body = read(WRITE)
    assert body.index("still exists after removal") < body.index('"reaped sidecar: "')


def test_the_record_comparison_is_ordinal():
    # A source pin, not a runtime case: the harness cannot make the file on
    # disk differ from the serialized text by case alone (Set-Content writes
    # exactly $json), so the comparison form itself is what has to be locked.
    body = read(WRITE)
    assert body.count(
        "[string]::Equals($writtenText, $json, [System.StringComparison]::Ordinal)"
    ) == 1
    assert "$writtenText -ne $json" not in body
    assert "$writtenText -eq $json" not in body
