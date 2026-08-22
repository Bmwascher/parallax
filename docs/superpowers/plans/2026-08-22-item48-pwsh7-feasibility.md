# Item 48: PowerShell 7 feasibility investigation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a written feasibility record, with a VERDICT, on declaring
PowerShell 7 the supported host for this repo and retiring Windows
PowerShell 5.1.

**Architecture:** The record is assembled in a fixed order: the NO-criteria
are committed BEFORE any measurement, then a mechanically-verified entry
point inventory, then five independent measurements, then the verdict. A
script makes every DETECTED entry point impossible to pass over silently,
by failing on any unclassified match, because both previous hand
inventories of this item were wrong. It does not prove its own filter
catches everything, and the record says so in those words: two reviewers
found four classes the filter missed on the rounds after it was written.

**Tech Stack:** Python 3.12 (survey script and probe drivers), Windows
PowerShell 5.1.26100.9168 and PowerShell 7.6.5, `gh` CLI for CI evidence,
`git grep` and `git ls-files` over tracked files.

**Spec:** `docs/superpowers/plans/2026-07-27-0150-backlog.md`, section
`## Item 48: feasibility of moving EVERYTHING to PowerShell 7`. Read that
section in full before starting any task. Supporting measurement already in
hand: `docs/superpowers/plans/rounds/2026-08-22-item51-inline-brief-probe/probe-record.md`.

## Global Constraints

- **NOTHING IS REPINNED.** No file outside
  `docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/` and
  `docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md` may be
  created, modified or deleted. That includes every file under `tools/`,
  `evals/`, `skills/`, `agents/`, `commands/`, `hooks/`, `.githooks/` and
  `.github/`. Item 48 states this as its own rule: "It must not repin
  anything, it must not delete a 5.1 test".
- **No 5.1 test may be deleted, skipped or marked xfail.** Item 48: "the
  code must become UNABLE to run on 5.1 before it stops being tested
  there."
- **Every claim in the record carries its evidence inline**: a `path:line`
  read during the task, or a command with its captured output. A claim
  written from memory is a plan violation. This item's inventory was wrong
  twice because it recorded what was believed instead of what was read.
- **An unmade measurement is never reported as a clean one.** Where a task
  cannot measure something, it writes a named residual limit saying so.
- **Both hosts count.** Windows PowerShell 5.1 is
  `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`; PowerShell 7
  is `C:\Program Files\PowerShell\7\pwsh.exe`. Use those absolute paths,
  never a bare name resolved from PATH.
- **Dispatch anything that may exceed 600 seconds detached**, from the
  first attempt, using `run_in_background`. The foreground tool ceiling
  kills the caller, not the work, and a killed run is spent effort for
  nothing.
- **The record directory is**
  `docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/`,
  written `<REC>` below. Task 1 creates it; every later task assumes it.
- **Commit after every task**, lowercase imperative subject, no AI
  attribution in the message body.

---

### Task 1: Commit the NO-criteria and the method, before measuring anything

**Files:**
- Create: `<REC>/feasibility-record.md`

**Interfaces:**
- Produces: `<REC>/feasibility-record.md` carrying, in this order, the
  headings `## Verdict`, `## What would make the verdict NO`, `## Method`,
  `## Entry point inventory`, `## Measurement 1: re-exec fidelity`,
  `## Measurement 2: is PowerShell 7 present`,
  `## Measurement 3: behaviour under 7`,
  `## Measurement 4: refusal when pwsh is missing`,
  `## Measurement 5: what is saved`, `## Residual limits`. Later tasks fill
  exactly one section each and MUST NOT reorder or rename them.

- [ ] **Step 1: Create the record directory and the skeleton**

Create `<REC>/feasibility-record.md` with exactly this content:

```markdown
# Feasibility record: moving everything to PowerShell 7 (backlog item 48)

Date started: 2026-08-22 (local, CDT).
Repo: branch `item48-pwsh7-feasibility`, cut from `main` at `6842547`.
Hosts under test: Windows PowerShell 5.1.26100.9168 and PowerShell 7.6.5.
Driver: Opus 5, subagent-driven per task.

**This is an investigation. Nothing in this cycle is repinned and no 5.1
test is deleted.**

## Verdict

NOT YET WRITTEN. Filled by the final task, after every measurement below.

## What would make the verdict NO

Copied verbatim from backlog item 48 BEFORE any measurement was made, so
the answer cannot be shaped by the effort already spent:

- Any entry point that cannot be made to reach 7 - most likely a hook or a
  scheduled task registered outside this repo's control.
- A re-exec that cannot pass arguments through provably intact.
- A user-facing failure mode worse than the bugs being removed.
- Any need to keep a 5.1 code path "just in case", which would mean paying
  for both hosts and testing one.

## Method

The entry point inventory is produced by `survey.py` in this directory and
verified by re-running it, not by rereading it. Two earlier hand
inventories of this item were wrong: the first in three of four entries,
the second in four further ways after claiming to fix the first.

The script matches THREE regex families across every tracked file it can
read, and FAILS if any match lacks a written classification. So a DETECTED
entry point cannot be passed over silently.

It does not do more than that, and this record does not claim it does:

- The families are a filter. They were two when first written, and two
  reviewers then named four live classes the filter missed. It is three
  families now, and there is no argument here that three is enough.
- A green run says every detected match carries a row. It says nothing
  about whether the row is CORRECT.
- A file the script cannot read is listed as `NOT SCANNED`, by name. An
  unread file is not a clean one.

## Entry point inventory

NOT YET WRITTEN.

## Measurement 1: re-exec fidelity

NOT YET WRITTEN.

## Measurement 2: is PowerShell 7 present

NOT YET WRITTEN.

## Measurement 3: behaviour under 7

NOT YET WRITTEN.

## Measurement 4: refusal when pwsh is missing

NOT YET WRITTEN.

## Measurement 5: what is saved

NOT YET WRITTEN.

## Residual limits

NOT YET WRITTEN.
```

- [ ] **Step 2: Verify the NO-criteria are the backlog's own, not a paraphrase**

Write this to `check-nocriteria.py` in the scratchpad and run
`python check-nocriteria.py`:

