"""Contract pins for the per-debate kimi-code lane home."""
import os
import re
import shutil
import subprocess
import tomllib
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


def _render_config_template(model, effort, model_table_fields):
    """Extract the ACTUAL config.toml here-string from the committed
    script and substitute its interpolated variables the same way
    PowerShell's simple `"$Var"` string interpolation would - so any
    future edit to the real template is what this test parses, not a
    copy that can silently drift from it."""
    body = _read(BUILDER)
    match = re.search(r'\$configToml = @"\r?\n(.*?)\r?\n"@', body, re.DOTALL)
    assert match, "could not locate the config.toml here-string in the builder"
    template = match.group(1)
    return (template
            .replace("$modelTableFields", model_table_fields)
            .replace("$Model", model)
            .replace("$Effort", effort))


def test_rendered_config_places_root_keys_at_the_document_root():
    """Fix-round-3 finding: in TOML, a table header claims every
    key-value pair that follows it until the NEXT header - a blank line
    does NOT end a table. An earlier template put
    default_model/extra_skill_dirs/telemetry AFTER [models."$Model"], so
    all three silently became keys of the MODEL table instead of the
    document root: extra_skill_dirs is a containment setting that then
    suppressed nothing while looking like it did, and telemetry was
    observed resolving to true despite this file saying false. A test
    asserting the file merely CONTAINS "default_model" would have passed
    against the broken template - it is not this test. This one parses
    the real template with an actual TOML parser (not a text/substring
    check, which cannot distinguish a root key from a same-named key
    nested under a table) and asserts where the keys actually resolve."""
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
    # default_effort is the ONE key that belongs inside the model table;
    # the other three must not be duplicated or misplaced there.
    assert "default_model" not in model_table
    assert "extra_skill_dirs" not in model_table
    assert "telemetry" not in model_table

    # The providers table and its .oauth sub-table sit BETWEEN the root
    # keys and the model table in the source - confirm nothing intended
    # for one drifted into another.
    provider_table = parsed["providers"]["managed:kimi-code"]
    assert provider_table["type"] == "kimi"
    assert "storage" not in provider_table
    assert "key" not in provider_table
    oauth_table = provider_table["oauth"]
    assert oauth_table["storage"] == "file"
    assert oauth_table["key"] == "oauth/kimi-code"
    assert "type" not in oauth_table
    assert "api_key" not in oauth_table


# --- Fix round 4: the model table must be a FAITHFUL copy of the real one ---
#
# The template used to hand-write four fields (provider, model,
# max_context_size, default_effort) and omit `capabilities` and
# `support_efforts`. Measured, one dispatch per state, same agent file,
# same model, same effort:
#
#     WITHOUT the two keys:  thinkingEffort=off   toolCount=4
#     WITH the two keys:     thinkingEffort=high  toolCount=5
#
# No `thinking` capability means thinking is off and the pinned effort has
# nothing to resolve against, so the log reads `off` while config.toml
# says `high`; no `image_in` capability gates ReadMediaFile out of the
# schema, so a five-tool allowlist arrives as four. One omission, two
# silently broken evidence claims.
#
# These tests drive the REAL script against a FAKE USERPROFILE carrying a
# fake real-config, then parse the file it actually wrote. A test asserting
# the rendered text merely CONTAINS "capabilities" is not this test - that
# would pass against a template writing the key into the wrong table,
# which is the exact mistake fix round 3 had to repair. tomllib resolves
# where each key actually lands.

PLACEHOLDER_MODEL = "kimi-code/test-placeholder-model"

# Shaped like the user's real config: root key, hooks, OTHER model tables,
# a [thinking] table and [services.*] blocks after the wanted table. Only
# the one wanted table may reach the rendered home.
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


def _fake_profile(tmp_path, config_text):
    """A stand-in USERPROFILE carrying a .kimi-code with a config and a
    credential, so the builder can be driven end to end offline."""
    profile = tmp_path / "fake-profile"
    kimi = profile / ".kimi-code"
    (kimi / "credentials").mkdir(parents=True)
    (kimi / "credentials" / "kimi-code.json").write_text(
        '{"access_token": "not-a-real-token"}', encoding="ascii")
    if config_text is not None:
        (kimi / "config.toml").write_text(config_text, encoding="ascii")
    return profile


def _build(tmp_path, target, profile, model=PLACEHOLDER_MODEL, effort="high"):
    env = dict(os.environ)
    env["USERPROFILE"] = str(profile)
    # This pytest process inherits a PowerShell 7 flavoured PSModulePath
    # whose `...\PowerShell\7\Modules` entry shadows the 5.1 copy of
    # Microsoft.PowerShell.Security, so Get-Acl fails to load inside a
    # powershell.exe child. Dropping the variable lets each host compute
    # its own default. Nothing under test depends on it. Popped
    # case-insensitively: Windows os.environ normalizes keys to upper
    # case, so a plain pop("PSModulePath") silently removes nothing.
    for key in [k for k in env if k.lower() == "psmodulepath"]:
        del env[key]
    return subprocess.run(
        [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-File", str(BUILDER), "-Path", str(target),
         "-Model", model, "-Effort", effort],
        capture_output=True, text=True, timeout=120, env=env)


