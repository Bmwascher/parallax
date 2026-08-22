# Item 48: PowerShell 7 feasibility investigation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a written feasibility record, with a VERDICT, on declaring
PowerShell 7 the supported host for this repo and retiring Windows
PowerShell 5.1.

**Architecture:** The record is assembled in a fixed order: the NO-criteria
are committed BEFORE any measurement, then a mechanically-verified entry
point inventory, then five independent measurements, then the verdict. The
inventory's completeness is enforced by a script that fails on any
unclassified match, because both previous hand inventories of this item
were wrong.

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
the second in four further ways after claiming to fix the first. The
script matches two regex families across every tracked file and FAILS if
any match lacks a written classification, so a missed entry point is a red
gate rather than a silent omission.

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
rec = io.open("docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/feasibility-record.md", encoding="utf-8").read()
bl = io.open("docs/superpowers/plans/2026-07-27-0150-backlog.md", encoding="utf-8").read()
start = bl.index("### What would make the verdict NO")
end = bl.index("### What it must NOT do")
want = [l.strip() for l in bl[start:end].splitlines() if l.strip().startswith("- ")]
missing = [w for w in want if w[2:42] not in rec]
print("criteria in backlog:", len(want))
print("missing from record:", missing)
raise SystemExit(1 if missing or len(want) != 4 else 0)
```

Expected output: `criteria in backlog: 4`, then `missing from record: []`,
exit code 0.

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

Completeness here is a property of the SCRIPT, not of anyone's reading.
Two hand inventories of this item shipped wrong. This matches two regex
families across every tracked file and fails on any match carrying no
written classification, so a missed entry point is a red gate.

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
# naming one. An entry point is "who starts a script and with which host",
# so both families are needed and neither alone is the inventory.
FAMILIES = {
    "host": re.compile(r"powershell\.exe|(?<![\w.\-])pwsh(\.exe)?(?![\w\-])",
                       re.IGNORECASE),
    "launch": re.compile(
        r"Start-Process|System\.Diagnostics\.Process|ProcessStartInfo"
        r"|Get-Process\s+-Id\s+\$PID|schtasks|Register-ScheduledTask"
        r"|New-ScheduledTask\w*|subprocess\.(run|Popen|check_output|call)"
        r"|Invoke-Expression|(?<![\w\-])-File(?![\w\-])"),
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
}
MIGRATION = {"must-change", "no-change", "unknown"}


def digest(line):
    return hashlib.sha1(line.strip().encode("utf-8")).hexdigest()[:12]


def tracked_files():
    out = subprocess.run(["git", "ls-files", "-z"], capture_output=True,
                         check=True, cwd=str(REPO)).stdout
    return [p for p in out.decode("utf-8").split("\0") if p]


def scan():
    hits = {}
    for rel in tracked_files():
        path = REPO / rel
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            continue
        if "\0" in text[:4096]:
            continue
        for n, line in enumerate(text.splitlines(), 1):
            for fam, rx in FAMILIES.items():
                if rx.search(line):
                    hits[(rel, n, fam)] = digest(line)
    return hits


def load_rows():
    rows = {}
    prefixes = []
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
            prefixes.append((rel, fam, cls, mig))
        else:
            rows[(rel, int(line), fam)] = (dg, cls, mig)
    return rows, prefixes


def covered_by_prefix(key, prefixes):
    rel, _, fam = key
    for prel, pfam, _, _ in prefixes:
        if rel.startswith(prel) and (pfam == "*" or pfam == fam):
            return True
    return False


def main():
    hits = scan()
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
    print("SURVEY: %d hits, %d classified, %d unclassified, %d stale"
          % (len(hits), len(hits) - len(unclassified), len(unclassified),
             len(stale)))
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

- [ ] **Step 3: Run the survey and verify it FAILS**

Run: `python docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/survey.py`

Expected: a long list of `UNCLASSIFIED <path>:<line> (<family>)` lines, a
final line reading
`SURVEY: <N> hits, 0 classified, <N> unclassified, 0 stale` with N above
150, and **exit code 1**. Record N in the task report. A pass here would
mean the gate cannot fail, which is the one outcome this script may never
produce.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/survey.py docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/entry-points.tsv
git commit -m "add the item 48 entry-point survey, failing with nothing classified"
```

---

