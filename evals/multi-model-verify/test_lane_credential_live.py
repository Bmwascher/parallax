"""Live gates for the junction and credential facts (Task 7, 2026-08-01
lane-credential-and-lock plan).

Opt-in on PARALLAX_LANE_LIVE (unset: this whole module SKIPS - that is
the one legitimate skip in this file). Windows only. Once opted in, EVERY
setup failure below FAILS the gate rather than skipping it: "an unmade,
failed, or unreadable measurement is never a clean one... a live gate
whose setup fails is a FAILED gate, never a skipped branch."

This module drives the REAL kimi-code client against three dedicated
lane homes the operator provisions by hand (PARALLAX_LANE_LIVE_HOME_A/B/C
- see the manual setup sequence in the plan). It never touches the
user's own ~/.kimi-code credential and never creates a login itself; a
missing or unusable home fails the suite naming
tools/new-kimi-lane-login.ps1, the recovery tool.
"""
import importlib.util as _importlib_util
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
_SUPPORT_MODULE_PATH = REPO / "evals" / "tools" / "lane_credential_live_support.py"


def _load_support():
    if "lane_credential_live_support" not in sys.modules:
        spec = _importlib_util.spec_from_file_location(
            "lane_credential_live_support", _SUPPORT_MODULE_PATH)
        module = _importlib_util.module_from_spec(spec)
        sys.modules["lane_credential_live_support"] = module
        spec.loader.exec_module(module)
    return sys.modules["lane_credential_live_support"]


support = _load_support()

PROBE_RECORD = (REPO / "docs" / "superpowers" / "plans" / "rounds"
                 / "2026-08-01-cred-lock" / "probe-record.md")

DISPATCH_PROMPT = "Reply with the single word PROBE."

pytestmark = pytest.mark.skipif(
    not os.environ.get(support.ENV_LIVE_OPT_IN) or os.name != "nt",
    reason="opt-in on PARALLAX_LANE_LIVE; this gate drives the real "
           "kimi-code client and is Windows-only")


# =======================================================================
# Module-scoped setup. Every failure here is pytest.fail, never
# pytest.skip - the opt-in above is the only legitimate skip in this file.
# =======================================================================
@pytest.fixture(scope="module")
def host():
    resolved = support.resolve_ps_host()
    if resolved is None:
        pytest.fail(
            "no PowerShell host resolved (PARALLAX_PS_HOST unset and "
            "neither powershell nor pwsh is on PATH); a live gate whose "
            "setup fails is a failed gate, never a skipped branch")
    return resolved


@pytest.fixture(scope="module")
def module_owner(host):
    try:
        return support.resolve_owner(host)
    except support.OwnerResolutionError as exc:
        pytest.fail(str(exc))


@pytest.fixture(scope="module")
def live_homes(host):
    try:
        return support.resolve_and_validate_live_homes(host)
    except support.LiveSetupError as exc:
        pytest.fail(str(exc))


@pytest.fixture(scope="module")
def backup_model():
    try:
        return support.read_canonical_backup_model()
    except support.ModelNotesReadError as exc:
        pytest.fail(str(exc))


@pytest.fixture(scope="module")
def backup_effort():
    try:
        return support.read_canonical_backup_effort()
    except support.ModelNotesReadError as exc:
        pytest.fail(str(exc))


@pytest.fixture(scope="module")
def kimi_binary():
    # Global Constraint: "the client binary is ~/.kimi-code/bin/kimi.exe,
    # always by ABSOLUTE PATH."
    profile = os.environ.get("USERPROFILE")
    if not profile:
        pytest.fail("USERPROFILE is not set; cannot resolve the client binary")
    path = Path(profile) / ".kimi-code" / "bin" / "kimi.exe"
    if not path.is_file():
        pytest.fail("client binary not found at %s" % path)
    return str(path)


@pytest.fixture(scope="module")
def guard(host, module_owner, live_homes):
    """The seed step: the sole direct-acquire exception to builder
    custody. Seeds the retained secret union from A, B and C - locked,
    one at a time - before any live command runs. Item 6's disposable
    homes are merged separately, without a lock, at their own point."""
    g = support.SecretGuard()
    for home in (live_homes.a, live_homes.b, live_homes.c):
        debate_id = support.new_hex32()
        with support.seed_hold(host, home, debate_id, module_owner.owner_pid,
                                module_owner.owner_ticks):
            merged = g.merge_credential_file(home / "credentials" / "kimi-code.json")
            if not merged:
                pytest.fail("could not read/merge the credential at %s during seeding" % home)
    return g