```python
import io
import re

REC = "docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/feasibility-record.md"
rec = io.open(REC, encoding="utf-8").read()
bl = io.open("docs/superpowers/plans/2026-07-27-0150-backlog.md", encoding="utf-8").read()

start = bl.index("### What would make the verdict NO")
end = bl.index("### What it must NOT do")


def bullets(text):
    """Whole bullets, rejoined across their wrapped lines and normalized.

    A prefix comparison would accept a bullet whose ENDING was rewritten,
    which is the half most likely to be softened. This compares all of it.
    """
    out, cur = [], None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("- "):
            if cur is not None:
                out.append(cur)
            cur = s[2:]
        elif cur is not None and s:
            cur += " " + s
        elif cur is not None:
            out.append(cur)
            cur = None
    if cur is not None:
        out.append(cur)
    return [re.sub(r"\s+", " ", b).strip() for b in out]


want = bullets(bl[start:end])
rstart = rec.index("## What would make the verdict NO")
rend = rec.index("## Method")
got = bullets(rec[rstart:rend])

HEADINGS = ["## Verdict", "## What would make the verdict NO", "## Method",
            "## Entry point inventory", "## Measurement 1: re-exec fidelity",
            "## Measurement 2: is PowerShell 7 present",
            "## Measurement 3: behaviour under 7",
            "## Measurement 4: refusal when pwsh is missing",
            "## Measurement 5: what is saved", "## Residual limits"]
positions = [rec.find(h) for h in HEADINGS]

print("criteria in backlog:", len(want))
print("criteria in record: ", len(got))
print("exact match:", got == want)
print("missing:", [w for w in want if w not in got])
print("headings present and in order:",
      all(p >= 0 for p in positions) and positions == sorted(positions))
raise SystemExit(0 if (len(want) == 4 and got == want
                       and all(p >= 0 for p in positions)
                       and positions == sorted(positions)) else 1)
```

Expected output: `criteria in backlog: 4`, `criteria in record:  4`,
`exact match: True`, `missing: []`,
`headings present and in order: True`, exit code 0.

- [ ] **Step 2b: Replace the skeleton's asserted facts with captured ones**

The skeleton's header states a branch, a base commit and two host versions.
The plan's own Global Constraints call a claim written from memory a
violation, so capture them instead of asserting them. Run:

```bash
git rev-parse --abbrev-ref HEAD
git merge-base main HEAD
"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -Command "$PSVersionTable.PSVersion.ToString()"
"C:\Program Files\PowerShell\7\pwsh.exe" -NoProfile -Command "$PSVersionTable.PSVersion.ToString()"
```

`git merge-base`, not `git rev-parse HEAD`. The field says "cut from `main`
at", and HEAD equals the cut point only while the branch has no commits of
its own — which it will not, since the plan itself lands on the branch
first. Capturing HEAD there would write a false statement produced BY the
fix that was supposed to remove asserted facts.

