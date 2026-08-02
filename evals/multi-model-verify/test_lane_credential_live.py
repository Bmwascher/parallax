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
def debate_ids():
    """One debate id PER HOME for the WHOLE MODULE RUN, not per operation
    (packet "One debate id PER HOME for the whole module run"): resolved
    once and used for seeding AND for every later operation against that
    home."""
    return {"A": support.new_hex32(), "B": support.new_hex32(), "C": support.new_hex32()}


@pytest.fixture(scope="module")
def guard(host, module_owner, live_homes, debate_ids):
    """The seed step: the sole direct-acquire exception to builder
    custody. Seeds the retained secret union from A, B and C - locked,
    one at a time - before any live command runs. Item 6's disposable
    homes are merged separately, without a lock, at their own point."""
    g = support.SecretGuard()
    for label, home in (("A", live_homes.a), ("B", live_homes.b), ("C", live_homes.c)):
        with support.seed_hold(host, home, debate_ids[label], module_owner.owner_pid,
                                module_owner.owner_ticks):
            merged = g.merge_credential_file(home / "credentials" / "kimi-code.json")
            if not merged:
                pytest.fail("could not read/merge the credential at %s during seeding" % home)
    return g


# =======================================================================
# Small shared helpers.
# =======================================================================
def _dispatch_probe(kimi_binary, model, debate_home, guard, timeout=180, post_capture_merge=None):
    args = [kimi_binary, "-m", model, "--skills-dir", str(Path(debate_home) / "skills"),
            "-p", DISPATCH_PROMPT]
    env = support.clean_env({"KIMI_CODE_HOME": str(debate_home)})
    return support.dispatch_and_guard(args, guard, timeout=timeout,
                                       cwd=str(debate_home), env=env,
                                       post_capture_merge=post_capture_merge)


def _provider_list(kimi_binary, debate_home, guard, timeout=60, post_capture_merge=None):
    args = [kimi_binary, "provider", "list"]
    env = support.clean_env({"KIMI_CODE_HOME": str(debate_home)})
    return support.dispatch_and_guard(args, guard, timeout=timeout,
                                       cwd=str(debate_home), env=env,
                                       post_capture_merge=post_capture_merge)


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
    try:
        return support.no_standalone_credential_file(host, debate_home)
    except support.PhysicalInventoryError as exc:
        pytest.fail(str(exc))


# Item 6's MINIMAL GENERATED config (r31): only the non-secret managed
# Kimi provider and OAuth declaration `provider list` needs - the
# builder's own provider block (tools/new-kimi-lane-home.ps1:867-874) is
# already explicit and credential-free, so this mirrors that block
# exactly rather than copying the user's real ~/.kimi-code/config.toml,
# which can carry lifecycle hooks and is unrelated to what this check
# exercises.
_ITEM6_MINIMAL_CONFIG = (
    '[providers."managed:kimi-code"]\n'
    'type = "kimi"\n'
    'api_key = ""\n'
    'base_url = "https://api.kimi.com/coding/v1"\n'
    '\n'
    '[providers."managed:kimi-code".oauth]\n'
    'storage = "file"\n'
    'key = "oauth/kimi-code"\n'
)

# The structurally valid FAKE credential for item 6's positive control -
# never a real token.
_ITEM6_VALID_CREDENTIAL_JSON = (
    '{"access_token": "item6-fake-access-token-not-real", '
    '"refresh_token": "item6-fake-refresh-token-not-real", '
    '"expires_at": 9999999999}')


def _build_disposable_home(tmp_path, name, credential_text):
    """Item 6 ONLY: an isolated, disposable home built by hand, outside
    the lock/builder pipeline entirely (routing table: custody NONE - no
    real credential exists to protect)."""
    home = tmp_path / name
    home.mkdir(parents=True)
    (home / "config.toml").write_text(_ITEM6_MINIMAL_CONFIG, encoding="ascii")
    (home / "skills").mkdir()
    if credential_text is not None:
        cred_dir = home / "credentials"
        cred_dir.mkdir()
        (cred_dir / "kimi-code.json").write_text(credential_text, encoding="utf-8")
    return home