@pytest.mark.skipif(POWERSHELL is None, reason="no PowerShell host on PATH")
def test_capabilities_and_support_efforts_land_inside_the_model_table(tmp_path):
    """The rendered model table must carry the real table's capabilities
    and support_efforts, INSIDE the model table - not at the document
    root, not under [thinking], not under the provider table."""
    target = tmp_path / "carried-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    proc = _build(tmp_path, target, profile)
    assert proc.returncode == 0, proc.stdout + proc.stderr

    with open(target / "config.toml", "rb") as fh:
        parsed = tomllib.load(fh)

    model_table = parsed["models"][PLACEHOLDER_MODEL]
    assert model_table["capabilities"] == [
        "thinking", "always_thinking", "image_in", "tool_use"]
    assert model_table["support_efforts"] == ["low", "high", "max"]
    # Placement, not mere presence: neither key may resolve anywhere else.
    assert "capabilities" not in parsed
    assert "support_efforts" not in parsed
    assert "capabilities" not in parsed["thinking"]
    assert "support_efforts" not in parsed["thinking"]
    assert "capabilities" not in parsed["providers"]["managed:kimi-code"]

    # The rest of the real table comes across too, including the context
    # window that used to be a hardcoded literal in the script.
    assert model_table["provider"] == "managed:kimi-code"
    assert model_table["model"] == "test-placeholder-model"
    assert model_table["max_context_size"] == 262144
    assert model_table["display_name"] == "Test Placeholder"


@pytest.mark.skipif(POWERSHELL is None, reason="no PowerShell host on PATH")
def test_effort_is_the_argument_not_the_real_configs_value(tmp_path):
    """Pinning effort per debate is the whole point of -Effort, so the
    real config's own default_effort must never win. The fake config says
    "low"; the build asks for "max"."""
    target = tmp_path / "effort-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    proc = _build(tmp_path, target, profile, effort="max")
    assert proc.returncode == 0, proc.stdout + proc.stderr

    with open(target / "config.toml", "rb") as fh:
        parsed = tomllib.load(fh)

    model_table = parsed["models"][PLACEHOLDER_MODEL]
    assert model_table["default_effort"] == "max"
    # A carried duplicate would make the file invalid TOML, so reaching
    # here at all proves the real config's own line was dropped, not
    # appended alongside; assert the resolved value anyway.
    assert model_table["default_effort"] != "low"


@pytest.mark.skipif(POWERSHELL is None, reason="no PowerShell host on PATH")
def test_nothing_outside_the_model_table_is_carried(tmp_path):
    """Isolation is why this script renders its own file. The fake config
    carries hooks, a second model, and a services block; none may follow
    the model table's fields into the home."""
    target = tmp_path / "isolation-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    proc = _build(tmp_path, target, profile)
    assert proc.returncode == 0, proc.stdout + proc.stderr

    with open(target / "config.toml", "rb") as fh:
        parsed = tomllib.load(fh)

    assert "hooks" not in parsed
    assert "services" not in parsed
    assert list(parsed["models"].keys()) == [PLACEHOLDER_MODEL]
    # The real config's root default_model must not override the home's.
    assert parsed["default_model"] == PLACEHOLDER_MODEL


@pytest.mark.skipif(POWERSHELL is None, reason="no PowerShell host on PATH")
def test_a_missing_model_table_refuses_instead_of_guessing(tmp_path):
    """A home built on a guessed model table is an unmade measurement, and
    an unmade measurement is never a clean one. No fallback to defaults."""
    target = tmp_path / "no-table-home"
    profile = _fake_profile(tmp_path, FAKE_REAL_CONFIG)
    proc = _build(tmp_path, target, profile,
                  model="kimi-code/model-not-in-the-config")
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert "declares no model table" in proc.stdout + proc.stderr
    assert not target.exists(), (
        "the refusal must land before any directory is created")


@pytest.mark.skipif(POWERSHELL is None, reason="no PowerShell host on PATH")
def test_a_missing_real_config_refuses_instead_of_guessing(tmp_path):
    target = tmp_path / "no-config-home"
    profile = _fake_profile(tmp_path, None)
    proc = _build(tmp_path, target, profile)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert "no kimi-code config at" in proc.stdout + proc.stderr
    assert not target.exists()