Edit the record's header lines to carry the four captured values, and add
one line naming these four commands as their source. If a captured value
differs from what the skeleton asserted, the captured value wins.

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/feasibility-record.md
git commit -m "open the item 48 record with its NO-criteria fixed first"
```

---

### Task 2: Write the survey script and prove it FAILS with nothing classified

**Files:**
- Create: `<REC>/survey.py`
- Create: `<REC>/entry-points.tsv`

**Interfaces:**
- Produces: `survey.py`, runnable as `python <REC>/survey.py` (verify) and
  `python <REC>/survey.py --emit` (print TSV stubs for every unclassified
  match). Task 3 consumes both. The final line of a verify run is exactly
  `SURVEY: <total> hits, <classified> classified, <unclassified> unclassified, <stale> stale`
  and the exit code is 0 only when unclassified and stale are both 0.

- [ ] **Step 1: Write the survey script**

Create `<REC>/survey.py` with exactly this content:

```python
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
# .github/workflows/skill-evals.yml:70 - after an earlier version of this
# script carried only the first two families.
#
# THESE THREE FAMILIES ARE A FILTER, NOT A PROOF. They are what is known to
# catch entry points today. A fourth class may exist; the record says so in
# its own words rather than presenting this list as closed.
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
#   - a CI `run:` step, whose host the platform supplies with no token on
#     the line: .github/workflows/skill-evals.yml:71.
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
        r"Start-Process|System\.Diagnostics\.Process|ProcessStartInfo"
        r"|Get-Process\s+-Id\s+\$PID|schtasks|Register-ScheduledTask"
        r"|New-ScheduledTask\w*|subprocess\.(run|Popen|check_output|call)"
        r"|Invoke-Expression|(?<![\w\-])-File(?![\w\-])"),
    "bare": re.compile(
        r"(?<![\w\-])(codex|kimi(-code)?|claude)(\.exe|\.cmd)?\s+[\w\-]"
        r"|[\w\-/\\]+\.ps1(?=\s+-)"
        r"|&\s*['\"]?[\w\-/\\:.$()\[\]]*\.ps1"
        r"|&\s*['\"]?\$[\w:.\[\]]+"
        r"|`[^`]*\.ps1[^`]*`"
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
```

- [ ] **Step 2: Create the classification file with no classifications**

Create `<REC>/entry-points.tsv` with exactly these two lines (the fields
are separated by literal TAB characters, not spaces):

```
# path	line	family	sha	classification	migration
# line "*" classifies every match under a path prefix.
```

- [ ] **Step 3: Commit BEFORE measuring, because the scanner scans itself**

```bash
git add docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/survey.py docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/entry-points.tsv
git commit -m "add the item 48 entry-point survey, failing with nothing classified"
```

This order is load-bearing and is NOT the usual test-then-commit shape.
`survey.py` scans `git ls-files`, and its own source matches its own
families in several places — `pwsh` in the host pattern, and `-File`,
`subprocess.run` and `Start-Process` in the launch pattern, all written out
as literals in the regexes. Until the file is tracked it cannot see itself,
so an N measured before this commit is smaller than the N measured after
it, and Task 3 would inherit a count it could never reproduce. Committing
first makes the two counts the same number.

(Not every literal self-matches — `powershell\.exe` is written escaped and
does not match its own line. The conclusion holds on the ones that do; the
claim is deliberately not "every token in the file matches itself".)

- [ ] **Step 4: Run the survey and verify it FAILS**

Run: `python docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/survey.py`

Expected: a long list of `UNCLASSIFIED <path>:<line> (<family>)` lines, then
a final line reading
`SURVEY: <N> hits, 0 classified, <N> unclassified, 0 stale, <S> files not scanned`,
and **exit code 1**. Record both N and S in the task report, and list every
`NOT SCANNED` path if S is above zero — a file that was not read is not a
file that came back clean.

A pass here would mean the gate cannot fail, which is the one outcome this
script may never produce.

**N is an observation, not a target.** Do not adjust anything to reach a
particular number; report what the run prints.

---

### Task 3: Classify every match, and write the inventory section

**Split this task by FAMILY, one subagent each, in this order: `host`, then
`launch`, then `bare`.** Measured against the repo on 2026-08-22 with the
families exactly as written above, there are about 5169 matches, of which
about 4380 fall under the `docs/` prefix row and about 789 need a
hand-written row: roughly 120 `host`, 241 `launch` and 428 `bare`. One
subagent classifying 789 lines in one pass is how a survey stops being read
and starts being guessed, which is the exact failure this task exists to
prevent.

Each family's task ends on its own `FAMILY <name>: <n> hits, 0 unclassified`
line AND on every EARLIER family's line still reading 0. Checking only your
own family leaves a seam: the `launch` task could delete or overwrite the
`host` task's rows and still report itself green. The whole-survey exit
code stays 1, and that is EXPECTED, until the last family is done — say so
in the task report rather than treating it as a failure.

Every family task COMMITS its own rows before handing over, even though the
survey is still red. An uncommitted TSV between subagents loses work to a
crash, and the plan's own constraint is to commit after every task.

Only the `bare` task runs Steps 3 through 5 below.

A duplicate row is now refused outright by `survey.py`, so two subagents
writing the same match with different classifications stops the survey
instead of last-wins overwriting one of them.

Those counts are what one run printed. They are context for splitting the
work, not a target: report what your own run prints.

**Files:**
- Modify: `<REC>/entry-points.tsv`
- Modify: `<REC>/feasibility-record.md` (section `## Entry point inventory` only)

**Interfaces:**
- Consumes: `survey.py` and its `--emit` mode from Task 2.
- Produces: a green survey run, and the inventory section every later task
  cites when it names an entry point.

- [ ] **Step 1: Emit the stubs**

Run:

```bash
SCRATCH="C:/Users/Brandon/AppData/Local/Temp/claude/C--Users-Brandon-Documents-parallax/90c32d4a-9b49-468b-a954-6e7c5c5a8792/scratchpad/item48"
mkdir -p "$SCRATCH"
python docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/survey.py --emit > "$SCRATCH/stubs.tsv"
wc -l "$SCRATCH/stubs.tsv"
```

The stubs file goes to the scratchpad, NOT the repo. The Global Constraints
forbid creating any repo file outside the record directory, and a working
file in the repo root would break that rule on the plan's own first use.

Expected: one line per unclassified match, matching the N from Task 2.

Take only your own family. The family is field 3:

```bash
awk -F'\t' '$3=="host"' "$SCRATCH/stubs.tsv" | wc -l
awk -F'\t' '$3=="host"' "$SCRATCH/stubs.tsv" > "$SCRATCH/stubs-host.tsv"
```

Substitute `launch` or `bare` for `host` in the family task you are running.

- [ ] **Step 2: Classify every stub by READING the line it points at**

Append the stub rows to `<REC>/entry-points.tsv`, replacing `TODO` with one
value from this closed vocabulary and `unknown` with one of `must-change`,
`no-change`, `unknown`:

| classification | choose it when |
|---|---|
| `host-pin-exec` | the line names a host AND that host is the interpreter for a process this repo starts |
| `host-pin-nonexec` | the line names a host but selects something else (a notification identity, an ancestry allowlist, a version string) |
| `launch-inherit` | the line starts a process under whatever host is already running |
| `launch-explicit` | the line starts a process under a host it names itself |
| `launch-nonhost` | the line starts a process that is not a PowerShell host (python, git, codex, kimi) |
| `test-harness` | the line is test code that drives a host or a launch |
| `ci` | the line is a CI workflow declaration |
| `doc-instruction` | the line is prose telling a human or an agent to run something |
| `fixture` | the line is test data and is never executed |
| `record` | the line is a historical record and is never executed |

Rules that are NOT judgment calls:

- **Open the file and read the line.** The classification must come from
  the line and its surrounding code, never from the path or from this
  plan's expectations. Round 7 of a previous debate found three of four
  entries wrong precisely because they were written from belief.
- **`docs/` may be covered by one prefix row, WITH an exception.** Add
  exactly this row (TAB separated), and no other prefix rows:
  `docs/	*	*	-	record	no-change`
  Then add an EXPLICIT per-line row for every match inside the record
  directory AND for every match in this plan file itself,
  `docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md`. An
  explicit row wins over a prefix row in `survey.py`, so this works without
  changing the script.
  **Why the exception exists.** `record` is defined as "never executed", and
  the blanket row would apply it to `survey.py`, to the probe scripts Tasks
  4 and 7 create, and to this plan — all of which ARE executed, this plan by
  its own first line. A green survey would then attest "never executed" over
  running code. Reviewers on both lanes found this independently on
  2026-08-22, and a later round found that the first version of this
  exception named the plan as its reason while scoping itself to the record
  directory, which does not contain the plan.
  **This exception is a STANDING RULE, not a one-time step.** Tasks 4 and 7
  create new tracked files under the record directory that carry family
  matches — `reexec/parent.ps1` alone has `-File` and `ProcessStartInfo`,
  and `run.py` carries both host paths and `subprocess.run`. Any task that
  adds a file under the record directory adds its explicit rows BEFORE its
  own commit. Without that, the blanket row silently absorbs them and Task 9's
  re-run comes back green with executed scripts attested "never executed" —
  the same defect one task later, which is how it was found.
- **A line matching both families produces TWO rows**, one per family, and
  they may carry different classifications.
- **`migration` is `must-change` only if a move to PowerShell 7 would have
  to edit that line.** If you cannot tell from the line and its file, write
  `unknown` and say why in Step 3. `unknown` is an honest answer here;
  a guess is not.

- [ ] **Step 3: Run the survey and verify it PASSES**

Run: `python docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/survey.py`

Expected: no `UNCLASSIFIED` and no `STALE` lines, three
`FAMILY <name>: <n> hits, 0 unclassified` lines, a final
`SURVEY: <N> hits, <N> classified, 0 unclassified, 0 stale, <S> files not scanned`,
and **exit code 0**.

In the `host` and `launch` tasks, only your own family's line reads 0 and
the exit code is still 1. That is the expected outcome for those tasks, and
it is what their report states.

**State what this green run proves and nothing more.** It proves every
detected match carries a syntactically valid row, and that no row points at
a line that has changed or gone. It does NOT prove any classification is
CORRECT, and it does not prove the three families detect every entry point.
Write that sentence into the record in Step 4 rather than letting the green
run speak for itself.

- [ ] **Step 4: Write the inventory section**

Replace `NOT YET WRITTEN.` under `## Entry point inventory` in
`<REC>/feasibility-record.md` with:

1. The survey's final line, verbatim.
2. A count per classification, produced by this command and pasted as a
   table:

```bash
awk -F'\t' '!/^#/ && NF==6 {print $5}' docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/entry-points.tsv | sort | uniq -c | sort -rn
```

3. A list of EVERY row whose migration value is `must-change`, one line
   each as `path:line — what a migration must do to it`.
4. A list of EVERY row whose migration value is `unknown`, one line each,
   saying what could not be determined from the line.
5. The sentence from Step 3 stating exactly what the green run proves.
6. A subsection `### What this method cannot see`, naming each of these and
   why the method misses it:
   - the versioned plugin cache copy of `hooks/hooks.json`, which is what
     actually runs and only changes on a version bump plus `plugin update`;
   - an already-registered scheduled task, which keeps the host written
     into its action at registration time;
   - any instruction a human or agent follows that is not written in a
     tracked file;
   - any file listed as `NOT SCANNED` by the survey, by name;
   - a classification that is syntactically valid and semantically wrong,
     which no run of this script can detect.
   End the subsection with this sentence, which is the point of it:
   **this list is not itself provably complete, and a blind-spot list that
   reads as complete is the same defect one level up.** The third regex
   family exists because two reviewers found two classes the first two
   families missed, after that list had already been written once.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/
git commit -m "classify every entry-point match and write the item 48 inventory"
```

---

### Task 4: Measurement 1 — can a 5.1 script re-exec into 7 with arguments intact

**Files:**
- Create: `<REC>/reexec/child.ps1`
- Create: `<REC>/reexec/child-named.ps1`
- Create: `<REC>/reexec/parent.ps1`
- Create: `<REC>/reexec/parent-named.ps1`
- Create: `<REC>/reexec/run.py`
- Modify: `<REC>/feasibility-record.md` (section `## Measurement 1: re-exec fidelity` only)

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `<REC>/reexec/results.json`, and the measurement section.

This is the measurement that can produce a NO. Item 48: "A re-exec that
cannot pass arguments through provably intact" is a stated NO-criterion,
and the 2026-08-22 item 51 probe already measured Windows PowerShell 5.1
building a command line that corrupts embedded quotes.

- [ ] **Step 1: Write the child, which records what it actually received**

Create `<REC>/reexec/child.ps1` with exactly this content:

```powershell
$enc = New-Object System.Text.UTF8Encoding($false)
$lines = @()
foreach ($a in $args) {
  $bytes = [System.Text.Encoding]::UTF8.GetBytes([string]$a)
  $lines += (($bytes | ForEach-Object { '{0:x2}' -f $_ }) -join '')
}
[System.IO.File]::WriteAllText($env:PROBE_CHILD_OUT, ($lines -join "`n"), $enc)
```

- [ ] **Step 2: Write the parent, which records what IT received and then forwards**

Create `<REC>/reexec/parent.ps1` with exactly this content:

```powershell
$enc = New-Object System.Text.UTF8Encoding($false)
$lines = @()
foreach ($a in $args) {
  $bytes = [System.Text.Encoding]::UTF8.GetBytes([string]$a)
  $lines += (($bytes | ForEach-Object { '{0:x2}' -f $_ }) -join '')
}
[System.IO.File]::WriteAllText($env:PROBE_PARENT_OUT, ($lines -join "`n"), $enc)

function Esc([string]$s) {
  $s = $s -replace '(\\*)"', '$1$1\"'
  $s = $s -replace '(\\+)$', '$1$1'
  return '"' + $s + '"'
}

if ($env:PROBE_FORM -eq 'splat') {
  & $env:PROBE_TARGET_HOST -NoProfile -ExecutionPolicy Bypass -File $env:PROBE_CHILD @args
} else {
  $cmd = '-NoProfile -ExecutionPolicy Bypass -File ' + (Esc $env:PROBE_CHILD)
  foreach ($a in $args) { $cmd = $cmd + ' ' + (Esc ([string]$a)) }
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = $env:PROBE_TARGET_HOST
  $psi.Arguments = $cmd
  $psi.UseShellExecute = $false
  $proc = [System.Diagnostics.Process]::Start($psi)
  $proc.WaitForExit()
}
```

- [ ] **Step 3: Write the driver**

Create `<REC>/reexec/run.py` with exactly this content:

```python
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


def main():
    results = {}
    for host_name, host in (("ps51", PS51), ("pwsh7", PWSH)):
        for form in ("splat", "escaped"):
            results["%s/%s" % (host_name, form)] = run(host, form)
    (HERE / "results.json").write_text(
        json.dumps(results, indent=1), encoding="utf-8")
    print(json.dumps(results, indent=1))

    # The task needs an oracle that can FAIL, not a script that always
    # exits 0 while the prose promises someone will notice. Any arm whose
    # child never ran, or whose stage A did not survive, is a red run.
    broken = [k for k, v in results.items()
              if v["returncode"] != 0 or not v["stage_a_parent_exact"]
              or v["stage_b_child_count"] is None]
    if broken:
        print("ARMS THAT DID NOT MEASURE ANYTHING: %s" % ", ".join(sorted(broken)))
        return 1
    # Stage B failing is a RESULT, not an error: it is what a NO looks
    # like. It is reported, and it does not fail the run.
    print("all four arms ran; stage B exact: %s"
          % {k: v["stage_b_child_exact"] for k, v in sorted(results.items())})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Add the NAMED-PARAMETER arm**

Positional `$args` is not the shape a real migration forwards. Most shipped
scripts in this repo declare named parameters — `tools/check-drift.ps1:30-34`
declares `[switch]$Register`, `[switch]$TestNotify` and `[switch]$NoAutoTriage` —
so a probe that only forwards positional arguments answers a narrower
question than the one item 48 asks.

**"Most", not "every".** `hooks/superpowers-review-companion.ps1:12-13` has
no `param()` block at all and reads its input from stdin. An earlier draft
of this paragraph said every shipped script declares named parameters,
which was false about a file the glob in Task 6 had just been widened to
include.

**The parent needs its own named parameters too.** A real migration re-execs
a script whose OWN parameters were already bound by the caller, then
forwards those bound values. A parent that only carries `$args` measures
binding at the child and never measures forwarding FROM a bound parent, so
this step adds a second parent rather than reusing the positional one.

Create `<REC>/reexec/child-named.ps1` with exactly this content:

```powershell
param(
  [switch]$Register,
  [string]$RouteNote,
  [string]$Path
)
$enc = New-Object System.Text.UTF8Encoding($false)
$obj = @{
  register  = [bool]$Register
  routeNote = $RouteNote
  path      = $Path
}
[System.IO.File]::WriteAllText($env:PROBE_CHILD_OUT,
  ($obj | ConvertTo-Json -Compress -Depth 3), $enc)
```

Then add this function to `run.py`, and call it for both hosts and both
forms, storing the results under keys `"<host>/<form>/named"`:

```python
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
    # SAME KEY NAMES as run(), so main() can treat every arm alike. An
    # earlier draft returned a different key set, which made main()'s
    # checks raise KeyError on exactly these arms.
    return {
        "returncode": proc.returncode,
        "stderr": proc.stderr.strip()[:400],
        "stage_a_parent_exact": parent_bound == NAMED_EXPECTED,
        "stage_a_parent_count": None if parent_bound is None else len(NAMED),
        "stage_b_child_exact": child_bound == NAMED_EXPECTED,
        "stage_b_child_count": None if child_bound is None else len(NAMED),
        "sent_count": len(NAMED),
        "first_difference": None,
        "parent_bound": parent_bound,
        "child_bound": child_bound,
    }
```

Create `<REC>/reexec/parent-named.ps1` with exactly this content. It is the
positional parent with a `param()` block in front and its OWN bound values
forwarded, rather than `$args`:

```powershell
param(
  [switch]$Register,
  [string]$RouteNote,
  [string]$Path
)
$enc = New-Object System.Text.UTF8Encoding($false)
$mine = @{
  register  = [bool]$Register
  routeNote = $RouteNote
  path      = $Path
}
[System.IO.File]::WriteAllText($env:PROBE_PARENT_OUT,
  ($mine | ConvertTo-Json -Compress -Depth 3), $enc)

$forward = @()
if ($Register) { $forward += '-Register' }
$forward += '-RouteNote'; $forward += $RouteNote
$forward += '-Path';      $forward += $Path

function Esc([string]$s) {
  $s = $s -replace '(\\*)"', '$1$1\"'
  $s = $s -replace '(\\+)$', '$1$1'
  return '"' + $s + '"'
}

if ($env:PROBE_FORM -eq 'splat') {
  & $env:PROBE_TARGET_HOST -NoProfile -ExecutionPolicy Bypass -File $env:PROBE_CHILD @forward
} else {
  $cmd = '-NoProfile -ExecutionPolicy Bypass -File ' + (Esc $env:PROBE_CHILD)
  foreach ($a in $forward) { $cmd = $cmd + ' ' + (Esc ([string]$a)) }
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = $env:PROBE_TARGET_HOST
  $psi.Arguments = $cmd
  $psi.UseShellExecute = $false
  $proc = [System.Diagnostics.Process]::Start($psi)
  $proc.WaitForExit()
}
```

Then DELETE the `main()` function written in Step 3 and put exactly this in
its place, so every arm carries the same keys and one check covers all
eight. Do not merge the two by hand — the file must end with one `main()`:

```python
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
              or v["stage_b_child_count"] is None]
    if broken:
        print("ARMS THAT DID NOT MEASURE ANYTHING: %s"
              % ", ".join(sorted(broken)))
        return 1
    print("all eight arms ran; stage B exact: %s"
          % {k: v["stage_b_child_exact"] for k, v in sorted(results.items())})
    return 0
```

- [ ] **Step 5: Run it**

Run: `python docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/reexec/run.py`

Expected: eight result blocks, exit code 0, and a final line listing stage
B per arm.

Exit code 1 means at least one arm measured NOTHING — a nonzero return
code, a child that never wrote its file, or a stage A that did not survive.
In that case the task STOPS and reports which arm and which condition. Per
the driver's docstring, a stage-A failure is reported as **either** a probe
defect **or** the host's own `-File` parsing mangling arguments before the
script sees them; decide which by reading `parent-out.txt` against the
payload, and say which one it was.

A stage B of `false` is a RESULT, not a failure. It is what a NO looks
like, and it is recorded as a finding.

- [ ] **Step 6: Write the measurement section**

Replace `NOT YET WRITTEN.` under `## Measurement 1: re-exec fidelity` with:

1. An eight-row table: host, forwarding form, positional or named, return
   code, whether the child ran, stage A exact, stage B exact (or
   `bound_exact` for the named arms), and the index of the first differing
   argument. **The return code and the child-ran column are not optional**:
   without them a child that never started tabulates identically to a child
   that received corrupt arguments.
2. Both payload lists, verbatim, so a reader knows exactly what was tried.
3. One paragraph answering the NO-criterion in its own words: whether a
   re-exec CAN pass these argument shapes through intact, under which
   forwarding form, and on which host.
4. **State the claim at the width of the evidence.** This measures ten
   positional payload shapes and one named-parameter set. It does not
   establish anything about ARBITRARY arguments, and the record must not
   say it does. If the NO-criterion's word "arbitrary" is to be answered at
   all, the record says which shapes were covered and which were not.
5. Residual limits, naming what was not covered: arguments above the
   32767-character command line ceiling measured on 2026-08-22; the host's
   own `-File` parameter parsing, measured end-to-end here rather than
   isolated; parameter shapes not tried, including arrays, `ValueFromRemainingArguments`,
   and a script that re-execs ITSELF rather than a sibling.

- [ ] **Step 7: Add explicit inventory rows for the files this task created**

The standing rule in Task 3 applies here. `child.ps1`, `child-named.ps1`,
`parent.ps1` and `run.py` all carry family matches, and the `docs/` blanket
row would otherwise classify them `record — never executed`. Run:

```bash
SCRATCH="C:/Users/Brandon/AppData/Local/Temp/claude/C--Users-Brandon-Documents-parallax/90c32d4a-9b49-468b-a954-6e7c5c5a8792/scratchpad/item48"
python docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/survey.py --emit \
  | grep "2026-08-22-item48-pwsh7-feasibility/reexec" > "$SCRATCH/stubs-reexec.tsv"
wc -l "$SCRATCH/stubs-reexec.tsv"
```

Classify every row and append it to `<REC>/entry-points.tsv`. These are
`test-harness` / `no-change`: they are this investigation's own probes and
no migration edits them. Then confirm none is left prefix-covered:

```bash
python docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/survey.py --emit \
  | grep -c "2026-08-22-item48-pwsh7-feasibility/reexec"
```

Expected: `0`.

- [ ] **Step 8: Commit**

```bash
git add docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/
git commit -m "measure a 5.1 to 7 re-exec against eleven argument shapes"
```

---

### Task 5: Measurement 2 — is PowerShell 7 actually present where this must run

**Files:**
- Modify: `<REC>/feasibility-record.md` (section `## Measurement 2: is PowerShell 7 present` only)

**Interfaces:**
- Consumes: the inventory from Task 3, to name which entry points the
  answer has to cover.

- [ ] **Step 1: Read what the CI workflow declares**

Run:

```bash
grep -n "runs-on\|shell:\|pwsh\|powershell" .github/workflows/skill-evals.yml
```

Record every runner image and every declared shell, with line numbers.

- [ ] **Step 2: Get evidence from a real CI run, not from the file alone**

Run:

```bash
gh run list --workflow skill-evals.yml --limit 5 --json databaseId,headSha,status,conclusion,createdAt
```

Then, for the most recent successful run id `<ID>`:

```bash
gh run view <ID> --json jobs --jq '.jobs[] | {name, conclusion, startedAt, completedAt, runnerName}'
```

Expected: the `powershell-hosts` job present and successful. A green
`powershell-hosts` job that runs `pwsh` on the Windows runner is direct
evidence that PowerShell 7 exists there; say so with the job name and run
id, and do not generalise past what the job actually ran.

**Bind the evidence to the revision it came from.** The run's metadata and
the workflow file in the working tree are two different things: a job that
passed last week ran the workflow as it stood at that commit, which may not
be the text just read in Step 1. Read the workflow AT the run's own SHA:

```bash
gh run view <ID> --json headSha --jq '.headSha'
git show <headSha>:.github/workflows/skill-evals.yml | grep -n "runs-on\|shell:\|pwsh\|powershell"
```

If that differs from Step 1's output, the difference is the finding: say
which lines moved and which claim rests on which revision. If `git show`
fails because the SHA is not present locally, say so and record the
evidence as revision-unbound rather than treating the working tree as a
stand-in.

- [ ] **Step 3: Answer the Linux side separately**

Determine whether ANY step in the `ubuntu-latest` job invokes `pwsh`. Read
the WHOLE job, not the lines just after `runs-on`:

```bash
awk '/^  skill-evals:/{f=1} f&&/^  [a-z-]+:/&&!/^  skill-evals:/{exit} f' .github/workflows/skill-evals.yml | grep -n "pwsh\|powershell\|shell:\|run:"
```

An earlier version of this step ran `grep -A4` after `runs-on`, which reads
about four lines of a job that runs from `.github/workflows/skill-evals.yml:16`
to `:47`. That command could not answer the question the step asks, which
is the same defect this plan exists to avoid: a check narrower than its
claim.

If no Linux step invokes `pwsh`, then PowerShell 7's presence on the Linux
runner is UNPROVEN by this repo's own evidence. Write that as an unproven
statement, not as an absence of a problem.

- [ ] **Step 4: Answer the local user side**

Run:

```bash
where.exe pwsh
"C:\Program Files\PowerShell\7\pwsh.exe" -NoProfile -Command "$PSVersionTable.PSVersion.ToString()"
```

Record the result. Then handle the preinstall question carefully, because
it is the one claim in this task that this machine cannot measure.

**Do not assert that PowerShell 7 is absent from a stock Windows install as
though it were measured here.** This machine has it. The Global Constraints
forbid a claim written from memory, and "no user has it unless they
installed it" is exactly that. Write it in one of these two forms and no
other:

- Cited: quote Microsoft's own installation documentation, with the URL and
  the date read, saying PowerShell 7 is a separate install.
- Or labelled `background knowledge, not measured here`, followed by what
  would prove it: a stock Windows image, a CI runner with no PowerShell 7
  step, or a user report.

Then note the already-known half-requirement: `hooks/hooks.json` invokes
its hook as `pwsh`, so anyone using the hooks already needs 7 installed.
Cite the line number from the inventory rather than from memory.

- [ ] **Step 5: Write the measurement section**

Replace `NOT YET WRITTEN.` under `## Measurement 2: is PowerShell 7 present`
with a short subsection per environment — Windows CI runner, Linux CI
runner, developer machine, plugin user's machine — each carrying its
evidence or the words "unproven, and here is what would prove it".

- [ ] **Step 6: Commit**

```bash
git add docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/
git commit -m "record where PowerShell 7 is proven present and where it is not"
```

---

### Task 6: Measurement 3 — which host-sensitive behaviours are already proven under 7

**Files:**
- Modify: `<REC>/feasibility-record.md` (section `## Measurement 3: behaviour under 7` only)

**Interfaces:**
- Consumes: the inventory from Task 3, AND the revision-bound successful CI
  run id from Task 5 Step 2, which is the only evidence in this
  investigation that anything PASSED under PowerShell 7.

Item 48's warning is precise: "Not 'does it start'. 0.16.0's lock STARTED
fine on 7 and did not lock." So this task maps COVERAGE, and does not
re-run the suite.

- [ ] **Step 1: List the modules the dual-host CI job actually runs**

Run:

```bash
grep -n -B4 -A25 "powershell-hosts" .github/workflows/skill-evals.yml
```

Record, with line numbers, exactly which test modules the job re-runs under
both hosts and how that list is selected.

- [ ] **Step 2: List the shipped scripts and mark which are covered**

Run:

```bash
git ls-files 'tools/*.ps1' '.githooks/*' 'evals/tools/*.ps1' 'hooks/*.ps1'
```

**Do not write a count into the heading or the record before running this.**
An earlier version of this step said "the 13 shipped scripts" ahead of the
command that counts them, which is the defect item 48 records about its own
first inventory. Report the number the command prints.

`hooks/*.ps1` is in the glob deliberately: `hooks/superpowers-review-companion.ps1`
is a shipped script, and the CHECKOUT's `hooks/hooks.json:10` and `:22`
invoke it as bare `pwsh`. Both reviewers found it missing from an earlier
version of this glob.

**Say that at the width of the evidence.** An earlier draft called it "the
ONLY one already running under PowerShell 7 in production". What was read
was the checkout, and this plan states elsewhere that the versioned plugin
cache is what actually runs and only changes on a version bump plus
`plugin update`. No task here inspects the cache. Either read it and cite
it:

```bash
python -c "import json;d=json.load(open(r'C:/Users/Brandon/.claude/plugins/installed_plugins.json'));print([v for k,v in d['plugins'].items() if 'parallax' in k])"
```

then read `hooks/hooks.json` inside that `installPath` and cite both — or
write the claim about the CHECKOUT only and say the installed copy was not
inspected.

For each script, find candidate covering modules:

```bash
grep -rln "<script-basename>" evals/
```

**A grep hit is a mention, not coverage.** A comment, a constant, a fixture
path or an assertion about the script's TEXT all match. For each candidate,
open it and decide which of these it is, and put that word in the table:

- `runs` — the module actually invokes the script as a process, and the
  invocation is in the module. Cite the line.
- `reads` — the module only reads or asserts on the script's text.
- `mentions` — neither; the name appears incidentally.

Produce a table: script, covering module, `runs`/`reads`/`mentions` with a
line citation, and whether that module is in the dual-host job from Step 1.
Only `runs` rows count as behaviour proven under a host.

- [ ] **Step 3: Name the host-sensitive behaviours with NO coverage under 7**

The known 5.1-specific traps, each already measured in this repo, are
listed in backlog item 48 under "5.1 is where the traps live". For each,
say whether a test exercises the same behaviour under 7, citing the test
file and line, or write "no coverage under 7".

- [ ] **Step 4: Write the measurement section**

**What "proven" is allowed to mean here.** A `runs` row says a module
invokes the script. It does not say that module PASSED under PowerShell 7.
The evidence for passing is a successful CI run of the dual-host job,
which Task 5 gathered and bound to its own revision. Cite that run id in
this section, and where you cannot, write `exercised, pass not evidenced
here` rather than `proven`.

Replace `NOT YET WRITTEN.` under `## Measurement 3: behaviour under 7` with
the two tables from Steps 2 and 3, and one paragraph stating how much of
the shipped surface is exercised under 7 today and how much of that is
evidenced by a green run. Do not estimate a percentage
that the tables do not support.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/
git commit -m "map which shipped behaviour is proven under PowerShell 7"
```

---

### Task 7: Measurement 4 — what a user sees when pwsh is missing

**Files:**
- Create: `<REC>/missing-pwsh/probe.py`
- Modify: `<REC>/feasibility-record.md` (section `## Measurement 4: refusal when pwsh is missing` only)

**Interfaces:**
- Consumes: the inventory from Task 3, for the entry points that already
  require `pwsh`.

Item 48's requirement: "It must stop with a message naming what to install.
It must never silently continue on 5.1, and it must never report a
measurement it did not make." Today exactly one shipped entry point already
requires `pwsh` — the hook in `hooks/hooks.json` — so that is the one whose
current failure mode can be measured.

- [ ] **Step 1: Read what the hook actually invokes**

Run:

```bash
cat hooks/hooks.json
```

Record the exact command string, with its line number.

- [ ] **Step 2: Write the probe**

Create `<REC>/missing-pwsh/probe.py` with exactly this content:

```python
#!/usr/bin/env python3
"""What does a caller see when `pwsh` cannot be resolved?

The hook is invoked as a bare `pwsh`, so its failure mode when PowerShell 7
is absent is decided by PATH resolution. This runs the hook's OWN
invocation shape with a PATH stripped of every directory containing pwsh,
and captures what that call produced. Nothing is modified: the real PATH is
untouched outside this child process.

What this captures is what THIS caller saw. Claude Code's hook runner may
present a failure differently, and that presentation was not measured here.
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent


def stripped_path():
    keep = []
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        if not entry:
            continue
        candidate = Path(entry) / "pwsh.exe"
        if candidate.exists():
            continue
        keep.append(entry)
    return os.pathsep.join(keep)


def main():
    env = dict(os.environ)
    env["PATH"] = stripped_path()
    still_there = shutil.which("pwsh", path=env["PATH"])
    result = {
        "pwsh_on_real_path": shutil.which("pwsh"),
        "pwsh_after_stripping": still_there,
    }
    # The SHIPPED shape, not a convenient one. hooks/hooks.json:10 invokes
    # `pwsh -NoProfile -NonInteractive -File <script>`; a `-Command
    # Write-Output ok` call would measure a different caller path and then
    # be written up as what the hook shows a user.
    hook_script = str(HERE.parents[5] / "hooks"
                      / "superpowers-review-companion.ps1")
    result["invocation"] = ["pwsh", "-NoProfile", "-NonInteractive",
                            "-File", hook_script]
    # stdin MUST be closed and there MUST be a timeout. The hook's first
    # act is [Console]::In.ReadToEnd() (hooks/superpowers-review-companion.ps1:13).
    # With inherited stdin and no timeout, the SUCCESS path - the one this
    # probe pre-names as a finding - launches the real hook and blocks
    # forever, and no oracle fires. The convenient `-Command Write-Output ok`
    # this replaced could not hang; the faithful shape can.
    try:
        proc = subprocess.run(
            result["invocation"],
            capture_output=True, text=True, env=env, shell=False,
            stdin=subprocess.DEVNULL, timeout=60)
    except subprocess.TimeoutExpired:
        result["outcome"] = "timed out after 60s"
        result["returncode"] = None
        result["stdout"] = ""
        result["stderr"] = ""
        (HERE / "results.json").write_text(json.dumps(result, indent=1),
                                           encoding="utf-8")
        print(json.dumps(result, indent=1))
        return
    result["returncode"] = proc.returncode
    result["stdout"] = proc.stdout.strip()
    result["stderr"] = proc.stderr.strip()
    (HERE / "results.json").write_text(json.dumps(result, indent=1),
                                       encoding="utf-8")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Run it**

Run: `python docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/missing-pwsh/probe.py`

Expected: `pwsh_after_stripping` is `null`. Then exactly one of three
outcomes, and the record names WHICH:

- **The call fails to find `pwsh`.** Report the error or traceback text
  verbatim. Call it "what THIS caller saw", not "the user-facing failure
  mode": Claude Code's own hook runner may present it differently and was
  not measured here.
- **The call succeeds anyway.** See the paragraph below. Absence was not
  reproduced, and no failure text exists to report.
- **The call times out.** The hook read stdin and nothing closed it. Report
  it as a probe defect and fix the probe.

If `pwsh_after_stripping` is NOT null, the strip failed and nothing was
measured; say so and stop rather than reporting a clean result.

**One outcome that is a finding rather than a broken probe.** On Windows,
when the executable is named without a full path, the process-creation call
resolves it using the PARENT process's environment, not the child
environment being passed in. So the call may SUCCEED even with `PATH`
stripped. If that happens, record it as measured behaviour — the strip
proved the resolution ignores the supplied environment — and say plainly
that this probe therefore did NOT reproduce a machine without PowerShell 7.
Do not report the success as evidence that the failure mode is benign. Name
what would prove it instead: a machine, container or CI runner with
PowerShell 7 genuinely absent.

- [ ] **Step 4: Write the measurement section**

Replace `NOT YET WRITTEN.` under
`## Measurement 4: refusal when pwsh is missing` with:

1. Which of the three outcomes from Step 3 occurred, named explicitly.
2. If a failure was produced: its text verbatim in a fenced block, and one
   sentence on whether that text names what to install. If it does not, say
   so plainly: an undeclared prerequisite failing obscurely is worse than a
   declared one, and item 48 names that as a NO-criterion.
   If NO failure was produced: write that no failure text exists because
   absence was not reproduced, and do not substitute a description of what
   a failure would probably look like.
3. Named residual limits: only the bare-`pwsh` resolution path was measured;
   entry points that today name `powershell.exe` were not, since nothing
   about them changes until a migration edits them; and the harness's own
   presentation of a hook failure was not measured by this probe.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/
git commit -m "measure the failure a caller sees when pwsh is absent"
```

---

### Task 8: Measurement 5 — what the change actually saves

**Files:**
- Modify: `<REC>/feasibility-record.md` (section `## Measurement 5: what is saved` only)

**Interfaces:**
- Consumes: the CI run ids gathered in Task 5.

- [ ] **Step 1: Pull real job durations from the last five successful runs**

Run:

```bash
gh run list --workflow skill-evals.yml --limit 10 --json databaseId,conclusion,headSha --jq '.[] | select(.conclusion=="success") | .databaseId'
```

For each of the first five ids `<ID>`, pull STEP timings, not job timings:

```bash
gh run view <ID> --json jobs --jq '.jobs[] | {job: .name, steps: [.steps[] | {name, startedAt, completedAt}]}'
```

Compute the duration in minutes of the two steps named
`PowerShell-facing tests under Windows PowerShell 5.1` and
`PowerShell-facing tests under PowerShell 7`, and of the whole
`powershell-hosts` job.

**Job duration is the wrong unit and would overstate the saving.** The two
hosts are separate sequential STEPS inside one job
(`.github/workflows/skill-evals.yml:93` and `:110`), and the same job also
pays for checkout, Python setup and pytest install (`:61-71`), which a
migration does not remove. Only the 5.1 step's own time is removed by
dropping 5.1.

If a run's step timings are unavailable through `gh`, say so and mark that
run's row as unmeasured rather than substituting the job duration.

- [ ] **Step 2: Write the measurement section**

Replace `NOT YET WRITTEN.` under `## Measurement 5: what is saved` with:

1. A table of the five runs: run id, `powershell-hosts` job duration, the
   5.1 step duration, the 7 step duration.
2. The GROSS saving from dropping the 5.1 step, stated as a RANGE across
   those five runs, not as one number.
3. **The NET saving is not determined by this task**, and the record says
   so: a migration keeps some cases that start from 5.1 to prove the
   refusal and the re-exec, and which cases those are is decided in Task 9.
   State gross here, and state that net is bounded above by it.
4. The already-recorded local pair, cited from backlog item 48 rather than
   re-measured: 32m23s under 5.1 against 18m33s under pwsh at the same
   head, and a second pair of 20m22s against 18m50s, with item 48's own
   caveat that the 5.1 spread is wider than the gap.
5. Item 44's 57 minutes across three serial passes, cited by item number,
   and the GROSS upper bound this change could remove from it. Not a net
   figure: the retained-case decision has not been made yet, and a sentence
   saying how much "this change would remove" would state as known a number
   that Task 9 has not yet determined.

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/
git commit -m "record the measured cost of the dual-host matrix"
```

---

### Task 9: Write the verdict and the residual limits

**Files:**
- Modify: `<REC>/feasibility-record.md` (sections `## Verdict` and
  `## Residual limits` only)