# =======================================================================
# Item 1 (measurement 5): absolute oauth.key. FIVE-STEP three-state
# STRUCTURAL oracle, frozen at r33, replacing the r31 pin protocol
# entirely. NOTHING about message text is pinned: the client's stderr
# carries a model-generated summary line (different words each run) and a
# fresh session id that no normalization removes, so a text pin can never
# be stable for this command. What IS pinned: zero-versus-nonzero exit,
# and the presence or absence of PROBE in stdout - never the exact
# numeric exit code, stdout or stderr text, the session id, or the
# summary line.
#
# All five steps run under C's SAME builder-retained hold, with the
# strict merge callback and the stream guard applied throughout. No
# second credential copy is ever created; C's real credential is used in
# place. The home is built normally and its config.toml is hand-edited in
# the throwaway copy for steps 3 and 4 - the builder renders only the
# relative form and gains no parameter for an absolute one.
# =======================================================================
def test_absolute_oauth_key_structural_oracle(tmp_path, host, module_owner, live_homes,
                                               backup_model, backup_effort, kimi_binary, guard,
                                               debate_ids):
    target = tmp_path / "item1-absolute-key-home"
    with support.custody_of(host, target, backup_model, backup_effort, live_homes.c,
                             debate_ids["C"], module_owner.owner_pid,
                             module_owner.owner_ticks) as custody:
        debate_home = custody.debate_home
        cred_path = _credential_path(debate_home)
        merge = support.strict_reread_and_merge_callback(guard, cred_path)
        # C's real credential file, by LANE HOME rather than by the
        # debate home's (soon-to-be-renamed-away) junction - once step 2
        # renames the debate home's `credentials` directory, re-reading
        # through `cred_path` can no longer succeed, but the real file
        # this whole test is about stays exactly here regardless.
        real_cred_path = live_homes.c / "credentials" / "kimi-code.json"
        merge_real = support.strict_reread_and_merge_callback(guard, real_cred_path)

        # Step 1: the relative-key positive control, unmodified.
        step1 = _dispatch_probe(kimi_binary, backup_model, debate_home, guard,
                                 post_capture_merge=merge)
        assert step1.returncode == 0, "step 1 (relative-key control) must exit 0"
        assert "PROBE" in step1.stdout, "step 1 (relative-key control) must contain PROBE"

        # Step 2: make the default UNREACHABLE. Rename the `credentials`
        # junction (tools/new-kimi-lane-home.ps1:858) to a non-default
        # name, then PROVE the default path is absent while C's real
        # credential is still measurable through the renamed junction -
        # renaming a reparse point is a local directory-entry operation
        # and does not touch what it points at.
        credentials_dir = Path(debate_home) / "credentials"
        renamed_name = "credentials-renamed-away"
        renamed_dir = Path(debate_home) / renamed_name
        escaped_credentials = str(credentials_dir).replace("'", "''")
        rename = subprocess.run(
            [host, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command",
             "Rename-Item -LiteralPath '%s' -NewName '%s'" % (escaped_credentials, renamed_name)],
            capture_output=True, text=True, timeout=30, env=support.clean_env())
        assert rename.returncode == 0, "renaming the credentials junction away failed"

        default_cred_path = credentials_dir / "kimi-code.json"
        assert not default_cred_path.exists(), (
            "the default credential path must be unreachable once the "
            "credentials junction is renamed away")
        renamed_cred_path = renamed_dir / "kimi-code.json"
        assert renamed_cred_path.is_file(), (
            "the renamed junction must still resolve to a real file")
        still_readable = support.validate_credential(host, real_cred_path)
        assert still_readable.ok and still_readable.status == "ok", (
            "C's real credential must still be readable after the debate "
            "home's junction was renamed away")

        # Step 3: the missing-absolute negative control. Load-bearing:
        # without it, removing the default and testing one absolute path
        # cannot distinguish "absolute paths are unsupported" from
        # unrelated fallback behaviour.
        config_path = Path(debate_home) / "config.toml"
        original_config = config_path.read_text(encoding="ascii")
        nonexistent_absolute = str(
            tmp_path / "item1-does-not-exist-anywhere" / "kimi-code.json").replace("\\", "/")
        missing_config = original_config.replace(
            'key = "oauth/kimi-code"', 'key = "%s"' % nonexistent_absolute)
        assert missing_config != original_config, "the relative key line was not found to edit"
        config_path.write_text(missing_config, encoding="ascii")

        step3 = _dispatch_probe(kimi_binary, backup_model, debate_home, guard,
                                 post_capture_merge=merge_real)
        assert step3.returncode != 0, (
            "step 3 (missing-absolute negative control) must exit nonzero")
        assert "PROBE" not in step3.stdout, (
            "step 3 (missing-absolute negative control) must not contain PROBE")

        # Step 4: oauth.key set to the absolute path of C's REAL
        # credential file, taken WITHOUT Path.resolve() - resolve()
        # FOLLOWS a junction on Windows, which is what made the old
        # oracle undiscriminating. Run TWICE; either success REFUTES
        # measurement 5, and that is the finding, not a test to work
        # around.
        real_absolute = str(real_cred_path).replace("\\", "/")
        real_config = original_config.replace(
            'key = "oauth/kimi-code"', 'key = "%s"' % real_absolute)
        assert real_config != original_config, "the relative key line was not found to edit"
        config_path.write_text(real_config, encoding="ascii")

        for run_index in (1, 2):
            step4 = _dispatch_probe(kimi_binary, backup_model, debate_home, guard,
                                     post_capture_merge=merge_real)
            found_probe = "PROBE" in step4.stdout
            if step4.returncode == 0 or found_probe:
                pytest.fail(
                    "MEASUREMENT 5 IS REFUTED on run %d of 2: an absolute "
                    "oauth.key pointed at C's real credential file "
                    "resolved (exit-zero=%s, PROBE-present=%s). This is a "
                    "finding, not a test defect - do not adjust the test "
                    "to make it pass."
                    % (run_index, step4.returncode == 0, found_probe))

        # Step 5: C's credential stays measurable and guarded after every
        # command.
        final_check = support.validate_credential(host, real_cred_path)
        assert final_check.ok and final_check.status == "ok", (
            "C's credential must still be structurally measurable after "
            "every command in this test")
        assert guard.merge_credential_file(real_cred_path), (
            "C's credential must still be readable and mergeable into "
            "the secret guard after every command in this test")


