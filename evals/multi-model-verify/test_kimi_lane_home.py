"""Contract pins for the per-debate kimi-code lane home."""
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BUILDER = REPO / "tools" / "new-kimi-lane-home.ps1"
SENTINEL = ".parallax-lane-home"


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
