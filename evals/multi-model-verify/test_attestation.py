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

import hashlib
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


def attest(repo, base, head, verdict="PASS", status="FULL",
           route="effective route confirmed", checkpoint=None):
    args = [WRITE, "-RepoRoot", str(repo), "-BaseSha", base,
            "-HeadSha", head, "-Verdict", verdict,
            "-VerificationStatus", status, "-RouteNote", route,
            "-Rounds", "1", "-Participants", "session/reviewer"]
    if checkpoint is not None:
        args += ["-CheckpointFile", str(checkpoint)]
    return run_ps(*args)


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
        assert v.returncode == 1 and "FULL, confirmed-route PASS" in v.stdout

    def test_degraded_status_rejected(self, tmp_path):
        # A DEGRADED PASS must never satisfy the gate - the poisoning rule
        # holds mechanically, not just in skill prose.
        repo = make_repo(tmp_path)
        base = rev(repo)
        head = feature_head(repo, base)
        assert attest(repo, base, head, status="DEGRADED").returncode == 0
        v = verify(repo, head)
        assert v.returncode == 1 and "status=DEGRADED" in v.stdout

    def test_unconfirmed_route_rejected(self, tmp_path):
        repo = make_repo(tmp_path)
        base = rev(repo)
        head = feature_head(repo, base)
        assert attest(repo, base, head,
                      route="route-mismatch (header model differed)"
                      ).returncode == 0
        v = verify(repo, head)
        assert v.returncode == 1 and "confirmed-route" in v.stdout

    def test_wrong_mode_rejected(self, tmp_path):
        # Only mode=diff records are gate input; a tampered mode field is
        # a stale/hand-edited record.
        repo = make_repo(tmp_path)
        base = rev(repo)
        head = feature_head(repo, base)
        assert attest(repo, base, head).returncode == 0
        record = json.loads(att_file(repo, head).read_text(encoding="utf-8"))
        record["mode"] = "plan"
        att_file(repo, head).write_text(json.dumps(record), encoding="utf-8")
        v = verify(repo, head)
        assert v.returncode == 1

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