# =======================================================================
# Item 2 (measurement 6): junction read-through, on C.
# =======================================================================
def test_junction_read_through(tmp_path, host, module_owner, live_homes,
                                backup_model, backup_effort, kimi_binary, guard, debate_ids):
    target = tmp_path / "item2-junction-home"
    with support.custody_of(host, target, backup_model, backup_effort, live_homes.c,
                             debate_ids["C"], module_owner.owner_pid,
                             module_owner.owner_ticks) as custody:
        result = _dispatch_probe(
            kimi_binary, backup_model, custody.debate_home, guard,
            post_capture_merge=support.strict_reread_and_merge_callback(
                guard, _credential_path(custody.debate_home)))
        assert result.returncode == 0, result.stderr
        assert "PROBE" in result.stdout


# =======================================================================
# Item 3 (measurement 7): refresh write-through, on C. Force expiry in
# the pre-command phase, dispatch, require success, then assert both
# token fields rotated (never disclosed) and no second credential file
# exists anywhere under the debate home.
# =======================================================================
def test_refresh_write_through(tmp_path, host, module_owner, live_homes,
                                backup_model, backup_effort, kimi_binary, guard, debate_ids):
    target = tmp_path / "item3-refresh-home"
    with support.custody_of(host, target, backup_model, backup_effort, live_homes.c,
                             debate_ids["C"], module_owner.owner_pid,
                             module_owner.owner_ticks) as custody:
        debate_home = custody.debate_home
        cred_path = _credential_path(debate_home)

        # Pre-command phase: the ONLY deliberate mutation, under custody.
        before = json.loads(cred_path.read_text(encoding="utf-8"))
        _force_expiry(debate_home)

        result = _dispatch_probe(
            kimi_binary, backup_model, debate_home, guard,
            post_capture_merge=support.strict_reread_and_merge_callback(guard, cred_path))
        assert result.returncode == 0, result.stderr
        assert "PROBE" in result.stdout

        after = json.loads(cred_path.read_text(encoding="utf-8"))

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
                                     backup_model, backup_effort, debate_ids):
    target = tmp_path / "item4a-delete-home"
    with support.custody_of(host, target, backup_model, backup_effort, live_homes.c,
                             debate_ids["C"], module_owner.owner_pid,
                             module_owner.owner_ticks):
        assert target.exists()
    assert not target.exists()
    assert support.lock_status(host, live_homes.c)["state"] == "free"