@pytest.mark.skipif(POWERSHELL is None, reason="no PowerShell host on PATH")
def test_an_unparseable_model_table_refuses_instead_of_guessing(tmp_path):
    """A field this reader cannot account for is unparseable, and
    unparseable refuses - it is never silently dropped, because a silently
    dropped field is exactly the defect this whole round exists to fix."""
    broken = FAKE_REAL_CONFIG.replace(
        'display_name = "Test Placeholder"',
        "display_name = { first = 'nested inline table' }")
    target = tmp_path / "unparseable-home"
    profile = _fake_profile(tmp_path, broken)
    proc = _build(tmp_path, target, profile)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert "unparseable line" in proc.stdout + proc.stderr
    assert not target.exists()


# --- Fix round 5: a non-empty carried table is not a DISPATCHABLE one ---
#
# The count gate only guarded total emptiness. A reviewer reached both of
# these live against probe tables: a table carrying only display_name and
# default_effort BUILT, rendering a model with no provider and no model
# name; and a table naming `managed:some-other-provider` BUILT, rendering
# a model table that references a provider absent from its own providers
# table. Both are dormant against today's real config and neither stays
# dormant once that config grows a second provider. Both failed the same
# bad way - silent success at build time, confusing client error
# mid-debate - which is the class of failure every gate in this script
# exists to convert into a clean build-time refusal.


@pytest.mark.skipif(POWERSHELL is None, reason="no PowerShell host on PATH")
def test_a_model_table_without_a_provider_key_refuses(tmp_path):
    without_provider = FAKE_REAL_CONFIG.replace(
        '[models."%s"]\nprovider = "managed:kimi-code"\n' % PLACEHOLDER_MODEL,
        '[models."%s"]\n' % PLACEHOLDER_MODEL)
    assert 'provider = "managed:kimi-code"\nmodel = "test-placeholder-model"' \
        not in without_provider
    target = tmp_path / "no-provider-home"
    profile = _fake_profile(tmp_path, without_provider)
    proc = _build(tmp_path, target, profile)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert "carries no provider key" in proc.stdout + proc.stderr
    assert not target.exists()


@pytest.mark.skipif(POWERSHELL is None, reason="no PowerShell host on PATH")
def test_a_model_table_without_a_model_key_refuses(tmp_path):
    without_model = FAKE_REAL_CONFIG.replace(
        '\nmodel = "test-placeholder-model"\n', "\n")
    assert 'model = "test-placeholder-model"' not in without_model
    target = tmp_path / "no-model-home"
    profile = _fake_profile(tmp_path, without_model)
    proc = _build(tmp_path, target, profile)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert "carries no model key" in proc.stdout + proc.stderr
    assert not target.exists()


@pytest.mark.skipif(POWERSHELL is None, reason="no PowerShell host on PATH")
def test_a_model_table_naming_an_undeclared_provider_refuses(tmp_path):
    """The rendered home declares exactly one provider table. A carried
    `provider` value naming anything else renders a dangling reference."""
    other_provider = FAKE_REAL_CONFIG.replace(
        '[models."%s"]\nprovider = "managed:kimi-code"' % PLACEHOLDER_MODEL,
        '[models."%s"]\nprovider = "managed:some-other-provider"'
        % PLACEHOLDER_MODEL)
    assert "managed:some-other-provider" in other_provider
    target = tmp_path / "other-provider-home"
    profile = _fake_profile(tmp_path, other_provider)
    proc = _build(tmp_path, target, profile)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert "which this home does not declare" in proc.stdout + proc.stderr
    assert not target.exists()


# --- Fix round 5, the two minors: refusals that were structurally sound
# but exercised by nothing. Each needs only a fake config to drive it.


@pytest.mark.skipif(POWERSHELL is None, reason="no PowerShell host on PATH")
def test_an_unreadable_real_config_refuses(tmp_path):
    """Present but unreadable is not the same as absent, and it must not
    fall through to the absent branch's message or to a raw client error.
    A directory standing where the file belongs passes Test-Path and then
    fails to read, which is the cheapest real instance of the condition."""
    target = tmp_path / "unreadable-config-home"
    profile = _fake_profile(tmp_path, None)
    (profile / ".kimi-code" / "config.toml").mkdir()
    proc = _build(tmp_path, target, profile)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert "could not read" in proc.stdout + proc.stderr
    assert not target.exists()


@pytest.mark.skipif(POWERSHELL is None, reason="no PowerShell host on PATH")
def test_a_duplicate_model_table_refuses(tmp_path):
    """Two tables for the same model make which one was carried a matter
    of scan order, so neither is carried."""
    duplicated = FAKE_REAL_CONFIG + (
        '\n[models."%s"]\nprovider = "managed:kimi-code"\n'
        'model = "test-placeholder-model"\n' % PLACEHOLDER_MODEL)
    assert duplicated.count('[models."%s"]' % PLACEHOLDER_MODEL) == 2
    target = tmp_path / "duplicate-table-home"
    profile = _fake_profile(tmp_path, duplicated)
    proc = _build(tmp_path, target, profile)
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert "more than once" in proc.stdout + proc.stderr
    assert not target.exists()
