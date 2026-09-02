"""Task-local oracle for Task 8's wrapper-probe.md record (2026-08-30
item32-detached-dispatch plan).

Round 4 found this task had no oracle at all; round 18 found the
replacement counting the record's ROWS instead of reading them, which a
record stating every measurement had FAILED would still pass. This
module reads every field the record's fixed schema names and asserts
its MEASURED value, never merely that a row of that name exists.

`prompt_bytes_match` is asserted `false` on both hosts, on purpose. It
was measured false, twice, on two independent hosts, and root-caused
with no codex call at all: PowerShell's own pipe-to-native-process
serialization (`$brief | codex exec ... -`) appends a trailing CRLF the
fixture never carried. The load-bearing property is
`prompt_sha256_matches`, which is true because
`read-codex-round-evidence.ps1` canonicalizes (CRLF fold, trim) before
hashing - see the record's own explanation. Asserting `true` here would
assert something the measurement refutes; deleting or redefining the
field would hide the one measurement this task exists to make. A future
change that made the raw bytes match end to end would turn this
assertion red ON PURPOSE, which is the whole point of pinning a measured
value instead of a hoped-for one.
"""
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
RECORD = (REPO / "docs" / "superpowers" / "plans" / "rounds" /
          "2026-08-30-item32-detached-dispatch" / "wrapper-probe.md")

HOSTS = ("windows-powershell-5.1", "powershell-7")

FIELD_RE = re.compile(r"(\w+)=(\S+)")


def _parse_fields(line):
    """"key: a=1 b=2 c=3" -> {"a": "1", "b": "2", "c": "3"}."""
    _, _, rest = line.partition(":")
    return dict(FIELD_RE.findall(rest))


def parse_record(path=RECORD):
    """Read the record's fixed-shape fields: one harness dict, and one
    dict of {boundary, states, encoding, kimi_reply} rows per host
    section. Raises AssertionError naming what is missing rather than
    returning a partial structure silently - a record this parser
    cannot read is not evidence of anything either. Takes an injectable
    `path` so the negative self-test below can point it at a mutated
    scratch copy instead of the real record.
    """
    text = path.read_text(encoding="utf-8")

    harness_match = re.search(r"^harness:.*$", text, re.MULTILINE)
    assert harness_match, "record carries no harness line"
    harness = _parse_fields(harness_match.group(0))

    hosts = {}
    # re.split with a capturing group interleaves the delimiter text:
    # [before, host1, body1, host2, body2, ...].
    sections = re.split(r"^## host: (.+)$", text, flags=re.MULTILINE)
    for i in range(1, len(sections), 2):
        host = sections[i].strip()
        body = sections[i + 1]
        rows = {}
        for label in ("boundary", "states", "encoding", "kimi_reply"):
            row_match = re.search(r"^%s:.*$" % label, body, re.MULTILINE)
            assert row_match, "%s section carries no %r row" % (host, label)
            rows[label] = _parse_fields(row_match.group(0))
        hosts[host] = rows

    return harness, hosts


# ---------------------------------------------------------------------
# Shared assertions, one per record row. Both the normal per-host tests
# and the negative self-test at the bottom call these SAME functions,
# so the negative test proves the real check can fail rather than a
# re-typed stand-in for it.
# ---------------------------------------------------------------------
def _assert_harness(harness):
    assert harness.get("plugin_root_token") == "substituted", (
        "plugin_root_token measured %r, not 'substituted' - this is a "
        "plan-level change, not something a task may absorb" %
        harness.get("plugin_root_token"))
    assert harness.get("client_version"), "client_version is empty"


def _assert_boundary(host, row):
    seconds = float(row["launch_return_seconds"])
    assert seconds < 15, (
        "%s: launch_return_seconds=%s is not under 15 - the launch call "
        "did not return until the child was done, the blocking form "
        "again" % (host, seconds))
    assert row["alive_in_later_call"] == "true", (
        "%s: alive_in_later_call=%s" % (host, row["alive_in_later_call"]))
    assert row["exit_file_after_sleep"] == "true", (
        "%s: exit_file_after_sleep=%s" % (host, row["exit_file_after_sleep"]))