**Interfaces:**
- Consumes: every section written by Tasks 3 through 8.

- [ ] **Step 1: Re-run the survey, so the inventory is current at verdict time**

Run: `python docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/survey.py`

Expected: exit code 0, `0 unclassified, 0 stale`. If it fails, the verdict
is not written until Task 3's classification is repaired.

Then check that the sections the verdict rests on were actually written:

```bash
grep -n "NOT YET WRITTEN" docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/feasibility-record.md
```

Expected: at most ONE hit, and it must be inside `## Verdict`, which this
task is about to replace. Any other remaining `NOT YET WRITTEN` means a
measurement section was never filled, and the verdict is not written until
it is. Without this check, every command in this plan passes over a verdict
written on top of an empty Measurement 3.

- [ ] **Step 2: Collect the residual limits, BEFORE anything is adjudicated**

Replace `NOT YET WRITTEN.` under `## Residual limits` with every residual
limit written by Tasks 3 through 8, gathered into one list, each naming the
section it came from. Add any limit of the investigation as a whole: one
machine, one ANSI code page, one Claude Code version, and the fact that no
script was run under a migration it does not yet have.

This comes first because Step 4's rules gate the verdict on these. An
earlier draft collected them after the verdict was written, so the rule
that was supposed to force CONDITIONAL pointed at a list that did not
exist yet.

