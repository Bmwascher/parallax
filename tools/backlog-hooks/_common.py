"""Shared pieces of the three backlog hook scripts. Stdlib only.

Every script reads the hook's JSON from stdin and prints for the harness.
The baseline directory is PARALLAX_BACKLOG_BASELINE_DIR when set, else
<tempdir>/parallax-backlog-baselines; a file per session_id.
PARALLAX_BACKLOG_GIT overrides the git binary (tests use it to simulate a
missing git).
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKLOG = REPO_ROOT / "BACKLOG.md"


def load_lint():
    path = REPO_ROOT / "evals" / "tools" / "backlog_lint.py"
    spec = importlib.util.spec_from_file_location("backlog_lint", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_payload():
    raw = sys.stdin.read()
    try:
        return json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return {}


def baseline_dir():
    override = os.environ.get("PARALLAX_BACKLOG_BASELINE_DIR")
    base = Path(override) if override else Path(tempfile.gettempdir()) / "parallax-backlog-baselines"
    base.mkdir(parents=True, exist_ok=True)
    return base


def baseline_path(session_id):
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in (session_id or "unknown"))
    return baseline_dir() / (safe + ".json")


def git(*args):
    binary = os.environ.get("PARALLAX_BACKLOG_GIT", "git")
    try:
        proc = subprocess.run([binary, *args], cwd=str(REPO_ROOT), capture_output=True,
                              text=True, encoding="utf-8")
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout


def backlog_sha256():
    if not BACKLOG.exists():
        return "absent"
    return hashlib.sha256(BACKLOG.read_bytes()).hexdigest()


def lint_working_tree(lint):
    """Run the lint on the working tree; return (exit_code, output_text)."""
    import io
    import contextlib
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        code = lint.main(["--repo-root", str(REPO_ROOT)])
    return code, buffer.getvalue()