# =======================================================================
# Item 4b, three cases (frozen at r32). A hostile -Model is refused at
# tools/new-kimi-lane-home.ps1:613, which is INSIDE the main try and AFTER
# the acquire at line 573 - so it proves acquisition and release, but it
# never reaches the deletion branch at all: $createdByThisInvocation is
# set only at line 828, long after that refusal, and the recursive
# cleanup at line 927 is conditional on it. The two cases below exercise
# the real deletion branch instead, using the seams
# PARALLAX_LANE_HOME_FAULT (line 909, immediately before the custody line
# is emitted) and PARALLAX_LANE_HOME_CLEANUP_DELETE_FAULT (line 928,
# inside the catch's cleanup branch). All three cases use the module's
# debate id for C, like every other operation against C.
# =======================================================================
def test_the_failed_build_cleanup_path_deletion_fault_leaves_home_present(
        tmp_path, host, module_owner, live_homes, backup_model, backup_effort, debate_ids):
    """PARALLAX_LANE_HOME_FAULT alone already proves the catch branch
    runs; this case additionally faults the recursive delete itself, so
    the delete branch is reached but never actually deletes anything -
    proving the build genuinely reached the post-junction cleanup branch,
    with the debate home and its real junction still on disk to show for
    it, and the lock released back to free."""
    target = tmp_path / "item4b-delete-fault-home"
    env = support.clean_env({"PARALLAX_LANE_HOME_FAULT": "1",
                              "PARALLAX_LANE_HOME_CLEANUP_DELETE_FAULT": "1"})
    build = support.build_lane_home(host, target, backup_model, backup_effort, live_homes.c,
                                     debate_ids["C"], module_owner.owner_pid,
                                     module_owner.owner_ticks, env=env)

    assert build.returncode != 0
    assert build.nonce is None
    assert "PARALLAX_LANE_HOME_FAULT injected: simulated pre-emission failure" in build.stderr
    assert ("PARALLAX_LANE_HOME_CLEANUP_DELETE_FAULT injected: simulated cleanup "
            "deletion failure") in build.stderr

    assert target.exists(), "the deletion fault must leave the debate home on disk"
    assert support.is_junction(host, target / "credentials"), (
        "the debate home's credentials directory must still be the real junction")
    assert support.lock_status(host, live_homes.c)["state"] == "free"