- [ ] **Step 3: Answer item 48's open questions, BEFORE the verdict**

Two of item 48's required answers are not NO-criteria, so a verdict written
first would not be forced to consider them. Write them first, as
subsections under `## Verdict`:

- `### What the test matrix becomes`. Item 48 states the expected shape and
  marks it as a guess: "probably not 'one host' but 'one host plus a small
  number of cases proving the refusal and the re-exec work when started
  from 5.1'". Answer it from Task 4's and Task 7's measurements, name the
  cases that must survive, and say which exist today and which would be
  new. If the measurements do not decide it, say so rather than repeating
  the guess as a conclusion.
- `### Questions item 48 asked that this investigation did not answer`.
  List them by name, each with what would answer it.

- [ ] **Step 4: Answer each NO-criterion, and REPLACE the verdict placeholder**

Delete the line `NOT YET WRITTEN. Filled by the final task, after every
measurement below.` under `## Verdict`. It is the only remaining
placeholder at this point, and nothing later removes it: say so explicitly,
because an earlier draft said only "write subsections" and would have
shipped the record with that sentence still standing under the verdict.

Add a subsection per NO-criterion, in the order they appear under
`## What would make the verdict NO`, each answering exactly one of **MET**,
**NOT MET**, or **UNKNOWN**, and citing the measurement section that
decides it.

