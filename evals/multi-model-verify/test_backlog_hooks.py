"""Hook-shape tests for tools/backlog-hooks/*.py (2026-09-04 backlog
rewrite plan, spec Part 3).

Each script is fed the documented stdin JSON inside a temporary repo and
its exit code asserted. Every script is driven THROUGH the same
PowerShell entry point .claude/settings.json names (run-hook.ps1 with
-File), under whichever host PARALLAX_PS_HOST names, so the stdin
plumbing through the host is what is measured and not only the Python.
Skips when no host is found.
"""
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
FIXTURES = REPO / "evals" / "multi-model-verify" / "fixtures" / "backlog"
HOOKS = REPO / "tools" / "backlog-hooks"
POWERSHELL = (os.environ.get("PARALLAX_PS_HOST")
              or shutil.which("powershell") or shutil.which("pwsh"))
pytestmark = pytest.mark.skipif(POWERSHELL is None, reason="no PowerShell host")


def _git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True,
                          encoding="utf-8", check=True).stdout.strip()


def clean_text():
    return (FIXTURES / "clean.md").read_text(encoding="utf-8")


def seed_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "t")
    (repo / "BACKLOG.md").write_text(clean_text(), encoding="utf-8")
    old = repo / "docs" / "superpowers" / "plans" / "2026-07-27-0150-backlog.md"
    old.parent.mkdir(parents=True)
    old.write_text((FIXTURES / "pointer.md").read_text(encoding="utf-8"), encoding="utf-8")
    spec = repo / "docs" / "superpowers" / "specs"
    spec.mkdir(parents=True)
    (spec / "2026-09-04-backlog-rewrite-design.md").write_text("x\n", encoding="utf-8")
    (repo / "tools").mkdir()
    (repo / "tools" / "a.txt").write_text("a\n", encoding="utf-8")
    # Importing the scripts writes __pycache__ under governed paths; the
    # real repo ignores it at .gitignore:1 and the seed must too.
    (repo / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
    for name in ("run-hook.ps1", "_common.py", "session_start.py",
                 "post_tool_use.py", "stop.py"):
        (repo / "tools" / "backlog-hooks").mkdir(exist_ok=True)
        shutil.copy(HOOKS / name, repo / "tools" / "backlog-hooks" / name)
    (repo / "evals" / "tools").mkdir(parents=True)
    shutil.copy(REPO / "evals" / "tools" / "backlog_lint.py",
                repo / "evals" / "tools" / "backlog_lint.py")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "seed")
    return repo


HOOK_ARGS = ["-NoProfile", "-NonInteractive", "-File", "tools/backlog-hooks/run-hook.ps1",
             "-Script"]


def run_hook(repo, script, payload, baseline_dir, env_extra=None):
    """Drive the script exactly the way settings.json does: the host, then
    HOOK_ARGS, then the script name. Task 6 asserts the settings file's
    command strings are this same shape."""
    env = dict(os.environ, PARALLAX_BACKLOG_BASELINE_DIR=str(baseline_dir),
               PARALLAX_BACKLOG_TODAY="2026-09-04")
    env.update(env_extra or {})
    proc = subprocess.run([POWERSHELL, *HOOK_ARGS, script],
                          cwd=repo, input=json.dumps(payload), capture_output=True,
                          text=True, encoding="utf-8", env=env)
    return proc


def path_without_python():
    """A PATH with every directory that holds a python executable removed."""
    keep = []
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        if not entry:
            continue
        if any((Path(entry) / name).exists() for name in ("python.exe", "python")):
            continue
        keep.append(entry)
    return os.pathsep.join(keep)


def start(repo, baseline_dir, session="s1"):
    proc = run_hook(repo, "session_start.py", {"session_id": session, "cwd": str(repo),
                                               "hook_event_name": "SessionStart"},
                    baseline_dir)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return proc


def stop(repo, baseline_dir, session="s1", active=False):
    return run_hook(repo, "stop.py", {"session_id": session, "cwd": str(repo),
                                      "hook_event_name": "Stop",
                                      "stop_hook_active": active}, baseline_dir)


class TestSessionStart:
    def test_writes_baseline(self, tmp_path):
        repo = seed_repo(tmp_path)
        base = tmp_path / "b"
        start(repo, base)
        data = json.loads((base / "s1.json").read_text(encoding="utf-8"))
        assert data["head"] == _git(repo, "rev-parse", "HEAD")
        digest = hashlib.sha256((repo / "BACKLOG.md").read_bytes()).hexdigest()
        assert data["backlog_sha256"] == digest

    def test_absent_backlog_recorded(self, tmp_path):
        repo = seed_repo(tmp_path)
        (repo / "BACKLOG.md").unlink()
        base = tmp_path / "b"
        start(repo, base)
        data = json.loads((base / "s1.json").read_text(encoding="utf-8"))
        assert data["backlog_sha256"] == "absent"


class TestEntryPoint:
    def test_missing_python_passes_with_note(self, tmp_path):
        repo = seed_repo(tmp_path)
        proc = run_hook(repo, "stop.py", {"session_id": "s1", "cwd": str(repo),
                                          "stop_hook_active": False},
                        tmp_path / "b", env_extra={"PATH": path_without_python()})
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert "python not found" in proc.stdout

    def test_unknown_script_name_is_refused(self, tmp_path):
        repo = seed_repo(tmp_path)
        proc = run_hook(repo, "nope.py", {}, tmp_path / "b")
        assert proc.returncode == 0 and "not found" in proc.stdout


