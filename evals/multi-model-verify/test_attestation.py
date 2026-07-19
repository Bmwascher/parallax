"""Tests for tools/write-attestation.ps1 + tools/verify-attestation.ps1.

The attestation lane records a multi-model-verify diff-mode TERMINAL
verdict, SHA-bound, under the reviewed repo's git common dir; the verifier
is what the pre-push hooks call (non-blocking v1). Rules under test are the
session-adjudicated set from the 2026-07-19 Sol consult: direct match,
merge parent match, and the rejections - moved base, squash, non-PASS
verdict, tampered or misfiled records.

Runs wherever a PowerShell host exists: Windows powershell.exe or pwsh
(GitHub ubuntu runners ship pwsh); skipped otherwise.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
PLUGIN_ROOT = HERE.parent.parent
WRITE = PLUGIN_ROOT / "tools" / "write-attestation.ps1"
VERIFY = PLUGIN_ROOT / "tools" / "verify-attestation.ps1"

POWERSHELL = shutil.which("powershell") or shutil.which("pwsh")

pytestmark = pytest.mark.skipif(
    POWERSHELL is None, reason="no PowerShell host on PATH")


def run_ps(script, *args):
    return subprocess.run(
        [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-File", str(script), *args],
        capture_output=True, text=True, timeout=120)


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo),
                    "-c", "user.name=att-test",
                    "-c", "user.email=t@localhost", *args],
                   check=True, capture_output=True)


def rev(repo, ref="HEAD"):
    out = subprocess.run(["git", "-C", str(repo), "rev-parse", ref],
                         check=True, capture_output=True, text=True)
    return out.stdout.strip()


def make_repo(tmp_path, name="repo"):
    repo = tmp_path / name
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True,
                   capture_output=True)
    git(repo, "commit", "--allow-empty", "-q", "-m", "base")
    return repo


def feature_head(repo, base, branch="feat", filename="f.txt"):
    git(repo, "checkout", "-q", "-b", branch, base)
    (repo / filename).write_text("x\n", encoding="utf-8")
    git(repo, "add", filename)
    git(repo, "commit", "-q", "-m", branch)
    return rev(repo)


def attest(repo, base, head, verdict="PASS"):
    return run_ps(WRITE, "-RepoRoot", str(repo), "-BaseSha", base,
                  "-HeadSha", head, "-Verdict", verdict, "-Rounds", "1",
                  "-Participants", "session/reviewer")


def verify(repo, sha):
    return run_ps(VERIFY, "-RepoRoot", str(repo), "-LocalSha", sha)


def att_file(repo, sha):
    return repo / ".git" / "parallax" / "attestations" / f"{sha}.json"


class TestAttestationLane:
    def test_direct_and_merge_attested(self, tmp_path):
        repo = make_repo(tmp_path)
        base = rev(repo)
        head = feature_head(repo, base)
        emitted = attest(repo, base, head)
        assert emitted.returncode == 0, emitted.stdout + emitted.stderr
        assert "attestation written" in emitted.stdout
        assert att_file(repo, head).is_file()
        v = verify(repo, head)
        assert v.returncode == 0 and "direct" in v.stdout
        # Merge with parent1 == attested base, parent2 == attested head.
        git(repo, "checkout", "-q", "-b", "trunk", base)
        git(repo, "merge", "-q", "--no-ff", "feat", "-m", "merge")
        v = verify(repo, rev(repo))
        assert v.returncode == 0 and "merge" in v.stdout

    def test_moved_base_forces_rereview(self, tmp_path):
        repo = make_repo(tmp_path)
        base = rev(repo)
        head = feature_head(repo, base)
        assert attest(repo, base, head).returncode == 0
        git(repo, "checkout", "-q", "-b", "trunk", base)
        # Main moves after the review: parent1 no longer equals the
        # attested base, so the merge must NOT count as attested.
        git(repo, "commit", "--allow-empty", "-q", "-m", "drift-on-main")
        git(repo, "merge", "-q", "--no-ff", "feat", "-m", "merge")
        v = verify(repo, rev(repo))
        assert v.returncode == 1 and "re-review" in v.stdout

    def test_squash_is_a_new_unattested_sha(self, tmp_path):
        repo = make_repo(tmp_path)
        base = rev(repo)
        head = feature_head(repo, base)
        assert attest(repo, base, head).returncode == 0
        git(repo, "checkout", "-q", "-b", "trunk", base)
        git(repo, "merge", "--squash", "-q", "feat")
        git(repo, "commit", "-q", "-m", "squashed")
        v = verify(repo, rev(repo))
        assert v.returncode == 1 and "no attestation" in v.stdout

    def test_non_pass_verdict_rejected(self, tmp_path):
        repo = make_repo(tmp_path)
        base = rev(repo)
        head = feature_head(repo, base)
        assert attest(repo, base, head, verdict="FIX").returncode == 0
        v = verify(repo, head)
        assert v.returncode == 1 and "not PASS" in v.stdout

    def test_misfiled_record_rejected(self, tmp_path):
        # A record whose head_sha does not match its own filename is stale
        # or hand-moved - never a pass, even with verdict PASS inside.
        repo = make_repo(tmp_path)
        base = rev(repo)
        head = feature_head(repo, base)
        assert attest(repo, base, head).returncode == 0
        misfiled = att_file(repo, base)
        misfiled.write_text(att_file(repo, head).read_text(encoding="utf-8"),
                            encoding="utf-8")
        v = verify(repo, base)
        assert v.returncode == 1

    def test_wrong_repo_name_rejected(self, tmp_path):
        repo = make_repo(tmp_path)
        base = rev(repo)
        head = feature_head(repo, base)
        assert attest(repo, base, head).returncode == 0
        record = json.loads(att_file(repo, head).read_text(encoding="utf-8"))
        record["repo"] = "some-other-repo"
        att_file(repo, head).write_text(json.dumps(record), encoding="utf-8")
        v = verify(repo, head)
        assert v.returncode == 1

    def test_emitter_rejects_empty_range(self, tmp_path):
        repo = make_repo(tmp_path)
        base = rev(repo)
        p = attest(repo, base, base)
        assert p.returncode == 2 and "nothing was reviewed" in p.stdout

    def test_no_attestations_dir_is_not_attested(self, tmp_path):
        repo = make_repo(tmp_path)
        v = verify(repo, rev(repo))
        assert v.returncode == 1 and "no attestations" in v.stdout
