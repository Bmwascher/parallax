"""Structural validation contract pins for read-kimi-credential-state.ps1.

The validator reports SHAPE only: whether a kimi-code credential document
is readable JSON, is an object, carries every required field with the
right .NET type, and carries no blank token after trimming. It never
checks truthiness (0 is a valid expires_at) and never checks freshness (a
past expiry is a valid expires_at) - getting either of those wrong is the
whole point of test_expires_at_zero_is_ok and
test_a_past_expiry_is_still_ok below.

Defect precedence is frozen: not-json, not-object, missing-field,
wrong-type, blank-token. A document can carry several defects at once;
only the FIRST that fires in this order is ever reported.

EXIT CODE, frozen and NOT "clean vs dirty": the exit code answers only
"did this invocation produce a classification". `ok`, `absent`,
`unreadable`, and every `malformed` detail are all completed
classifications and all exit 0, with exactly one schema-valid JSON line
on stdout and nothing on stderr. Only an invocation that could not
classify at all - a blank/whitespace -Path, the
PARALLAX_KIMI_CREDENTIAL_STATE_FAULT seam, or a PowerShell parameter-
binding refusal - exits 1 (or, for a binding refusal PowerShell itself
raises, nonzero) with no stdout and a message on stderr. Collapsing
"measured and found absent" into the same signal as "never measured"
would be the unmade-measurement case wearing a passing exit code, which
is exactly what the doctor's separate `N/A` (credential absent) and
`BROKEN` (validator failed to run) rows exist to keep apart.

The output object is frozen as exactly status/detail/fields - never a
fourth key - which assert_classification below checks on every single
classification in this file, not just once.

Fixtures use obviously fake token values. This repo is public, so every
assertion here inspects the PARSED status/detail/fields, and
run_validator scans the raw process output too - no test may let a token
value reach stdout or stderr.

WINDOWS ONLY: the validator is a PowerShell script exercising real
Windows file I/O (icacls-denied ACLs for the unreadable case), so this
whole module is skipped unless a PowerShell host is selected AND the
platform is actually Windows - PARALLAX_PS_HOST selects the host, and the
os.name guard exists because Ubuntu CI supplies pwsh: a selector that
merely finds a host would happily collect these tests there too, same
lesson as test_codex_context_probe.py.
"""
import importlib.util
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
VALIDATOR = REPO / "tools" / "read-kimi-credential-state.ps1"