def _assert_states(host, row):
    assert row["killed_tree"] == "no-exit-file", (
        "%s: killed_tree=%s" % (host, row["killed_tree"]))
    assert row["refused_receipt"] == "no-receipt", (
        "%s: refused_receipt=%s" % (host, row["refused_receipt"]))
    assert row["empty_reply"] == "reply-empty", (
        "%s: empty_reply=%s" % (host, row["empty_reply"]))


def _assert_encoding(host, row):
    assert row["binder"] == "accepted", "%s: binder=%s" % (host, row["binder"])
    assert row["prompt_sha256_matches"] == "true", (
        "%s: prompt_sha256_matches=%s" % (host, row["prompt_sha256_matches"]))
    assert row["prompt_bytes_match"] == "false", (
        "%s: prompt_bytes_match=%s (measured false: PowerShell's pipe "
        "appends a trailing CRLF the fixture never carried; canonical "
        "identity via prompt_sha256_matches, not raw-byte identity, is "
        "what the transport guarantees)" %
        (host, row["prompt_bytes_match"]))


def _assert_kimi_reply(host, row):
    assert row["bytes_match"] == "true", (
        "%s: bytes_match=%s" % (host, row["bytes_match"]))
    assert row["bom_present"] == "false", (
        "%s: bom_present=%s" % (host, row["bom_present"]))


# ---------------------------------------------------------------------
# Presence
# ---------------------------------------------------------------------
def test_record_exists():
    assert RECORD.exists(), "wrapper-probe.md is missing"


def test_both_host_sections_present():
    _, hosts = parse_record()
    for host in HOSTS:
        assert host in hosts, "record carries no ## host: %s section" % host


# ---------------------------------------------------------------------
# harness - Task 1 step 0's line; this task only reads it.
# ---------------------------------------------------------------------
def test_harness_values():
    harness, _ = parse_record()
    _assert_harness(harness)


# ---------------------------------------------------------------------
# Per-host measured values. Round 4/18: assert VALUES, never counts.
# ---------------------------------------------------------------------
@pytest.mark.parametrize("host", HOSTS)
def test_boundary_values(host):
    _, hosts = parse_record()
    _assert_boundary(host, hosts[host]["boundary"])


@pytest.mark.parametrize("host", HOSTS)
def test_states_values(host):
    _, hosts = parse_record()
    _assert_states(host, hosts[host]["states"])


@pytest.mark.parametrize("host", HOSTS)
def test_encoding_values(host):
    _, hosts = parse_record()
    _assert_encoding(host, hosts[host]["encoding"])


@pytest.mark.parametrize("host", HOSTS)
def test_kimi_reply_values(host):
    _, hosts = parse_record()
    _assert_kimi_reply(host, hosts[host]["kimi_reply"])


# ---------------------------------------------------------------------
# Step 6's own requirement: prove the oracle can fail. Round 18's
# finding was an oracle that only counted rows; this changes ONE
# recorded value in a SCRATCH COPY, re-parses it, and confirms the SAME
# assertion function used above fails and names that field - never a
# re-typed stand-in for the real check.
# ---------------------------------------------------------------------
def test_the_oracle_can_fail_on_a_changed_value(tmp_path):
    original = RECORD.read_text(encoding="utf-8")
    assert original.count("alive_in_later_call=true") == 2, (
        "expected exactly one boundary row per host to mutate")

    # Replaces only the FIRST occurrence, which is the
    # windows-powershell-5.1 section (it appears first in the file).
    mutated = original.replace(
        "alive_in_later_call=true", "alive_in_later_call=false", 1)
    assert mutated != original, "the targeted field was not found to mutate"
    scratch = tmp_path / "wrapper-probe-scratch.md"
    scratch.write_text(mutated, encoding="utf-8")

    _, hosts = parse_record(scratch)
    with pytest.raises(AssertionError, match="alive_in_later_call"):
        _assert_boundary("windows-powershell-5.1",
                          hosts["windows-powershell-5.1"]["boundary"])

    # The second host section's own row is untouched by a first-only
    # replace, so the same assertion against it still passes - this
    # confirms the failure is scoped to the field that actually changed.
    _assert_boundary("powershell-7", hosts["powershell-7"]["boundary"])

    # The real record on disk is untouched - this ran against a copy only.
    assert RECORD.read_text(encoding="utf-8") == original
