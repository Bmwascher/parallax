#!/usr/bin/env python3
"""Measure whether a 5.1 script can re-exec into 7 with arguments intact.

Two stages, because only the second is the question and the first is what
makes it meaningful. Stage A is what the PARENT received; stage B is what
the CHILD received after the parent forwarded them.

A stage-A failure is NOT automatically a broken probe. Python builds an
exact command line, but the host's own `-File` argument parsing sits
between that command line and `$args`, and that parsing is part of what a
migration would depend on. So a stage-A failure means one of two things -
this probe is wrong, or the host mangles arguments before a script ever
sees them - and the task must say which before going further. Calling it
"the probe is broken" would file a real finding under housekeeping.
"""
import json
import os
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
PS51 = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
PWSH = r"C:\Program Files\PowerShell\7\pwsh.exe"

# Hostile on purpose. Every one of these appears in a real brief, a real
# path or a real flag somewhere in this repo.
PAYLOAD = [
    "plain",
    "has space",
    'has"quote',
    'odd"quote"count"',
    "em\u2014dash",
    "",
    "trailing\\",
    "semi;colon &amp",
    "$var and `backtick`",
    "-looks-like-a-flag",
]


def hexed(items):
    return [a.encode("utf-8").hex() for a in items]


def read_dump(path):
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    return text.split("\n") if text else []


def run(host, form):
    parent_out = HERE / "parent-out.txt"
    child_out = HERE / "child-out.txt"
    for p in (parent_out, child_out):
        if p.exists():
            p.unlink()
    env = dict(os.environ)
    env.update({
        "PROBE_PARENT_OUT": str(parent_out),
        "PROBE_CHILD_OUT": str(child_out),
        "PROBE_CHILD": str(HERE / "child.ps1"),
        "PROBE_TARGET_HOST": PWSH,
        "PROBE_FORM": form,
    })
    proc = subprocess.run(
        [host, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
         str(HERE / "parent.ps1")] + PAYLOAD,
        capture_output=True, text=True, timeout=300, env=env)
    want = hexed(PAYLOAD)
    got_parent = read_dump(parent_out)
    got_child = read_dump(child_out)
    return {
        "returncode": proc.returncode,
        "stderr": proc.stderr.strip()[:400],
        "stage_a_parent_exact": got_parent == want,
        "stage_a_parent_count": None if got_parent is None else len(got_parent),
        "stage_b_child_exact": got_child == want,
        "stage_b_child_count": None if got_child is None else len(got_child),
        "sent_count": len(want),
        "first_difference": next(
            (i for i, w in enumerate(want)
             if got_child is None or i >= len(got_child) or got_child[i] != w),
            None),
    }


NAMED = ["-Register", "-RouteNote", 'a "quoted" note \u2014 here',
         "-Path", "C:\\dir with space\\"]
NAMED_EXPECTED = {"register": True,
                  "routeNote": 'a "quoted" note \u2014 here',
                  "path": "C:\\dir with space\\"}


def run_named(host, form):
    """Same two stages as run(), so the results are comparable.

    Stage A here is the PARENT's own bound parameters, written by
    parent-named.ps1. Without it this arm would have no control at all,
    and the arm that can produce a NO is the last place to drop one.
    """
    child_out = HERE / "child-out.json"
    parent_out = HERE / "parent-out.json"
    for p in (child_out, parent_out):
        if p.exists():
            p.unlink()
    env = dict(os.environ)
    env.update({
        "PROBE_PARENT_OUT": str(parent_out),
        "PROBE_CHILD_OUT": str(child_out),
        "PROBE_CHILD": str(HERE / "child-named.ps1"),
        "PROBE_TARGET_HOST": PWSH,
        "PROBE_FORM": form,
    })
    proc = subprocess.run(
        [host, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
         str(HERE / "parent-named.ps1")] + NAMED,
        capture_output=True, text=True, timeout=300, env=env)

    def load(path):
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except ValueError:
            return "unparseable"

    parent_bound = load(parent_out)
    child_bound = load(child_out)
    # "unparseable" is a BROKEN ARM, not a failed comparison. Without this,
    # a child that emitted garbage JSON would compare unequal to
    # NAMED_EXPECTED and be reported as stage B false - filed as evidence
    # toward a NO by an arm that measured nothing about argument fidelity.
    broken_output = "unparseable" in (parent_bound, child_bound)
    # SAME KEY NAMES as run(), so main() can treat every arm alike. An
    # earlier draft returned a different key set, which made main()'s
    # checks raise KeyError on exactly these arms.
    return {
        "returncode": proc.returncode,
        "stderr": proc.stderr.strip()[:400],
        "stage_a_parent_exact": (not broken_output
                                 and parent_bound == NAMED_EXPECTED),
        # A COUNT OF WHAT CAME BACK, never the count of what was sent. The
        # first draft returned len(NAMED) whenever the file merely existed,
        # which is a sent count wearing a received count's name - and it
        # read as a clean number even for the unparseable case.
        "stage_a_parent_count": (len(parent_bound)
                                 if isinstance(parent_bound, dict) else None),
        "stage_b_child_exact": (not broken_output
                                and child_bound == NAMED_EXPECTED),
        "stage_b_child_count": (len(child_bound)
                                if isinstance(child_bound, dict) else None),
        "sent_count": len(NAMED_EXPECTED),
        # The first PARAMETER that differs, by name. `None` here would be
        # indistinguishable from "nothing differed", and the measurement
        # table asks every arm for a first difference.
        #
        # Compare the UNION of expected and received keys. Iterating only
        # the expected ones returns None when the child bound everything
        # correctly AND added a parameter nobody sent - stage B is false,
        # and the field that says WHY says nothing. The current child
        # writes exactly the three expected keys so that state is not
        # reachable today; the field is written not to lie if it ever is.
        "first_difference": next(
            (k for k in sorted(set(NAMED_EXPECTED)
                               | (set(child_bound)
                                  if isinstance(child_bound, dict) else set()))
             if not isinstance(child_bound, dict)
             or child_bound.get(k) != NAMED_EXPECTED.get(k)),
            None),
        "unparseable_output": broken_output,
        "parent_bound": parent_bound,
        "child_bound": child_bound,
    }


def main():
    results = {}
    for host_name, host in (("ps51", PS51), ("pwsh7", PWSH)):
        for form in ("splat", "escaped"):
            results["%s/%s/positional" % (host_name, form)] = run(host, form)
            results["%s/%s/named" % (host_name, form)] = run_named(host, form)
    (HERE / "results.json").write_text(
        json.dumps(results, indent=1), encoding="utf-8")
    print(json.dumps(results, indent=1))

    broken = [k for k, v in results.items()
              if v["returncode"] != 0 or not v["stage_a_parent_exact"]
              or v["stage_b_child_count"] is None
              or v.get("unparseable_output")]
    if broken:
        print("ARMS THAT DID NOT MEASURE ANYTHING: %s"
              % ", ".join(sorted(broken)))
        return 1
    print("all eight arms ran; stage B exact: %s"
          % {k: v["stage_b_child_exact"] for k, v in sorted(results.items())})
    # Remove the per-arm scratch files. Only results.json is a deliverable;
    # the four *-out.* files are overwritten by every arm and hold nothing
    # the JSON does not. Leaving them behind put build products next to the
    # sources and broke the staging assertion in Step 7.
    for name in ("parent-out.txt", "child-out.txt",
                 "parent-out.json", "child-out.json"):
        p = HERE / name
        if p.exists():
            p.unlink()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
