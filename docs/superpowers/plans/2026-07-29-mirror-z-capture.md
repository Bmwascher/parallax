# Mirror `-z` Capture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Switch both of `tools/new-review-mirror.ps1`'s git pathname
captures to `-z`, delete the hand-written C-style decoder, and parse the
status capture structurally so a rename can never resolve to the wrong
file.

**Architecture:** Five small functions replace one. `Invoke-GitProcess`
runs git and returns raw bytes. `ConvertFrom-NulCapture` turns those bytes
into fields, failing closed on a missing trailing NUL or invalid UTF-8.
`Test-WindowsPathname` refuses a name no Windows file can carry.
`ConvertTo-StatusRecord` builds structured records, consuming a rename's
source from the NEXT field. `Format-StatusRecord` renders one record in
git's display order for the evidence record, one way only.

**Tech Stack:** Windows PowerShell 5.1 and PowerShell 7, git for Windows,
pytest driving both hosts.

**Spec:** `docs/superpowers/specs/2026-07-29-mirror-z-capture-design.md`

## Global Constraints

- `tools/new-review-mirror.ps1` is **Windows PowerShell 5.1 compatible and
  ASCII ONLY**. Both rules are already stated in its header and both stay.
- **`ProcessStartInfo.ArgumentList` does not exist in .NET Framework**, so
  Windows PowerShell 5.1 cannot use it. The command line is one string.
- **Every git argument is a whitespace-free literal and the repo is passed
  as `WorkingDirectory`, never as `-C <path>`.** A repo path can contain
  spaces; hand-quoting it into a command-line string is the defect class
  this cycle is removing.
- **Every argument is wrapped in double quotes on the command line.** Git
  for Windows runs on the MSYS2 runtime, which glob-expands an unquoted
  argument. `*AGENTS.md` must reach git unexpanded.
- **A function that returns a collection returns a hashtable wrapper.** A
  bare `@()` is unrolled by PowerShell, the caller's variable becomes
  `$null`, and a clean repo reads exactly like a failed capture.
- **Fail closed everywhere.** An unmade, failed or unreadable measurement
  is never a clean one.
- Exit codes are unchanged: `0` built and clean, `1` blocked with the
  reason on stdout, `2` script or environment error.
- Text inside `contract:start` / `contract:end` markers must sit WHOLE
  inside a single pin in `evals/multi-model-verify/`. This plan adds no
  marked region and removes none, so `DECLARED_REGIONS` is untouched.
- **The full suite runs under BOTH hosts** before the cycle is called
  done, selected with `PARALLAX_PS_HOST`. A green run on one host proves
  one interpreter.

---

## File Structure

| file | responsibility | change |
|---|---|---|
| `tools/new-review-mirror.ps1` | mirror construction, remediation, evidence | modified throughout |
| `evals/multi-model-verify/test_review_mirror.py` | the suite that locks it | modified, two tests replaced |

No new files. The script is a single deliverable tool and the repo's
pattern is one script per tool.

The new functions go at the TOP of the function block, above the surviving
ones, and `BODY_START` in the test module moves to the first of them so the
dot-source slice keeps covering everything.

---

### Task 1: Raw byte capture and NUL field splitting

**Files:**
- Modify: `tools/new-review-mirror.ps1` — insert two functions above
  `function Invoke-GitLines` (currently line 28)
- Modify: `evals/multi-model-verify/test_review_mirror.py:568-569` —
  `BODY_START`
- Test: `evals/multi-model-verify/test_review_mirror.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces:
  - `Invoke-GitProcess($repo, $gitArgs)` returns
    `@{ Ok = $true; Bytes = [byte[]] }` or
    `@{ Ok = $false; Reason = [string]; Bytes = @() }`.
  - `ConvertFrom-NulCapture($bytes)` returns
    `@{ Ok = $true; Fields = [string[]] }` or
    `@{ Ok = $false; Reason = [string]; Fields = @() }`.

- [ ] **Step 1: Point the dot-source slice at the new first function**

In `evals/multi-model-verify/test_review_mirror.py`, change:

```python
BODY_START = "function Invoke-GitLines"
BODY_END = "$toplevel ="
```

to:

```python
BODY_START = "function Invoke-GitProcess"
BODY_END = "$toplevel ="
```

- [ ] **Step 2: Write the failing tests**

Append to `evals/multi-model-verify/test_review_mirror.py`:

```python
def test_an_empty_capture_is_a_legitimate_state():
    # A repo with nothing to list produces no bytes. That is not a failure,
    # and the wrapper is what keeps it from reading as one.
    out = run_functions(
        '$r = ConvertFrom-NulCapture ([byte[]]@())\n'
        '"{0}|{1}" -f $r.Ok, (@($r.Fields).Count)')
    assert out == "True|0", out


def test_fields_split_on_nul_and_keep_their_spaces():
    # THE WHOLE POINT. A space in a pathname is what made git quote it, and
    # under -z the space is simply part of the field.
    out = run_functions(
        '$b = [System.Text.Encoding]::UTF8.GetBytes("M+ Timer/a.lua`0b.lua`0")\n'
        '$r = ConvertFrom-NulCapture $b\n'
        '(@($r.Fields) -join "|")')
    assert out == "M+ Timer/a.lua|b.lua", out


def test_a_capture_without_a_trailing_nul_stops():
    # A truncated capture ends mid-pathname. Accepting it would put a
    # fragment into the manifest under the name of a real file.
    out = run_functions(
        '$b = [byte[]]@(97, 46, 116, 120, 116)\n'
        '$r = ConvertFrom-NulCapture $b\n'
        '"{0}|{1}" -f $r.Ok, $r.Reason')
    assert out.startswith("False|"), out
    assert "does not end with a NUL" in out, out


def test_invalid_utf8_stops_instead_of_being_replaced():
    # The reason the bytes are read raw. PowerShell's own decode maps a
    # malformed byte to U+FFFD silently, which on this boundary is a wrong
    # pathname reported as a good one.
    out = run_functions(
        '$b = [byte[]]@(97, 255, 0)\n'
        '$r = ConvertFrom-NulCapture $b\n'
        '"{0}|{1}" -f $r.Ok, $r.Reason')
    assert out.startswith("False|"), out
    assert "not valid UTF-8" in out, out