# =======================================================================
# Small shared helpers.
# =======================================================================
def _dispatch_probe(kimi_binary, model, debate_home, guard, timeout=180):
    args = [kimi_binary, "-m", model, "--skills-dir", str(Path(debate_home) / "skills"),
            "-p", DISPATCH_PROMPT]
    env = support.clean_env({"KIMI_CODE_HOME": str(debate_home)})
    return support.dispatch_and_guard(args, guard, timeout=timeout,
                                       cwd=str(debate_home), env=env)


def _provider_list(kimi_binary, debate_home, guard, timeout=60):
    args = [kimi_binary, "provider", "list"]
    env = support.clean_env({"KIMI_CODE_HOME": str(debate_home)})
    return support.dispatch_and_guard(args, guard, timeout=timeout,
                                       cwd=str(debate_home), env=env)


def _credential_path(debate_home):
    return Path(debate_home) / "credentials" / "kimi-code.json"


def _force_expiry(debate_home):
    """Pre-command mutation: rewrite `expires_at` to a clearly-past epoch
    value, IN PLACE, writing through the junction to the lane home's own
    file - the ONLY deliberate credential mutation in this suite, and it
    happens under builder custody per the frozen pre-command-phase rule."""
    cred_path = _credential_path(debate_home)
    obj = json.loads(cred_path.read_text(encoding="utf-8"))
    obj["expires_at"] = 1
    cred_path.write_text(json.dumps(obj), encoding="utf-8")


def _no_standalone_credential_file(host, debate_home):
    """Get-ChildItem -Recurse does not descend into a directory JUNCTION
    by default (measured live, test_kimi_lane_home.py's own junction
    oracle) - a standalone copy would be the only way a second
    kimi-code.json shows up in this listing."""
    proc = subprocess.run(
        [host, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command",
         "Get-ChildItem -LiteralPath '%s' -Recurse -Force -File | "
         "Where-Object { $_.Name -eq 'kimi-code.json' } | "
         "ForEach-Object { $_.FullName }" % str(debate_home)],
        capture_output=True, text=True, timeout=60, env=support.clean_env())
    if proc.returncode != 0:
        pytest.fail("junction inventory check failed: %s" % (proc.stdout + proc.stderr))
    return proc.stdout.strip() == ""


def _build_disposable_home(tmp_path, name, credential_text):
    """Item 6 ONLY: an isolated, disposable home built by hand, outside
    the lock/builder pipeline entirely (routing table: custody NONE - no
    real credential exists to protect). The real ~/.kimi-code/config.toml
    is copied verbatim so `provider list` has a real provider/model table
    to read; nothing here ever runs a dispatch through it."""
    profile = os.environ.get("USERPROFILE")
    real_config = Path(profile) / ".kimi-code" / "config.toml"
    if not real_config.is_file():
        pytest.fail("no real config.toml at %s for item 6's disposable homes" % real_config)
    home = tmp_path / name
    home.mkdir(parents=True)
    (home / "config.toml").write_text(real_config.read_text(encoding="utf-8"), encoding="utf-8")
    (home / "skills").mkdir()
    if credential_text is not None:
        cred_dir = home / "credentials"
        cred_dir.mkdir()
        (cred_dir / "kimi-code.json").write_text(credential_text, encoding="utf-8")
    return home