**UNKNOWN is a permitted and sometimes correct answer**, and it is what
stops a verdict from being wider than its evidence. Use it whenever the
measurement that would decide the criterion was not made, was inconclusive,
or was made on ground narrower than the criterion. Three known ways this
happens, each already anticipated by an earlier task:

- Task 5 may record an environment as `unproven`.
- Task 6 may record a script or a host-sensitive behaviour as having no
  coverage under 7.
- Task 7 may fail to reproduce a machine without PowerShell 7 at all.

Then one line:
`**VERDICT: YES** | **VERDICT: NO** | **VERDICT: CONDITIONAL ON <x>**`,
followed by at most one paragraph of reasoning.

The rules that produce that line, in order:

1. Any criterion **MET** produces **NO**.
2. Any criterion **UNKNOWN** produces **CONDITIONAL**, naming what is
   unknown. It can never produce YES.
3. Any `migration=unknown` row in the inventory that bears on criterion 1
   ("any entry point that cannot be made to reach 7") produces
   **CONDITIONAL**, listing those rows by `path:line`. The survey gates on
   unclassified and stale only and never reads the migration column, so
   nothing else would catch this.
4. Any residual limit from the `## Residual limits` list written in Step 2
   that a reader could reasonably say bears on a criterion must be
   explicitly dispositioned in that criterion's subsection — "does not bear
   on this, because X" — or it produces **CONDITIONAL**.