def test_a_non_ascii_field_arrives_as_one_character_not_two_bytes():
    # THE DECODER DEFECT THIS CYCLE DELETES, pinned so it cannot return.
    # The old ConvertFrom-GitQuotedPath turned `caf\303\251` into character
    # codes 195,169 - two characters - instead of 233. Reading raw bytes and
    # decoding once from UTF-8 is what makes that impossible.
    out = run_functions(
        '$b = [byte[]]@(99, 97, 102, 195, 169, 0)\n'
        '$r = ConvertFrom-NulCapture $b\n'
        '(([int[]][char[]]$r.Fields[0]) -join ",")')
    assert out == "99,97,102,233", out


def test_an_empty_field_before_the_end_is_kept_for_the_parser_to_refuse():
    # Only the empty string AFTER the final NUL is dropped. An empty field
    # anywhere else is a real fault and must reach the caller rather than
    # being tidied away here.
    out = run_functions(
        '$b = [System.Text.Encoding]::UTF8.GetBytes("a.txt`0`0b.txt`0")\n'
        '$r = ConvertFrom-NulCapture $b\n'
        '"{0}|{1}" -f (@($r.Fields).Count), (@($r.Fields) -join ",")')
    assert out == "3|a.txt,,b.txt", out
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -k "capture or field or utf8" -v`

Expected: FAIL. `ConvertFrom-NulCapture` is not defined, so the dot-sourced
snippet exits non-zero and `run_functions` trips its own assert.

- [ ] **Step 4: Write the implementation**

Insert into `tools/new-review-mirror.ps1` immediately above
`function Invoke-GitLines`:

```powershell
function Invoke-GitProcess($repo, $gitArgs) {
    # Run git and hand back its stdout as RAW BYTES.
    #
    # Reading bytes rather than PowerShell's decoded string is the point.
    # Windows PowerShell 5.1 decodes a native command's output with the
    # console code page, and even a UTF-8 console override maps a malformed
    # byte to U+FFFD SILENTLY. On this boundary a substituted character is
    # a wrong pathname reported as a good one, so the decode happens once,
    # downstream, and strictly.
    #
    # ARGUMENTS ARE WHITESPACE-FREE LITERALS AND THE REPO IS THE WORKING
    # DIRECTORY. .NET Framework's ProcessStartInfo has no ArgumentList, so
    # the command line is one string; passing the repo path through it
    # would mean hand-quoting a value that can contain spaces, which is the
    # defect class this change removes. The guard below refuses an argument
    # this command line cannot express rather than trusting the caller.
    #
    # Every argument is QUOTED. Git for Windows runs on the MSYS2 runtime,
    # which glob-expands an unquoted argument, and `*AGENTS.md` must reach
    # git unexpanded or the back-channel enumeration silently narrows to
    # whatever happens to sit in the working directory.
    foreach ($a in @($gitArgs)) {
        if ([string]$a -match '[\s"]') {
            return @{ Ok = $false; Bytes = @()
                      Reason = ("git argument '" + $a + "' carries" +
                        " whitespace or a quote, which this command line" +
                        " cannot express") }
        }
    }
    $quoted = @($gitArgs | ForEach-Object { '"' + $_ + '"' })
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "git"
    $psi.Arguments = ($quoted -join " ")
    $psi.WorkingDirectory = $repo
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $mem = New-Object System.IO.MemoryStream
    try {
        $p = [System.Diagnostics.Process]::Start($psi)
        # Drain stderr CONCURRENTLY. A full stderr pipe blocks git before
        # it finishes writing stdout, and the stdout read below would then
        # never return.
        $errTask = $p.StandardError.ReadToEndAsync()
        $p.StandardOutput.BaseStream.CopyTo($mem)
        $p.WaitForExit()
        [void]$errTask.Wait(5000)
    } catch {
        return @{ Ok = $false; Bytes = @()
                  Reason = ("git could not be run: " +
                            $_.Exception.Message) }
    }
    if ($p.ExitCode -ne 0) {
        return @{ Ok = $false; Bytes = @()
                  Reason = ("git exited " + $p.ExitCode) }
    }
    return @{ Ok = $true; Bytes = $mem.ToArray() }
}

function ConvertFrom-NulCapture($bytes) {
    # Turn a `-z` capture into its fields. Every failure here is a STOP.
    #
    # `-z` is why this exists. Git C-style-quotes a pathname whenever
    # quoting would change it, and the trigger set is WIDER than the
    # escapes alone: a plain SPACE is enough. Measured 2026-07-29, a
    # directory named `M+ Timer` came back from `status --porcelain` as
    # `?? "M+ Timer/"`, and `core.quotepath=false` did not suppress it.
    # Under `-z` git emits the pathname verbatim and NUL-terminated and
    # never quotes, so there is no escape grammar to decode.
    $raw = [byte[]]@($bytes)
    if ($raw.Length -eq 0) { return @{ Ok = $true; Fields = @() } }
    if ($raw[$raw.Length - 1] -ne 0) {
        return @{ Ok = $false; Fields = @()
                  Reason = ("the -z capture does not end with a NUL, so it" +
                    " was truncated and its last pathname is a fragment") }
    }
    # throwOnInvalidBytes, deliberately. The permissive decode substitutes
    # U+FFFD and hands back a pathname that names a different file.
    $utf8 = New-Object System.Text.UTF8Encoding($false, $true)
    $text = ""
    try {
        $text = $utf8.GetString($raw)
    } catch {
        return @{ Ok = $false; Fields = @()
                  Reason = ("the -z capture is not valid UTF-8, so a" +
                    " pathname in it cannot be read without guessing") }
    }
    # The capture ends with a NUL, so the split's LAST element is the empty
    # string after it. Drop exactly that one. An empty field anywhere else
    # is a real fault and belongs to the caller, not to this function.
    $parts = $text.Split([char]0)
    $fields = New-Object System.Collections.ArrayList
    for ($i = 0; $i -lt $parts.Length - 1; $i++) {
        [void]$fields.Add($parts[$i])
    }
    return @{ Ok = $true; Fields = @($fields) }
}
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -k "capture or field or utf8" -v`

Expected: PASS, 6 tests.

- [ ] **Step 6: Run the whole module to prove nothing regressed**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -q`