# =======================================================================
# Item 1 (measurement 5): absolute oauth.key. Junction-based control on
# C, then the same throwaway copy with config.toml hand-edited so
# `key = "oauth/kimi-code"` becomes an absolute path.
# =======================================================================
def test_absolute_oauth_key_does_not_resolve(tmp_path, host, module_owner, live_homes,
                                              backup_model, backup_effort, kimi_binary, guard):
    target = tmp_path / "item1-absolute-key-home"
    with support.custody_of(host, target, backup_model, backup_effort, live_homes.c,
                             support.new_hex32(), module_owner.owner_pid,
                             module_owner.owner_ticks) as custody:
        debate_home = custody.debate_home

        # Positive control: the SAME credential and config, unmodified.
        control = _dispatch_probe(kimi_binary, backup_model, debate_home, guard)
        assert control.returncode == 0, control.stderr
        assert "PROBE" in control.stdout
        support.reread_and_merge_credential(guard, _credential_path(debate_home))

        # Hand-edit config.toml: the rendered relative key becomes an
        # absolute path to the same credential file.
        config_path = Path(debate_home) / "config.toml"
        original_config = config_path.read_text(encoding="ascii")
        absolute_key = str(_credential_path(debate_home).resolve()).replace("\\", "/")
        edited_config = original_config.replace(
            'key = "oauth/kimi-code"', 'key = "%s"' % absolute_key)
        assert edited_config != original_config, "the relative key line was not found to edit"
        config_path.write_text(edited_config, encoding="ascii")

        fixture_root = str(Path(debate_home).resolve())

        def _run_once():
            result = _dispatch_probe(kimi_binary, backup_model, debate_home, guard)
            norm_stdout = support.normalize_probe_output(result.stdout, fixture_root)
            norm_stderr = support.normalize_probe_output(result.stderr, fixture_root)
            return result.returncode, norm_stdout, norm_stderr

        exit1, stdout1, stderr1 = _run_once()
        assert exit1 != 0, "the absolute oauth.key case must fail"
        exit2, stdout2, stderr2 = _run_once()
        assert exit2 != 0

        if stderr1 != stderr2:
            pytest.fail(
                "the absolute-key failure message is not stable across two runs; "
                "STOP and amend the plan rather than selecting one:\nrun 1: %r\nrun 2: %r"
                % (stderr1, stderr2))

        PROBE_RECORD.parent.mkdir(parents=True, exist_ok=True)
        PROBE_RECORD.write_text(
            "# Live probe record: absolute oauth.key rejection\n\n"
            "Measured %s against the real kimi-code client on this machine "
            "(Task 7, 2026-08-01 lane-credential-and-lock plan, item 1 / "
            "measurement 5).\n\n"
            "- Exit code: `%d`\n"
            "- Normalization: the resolved fixture root replaced with "
            "`<fixture-root>` (case-insensitive), CRLF normalized to LF, "
            "one terminal newline trimmed.\n\n"
            "## Normalized stdout\n\n```\n%s\n```\n\n"
            "## Normalized stderr (the pinned value)\n\n```\n%s\n```\n"
            % (datetime.now(timezone.utc).isoformat(), exit1, stdout1, stderr1),
            encoding="utf-8")


# =======================================================================
# Item 2 (measurement 6): junction read-through, on C.
# =======================================================================
def test_junction_read_through(tmp_path, host, module_owner, live_homes,
                                backup_model, backup_effort, kimi_binary, guard):
    target = tmp_path / "item2-junction-home"
    with support.custody_of(host, target, backup_model, backup_effort, live_homes.c,
                             support.new_hex32(), module_owner.owner_pid,
                             module_owner.owner_ticks) as custody:
        result = _dispatch_probe(kimi_binary, backup_model, custody.debate_home, guard)
        assert result.returncode == 0, result.stderr
        assert "PROBE" in result.stdout
        support.reread_and_merge_credential(guard, _credential_path(custody.debate_home))


# =======================================================================
# Item 3 (measurement 7): refresh write-through, on C. Force expiry in
# the pre-command phase, dispatch, require success, then assert both
# token fields rotated (never disclosed) and no second credential file
# exists anywhere under the debate home.
# =======================================================================
def test_refresh_write_through(tmp_path, host, module_owner, live_homes,
                                backup_model, backup_effort, kimi_binary, guard):
    target = tmp_path / "item3-refresh-home"
    with support.custody_of(host, target, backup_model, backup_effort, live_homes.c,
                             support.new_hex32(), module_owner.owner_pid,
                             module_owner.owner_ticks) as custody:
        debate_home = custody.debate_home
        cred_path = _credential_path(debate_home)

        # Pre-command phase: the ONLY deliberate mutation, under custody.
        before = json.loads(cred_path.read_text(encoding="utf-8"))
        _force_expiry(debate_home)

        result = _dispatch_probe(kimi_binary, backup_model, debate_home, guard)
        assert result.returncode == 0, result.stderr
        assert "PROBE" in result.stdout

        after = json.loads(cred_path.read_text(encoding="utf-8"))
        support.reread_and_merge_credential(guard, cred_path)

        # Token-rotation assertions must not disclose: an ordinary `if` +
        # pytest.fail, never `assert x != y` (which prints both operands
        # through pytest's introspection on failure).
        if before["access_token"] == after["access_token"]:
            pytest.fail("access_token did not rotate")
        if before["refresh_token"] == after["refresh_token"]:
            pytest.fail("refresh_token did not rotate")

        assert _no_standalone_credential_file(host, debate_home)


# =======================================================================
# Item 4 (measurement 10): both delete paths, exercised directly.
# =======================================================================
def test_the_successful_delete_path(tmp_path, host, module_owner, live_homes,
                                     backup_model, backup_effort):
    target = tmp_path / "item4a-delete-home"
    with support.custody_of(host, target, backup_model, backup_effort, live_homes.c,
                             support.new_hex32(), module_owner.owner_pid,
                             module_owner.owner_ticks):
        assert target.exists()
    assert not target.exists()
    assert support.lock_status(host, live_homes.c)["state"] == "free"


