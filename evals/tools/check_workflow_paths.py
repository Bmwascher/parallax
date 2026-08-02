#!/usr/bin/env python3
"""check_workflow_paths.py - pure Python guard for the GitHub Actions
workflow's file-path and dual-host-module references (0.13.x, backlog
Task 1).

Why this exists: `775472c` deleted
`evals/multi-model-verify/test_kimi_lane_lock.py` and
`tools/kimi-lane-lock.ps1` but never touched the workflow, which still
named the dead test path. `python -m pytest <dead path> -q` exits 4 with
"file or directory not found" - a merge-blocking break the ubuntu job
itself cannot catch, because nothing there re-parses the Windows job's
steps. This script is invoked BY the ubuntu job (Tier 2b), so it has to be
pure Python with no platform branch: no `os.name` guard, no PowerShell
call-out.

Two checks, not one:

1. Every `evals/...py` token named anywhere in the workflow resolves to a
   READABLE REGULAR FILE. Plain existence is not the state that matters -
   a DIRECTORY named `test_something.py` exists happily and `is_file()`
   would report it correctly, but an implementation that stops at
   `exists()` would not. READABILITY is frozen as successfully OPENING the
   file for binary reading: only an actual open establishes the file can
   be read, so that is what this checks, not `exists()` or `is_file()`
   alone.
2. HOST PARITY: a declared set of required dual-host modules must be
   present in BOTH Windows PowerShell-facing pytest steps. Existence alone
   is not an oracle here either - a module omitted from one host step
   still exists on disk and stays green under a existence-only check.
   Finding the two host steps in the first place is part of that
   measurement, not a precondition assumed true: an unmade measurement is
   never a clean one, so discovering zero, one, or an unexpected host name
   is a reported error, not a vacuous pass. Renaming PARALLAX_PS_HOST,
   breaking the host-step pattern, or deleting the Windows job entirely
   must all fail this check rather than silently verify nothing.

   Discovered steps are kept as a LIST, not a dict keyed by host: a dict
   lets a SECOND step for the same host name silently overwrite the
   first, discarding both its module set and the fact that two steps
   exist under one name before parity is ever checked. The discovered
   host MULTISET must be exactly one `powershell.exe` and one `pwsh.exe`
   - the multiset, not the set - because two `powershell.exe` steps plus
   one `pwsh.exe` step collapse to the same SET as the correct pair while
   never establishing "both steps" for the doubled host. Required modules
   are then checked in EACH preserved step, not once per host name.
"""
import collections
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "skill-evals.yml"

# The initial required set is exactly these four - the modules that survive
# in the workflow once the orphaned test_kimi_lane_lock.py reference is
# removed. Not the implementer's to choose or extend here; a later task
# adds its own named modules to this set.
REQUIRED_DUAL_HOST_MODULES = [
    "evals/multi-model-verify/test_attestation.py",
    "evals/multi-model-verify/test_codex_context_probe.py",
    "evals/multi-model-verify/test_review_mirror.py",
    "evals/multi-model-verify/test_kimi_round_evidence.py",
    "evals/multi-model-verify/test_kimi_lane_lock.py",
    "evals/multi-model-verify/test_lock_protocol_live.py",
    "evals/multi-model-verify/test_kimi_credential_state.py",
    "evals/multi-model-verify/test_kimi_lane_login.py",
    "evals/multi-model-verify/test_kimi_lane_home.py",
    "evals/multi-model-verify/test_lane_credential_live_support.py",
]

# The dual-host pair this workflow runs, and the ONLY set that counts as
# "both Windows pytest steps found". check_host_parity refuses rather than
# passing vacuously if discovery turns up anything else - zero steps, one,
# or an unexpected host name all mean the measurement was not made.
REQUIRED_HOST_NAMES = {"powershell.exe", "pwsh.exe"}