class TestPostToolUse:
    def test_backlog_edit_reports_lint(self, tmp_path):
        repo = seed_repo(tmp_path)
        (repo / "BACKLOG.md").write_text(clean_text().replace("- 3\n", ""), encoding="utf-8")
        proc = run_hook(repo, "post_tool_use.py",
                        {"tool_name": "Edit",
                         "tool_input": {"file_path": str(repo / "BACKLOG.md")}},
                        tmp_path / "b")
        assert proc.returncode == 0
        data = json.loads(proc.stdout)
        assert "item 3: rule 4" in data["hookSpecificOutput"]["additionalContext"]

    def test_other_file_is_silent(self, tmp_path):
        repo = seed_repo(tmp_path)
        proc = run_hook(repo, "post_tool_use.py",
                        {"tool_name": "Write",
                         "tool_input": {"file_path": str(repo / "tools" / "a.txt")}},
                        tmp_path / "b")
        assert proc.returncode == 0 and proc.stdout.strip() == ""


class TestStop:
    def test_stop_hook_active_passes(self, tmp_path):
        repo = seed_repo(tmp_path)
        base = tmp_path / "b"
        start(repo, base)
        (repo / "tools" / "a.txt").write_text("b\n", encoding="utf-8")
        assert stop(repo, base, active=True).returncode == 0

    def test_missing_baseline_passes_with_note(self, tmp_path):
        repo = seed_repo(tmp_path)
        proc = stop(repo, tmp_path / "b")
        assert proc.returncode == 0 and "baseline" in proc.stdout

    def test_governed_change_without_backlog_blocks(self, tmp_path):
        repo = seed_repo(tmp_path)
        base = tmp_path / "b"
        start(repo, base)
        (repo / "tools" / "a.txt").write_text("b\n", encoding="utf-8")
        proc = stop(repo, base)
        assert proc.returncode == 2
        refusal = ("BACKLOG.md carries no re-attested item this session while governed "
                   "surfaces changed; update the item that owns the work and refresh "
                   "its Verified field")
        assert refusal in proc.stdout and refusal in proc.stderr

    def test_governed_change_committed_still_blocks(self, tmp_path):
        repo = seed_repo(tmp_path)
        base = tmp_path / "b"
        start(repo, base)
        (repo / "tools" / "a.txt").write_text("b\n", encoding="utf-8")
        _git(repo, "commit", "-q", "-am", "x")
        assert stop(repo, base).returncode == 2

    def test_new_untracked_governed_file_blocks(self, tmp_path):
        repo = seed_repo(tmp_path)
        base = tmp_path / "b"
        start(repo, base)
        (repo / "tools" / "new.txt").write_text("b\n", encoding="utf-8")
        assert stop(repo, base).returncode == 2

    def test_governed_change_with_reattest_passes(self, tmp_path):
        repo = seed_repo(tmp_path)
        base = tmp_path / "b"
        start(repo, base)
        (repo / "tools" / "a.txt").write_text("b\n", encoding="utf-8")
        text = clean_text()
        old = [ln for ln in text.splitlines() if ln.startswith("Verified: ")][0]
        text = text.replace(old, old.replace("2026-09-04", "2026-09-03"), 1)
        (repo / "BACKLOG.md").write_text(text, encoding="utf-8")
        proc = stop(repo, base)
        assert proc.returncode == 0 and "re-attested: 1" in proc.stdout

    def test_unrelated_backlog_byte_blocks(self, tmp_path):
        repo = seed_repo(tmp_path)
        base = tmp_path / "b"
        start(repo, base)
        (repo / "tools" / "a.txt").write_text("b\n", encoding="utf-8")
        (repo / "BACKLOG.md").write_text(clean_text().replace("Headers are", "HEADERS are"),
                                         encoding="utf-8")
        assert stop(repo, base).returncode == 2

    def test_docs_only_change_passes(self, tmp_path):
        repo = seed_repo(tmp_path)
        base = tmp_path / "b"
        start(repo, base)
        (repo / "docs" / "superpowers" / "specs" / "2026-09-04-backlog-rewrite-design.md"
         ).write_text("y\n", encoding="utf-8")
        assert stop(repo, base).returncode == 0

    def test_backlog_edit_failing_lint_blocks(self, tmp_path):
        repo = seed_repo(tmp_path)
        base = tmp_path / "b"
        start(repo, base)
        (repo / "BACKLOG.md").write_text(clean_text().replace("- 3\n", ""), encoding="utf-8")
        proc = stop(repo, base)
        assert proc.returncode == 2 and "item 3: rule 4" in proc.stdout

    def test_detached_head_is_handled(self, tmp_path):
        repo = seed_repo(tmp_path)
        _git(repo, "checkout", "-q", "--detach")
        base = tmp_path / "b"
        start(repo, base)
        (repo / "tools" / "a.txt").write_text("b\n", encoding="utf-8")
        assert stop(repo, base).returncode == 2

    def test_git_unavailable_passes_with_note(self, tmp_path):
        repo = seed_repo(tmp_path)
        base = tmp_path / "b"
        start(repo, base)
        (repo / "tools" / "a.txt").write_text("b\n", encoding="utf-8")
        proc = run_hook(repo, "stop.py", {"session_id": "s1", "cwd": str(repo),
                                          "stop_hook_active": False}, base,
                        env_extra={"PARALLAX_BACKLOG_GIT": "C:/no/such/git.exe"})
        assert proc.returncode == 0 and "git" in proc.stdout