def test_the_failed_build_cleanup_path(tmp_path, host, module_owner, live_homes,
                                        backup_effort, monkeypatch):
    """A hostile -Effort (carries a double quote) is refused by the
    builder's own SafeConfigToken gate before anything is rendered - a
    REAL refusal, not an injected seam. No nonce is ever returned, so
    -Remove must never be called on this path; Task 6's own internal
    cleanup already released the lock."""
    target = tmp_path / "item4b-failed-build-home"
    called_remove = []
    monkeypatch.setattr(support, "remove_lane_home",
                         lambda *a, **k: called_remove.append(1) or pytest.fail(
                             "-Remove must never be called after a refused build"))

    with pytest.raises(support.BuildRefusal):
        with support.custody_of(host, target, "kimi-code/hostile\"-model",
                                 backup_effort, live_homes.c, support.new_hex32(),
                                 module_owner.owner_pid, module_owner.owner_ticks):
            pytest.fail("the build was refused; the with-block body must never run")

    assert called_remove == []
    assert not target.exists()
    assert support.lock_status(host, live_homes.c)["state"] == "free"


# =======================================================================
# Item 5 (measurement 11): coexistence, narrowed to what a
# pre-provisioned fixture supports. The claim is "A remains usable after
# B was created", not "the creation of B was observed to be harmless" -
# this test dispatches A, then B, then A again, each requiring exit 0,
# after asserting A's marker precedes B's.
# =======================================================================
def test_coexistence_a_then_b_then_a(tmp_path, host, module_owner, live_homes,
                                      backup_model, backup_effort, kimi_binary, guard):
    assert int(live_homes.marker_a) < int(live_homes.marker_b), (
        "A's login-created marker must precede B's")

    for round_index, home in enumerate((live_homes.a, live_homes.b, live_homes.a)):
        target = tmp_path / ("item5-coexist-home-%d" % round_index)
        with support.custody_of(host, target, backup_model, backup_effort, home,
                                 support.new_hex32(), module_owner.owner_pid,
                                 module_owner.owner_ticks) as custody:
            result = _dispatch_probe(kimi_binary, backup_model, custody.debate_home, guard)
            assert result.returncode == 0, result.stderr
            assert "PROBE" in result.stdout
            support.reread_and_merge_credential(guard, _credential_path(custody.debate_home))


# =======================================================================
# Item 6 (measurement 16): `provider list` false positives. Isolated
# disposable homes, no lock, no real credential.
# =======================================================================
def test_provider_list_false_positive_garbage_credential(tmp_path, host, kimi_binary, guard):
    home = _build_disposable_home(tmp_path, "item6-garbage-home",
                                   credential_text="not valid json at all")
    result = _provider_list(kimi_binary, home, guard)
    assert result.returncode == 0, result.stderr
    assert "source=oauth" in result.stdout
    # Re-read and merge WITHOUT a lock: no hold to keep in force for a
    # disposable, unlocked home. A parse failure here is expected and
    # harmless - the lenient merge simply finds nothing to add.
    guard.merge_credential_file(home / "credentials" / "kimi-code.json")


def test_provider_list_false_positive_absent_credential(tmp_path, host, kimi_binary, guard):
    home = _build_disposable_home(tmp_path, "item6-absent-home", credential_text=None)
    result = _provider_list(kimi_binary, home, guard)
    assert result.returncode == 0, result.stderr
    assert "source=oauth" in result.stdout
    guard.merge_credential_file(home / "credentials" / "kimi-code.json")


# =======================================================================
# Item 7 (measurement 17): `provider list` is not a refresh path, on C.
# Force expiry and take the pre-command snapshot inside the SAME
# pre-command phase; require exit 0 and the expected provider line; then
# require byte-identity by SHA-256, length AND mtime, each measured
# successfully before the comparison ever runs.
# =======================================================================
def test_provider_list_is_not_a_refresh_path(tmp_path, host, module_owner, live_homes,
                                              backup_model, backup_effort, kimi_binary, guard):
    target = tmp_path / "item7-provider-list-home"
    with support.custody_of(host, target, backup_model, backup_effort, live_homes.c,
                             support.new_hex32(), module_owner.owner_pid,
                             module_owner.owner_ticks) as custody:
        debate_home = custody.debate_home
        cred_path = _credential_path(debate_home)

        _force_expiry(debate_home)
        pre_snapshot = support.measure_file_snapshot(cred_path)

        result = _provider_list(kimi_binary, debate_home, guard)
        assert result.returncode == 0, result.stderr
        assert "source=oauth" in result.stdout

        support.reread_and_merge_credential(guard, cred_path)
        post_snapshot = support.measure_file_snapshot(cred_path)

        assert pre_snapshot == post_snapshot, (
            "`provider list` must never mutate the credential file: "
            "pre=%r post=%r" % (pre_snapshot, post_snapshot))
