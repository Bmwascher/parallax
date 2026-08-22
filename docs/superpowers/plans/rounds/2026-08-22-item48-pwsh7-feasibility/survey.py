#!/usr/bin/env python3
"""Entry-point survey for backlog item 48.

This matches THREE regex families across every tracked file it can read,
and fails on any match carrying no written classification. Two hand
inventories of this item shipped wrong, so the gate exists to stop a match
being passed over silently.

WHAT IT DOES AND DOES NOT ESTABLISH. It makes a DETECTED match impossible
to ignore. It does not prove the families detect every entry point - they
are a filter, and the third family was added only after reviewers found two
classes the first two missed. It does not prove any classification is
correct. And a file it could not read is REPORTED rather than counted
clean.

Usage:
    python survey.py           verify every match is classified and current
    python survey.py --emit    print TSV stubs for the unclassified matches
"""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True, check=True,
                           cwd=str(HERE)).stdout.strip())
TSV = HERE / "entry-points.tsv"

# Family 1 names a host. Family 2 starts a process without necessarily
# naming one. Family 3 covers the two ways a run can start with NEITHER a
# host name nor a launch verb on the line: a bare invocation of a native
# client or a `.ps1` path, and a CI `run:` step whose host the platform
# chooses. Both were found by reviewers on 2026-08-22 with live instances -
# tools/check-drift.ps1:1060, skills/multi-model-verify/SKILL.md:94, and
# .github/workflows/skill-evals.yml:71 - after an earlier version of this
# script carried only the first two families.
#
# THESE THREE FAMILIES ARE A FILTER, NOT A PROOF.
#
# THIS COMMENT IS THE SINGLE SOURCE FOR THE CORRECTION COUNT. Every other
# place that mentions it - the plan's Architecture paragraph, the record
# skeleton's Method section, Task 3's blind-spot instruction - points HERE
# instead of repeating a number. The count was restated in three places and
# went stale in two of them twice, which is its own instance of the defect
# this plan is about, so the duplication is removed rather than
# re-synchronised again.
#
# THE CORRECTIONS, enumerated. Across FIVE review rounds a reviewer
# produced a live entry point this filter did not match NINE times:
#   1-2. two classes prompted the third family at all;
#   3-4. two more widened it (call operator through a variable; flagless
#        instruction invocations);
#   5.   Start-Job joined the launch family;
#   6.   the line-wrapped backtick form;
#   7-8. the generic call operator with a literal command, and bare
#        `python`;
#   9.   bare `agy`, the Flash implementer's client - live at
#        agents/flash-implementer.md:47 and :78, and used across six
#        non-docs files.
#
# Nobody has produced a tenth. That is the only honest statement available,
# and it is not the same as saying there is none.
#
# ONE KNOWN MISS IS LEFT IN DELIBERATELY, with its instance named. Bare
# `git` invocations - tools/check-drift.ps1:987, `git -C $worktree commit`
# - are NOT matched. Matching bare `git` costs 179 further hits, almost all
# of them prose and shell plumbing, against a class that never starts a
# PowerShell host. That is a measured trade and not an empty set: the
# instance above is real and is not in the inventory.
#
# The third family matches INVOCATION shapes rather than every mention of a
# script. Its alternatives, and why each is here, all measured 2026-08-22:
#
#   - a literal client name followed by a word: tools/check-drift.ps1:1060
#     (the item 31 site) and :500.
#   - a `.ps1` followed by a flag: skills/multi-model-verify/SKILL.md:94.
#   - a `.ps1` after the call operator, and the call operator applied to a
#     VARIABLE: tools/new-kimi-lane-home.ps1:152 and
#     tools/new-kimi-lane-login.ps1:214 both run `& $LockScript @LockArgs`
#     with the path assigned at new-kimi-lane-home.ps1:96, and
#     new-kimi-lane-login.ps1:442 runs `& $KimiBinaryPath "login"`. This
#     alternative also catches evals/tools/drift_statemachine_tests.ps1:552,
#     which launches a HOST through a variable - the dual-host harness
#     itself, which no other family sees.
#   - a backticked or dot-slash `.ps1` with no flag after it: README.md:392
#     and CLAUDE.md:41, both instructions to run a shipped script by hand,
#     which is entry point 6 in item 48's own survey.
#   - a backticked invocation whose flags WRAP to the next line, so the
#     `.ps1` ends the line with the backtick still open:
#     skills/multi-model-verify/references/backup-lane.md:119, :136 and
#     :141. This scanner reads one line at a time, so without this
#     alternative the first line has no flag and the second has no `.ps1`.
#   - a CI `run:` step, whose host the platform supplies with no token on
#     the line: .github/workflows/skill-evals.yml:71.
#
# `Start-Job` is in the LAUNCH family rather than here, for one token. It
# spawns a child of the CURRENT host, and tools/check-drift.ps1:1054 is the
# job the codex dispatch runs inside - so that line decides which host the
# background dispatch child gets. No family saw it until round 3.
#
# THE NARROWING IS STILL REAL AND IS STILL A TRADE. Matching every `.ps1`
# mention gives 251 hits outside docs/ against 96 for the invocation
# shapes. The 155 not matched were NOT read one by one, so nothing here
# says they are all harmless - only that they do not carry an invocation
# shape. The first draft of this comment claimed they "were prose
# references that no migration would edit", which was a statement about 155
# lines nobody had opened, and a reviewer found two counterexamples inside
# the dropped set on the next round.
FAMILIES = {
    "host": re.compile(r"powershell\.exe|(?<![\w.\-])pwsh(\.exe)?(?![\w\-])",
                       re.IGNORECASE),
    "launch": re.compile(
        r"Start-Process|Start-Job|System\.Diagnostics\.Process|ProcessStartInfo"
        r"|Get-Process\s+-Id\s+\$PID|schtasks|Register-ScheduledTask"
        r"|New-ScheduledTask\w*|subprocess\.(run|Popen|check_output|call)"
        r"|Invoke-Expression|(?<![\w\-])-File(?![\w\-])"),
    "bare": re.compile(
        r"(?<![\w\-])(codex|kimi(-code)?|claude|agy)(\.exe|\.cmd)?\s+[\w\-]"
        r"|[\w\-/\\]+\.ps1(?=\s+-)"
        r"|&\s*['\"]?[\w\-/\\:.$()\[\]]*\.ps1"
        r"|&\s*['\"]?\$[\w:.\[\]]+"
        r"|&\s*['\"]?[a-z][\w\-]*(\.exe)?(?![\w\-/\\.])"
        r"|(?<![\w\-/\\.])python(\.exe)?\s+[\w\-]"
        r"|`[^`]*\.ps1[^`]*`"
        r"|`[^`]*\.ps1\s*$"
        r"|(?<![\w\-])\.[\\/][\w\-/\\.]*\.ps1"
        r"|^\s*-?\s*run:\s*\S"),
}

