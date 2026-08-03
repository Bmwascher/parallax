"""Guard contract pins for plant-home-skill-canary.ps1.

This tool WRITES INTO THE USER'S REAL HOME DIRECTORY. It plants exactly one
directory of exactly one fixed name inside a skill-discovery root, and
removes it again, so the probe in backlog item 17 can ask whether that root
reaches the Kimi lane's reviewer. Every refusal pinned here is load-bearing:
the cost of a wrong recursive delete is the user's own files.

The shape that matters, stated once. PLANT is TRANSACTIONAL - if it cannot
emit a state file good enough to remove by, it removes what it created
before exiting, because a half-succeeded plant leaves a directory in a home
with nothing recorded to clean it up, and that is the one residue the
caller's try/finally cannot reach. REMOVE is NOT idempotent - finding
nothing to remove is a failure, not a success, because a removal that
verified nothing has not established the thing it claims. And REMOVE
refuses anything it does not recognise: a canary path that is not exactly
<root>/parallax-home-root-canary, a directory holding anything but the
SKILL.md it planted at the hash it recorded, or a reparse point anywhere
inside it.

Case sensitivity is asserted explicitly. PowerShell's Compare-Object, -eq,
-ne and -contains are all case-INSENSITIVE by default, and this repo has
already shipped one allowlist defeated by exactly that (a tool named `read`
passing a list saying `Read`). A before/after root comparison that folds
case would call a renamed directory unchanged.

The nonce never reaches stdout or stderr. This repo is public and the probe
record is committed, so run_tool scans the raw process output of EVERY
invocation for it rather than trusting one dedicated test.

WINDOWS ONLY: real Windows filesystem semantics - junctions, ordinal name
comparison, profile-root resolution. PARALLAX_PS_HOST selects the host, and
the os.name guard exists because Ubuntu CI supplies pwsh: a selector that
merely finds a host would happily collect these tests there too, same
lesson as test_codex_context_probe.py.
"""
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
TOOL = REPO / "tools" / "plant-home-skill-canary.ps1"

POWERSHELL = (os.environ.get("PARALLAX_PS_HOST")
              or shutil.which("powershell") or shutil.which("pwsh"))

pytestmark = pytest.mark.skipif(
    os.name != "nt" or POWERSHELL is None,
    reason="the canary harness is a Windows tool: it needs a real "
           "PowerShell host, junction support, and profile-root resolution")


def ps_host():
    """PARALLAX_PS_HOST selects the interpreter. A green suite on one
    Windows host proves ONE interpreter."""
    return POWERSHELL


CANARY_NAME = "parallax-home-root-canary"
NONCE = "0123456789abcdef0123456789abcdef"
OTHER_NONCE = "fedcba9876543210fedcba9876543210"
FAULT_VAR = "PARALLAX_CANARY_STATE_FAULT"
FAULT_MESSAGE = (
    "PARALLAX_CANARY_STATE_FAULT injected: simulated state emission failure")
LEFTOVER_MESSAGE = "canary already present: a previous run did not clean up"
PROFILE_ROOT_MESSAGE = "refusing to plant directly in the profile root"
REPARSE_MESSAGE = "canary holds a reparse point; refusing to recurse"

# Every nonce literal this module ever passes in. Checked against raw
# stdout AND stderr on EVERY invocation, so a leak introduced by a future
# case here cannot slip past for want of its own assertion.
ALL_NONCES = (NONCE, OTHER_NONCE)


def run_tool(args, env_overrides=None):
    argv = [ps_host(), "-NoProfile", "-NonInteractive", "-File", str(TOOL)]
    argv += [str(a) for a in args]
    env = dict(os.environ)
    env.pop(FAULT_VAR, None)
    if env_overrides:
        env.update(env_overrides)
    proc = subprocess.run(argv, capture_output=True, text=True, env=env)
    for nonce in ALL_NONCES:
        assert nonce not in proc.stdout, "nonce leaked to stdout"
        assert nonce not in proc.stderr, "nonce leaked to stderr"
    return proc


def names(root):
    """Directory entry names, ordinal-sorted, as the tool records them."""
    return sorted(p.name for p in Path(root).iterdir())


def make_root(tmp_path, entries=("alpha", "Beta", "gamma.md")):
    root = tmp_path / "skills"
    root.mkdir()
    for e in entries:
        if e.endswith(".md"):
            (root / e).write_text("x", encoding="ascii")
        else:
            (root / e).mkdir()
    return root


def plant(root, state_out, nonce=NONCE, env_overrides=None):
    return run_tool(["-Plant", "-Root", root, "-Nonce", nonce,
                     "-StateOut", state_out], env_overrides)


def remove(root, state):
    return run_tool(["-Remove", "-Root", root, "-State", state])


def read_state(path):
    raw = Path(path).read_bytes().decode("ascii")
    lines = [ln for ln in raw.split("\n") if ln.strip()]
    assert len(lines) == 1, "state file must be exactly one nonempty line"
    return json.loads(lines[0])