Expected: the one pre-existing failure
(`test_a_quoted_baseline_entry_stops_instead_of_being_unquoted`) and
nothing new. Task 6 replaces that test.

- [ ] **Step 7: Commit**

```bash
git add tools/new-review-mirror.ps1 evals/multi-model-verify/test_review_mirror.py
git commit -m "read git pathname captures as raw NUL-separated bytes"
```

---

### Task 2: The Windows pathname guard

**Files:**
- Modify: `tools/new-review-mirror.ps1` — one function below
  `ConvertFrom-NulCapture`
- Test: `evals/multi-model-verify/test_review_mirror.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `Test-WindowsPathname($value)` returns `$true` or `$false`.

- [ ] **Step 1: Write the failing test**

Append to `evals/multi-model-verify/test_review_mirror.py`:

```python
def test_the_windows_pathname_guard_is_pinned_in_both_directions():
    # Measured 2026-07-29: of every character that makes git quote a path,
    # Windows permits only a SPACE and non-ASCII in a real filename. A name
    # carrying any of the refusals names no file this script can delete or
    # hash, and git reads names from its INDEX, which can carry one authored
    # elsewhere. Pinned in both directions so a future edit cannot make the
    # guard constant.
    out = run_functions(
        '$q = [char]34\n'
        '$results = @(\n'
        '  (Test-WindowsPathname "M+ Timer/core.lua"),\n'
        '  (Test-WindowsPathname "caf' + "é" + '/input.txt"),\n'
        '  (Test-WindowsPathname "a$([char]9)b.txt"),\n'
        '  (Test-WindowsPathname "a$([char]10)b.txt"),\n'
        '  (Test-WindowsPathname ("a" + $q + "b.txt")),\n'
        '  (Test-WindowsPathname "a\\b.txt"),\n'
        '  (Test-WindowsPathname "")\n'
        ')\n'
        '($results -join ",")')
    assert out == "True,True,False,False,False,False,False", out
```

Note: this test file is read as UTF-8 by pytest, so the accented literal is
fine here. The SCRIPT stays ASCII; nothing above adds a non-ASCII character
to it.

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -k windows_pathname_guard -v`

Expected: FAIL, `Test-WindowsPathname` is not recognized.

- [ ] **Step 3: Write the implementation**

Insert into `tools/new-review-mirror.ps1` below `ConvertFrom-NulCapture`:

```powershell
function Test-WindowsPathname($value) {
    # Under `-z` git never quotes, so whatever arrives IS the pathname.
    # This answers a different question: can it BE a Windows pathname at
    # all? git reads names from its INDEX, which can carry a name authored
    # on a platform with looser rules.
    #
    # Measured 2026-07-29 on this machine: of every character that makes
    # git quote a path, Windows permits only a SPACE and non-ASCII in a
    # real filename. It refuses a double quote, a backslash, `>` and every
    # control character.
    #
    # The BACKSLASH refusal is the load-bearing one. git separates path
    # components with a forward slash, so a backslash in a field is a
    # literal character in a NAME - and `Join-Path` would then read it as a
    # separator and resolve a DIFFERENT file, which the script would delete
    # or hash under the name the baseline gave. That is false coverage
    # rather than a refusal, which is the one outcome this preflight exists
    # to prevent.
    $text = [string]$value
    if ($text.Length -eq 0) { return $false }
    foreach ($ch in $text.ToCharArray()) {
        if ([int]$ch -lt 32) { return $false }
        if ($ch -eq [char]34) { return $false }
        if ($ch -eq '\') { return $false }
    }
    return $true
}
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -k windows_pathname_guard -v`

Expected: PASS.

- [ ] **Step 5: Confirm the script is still ASCII**

Run:

```bash
python -c "p='tools/new-review-mirror.ps1'; b=open(p,'rb').read(); bad=[(i,c) for i,c in enumerate(b) if c>127]; print('NON-ASCII' if bad else 'ascii ok', bad[:5])"
```

Expected: `ascii ok []`

- [ ] **Step 6: Commit**

```bash
git add tools/new-review-mirror.ps1 evals/multi-model-verify/test_review_mirror.py
git commit -m "refuse a pathname no Windows file can carry"
```

---

### Task 3: Structural status parsing, with the inverted rename order

**Files:**
- Modify: `tools/new-review-mirror.ps1` — one function below
  `Test-WindowsPathname`
- Test: `evals/multi-model-verify/test_review_mirror.py`

**Interfaces:**
- Consumes: `Test-WindowsPathname($value)` from Task 2.
- Produces: `ConvertTo-StatusRecord($fields)` returns
  `@{ Records = @(@{ X; Y; Path; Source }) }` or `@{ Error = [string] }`.
  `Source` is `$null` for every record that is not a rename or a copy.

- [ ] **Step 1: Write the failing tests**

Append to `evals/multi-model-verify/test_review_mirror.py`:

```python
def test_a_rename_record_reads_destination_first_then_source():
    # THE INVERSION. Measured 2026-07-29 against a real git: the line form
    # reads `R  <old> -> <new>`, and the same rename under -z reads
    # `R  <new>` NUL `<old>` NUL. A parse that carries the line form's order
    # across hashes and deletes the wrong file and says nothing.
    out = run_functions(
        '$r = ConvertTo-StatusRecord @("R  M+ Timer/new name.lua",\n'
        '                              "M+ Timer/old name.lua")\n'
        '$rec = $r.Records[0]\n'
        '"{0}|{1}|{2}{3}" -f $rec.Path, $rec.Source, $rec.X, $rec.Y')
    assert out == "M+ Timer/new name.lua|M+ Timer/old name.lua|R ", out


def test_a_plain_entry_has_no_source_and_keeps_its_spaces():
    out = run_functions(
        '$r = ConvertTo-StatusRecord @("?? untracked file.txt")\n'
        '$rec = $r.Records[0]\n'
        '"{0}|{1}" -f $rec.Path, ($null -eq $rec.Source)')
    assert out == "untracked file.txt|True", out


def test_a_rename_with_no_source_field_stops():
    # A truncated capture. The record claims a source that is not there.
    out = run_functions(
        '$r = ConvertTo-StatusRecord @("R  new.lua"); $r.Error')
    assert "no source field" in out, out


def test_a_copy_in_the_second_column_also_consumes_a_source():
    # EITHER column can carry R or C, which is why both are tested.
    out = run_functions(
        '$r = ConvertTo-StatusRecord @(" C dest.lua", "src.lua")\n'
        '"{0}|{1}|{2}" -f $r.Records.Count, $r.Records[0].Path,'
        ' $r.Records[0].Source')
    assert out == "1|dest.lua|src.lua", out


def test_a_control_character_in_a_status_pathname_stops():
    out = run_functions(
        '$r = ConvertTo-StatusRecord @("?? a$([char]9)b.txt"); $r.Error')
    assert "cannot exist on this platform" in out, out


def test_a_status_field_too_short_to_carry_a_pathname_stops():
    out = run_functions(
        '$r = ConvertTo-StatusRecord @("?? "); $r.Error')
    assert "shorter than" in out, out


def test_a_status_field_with_no_space_after_the_code_stops():
    out = run_functions(
        '$r = ConvertTo-StatusRecord @("??x.txt"); $r.Error')
    assert "no space where the status code ends" in out, out


def test_an_empty_status_field_stops():
    # ConvertFrom-NulCapture deliberately passes an interior empty field
    # through. This is where it is refused.
    out = run_functions(
        '$r = ConvertTo-StatusRecord @(""); $r.Error')
    assert "shorter than" in out, out
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -k "status_record or rename or copy_in_the_second or status_field or status_pathname" -v`

Expected: FAIL, `ConvertTo-StatusRecord` is not recognized.

- [ ] **Step 3: Write the implementation**

Insert into `tools/new-review-mirror.ps1` below `Test-WindowsPathname`:

```powershell
function ConvertTo-StatusRecord($fields) {
    # Parse the `-z` status capture STRUCTURALLY. Returns @{Records=..} or
    # @{Error=..}; a caller that cannot parse an entry must BLOCK, never
    # skip, because a skipped entry is a silent hole in the manifest.
    #
    # THE RENAME FIELD ORDER IS INVERTED FROM THE LINE FORM. Measured
    # 2026-07-29: the line form reads `R  <old> -> <new>`, and the same
    # rename under `-z` reads `R  <new>` NUL `<old>` NUL - DESTINATION
    # first, SOURCE second. Nothing about the record hints at the order,
    # which is why it is stated here rather than left to a reader.
    #
    # Each field is the two status columns, one space, then the pathname.
    $records = New-Object System.Collections.ArrayList
    $all = @($fields)
    $i = 0
    while ($i -lt $all.Count) {
        $field = [string]$all[$i]
        $i++
        if ($field.Length -lt 4) {
            return @{ Error = ("status field '" + $field + "' is shorter" +
                " than two status columns, a space and a pathname") }
        }
        if ($field[2] -ne ' ') {
            return @{ Error = ("status field '" + $field + "' has no space" +
                " where the status code ends, so this capture is not the" +
                " porcelain format this parser reads") }
        }
        $x = $field[0]
        $y = $field[1]
        $path = $field.Substring(3)
        if (-not (Test-WindowsPathname $path)) {
            return @{ Error = ("status entry '" + $field + "' names a path" +
                " that cannot exist on this platform, so the file it points" +
                " at cannot be resolved without guessing") }
        }
        $source = $null
        if ($x -eq "R" -or $x -eq "C" -or $y -eq "R" -or $y -eq "C") {
            if ($i -ge $all.Count) {
                return @{ Error = ("rename or copy entry '" + $field +
                    "' has no source field after it, so the capture is" +
                    " truncated") }
            }
            $source = [string]$all[$i]
            $i++
            if (-not (Test-WindowsPathname $source)) {
                return @{ Error = ("rename or copy entry '" + $field +
                    "' names a source that cannot exist on this platform") }
            }
        }
        [void]$records.Add(@{ X = $x; Y = $y; Path = $path
                              Source = $source })
    }
    return @{ Records = @($records) }
}
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -k "status_record or rename or copy_in_the_second or status_field or status_pathname" -v`

Expected: PASS, 8 tests.

- [ ] **Step 5: Commit**

```bash
git add tools/new-review-mirror.ps1 evals/multi-model-verify/test_review_mirror.py
git commit -m "parse the -z status capture structurally"
```

---

### Task 4: Rendering one record for the evidence

**Files:**
- Modify: `tools/new-review-mirror.ps1` — one function below
  `ConvertTo-StatusRecord`
- Test: `evals/multi-model-verify/test_review_mirror.py`

**Interfaces:**
- Consumes: a record from `ConvertTo-StatusRecord($fields)` (Task 3).
- Produces: `Format-StatusRecord($record)` returns a `[string]`.

- [ ] **Step 1: Write the failing tests**

Append to `evals/multi-model-verify/test_review_mirror.py`:

```python
def test_a_rename_renders_in_gits_display_order():
    # The recorded baseline keeps the shape references/backup-lane.md
    # already describes, so this change does not make earlier baselines
    # unreadable. The arrow is unambiguous because Windows refuses `>` in a
    # filename and Test-WindowsPathname refuses a name Windows cannot
    # carry.
    out = run_functions(
        '$r = ConvertTo-StatusRecord @("R  M+ Timer/new name.lua",\n'
        '                              "M+ Timer/old name.lua")\n'
        'Format-StatusRecord $r.Records[0]')
    assert out == "R  M+ Timer/old name.lua -> M+ Timer/new name.lua", out


def test_a_plain_entry_renders_as_the_status_code_and_the_path():
    out = run_functions(
        '$r = ConvertTo-StatusRecord @("!! ignored dir/note.txt")\n'
        'Format-StatusRecord $r.Records[0]')
    assert out == "!! ignored dir/note.txt", out


def test_a_status_code_with_a_leading_space_survives_rendering():
    # ` M` and ` D` are ordinary porcelain codes. Trimming the render would
    # change what the record says happened.
    out = run_functions(
        '$r = ConvertTo-StatusRecord @(" M kept.txt")\n'
        '"[{0}]" -f (Format-StatusRecord $r.Records[0])')
    assert out == "[ M kept.txt]", out
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -k "renders or rendering" -v`