def test_the_failed_build_cleanup_path_deletion_does_not_traverse_the_junction(
        tmp_path, host, module_owner, live_homes, backup_model, backup_effort, debate_ids):
    """PARALLAX_LANE_HOME_FAULT alone: no deletion fault this time, so the
    catch branch's ordinary recursive Remove-Item runs for real. Requiring
    the debate home ABSENT and C's credential BYTE-IDENTICAL together is
    what proves the recursive delete does not traverse the junction into
    the lane home's own credentials directory."""
    target = tmp_path / "item4b-pre-emission-fault-home"
    cred_path = live_homes.c / "credentials" / "kimi-code.json"
    before = cred_path.read_bytes()

    env = support.clean_env({"PARALLAX_LANE_HOME_FAULT": "1"})
    build = support.build_lane_home(host, target, backup_model, backup_effort, live_homes.c,
                                     debate_ids["C"], module_owner.owner_pid,
                                     module_owner.owner_ticks, env=env)

    assert build.returncode != 0
    assert build.nonce is None
    assert build.stdout == "", "no custody line may be emitted after the pre-emission fault"

    assert not target.exists(), "with no deletion fault, the real delete must run"
    assert support.lock_status(host, live_homes.c)["state"] == "free"

    after = cred_path.read_bytes()
    assert after == before, (
        "the recursive delete must not traverse the credentials junction "
        "and delete C's real credential file")


def test_the_hostile_model_release_only_control(tmp_path, host, module_owner, live_homes,
                                                  backup_effort, debate_ids, monkeypatch):
    """OPTIONAL release-only control. A hostile -Model (carries a double
    quote) is refused by the builder's own SafeConfigToken gate before
    anything is rendered - a REAL refusal, not an injected seam. This
    proves acquisition and release ONLY: the refusal happens before
    $createdByThisInvocation is ever set, so it never reaches the
    deletion branch the two cases above exist to exercise. No nonce is
    ever returned, so -Remove must never be called on this path; Task 6's
    own internal cleanup already released the lock."""
    target = tmp_path / "item4b-hostile-model-control-home"
    called_remove = []
    monkeypatch.setattr(support, "remove_lane_home",
                         lambda *a, **k: called_remove.append(1) or pytest.fail(
                             "-Remove must never be called after a refused build"))

    with pytest.raises(support.BuildRefusal):
        with support.custody_of(host, target, "kimi-code/hostile\"-model",
                                 backup_effort, live_homes.c, debate_ids["C"],
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
                                      backup_model, backup_effort, kimi_binary, guard,
                                      debate_ids):
    assert int(live_homes.marker_a) < int(live_homes.marker_b), (
        "A's login-created marker must precede B's")

    rounds = (("A", live_homes.a), ("B", live_homes.b), ("A", live_homes.a))
    for round_index, (label, home) in enumerate(rounds):
        target = tmp_path / ("item5-coexist-home-%d" % round_index)
        with support.custody_of(host, target, backup_model, backup_effort, home,
                                 debate_ids[label], module_owner.owner_pid,
                                 module_owner.owner_ticks) as custody:
            result = _dispatch_probe(
                kimi_binary, backup_model, custody.debate_home, guard,
                post_capture_merge=support.strict_reread_and_merge_callback(
                    guard, _credential_path(custody.debate_home)))
            assert result.returncode == 0, result.stderr
            assert "PROBE" in result.stdout


# =======================================================================
# Item 6 (measurement 16): `provider list` false positives. Isolated
# disposable homes, no lock, no real credential. The positive control
# (a structurally VALID fake credential) runs first, so the garbage/
# absent cases below can be read as "provider list reports source=oauth
# for these too" - the false positive - rather than as an unexplained
# baseline.
#
# Frozen at r32: the post-capture merge is a CALLBACK carrying each
# fixture's EXPECTED state, run INSIDE dispatch_and_guard before the
# stream is returned - never a lenient merge run by hand after the
# assertions below, which is the exact ordering this rewrite forbids (the
# merge-before-guard boundary is a security ordering).
# =======================================================================
def _item6_garbage_merge_callback(cred_path):
    """The `garbage` fixture's expected state: the read must succeed and
    the JSON parse must FAIL as expected. An unexpected read failure fails
    closed (DispatchReadFailure, the same sanitized failure every other
    read fault uses); an unexpectedly successful parse means the fixture
    itself is not garbage, which is a test defect, not a filesystem
    uncertainty, so it is reported through pytest.fail rather than as a
    dispatch failure."""
    def _callback():
        try:
            raw = Path(cred_path).read_text(encoding="utf-8")
        except OSError:
            raise support.DispatchReadFailure() from None
        try:
            json.loads(raw)
        except ValueError:
            return
        pytest.fail(
            "item 6 garbage fixture: expected the JSON parse to fail, "
            "but it parsed successfully")
    return _callback