# Closed vocabulary. A migration answers a different question for each of
# these, which is why one bucket would be useless.
CLASSES = {
    "host-pin-exec":    "names a host AND that host runs a process we start",
    "host-pin-nonexec": "names a host but selects something else",
    "launch-inherit":   "starts a process under the CURRENT host",
    "launch-explicit":  "starts a process under a host it names itself",
    "launch-nonhost":   "starts a process that is not a PowerShell host",
    "test-harness":     "test code that drives a host or a launch",
    "ci":               "a CI workflow declaration",
    "doc-instruction":  "prose instructing a human or an agent to run it",
    "fixture":          "test data, never executed",
    "record":           "historical record, never executed",
    "not-a-launch":     "matched the filter but starts no process at all",
}
MIGRATION = {"must-change", "no-change", "unknown"}

# A prefix row never covers a file under `docs/` whose name ends,
# case-sensitively, in one of EXEMPT_SUFFIXES below, or that matches
# EXEMPT_EXACT exactly. That is the WHOLE test - not "any executable
# file", which this comment claimed twice before and which the code has
# never actually enforced. A `.BAT`, `.PSM1`, `.SH`, or an upper-cased
# `.PS1`/`.PY`/`.CMD` under `docs/` would still be swallowed by a prefix
# row as `record - never executed`; none exists in this repo today
# (checked directly: `git ls-files 'docs/*'` has no such name, in any
# case), so this is a stated, checked scope limit on the guard, not a
# silent gap in it.
#
# Enforced HERE rather than by an instruction, because an instruction to
# "add explicit rows" had no oracle: `--emit` prints only UNCLASSIFIED
# matches, and a prefix-covered match is not unclassified, so the check
# written to prove the rows existed printed zero either way. That fail-open
# gate was itself written while closing a fail-open gate.
#
# THE TEST IS THE SUFFIX, not a list of exact paths, and not conjoined with
# a prefix either - fixed at the final whole-branch review, which found the
# suffix test ANDed with EXEMPT_PREFIXES below, so it only fired inside this
# one item-48 directory. A `.py`/`.ps1` anywhere else under `docs/` fell
# through to the general prefix loop and was swallowed by the `docs/`
# prefix row as `record - never executed` - the exact attestation this
# comment says must never happen. Latent on this branch (`git ls-files
# 'docs/*'` filtered to `.py`/`.ps1` returns exactly the 7 files this
# investigation itself created, all with explicit rows already), but this
# script is meant to outlive the branch (the migration draft's own ordered
# work re-runs it), so the guard is widened now rather than left narrower
# than the invariant it states. Everything else the investigation writes
# under its own directory - `feasibility-record.md`, `entry-points.tsv`,
# `results.json`, the probe scratch files - IS a record and is correctly
# covered by the `docs/` prefix row, because none of them end in `.py` or
# `.ps1`; the suffix test alone already draws that line without needing a
# prefix to narrow it. An earlier version exempted the whole directory and
# then carved two files back out by name; that left every generated
# sidecar exempt, so a result file would have needed hand rows keyed to
# line numbers that change on every re-run, and the record's own growing
# prose would have gone stale and blocked Task 9 for a reason that is not
# an entry point.
#
# `.cmd` ADDED at the whole-branch review's Fable seat: the comment above
# already claimed "anywhere under docs/", but the code only tested `.py`
# and `.ps1` - the widening fix left a narrower version of the exact gap
# it closed. This repo has a live `.cmd` executable this record itself
# classifies `must-change`
# (`evals/multi-model-verify/fixtures/stub-appserver/stub-appserver.cmd`),
# so the suffix list is widened to match what the comment already claimed,
# not narrowed to match what the code enforced. `git ls-files 'docs/*'`
# has no `.cmd` today, so this is latent, the same way `.py`/`.ps1` were.
#
# THIRD occurrence of this comment overclaiming what the code enforces -
# widened twice already (`.py`/`.ps1` freed from EXEMPT_PREFIXES, then
# `.cmd` added), and each fix reproduced a narrower version of the same
# gap. Debate round 1 stops widening the tuple: the opening paragraph
# above now states EXACTLY the test the code runs - suffix, case-
# sensitive, exact-path - instead of a general "any executable file"
# claim the code was never going to fully enforce. Widening the tuple
# again would only postpone the next instance; stating the true scope
# ends the class, because there is no narrower truth left to overclaim.
EXEMPT_SUFFIXES = (".py", ".ps1", ".cmd")
EXEMPT_EXACT = (
    "docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md",
)