_PY_TOKEN_RE = re.compile(r"evals/[\w./-]+\.py")
# A Windows PowerShell-facing pytest step is identified by carrying
# PARALLAX_PS_HOST in its env block; the two such steps are exactly the
# dual-host pair this workflow runs. Captures the host value and the run
# block text up to the next step (indented "- name:") or end of file.
_HOST_STEP_RE = re.compile(
    r"PARALLAX_PS_HOST:\s*(\S+).*?run:\s*(.*?)(?=\n\s*- name:|\Z)",
    re.DOTALL,
)


def _open_binary(path):
    """Indirection point only, so a test can simulate a deterministic
    PermissionError/OSError on a specific path without depending on a real
    Windows ACL denial, which machine behaviour a test may not rely on."""
    return open(path, "rb")


def extract_py_tokens(workflow_text):
    """Every evals/...py path token named anywhere in the workflow text."""
    return sorted(set(_PY_TOKEN_RE.findall(workflow_text)))


def extract_windows_host_steps(workflow_text):
    """Every discovered Windows PowerShell-facing step, as a LIST of
    (host, module-set) pairs - one entry per step found, in document
    order. Not a dict keyed by host: keying by host would let a second
    step for the same host silently overwrite the first, losing both its
    module set and the fact that two steps exist under that name."""
    steps = []
    for match in _HOST_STEP_RE.finditer(workflow_text):
        host, run_block = match.group(1), match.group(2)
        steps.append((host, set(_PY_TOKEN_RE.findall(run_block))))
    return steps


def check_paths_readable(tokens, base_dir):
    """Every token must resolve to a READABLE REGULAR FILE. A stat or
    readability failure is FATAL: an unmade or failed measurement is never
    a clean one."""
    errors = []
    for token in tokens:
        path = base_dir / token
        try:
            handle = _open_binary(path)
        except OSError as exc:
            errors.append(
                "unreadable path referenced in workflow, not a readable "
                "test file: {} ({})".format(token, exc))
        else:
            handle.close()
    return errors


def check_host_parity(host_steps, required, required_hosts=REQUIRED_HOST_NAMES):
    """Every required dual-host module must appear in EACH Windows
    PowerShell-facing pytest step.

    `host_steps` is a LIST of (host, module-set) pairs, one per step
    discovered - never a dict, which would let a second step for the same
    host silently overwrite the first before parity is ever checked.

    Discovering the two host steps is part of the measurement: a guard
    that cannot be evaluated REFUSES rather than passing vacuously. The
    discovered host MULTISET must be exactly one of each name in
    `required_hosts` - the multiset, not the set - because two
    `powershell.exe` steps plus one `pwsh.exe` step collapse to the same
    SET as the correct pair while never establishing "both steps" for the
    doubled host. Anything else - none, one, an unexpected host name, or
    a duplicated one - is reported as an error and never read as clean
    parity."""
    discovered_counts = collections.Counter(host for host, _ in host_steps)
    required_counts = collections.Counter(required_hosts)
    if discovered_counts != required_counts:
        return [
            "could not find the expected Windows dual-host pytest steps: "
            "required exactly one of each of {}, discovered {}".format(
                sorted(required_hosts),
                sorted(discovered_counts.elements()))
        ]
    errors = []
    for host, modules in sorted(host_steps, key=lambda pair: pair[0]):
        missing = sorted(set(required) - modules)
        for token in missing:
            errors.append(
                "required dual-host module missing from host step {}: {}"
                .format(host, token))
    return errors


def check_workflow(workflow_path=WORKFLOW_PATH, base_dir=REPO_ROOT,
                    required=REQUIRED_DUAL_HOST_MODULES):
    """Runs both checks against a workflow file and returns a list of
    error strings - empty when clean."""
    text = workflow_path.read_text(encoding="utf-8")
    tokens = extract_py_tokens(text)
    errors = check_paths_readable(tokens, base_dir)
    host_steps = extract_windows_host_steps(text)
    errors += check_host_parity(host_steps, required)
    return errors


def main():
    errors = check_workflow()
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