def _item6_absent_merge_callback(cred_path):
    """The `absent` fixture's expected state: absence must be MEASURED
    successfully (a FileNotFoundError on the read). Any OTHER filesystem
    error fails closed, never absence-by-inference; an unexpectedly
    readable file means the fixture is not absent, a test defect reported
    through pytest.fail."""
    def _callback():
        try:
            Path(cred_path).read_text(encoding="utf-8")
        except FileNotFoundError:
            return
        except OSError:
            raise support.DispatchReadFailure() from None
        pytest.fail(
            "item 6 absent fixture: expected the credential file to be "
            "absent, but it was readable")
    return _callback


def test_provider_list_positive_control_valid_credential(tmp_path, host, kimi_binary, guard):
    home = _build_disposable_home(tmp_path, "item6-valid-control-home",
                                   credential_text=_ITEM6_VALID_CREDENTIAL_JSON)
    cred_path = home / "credentials" / "kimi-code.json"
    result = _provider_list(
        kimi_binary, home, guard,
        post_capture_merge=support.strict_reread_and_merge_callback(guard, cred_path))
    assert result.returncode == 0, result.stderr
    assert "source=oauth" in result.stdout


def test_provider_list_false_positive_garbage_credential(tmp_path, host, kimi_binary, guard):
    home = _build_disposable_home(tmp_path, "item6-garbage-home",
                                   credential_text="not valid json at all")
    cred_path = home / "credentials" / "kimi-code.json"
    result = _provider_list(
        kimi_binary, home, guard,
        post_capture_merge=_item6_garbage_merge_callback(cred_path))
    assert result.returncode == 0, result.stderr
    assert "source=oauth" in result.stdout


def test_provider_list_false_positive_absent_credential(tmp_path, host, kimi_binary, guard):
    home = _build_disposable_home(tmp_path, "item6-absent-home", credential_text=None)
    cred_path = home / "credentials" / "kimi-code.json"
    result = _provider_list(
        kimi_binary, home, guard,
        post_capture_merge=_item6_absent_merge_callback(cred_path))
    assert result.returncode == 0, result.stderr
    assert "source=oauth" in result.stdout


# =======================================================================
# Item 7 (measurement 17): `provider list` is not a refresh path, on C.
# Force expiry and take the pre-command snapshot inside the SAME
# pre-command phase; require exit 0 and the expected provider line; then
# require byte-identity by SHA-256, length AND mtime, each measured
# successfully before the comparison ever runs.
# =======================================================================
def test_provider_list_is_not_a_refresh_path(tmp_path, host, module_owner, live_homes,
                                              backup_model, backup_effort, kimi_binary, guard,
                                              debate_ids):
    target = tmp_path / "item7-provider-list-home"
    with support.custody_of(host, target, backup_model, backup_effort, live_homes.c,
                             debate_ids["C"], module_owner.owner_pid,
                             module_owner.owner_ticks) as custody:
        debate_home = custody.debate_home
        cred_path = _credential_path(debate_home)

        _force_expiry(debate_home)
        pre_snapshot = support.measure_file_snapshot(cred_path)

        result = _provider_list(
            kimi_binary, debate_home, guard,
            post_capture_merge=support.strict_reread_and_merge_callback(guard, cred_path))
        assert result.returncode == 0, result.stderr
        assert "source=oauth" in result.stdout

        post_snapshot = support.measure_file_snapshot(cred_path)

        assert pre_snapshot == post_snapshot, (
            "`provider list` must never mutate the credential file: "
            "pre=%r post=%r" % (pre_snapshot, post_snapshot))