def digest(line):
    return hashlib.sha1(line.strip().encode("utf-8")).hexdigest()[:12]


def tracked_files():
    out = subprocess.run(["git", "ls-files", "-z"], capture_output=True,
                         check=True, cwd=str(REPO)).stdout
    return [p for p in out.decode("utf-8").split("\0") if p]


def scan():
    """Returns (hits, skipped).

    A file this cannot read is REPORTED, never silently dropped. "Matched
    across every tracked file" would otherwise be wider than the evidence:
    an unreadable file and a clean file would look identical.
    """
    hits = {}
    skipped = []
    for rel in tracked_files():
        path = REPO / rel
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except (OSError, ValueError) as exc:
            skipped.append((rel, "unreadable: %s" % exc.__class__.__name__))
            continue
        if "\0" in text[:4096]:
            skipped.append((rel, "binary: NUL in first 4096 characters"))
            continue
        for n, line in enumerate(text.splitlines(), 1):
            for fam, rx in FAMILIES.items():
                if rx.search(line):
                    hits[(rel, n, fam)] = digest(line)
    return hits, skipped


def load_rows():
    rows = {}
    prefixes = []
    seen_prefixes = set()
    if not TSV.exists():
        return rows, prefixes
    for raw in TSV.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.startswith("#"):
            continue
        parts = raw.split("\t")
        if len(parts) != 6:
            sys.exit("malformed row (want 6 tab-separated fields): %r" % raw)
        rel, line, fam, dg, cls, mig = parts
        if cls not in CLASSES:
            sys.exit("unknown classification %r in row %r" % (cls, raw))
        if mig not in MIGRATION:
            sys.exit("unknown migration value %r in row %r" % (mig, raw))
        if line == "*":
            key = (rel, fam)
            if key in seen_prefixes:
                sys.exit("duplicate prefix row for %s (%s)" % (rel, fam))
            seen_prefixes.add(key)
            prefixes.append((rel, fam, cls, mig))
        else:
            key = (rel, int(line), fam)
            # A duplicate is REFUSED, never last-wins. Classification is
            # split across three subagents; two rows for one match with
            # different classifications would otherwise be invisible to
            # every check here, including the per-family counts, which
            # count matches rather than rows.
            if key in rows:
                sys.exit("duplicate row for %s:%s (%s) - two classifications "
                         "for one match" % (rel, line, fam))
            rows[key] = (dg, cls, mig)
    return rows, prefixes