### Task 3: Classify every match, and write the inventory section

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
python docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/survey.py --emit > stubs.tsv
wc -l stubs.tsv
```

`stubs.tsv` is a working file in the repo root. Delete it in Step 3 and do
NOT commit it.

Expected: one line per unclassified match, matching the N from Task 2.

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
- **`docs/` may be covered by one prefix row**, because it is entirely
  historical record. Add exactly this row (TAB separated), and no other
  prefix rows:
  `docs/	*	*	-	record	no-change`
- **A line matching both families produces TWO rows**, one per family, and
  they may carry different classifications.
- **`migration` is `must-change` only if a move to PowerShell 7 would have
  to edit that line.** If you cannot tell from the line and its file, write
  `unknown` and say why in Step 3. `unknown` is an honest answer here;
  a guess is not.

- [ ] **Step 3: Run the survey and verify it PASSES**

Run: `python docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/survey.py`

Expected: no `UNCLASSIFIED` and no `STALE` lines, a final
`SURVEY: <N> hits, <N> classified, 0 unclassified, 0 stale`, and **exit
code 0**.

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
5. A subsection `### What this method cannot see`, naming each of these and
   why the regexes miss it: the versioned plugin cache copy of
   `hooks/hooks.json`; an already-registered scheduled task, which keeps
   the host written into its action at registration time; and any
   instruction a human or agent follows that is not written in a tracked
   file.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/
git commit -m "classify every entry-point match and write the item 48 inventory"
```

---

### Task 4: Measurement 1 — can a 5.1 script re-exec into 7 with arguments intact

**Files:**
- Create: `<REC>/reexec/child.ps1`
- Create: `<REC>/reexec/parent.ps1`
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
makes it meaningful. Stage A is what the PARENT received: Python's own
argument passing is exact, so a corruption here would mean the probe is
broken rather than the re-exec. Stage B is what the CHILD received after
the parent forwarded them.
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


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run it**

Run: `python docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/reexec/run.py`

Expected: four result blocks. `stage_a_parent_exact` must be `true` in all
four; if it is false anywhere, the probe itself is broken and the task
STOPS and reports that, because stage B means nothing without it. Record
`stage_b_child_exact` and `first_difference` for each of the four.

- [ ] **Step 5: Write the measurement section**

Replace `NOT YET WRITTEN.` under `## Measurement 1: re-exec fidelity` with:

1. A four-row table: host, forwarding form, stage A exact, stage B exact,
   index of the first differing argument.
2. The payload list, verbatim, so a reader knows exactly what was tried.
3. One paragraph answering the NO-criterion in its own words: whether a
   re-exec CAN pass arguments through provably intact, under which
   forwarding form, and on which host.
4. A residual limit naming what was not covered: arguments above the
   32767-character command line ceiling measured on 2026-08-22, and
   PowerShell's own `-File` parameter parsing, which sits between the
   command line and `$args` and was measured end-to-end here rather than
   isolated.

- [ ] **Step 6: Commit**

```bash
git add docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/
git commit -m "measure whether a 5.1 to 7 re-exec preserves arbitrary arguments"
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

- [ ] **Step 3: Answer the Linux side separately**

Determine whether ANY step in the `ubuntu-latest` job invokes `pwsh`. Run:

```bash
grep -n -A4 "runs-on: ubuntu" .github/workflows/skill-evals.yml
```

If no Linux step invokes `pwsh`, then PowerShell 7's presence on the Linux
runner is UNPROVEN by this repo's own evidence. Write that as an unproven
statement, not as an absence of a problem.

- [ ] **Step 4: Answer the local user side**

Run:

```bash
where.exe pwsh
"C:\Program Files\PowerShell\7\pwsh.exe" -NoProfile -Command "$PSVersionTable.PSVersion.ToString()"
```

Record the result, and state plainly that PowerShell 7 is NOT preinstalled
on Windows: a user who has never installed it has `powershell.exe` only.
Note the already-known half-requirement: `hooks/hooks.json` invokes its
hook as `pwsh`, so anyone using the hooks already needs 7 installed.
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
- Consumes: the inventory from Task 3.

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

- [ ] **Step 2: List the 13 shipped scripts and mark which are covered**

Run:

```bash
git ls-files 'tools/*.ps1' '.githooks/*' 'evals/tools/*.ps1'
```

For each, name the test module that exercises it, found by:

```bash
grep -rln "<script-basename>" evals/
```

Produce a table: script, covering module, and whether that module is in the
dual-host job from Step 1.

- [ ] **Step 3: Name the host-sensitive behaviours with NO coverage under 7**

The known 5.1-specific traps, each already measured in this repo, are
listed in backlog item 48 under "5.1 is where the traps live". For each,
say whether a test exercises the same behaviour under 7, citing the test
file and line, or write "no coverage under 7".

- [ ] **Step 4: Write the measurement section**

Replace `NOT YET WRITTEN.` under `## Measurement 3: behaviour under 7` with
the two tables from Steps 2 and 3, and one paragraph stating how much of
the shipped surface is proven under 7 today. Do not estimate a percentage
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
is absent is decided by PATH resolution. This runs the same shape of call
with a PATH that has been stripped of every directory containing pwsh, and
captures verbatim what a user would see. Nothing is modified: the real PATH
is untouched outside this child process.
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
    proc = subprocess.run(
        ["pwsh", "-NoProfile", "-Command", "Write-Output ok"],
        capture_output=True, text=True, env=env, shell=False)
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

