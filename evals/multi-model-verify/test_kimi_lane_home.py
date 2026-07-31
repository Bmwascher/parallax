"""Contract pins for the per-debate kimi-code lane home."""
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
BUILDER = REPO / "tools" / "new-kimi-lane-home.ps1"
SENTINEL = ".parallax-lane-home"

# Fix-round finding (Critical 1): live proof that an unsanitized -Model
# cannot be rendered into config.toml. A text-only pin against the static
# template cannot catch this - the injection happens at render time, when
# the caller's value is interpolated - so this one test actually invokes
# the script. Skipped, not failed, when neither host is on PATH: the rest
# of this file is offline and must still run in that environment.
POWERSHELL = shutil.which("powershell") or shutil.which("pwsh")


def _read(p):
    return p.read_text(encoding="utf-8")


def test_builder_exists():
    assert BUILDER.is_file(), str(BUILDER)


def test_model_is_mandatory_within_the_build_set_only():
    """SWEEP_GLOBS covers tools/*.ps1, so a parameter default carrying the
    canonical id would fail test_backup_literal_single_source. But a
    GLOBALLY mandatory -Model makes `-Remove` uncallable, so the two forms
    are separate parameter sets."""
    body = _read(BUILDER)
    assert 'DefaultParameterSetName = "Build"' in body
    assert 'ParameterSetName = "Build", Mandatory = $true)][string]$Model' in body
    assert "k3-256k" not in body


def test_builder_refuses_without_a_credential():
    assert "the lane is UNAVAILABLE" in _read(BUILDER)


def test_builder_refuses_a_reused_or_unsafe_destination():
    """A reused home carries stale sessions, which is exactly what the
    freshness rule exists to exclude, so reuse corrupts the evidence
    rather than merely being untidy."""
    body = _read(BUILDER)
    assert "destination already exists" in body
    assert "inside a git work tree" in body


def test_the_git_check_fails_closed():
    """r2 treated any nonzero `git rev-parse` as 'not in a work tree', so
    git being absent or erroring placed an OAuth credential in a repo."""
    body = _read(BUILDER)
    assert "$LASTEXITCODE" in body
    assert "could not determine" in body


def test_removal_is_callable_and_guarded():
    """r2 defined a function inside a script invoked with `pwsh -File`,
    which no caller can ever reach. Removal is a parameter set on the same
    script, and it refuses any directory this builder did not create.

    The sentinel's NAME is not the credential: a bare filename can be
    planted in any directory and would then authorize a recursive delete.
    It carries a magic string and the resolved path it was written for,
    and removal refuses a mismatch."""
    body = _read(BUILDER)
    assert "[switch]$Remove" in body
    assert SENTINEL in body
    assert "PARALLAX-LANE-HOME-V1" in body
    assert "sentinel does not match this path" in body


def test_removal_refuses_dangerous_roots():
    """Belt and braces on top of the sentinel: even a correctly-formed
    sentinel must not authorize deleting a drive root, the user profile,
    or a repository root. Task 3 Step 5 exercises all three live, each
    with a correctly-formed sentinel - a guard that has only ever seen a
    malformed sentinel has not been tested."""
    body = _read(BUILDER)
    assert "refusing to remove" in body
    assert "$env:USERPROFILE" in body
    assert "IsPathRooted" in body
    assert ".git" in body


def test_a_failed_build_leaves_no_credential_behind():
    """Cleanup runs only for a directory THIS invocation created and
    marked - an unconditional recursive delete in a catch block would
    delete a directory the script had refused to touch."""
    body = _read(BUILDER)
    assert "try {" in body
    assert "$createdByThisInvocation" in body


def test_cleanup_is_fault_tested_live():
    """A cleanup path with no test asserting it runs is a cleanup path
    that has never run. Task 3 Step 5 injects a post-credential failure."""
    body = _read(BUILDER)
    assert "PARALLAX_LANE_HOME_FAULT" in body


def test_builder_writes_no_hooks():
    """The user's real config carries seven Orca lifecycle hooks including
    PreToolUse and PermissionRequest, each running a shell script."""
    body = _read(BUILDER)
    assert "[[hooks]]" not in body
    assert "carries no hooks by construction" in body


def test_builder_pins_effort_and_empties_the_skill_sources():
    body = _read(BUILDER)
    assert "extra_skill_dirs = []" in body
    assert "default_effort" in body


@pytest.mark.skipif(POWERSHELL is None, reason="no PowerShell host on PATH")
def test_a_hostile_model_is_refused_not_rendered(tmp_path):
    """The reviewer's failure scenario, run for real: a -Model carrying a
    double quote and a newline would, unvalidated, break out of the
    `[models."$Model"]` quoting and let an attacker write a fabricated
    hooks table into the rendered config.toml - the exact command-executing
    back-channel this script exists to keep out of the reviewer's config.
    The refusal must land BEFORE anything is rendered or written: no
    destination directory, no config.toml, no credential copy."""
    target = tmp_path / "hostile-home"
    hostile_model = (
        'kimi-code/test-model"]\n\n[hooks]\nevent = "PreToolUse"\n'
        'command = "calc.exe"\n[models."x'
    )
    proc = subprocess.run(
        [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-File", str(BUILDER), "-Path", str(target), "-Model", hostile_model],
        capture_output=True, text=True, timeout=60)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert not target.exists(), "a hostile -Model must be refused before any directory is created"


@pytest.mark.skipif(POWERSHELL is None, reason="no PowerShell host on PATH")
def test_a_hostile_effort_is_refused_not_rendered(tmp_path):
    """Same injection surface, the other interpolated parameter."""
    target = tmp_path / "hostile-effort-home"
    proc = subprocess.run(
        [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-File", str(BUILDER), "-Path", str(target),
         "-Model", "kimi-code/test-placeholder-model",
         "-Effort", 'high"\n\n[hooks]\nevent = "PreToolUse'],
        capture_output=True, text=True, timeout=60)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert not target.exists(), "a hostile -Effort must be refused before any directory is created"


@pytest.mark.skipif(POWERSHELL is None, reason="no PowerShell host on PATH")
def test_a_model_with_a_trailing_newline_is_refused(tmp_path):
    """Fix-round-2 finding (Open 1 from Critical 1): in .NET regex, $
    matches before a single trailing newline at the end of the string even
    without multiline mode, so the original '^[...]*$' pattern let a
    -Model ending in exactly one literal newline through despite the
    newline itself not being in the documented allowed set - confirmed
    live, both in isolation against the pattern and by running the real
    script, which sailed past validation and went on to create
    directories. The anchors are now \\A and \\z, which admit no such
    exception. This does not reopen the hooks-injection attack (quotes and
    brackets are still excluded), but the requirement was to reject
    anything outside the strict set, and a trailing newline is outside it."""
    target = tmp_path / "trailing-newline-home"
    proc = subprocess.run(
        [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-File", str(BUILDER), "-Path", str(target),
         "-Model", "kimi-code/test-placeholder-model\n"],
        capture_output=True, text=True, timeout=60)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert not target.exists(), "a -Model with a trailing newline must be refused before any directory is created"
