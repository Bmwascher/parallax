"""Disposable-clone tests for the pre-push backlog clause (spec 3c).

A bare stub remote and a clone with core.hooksPath pointing at the
working-tree .githooks/pre-push, so uncommitted hook edits are what gets
tested. Each scenario pushes main with a merge, a squash or a
fast-forward, with and without a re-attested item beside a governed
change. The hook is bash under git; git for Windows ships it.
"""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
FIXTURES = REPO / "evals" / "multi-model-verify" / "fixtures" / "backlog"


def _git(repo, *args, check=True):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True,
                          encoding="utf-8", check=check)


def out(repo, *args):
    return _git(repo, *args).stdout.strip()


def clean_text():
    return (FIXTURES / "clean.md").read_text(encoding="utf-8")


def refreshed(text, item_id="1"):
    lines = text.splitlines(keepends=True)
    seen = False
    for index, line in enumerate(lines):
        if line.startswith("## %s. " % item_id):
            seen = True
        if seen and line.startswith("Verified: 2026-09-04 "):
            lines[index] = line.replace("2026-09-04", "2026-09-03", 1)
            break
    return "".join(lines)


@pytest.fixture
def clone(tmp_path):
    remote = tmp_path / "remote.git"
    _git(tmp_path, "init", "-q", "--bare", "-b", "main", str(remote))
    work = tmp_path / "work"
    work.mkdir()
    _git(work, "init", "-q", "-b", "main")
    _git(work, "config", "user.email", "t@t")
    _git(work, "config", "user.name", "t")
    (work / "BACKLOG.md").write_text(clean_text(), encoding="utf-8")
    old = work / "docs" / "superpowers" / "plans" / "2026-07-27-0150-backlog.md"
    old.parent.mkdir(parents=True)
    old.write_text((FIXTURES / "pointer.md").read_text(encoding="utf-8"), encoding="utf-8")
    spec = work / "docs" / "superpowers" / "specs"
    spec.mkdir(parents=True)
    (spec / "2026-09-04-backlog-rewrite-design.md").write_text("x\n", encoding="utf-8")
    (work / "tools").mkdir()
    (work / "tools" / "a.txt").write_text("a\n", encoding="utf-8")
    (work / "README.md").write_text("r\n", encoding="utf-8")
    (work / "CLAUDE.md").write_text("c\n", encoding="utf-8")
    (work / "evals" / "tools").mkdir(parents=True)
    for name in ("backlog_lint.py", "exact_line.py"):
        shutil.copy(REPO / "evals" / "tools" / name, work / "evals" / "tools" / name)
    hooks = work / ".githooks"
    hooks.mkdir()
    shutil.copy(REPO / ".githooks" / "pre-push", hooks / "pre-push")
    _git(work, "add", "-A")
    _git(work, "commit", "-q", "-m", "seed")
    _git(work, "remote", "add", "origin", str(remote))
    _git(work, "config", "core.hooksPath", ".githooks")
    seed_push = push(work)
    assert seed_push.returncode == 0, seed_push.stderr
    return work


def push(work):
    """Every push, the seed included, pins today so the fixture's dates
    never read as future on a machine whose clock is behind."""
    env = dict(os.environ, PARALLAX_BACKLOG_TODAY="2026-09-04")
    return subprocess.run(["git", "push", "origin", "main"], cwd=work, capture_output=True,
                          text=True, encoding="utf-8", env=env)


def feature(work, files, message="feat"):
    _git(work, "switch", "-q", "-c", "feat")
    for path, text in files.items():
        target = work / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    _git(work, "add", "-A")
    _git(work, "commit", "-q", "-m", message)
    _git(work, "switch", "-q", "main")


def land(work, how):
    if how == "merge":
        _git(work, "merge", "-q", "--no-ff", "-m", "merge", "feat")
    elif how == "squash":
        _git(work, "merge", "-q", "--squash", "feat")
        _git(work, "commit", "-q", "-m", "squash")
    else:
        _git(work, "merge", "-q", "--ff-only", "feat")


@pytest.mark.parametrize("how", ["merge", "squash", "ff"])
def test_governed_change_without_reattest_is_refused(clone, how):
    feature(clone, {"tools/a.txt": "b\n"})
    land(clone, how)
    proc = push(clone)
    assert proc.returncode != 0
    assert "no OPEN or PARTIAL item was re-attested" in proc.stderr + proc.stdout


@pytest.mark.parametrize("how", ["merge", "squash", "ff"])
def test_governed_file_renamed_out_of_governance_is_refused(clone, how):
    """A rename lists both sides, so the governed source still counts."""
    _git(clone, "switch", "-q", "-c", "feat")
    _git(clone, "mv", "tools/a.txt", "docs/a.txt")
    _git(clone, "commit", "-q", "-m", "move")
    _git(clone, "switch", "-q", "main")
    land(clone, how)
    proc = push(clone)
    assert proc.returncode != 0
    assert "tools/a.txt" in proc.stderr + proc.stdout


@pytest.mark.parametrize("how", ["merge", "squash", "ff"])
def test_governed_change_with_reattest_passes(clone, how):
    feature(clone, {"tools/a.txt": "b\n", "BACKLOG.md": refreshed(clean_text())})
    land(clone, how)
    proc = push(clone)
    assert proc.returncode == 0, proc.stderr


def test_docs_only_push_passes(clone):
    feature(clone, {"docs/note.md": "n\n"})
    land(clone, "ff")
    assert push(clone).returncode == 0


@pytest.mark.parametrize("path", ["README.md", "CLAUDE.md"])
def test_readme_or_claude_alone_is_refused(clone, path):
    feature(clone, {path: "changed\n"})
    land(clone, "ff")
    assert push(clone).returncode != 0


def test_unrelated_backlog_byte_is_refused(clone):
    feature(clone, {"tools/a.txt": "b\n",
                    "BACKLOG.md": clean_text().replace("Headers are", "HEADERS are")})
    land(clone, "ff")
    assert push(clone).returncode != 0


def test_backlog_failing_lint_is_refused(clone):
    feature(clone, {"BACKLOG.md": clean_text().replace("- 3\n", "")})
    land(clone, "ff")
    proc = push(clone)
    assert proc.returncode != 0 and "item 3: rule 4" in proc.stderr + proc.stdout


def test_range_mode_driven_directly_agrees(clone):
    feature(clone, {"tools/a.txt": "b\n"})
    land(clone, "ff")
    base = out(clone, "rev-parse", "origin/main")
    head = out(clone, "rev-parse", "HEAD")
    proc = subprocess.run(["python", "evals/tools/backlog_lint.py", "--range",
                           "%s..%s" % (base, head)], cwd=clone, capture_output=True,
                          text=True, encoding="utf-8",
                          env=dict(os.environ, PARALLAX_BACKLOG_TODAY="2026-09-04"))
    assert proc.returncode == 1


def test_missing_python_refuses(clone, tmp_path):
    feature(clone, {"docs/note.md": "n\n"})
    land(clone, "ff")
    env = dict(os.environ, PARALLAX_BACKLOG_PYTHON="C:/no/such/python.exe")
    proc = subprocess.run(["git", "push", "origin", "main"], cwd=clone, capture_output=True,
                          text=True, encoding="utf-8", env=env)
    assert proc.returncode != 0 and "python" in (proc.stderr + proc.stdout).lower()


def test_non_main_push_is_not_checked(clone):
    feature(clone, {"tools/a.txt": "b\n"})
    proc = subprocess.run(["git", "push", "-q", "origin", "feat"], cwd=clone,
                          capture_output=True, text=True, encoding="utf-8")
    assert proc.returncode == 0, proc.stderr