Expected: FAIL, `Format-StatusRecord` is not recognized.

- [ ] **Step 3: Write the implementation**

Insert into `tools/new-review-mirror.ps1` below `ConvertTo-StatusRecord`:

```powershell
function Format-StatusRecord($record) {
    # Render one record in git's own DISPLAY order, `R  <old> -> <new>`, so
    # the recorded baseline keeps the shape references/backup-lane.md
    # already describes and two captures stay comparable across this
    # change.
    #
    # ONE WAY ONLY. Nothing re-parses this text: the manifest's subjects
    # come from the RECORDS. That separation is the whole reason the arrow
    # is safe to write here at all.
    $head = [string]$record.X + [string]$record.Y + " "
    if ($record.Source) {
        return ($head + $record.Source + " -> " + $record.Path)
    }
    return ($head + $record.Path)
}
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -k "renders or rendering" -v`

Expected: PASS, 3 tests.

- [ ] **Step 5: Commit**

```bash
git add tools/new-review-mirror.ps1 evals/multi-model-verify/test_review_mirror.py
git commit -m "render one status record for the evidence, one way only"
```

---

### Task 5: Wire the main flow and delete the decoder

**Files:**
- Modify: `tools/new-review-mirror.ps1` — `Invoke-GitLines` (28-61),
  `Test-GitQuotedPath` (63-71), `ConvertFrom-GitQuotedPath` (73-137),
  `Resolve-GitPathname` (139-147), `Get-BackChannelEntry` (149-175),
  `Get-BaselineRaw` (182-197), `Get-ManifestSubject` (199-244), the
  back-channel block (369-385) and the baseline block (443-455)
- Test: `evals/multi-model-verify/test_review_mirror.py` (existing cases
  are the regression net)

**Interfaces:**
- Consumes: `Invoke-GitProcess`, `ConvertFrom-NulCapture` (Task 1),
  `Test-WindowsPathname` (Task 2), `ConvertTo-StatusRecord` (Task 3),
  `Format-StatusRecord` (Task 4).
- Produces:
  - `Invoke-GitFields($repo, $gitArgs)` returns
    `@{ Ok = $true; Fields = [string[]] }` or
    `@{ Ok = $false; Reason = [string]; Fields = @() }`.
  - `Get-BackChannelEntry($repo)` returns
    `@{ Ok = $true; Entries = [string[]] }` or
    `@{ Ok = $false; Reason = [string]; Entries = @() }`. **`Reason` is
    new**; the caller now prints it.
  - `Get-BaselineRaw($repo)` returns the `Invoke-GitFields` shape.
  - `Get-ManifestSubject($records)` now takes RECORDS, not lines, and
    returns `@{ Paths = [string[]] }` or `@{ Error = [string] }`.

- [ ] **Step 1: Replace `Invoke-GitLines` with `Invoke-GitFields`**

Delete `function Invoke-GitLines` (lines 28-61) entirely, including its
comment block, and put this in its place:

```powershell
function Invoke-GitFields($repo, $gitArgs) {
    # Every git capture that produces PATHNAMES goes through here, so both
    # of them answer the same questions the same way.
    #
    # `core.quotepath=false` is GONE from these captures and its absence is
    # deliberate. The flag governed the DISPLAY form, and `-z` has no
    # display form: measured 2026-07-29, `git ls-files -z` returned raw
    # UTF-8 bytes with the flag ABSENT. Keeping a flag that does nothing
    # invites a later reader to treat it as load-bearing.
    #
    # The console-encoding guard the old capture needed is gone for the
    # same reason: nothing here goes through PowerShell's decoder. The
    # bytes are read from the process stream and decoded once, strictly,
    # in ConvertFrom-NulCapture.
    $captured = Invoke-GitProcess $repo $gitArgs
    if (-not $captured.Ok) {
        return @{ Ok = $false; Fields = @(); Reason = $captured.Reason }
    }
    return (ConvertFrom-NulCapture $captured.Bytes)
}
```

- [ ] **Step 2: Delete the three decoder functions**

Delete `Test-GitQuotedPath`, `ConvertFrom-GitQuotedPath` and
`Resolve-GitPathname` in full, comments included. Nothing replaces them.

- [ ] **Step 3: Rewrite `Get-BackChannelEntry`**

Replace its body so it adds `-z`, drops the decode loop, and applies the
guard:

```powershell
function Get-BackChannelEntry($repo) {
    # One listing covering tracked, untracked AND ignored files. `--others`
    # without `--exclude-standard` includes ignored paths. `*AGENTS.md`
    # reaches any depth; `.agents/*` is anchored at the repo ROOT and does
    # NOT, which is the asymmetry recorded in SKILL.md's
    # enumeration-depth-asymmetry region. Do not restate "at any depth"
    # here.
    #
    # Returns @{Ok=..; Entries=..; Reason=..}. A function returning a bare
    # @() has its empty array unrolled by PowerShell, so the caller's
    # variable becomes $null and a CLEAN repo reads exactly like a FAILED
    # enumeration.
    $r = Invoke-GitFields $repo @("ls-files", "--cached", "--others", "-z",
                                  "*AGENTS.md", ".agents/*")
    if (-not $r.Ok) {
        return @{ Ok = $false; Entries = @(); Reason = $r.Reason }
    }
    # An entry this platform cannot name is a stop: a back-channel this
    # script cannot name is a back-channel it cannot delete, and reporting
    # it as clean is the one outcome the whole preflight exists to prevent.
    foreach ($e in @($r.Fields)) {
        if (-not (Test-WindowsPathname $e)) {
            return @{ Ok = $false; Entries = @()
                      Reason = ("the back-channel entry '" + $e + "' names" +
                        " a path that cannot exist on this platform, so it" +
                        " cannot be deleted") }
        }
    }
    return @{ Ok = $true; Entries = @($r.Fields) }
}
```

- [ ] **Step 4: Add `-z` to the status capture**

In `Get-BaselineRaw`, change the call and leave the comment block intact
except for the sentence naming the return shape:

```powershell
    return (Invoke-GitFields $repo @("status", "--porcelain", "--ignored",
                                     "-uall", "-z"))
```

- [ ] **Step 5: Rewrite `Get-ManifestSubject` to take records**

Replace the function in full:

```powershell
function Get-ManifestSubject($records) {
    # Coverage is exactly the baseline's paths. Returns @{Paths=..} or
    # @{Error=..}; a caller that cannot resolve an entry must BLOCK, never
    # skip, because a skipped entry is a silent hole in the manifest.
    #
    # Takes RECORDS, never rendered text. A rename's destination is already
    # the record's Path under `-z`, so there is no arrow to search for and
    # no chance of splitting inside a pathname.
    $paths = New-Object System.Collections.ArrayList
    foreach ($r in @($records)) {
        $x = $r.X
        $y = $r.Y
        # Deletion-only entries have no bytes to hash. HEAD plus the
        # baseline already bind the absence, which is the whole content of
        # the fact, so OMIT them.
        if (($x -eq " " -and $y -eq "D") -or ($x -eq "D" -and $y -eq " ")) {
            continue
        }
        # An `RD` destination no longer exists. That entry names no
        # readable file, so it is a stop rather than a silent omission.
        if ($y -eq "D" -and ($x -eq "R" -or $x -eq "C")) {
            return @{ Error = ("baseline entry '" +
                (Format-StatusRecord $r) + "' names a destination that has" +
                " been deleted; the mirror is not in a state this manifest" +
                " rule can describe") }
        }
        [void]$paths.Add($r.Path)
    }
    return @{ Paths = @($paths) }
}
```

- [ ] **Step 6: Report the enumeration reason in the main flow**

At the two back-channel call sites, print the reason instead of a bare
sentence. Replace lines 369-385 with:

```powershell
$found = Get-BackChannelEntry $MirrorPath
if (-not $found.Ok) {
    Write-Output ("ERROR: could not enumerate back-channels in the" +
        " mirror: " + $found.Reason)
    exit 2
}
$entries = $found.Entries
```

The quoted-entry loop that followed is DELETED. Under `-z` nothing is
quoted, and `Test-WindowsPathname` inside `Get-BackChannelEntry` now covers
the residue that loop was reaching for.

Replace the re-enumeration failure line (currently 427-430) the same way:

```powershell
if (-not $after.Ok) {
    Write-Output ("ERROR: could not re-enumerate back-channels in the" +
        " mirror: " + $after.Reason)
    exit 2
}
```

- [ ] **Step 7: Wire the baseline through parse and render**

Replace lines 443-455 with:

```powershell
$captured = Get-BaselineRaw $MirrorPath
if (-not $captured.Ok) {
    Write-Output ("BLOCKED: the baseline capture failed (" +
        $captured.Reason + "). A failed capture printed as success would" +
        " quarantine every round of the review that follows, or absorb" +
        " changes it should have caught.")
    exit 1
}
$parsed = ConvertTo-StatusRecord $captured.Fields
if ($parsed.ContainsKey("Error")) {
    Write-Output ("BLOCKED: " + $parsed.Error)
    exit 1
}
$baseline = @(@($parsed.Records) |
    ForEach-Object { Format-StatusRecord $_ })
$subjects = Get-ManifestSubject $parsed.Records
if ($subjects.ContainsKey("Error")) {
    Write-Output ("BLOCKED: " + $subjects.Error)
    exit 1
}
```

- [ ] **Step 8: Run the whole module**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -q`

Expected: every test passes EXCEPT the two that name the deleted
functions — `test_a_quoted_baseline_entry_stops_instead_of_being_unquoted`
and `test_the_quoted_form_is_recognized_and_a_plain_path_is_not`. Task 6
replaces both. If any OTHER test fails, stop and fix it here.

- [ ] **Step 9: Confirm the script is still ASCII**

Run:

```bash
python -c "p='tools/new-review-mirror.ps1'; b=open(p,'rb').read(); bad=[(i,c) for i,c in enumerate(b) if c>127]; print('NON-ASCII' if bad else 'ascii ok', bad[:5])"
```

Expected: `ascii ok []`

- [ ] **Step 10: Commit**

```bash
git add tools/new-review-mirror.ps1
git commit -m "wire the -z captures through and delete the quoted-path decoder"
```

---

### Task 6: Replace the stale tests and cover the real cases end to end

**Files:**
- Modify: `evals/multi-model-verify/test_review_mirror.py:270-296`
  (manifest splitting), `:603-621` (the two stale tests)
- Test: the same file

**Interfaces:**
- Consumes: everything from Tasks 1-5.
- Produces: no new script surface.

- [ ] **Step 1: Fix the manifest assertions that split at the first space**

A manifest line is `<path> <sha256>`, and a path can now contain spaces, so
splitting from the LEFT takes the first word. Split from the RIGHT instead.

In `test_the_manifest_covers_exactly_the_baseline_paths`, replace:

```python
    paths = [line.split(" ", 1)[0]
             for line in read_block(proc.stdout, "manifest:")]
```

with:

```python
    paths = [line.rsplit(" ", 1)[0]
             for line in read_block(proc.stdout, "manifest:")]
```

In `test_the_manifest_hashes_raw_bytes_and_sorts_by_path`, replace:

```python
    paths = [line.split(" ", 1)[0] for line in manifest]
    assert paths == sorted(paths), "sorted by path in byte order"
    for line in manifest:
        path, digest = line.split(" ", 1)
```

with:

```python
    paths = [line.rsplit(" ", 1)[0] for line in manifest]
    assert paths == sorted(paths), "sorted by path in byte order"
    for line in manifest:
        path, digest = line.rsplit(" ", 1)
```

In `test_a_directory_expands_recursively`, replace:

```python
    paths = [line.split(" ", 1)[0]
             for line in read_block(proc.stdout, "manifest:")]
```

with:

```python
    paths = [line.rsplit(" ", 1)[0]
             for line in read_block(proc.stdout, "manifest:")]
```

- [ ] **Step 2: Delete the two tests that name deleted functions**

Delete `test_a_quoted_baseline_entry_stops_instead_of_being_unquoted` and
`test_the_quoted_form_is_recognized_and_a_plain_path_is_not` in full,
comments included. Their subject no longer exists. The comment above
`run_functions` that explains WHY the dot-source slice exists stays.

- [ ] **Step 3: Write the failing end-to-end tests**

Append to `evals/multi-model-verify/test_review_mirror.py`:

```python
# A path with a SPACE. This is the whole reason for the -z change: git
# quotes any pathname containing a space, the old capture refused every
# quoted entry, and a repo using the `References/<name with spaces>/`
# convention could not be mirrored at all. Measured 2026-07-29 against a
# throwaway repo, a directory named `M+ Timer` came back as `?? "M+ Timer/"`
# from `status --porcelain`, quoted for the space and nothing else.
SPACED = "M+ Timer"


def test_a_back_channel_under_a_spaced_directory_is_removed(tmp_path):
    repo = make_repo(tmp_path)
    (repo / SPACED).mkdir()
    (repo / SPACED / "AGENTS.md").write_text("# planted\n")
    mirror = tmp_path / "mirror"
    proc = run_mirror(repo, mirror)
    assert "survived remediation" not in proc.stdout, proc.stdout
    assert_built(proc)
    assert not (mirror / SPACED / "AGENTS.md").exists()
    assert (repo / SPACED / "AGENTS.md").exists(), (
        "the real tree is never touched")


def test_a_spaced_baseline_entry_reaches_the_manifest(tmp_path):
    repo = make_repo(tmp_path)
    (repo / SPACED).mkdir()
    body = b"subject material\n"
    (repo / SPACED / "input.txt").write_bytes(body)
    proc = run_mirror(repo, tmp_path / "mirror")
    assert_built(proc)
    expected = hashlib.sha256(body).hexdigest()
    assert f"{SPACED}/input.txt {expected}" in proc.stdout, proc.stdout
    assert f"?? {SPACED}/input.txt" in proc.stdout, proc.stdout


def test_a_spaced_ignored_entry_reaches_the_manifest(tmp_path):
    # Ignored content is the entire reason this workspace is a mirror.
    repo = make_repo(tmp_path)
    (repo / ".gitignore").write_text("ignored/\nrefs with spaces/\n")
    git(repo, "add", ".gitignore")
    commit(repo, "ignore a spaced directory")
    (repo / "refs with spaces").mkdir()
    body = b"reference source\n"
    (repo / "refs with spaces" / "note.txt").write_bytes(body)
    proc = run_mirror(repo, tmp_path / "mirror")
    assert_built(proc)
    expected = hashlib.sha256(body).hexdigest()
    assert f"refs with spaces/note.txt {expected}" in proc.stdout, proc.stdout
    assert "!! refs with spaces/note.txt" in proc.stdout, proc.stdout


def test_a_rename_with_spaces_hashes_the_destination_not_the_source(tmp_path):
    # THE INVERSION, end to end. Under -z the destination arrives FIRST and
    # the source second, the opposite of the line form. A parse that keeps
    # the old order would hash the source, which no longer exists, and the
    # run would stop with the wrong reason - or worse, hash a file that
    # happens to be there.
    repo = make_repo(tmp_path)
    (repo / SPACED).mkdir()
    body = b"renamed content\n"
    (repo / SPACED / "old name.lua").write_bytes(body)
    git(repo, "add", "--", f"{SPACED}/old name.lua")
    commit(repo, "add the spaced file")
    git(repo, "mv", f"{SPACED}/old name.lua", f"{SPACED}/new name.lua")
    proc = run_mirror(repo, tmp_path / "mirror")
    assert_built(proc)
    expected = hashlib.sha256(body).hexdigest()
    assert f"{SPACED}/new name.lua {expected}" in proc.stdout, proc.stdout
    assert f"{SPACED}/old name.lua {expected}" not in proc.stdout, (
        "the source of a rename no longer exists; hashing it would be a"
        " hash of whatever happened to take its place")


def test_a_rename_renders_in_the_baseline_as_source_arrow_destination(tmp_path):
    # references/backup-lane.md describes the baseline as the status
    # command's output, and every earlier baseline reads `old -> new`. The
    # -z wire order is the opposite, so the render is what keeps two
    # captures comparable across this change.
    repo = make_repo(tmp_path)
    (repo / SPACED).mkdir()
    (repo / SPACED / "old name.lua").write_bytes(b"x\n")
    git(repo, "add", "--", f"{SPACED}/old name.lua")
    commit(repo, "add the spaced file")
    git(repo, "mv", f"{SPACED}/old name.lua", f"{SPACED}/new name.lua")
    proc = run_mirror(repo, tmp_path / "mirror")
    assert_built(proc)
    baseline = read_block(proc.stdout, "baseline:")
    assert f"R  {SPACED}/old name.lua -> {SPACED}/new name.lua" in baseline, (
        baseline)


def test_escape_looking_field_text_is_never_interpreted():
    # `caf\303\251` is the exact string the deleted decoder mishandled: it
    # turned those nine characters into two, neither of them the accented
    # letter the real name holds. Under -z the bytes are the pathname, so
    # the field must come back as the nine literal characters it is.
    #
    # This is a FIELD-level case and not an end-to-end one on purpose. A
    # file with this name cannot exist on Windows, because the backslash is
    # a path separator there - measured 2026-07-29. The bytes can still
    # arrive from git's INDEX, which is what Test-WindowsPathname then
    # refuses, so the two halves are tested where each can actually be
    # reached.
    out = run_functions(
        '$b = [System.Text.Encoding]::UTF8.GetBytes("caf\\303\\251.txt`0")\n'
        '$r = ConvertFrom-NulCapture $b\n'
        '"{0}|{1}" -f $r.Fields[0], $r.Fields[0].Length')
    assert out == "caf\\303\\251.txt|15", out


def test_a_backslash_bearing_index_entry_stops_the_enumeration():
    # The other half. git reads names from its INDEX, which can carry a
    # name Windows cannot represent. Join-Path would read the backslash as
    # a separator and resolve a DIFFERENT file, which the script would then
    # delete or hash under the name the baseline gave.
    out = run_functions(
        '$r = ConvertTo-StatusRecord @("?? caf\\303\\251.txt"); $r.Error')
    assert "cannot exist on this platform" in out, out
```

- [ ] **Step 4: Run the new tests to verify they pass**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -k "spaced or rename or escape_looking or backslash_bearing" -v`

Expected: PASS.

- [ ] **Step 5: Run the whole module**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -q`

Expected: all pass, zero failures.

- [ ] **Step 6: Commit**

```bash
git add evals/multi-model-verify/test_review_mirror.py
git commit -m "cover spaces, the inverted rename order and literal escape text"
```

---

### Task 7: Prove it on both hosts and update the reference

**Files:**
- Modify: `skills/multi-model-verify/references/backup-lane.md:299-301`
- Test: the whole repo suite

**Interfaces:**
- Consumes: everything above.
- Produces: nothing new.

- [ ] **Step 1: Run the mirror suite under Windows PowerShell**

Run:

```powershell
$env:PARALLAX_PS_HOST = (Get-Command powershell).Source
python -m pytest evals/multi-model-verify/test_review_mirror.py -q
```

Expected: all pass. Record the count.

- [ ] **Step 2: Run the mirror suite under PowerShell 7**

Run:

```powershell
$env:PARALLAX_PS_HOST = (Get-Command pwsh).Source
python -m pytest evals/multi-model-verify/test_review_mirror.py -q
```

Expected: the same count, all pass. A difference between the two hosts is a
finding, not noise: 0.16.1 shipped a lock that passed on Windows PowerShell
and did not lock on `pwsh`.

- [ ] **Step 3: Clear the host override and run the required suites**

Run:

```powershell
$env:PARALLAX_PS_HOST = $null
python evals/tools/skill_lint.py skills/multi-model-verify --strict
python evals/tools/skill_scanner.py skills
python evals/tools/run_trigger_evals.py
python -m pytest evals -q
```

Expected: all four green. These are what CI runs on every push.

- [ ] **Step 4: Update the rename wording in the reference**

`skills/multi-model-verify/references/backup-lane.md` currently says:

```markdown
    - **Rename or copy entries** (`R`/`C`, `old -> new`): hash the
      CURRENT DESTINATION path. The source path is a deletion and falls
      under the rule above.
```

Replace with:

```markdown
    - **Rename or copy entries** (`R`/`C`, recorded as `old -> new`):
      hash the CURRENT DESTINATION path. The source path is a deletion
      and falls under the rule above. The recorded form is git's DISPLAY
      order; the `-z` capture the mirror script reads emits the two
      pathnames in the opposite order, destination first, and the script
      renders them back into this form. Measured 2026-07-29.
```

- [ ] **Step 5: Confirm the contract regions still lock**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py -q`

Expected: PASS. This plan adds and removes no marked region, so
`DECLARED_REGIONS` is unchanged.

- [ ] **Step 6: Run the drift state machine, which drives this script**

Run:

```powershell
$env:PARALLAX_STATEMACHINE = "1"
python -m pytest evals -q
```

Expected: PASS. Slow — four scenarios re-run the full suite inside a
disposable worktree.

- [ ] **Step 7: Commit**

```bash
git add skills/multi-model-verify/references/backup-lane.md
git commit -m "record the -z rename field order in the baseline contract"
```

---

## Self-Review

**Spec coverage.**

| spec requirement | task |
|---|---|
| Capture: raw bytes, trailing NUL, split on NUL, strict UTF-8 | 1 |
| Empty trailing field discarded, interior empty field is a stop | 1 |
| Guard: not empty, no control character, no `"` | 2 |
| Parse: structural, `XY` + space + path, four-character minimum | 3 |
| Parse: rename consumes the NEXT field as source | 3 |
| Parse: missing second field is a stop | 3 |
| Deletion-only omitted, `RD` is a stop, destination hashed | 5 |
| Render: git display order, one way only | 4 |
| Manifest subjects from records, never from text | 5 |
| Delete the three decoder functions | 5 |
| Delete the ` -> ` text search | 5 |
| Delete the unreachable quoted-path check in the main flow | 5 |
| Delete `core.quotepath=false`, replace its comment | 5 |
| Error handling: git non-zero, no trailing NUL, bad UTF-8, empty field, missing rename source, guard failure, short field, `RD` | 1, 3, 5 |
| Whole suite on both hosts | 7 |
| Space, non-ASCII, rename with spaces, literal escape text | 6 |
| Manifest assertions split from the digest | 6 |
| Stale refusal test replaced, not deleted | 6 |

Two spec items are covered by tests that already exist and are not
rewritten: the non-ASCII cases
(`test_a_non_ascii_back_channel_is_removed_not_left_behind`,
`test_a_non_ascii_baseline_entry_reaches_the_manifest`) and the `RD` case
(`test_a_rename_whose_destination_was_deleted_blocks`). They pass through
the new code path unchanged, which is the regression evidence Task 5 Step 8
depends on.

**Placeholder scan.** No TBD, no "handle edge cases", no "similar to Task
N". Every code step carries the code.

**Type consistency.** `Invoke-GitProcess` returns `Bytes`;
`ConvertFrom-NulCapture` takes bytes and returns `Fields`;
`Invoke-GitFields` returns the `ConvertFrom-NulCapture` shape and adds
`Reason` on a process failure; `Get-BackChannelEntry` returns `Entries` and
`Reason`; `Get-BaselineRaw` returns the `Invoke-GitFields` shape;
`ConvertTo-StatusRecord` takes `Fields` and returns `Records`;
`Get-ManifestSubject` takes `Records` and returns `Paths`;
`Format-StatusRecord` takes one record and returns a string. Checked
against every call site named in Task 5.

**One case deliberately not end to end.** A filename containing a literal
backslash cannot exist on Windows, so `caf\303\251.txt` is tested at the
FIELD level, where the bytes can actually arrive, and its refusal is tested
at the parser, where the index entry would actually be caught. Building it
as one end-to-end case would have produced a test that passes because the
OS refused the setup.