# --------------------------------------------------------------------------
# Plant
# --------------------------------------------------------------------------

def test_plant_happy_path_writes_the_canary(tmp_path):
    root = make_root(tmp_path)
    state_out = tmp_path / "state.json"
    proc = plant(root, state_out)
    assert proc.returncode == 0, proc.stderr

    skill = root / CANARY_NAME / "SKILL.md"
    assert skill.is_file()
    raw = skill.read_bytes()
    raw.decode("ascii")  # ASCII only; raises otherwise
    body = raw.decode("ascii")
    assert body.count("PARALLAX-CANARY-" + NONCE) == 2, (
        "the marker must appear exactly twice: description and body")
    # It must not name anything else living in the root.
    for other in ("alpha", "Beta", "gamma.md"):
        assert other not in body


def test_plant_state_file_shape(tmp_path):
    root = make_root(tmp_path)
    state_out = tmp_path / "state.json"
    assert plant(root, state_out).returncode == 0

    state = read_state(state_out)
    assert set(state) == {"version", "root", "nonce", "canary",
                          "canarySha256", "before"}
    assert state["version"] == 1
    assert state["nonce"] == NONCE
    assert Path(state["root"]) == root.resolve()
    assert Path(state["canary"]) == (root / CANARY_NAME).resolve()
    assert state["before"] == ["Beta", "alpha", "gamma.md"], (
        "before must be ordinal-sorted, which puts uppercase first")
    assert CANARY_NAME not in state["before"]

    expected = hashlib.sha256(
        (root / CANARY_NAME / "SKILL.md").read_bytes()).hexdigest()
    assert state["canarySha256"] == expected


def test_plant_refuses_a_leftover_canary(tmp_path):
    root = make_root(tmp_path)
    (root / CANARY_NAME).mkdir()
    proc = plant(root, tmp_path / "state.json")
    assert proc.returncode == 1
    assert proc.stderr.strip() == LEFTOVER_MESSAGE


@pytest.mark.parametrize("bad_root", ["", "   "])
def test_plant_refuses_a_blank_root(tmp_path, bad_root):
    proc = plant(bad_root, tmp_path / "state.json")
    assert proc.returncode == 1


@pytest.mark.parametrize("bad_nonce", [
    "", "0123456789ABCDEF0123456789ABCDEF", "0123456789abcdef", "zz" * 16,
    "0123456789abcdef0123456789abcde", "0123456789abcdef0123456789abcdef0",
])
def test_plant_refuses_a_malformed_nonce(tmp_path, bad_nonce):
    root = make_root(tmp_path)
    proc = plant(root, tmp_path / "state.json", nonce=bad_nonce)
    assert proc.returncode == 1
    assert not (root / CANARY_NAME).exists()


def test_plant_refuses_the_profile_root(tmp_path):
    proc = plant(os.environ["USERPROFILE"], tmp_path / "state.json")
    assert proc.returncode == 1
    assert proc.stderr.strip() == PROFILE_ROOT_MESSAGE
    assert not (Path(os.environ["USERPROFILE"]) / CANARY_NAME).exists(), (
        "the refusal must fire BEFORE anything is created")


def test_plant_refuses_a_root_that_does_not_exist(tmp_path):
    proc = plant(tmp_path / "not-there", tmp_path / "state.json")
    assert proc.returncode == 1
    assert not (tmp_path / "not-there").exists(), (
        "it must never conjure the discovery root")


# --------------------------------------------------------------------------
# Plant is transactional
# --------------------------------------------------------------------------

def test_plant_rolls_back_when_the_state_file_cannot_be_written(tmp_path):
    root = make_root(tmp_path)
    before = names(root)
    proc = plant(root, tmp_path / "no-such-dir" / "state.json")
    assert proc.returncode == 1
    assert names(root) == before, "a half-plant must leave nothing behind"


def test_the_fault_seam_reports_and_rolls_back(tmp_path):
    root = make_root(tmp_path)
    before = names(root)
    state_out = tmp_path / "state.json"
    proc = plant(root, state_out, env_overrides={FAULT_VAR: "1"})
    assert proc.returncode == 1
    assert proc.stdout.strip() == ""
    assert proc.stderr.strip() == FAULT_MESSAGE
    assert names(root) == before
    assert not state_out.exists()


def test_the_fault_seam_fires_after_the_canary_exists(tmp_path):
    """The rollback's own positive control.

    Without this, both transactional tests above pass equally against an
    implementation that never created anything at all - they only observe
    the root afterwards. The seam is frozen to fire AFTER the directory and
    its SKILL.md are written, so a run that reports the fault proves the
    directory existed mid-call and was removed on the way out.
    """
    root = make_root(tmp_path)
    state_out = tmp_path / "state.json"
    proc = plant(root, state_out, env_overrides={FAULT_VAR: "1"})
    assert proc.stderr.strip() == FAULT_MESSAGE, (
        "reaching the seam is what proves creation happened first")
    assert not (root / CANARY_NAME).exists()