def covered_by_prefix(key, prefixes):
    rel, _, fam = key
    if rel in EXEMPT_EXACT:
        return False
    if rel.endswith(EXEMPT_SUFFIXES):
        return False
    for prel, pfam, _, _ in prefixes:
        if rel.startswith(prel) and (pfam == "*" or pfam == fam):
            return True
    return False


def main():
    hits, skipped = scan()
    rows, prefixes = load_rows()
    unclassified = [k for k in hits
                    if k not in rows and not covered_by_prefix(k, prefixes)]
    stale = [k for k, v in rows.items()
             if k not in hits or hits[k] != v[0]]

    if "--emit" in sys.argv:
        for rel, n, fam in sorted(unclassified):
            print("\t".join([rel, str(n), fam, hits[(rel, n, fam)],
                             "TODO", "unknown"]))
        return 0

    for rel, n, fam in sorted(unclassified):
        print("UNCLASSIFIED %s:%d (%s)" % (rel, n, fam))
    for rel, n, fam in sorted(stale):
        why = "gone" if (rel, n, fam) not in hits else "line changed"
        print("STALE %s:%d (%s) - %s" % (rel, n, fam, why))
    for rel, why in sorted(skipped):
        print("NOT SCANNED %s - %s" % (rel, why))
    # Per-family progress, so classification can be split across tasks and
    # each one still has an oracle of its own. Without it the only signal
    # is the whole-survey exit code, which stays red until the last row is
    # written and therefore measures nothing in between.
    for fam in sorted(FAMILIES):
        fam_hits = [k for k in hits if k[2] == fam]
        fam_unc = [k for k in unclassified if k[2] == fam]
        print("FAMILY %s: %d hits, %d unclassified"
              % (fam, len(fam_hits), len(fam_unc)))
    print("SURVEY: %d hits, %d classified, %d unclassified, %d stale, "
          "%d files not scanned"
          % (len(hits), len(hits) - len(unclassified), len(unclassified),
             len(stale), len(skipped)))
    return 1 if (unclassified or stale) else 0


if __name__ == "__main__":
    raise SystemExit(main())