def _load_exact_line_module():
    path = REPO / "evals" / "tools" / "exact_line.py"
    spec = importlib.util.spec_from_file_location("exact_line", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


accept_exactly_one_nonempty_line = _load_exact_line_module().accept_exactly_one_nonempty_line

POWERSHELL = (os.environ.get("PARALLAX_PS_HOST")
              or shutil.which("powershell") or shutil.which("pwsh"))

pytestmark = pytest.mark.skipif(
    os.name != "nt" or POWERSHELL is None,
    reason="the validator is a Windows tool: it needs a real PowerShell "
           "host and Windows ACL semantics for the unreadable case")


def ps_host():
    """PARALLAX_PS_HOST selects the interpreter. A green suite on one
    Windows host proves ONE interpreter."""
    return POWERSHELL


FAULT_VAR = "PARALLAX_KIMI_CREDENTIAL_STATE_FAULT"
VALIDATOR_FAILED_MESSAGE = "credential validator failed"
FAULT_MESSAGE = (
    "PARALLAX_KIMI_CREDENTIAL_STATE_FAULT injected: simulated validator failure")

FAKE_ACCESS = "fake-access-abc123-not-real"
FAKE_REFRESH = "fake-refresh-xyz789-not-real"
FAKE_ACCESS_STALE = "fake-access-stale-first-value"
FAKE_REFRESH_STALE = "fake-refresh-stale-first-value"

# Every fixture token literal used anywhere in this file. Checked against
# raw stdout AND stderr on EVERY invocation, not just in one dedicated
# test, so a leak introduced by a future case in this file cannot slip
# past for lack of its own assertion.
ALL_FIXTURE_TOKENS = (
    FAKE_ACCESS, FAKE_REFRESH, FAKE_ACCESS_STALE, FAKE_REFRESH_STALE,
)


def run_validator(path=None, extra_args=None, env_overrides=None):
    args = [ps_host(), "-NoProfile", "-NonInteractive", "-File", str(VALIDATOR)]
    if path is not None:
        args += ["-Path", str(path)]
    if extra_args:
        args += extra_args
    env = dict(os.environ)
    env.pop(FAULT_VAR, None)
    if env_overrides:
        env.update(env_overrides)
    proc = subprocess.run(args, capture_output=True, text=True, env=env)
    for token in ALL_FIXTURE_TOKENS:
        assert token not in proc.stdout, (
            f"a fixture token value leaked into stdout: {token!r}")
        assert token not in proc.stderr, (
            f"a fixture token value leaked into stderr: {token!r}")
    return proc


def assert_classification(proc):
    """A completed classification: exit 0, exactly one schema-valid JSON
    line on stdout, nothing on stderr. Also enforces the frozen output
    shape - exactly status/detail/fields, fields an array of strings -
    on every call site that classifies, not just in one dedicated test.
    """
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert proc.stderr == "", f"stderr must be empty on a classification, got {proc.stderr!r}"
    line = accept_exactly_one_nonempty_line(proc.stdout)
    assert line is not None, f"expected exactly one output line, got {proc.stdout!r}"
    report = json.loads(line)
    assert set(report.keys()) == {"status", "detail", "fields"}, report.keys()
    assert isinstance(report["fields"], list)
    assert all(isinstance(f, str) for f in report["fields"])
    return report


def assert_validator_failure(proc, expected_stderr=None):
    """No classification could be produced: nonzero exit, no stdout at
    all. When this script's own code decided the failure (as opposed to
    PowerShell's parameter binder refusing the invocation before our
    code ever runs), it is specifically exit 1 with exactly one message
    on stderr."""
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert proc.stdout == "", f"validator failure must produce no stdout, got {proc.stdout!r}"
    if expected_stderr is not None:
        assert proc.returncode == 1, proc.stdout + proc.stderr
        assert proc.stderr == expected_stderr, proc.stderr


def write_raw(tmp_path, name, text):
    p = tmp_path / name
    p.write_bytes(text.encode("utf-8"))
    return p


def write_doc(tmp_path, name, **fields):
    return write_raw(tmp_path, name, json.dumps(fields))


def valid_fields(**overrides):
    doc = {"access_token": FAKE_ACCESS, "refresh_token": FAKE_REFRESH,
           "expires_at": 900}
    doc.update(overrides)
    return doc


def deny_read(path):
    user = os.environ["USERNAME"]
    deny = subprocess.run(["icacls", str(path), "/deny", f"{user}:(R)"],
                          capture_output=True, text=True)
    assert deny.returncode == 0, deny.stdout + deny.stderr


def restore_read(path):
    # icacls's own DACL-modifying commands need WRITE_DAC, and a plain
    # /deny "$user:(R)" denies READ_CONTROL along with data read (R
    # expands to FILE_GENERIC_READ, which includes READ_CONTROL) -
    # measured live: a bare `icacls /reset` after that deny fails with
    # "Access is denied" on this machine's temp-directory ACLs, where
    # ownership does not resolve to the running identity through OWNER
    # RIGHTS alone. `takeown` re-establishes literal ownership first,
    # which carries an inherent WRITE_DAC regardless of any DACL entry,
    # so the subsequent reset can always succeed.
    takeown = subprocess.run(["takeown", "/f", str(path)],
                             capture_output=True, text=True)
    assert takeown.returncode == 0, takeown.stdout + takeown.stderr
    restore = subprocess.run(["icacls", str(path), "/reset"],
                             capture_output=True, text=True)
    assert restore.returncode == 0, restore.stdout + restore.stderr


# --- one test per status/detail row, all now classifications (exit 0) ---


def test_absent(tmp_path):
    proc = run_validator(tmp_path / "does-not-exist.json")
    report = assert_classification(proc)
    assert report == {"status": "absent", "detail": "no-file", "fields": []}


def test_unreadable(tmp_path):
    """icacls-deny read to the current identity, run, restore in a
    finally - never leaving a locked-down file behind even if the
    assertion fails."""
    path = write_doc(tmp_path, "unreadable.json", **valid_fields())
    deny_read(path)
    try:
        proc = run_validator(path)
        report = assert_classification(proc)
        assert report == {
            "status": "unreadable", "detail": "read-failed", "fields": []}
    finally:
        restore_read(path)


def test_not_json(tmp_path):
    path = write_raw(tmp_path, "not-json.json", "not json at all")
    proc = run_validator(path)
    report = assert_classification(proc)
    assert report == {
        "status": "malformed", "detail": "not-json", "fields": []}


def test_not_object(tmp_path):
    path = write_raw(tmp_path, "not-object.json", "[1,2,3]")
    proc = run_validator(path)
    report = assert_classification(proc)
    assert report == {
        "status": "malformed", "detail": "not-object", "fields": []}


@pytest.mark.parametrize("absent_field", [
    "access_token", "refresh_token", "expires_at"])
def test_missing_field(tmp_path, absent_field):
    doc = valid_fields()
    del doc[absent_field]
    path = write_doc(tmp_path, "missing.json", **doc)
    proc = run_validator(path)
    report = assert_classification(proc)
    assert report["status"] == "malformed"
    assert report["detail"] == "missing-field"
    assert report["fields"] == sorted(doc.keys())


@pytest.mark.parametrize("bad_expires_at", [
    1.5,             # fractional
    True,            # boolean
    None,            # null
    "123",           # numeric-looking string
    99999999999999999999999999,  # Int64-overflowing
], ids=["fractional", "boolean", "null", "numeric-string", "overflow"])
def test_wrong_type(tmp_path, bad_expires_at):
    doc = valid_fields(expires_at=bad_expires_at)
    path = write_doc(tmp_path, "wrong-type.json", **doc)
    proc = run_validator(path)
    report = assert_classification(proc)
    assert report["status"] == "malformed"
    assert report["detail"] == "wrong-type"
    assert report["fields"] == sorted(doc.keys())


def test_blank_token_is_whitespace_only(tmp_path):
    doc = valid_fields(access_token="   ")
    path = write_doc(tmp_path, "blank.json", **doc)
    proc = run_validator(path)
    report = assert_classification(proc)
    assert report["status"] == "malformed"
    assert report["detail"] == "blank-token"
    assert report["fields"] == sorted(doc.keys())


def test_ok(tmp_path):
    doc = valid_fields()
    path = write_doc(tmp_path, "ok.json", **doc)
    proc = run_validator(path)
    report = assert_classification(proc)
    assert report["status"] == "ok"
    assert report["detail"] == "valid"
    assert report["fields"] == sorted(doc.keys())


# --- no truthiness, no freshness ----------------------------------------


def test_expires_at_zero_is_ok(tmp_path):
    """0 is falsy in most languages. A truthiness check here would be
    wrong: expires_at 0 is a structurally valid integer field."""
    doc = valid_fields(expires_at=0)
    path = write_doc(tmp_path, "zero.json", **doc)
    proc = run_validator(path)
    assert assert_classification(proc)["status"] == "ok"


def test_a_past_expiry_is_still_ok(tmp_path):
    """This validator checks SHAPE, never the clock. A credential that
    expired ten years ago is still a structurally valid document - it is
    someone else's job to decide whether an ok-but-expired credential is
    usable."""
    doc = valid_fields(expires_at=1000000)  # 1970-01-12, long past
    path = write_doc(tmp_path, "past-expiry.json", **doc)
    proc = run_validator(path)
    assert assert_classification(proc)["status"] == "ok"


# --- optional fields and unknown fields ----------------------------------


def test_all_optional_fields_absent_is_ok(tmp_path):
    doc = {"access_token": FAKE_ACCESS, "refresh_token": FAKE_REFRESH,
           "expires_at": 900}
    assert not ({"scope", "token_type", "expires_in"} & doc.keys())
    path = write_doc(tmp_path, "no-optional.json", **doc)
    proc = run_validator(path)
    assert assert_classification(proc)["status"] == "ok"


def test_an_unknown_extra_field_is_ok(tmp_path):
    doc = valid_fields(some_unknown_field="anything")
    path = write_doc(tmp_path, "extra.json", **doc)
    proc = run_validator(path)
    report = assert_classification(proc)
    assert report["status"] == "ok"
    assert report["fields"] == sorted(doc.keys())


# --- fields: sorted with the Ordinal comparer, [] for the four statuses -


def test_fields_are_sorted_with_the_ordinal_comparer(tmp_path):
    """A default (culture-aware) sort would order these names
    differently - it places 'Zebra_extra' LAST, case-insensitively mixed
    in with the lowercase names, where Ordinal places it FIRST because
    'Z' (0x5A) sorts before '_' (0x5F) and 'a' (0x61) as raw code points.
    Comparing against Python's default str sort (also code-point order
    for ASCII) catches a script that used PowerShell's default sort
    instead of [System.StringComparer]::Ordinal."""
    doc = valid_fields(Zebra_extra="x", apple_extra="y", _lead_extra="z")
    path = write_doc(tmp_path, "sorted.json", **doc)
    proc = run_validator(path)
    report = assert_classification(proc)
    assert report["fields"] == sorted(doc.keys())
    assert report["fields"][0] == "Zebra_extra", (
        "Ordinal sorts 'Zebra_extra' before the lowercase and "
        "underscore-leading names; a culture-aware sort would not")


@pytest.mark.parametrize("case", ["absent", "unreadable", "not-json", "not-object"])
def test_fields_is_empty_for_the_four_unparseable_statuses(tmp_path, case):
    if case == "absent":
        path = tmp_path / "missing-entirely.json"
        proc = run_validator(path)
    elif case == "unreadable":
        path = write_doc(tmp_path, "unreadable2.json", **valid_fields())
        deny_read(path)
        try:
            proc = run_validator(path)
        finally:
            restore_read(path)
    elif case == "not-json":
        path = write_raw(tmp_path, "notjson2.json", "{not valid")
        proc = run_validator(path)
    else:
        path = write_raw(tmp_path, "notobject2.json", '"just a string"')
        proc = run_validator(path)
    report = assert_classification(proc)
    assert report["fields"] == []


# --- defect precedence, frozen -------------------------------------------


def test_the_precedence_order_for_a_document_carrying_three_defects_at_once(tmp_path):
    """expires_at is entirely ABSENT (missing-field), access_token is an
    integer (wrong-type), and refresh_token is whitespace-only
    (blank-token) - all three fire on the same document. The frozen
    order is not-json, not-object, missing-field, wrong-type,
    blank-token, so missing-field must be the one reported."""
    path = write_doc(tmp_path, "triple-defect.json",
                     access_token=123, refresh_token="   ")
    proc = run_validator(path)
    report = assert_classification(proc)
    assert report["status"] == "malformed"
    assert report["detail"] == "missing-field"


# --- duplicate keys: the validator validates what the reader returned ---


def test_a_duplicate_key_with_an_invalid_first_and_a_valid_last_is_ok(tmp_path):
    """An implementation that rejected duplicate keys outright, or that
    kept the FIRST value instead of the last, would also pass every
    other test in this file - this is the opposite-direction oracle that
    forces 'take the last occurrence' specifically."""
    raw = (
        '{"access_token": "%s", "access_token": "%s", '
        '"refresh_token": "%s", "expires_at": 900}'
        % (FAKE_ACCESS_STALE, FAKE_ACCESS, FAKE_REFRESH)
    )
    path = write_raw(tmp_path, "dup-ok.json", raw)
    proc = run_validator(path)
    assert assert_classification(proc)["status"] == "ok"


def test_a_duplicate_key_with_a_valid_first_and_an_invalid_last_reports_the_last_defect(tmp_path):
    raw = (
        '{"access_token": "%s", "access_token": "   ", '
        '"refresh_token": "%s", "expires_at": 900}'
        % (FAKE_ACCESS, FAKE_REFRESH)
    )
    path = write_raw(tmp_path, "dup-bad.json", raw)
    proc = run_validator(path)
    report = assert_classification(proc)
    assert report["status"] == "malformed"
    assert report["detail"] == "blank-token"


# --- no output line ever contains a fixture token value -----------------


def test_no_output_line_contains_a_fixture_token_value(tmp_path):
    """Belt and braces on top of run_validator's automatic scan: an
    explicit test naming the exact fixture tokens, against an 'ok'
    document where the tokens are guaranteed to have been parsed and
    handled, not merely absent from an early-exit branch."""
    doc = valid_fields()
    path = write_doc(tmp_path, "leak-check.json", **doc)
    proc = run_validator(path)
    assert_classification(proc)
    assert FAKE_ACCESS not in proc.stdout
    assert FAKE_REFRESH not in proc.stdout
    assert FAKE_ACCESS not in proc.stderr
    assert FAKE_REFRESH not in proc.stderr


# --- validator failure: no classification could be produced -------------


def test_a_blank_path_takes_the_validator_failure_path_never_absent(tmp_path):
    """An empty -Path was never a file that got measured and found
    missing - PowerShell's own mandatory-string binder refuses a
    genuinely empty value outright (a binding refusal, covered by its
    own test below), which already lands on validator failure without
    this script's code ever running. Either way, 'absent' must never be
    the outcome."""
    proc = run_validator(path="")
    assert_validator_failure(proc)


def test_a_whitespace_only_path_takes_the_validator_failure_path(tmp_path):
    """Unlike a fully empty string, PowerShell's binder happily binds a
    whitespace-only value, so this script's OWN check is what has to
    catch it - and it must report validator failure, not 'absent'."""
    proc = run_validator(path="   ")
    assert_validator_failure(proc, expected_stderr=VALIDATOR_FAILED_MESSAGE + "\n")


def test_the_fault_seam_produces_validator_failure(tmp_path):
    doc = valid_fields()
    path = write_doc(tmp_path, "fault.json", **doc)
    proc = run_validator(path, env_overrides={FAULT_VAR: "1"})
    assert_validator_failure(proc, expected_stderr=FAULT_MESSAGE + "\n")


@pytest.mark.parametrize("fault_value", ["1", "x", "0", "false", "   "],
                        ids=["one", "letter", "zero", "false-string", "whitespace"])
def test_the_fault_seam_activates_on_any_nonempty_value(tmp_path, fault_value):
    doc = valid_fields()
    path = write_doc(tmp_path, "fault-any.json", **doc)
    proc = run_validator(path, env_overrides={FAULT_VAR: fault_value})
    assert_validator_failure(proc, expected_stderr=FAULT_MESSAGE + "\n")


def test_the_fault_seam_does_not_activate_on_an_empty_value(tmp_path):
    """The opposite-direction oracle for 'ANY NONEMPTY value': a set but
    EMPTY environment variable must not trip the seam, so a normal
    classification still comes through."""
    doc = valid_fields()
    path = write_doc(tmp_path, "fault-empty.json", **doc)
    proc = run_validator(path, env_overrides={FAULT_VAR: ""})
    assert assert_classification(proc)["status"] == "ok"


def test_the_fault_seam_fires_before_the_path_probe_even_for_an_absent_path(tmp_path):
    """The seam is specified to fire immediately BEFORE the path probe,
    so it must preempt an otherwise-valid 'absent' classification too -
    the fault result, not 'absent', must come out."""
    proc = run_validator(tmp_path / "does-not-exist.json",
                         env_overrides={FAULT_VAR: "1"})
    assert_validator_failure(proc, expected_stderr=FAULT_MESSAGE + "\n")


def test_a_binding_refusal_produces_no_classification(tmp_path):
    """-Path is mandatory. Omitting it entirely is rejected by
    PowerShell's own parameter binder before this script's code ever
    runs - a process-launch-shaped failure, not one this script's Fail
    path produces, but it must still exit nonzero with no valid result
    line on stdout."""
    proc = run_validator(path=None)
    assert_validator_failure(proc)