5. **YES** requires every criterion NOT MET with a citation to a
   measurement, no bearing unknowns, and every material residual
   dispositioned. A criterion answered from reasoning rather than from a
   measurement is UNKNOWN, not NOT MET.

- [ ] **Step 5: If the verdict is YES or CONDITIONAL, draft the migration item**

Append to `<REC>/feasibility-record.md` a final section
`## Draft: the migration item`, written in the same shape as the backlog's
other items: Problem, What would close it, ordered work, and Priority. It
must include, as a hard ordering rule taken from item 48: the code becomes
UNABLE to run on 5.1 BEFORE any 5.1 test is deleted. It must also name
backlog items 51 and 31 as absorbed by it, since both defects are 5.1-only.

It cites the test-matrix answer already written in Step 2 rather than
restating it, and its ordered work must be consistent with it.

Do NOT edit `docs/superpowers/plans/2026-07-27-0150-backlog.md` in this
task. The backlog edit happens at merge, not here.

- [ ] **Step 6: Re-run both gates, now that the record is finished**

```bash
python docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/survey.py
grep -n "NOT YET WRITTEN" docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/feasibility-record.md
```

Expected: survey exit code 0, and the grep finds NOTHING — exit code 1 from
grep, with no output. Step 1 tolerated one placeholder under `## Verdict`
because the verdict had not been written; by now nothing may remain. Without
this second run, the tolerance granted in Step 1 is never withdrawn.

- [ ] **Step 7: Commit**

```bash
git add docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/
git commit -m "write the item 48 verdict against its own NO-criteria"
```

---

## Debate record

**Participants:** not yet dispatched
**Rounds used:** 0 of 12
**Outcome:** pending
**Verification status:** pending
**Degradation:** none
**Authorized by:** n/a
**Raw rounds:** `docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/`

### Resolved points
| # | Claim | Raised by | Outcome | Evidence |
|---|-------|-----------|---------|----------|
| — | none yet | — | — | — |

### Escalated points (user-decided)
| # | Question | Session position | Reviewer position | Owner's call |
|---|----------|------------------|-------------------|--------------|
| — | none yet | — | — | — |
