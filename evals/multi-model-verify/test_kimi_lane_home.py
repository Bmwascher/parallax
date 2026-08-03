"""Contract pins for the per-debate kimi-code lane home.

Task 6 (2026-08-01 lane-credential-and-lock plan) removed the credential
COPY: the builder now acquires a persistent per-lane-home lock
(tools/kimi-lane-lock.ps1), validates a lane-owned credential
(tools/read-kimi-credential-state.ps1) at <lane-home>\\credentials\\
kimi-code.json, and junctions the debate home's own `credentials`
directory to it rather than copying a file across. Every process-driving
test below therefore needs, in addition to the fake USERPROFILE carrying
the real config.toml (for the model-table-carrying gates), a LANE HOME
fixture carrying its own credential, plus the four new mandatory
identity parameters (-LaneHome/-DebateId/-OwnerPid/-OwnerStartTicksUtc,
plus -Nonce on -Remove).
"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import tomllib
import uuid
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
BUILDER = REPO / "tools" / "new-kimi-lane-home.ps1"
CREDENTIAL_VALIDATOR = REPO / "tools" / "read-kimi-credential-state.ps1"
LOCK_TOOL = REPO / "tools" / "kimi-lane-lock.ps1"
LOGIN_WRAPPER = REPO / "tools" / "new-kimi-lane-login.ps1"
SENTINEL = ".parallax-lane-home"


def _load_exact_line_module():
    path = REPO / "evals" / "tools" / "exact_line.py"
    spec = importlib.util.spec_from_file_location("exact_line", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


accept_exactly_one_nonempty_line = _load_exact_line_module().accept_exactly_one_nonempty_line

# Fix-round finding (Critical 1): live proof that an unsanitized -Model
# cannot be rendered into config.toml. A text-only pin against the static
# template cannot catch this - the injection happens at render time, when
# the caller's value is interpolated - so this one test actually invokes
# the script.
#
# WINDOWS ONLY, whole module: the builder manipulates real Windows
# filesystem behaviour ($env:USERPROFILE-rooted paths, ACLs via Get-Acl,
# junctions). PARALLAX_PS_HOST selects which host runs these tests, same
# pattern as test_codex_context_probe.py:35-67 - a selector that merely
# finds A host would happily collect them on Ubuntu CI too, where pwsh is
# on PATH but the Windows paths and ACL semantics under test do not
# exist. A green suite on one Windows host proves ONE interpreter.
POWERSHELL = (os.environ.get("PARALLAX_PS_HOST")
              or shutil.which("powershell") or shutil.which("pwsh"))

pytestmark = pytest.mark.skipif(
    os.name != "nt" or POWERSHELL is None,
    reason="this suite exercises real Windows filesystem behaviour; it "
           "needs a PowerShell host and the platform it actually targets")


def _read(p):
    return p.read_text(encoding="utf-8")


def test_builder_exists():
    assert BUILDER.is_file(), str(BUILDER)


def test_model_is_mandatory_within_the_build_set_only():
    """SWEEP_GLOBS covers tools/*.ps1, so a parameter default carrying the
    canonical id would fail test_backup_literal_single_source. But a
    GLOBALLY mandatory -Model would make `-Remove` uncallable, so the two
    forms are separate parameter sets."""
    body = _read(BUILDER)
    assert 'DefaultParameterSetName = "Build"' in body
    assert 'ParameterSetName = "Build", Mandatory = $true)][string]$Model' in body
    assert "k3-256k" not in body


def test_builder_refuses_without_a_lane_home():
    """The old message text ("the lane is UNAVAILABLE") is reused for the
    new first-use probe's nonexistent-lane-home row."""
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
    or a repository root."""
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
    that has never run."""
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


def test_builder_no_longer_copies_a_credential():
    """Task 6: the credential COPY is gone; a JUNCTION replaces it."""
    body = _read(BUILDER)
    assert "Copy-Item" not in body
    assert "New-Item -ItemType Junction" in body


def test_lock_and_validator_tools_are_invoked_not_rewritten():
    body = _read(BUILDER)
    assert "kimi-lane-lock.ps1" in body
    assert "read-kimi-credential-state.ps1" in body


# ---------------------------------------------------------------------
# Shared fixtures for every process-driving test below.
# ---------------------------------------------------------------------

VALID_CREDENTIAL_JSON = (
    '{"access_token": "not-a-real-token", '
    '"refresh_token": "not-a-real-refresh-token", '
    '"expires_at": 900}')

DIFFERING_USER_CREDENTIAL_JSON = (
    '{"access_token": "user-side-token-must-never-be-read", '
    '"refresh_token": "user-side-refresh-must-never-be-read", '
    '"expires_at": 111}')

PLACEHOLDER_MODEL = "kimi-code/test-placeholder-model"

FAKE_REAL_CONFIG = '''default_model = "kimi-code/some-other-model"

[[hooks]]
event = "PreToolUse"
command = "/bin/sh /some/hook.sh"
timeout = 10

[providers."managed:kimi-code"]
type = "kimi"
api_key = ""
base_url = "https://api.kimi.com/coding/v1"

[models."kimi-code/some-other-model"]
provider = "managed:kimi-code"
model = "some-other-model"
max_context_size = 1048576
capabilities = [ "thinking", "tool_use" ]
display_name = "Some Other"

[models."%s"]
provider = "managed:kimi-code"
model = "test-placeholder-model"
max_context_size = 262144
capabilities = [ "thinking", "always_thinking", "image_in", "tool_use" ]
display_name = "Test Placeholder"
support_efforts = [ "low", "high", "max" ]
default_effort = "low"

[thinking]
enabled = true

[services.moonshot_search]
base_url = "https://api.kimi.com/coding/v1/search"
api_key = ""
''' % PLACEHOLDER_MODEL


def _clean_env(**overrides):
    """PSModulePath dropped: this pytest process inherits a PowerShell 7
    flavoured PSModulePath whose ...\\PowerShell\\7\\Modules entry shadows
    the 5.1 copy of Microsoft.PowerShell.Security, so Get-Acl fails to
    load inside a powershell.exe child. Popped case-insensitively:
    os.environ normalizes keys to upper case on Windows, so a plain
    pop("PSModulePath") silently removes nothing."""
    env = dict(os.environ)
    for key in [k for k in env if k.lower() == "psmodulepath"]:
        del env[key]
    env.update(overrides)
    return env


def _fake_profile(tmp_path, config_text, name="fake-profile"):
    """A stand-in USERPROFILE carrying only .kimi-code/config.toml (the
    model-table source) and, optionally, a DIFFERING credential planted
    to prove the builder never reads it any more."""
    profile = tmp_path / name
    kimi = profile / ".kimi-code"
    kimi.mkdir(parents=True)
    if config_text is not None:
        (kimi / "config.toml").write_text(config_text, encoding="ascii")
    return profile


def _fake_lane_home(tmp_path, name="lane-home", credential_text=VALID_CREDENTIAL_JSON,
                     seed_credential=True):
    """A stand-in persistent lane home: a plain directory, optionally
    carrying a `credentials\\kimi-code.json`. seed_credential=False leaves
    the directory present but the credential absent."""
    lane_home = tmp_path / name
    lane_home.mkdir(parents=True, exist_ok=True)
    if seed_credential:
        cred_dir = lane_home / "credentials"
        cred_dir.mkdir(parents=True, exist_ok=True)
        (cred_dir / "kimi-code.json").write_text(credential_text, encoding="ascii")
    return lane_home


def _new_hex32():
    return uuid.uuid4().hex


_SELF_TICKS_CACHE = {}


def _self_owner_identity():
    """(ownerPid, ownerStartTicksUtc) for THIS pytest process - a real,
    live process for the whole test run, which is what a Remove-mode
    identity re-verification needs (the lock's own liveness check treats
    a dead owner pid as DEAD even on an otherwise-matching re-acquire)."""
    pid = os.getpid()
    if pid not in _SELF_TICKS_CACHE:
        proc = subprocess.run(
            [POWERSHELL, "-NoProfile", "-Command",
             "(Get-Process -Id %d).StartTime.ToUniversalTime().Ticks" % pid],
            capture_output=True, text=True, timeout=30)
        assert proc.returncode == 0, proc.stdout + proc.stderr
        _SELF_TICKS_CACHE[pid] = proc.stdout.strip()
    return str(pid), _SELF_TICKS_CACHE[pid]


def _owner_ticks_for_pid(pid):
    proc = subprocess.run(
        [POWERSHELL, "-NoProfile", "-Command",
         "(Get-Process -Id %d).StartTime.ToUniversalTime().Ticks" % pid],
        capture_output=True, text=True, timeout=30)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return proc.stdout.strip()


def _build2(target, profile, lane_home, model=PLACEHOLDER_MODEL, effort="high",
            debate_id=None, owner_pid=None, owner_ticks=None, extra_env=None,
            timeout=120):
    if debate_id is None:
        debate_id = _new_hex32()
    if owner_pid is None or owner_ticks is None:
        self_pid, self_ticks = _self_owner_identity()
        owner_pid = owner_pid or self_pid
        owner_ticks = owner_ticks or self_ticks
    env = _clean_env(USERPROFILE=str(profile))
    if extra_env:
        env.update(extra_env)
    proc = subprocess.run(
        [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-File", str(BUILDER), "-Path", str(target),
         "-Model", model, "-Effort", effort,
         "-LaneHome", str(lane_home), "-DebateId", debate_id,
         "-OwnerPid", str(owner_pid), "-OwnerStartTicksUtc", str(owner_ticks)],
        capture_output=True, text=True, timeout=timeout, env=env)
    return proc, debate_id, str(owner_pid), str(owner_ticks)


def _remove2(target, lane_home, debate_id, owner_pid, owner_ticks, nonce,
             extra_env=None, timeout=120):
    env = _clean_env()
    if extra_env:
        env.update(extra_env)
    proc = subprocess.run(
        [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-File", str(BUILDER), "-Path", str(target), "-Remove",
         "-LaneHome", str(lane_home), "-DebateId", debate_id,
         "-OwnerPid", str(owner_pid), "-OwnerStartTicksUtc", str(owner_ticks),
         "-Nonce", nonce],
        capture_output=True, text=True, timeout=timeout, env=env)
    return proc


def _lock_status(lane_home):
    proc = subprocess.run(
        [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-File", str(LOCK_TOOL), "-Status", "-LaneHome", str(lane_home)],
        capture_output=True, text=True, timeout=60, env=_clean_env())
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return json.loads(proc.stdout)


def _lock_acquire_direct(lane_home, debate_id, owner_pid, owner_ticks, debate_home,
                          nonce=None):
    args = [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", str(LOCK_TOOL), "-Acquire", "-LaneHome", str(lane_home),
            "-DebateId", debate_id, "-OwnerPid", str(owner_pid),
            "-OwnerStartTicksUtc", str(owner_ticks), "-DebateHome", str(debate_home)]
    if nonce:
        args += ["-Nonce", nonce]
    proc = subprocess.run(args, capture_output=True, text=True, timeout=60,
                           env=_clean_env())
    return proc


def _lock_release_direct(lane_home, debate_id, owner_pid, owner_ticks, nonce):
    proc = subprocess.run(
        [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-File", str(LOCK_TOOL), "-Release", "-LaneHome", str(lane_home),
         "-DebateId", debate_id, "-OwnerPid", str(owner_pid),
         "-OwnerStartTicksUtc", str(owner_ticks), "-Nonce", nonce],
        capture_output=True, text=True, timeout=60, env=_clean_env())
    return proc


def _parse_custody(stdout):
    line = accept_exactly_one_nonempty_line(stdout)
    assert line is not None, "expected exactly one stdout line, got: %r" % (stdout,)
    obj = json.loads(line)
    assert set(obj.keys()) == {"debateHome", "nonce"}, obj
    return obj


# --- rewritten "existing gate" tests: real invocations now need the lane
# home fixture too, since the gates they exercise all sit AFTER lock
# acquisition and credential validation in the new build order. ---


def test_a_hostile_model_is_refused_not_rendered(tmp_path):
    """The reviewer's failure scenario, run for real: a -Model carrying a
    double quote and a newline would, unvalidated, break out of the
    `[models."$Model"]` quoting. The refusal must land BEFORE anything is
    rendered or written: no destination directory, no config.toml, no
    junction."""
    target = tmp_path / "hostile-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)
    hostile_model = (
        'kimi-code/test-model"]\n\n[hooks]\nevent = "PreToolUse"\n'
        'command = "calc.exe"\n[models."x'
    )
    proc, debate_id, owner_pid, owner_ticks = _build2(
        target, profile, lane_home, model=hostile_model)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert not target.exists(), "a hostile -Model must be refused before any directory is created"
    assert _lock_status(lane_home)["state"] == "free"


def test_a_hostile_effort_is_refused_not_rendered(tmp_path):
    target = tmp_path / "hostile-effort-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)
    proc, *_ = _build2(target, profile, lane_home,
                        effort='high"\n\n[hooks]\nevent = "PreToolUse')
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert not target.exists(), "a hostile -Effort must be refused before any directory is created"
    assert _lock_status(lane_home)["state"] == "free"


def test_a_model_with_a_trailing_newline_is_refused(tmp_path):
    """Fix-round-2 finding: in .NET regex, $ matches before a single
    trailing newline at the end of the string even without multiline
    mode."""
    target = tmp_path / "trailing-newline-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)
    proc, *_ = _build2(target, profile, lane_home,
                        model="kimi-code/test-placeholder-model\n")
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert not target.exists()
    assert _lock_status(lane_home)["state"] == "free"


def _render_config_template(model, effort, model_table_fields):
    body = _read(BUILDER)
    match = re.search(r'\$configToml = @"\r?\n(.*?)\r?\n"@', body, re.DOTALL)
    assert match, "could not locate the config.toml here-string in the builder"
    template = match.group(1)
    return (template
            .replace("$modelTableFields", model_table_fields)
            .replace("$Model", model)
            .replace("$Effort", effort))


def test_rendered_config_places_root_keys_at_the_document_root():
    rendered = _render_config_template(
        model="kimi-code/test-model", effort="high",
        model_table_fields=('provider = "managed:kimi-code"\n'
                            'model = "test-model"\n'
                            "max_context_size = 262144"))
    parsed = tomllib.loads(rendered)

    assert parsed["default_model"] == "kimi-code/test-model"
    assert parsed["extra_skill_dirs"] == []
    assert parsed["telemetry"] is False

    model_table = parsed["models"]["kimi-code/test-model"]
    assert model_table["default_effort"] == "high"
    assert "default_model" not in model_table
    assert "extra_skill_dirs" not in model_table
    assert "telemetry" not in model_table

    provider_table = parsed["providers"]["managed:kimi-code"]
    assert provider_table["type"] == "kimi"
    assert "storage" not in provider_table
    assert "key" not in provider_table
    oauth_table = provider_table["oauth"]
    assert oauth_table["storage"] == "file"
    assert oauth_table["key"] == "oauth/kimi-code"
    assert "type" not in oauth_table
    assert "api_key" not in oauth_table


def test_capabilities_and_support_efforts_land_inside_the_model_table(tmp_path):
    target = tmp_path / "carried-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)
    proc, debate_id, owner_pid, owner_ticks = _build2(target, profile, lane_home)
    assert proc.returncode == 0, proc.stdout + proc.stderr

    with open(target / "config.toml", "rb") as fh:
        parsed = tomllib.load(fh)

    model_table = parsed["models"][PLACEHOLDER_MODEL]
    assert model_table["capabilities"] == [
        "thinking", "always_thinking", "image_in", "tool_use"]
    assert model_table["support_efforts"] == ["low", "high", "max"]
    assert "capabilities" not in parsed
    assert "support_efforts" not in parsed
    assert "capabilities" not in parsed["thinking"]
    assert "support_efforts" not in parsed["thinking"]
    assert "capabilities" not in parsed["providers"]["managed:kimi-code"]

    assert model_table["provider"] == "managed:kimi-code"
    assert model_table["model"] == "test-placeholder-model"
    assert model_table["max_context_size"] == 262144
    assert model_table["display_name"] == "Test Placeholder"

    custody = _parse_custody(proc.stdout)
    _remove2(target, lane_home, debate_id, owner_pid, owner_ticks, custody["nonce"])


def test_effort_is_the_argument_not_the_real_configs_value(tmp_path):
    target = tmp_path / "effort-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)
    proc, debate_id, owner_pid, owner_ticks = _build2(
        target, profile, lane_home, effort="max")
    assert proc.returncode == 0, proc.stdout + proc.stderr

    with open(target / "config.toml", "rb") as fh:
        parsed = tomllib.load(fh)

    model_table = parsed["models"][PLACEHOLDER_MODEL]
    assert model_table["default_effort"] == "max"
    assert model_table["default_effort"] != "low"

    custody = _parse_custody(proc.stdout)
    _remove2(target, lane_home, debate_id, owner_pid, owner_ticks, custody["nonce"])


def test_nothing_outside_the_model_table_is_carried(tmp_path):
    target = tmp_path / "isolation-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)
    proc, debate_id, owner_pid, owner_ticks = _build2(target, profile, lane_home)
    assert proc.returncode == 0, proc.stdout + proc.stderr

    with open(target / "config.toml", "rb") as fh:
        parsed = tomllib.load(fh)

    assert "hooks" not in parsed
    assert "services" not in parsed
    assert list(parsed["models"].keys()) == [PLACEHOLDER_MODEL]
    assert parsed["default_model"] == PLACEHOLDER_MODEL

    custody = _parse_custody(proc.stdout)
    _remove2(target, lane_home, debate_id, owner_pid, owner_ticks, custody["nonce"])


def test_a_missing_model_table_refuses_instead_of_guessing(tmp_path):
    target = tmp_path / "no-table-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)
    proc, *_ = _build2(target, profile, lane_home,
                        model="kimi-code/model-not-in-the-config")
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert "declares no model table" in proc.stdout + proc.stderr
    assert not target.exists()
    assert _lock_status(lane_home)["state"] == "free"


def test_a_missing_real_config_refuses_instead_of_guessing(tmp_path):
    target = tmp_path / "no-config-home"
    profile = _fake_profile(tmp_path, None)
    lane_home = _fake_lane_home(tmp_path)
    proc, *_ = _build2(target, profile, lane_home)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert "no kimi-code config at" in proc.stdout + proc.stderr
    assert not target.exists()
    assert _lock_status(lane_home)["state"] == "free"


def test_an_unparseable_model_table_refuses_instead_of_guessing(tmp_path):
    broken = FAKE_REAL_CONFIG.replace(
        'display_name = "Test Placeholder"',
        "display_name = { first = 'nested inline table' }")
    target = tmp_path / "unparseable-home"
    profile = _fake_profile(tmp_path, broken)
    lane_home = _fake_lane_home(tmp_path)
    proc, *_ = _build2(target, profile, lane_home)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert "unparseable line" in proc.stdout + proc.stderr
    assert not target.exists()
    assert _lock_status(lane_home)["state"] == "free"


def test_a_model_table_without_a_provider_key_refuses(tmp_path):
    without_provider = FAKE_REAL_CONFIG.replace(
        '[models."%s"]\nprovider = "managed:kimi-code"\n' % PLACEHOLDER_MODEL,
        '[models."%s"]\n' % PLACEHOLDER_MODEL)
    target = tmp_path / "no-provider-home"
    profile = _fake_profile(tmp_path, without_provider)
    lane_home = _fake_lane_home(tmp_path)
    proc, *_ = _build2(target, profile, lane_home)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert "carries no provider key" in proc.stdout + proc.stderr
    assert not target.exists()
    assert _lock_status(lane_home)["state"] == "free"


def test_a_model_table_without_a_model_key_refuses(tmp_path):
    without_model = FAKE_REAL_CONFIG.replace(
        '\nmodel = "test-placeholder-model"\n', "\n")
    target = tmp_path / "no-model-home"
    profile = _fake_profile(tmp_path, without_model)
    lane_home = _fake_lane_home(tmp_path)
    proc, *_ = _build2(target, profile, lane_home)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert "carries no model key" in proc.stdout + proc.stderr
    assert not target.exists()
    assert _lock_status(lane_home)["state"] == "free"


def test_a_model_table_naming_an_undeclared_provider_refuses(tmp_path):
    other_provider = FAKE_REAL_CONFIG.replace(
        '[models."%s"]\nprovider = "managed:kimi-code"' % PLACEHOLDER_MODEL,
        '[models."%s"]\nprovider = "managed:some-other-provider"'
        % PLACEHOLDER_MODEL)
    target = tmp_path / "other-provider-home"
    profile = _fake_profile(tmp_path, other_provider)
    lane_home = _fake_lane_home(tmp_path)
    proc, *_ = _build2(target, profile, lane_home)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert "which this home does not declare" in proc.stdout + proc.stderr
    assert not target.exists()
    assert _lock_status(lane_home)["state"] == "free"


def test_an_unreadable_real_config_refuses(tmp_path):
    target = tmp_path / "unreadable-config-home"
    profile = _fake_profile(tmp_path, None)
    (profile / ".kimi-code" / "config.toml").mkdir()
    lane_home = _fake_lane_home(tmp_path)
    proc, *_ = _build2(target, profile, lane_home)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert "could not read" in proc.stdout + proc.stderr
    assert not target.exists()
    assert _lock_status(lane_home)["state"] == "free"


def test_a_duplicate_model_table_refuses(tmp_path):
    duplicated = FAKE_REAL_CONFIG + (
        '\n[models."%s"]\nprovider = "managed:kimi-code"\n'
        'model = "test-placeholder-model"\n' % PLACEHOLDER_MODEL)
    target = tmp_path / "duplicate-table-home"
    profile = _fake_profile(tmp_path, duplicated)
    lane_home = _fake_lane_home(tmp_path)
    proc, *_ = _build2(target, profile, lane_home)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert "more than once" in proc.stdout + proc.stderr
    assert not target.exists()
    assert _lock_status(lane_home)["state"] == "free"


def test_the_fake_credentials_are_structurally_valid(tmp_path):
    """The fixture's own oracle: VALID_CREDENTIAL_JSON must itself pass
    the real validator, or every test above would be exercising nothing."""
    lane_home = _fake_lane_home(tmp_path)
    proc = subprocess.run(
        [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-File", str(CREDENTIAL_VALIDATOR), "-Path",
         str(lane_home / "credentials" / "kimi-code.json")],
        capture_output=True, text=True, timeout=60, env=_clean_env())
    assert proc.returncode == 0, proc.stdout + proc.stderr
    report = json.loads(proc.stdout)
    assert report["status"] == "ok"


# =======================================================================
# Defects 2 (scalar `fields` passes an array check) and 3 (blank lines
# discarded before counting), at the builder's one validator call
# position. A disposable copy of the real builder and lock tool, next to
# a STUB validator, so $PSScriptRoot resolves the stub instead of the
# committed one - the builder itself is never rewritten.
# =======================================================================

STUB_VALIDATOR_SCALAR_FIELDS = (
    "param([string]$Path)\n"
    "Write-Output '{\"status\":\"ok\",\"detail\":\"valid\",\"fields\":\"access_token\"}'\n"
    "exit 0\n"
)
def _stub_validator_with_one_variant_key(variant_key):
    """EXACTLY ONE key varied, the other two canonical. Varying all three
    at once cannot tell "rejects Status" from "rejects any of the three"."""
    keys = {"status": "status", "detail": "detail", "fields": "fields"}
    keys[variant_key] = variant_key.capitalize()
    body = ('{"%s":"ok","%s":"valid","%s":["access_token"]}'
            % (keys["status"], keys["detail"], keys["fields"]))
    return ("param([string]$Path)\n"
            "Write-Output '" + body + "'\n"
            "exit 0\n")
STUB_VALIDATOR_CASE_VARIANT_PAIR = (
    "param([string]$Path)\n"
    "Write-Output '{\"status\":\"OK\",\"detail\":\"Valid\","
    "\"fields\":[\"access_token\"]}'\n"
    "exit 0\n"
)
STUB_VALIDATOR_BLANK_LINE_PADDED = (
    "param([string]$Path)\n"
    '[Console]::Out.Write("`n`n{`"status`":`"ok`",`"detail`":`"valid`",'
    '`"fields`":[`"access_token`"]}`n`n")\n'
    "exit 0\n"
)


def _build_with_stub_validator(target, profile, lane_home, validator_stub_text, tmp_path,
                                model=PLACEHOLDER_MODEL, effort="high", timeout=120):
    disposable = tmp_path / "stub-validator-tools"
    tools_dir = disposable / "tools"
    tools_dir.mkdir(parents=True)
    shutil.copy(str(BUILDER), str(tools_dir / "new-kimi-lane-home.ps1"))
    shutil.copy(str(LOCK_TOOL), str(tools_dir / "kimi-lane-lock.ps1"))
    (tools_dir / "read-kimi-credential-state.ps1").write_text(validator_stub_text, encoding="ascii")
    debate_id = _new_hex32()
    self_pid, self_ticks = _self_owner_identity()
    env = _clean_env(USERPROFILE=str(profile))
    proc = subprocess.run(
        [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-File", str(tools_dir / "new-kimi-lane-home.ps1"), "-Path", str(target),
         "-Model", model, "-Effort", effort,
         "-LaneHome", str(lane_home), "-DebateId", debate_id,
         "-OwnerPid", str(self_pid), "-OwnerStartTicksUtc", str(self_ticks)],
        capture_output=True, text=True, timeout=timeout, env=env)
    return proc, debate_id, self_pid, self_ticks


def test_builder_rejects_scalar_fields_from_the_validator(tmp_path):
    target = tmp_path / "scalar-fields-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)
    proc, debate_id, owner_pid, owner_ticks = _build_with_stub_validator(
        target, profile, lane_home, STUB_VALIDATOR_SCALAR_FIELDS, tmp_path)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert proc.stdout == ""
    assert not target.exists()
    assert _lock_status(lane_home)["state"] == "free"


def test_builder_rejects_blank_line_padded_validator_stdout(tmp_path):
    target = tmp_path / "blank-line-padded-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)
    proc, debate_id, owner_pid, owner_ticks = _build_with_stub_validator(
        target, profile, lane_home, STUB_VALIDATOR_BLANK_LINE_PADDED, tmp_path)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert proc.stdout == ""
    assert not target.exists()
    assert _lock_status(lane_home)["state"] == "free"


@pytest.mark.parametrize("variant_key", ["status", "detail", "fields"])
def test_builder_rejects_case_variant_result_keys(tmp_path, variant_key):
    """The frozen interface is exactly `status`, `detail`, `fields`. The
    pair oracle varies only the VALUES and leaves the property-set
    comparison untested. ONE key at a time."""
    target = tmp_path / ("case-variant-keys-home-" + variant_key)
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)
    proc, debate_id, owner_pid, owner_ticks = _build_with_stub_validator(
        target, profile, lane_home,
        _stub_validator_with_one_variant_key(variant_key), tmp_path)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert proc.stdout == ""
    assert not target.exists()
    assert _lock_status(lane_home)["state"] == "free"


def test_builder_rejects_a_case_variant_verdict_pair(tmp_path):
    """A pairing outside the frozen table is VALIDATOR FAILURE, never a
    credential state. -eq is case-insensitive on this platform, so
    "OK"/"Valid" satisfied the table and the builder then routed on a
    status the table does not contain - and `Status -ne "ok"` accepted it
    as a usable credential."""
    target = tmp_path / "case-variant-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)
    proc, debate_id, owner_pid, owner_ticks = _build_with_stub_validator(
        target, profile, lane_home, STUB_VALIDATOR_CASE_VARIANT_PAIR, tmp_path)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert proc.stdout == ""
    assert not target.exists()
    assert _lock_status(lane_home)["state"] == "free"


def test_builder_capture_read_fault_is_validator_failure(tmp_path):
    """Defect 4: a failed capture read of the validator's own stdout/
    stderr must be validator failure, never empty-stderr-and-proceed. The
    seam deletes the real stderr capture file right before it is read
    (stdout is left genuinely readable, so this cannot be satisfied by a
    coincidental empty-stdout rejection from the defect-3 fix instead),
    producing a genuine Get-Content failure."""
    target = tmp_path / "capture-read-fault-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)
    proc, *_ = _build2(target, profile, lane_home, extra_env={
        "PARALLAX_KIMI_CREDENTIAL_VALIDATOR_CAPTURE_READ_FAULT": "1",
    })
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert proc.stdout == ""
    assert not target.exists()
    assert _lock_status(lane_home)["state"] == "free"


# =======================================================================
# Task 6 Step 1: the new behaviour. Every test below drives the real
# builder (and, where the oracle requires it, the real lock tool
# directly) - no seam substitutes for a real fixture unless the plan
# names one.
# =======================================================================

# The FAIL-CLOSED recovery command (r29 of the plan): a child scriptblock
# setting $ErrorActionPreference = 'Stop' around a try, so every later
# step is structurally unreachable after any failure. Extracted
# byte-for-byte from tools/new-kimi-lane-home.ps1's own
# $RecoveryCommandTemplate (with its PowerShell '' escaping undone) so
# this pin cannot silently drift from the emitting production string.
RECOVERY_COMMAND_TEMPLATE = (
    '& { $ErrorActionPreference = \'Stop\'; try { $ownerLines = @(& \'tools/kimi-lane-lock.ps1\' -ResolveOwner); $ownerExit = $LASTEXITCODE; if ($ownerExit -ne 0) { throw "owner resolution failed with exit $ownerExit" }; if ($ownerLines.Count -ne 1 -or -not ($ownerLines[0] -is [string]) -or [string]::IsNullOrWhiteSpace([string]$ownerLines[0])) { throw \'owner resolution returned invalid output\' }; $owner = $ownerLines[0] | ConvertFrom-Json -ErrorAction Stop; if (-not ($owner -is [System.Management.Automation.PSCustomObject])) { throw \'owner resolution returned invalid schema\' }; $ownerFields = @($owner.PSObject.Properties.Name); if ($ownerFields.Count -ne 2 -or -not ($ownerFields -ccontains \'ownerPid\') -or -not ($ownerFields -ccontains \'ownerStartTicksUtc\') -or -not (($owner.ownerPid -is [int]) -or ($owner.ownerPid -is [long])) -or [long]$owner.ownerPid -le 0 -or -not ($owner.ownerStartTicksUtc -is [string]) -or $owner.ownerStartTicksUtc -notmatch \'\\A[0-9]+\\z\') { throw \'owner resolution returned invalid schema\' }; if ([string]::IsNullOrWhiteSpace($env:TEMP) -or -not (Test-Path -LiteralPath $env:TEMP -PathType Container -ErrorAction Stop)) { throw \'TEMP is not an existing directory\' }; $verdictOut = Join-Path -Path $env:TEMP -ChildPath \'parallax-kimi-lane-login-verdict.json\' -ErrorAction Stop; & \'tools/new-kimi-lane-login.ps1\' -LaneHome \'<lane-home>\' -OwnerPid ([string]$owner.ownerPid) -OwnerStartTicksUtc $owner.ownerStartTicksUtc -VerdictOut $verdictOut; $loginExit = $LASTEXITCODE; if ($loginExit -ne 0) { throw "lane login failed with exit $loginExit" } } catch { throw } }'
)


# The needle the ABSENCE checks below use, taken from the template above
# rather than typed from memory. Four sites used to assert
# `"$ownerJson" not in stderr`, which the r29 rewrite had replaced with
# $ownerLines, so those asserts could not fail whatever the builder
# printed. `test_the_recovery_command_absence_needle_discriminates` holds
# both directions of this needle, so a future template change breaks a
# test instead of silently emptying four others.
RECOVERY_COMMAND_NEEDLE = "$ownerLines = @(& 'tools/kimi-lane-lock.ps1' -ResolveOwner)"


def _expected_recovery_command(resolved_lane_home):
    escaped = resolved_lane_home.replace("'", "''")
    return RECOVERY_COMMAND_TEMPLATE.replace("<lane-home>", escaped)


def _extract_recovery_command(stderr_text):
    m = re.search(r'^& \{ \$ErrorActionPreference.*$', stderr_text, re.MULTILINE)
    assert m, "no recovery command found in stderr: %r" % (stderr_text,)
    return m.group(0)


def _resolved(path):
    """[System.IO.Path]::GetFullPath equivalent for an existing path,
    matching what the builder itself resolves -LaneHome to."""
    return str(Path(path).resolve())


def _file_id(path):
    proc = subprocess.run(["fsutil", "file", "queryfileid", str(path)],
                           capture_output=True, text=True, timeout=30)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return proc.stdout.strip()


def _fake_profile_with_credential(tmp_path, config_text, credential_text,
                                   name="fake-profile-with-cred"):
    profile = _fake_profile(tmp_path, config_text, name=name)
    cred_dir = profile / ".kimi-code" / "credentials"
    cred_dir.mkdir(parents=True, exist_ok=True)
    (cred_dir / "kimi-code.json").write_text(credential_text, encoding="ascii")
    return profile


def _spawn_live_holder():
    """A REAL, alive process to serve as a lock's owner identity - the
    plan requires the acquire-failure/acquire-precedes-validation oracles
    to use a genuine live holder rather than an invented seam, which is
    the stronger oracle."""
    proc = subprocess.Popen(
        [POWERSHELL, "-NoProfile", "-Command", "Start-Sleep -Seconds 120"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ticks = _owner_ticks_for_pid(proc.pid)
    return proc, str(proc.pid), ticks


def _kill_holder(proc):
    try:
        proc.terminate()
        proc.wait(timeout=15)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


# --- The junction oracle: three assertions, each with its own failing
# measurement. ---


def test_the_junction_oracle(tmp_path):
    target = tmp_path / "junction-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)
    proc, debate_id, owner_pid, owner_ticks = _build2(target, profile, lane_home)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    custody = _parse_custody(proc.stdout)

    lane_cred_file = lane_home / "credentials" / "kimi-code.json"
    debate_cred_file = target / "credentials" / "kimi-code.json"

    # 1. File identity is primary: the full NTFS file identity, not a
    # textual resolved path.
    assert _file_id(lane_cred_file) == _file_id(debate_cred_file)

    # 2. Write-through is required: mutate the lane fixture, observe the
    # new bytes through the debate path in the SAME test.
    refreshed = ('{"access_token": "refreshed-access", '
                 '"refresh_token": "refreshed-refresh", "expires_at": 1800}')
    lane_cred_file.write_text(refreshed, encoding="ascii")
    assert debate_cred_file.read_text(encoding="ascii") == refreshed

    # 3. A non-following physical inventory: enumerate the debate home
    # WITHOUT traversing reparse points and assert no standalone
    # credential file exists beneath it. Get-ChildItem -Recurse does not
    # descend into a directory junction by default (measured live) - a
    # standalone copy would be the only way a "kimi-code.json" shows up
    # in this listing.
    inv = subprocess.run(
        [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
         "Get-ChildItem -LiteralPath '%s' -Recurse -Force -File | "
         "Where-Object { $_.Name -eq 'kimi-code.json' } | "
         "ForEach-Object { $_.FullName }" % str(target)],
        capture_output=True, text=True, timeout=60, env=_clean_env())
    assert inv.returncode == 0, inv.stdout + inv.stderr
    assert inv.stdout.strip() == "", (
        "a standalone credential file must not exist beneath the debate "
        "home: found %r" % inv.stdout)

    # The credentials directory itself must be the reparse point.
    attr = subprocess.run(
        [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
         "(Get-Item -LiteralPath '%s' -Force).Attributes" %
         str(target / "credentials")],
        capture_output=True, text=True, timeout=60, env=_clean_env())
    assert "ReparsePoint" in attr.stdout

    _remove2(target, lane_home, debate_id, owner_pid, owner_ticks, custody["nonce"])


def test_custody_json_is_exactly_debate_home_and_nonce(tmp_path):
    target = tmp_path / "custody-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)
    proc, debate_id, owner_pid, owner_ticks = _build2(target, profile, lane_home)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    custody = _parse_custody(proc.stdout)
    assert custody["debateHome"] == str(target.resolve())
    assert re.match(r'\A[0-9a-f]{32}\Z', custody["nonce"])
    _remove2(target, lane_home, debate_id, owner_pid, owner_ticks, custody["nonce"])


def test_removal_uses_the_returned_nonce_a_wrong_one_is_refused(tmp_path):
    target = tmp_path / "wrong-nonce-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)
    proc, debate_id, owner_pid, owner_ticks = _build2(target, profile, lane_home)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    custody = _parse_custody(proc.stdout)

    wrong_nonce = _new_hex32()
    assert wrong_nonce != custody["nonce"]
    bad = _remove2(target, lane_home, debate_id, owner_pid, owner_ticks, wrong_nonce)
    assert bad.returncode != 0, bad.stdout + bad.stderr
    assert target.exists(), "a wrong nonce must not remove the home"
    status = _lock_status(lane_home)
    assert status["state"] == "held"
    assert status["nonce"] == custody["nonce"]

    good = _remove2(target, lane_home, debate_id, owner_pid, owner_ticks, custody["nonce"])
    assert good.returncode == 0, good.stdout + good.stderr
    assert not target.exists()
    assert _lock_status(lane_home)["state"] == "free"


def test_the_credential_source_is_the_lane_home_not_the_user_profile(tmp_path):
    """A planted, DIFFERING user credential under the fake USERPROFILE
    must never be read - the lane home's own credential is the only
    source now."""
    target = tmp_path / "source-home"
    profile = _fake_profile_with_credential(
        tmp_path, FAKE_REAL_CONFIG, DIFFERING_USER_CREDENTIAL_JSON)
    lane_home = _fake_lane_home(tmp_path)
    proc, debate_id, owner_pid, owner_ticks = _build2(target, profile, lane_home)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    custody = _parse_custody(proc.stdout)

    debate_cred = (target / "credentials" / "kimi-code.json").read_text(encoding="ascii")
    assert debate_cred == VALID_CREDENTIAL_JSON
    assert "user-side-token-must-never-be-read" not in debate_cred
    assert "user-side-refresh-must-never-be-read" not in debate_cred

    _remove2(target, lane_home, debate_id, owner_pid, owner_ticks, custody["nonce"])


# --- FIRST USE: the four-row directory probe of the lane home. ---


def test_the_recovery_command_absence_needle_discriminates(tmp_path):
    """BOTH DIRECTIONS of the needle the absence checks rest on. It must be
    present in the shipped template AND in a real emission of the command,
    and absent from a refusal that emits no command. A needle satisfying
    only the absent direction is what four of those checks had: they
    pinned `$ownerJson`, which r29 replaced, so they held whatever the
    builder printed."""
    assert RECOVERY_COMMAND_NEEDLE in RECOVERY_COMMAND_TEMPLATE

    target = tmp_path / "debate-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)

    emitting = tmp_path / "never-created-lane-home"
    proc, *_ = _build2(target, profile, emitting)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert RECOVERY_COMMAND_NEEDLE in proc.stderr, (
        "the needle must appear when the command IS emitted, or every "
        "absence check using it is vacuous")

    silent = tmp_path / "lane-home-is-a-file"
    silent.write_text("not a directory", encoding="ascii")
    proc2, *_ = _build2(tmp_path / "debate-home-2", profile, silent)
    assert proc2.returncode != 0, proc2.stdout + proc2.stderr
    assert RECOVERY_COMMAND_NEEDLE not in proc2.stderr


def test_a_nonexistent_lane_home_refuses_with_the_recovery_command(tmp_path):
    target = tmp_path / "debate-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = tmp_path / "never-created-lane-home"
    assert not lane_home.exists()

    proc, *_ = _build2(target, profile, lane_home)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert proc.stdout == ""
    assert not target.exists()
    assert not lane_home.exists(), "the builder must never create the lane home"

    cmd = _extract_recovery_command(proc.stderr)
    assert cmd == _expected_recovery_command(_resolved_nonexistent(lane_home))


def _resolved_nonexistent(path):
    """os.path.normpath-based GetFullPath equivalent for a path that does
    NOT exist (Path.resolve() on Windows still normalizes a nonexistent
    path with strict=False, matching .NET's GetFullPath, which never
    requires existence either)."""
    return str(Path(path).resolve())


def test_a_regular_file_at_the_lane_home_path_refuses_with_no_recovery_command(tmp_path):
    target = tmp_path / "debate-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = tmp_path / "lane-home-is-a-file"
    lane_home.write_text("not a directory", encoding="ascii")

    proc, *_ = _build2(target, profile, lane_home)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert proc.stdout == ""
    assert RECOVERY_COMMAND_NEEDLE not in proc.stderr
    assert not target.exists()
    # No lock invocation: no lane.lock can appear beside a file, and the
    # file itself is untouched.
    assert lane_home.read_text(encoding="ascii") == "not a directory"


def test_the_directory_probe_fault_seam_produces_the_unmeasurable_row(tmp_path):
    target = tmp_path / "debate-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)

    proc, *_ = _build2(target, profile, lane_home,
                        extra_env={"PARALLAX_LANE_HOME_DIRECTORY_PROBE_FAULT": "1"})
    assert proc.returncode == 6, proc.stdout + proc.stderr
    assert proc.stdout == ""
    assert ("PARALLAX_LANE_HOME_DIRECTORY_PROBE_FAULT injected: simulated "
            "lane-home directory probe failure") in proc.stderr
    assert RECOVERY_COMMAND_NEEDLE not in proc.stderr
    assert not target.exists()
    # No mutation of the (real, existing) lane home's own lock.
    assert _lock_status(lane_home)["state"] == "free"


# --- Absent / unreadable / malformed lane credential: each refuses with
# the recovery command, asserted whole. ---


def test_an_absent_lane_credential_refuses_with_the_recovery_command_acquires_and_releases(tmp_path):
    target = tmp_path / "debate-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path, seed_credential=False)

    proc, *_ = _build2(target, profile, lane_home)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert proc.stdout == ""
    assert not target.exists()

    cmd = _extract_recovery_command(proc.stderr)
    assert cmd == _expected_recovery_command(_resolved(lane_home))

    # Acquired then released: the lane home EXISTED (unlike the
    # nonexistent-row test above), so Acquire ran, and the refusal
    # released it back to free.
    assert _lock_status(lane_home)["state"] == "free"


def test_an_unreadable_lane_credential_refuses_with_the_recovery_command(tmp_path):
    target = tmp_path / "debate-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path, seed_credential=False)
    # A directory standing where the credential file belongs: present but
    # unreadable as bytes.
    (lane_home / "credentials" / "kimi-code.json").mkdir(parents=True)

    proc, *_ = _build2(target, profile, lane_home)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert proc.stdout == ""
    assert not target.exists()

    cmd = _extract_recovery_command(proc.stderr)
    assert cmd == _expected_recovery_command(_resolved(lane_home))
    assert _lock_status(lane_home)["state"] == "free"


def test_a_malformed_lane_credential_refuses_with_the_recovery_command(tmp_path):
    target = tmp_path / "debate-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path, credential_text="not json at all")

    proc, *_ = _build2(target, profile, lane_home)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert proc.stdout == ""
    assert not target.exists()

    cmd = _extract_recovery_command(proc.stderr)
    assert cmd == _expected_recovery_command(_resolved(lane_home))
    assert _lock_status(lane_home)["state"] == "free"


def test_validator_failure_is_not_an_actionable_state(tmp_path):
    """A VALIDATOR FAILURE (the injected PARALLAX_KIMI_CREDENTIAL_STATE_
    FAULT seam already frozen in Task 2's validator) is not one of the
    three actionable states: no recovery command, because nothing was
    measured. The lock is still acquired-then-released."""
    target = tmp_path / "debate-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)

    proc, *_ = _build2(target, profile, lane_home,
                        extra_env={"PARALLAX_KIMI_CREDENTIAL_STATE_FAULT": "1"})
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert proc.stdout == ""
    assert RECOVERY_COMMAND_NEEDLE not in proc.stderr
    assert not target.exists()
    assert _lock_status(lane_home)["state"] == "free"


def test_an_existing_lane_home_with_an_absent_credential_acquires_validates_and_releases(tmp_path):
    """Both directions of the pre-lock/under-lock split: an entirely
    absent lane home (tested above) never touches the lock; an EXISTING
    lane home with an absent credential acquires, validates absent,
    emits the same command, and releases."""
    target = tmp_path / "debate-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path, seed_credential=False)
    assert lane_home.is_dir()

    proc, *_ = _build2(target, profile, lane_home)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    cmd = _extract_recovery_command(proc.stderr)
    assert cmd == _expected_recovery_command(_resolved(lane_home))
    assert _lock_status(lane_home)["state"] == "free"


# --- Successful build retains the lock; a pre-emission failure releases. ---


def test_a_successful_build_retains_the_lock(tmp_path):
    target = tmp_path / "retain-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)
    proc, debate_id, owner_pid, owner_ticks = _build2(target, profile, lane_home)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    custody = _parse_custody(proc.stdout)

    status = _lock_status(lane_home)
    assert status["state"] == "held"
    assert status["nonce"] == custody["nonce"]
    assert status["debateId"] == debate_id

    _remove2(target, lane_home, debate_id, owner_pid, owner_ticks, custody["nonce"])


def test_a_preemission_fault_runs_cleanup_and_releases(tmp_path):
    """The relocated PARALLAX_LANE_HOME_FAULT seam, now firing between
    custody construction and emission. No stdout, the home gone, the
    lock exactly free - proves $buildCompleted is set only after the
    success line is out."""
    target = tmp_path / "preemission-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)

    proc, *_ = _build2(target, profile, lane_home,
                        extra_env={"PARALLAX_LANE_HOME_FAULT": "1"})
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert proc.stdout == ""
    assert "PARALLAX_LANE_HOME_FAULT injected: simulated pre-emission failure" in proc.stderr
    assert not target.exists()
    assert _lock_status(lane_home)["state"] == "free"


def test_an_acquire_failure_does_not_attempt_a_release_and_precedes_validation(tmp_path):
    """A REAL held-by-a-different-owner fixture, the stronger oracle: the
    lane home carries NO credential at all, so if credential validation
    ran before acquisition the failure would be an actionable "absent"
    refusal (recovery command, exit from the validator path). Acquiring
    first means this instead contends and fails BEFORE ever looking at
    the credential - proving both "acquire precedes validation" and
    "acquire failure does not release" (the holder's own record survives
    untouched) in one fixture."""
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path, seed_credential=False)
    target = tmp_path / "contended-home"

    holder_proc, holder_pid, holder_ticks = _spawn_live_holder()
    # Bound BEFORE the try, so a failed acquire does not make the finally
    # raise NameError and bury the real failure. The release is attempted
    # only if the acquire actually produced custody.
    holder_debate_id = _new_hex32()
    holder_nonce = None
    try:
        acquire = _lock_acquire_direct(lane_home, holder_debate_id, holder_pid,
                                        holder_ticks, str(tmp_path / "holder-debate-home"))
        assert acquire.returncode == 0, acquire.stdout + acquire.stderr
        holder_nonce = acquire.stdout.strip()
        before = _lock_status(lane_home)
        assert before["state"] == "held"

        proc, *_ = _build2(target, profile, lane_home)
        assert proc.returncode == 3, proc.stdout + proc.stderr  # lock contention
        assert proc.stdout == ""
        assert RECOVERY_COMMAND_NEEDLE not in proc.stderr, (
            "an absent-credential refusal would have printed the recovery "
            "command; contention must win, proving acquire precedes "
            "validation")
        assert "contended: holder pid %s" % holder_pid in proc.stderr
        assert not target.exists()

        after = _lock_status(lane_home)
        assert after == before, "an acquire failure must never mutate the record"
    finally:
        try:
            if holder_nonce is not None:
                _lock_release_direct(lane_home, holder_debate_id, holder_pid,
                                     holder_ticks, holder_nonce)
        finally:
            _kill_holder(holder_proc)


# --- The reclaim/contention integration oracles for the lock boundary. ---


def test_a_build_reclaiming_a_dead_holder_succeeds(tmp_path):
    target = tmp_path / "reclaim-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)

    dead_pid = "999999"
    dead_ticks = "638000000000000000"
    dead_debate_id = _new_hex32()
    acquire = _lock_acquire_direct(lane_home, dead_debate_id, dead_pid, dead_ticks,
                                    str(tmp_path / "dead-debate-home"))
    assert acquire.returncode == 0, acquire.stdout + acquire.stderr

    proc, debate_id, owner_pid, owner_ticks = _build2(target, profile, lane_home)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "reclaimed a dead holder: pid %s" % dead_pid in proc.stderr
    custody = _parse_custody(proc.stdout)
    assert proc.stdout.strip() == json.dumps(custody, separators=(",", ":"))

    _remove2(target, lane_home, debate_id, owner_pid, owner_ticks, custody["nonce"])


def test_a_build_contending_with_a_live_holder_fails(tmp_path):
    target = tmp_path / "contend-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)

    holder_proc, holder_pid, holder_ticks = _spawn_live_holder()
    # Bound BEFORE the try, so a failed acquire does not make the finally
    # raise NameError and bury the real failure. The release is attempted
    # only if the acquire actually produced custody.
    holder_debate_id = _new_hex32()
    holder_nonce = None
    try:
        acquire = _lock_acquire_direct(lane_home, holder_debate_id, holder_pid,
                                        holder_ticks, str(tmp_path / "holder-debate-home"))
        assert acquire.returncode == 0, acquire.stdout + acquire.stderr
        holder_nonce = acquire.stdout.strip()

        proc, *_ = _build2(target, profile, lane_home)
        assert proc.returncode == 3, proc.stdout + proc.stderr
        assert proc.stdout == ""
        assert "contended: holder pid %s" % holder_pid in proc.stderr
        assert not target.exists()
    finally:
        try:
            if holder_nonce is not None:
                _lock_release_direct(lane_home, holder_debate_id, holder_pid,
                                     holder_ticks, holder_nonce)
        finally:
            _kill_holder(holder_proc)


# --- Cleanup fault seams: delete and release, independently. ---


def test_cleanup_delete_fault_keeps_the_original_failure_primary(tmp_path):
    target = tmp_path / "cleanup-delete-fault-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)

    proc, *_ = _build2(target, profile, lane_home, extra_env={
        "PARALLAX_LANE_HOME_FAULT": "1",
        "PARALLAX_LANE_HOME_CLEANUP_DELETE_FAULT": "1",
    })
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert ("PARALLAX_LANE_HOME_CLEANUP_DELETE_FAULT injected: simulated "
            "cleanup deletion failure") in proc.stderr
    assert target.exists(), "the debate home must remain on disk when its cleanup deletion is skipped"
    assert _lock_status(lane_home)["state"] == "free", (
        "the release must still be attempted, and succeed, even though cleanup deletion was skipped")

    shutil.rmtree(target, ignore_errors=True)


def test_cleanup_release_fault_keeps_the_original_failure_primary(tmp_path):
    target = tmp_path / "cleanup-release-fault-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)

    proc, debate_id, owner_pid, owner_ticks = _build2(target, profile, lane_home, extra_env={
        "PARALLAX_LANE_HOME_FAULT": "1",
        "PARALLAX_LANE_HOME_CLEANUP_RELEASE_FAULT": "1",
    })
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert ("PARALLAX_LANE_HOME_CLEANUP_RELEASE_FAULT injected: simulated "
            "cleanup release refusal") in proc.stderr
    assert not target.exists(), "deletion is unaffected by the release-only seam"

    status = _lock_status(lane_home)
    assert status["state"] == "held", "the release was skipped, so the record stays held"
    assert status["debateId"] == debate_id

    _lock_release_direct(lane_home, debate_id, owner_pid, owner_ticks, status["nonce"])


# =======================================================================
# Remove order, frozen.
# =======================================================================


def _lock_file_bytes(lane_home):
    return (lane_home / "lane.lock").read_bytes()


def test_removes_identity_mismatch_leaves_home_and_lock_byte_identical(tmp_path):
    target = tmp_path / "mismatch-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)
    proc, debate_id, owner_pid, owner_ticks = _build2(target, profile, lane_home)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    custody = _parse_custody(proc.stdout)

    lock_before = _lock_file_bytes(lane_home)
    sentinel_before = (target / SENTINEL).read_bytes()

    wrong_debate_id = _new_hex32()
    assert wrong_debate_id != debate_id
    bad = _remove2(target, lane_home, wrong_debate_id, owner_pid, owner_ticks, custody["nonce"])
    assert bad.returncode != 0, bad.stdout + bad.stderr

    assert target.exists()
    assert (target / SENTINEL).read_bytes() == sentinel_before
    assert _lock_file_bytes(lane_home) == lock_before

    _remove2(target, lane_home, debate_id, owner_pid, owner_ticks, custody["nonce"])


def test_the_wrong_path_oracle(tmp_path):
    """Frozen six-step setup, using only the real builder. Building B
    while A holds the lock would contend and never reach the case, so B's
    lock is released directly after B is built, before A is built."""
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)
    home_a = tmp_path / "home-a"
    home_b = tmp_path / "home-b"

    # 1. Build B normally and capture its nonce.
    proc_b, debate_b, pid_b, ticks_b = _build2(home_b, profile, lane_home)
    assert proc_b.returncode == 0, proc_b.stdout + proc_b.stderr
    custody_b = _parse_custody(proc_b.stdout)

    # 2. Directly -Release B's lock, leaving B on disk.
    rel_b = _lock_release_direct(lane_home, debate_b, pid_b, ticks_b, custody_b["nonce"])
    assert rel_b.returncode == 0, rel_b.stdout + rel_b.stderr
    assert home_b.exists()

    # 3. Build A normally, retaining A's hold.
    proc_a, debate_a, pid_a, ticks_a = _build2(home_a, profile, lane_home)
    assert proc_a.returncode == 0, proc_a.stdout + proc_a.stderr
    custody_a = _parse_custody(proc_a.stdout)

    lock_before = _lock_file_bytes(lane_home)
    a_sentinel_before = (home_a / SENTINEL).read_bytes()
    b_sentinel_before = (home_b / SENTINEL).read_bytes()

    # 4. Call -Remove on B carrying A's complete identity and A's nonce.
    wrong_path_attempt = _remove2(home_b, lane_home, debate_a, pid_a, ticks_a, custody_a["nonce"])

    # 5. Require exit 2 and byte-identical A, B and lock.
    assert wrong_path_attempt.returncode == 2, (
        wrong_path_attempt.stdout + wrong_path_attempt.stderr)
    assert home_a.exists() and home_b.exists()
    assert (home_a / SENTINEL).read_bytes() == a_sentinel_before
    assert (home_b / SENTINEL).read_bytes() == b_sentinel_before
    assert _lock_file_bytes(lane_home) == lock_before

    # 6. Tear down: remove A normally, then acquire a fresh hold for B
    # and remove B normally.
    teardown_a = _remove2(home_a, lane_home, debate_a, pid_a, ticks_a, custody_a["nonce"])
    assert teardown_a.returncode == 0, teardown_a.stdout + teardown_a.stderr
    assert _lock_status(lane_home)["state"] == "free"

    fresh = _lock_acquire_direct(lane_home, debate_b, pid_b, ticks_b, str(home_b))
    assert fresh.returncode == 0, fresh.stdout + fresh.stderr
    fresh_nonce = fresh.stdout.strip()
    teardown_b = _remove2(home_b, lane_home, debate_b, pid_b, ticks_b, fresh_nonce)
    assert teardown_b.returncode == 0, teardown_b.stdout + teardown_b.stderr
    assert not home_b.exists()


def test_a_sentinel_refusal_after_identity_check_leaves_home_and_lock_unchanged(tmp_path):
    target = tmp_path / "sentinel-refusal-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)
    proc, debate_id, owner_pid, owner_ticks = _build2(target, profile, lane_home)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    custody = _parse_custody(proc.stdout)

    # Corrupt the sentinel AFTER the identity the lock knows about (the
    # lock's own -DebateHome is unaffected by this) - the lock identity
    # check (step 1) will still succeed against this same -Path, so the
    # sentinel guard (step 2) is what refuses.
    (target / SENTINEL).write_text("not the real sentinel", encoding="ascii")
    lock_before = _lock_file_bytes(lane_home)

    proc2 = _remove2(target, lane_home, debate_id, owner_pid, owner_ticks, custody["nonce"])
    assert proc2.returncode != 0, proc2.stdout + proc2.stderr
    assert "sentinel does not match this path" in proc2.stdout + proc2.stderr
    assert target.exists()
    assert _lock_file_bytes(lane_home) == lock_before
    assert _lock_status(lane_home)["state"] == "held"

    # Repair the sentinel and clean up for real.
    (target / SENTINEL).write_text("\n".join(["PARALLAX-LANE-HOME-V1", str(target.resolve())]),
                                    encoding="ascii")
    _remove2(target, lane_home, debate_id, owner_pid, owner_ticks, custody["nonce"])


def test_the_remove_verify_fault_seam_leaves_the_lock_held(tmp_path):
    target = tmp_path / "remove-verify-fault-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)
    proc, debate_id, owner_pid, owner_ticks = _build2(target, profile, lane_home)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    custody = _parse_custody(proc.stdout)

    proc2 = _remove2(target, lane_home, debate_id, owner_pid, owner_ticks, custody["nonce"],
                      extra_env={"PARALLAX_LANE_HOME_REMOVE_VERIFY_FAULT": "1"})
    assert proc2.returncode == 6, proc2.stdout + proc2.stderr
    assert proc2.stdout == ""
    assert ("PARALLAX_LANE_HOME_REMOVE_VERIFY_FAULT injected: simulated "
            "post-delete verification failure") in proc2.stderr
    # The deletion itself already happened (the fault fires AFTER
    # deletion, BEFORE verification) - the home is genuinely gone.
    assert not target.exists()
    assert _lock_status(lane_home)["state"] == "held"

    _lock_release_direct(lane_home, debate_id, owner_pid, owner_ticks, custody["nonce"])


def test_the_remove_release_fault_seam_is_failure_capable(tmp_path):
    target = tmp_path / "remove-release-fault-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)
    proc, debate_id, owner_pid, owner_ticks = _build2(target, profile, lane_home)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    custody = _parse_custody(proc.stdout)

    proc2 = _remove2(target, lane_home, debate_id, owner_pid, owner_ticks, custody["nonce"],
                      extra_env={"PARALLAX_LANE_HOME_REMOVE_RELEASE_FAULT": "1"})
    assert proc2.returncode == 5, proc2.stdout + proc2.stderr
    assert proc2.stdout == ""
    assert ("PARALLAX_LANE_HOME_REMOVE_RELEASE_FAULT injected: simulated "
            "post-delete release refusal") in proc2.stderr
    assert not target.exists()
    status = _lock_status(lane_home)
    assert status["state"] == "held"
    assert status["nonce"] == custody["nonce"]

    _lock_release_direct(lane_home, debate_id, owner_pid, owner_ticks, custody["nonce"])


def test_remove_does_not_delete_through_the_junction(tmp_path):
    target = tmp_path / "remove-no-follow-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)
    proc, debate_id, owner_pid, owner_ticks = _build2(target, profile, lane_home)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    custody = _parse_custody(proc.stdout)

    proc2 = _remove2(target, lane_home, debate_id, owner_pid, owner_ticks, custody["nonce"])
    assert proc2.returncode == 0, proc2.stdout + proc2.stderr
    assert not target.exists()
    # The lane home's own credential survives the debate home's removal.
    assert (lane_home / "credentials" / "kimi-code.json").exists()
    assert (lane_home / "credentials" / "kimi-code.json").read_text(
        encoding="ascii") == VALID_CREDENTIAL_JSON


def test_failed_build_cleanup_does_not_delete_through_the_junction(tmp_path):
    target = tmp_path / "cleanup-no-follow-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)

    # The junction is created before the PARALLAX_LANE_HOME_FAULT seam
    # fires (it fires right before custody emission, well after step 5's
    # junction creation), so this failed build's own cleanup deletion
    # exercises the same "does not follow" requirement.
    proc, *_ = _build2(target, profile, lane_home,
                        extra_env={"PARALLAX_LANE_HOME_FAULT": "1"})
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert not target.exists()
    assert (lane_home / "credentials" / "kimi-code.json").exists()
    assert (lane_home / "credentials" / "kimi-code.json").read_text(
        encoding="ascii") == VALID_CREDENTIAL_JSON
    assert _lock_status(lane_home)["state"] == "free"


def test_the_deletion_failure_oracle_is_real(tmp_path):
    """An exclusively opened file beneath the debate home blocks the
    TERMINATING delete: nonzero, the home still present, no success
    line, and the lock still held. Teardown is frozen: close the handle,
    release DIRECTLY using the retained identity, then delete the
    disposable remainder outside the behaviour under test."""
    target = tmp_path / "deletion-failure-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)
    proc, debate_id, owner_pid, owner_ticks = _build2(target, profile, lane_home)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    custody = _parse_custody(proc.stdout)

    held_file = target / "_held.txt"
    held_file.write_text("held", encoding="ascii")
    ready_signal = tmp_path / "holder-ready"
    release_signal = tmp_path / "holder-release"
    holder_script = tmp_path / "holder.ps1"
    holder_script.write_text(
        "param($Path, $ReadySignal, $ReleaseSignal)\n"
        "$fs = [System.IO.File]::Open($Path, [System.IO.FileMode]::Open, "
        "[System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::Read)\n"
        "New-Item -ItemType File -Path $ReadySignal -Force | Out-Null\n"
        "while (-not (Test-Path -LiteralPath $ReleaseSignal)) { Start-Sleep -Milliseconds 100 }\n"
        "$fs.Close()\n",
        encoding="ascii")

    holder = subprocess.Popen(
        [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
         str(holder_script), "-Path", str(held_file),
         "-ReadySignal", str(ready_signal), "-ReleaseSignal", str(release_signal)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=_clean_env())
    try:
        deadline = time.time() + 20
        while not ready_signal.exists():
            assert time.time() < deadline, "holder process never signalled ready"
            time.sleep(0.1)

        proc2 = _remove2(target, lane_home, debate_id, owner_pid, owner_ticks, custody["nonce"])
        assert proc2.returncode != 0, proc2.stdout + proc2.stderr
        assert "removed " not in proc2.stdout
        assert target.exists()
        status = _lock_status(lane_home)
        assert status["state"] == "held"
        assert status["nonce"] == custody["nonce"]
    finally:
        release_signal.write_text("go", encoding="ascii")
        holder.wait(timeout=20)
        _lock_release_direct(lane_home, debate_id, owner_pid, owner_ticks, custody["nonce"])
        shutil.rmtree(target, ignore_errors=True)


# =======================================================================
# Step 1b: the recovery command is EXECUTED, not just string-compared.
# NINE rows (r29 of the plan): three dependent boundaries was itself an
# under-count. Owner LAUNCH failure, output cardinality, owner SCHEMA and
# the environment the command reads were all unexercised before, and the
# old parse row asserted "never invoked" while the shipped command
# actually invoked the login with a null identity - fixed now by running
# the whole command inside a child scriptblock that sets
# $ErrorActionPreference = 'Stop' around a try (see
# tools/new-kimi-lane-home.ps1's $RecoveryCommandTemplate). Every row
# BEFORE the login launch asserts the login was NEVER invoked by MARKER
# ABSENCE, not merely a nonzero exit.
# =======================================================================

OWNER_STUB_NONZERO = (
    "param([switch]$ResolveOwner)\n"
    '[Console]::Error.WriteLine("stub: owner resolution refused")\n'
    "exit 2\n"
)
OWNER_STUB_ZERO_LINES = (
    "param([switch]$ResolveOwner)\n"
    "exit 0\n"
)
OWNER_STUB_MULTIPLE_LINES = (
    "param([switch]$ResolveOwner)\n"
    'Write-Output "line-one"\n'
    'Write-Output "line-two"\n'
    "exit 0\n"
)
OWNER_STUB_MALFORMED_JSON = (
    "param([switch]$ResolveOwner)\n"
    'Write-Output "not-json-at-all"\n'
    "exit 0\n"
)
OWNER_STUB_NOT_OBJECT = (
    "param([switch]$ResolveOwner)\n"
    "Write-Output '[1,2,3]'\n"
    "exit 0\n"
)
OWNER_STUB_MISSING_FIELD = (
    "param([switch]$ResolveOwner)\n"
    "Write-Output '{\"ownerPid\": 4321}'\n"
    "exit 0\n"
)
OWNER_STUB_EXTRA_FIELD = (
    "param([switch]$ResolveOwner)\n"
    "Write-Output '{\"ownerPid\": 4321, \"ownerStartTicksUtc\": \"123456789\", \"extra\": \"x\"}'\n"
    "exit 0\n"
)
OWNER_STUB_WRONG_PID_TYPE = (
    "param([switch]$ResolveOwner)\n"
    "Write-Output '{\"ownerPid\": \"4321\", \"ownerStartTicksUtc\": \"123456789\"}'\n"
    "exit 0\n"
)
OWNER_STUB_PID_ZERO = (
    "param([switch]$ResolveOwner)\n"
    "Write-Output '{\"ownerPid\": 0, \"ownerStartTicksUtc\": \"123456789\"}'\n"
    "exit 0\n"
)
OWNER_STUB_PID_NEGATIVE = (
    "param([switch]$ResolveOwner)\n"
    "Write-Output '{\"ownerPid\": -5, \"ownerStartTicksUtc\": \"123456789\"}'\n"
    "exit 0\n"
)
OWNER_STUB_WRONG_TICKS_TYPE = (
    "param([switch]$ResolveOwner)\n"
    "Write-Output '{\"ownerPid\": 4321, \"ownerStartTicksUtc\": 123456789}'\n"
    "exit 0\n"
)
OWNER_STUB_TICKS_NON_DIGIT = (
    "param([switch]$ResolveOwner)\n"
    "Write-Output '{\"ownerPid\": 4321, \"ownerStartTicksUtc\": \"12a456789\"}'\n"
    "exit 0\n"
)
OWNER_STUB_VALID_JSON = (
    "param([switch]$ResolveOwner)\n"
    "Write-Output '{\"ownerPid\": 4321, \"ownerStartTicksUtc\": \"123456789\"}'\n"
    "exit 0\n"
)
LOGIN_STUB_MARK_AND_FAIL = (
    "param([string]$LaneHome, [string]$OwnerPid, [string]$OwnerStartTicksUtc, "
    "[string]$VerdictOut, [switch]$Force)\n"
    'Set-Content -LiteralPath (Join-Path $PSScriptRoot "login-invoked.marker") '
    '-Value "invoked" -Encoding ascii\n'
    "exit 6\n"
)


def _disposable_tools_cwd(tmp_path, name, owner_stub_text, login_stub_text):
    """owner_stub_text=None omits tools/kimi-lane-lock.ps1 entirely (row
    1's launch-failure fixture); login_stub_text=None likewise omits
    tools/new-kimi-lane-login.ps1 (row 7's)."""
    disposable = tmp_path / name
    tools_dir = disposable / "tools"
    tools_dir.mkdir(parents=True)
    if owner_stub_text is not None:
        (tools_dir / "kimi-lane-lock.ps1").write_text(owner_stub_text, encoding="ascii")
    if login_stub_text is not None:
        (tools_dir / "new-kimi-lane-login.ps1").write_text(login_stub_text, encoding="ascii")
    return disposable, tools_dir


def _get_recovery_command_for(tmp_path, lane_home_name):
    """Drive the REAL builder against a nonexistent lane home to obtain
    an authentic, builder-emitted recovery command."""
    target = tmp_path / ("extraction-debate-home-" + lane_home_name)
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG, name="extraction-profile-" + lane_home_name)
    lane_home = tmp_path / lane_home_name
    proc, *_ = _build2(target, profile, lane_home)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    return _extract_recovery_command(proc.stderr)


def _run_recovery_row(tmp_path, row, owner_stub_text, login_stub_text=LOGIN_STUB_MARK_AND_FAIL,
                       omit_temp=False, temp_override=None):
    """temp_override, when given, is used verbatim as $env:TEMP (a
    nonexistent path or a path to a regular file). omit_temp removes the
    variable entirely. Neither is a fixture-shaping workaround: both are
    the row 6 sub-cases the plan's own table names."""
    cmd_text = _get_recovery_command_for(tmp_path, "stub-row-lane-home-" + row)
    disposable, tools_dir = _disposable_tools_cwd(
        tmp_path, "disposable-" + row, owner_stub_text, login_stub_text)
    fake_profile_dir = tmp_path / ("run-profile-" + row)
    fake_profile_dir.mkdir()
    env = _clean_env(USERPROFILE=str(fake_profile_dir))
    if omit_temp:
        env.pop("TEMP", None)
        env.pop("TMP", None)
    elif temp_override is not None:
        env["TEMP"] = str(temp_override)
    else:
        temp_dir = tmp_path / ("run-temp-" + row)
        temp_dir.mkdir(parents=True, exist_ok=True)
        env["TEMP"] = str(temp_dir)
    run = subprocess.run(
        [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd_text],
        capture_output=True, text=True, timeout=60, env=env, cwd=str(disposable))
    marker = tools_dir / "login-invoked.marker"
    return run, marker


def test_the_recovery_command_row1_owner_launch_failure(tmp_path):
    """Row 1: the owner command has no tools/kimi-lane-lock.ps1 to run at
    all. PowerShell's own CommandNotFoundException is terminating
    regardless of $ErrorActionPreference, so it is caught by the outer
    try/catch: nonzero, login stub never invoked."""
    run, marker = _run_recovery_row(tmp_path, "owner_launch_fail", owner_stub_text=None)
    assert run.returncode != 0, run.stdout + run.stderr
    assert not marker.exists()


def test_the_recovery_command_row2_owner_command_nonzero(tmp_path):
    """Row 2: the owner command itself exits nonzero. The command's own
    `if ($ownerExit -ne 0) { throw ... }` guard is an explicit `throw`,
    which reliably halts the rest of the try - confirmed live: exit
    nonzero, login stub never invoked."""
    run, marker = _run_recovery_row(tmp_path, "owner_nonzero", OWNER_STUB_NONZERO)
    assert run.returncode != 0, run.stdout + run.stderr
    assert not marker.exists()


@pytest.mark.parametrize("label,stub", [
    ("zero_lines", OWNER_STUB_ZERO_LINES),
    ("multiple_lines", OWNER_STUB_MULTIPLE_LINES),
])
def test_the_recovery_command_row3_owner_stdout_cardinality(tmp_path, label, stub):
    """Row 3: owner stdout is zero lines, or several - both directions,
    since a two-row oracle would leave one of them unexercised. The
    command's own `if ($ownerLines.Count -ne 1 -or ...) { throw ... }`
    guard catches both."""
    run, marker = _run_recovery_row(tmp_path, "owner_cardinality_" + label, stub)
    assert run.returncode != 0, run.stdout + run.stderr
    assert not marker.exists()


def test_the_recovery_command_row4_owner_json_malformed(tmp_path):
    """Row 4: owner stdout is malformed JSON.

    LIVE-VERIFIED FIX: the plan's PREVIOUS command (r20/r21) had this
    exact `$owner = $ownerJson | ConvertFrom-Json -ErrorAction Stop` with
    NO surrounding try/catch and no `$ErrorActionPreference = 'Stop'`
    anywhere in the one-liner, so the ConvertFrom-Json terminating error
    was promoted only for its OWN pipeline statement and the chain
    continued - the login stub ran with a null identity, reproduced live
    on both hosts. The r29 replacement wraps the whole command in a
    child scriptblock that sets $ErrorActionPreference = 'Stop' around a
    try, so this same ConvertFrom-Json failure now IS caught by the
    outer catch before the login stub is ever reached - reproduced live
    on both hosts as part of this task's fix: nonzero, login never
    invoked, no verdict, no credential mutation."""
    run, marker = _run_recovery_row(tmp_path, "owner_malformed_json", OWNER_STUB_MALFORMED_JSON)
    assert run.returncode != 0, run.stdout + run.stderr
    assert not marker.exists(), (
        "the login stub must never be invoked once the owner JSON fails to "
        "parse - the previous command's own bug, now fixed")


@pytest.mark.parametrize("label,stub", [
    ("not_object", OWNER_STUB_NOT_OBJECT),
    ("missing_field", OWNER_STUB_MISSING_FIELD),
    ("extra_field", OWNER_STUB_EXTRA_FIELD),
    ("wrong_pid_type", OWNER_STUB_WRONG_PID_TYPE),
    ("pid_zero", OWNER_STUB_PID_ZERO),
    ("pid_negative", OWNER_STUB_PID_NEGATIVE),
    ("wrong_ticks_type", OWNER_STUB_WRONG_TICKS_TYPE),
    ("ticks_non_digit", OWNER_STUB_TICKS_NON_DIGIT),
])
def test_the_recovery_command_row5_owner_schema(tmp_path, label, stub):
    """Row 5: owner JSON is valid but the wrong shape - not an object,
    wrong property set (missing or extra), wrong pid type, a pid <= 0,
    wrong ticks type, or ticks failing \\A[0-9]+\\z. Every sub-case must
    independently fail closed: nonzero, login never invoked."""
    run, marker = _run_recovery_row(tmp_path, "owner_schema_" + label, stub)
    assert run.returncode != 0, run.stdout + run.stderr
    assert not marker.exists()


@pytest.mark.parametrize("label", ["temp_unset", "temp_nonexistent", "temp_is_a_file"])
def test_the_recovery_command_row6_temp_unusable(tmp_path, label):
    """Row 6: TEMP missing or not a directory. (A SEPARATE forced
    Join-Path failure is not independently constructible without mocking
    the cmdlet itself: once the command's own preceding check confirms
    $env:TEMP exists and is a container, Join-Path -ChildPath with a
    fixed, safe literal child name cannot fail on either host - the
    guard that would need to fail has already run.) Every sub-case:
    nonzero, login never invoked."""
    if label == "temp_unset":
        run, marker = _run_recovery_row(tmp_path, "temp_unset", OWNER_STUB_VALID_JSON,
                                         omit_temp=True)
    elif label == "temp_nonexistent":
        run, marker = _run_recovery_row(
            tmp_path, "temp_nonexistent", OWNER_STUB_VALID_JSON,
            temp_override=tmp_path / "does-not-exist-temp")
    else:  # temp_is_a_file
        temp_as_file = tmp_path / "temp-is-a-file.txt"
        temp_as_file.write_text("not a directory", encoding="ascii")
        run, marker = _run_recovery_row(tmp_path, "temp_is_a_file", OWNER_STUB_VALID_JSON,
                                         temp_override=temp_as_file)
    assert run.returncode != 0, run.stdout + run.stderr
    assert not marker.exists()


def test_the_recovery_command_row7_login_launch_failure(tmp_path):
    """Row 7: owner resolution succeeds, but tools/new-kimi-lane-login.ps1
    does not exist to run. PowerShell's CommandNotFoundException is
    terminating, caught by the outer try/catch: nonzero."""
    run, marker = _run_recovery_row(tmp_path, "login_launch_fail", OWNER_STUB_VALID_JSON,
                                     login_stub_text=None)
    assert run.returncode != 0, run.stdout + run.stderr


def test_the_recovery_command_row8_login_nonzero(tmp_path):
    """Row 8: owner resolution succeeds with valid JSON; the login stub
    is invoked and fails. The command's third statement's explicit
    `throw` on the login's own nonzero $LASTEXITCODE reliably surfaces
    as the overall command's failure, and no `ok` verdict is ever
    written because the stub never writes one."""
    run, marker = _run_recovery_row(tmp_path, "login_nonzero", OWNER_STUB_VALID_JSON)
    assert run.returncode != 0, run.stdout + run.stderr
    assert marker.exists(), "the login stub must be invoked once owner resolution is valid"


def test_the_recovery_command_row9_full_success_with_apostrophe_and_space(tmp_path):
    """Row 9, and the escaping's own failure direction: every row above
    could pass with an ordinary path, which would let an implementation
    that never doubles apostrophes pass all of them. The SUCCESS row
    therefore uses a resolved lane home containing BOTH AN APOSTROPHE AND
    A SPACE IN THE SAME PATH SEGMENT - the apostrophe exercises the
    <lane-home> template's single-quote doubling, the space exercises
    tools/new-kimi-lane-login.ps1's own Start-Process argument quoting
    for the credential validator (fixed by this same task). An earlier
    fixture deliberately avoided combining the two characters; a fixture
    may not be shaped to avoid a defect in code it drives."""
    lane_home_name = "o'learys lane home"
    cmd_text = _get_recovery_command_for(tmp_path, lane_home_name)
    assert "o''learys lane home" in cmd_text, cmd_text

    disposable = tmp_path / "disposable-success"
    tools_dir = disposable / "tools"
    tools_dir.mkdir(parents=True)
    for name in ["kimi-lane-lock.ps1", "new-kimi-lane-login.ps1", "read-kimi-credential-state.ps1"]:
        shutil.copy(str(REPO / "tools" / name), str(tools_dir / name))

    lane_home = tmp_path / lane_home_name
    (lane_home / "credentials").mkdir(parents=True)
    (lane_home / "credentials" / "kimi-code.json").write_text(
        VALID_CREDENTIAL_JSON, encoding="ascii")

    fake_profile_dir = tmp_path / "success-run-profile"
    fake_profile_dir.mkdir()
    temp_dir = tmp_path / "success-run-temp"
    temp_dir.mkdir()
    env = _clean_env(USERPROFILE=str(fake_profile_dir), TEMP=str(temp_dir))

    run = subprocess.run(
        [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", cmd_text],
        capture_output=True, text=True, timeout=60, env=env, cwd=str(disposable))
    assert run.returncode == 0, run.stdout + run.stderr

    verdict_path = temp_dir / "parallax-kimi-lane-login-verdict.json"
    assert verdict_path.exists()
    verdict = json.loads(verdict_path.read_text(encoding="ascii"))
    assert verdict["status"] == "ok"

    # Writes only to the intended lane home: no OTHER credential file
    # was created anywhere under the disposable run profile.
    assert not (fake_profile_dir / ".kimi-code" / "credentials" / "kimi-code.json").exists()


# ---------------------------------------------------------------------
# 0.20.0: the builder's skills-directory POSTCONDITION.
#
# The reopened debate established that the builder's own New-Item is the
# ONLY site in this repository that writes to <debate-home>/skills, so
# there is no shipped writer and no per-round check is warranted. These
# cases therefore prove the DETECTOR fires for the reason it claims -
# never that the shipped lane can reach the state it detects. Presenting
# them as threat evidence would be a claim wider than its evidence, and
# that is why the seam exists rather than a fixture that pre-seeds the
# directory: the check has to run against content that appeared AFTER
# creation, which is the only moment it can legitimately catch.
# ---------------------------------------------------------------------


def test_build_asserts_its_skills_directory_is_empty(tmp_path):
    """A plain file planted between creation and the check must abort."""
    target = tmp_path / "seeded-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)

    proc, *_ = _build2(target, profile, lane_home,
                       extra_env={"PARALLAX_SKILLS_SEED_FILE": "1"})
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert "skills directory is not empty after creation" in proc.stderr
    assert not target.exists()
    assert _lock_status(lane_home)["state"] == "free"


def test_build_asserts_against_a_hidden_entry(tmp_path):
    """-Force, or the check is blind to the one intruder most worth
    catching. Watched SEPARATELY from the visible case, because a check
    that sees a plain file and not a hidden one passes the obvious test
    and fails the real one - the same -Force gap the canary harness was
    bitten by at mutations N3 and N4."""
    target = tmp_path / "hidden-seeded-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)

    proc, *_ = _build2(target, profile, lane_home,
                       extra_env={"PARALLAX_SKILLS_SEED_HIDDEN": "1"})
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert "skills directory is not empty after creation" in proc.stderr
    assert not target.exists()
    assert _lock_status(lane_home)["state"] == "free"


def test_the_postcondition_refuses_before_emitting_custody_json(tmp_path):
    """A refusal that has already printed the custody nonce hands the
    caller a home it must release and must not trust. Nothing on stdout
    is the assertion; a nonzero exit alone would pass either way."""
    target = tmp_path / "custody-order-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)

    proc, *_ = _build2(target, profile, lane_home,
                       extra_env={"PARALLAX_SKILLS_SEED_FILE": "1"})
    assert proc.returncode != 0
    assert proc.stdout == "", proc.stdout


def test_a_clean_build_still_succeeds_with_an_empty_skills_dir(tmp_path):
    """The POSITIVE CONTROL, and it is not optional: without it every
    case above is satisfied by a builder that refuses unconditionally."""
    target = tmp_path / "clean-postcondition-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    lane_home = _fake_lane_home(tmp_path)

    proc, debate_id, owner_pid, owner_ticks = _build2(target, profile, lane_home)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    custody = json.loads(accept_exactly_one_nonempty_line(proc.stdout))
    assert custody["debateHome"]
    skills = target / "skills"
    assert skills.is_dir()
    assert list(skills.iterdir()) == []
    _remove2(target, lane_home, debate_id, owner_pid, owner_ticks,
             custody["nonce"])


def test_the_postcondition_seam_is_declared_in_the_builder():
    """The seams are part of the tool's contract, not test scaffolding
    someone may delete as dead code."""
    body = _read(BUILDER)
    assert "PARALLAX_SKILLS_SEED_FILE" in body
    assert "PARALLAX_SKILLS_SEED_HIDDEN" in body
    assert "skills directory is not empty after creation" in body
    assert "skills directory could not be enumerated after creation" in body