Expected: `pwsh_after_stripping` is `null`, and the call fails. If the call
raises `FileNotFoundError` instead of returning, catch nothing and report
the traceback text verbatim — that IS the user-facing failure mode and it
is the finding. If `pwsh_after_stripping` is NOT null, the strip failed and
nothing was measured; say so and stop rather than reporting a clean result.

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

1. The captured failure text, verbatim, in a fenced block.
2. One sentence on whether that text names what to install. If it does not,
   say so plainly: an undeclared prerequisite failing obscurely is worse
   than a declared one, and item 48 names that as a NO-criterion.
3. A named residual limit: only the bare-`pwsh` resolution path was
   measured; entry points that today name `powershell.exe` were not, since
   nothing about them changes until a migration edits them.

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

For each of the first five ids `<ID>`:

```bash
gh run view <ID> --json jobs --jq '.jobs[] | {name, startedAt, completedAt}'
```

Compute each job's wall-clock duration in minutes.

- [ ] **Step 2: Write the measurement section**

Replace `NOT YET WRITTEN.` under `## Measurement 5: what is saved` with:

1. A table of the five runs: run id, `skill-evals` duration,
   `powershell-hosts` duration.
2. The saving if the dual-host job became single-host, stated as a RANGE
   across those five runs, not as one number.
3. The already-recorded local pair, cited from backlog item 48 rather than
   re-measured: 32m23s under 5.1 against 18m33s under pwsh at the same
   head, and a second pair of 20m22s against 18m50s, with item 48's own
   caveat that the 5.1 spread is wider than the gap.
4. Item 44's 57 minutes across three serial passes, cited by item number,
   and one sentence on how much of that this change would remove.

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

- [ ] **Step 2: Answer each NO-criterion in turn**

Replace `NOT YET WRITTEN.` under `## Verdict` with a subsection per
NO-criterion, in the order they appear under
`## What would make the verdict NO`, each answering MET or NOT MET and
citing the measurement section that decides it. Then one line:
`**VERDICT: YES** | **VERDICT: NO** | **VERDICT: YES, CONDITIONAL ON <x>**`,
followed by at most one paragraph of reasoning.

A verdict of YES requires every NO-criterion to be NOT MET, each with a
citation. A criterion answered from reasoning rather than from a
measurement makes the verdict CONDITIONAL, not YES.

- [ ] **Step 3: Collect the residual limits**

Replace `NOT YET WRITTEN.` under `## Residual limits` with every residual
limit written by Tasks 3 through 8, gathered into one list, each naming the
section it came from. Add any limit of the investigation as a whole: one
machine, one ANSI code page, one Claude Code version, and the fact that no
script was run under a migration it does not yet have.

- [ ] **Step 4: If the verdict is YES or CONDITIONAL, draft the migration item**

Append to `<REC>/feasibility-record.md` a final section
`## Draft: the migration item`, written in the same shape as the backlog's
other items: Problem, What would close it, ordered work, and Priority. It
must include, as a hard ordering rule taken from item 48: the code becomes
UNABLE to run on 5.1 BEFORE any 5.1 test is deleted. It must also name
backlog items 51 and 31 as absorbed by it, since both defects are 5.1-only.

It must also answer item 48's remaining question in its own subsection,
`### What the test matrix becomes`. Item 48 states the expected shape and
marks it as a guess: "probably not 'one host' but 'one host plus a small
number of cases proving the refusal and the re-exec work when started from
5.1'". Answer it from Task 4's and Task 7's measurements, name the cases
that must survive, and say which exist today and which would be new. If the
measurements do not decide it, say so rather than repeating the guess as a
conclusion.

Do NOT edit `docs/superpowers/plans/2026-07-27-0150-backlog.md` in this
task. The backlog edit happens at merge, not here.

- [ ] **Step 5: Commit**

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