# --------------------------------------------------------------------------
# Remove
# --------------------------------------------------------------------------

def test_remove_happy_path(tmp_path):
    root = make_root(tmp_path)
    state_out = tmp_path / "state.json"
    before = names(root)
    assert plant(root, state_out).returncode == 0

    proc = remove(root, state_out)
    assert proc.returncode == 0, proc.stderr
    assert not (root / CANARY_NAME).exists()
    assert names(root) == before


def test_remove_fails_when_a_foreign_entry_appeared(tmp_path):
    root = make_root(tmp_path)
    state_out = tmp_path / "state.json"
    assert plant(root, state_out).returncode == 0
    (root / "intruder").mkdir()

    proc = remove(root, state_out)
    assert proc.returncode == 1
    assert "intruder" in proc.stderr


def test_remove_fails_when_an_entry_disappeared(tmp_path):
    root = make_root(tmp_path)
    state_out = tmp_path / "state.json"
    assert plant(root, state_out).returncode == 0
    shutil.rmtree(root / "alpha")

    proc = remove(root, state_out)
    assert proc.returncode == 1
    assert "alpha" in proc.stderr


def test_remove_comparison_is_case_sensitive(tmp_path):
    """PowerShell's default comparers fold case. A root whose entry was
    renamed Beta -> beta is CHANGED, and a case-insensitive comparison
    calls it unchanged."""
    root = make_root(tmp_path)
    state_out = tmp_path / "state.json"
    assert plant(root, state_out).returncode == 0
    (root / "Beta").rename(root / "beta-tmp")
    (root / "beta-tmp").rename(root / "beta")

    proc = remove(root, state_out)
    assert proc.returncode == 1
    assert "beta" in proc.stderr


def test_remove_refuses_a_reparse_point_inside_the_canary(tmp_path):
    root = make_root(tmp_path)
    state_out = tmp_path / "state.json"
    assert plant(root, state_out).returncode == 0
    target = tmp_path / "junction-target"
    target.mkdir()
    subprocess.run(
        [ps_host(), "-NoProfile", "-NonInteractive", "-Command",
         "New-Item -ItemType Junction -Path '{}' -Target '{}' | Out-Null".format(
             root / CANARY_NAME / "link", target)],
        capture_output=True, text=True, check=True)

    proc = remove(root, state_out)
    assert proc.returncode == 1
    assert proc.stderr.strip() == REPARSE_MESSAGE
    assert (root / CANARY_NAME).exists(), "it must stop, not half-delete"


def test_remove_requires_the_exact_canary_path(tmp_path):
    """A hand-edited state file must not be able to aim a recursive delete
    at a sibling the harness never created. "Under the root" is not enough,
    because the delete is recursive on whatever the field names."""
    root = make_root(tmp_path)
    state_out = tmp_path / "state.json"
    assert plant(root, state_out).returncode == 0

    state = read_state(state_out)
    state["canary"] = str((root / "alpha").resolve())
    state_out.write_text(json.dumps(state), encoding="ascii")

    proc = remove(root, state_out)
    assert proc.returncode == 1
    assert (root / "alpha").exists(), "the aimed-at directory must survive"


def test_remove_refuses_an_extra_entry_in_the_canary(tmp_path):
    root = make_root(tmp_path)
    state_out = tmp_path / "state.json"
    assert plant(root, state_out).returncode == 0
    (root / CANARY_NAME / "extra.txt").write_text("x", encoding="ascii")

    proc = remove(root, state_out)
    assert proc.returncode == 1
    assert (root / CANARY_NAME).exists()


def test_remove_refuses_a_changed_skill_file(tmp_path):
    root = make_root(tmp_path)
    state_out = tmp_path / "state.json"
    assert plant(root, state_out).returncode == 0
    (root / CANARY_NAME / "SKILL.md").write_text("tampered", encoding="ascii")

    proc = remove(root, state_out)
    assert proc.returncode == 1
    assert (root / CANARY_NAME).exists()


def test_remove_refuses_a_missing_skill_file(tmp_path):
    root = make_root(tmp_path)
    state_out = tmp_path / "state.json"
    assert plant(root, state_out).returncode == 0
    (root / CANARY_NAME / "SKILL.md").unlink()

    proc = remove(root, state_out)
    assert proc.returncode == 1
    assert (root / CANARY_NAME).exists()


def test_remove_is_not_silently_idempotent(tmp_path):
    """A removal that finds nothing to remove has verified nothing. It must
    say so rather than report the success of an act it never performed."""
    root = make_root(tmp_path)
    state_out = tmp_path / "state.json"
    assert plant(root, state_out).returncode == 0
    shutil.rmtree(root / CANARY_NAME)

    proc = remove(root, state_out)
    assert proc.returncode == 1
    assert proc.stderr.strip() != ""