class TestCheckpointBinding:
    """0.7.0: -CheckpointFile binds the application checkpoint's hash and
    the EMITTER-computed changed-path set into the record; the verifier
    re-locates and re-hashes the artifact at its canonical git-common-dir
    location and rejects a record whose binding no longer holds. Binding
    metadata is all-or-none (Sol diff review round 1)."""

    def make_checkpoint(self, repo, name="checkpoint.md"):
        # The canonical location is the contract: the emitter refuses
        # anything else, because the verifier re-hashes it there.
        cp_dir = repo / ".git" / "parallax" / "application-checkpoints"
        cp_dir.mkdir(parents=True, exist_ok=True)
        cp = cp_dir / name
        cp.write_text("# Application checkpoint\nf.txt | x present | F1\n",
                      encoding="utf-8")
        return cp

    def test_checkpoint_recorded_and_verifies(self, tmp_path):
        repo = make_repo(tmp_path)
        base = rev(repo)
        head = feature_head(repo, base)
        cp = self.make_checkpoint(repo)
        emitted = attest(repo, base, head, checkpoint=cp)
        assert emitted.returncode == 0, emitted.stdout + emitted.stderr
        record = json.loads(att_file(repo, head).read_text(encoding="utf-8"))
        assert record["checkpoint_file"] == "checkpoint.md"
        # Hash is of the checkpoint file's bytes, computed by the emitter.
        expected = hashlib.sha256(cp.read_bytes()).hexdigest()
        assert record["checkpoint_hash"] == expected
        # Path set is emitter-computed from base..head, never caller input.
        assert record["changed_paths"] == ["f.txt"]
        v = verify(repo, head)
        assert v.returncode == 0 and "direct" in v.stdout

    def test_emitter_rejects_noncanonical_location(self, tmp_path):
        # An artifact outside the canonical directory is unverifiable
        # (the verifier could never re-locate it) - refuse at emit time.
        repo = make_repo(tmp_path)
        base = rev(repo)
        head = feature_head(repo, base)
        stray = tmp_path / "checkpoint.md"
        stray.write_text("# checkpoint\n", encoding="utf-8")
        p = attest(repo, base, head, checkpoint=stray)
        assert p.returncode == 2 and "must live under" in p.stdout

    def test_tampered_artifact_rejected(self, tmp_path):
        # Modifying the checkpoint after attestation invalidates the
        # record: the verifier re-hashes, it does not trust the field.
        repo = make_repo(tmp_path)
        base = rev(repo)
        head = feature_head(repo, base)
        cp = self.make_checkpoint(repo)
        assert attest(repo, base, head, checkpoint=cp).returncode == 0
        cp.write_text(cp.read_text(encoding="utf-8")
                      + "quietly widened scope\n", encoding="utf-8")
        v = verify(repo, head)
        assert v.returncode == 1 and "hash mismatch" in v.stdout

    def test_deleted_artifact_rejected(self, tmp_path):
        repo = make_repo(tmp_path)
        base = rev(repo)
        head = feature_head(repo, base)
        cp = self.make_checkpoint(repo)
        assert attest(repo, base, head, checkpoint=cp).returncode == 0
        cp.unlink()
        v = verify(repo, head)
        assert v.returncode == 1 and "missing" in v.stdout

    def test_partial_metadata_rejected(self, tmp_path):
        # Deleting changed_paths must not evade the binding: the bound
        # declaration demands all fields, so a partial record is tampered.
        repo = make_repo(tmp_path)
        base = rev(repo)
        head = feature_head(repo, base)
        cp = self.make_checkpoint(repo)
        assert attest(repo, base, head, checkpoint=cp).returncode == 0
        record = json.loads(att_file(repo, head).read_text(encoding="utf-8"))
        del record["changed_paths"]
        att_file(repo, head).write_text(json.dumps(record), encoding="utf-8")
        v = verify(repo, head)
        assert v.returncode == 1 and "binding fields missing" in v.stdout

    def test_legacy_partial_metadata_rejected(self, tmp_path):
        # The schema-1 all-or-none rule still holds for legacy records: a
        # downgraded-to-1 record keeping a partial field set is rejected,
        # not read as unbound.
        repo = make_repo(tmp_path)
        base = rev(repo)
        head = feature_head(repo, base)
        cp = self.make_checkpoint(repo)
        assert attest(repo, base, head, checkpoint=cp).returncode == 0
        record = json.loads(att_file(repo, head).read_text(encoding="utf-8"))
        record["schema"] = 1
        del record["checkpoint_binding"]
        del record["changed_paths"]
        att_file(repo, head).write_text(json.dumps(record), encoding="utf-8")
        v = verify(repo, head)
        assert v.returncode == 1 and "all-or-none" in v.stdout

    def test_separator_in_checkpoint_file_rejected(self, tmp_path):
        # checkpoint_file is a leaf name: a separator would let a record
        # point the re-hash at a file outside the canonical directory.
        repo = make_repo(tmp_path)
        base = rev(repo)
        head = feature_head(repo, base)
        cp = self.make_checkpoint(repo)
        assert attest(repo, base, head, checkpoint=cp).returncode == 0
        record = json.loads(att_file(repo, head).read_text(encoding="utf-8"))
        record["checkpoint_file"] = "../../../evil.md"
        att_file(repo, head).write_text(json.dumps(record), encoding="utf-8")
        v = verify(repo, head)
        assert v.returncode == 1 and "separator" in v.stdout

    def test_tampered_changed_paths_rejected(self, tmp_path):
        repo = make_repo(tmp_path)
        base = rev(repo)
        head = feature_head(repo, base)
        cp = self.make_checkpoint(repo)
        assert attest(repo, base, head, checkpoint=cp).returncode == 0
        record = json.loads(att_file(repo, head).read_text(encoding="utf-8"))
        record["changed_paths"] = ["f.txt", "unreviewed-extra.lua"]
        att_file(repo, head).write_text(json.dumps(record), encoding="utf-8")
        v = verify(repo, head)
        assert v.returncode == 1 and "changed-path set" in v.stdout

    def test_case_only_path_tamper_rejected(self, tmp_path):
        # PS Sort-Object/-ne are case-insensitive by default: without the
        # ordinal comparison a case-only alteration compares equal (Sol
        # diff review round 1, F4).
        repo = make_repo(tmp_path)
        base = rev(repo)
        head = feature_head(repo, base)
        cp = self.make_checkpoint(repo)
        assert attest(repo, base, head, checkpoint=cp).returncode == 0
        record = json.loads(att_file(repo, head).read_text(encoding="utf-8"))
        record["changed_paths"] = ["F.txt"]
        att_file(repo, head).write_text(json.dumps(record), encoding="utf-8")
        v = verify(repo, head)
        assert v.returncode == 1 and "changed-path set" in v.stdout

    def test_tampered_changed_paths_rejected_on_merge(self, tmp_path):
        # The merge acceptance branch applies the same binding.
        repo = make_repo(tmp_path)
        base = rev(repo)
        head = feature_head(repo, base)
        cp = self.make_checkpoint(repo)
        assert attest(repo, base, head, checkpoint=cp).returncode == 0
        record = json.loads(att_file(repo, head).read_text(encoding="utf-8"))
        record["changed_paths"] = ["something-else.lua"]
        att_file(repo, head).write_text(json.dumps(record), encoding="utf-8")
        git(repo, "checkout", "-q", "-b", "trunk", base)
        git(repo, "merge", "-q", "--no-ff", "feat", "-m", "merge")
        v = verify(repo, rev(repo))
        assert v.returncode == 1 and "changed-path set" in v.stdout

    def test_record_without_binding_skips_check(self, tmp_path):
        # A clean PASS with no fix application carries the emitter's
        # explicit checkpoint_binding=none declaration and no binding
        # fields - the check must skip, not reject.
        repo = make_repo(tmp_path)
        base = rev(repo)
        head = feature_head(repo, base)
        assert attest(repo, base, head).returncode == 0
        record = json.loads(att_file(repo, head).read_text(encoding="utf-8"))
        assert record["schema"] == 2
        assert record["checkpoint_binding"] == "none"
        assert "changed_paths" not in record
        v = verify(repo, head)
        assert v.returncode == 0

    def test_delete_all_fields_on_bound_record_rejected(self, tmp_path):
        # The R-F3 bypass (Sol round 2): stripping ALL binding fields must
        # not downgrade a bound record to unbound - the emitter-authored
        # discriminator says it was bound.
        repo = make_repo(tmp_path)
        base = rev(repo)
        head = feature_head(repo, base)
        cp = self.make_checkpoint(repo)
        assert attest(repo, base, head, checkpoint=cp).returncode == 0
        record = json.loads(att_file(repo, head).read_text(encoding="utf-8"))
        assert record["checkpoint_binding"] == "bound"
        for field in ("checkpoint_file", "checkpoint_hash", "changed_paths"):
            del record[field]
        att_file(repo, head).write_text(json.dumps(record), encoding="utf-8")
        v = verify(repo, head)
        assert v.returncode == 1 and "binding fields missing" in v.stdout

    def test_stripped_discriminator_rejected(self, tmp_path):
        # A schema-2 record must carry the declaration itself; deleting it
        # is the same downgrade attempt one level up.
        repo = make_repo(tmp_path)
        base = rev(repo)
        head = feature_head(repo, base)
        cp = self.make_checkpoint(repo)
        assert attest(repo, base, head, checkpoint=cp).returncode == 0
        record = json.loads(att_file(repo, head).read_text(encoding="utf-8"))
        del record["checkpoint_binding"]
        att_file(repo, head).write_text(json.dumps(record), encoding="utf-8")
        v = verify(repo, head)
        assert v.returncode == 1 and "without checkpoint_binding" in v.stdout

    def test_binding_none_with_fields_rejected(self, tmp_path):
        # The declaration must AGREE with the fields present - a "none"
        # record smuggling binding fields is tampered either way.
        repo = make_repo(tmp_path)
        base = rev(repo)
        head = feature_head(repo, base)
        cp = self.make_checkpoint(repo)
        assert attest(repo, base, head, checkpoint=cp).returncode == 0
        record = json.loads(att_file(repo, head).read_text(encoding="utf-8"))
        record["checkpoint_binding"] = "none"
        att_file(repo, head).write_text(json.dumps(record), encoding="utf-8")
        v = verify(repo, head)
        assert v.returncode == 1 and "binding fields present" in v.stdout

    def test_legacy_schema1_record_accepted(self, tmp_path):
        # Pre-0.7.0 records are schema 1 with no discriminator and no
        # binding fields - they must stay accepted, or every existing
        # attestation dies retroactively.
        repo = make_repo(tmp_path)
        base = rev(repo)
        head = feature_head(repo, base)
        assert attest(repo, base, head).returncode == 0
        record = json.loads(att_file(repo, head).read_text(encoding="utf-8"))
        record["schema"] = 1
        del record["checkpoint_binding"]
        att_file(repo, head).write_text(json.dumps(record), encoding="utf-8")
        v = verify(repo, head)
        assert v.returncode == 0 and "direct" in v.stdout

    def test_missing_checkpoint_file_errors(self, tmp_path):
        repo = make_repo(tmp_path)
        base = rev(repo)
        head = feature_head(repo, base)
        p = attest(repo, base, head,
                   checkpoint=tmp_path / "no-such-checkpoint.md")
        assert p.returncode == 2 and "not found" in p.stdout
