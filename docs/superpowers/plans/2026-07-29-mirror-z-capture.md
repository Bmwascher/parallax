# Mirror `-z` Capture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Switch both of `tools/new-review-mirror.ps1`'s git pathname
captures to `-z`, delete the hand-written C-style decoder, and parse the
status capture structurally so a rename can never resolve to the wrong
file.

**Architecture:** Six small functions replace one. `Invoke-GitProcess`
runs git and returns raw bytes. `ConvertFrom-NulCapture` turns those bytes
into fields, failing closed on a missing trailing NUL or invalid UTF-8.
`Test-SupportedPathname` refuses a name this tool cannot handle
exactly.
`ConvertTo-StatusRecord` builds structured records, consuming a rename's
source from the NEXT field. `Format-StatusPathname` reproduces git's
quoting for one pathname, and `Format-StatusRecord` uses it to render one
record in git's display order for the evidence record, one way only.

**Tech Stack:** Windows PowerShell 5.1 and PowerShell 7, git for Windows,
pytest driving both hosts.

**Spec:** `docs/superpowers/specs/2026-07-29-mirror-z-capture-design.md`

**STATUS: FROZEN 2026-07-29 at commit 8d14934.** Six rounds of cross-vendor
debate on two lanes, 30 amendments, nothing contested. Round 6 returned no
execution defect from either lane after both swept every live test
constraining every file this plan edits. From here the plan is the
specification: an implementer follows it as written, and a disagreement
with it is raised rather than resolved at the keyboard.

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

**Amendment A10, plan debate round 3, Sol lane (R6).** The `BODY_START`
edit used to be Step 1, BEFORE the function it names exists. That makes
`text.index(BODY_START)` in `run_functions` raise `ValueError` on the
red run, so the red would have been the harness failing to slice the
script rather than the function being undefined - a red for the wrong
reason, and the plan's stated expected result would not have happened. It
now runs AFTER the implementation, as Step 5.

**Amendment A16, plan debate round 4, Sol lane (S3).** Step 1 below is
new. Measured 2026-07-29 on BOTH hosts: a snippet calling an undefined
function returns exit code **0**, and `run_functions` returns the snippet's
partial output, so a missing function surfaces as a confusing VALUE
mismatch (`'|1'` against `'True|0'`) rather than as an error. That made the
old stated red - "the snippet exits non-zero and `run_functions` trips its
own assert" - simply untrue. Making the generated file stop on the first
error fixes every red in this plan at once, and makes a mistyped function
name in any future snippet fail loudly instead of quietly.

- [ ] **Step 1: Make the dot-source harness fail loudly**

In `evals/multi-model-verify/test_review_mirror.py`, inside
`run_functions`, change:

```python
        fh.write(body + "\n" + snippet)
```

to:

```python
        # Stop on the FIRST error. Measured 2026-07-29 on both hosts: an
        # undefined function is NON-terminating here, the host exits 0, and
        # the snippet's partial output comes back - so a missing or
        # mistyped function reads as a wrong VALUE instead of an error.
        # These snippets exercise pathname handling; a quiet failure is the
        # one outcome this module must not produce.
        fh.write('$ErrorActionPreference = "Stop"\n' + body + "\n" + snippet)
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
    # The old ConvertFrom-GitQuotedPath turned the ESCAPE PAIR
    # `\303\251` into character codes 195,169 - two characters -
    # where the byte pair names one, code 233. (The surrounding name
    # decoded normally: `caf\303\251` came out five characters, not
    # two. The two here are the escapes' own output.) Reading raw bytes
    # and decoding once from UTF-8 is what makes that impossible.
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

Run:

```bash
python -m pytest evals/multi-model-verify/test_review_mirror.py::test_an_empty_capture_is_a_legitimate_state evals/multi-model-verify/test_review_mirror.py::test_fields_split_on_nul_and_keep_their_spaces evals/multi-model-verify/test_review_mirror.py::test_a_capture_without_a_trailing_nul_stops evals/multi-model-verify/test_review_mirror.py::test_invalid_utf8_stops_instead_of_being_replaced evals/multi-model-verify/test_review_mirror.py::test_a_non_ascii_field_arrives_as_one_character_not_two_bytes evals/multi-model-verify/test_review_mirror.py::test_an_empty_field_before_the_end_is_kept_for_the_parser_to_refuse -v
```

Expected: FAIL, all 6, with the harness's own assert firing because the
generated file now stops on the first error and the host exits non-zero.

WITHOUT Step 1 this red would look different, and the difference is worth
knowing: measured 2026-07-29 on both hosts, an undefined function is
non-terminating, the host exits 0, and `run_functions` returns the
snippet's partial output - so the first case would fail on `'|1'` against
`'True|0'` rather than on anything naming the missing function.

**Amendment A11, plan debate round 3, backup lane (R6).** These steps name
the tests EXPLICITLY rather than selecting on `-k`. The old selector
`-k "capture or field or utf8"` also matched the pre-existing
`test_the_baseline_is_the_raw_status_capture`, which passes at this point,
so the stated count of 6 would have been 7. Naming the node ids cannot
drift as tests are added.

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

- [ ] **Step 5: Point the dot-source slice at the new first function**

`run_functions` slices the script between `BODY_START` and `BODY_END`, and
the two new functions sit ABOVE `Invoke-GitLines`, so the slice must start
at the new first function or it will not contain them.

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

This comes AFTER the implementation on purpose. See amendment A10 above.

- [ ] **Step 6: Run the tests to verify they pass**

Run:

```bash
python -m pytest evals/multi-model-verify/test_review_mirror.py::test_an_empty_capture_is_a_legitimate_state evals/multi-model-verify/test_review_mirror.py::test_fields_split_on_nul_and_keep_their_spaces evals/multi-model-verify/test_review_mirror.py::test_a_capture_without_a_trailing_nul_stops evals/multi-model-verify/test_review_mirror.py::test_invalid_utf8_stops_instead_of_being_replaced evals/multi-model-verify/test_review_mirror.py::test_a_non_ascii_field_arrives_as_one_character_not_two_bytes evals/multi-model-verify/test_review_mirror.py::test_an_empty_field_before_the_end_is_kept_for_the_parser_to_refuse -v
```

Expected: PASS, 6 tests.

- [ ] **Step 7: Run the whole module to prove nothing regressed**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -q`

Expected: the one pre-existing failure
(`test_a_quoted_baseline_entry_stops_instead_of_being_unquoted`) and
nothing new. Task 6 replaces that test.

- [ ] **Step 8: Commit**

```bash
git add tools/new-review-mirror.ps1 evals/multi-model-verify/test_review_mirror.py
git commit -m "read git pathname captures as raw NUL-separated bytes"
```

---

### Task 2: The supported-pathname guard

**Files:**
- Modify: `tools/new-review-mirror.ps1` — one function below
  `ConvertFrom-NulCapture`
- Test: `evals/multi-model-verify/test_review_mirror.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `Test-SupportedPathname($value)` returns `$true` or `$false`.

- [ ] **Step 1: Write the failing test**

Append to `evals/multi-model-verify/test_review_mirror.py`:

```python
def test_the_supported_pathname_guard_is_pinned_in_both_directions():
    # The guard admits exactly what Format-StatusPathname can record
    # exactly: an ordinary name, and a name whose ONLY quoting trigger is a
    # space. Everything the porcelain line form would quote or escape some
    # other way is refused, plus `>` for the arrow separator. Pinned in
    # both directions so a future edit cannot make the guard constant.
    out = run_functions(
        '$q = [char]34\n'
        '$results = @(\n'
        '  (Test-SupportedPathname "M+ Timer/core.lua"),\n'
        '  (Test-SupportedPathname "caf' + "é" + '/input.txt"),\n'
        '  (Test-SupportedPathname "a$([char]9)b.txt"),\n'
        '  (Test-SupportedPathname "a$([char]10)b.txt"),\n'
        '  (Test-SupportedPathname "a$([char]127)b.txt"),\n'
        '  (Test-SupportedPathname ("a" + $q + "b.txt")),\n'
        '  (Test-SupportedPathname "a\\b.txt"),\n'
        '  (Test-SupportedPathname "a>b.txt"),\n'
        '  (Test-SupportedPathname "")\n'
        ')\n'
        '($results -join ",")')
    assert out == ("True,True,False,False,False,"
                   "False,False,False,False"), out
```

**Amendment A1, plan debate round 1, Sol lane (P2, P4).** The `>` case is
in this list because the guard refuses `>`. The first draft named `>` in
the guard's own comment as a character Windows refuses and then did not
check it, so a `>`-bearing entry passed a function advertised as refusing
impossible names. It also mattered downstream: Task 4 justifies the ` -> `
render as unambiguous BECAUSE `>` cannot appear, and that argument is
empty unless the guard enforces it.

**Amendment A9, plan debate round 2, Kimi lane (Q2).** The 0x7F case is in
this list, and the function is renamed, because the earlier contract was
false. It claimed to refuse names Windows cannot hold, and argued from
that to the completeness of the one-condition quoting rule. Measured
2026-07-29: Windows CREATES `a<0x7F>b.txt`, and
`git status --porcelain` prints it as `?? "a\177b.txt"` with AND without
`core.quotepath=false`, while `-z` returns the byte raw. So a legal file
on a real disk passed the old guard and would have rendered bare where a
direct capture quotes it - the same defect class A2 exists to remove, in
the residue A2's own completeness argument claimed to have excluded.
Refusing it is right rather than rendering it: git's recorded form for
0x7F is the octal escape `\177`, and reproducing that would mean writing
the encoder this cycle deleted.

Note: this test file is read as UTF-8 by pytest, so the accented literal is
fine here. The SCRIPT stays ASCII; nothing above adds a non-ASCII character
to it.

- [ ] **Step 2: Run the test to verify it fails**

Run:

```bash
python -m pytest evals/multi-model-verify/test_review_mirror.py::test_the_supported_pathname_guard_is_pinned_in_both_directions -v
```

Expected: FAIL, `Test-SupportedPathname` is not recognized.

- [ ] **Step 3: Write the implementation**

Insert into `tools/new-review-mirror.ps1` below `ConvertFrom-NulCapture`:

```powershell
function Test-SupportedPathname($value) {
    # Under `-z` git never quotes, so whatever arrives IS the pathname.
    # The question this answers is whether this tool can handle that
    # pathname EXACTLY, in both senses:
    #
    #   1. Would resolving it risk naming the WRONG file? This is NOT a
    #      Windows name validator: it does not check reserved device
    #      names, trailing dots, length limits, or the other characters
    #      Windows refuses. A syntactically fine name with no file
    #      behind it is not this function's business; where it lands
    #      depends on its status shape, and only ONE of those routes is
    #      a stop. See the design record - the manifest stops on a
    #      subject with no file, deletion-only entries are omitted
    #      before that, and a back-channel match goes to remediation.
    #   2. Can Format-StatusPathname record it in the porcelain line form
    #      the baseline contract already uses?
    #
    # The admitted set is therefore an ordinary pathname, or one whose ONLY
    # line-form quoting trigger is a SPACE - the one trigger the renderer
    # reproduces. Everything else the line form quotes or escapes some
    # other way is refused, and so is `>`.
    #
    # REFUSING rather than rendering is the deliberate choice for that
    # residue. Git records it with git's own C-style encoder - NAMED
    # escapes for tab, newline, `"` and `\`, and OCTAL for the rest,
    # including the one reachable case, 0x7F as `\177`. Reproducing any
    # of that would mean writing back the encoder this cycle deletes. A
    # loud stop on a pathological name is the cheaper failure.
    #
    # The BACKSLASH refusal carries a second, heavier reason. git separates
    # path components with a forward slash, so a backslash in a field is a
    # literal character in a NAME - and `Join-Path` would then read it as a
    # separator and resolve a DIFFERENT file, which the script would delete
    # or hash under the name the baseline gave. That is false coverage
    # rather than a refusal, which is the one outcome this preflight exists
    # to prevent.
    #
    # `>` is refused for a reason of its own: Format-StatusRecord renders a
    # rename as `<old> -> <new>`, and that arrow is only unambiguous while
    # no pathname can contain `>`. The guard is what makes that true rather
    # than assumed.
    #
    # 0x7F is refused, and it is the case that shows why this function is
    # NOT named for Windows. Measured 2026-07-29: Windows CREATES
    # `a<0x7F>b.txt`, and `git status --porcelain` prints it as
    # `?? "a\177b.txt"` with AND without `core.quotepath=false`, while `-z`
    # returns the byte raw. It is legal on disk and a quoting trigger this
    # renderer cannot reproduce, so admitting it would put a bare name into
    # a baseline the direct capture quotes.
    #
    # Non-ASCII is NOT refused. The old captures set `core.quotepath=false`
    # and recorded an accented pathname raw, so it is not a trigger for the
    # form this baseline uses.
    $text = [string]$value
    if ($text.Length -eq 0) { return $false }
    foreach ($ch in $text.ToCharArray()) {
        if ([int]$ch -lt 32) { return $false }
        if ([int]$ch -eq 127) { return $false }
        if ($ch -eq [char]34) { return $false }
        if ($ch -eq '\') { return $false }
        if ($ch -eq '>') { return $false }
    }
    return $true
}
```

- [ ] **Step 4: Run the test to verify it passes**

Run:

```bash
python -m pytest evals/multi-model-verify/test_review_mirror.py::test_the_supported_pathname_guard_is_pinned_in_both_directions -v
```

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
git commit -m "refuse a pathname this tool cannot handle exactly"
```

---

### Task 3: Structural status parsing, with the inverted rename order

**Files:**
- Modify: `tools/new-review-mirror.ps1` — one function below
  `Test-SupportedPathname`
- Test: `evals/multi-model-verify/test_review_mirror.py`

**Interfaces:**
- Consumes: `Test-SupportedPathname($value)` from Task 2.
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
        '"{0}|{1}|[{2}{3}]" -f $rec.Path, $rec.Source, $rec.X, $rec.Y')
    assert out == "M+ Timer/new name.lua|M+ Timer/old name.lua|[R ]", out


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
    assert "cannot handle" in out, out


def test_a_del_character_in_a_status_pathname_stops():
    # 0x7F is the case the guard's old name got wrong. Windows CREATES
    # `a<0x7F>b.txt` - measured 2026-07-29 - and `git status --porcelain`
    # prints it as `?? "a\177b.txt"` with and without core.quotepath=false,
    # while -z returns the byte raw. It is above the control range, so a
    # `< 32` test admits it, and the render would then record it bare where
    # the direct capture quotes it.
    out = run_functions(
        '$r = ConvertTo-StatusRecord @("?? a$([char]127)b.txt"); $r.Error')
    assert "cannot handle" in out, out


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

**Amendment A31, build, self-caught at Task 3 Step 4.** The rename test's
expected value ended with a SPACE, because the record's `Y` column is a
space for a rename staged in the index. `run_functions` returns
`proc.stdout.strip()` (`test_review_mirror.py:606`), so a trailing space
can never survive and the assertion could not pass whatever the parser
did. Wrapping the two columns in brackets keeps exactly what the test
means to pin - `X` is `R` and `Y` is a space - and puts the space where
stripping cannot reach it. The implementation was correct as written and
did not change. Swept the whole plan for the same shape: this was the
only assertion whose expected literal ends in whitespace.

- [ ] **Step 2: Run the tests to verify they fail**

Run:

```bash
python -m pytest evals/multi-model-verify/test_review_mirror.py::test_a_rename_record_reads_destination_first_then_source evals/multi-model-verify/test_review_mirror.py::test_a_plain_entry_has_no_source_and_keeps_its_spaces evals/multi-model-verify/test_review_mirror.py::test_a_rename_with_no_source_field_stops evals/multi-model-verify/test_review_mirror.py::test_a_copy_in_the_second_column_also_consumes_a_source evals/multi-model-verify/test_review_mirror.py::test_a_control_character_in_a_status_pathname_stops evals/multi-model-verify/test_review_mirror.py::test_a_del_character_in_a_status_pathname_stops evals/multi-model-verify/test_review_mirror.py::test_a_status_field_too_short_to_carry_a_pathname_stops evals/multi-model-verify/test_review_mirror.py::test_a_status_field_with_no_space_after_the_code_stops evals/multi-model-verify/test_review_mirror.py::test_an_empty_status_field_stops -v
```

Expected: FAIL, `ConvertTo-StatusRecord` is not recognized.

- [ ] **Step 3: Write the implementation**

Insert into `tools/new-review-mirror.ps1` below `Test-SupportedPathname`:

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
        if (-not (Test-SupportedPathname $path)) {
            return @{ Error = ("status entry '" + $field + "' names a" +
                " path this script cannot handle exactly, on one of the" +
                " guard's two grounds: resolving it would risk naming the" +
                " WRONG file, or it cannot be recorded unambiguously in" +
                " the baseline's line form") }
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
            if (-not (Test-SupportedPathname $source)) {
                return @{ Error = ("rename or copy entry '" + $field +
                    "' names a source this script cannot handle" +
                    " exactly, on the same two grounds") }
            }
        }
        [void]$records.Add(@{ X = $x; Y = $y; Path = $path
                              Source = $source })
    }
    return @{ Records = @($records) }
}
```

- [ ] **Step 4: Run the tests to verify they pass**

Run:

```bash
python -m pytest evals/multi-model-verify/test_review_mirror.py::test_a_rename_record_reads_destination_first_then_source evals/multi-model-verify/test_review_mirror.py::test_a_plain_entry_has_no_source_and_keeps_its_spaces evals/multi-model-verify/test_review_mirror.py::test_a_rename_with_no_source_field_stops evals/multi-model-verify/test_review_mirror.py::test_a_copy_in_the_second_column_also_consumes_a_source evals/multi-model-verify/test_review_mirror.py::test_a_control_character_in_a_status_pathname_stops evals/multi-model-verify/test_review_mirror.py::test_a_del_character_in_a_status_pathname_stops evals/multi-model-verify/test_review_mirror.py::test_a_status_field_too_short_to_carry_a_pathname_stops evals/multi-model-verify/test_review_mirror.py::test_a_status_field_with_no_space_after_the_code_stops evals/multi-model-verify/test_review_mirror.py::test_an_empty_status_field_stops -v
```

Expected: PASS, 9 tests.

- [ ] **Step 5: Commit**

```bash
git add tools/new-review-mirror.ps1 evals/multi-model-verify/test_review_mirror.py
git commit -m "parse the -z status capture structurally"
```

---

### Task 4: Rendering one record for the evidence

**Files:**
- Modify: `tools/new-review-mirror.ps1` — TWO functions below
  `ConvertTo-StatusRecord`
- Test: `evals/multi-model-verify/test_review_mirror.py`

**Interfaces:**
- Consumes: a record from `ConvertTo-StatusRecord($fields)` (Task 3).
- Produces:
  - `Format-StatusPathname($path)` returns a `[string]`: the pathname,
    wrapped in double quotes if and only if it contains a space.
  - `Format-StatusRecord($record)` returns a `[string]`, calling
    `Format-StatusPathname` for the destination and, on a rename or copy,
    for the source independently.

- [ ] **Step 1: Write the failing tests**

Append to `evals/multi-model-verify/test_review_mirror.py`:

```python
def test_a_rename_renders_in_gits_display_order_with_its_quoting():
    # The recorded baseline must stay byte-comparable with a capture taken
    # by running THE STATUS COMMAND directly, which is what
    # references/backup-lane.md requires of every round. Measured
    # 2026-07-29, that command prints both spaced names QUOTED. The arrow
    # is unambiguous because Test-SupportedPathname refuses `>`.
    out = run_functions(
        '$r = ConvertTo-StatusRecord @("R  M+ Timer/new name.lua",\n'
        '                              "M+ Timer/old name.lua")\n'
        'Format-StatusRecord $r.Records[0]')
    assert out == ('R  "M+ Timer/old name.lua" -> "M+ Timer/new name.lua"'), out


def test_each_side_of_a_rename_is_quoted_independently():
    # Measured 2026-07-29: a spaced source with a plain destination prints
    # `R  "with space/a.lua" -> plain/a.lua`. Quoting the pair together, or
    # quoting both whenever either has a space, would both be wrong.
    out = run_functions(
        '$r = ConvertTo-StatusRecord @("R  plain/a.lua",\n'
        '                              "with space/a.lua")\n'
        'Format-StatusRecord $r.Records[0]')
    assert out == 'R  "with space/a.lua" -> plain/a.lua', out


def test_a_plain_entry_renders_unquoted():
    out = run_functions(
        '$r = ConvertTo-StatusRecord @("!! ignored/note.txt")\n'
        'Format-StatusRecord $r.Records[0]')
    assert out == "!! ignored/note.txt", out


def test_a_spaced_entry_renders_quoted():
    out = run_functions(
        '$r = ConvertTo-StatusRecord @("!! ignored dir/note.txt")\n'
        'Format-StatusRecord $r.Records[0]')
    assert out == '!! "ignored dir/note.txt"', out


def test_a_non_ascii_entry_renders_unquoted():
    # The old captures set core.quotepath=false, so an accented pathname
    # was recorded RAW. This render must keep that shape rather than
    # introduce quoting the baseline never had.
    #
    # Asserted as CHARACTER CODES, not as a literal. run_functions decodes
    # the host's stdout with the locale, so comparing an accented literal
    # here would test the harness's decoding rather than the renderer. The
    # codes are 63,63,32 for "?? " then 99,97,102,233 for "caf" and the
    # accented letter.
    out = run_functions(
        '$e = [char]233\n'
        '$r = ConvertTo-StatusRecord @("?? caf$e.txt")\n'
        '$line = Format-StatusRecord $r.Records[0]\n'
        '(([int[]][char[]]$line) -join ",")')
    assert out == "63,63,32,99,97,102,233,46,116,120,116", out


def test_a_status_code_with_a_leading_space_survives_rendering():
    # ` M` and ` D` are ordinary porcelain codes. Trimming the render would
    # change what the record says happened.
    out = run_functions(
        '$r = ConvertTo-StatusRecord @(" M kept.txt")\n'
        '"[{0}]" -f (Format-StatusRecord $r.Records[0])')
    assert out == "[ M kept.txt]", out
```

- [ ] **Step 2: Run the tests to verify they fail**

Run:

```bash
python -m pytest evals/multi-model-verify/test_review_mirror.py::test_a_rename_renders_in_gits_display_order_with_its_quoting evals/multi-model-verify/test_review_mirror.py::test_each_side_of_a_rename_is_quoted_independently evals/multi-model-verify/test_review_mirror.py::test_a_plain_entry_renders_unquoted evals/multi-model-verify/test_review_mirror.py::test_a_spaced_entry_renders_quoted evals/multi-model-verify/test_review_mirror.py::test_a_non_ascii_entry_renders_unquoted evals/multi-model-verify/test_review_mirror.py::test_a_status_code_with_a_leading_space_survives_rendering -v
```

Expected: FAIL, `Format-StatusRecord` is not recognized.

- [ ] **Step 3: Write the implementation**

Insert into `tools/new-review-mirror.ps1` below `ConvertTo-StatusRecord`:

```powershell
function Format-StatusPathname($path) {
    # Reproduce the porcelain LINE form's quoting for one pathname, so a
    # recorded baseline is byte-comparable with a capture taken by running
    # THE STATUS COMMAND directly - which is what
    # references/backup-lane.md requires of every round.
    #
    # The rule is one condition because the guard has already removed every
    # other trigger. Measured 2026-07-29: `git status --porcelain` quotes
    # each pathname independently and, once `"` , `\` and the control
    # characters are refused, a SPACE is the only remaining trigger. In the
    # same measurement a rename with a spaced source and a plain
    # destination printed `R  "with space/a.lua" -> plain/a.lua`, and the
    # reverse printed `R  plain/b.lua -> "with space/b.lua"` - each side on
    # its own.
    #
    # Non-ASCII is deliberately NOT quoted. The old captures set
    # `core.quotepath=false`, so an accented pathname was recorded raw, and
    # this render must keep that shape rather than introduce quoting the
    # baseline never had.
    if ([string]$path -match ' ') { return ('"' + $path + '"') }
    return [string]$path
}

function Format-StatusRecord($record) {
    # Render one record in git's own DISPLAY order, `R  <old> -> <new>`, so
    # the recorded baseline keeps the shape references/backup-lane.md
    # already describes and two captures stay comparable across this
    # change.
    #
    # ONE WAY ONLY. Nothing re-parses this text: the manifest's subjects
    # come from the RECORDS. That separation is the whole reason the arrow
    # is safe to write here at all, and Test-SupportedPathname refusing `>`
    # is what keeps it unambiguous.
    $head = [string]$record.X + [string]$record.Y + " "
    if ($record.Source) {
        return ($head + (Format-StatusPathname $record.Source) + " -> " +
                (Format-StatusPathname $record.Path))
    }
    return ($head + (Format-StatusPathname $record.Path))
}
```

**Amendment A2, plan debate round 1, Sol lane (P11).** The first draft
rendered every pathname bare. Run 2026-07-29 against the CURRENT script,
a spaced untracked file records as `?? "M+ Timer/input.txt"` - quoted. The
backup-lane contract requires each round's status capture to equal the
baseline, and a driver running THE STATUS COMMAND still gets the quoted
line form, so a bare render would have made every space-bearing path read
as a change on every round. `Format-StatusPathname` is the surgical fix:
the quoting rule is one condition precisely because the guard removed the
others. The manifest is NOT affected and stays unquoted - confirmed in the
same run, which printed `M+ Timer/input.txt <sha256>`.

- [ ] **Step 4: Run the tests to verify they pass**

Run:

```bash
python -m pytest evals/multi-model-verify/test_review_mirror.py::test_a_rename_renders_in_gits_display_order_with_its_quoting evals/multi-model-verify/test_review_mirror.py::test_each_side_of_a_rename_is_quoted_independently evals/multi-model-verify/test_review_mirror.py::test_a_plain_entry_renders_unquoted evals/multi-model-verify/test_review_mirror.py::test_a_spaced_entry_renders_quoted evals/multi-model-verify/test_review_mirror.py::test_a_non_ascii_entry_renders_unquoted evals/multi-model-verify/test_review_mirror.py::test_a_status_code_with_a_leading_space_survives_rendering -v
```

Expected: PASS, 6 tests.

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
  `Test-SupportedPathname` (Task 2), `ConvertTo-StatusRecord` (Task 3),
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
    # An entry this script cannot handle exactly is a stop, on either of
    # the guard's two grounds - a name whose resolution would risk the
    # WRONG file, or a name it could resolve but could not record.
    # Reporting either as clean is the one outcome the whole preflight
    # exists to prevent, and a back-channel is the case where that matters
    # most.
    foreach ($e in @($r.Fields)) {
        if (-not (Test-SupportedPathname $e)) {
            return @{ Ok = $false; Entries = @()
                      Reason = ("the back-channel entry '" + $e + "' names" +
                        " a path this script cannot handle exactly, so it" +
                        " cannot be enumerated, deleted and recorded as a" +
                        " single consistent fact") }
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
    # @{Error=..}.
    #
    # Two dispositions are DEFINED and are not the same thing as skipping.
    # A deletion-only entry is OMITTED, deliberately, because it has no
    # bytes; an `RD` destination is a STOP. What must never happen is a
    # third thing: an entry passed over because this function could not
    # make sense of it. That is the silent hole in the manifest, and it is
    # what the stops below exist to prevent.
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
quoted, and `Test-SupportedPathname` inside `Get-BackChannelEntry` now covers
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
- Modify: `evals/multi-model-verify/test_review_mirror.py` — the manifest
  splitting in `test_the_manifest_covers_exactly_the_baseline_paths`
  (`:270-282`), `test_the_manifest_hashes_raw_bytes_and_sorts_by_path`
  (`:284-296`) and `test_a_directory_expands_recursively` (`:298-313`),
  then the two stale tests (`:603-621`)
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
    # The MANIFEST is unquoted and the BASELINE is quoted. Both shapes are
    # what the current script already records for a spaced path; run
    # 2026-07-29 it printed `?? "M+ Timer/input.txt"` under `baseline:` and
    # `M+ Timer/input.txt <sha256>` under `manifest:`.
    assert f"{SPACED}/input.txt {expected}" in proc.stdout, proc.stdout
    assert f'?? "{SPACED}/input.txt"' in proc.stdout, proc.stdout


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
    assert '!! "refs with spaces/note.txt"' in proc.stdout, proc.stdout


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
    assert (f'R  "{SPACED}/old name.lua" -> "{SPACED}/new name.lua"'
            in baseline), baseline


def test_escape_looking_field_text_is_never_interpreted():
    # `caf\303\251` is the exact string the deleted decoder mishandled.
    # On the quoted form it turned the 15 characters of
    # `caf\303\251.txt` into NINE: three ordinary, two produced by the
    # octal escapes, and four from `.txt`. Neither produced character is
    # the accented letter the real name holds.
    #
    # Under -z the bytes ARE the pathname, so the field must come back as
    # the 15 literal characters it is.
    #
    # This is a FIELD-level case and not an end-to-end one on purpose. A
    # file with this name cannot exist on Windows, because the backslash is
    # a path separator there - measured 2026-07-29. The bytes can still
    # arrive from git's INDEX, which is what Test-SupportedPathname then
    # refuses, so the two halves are tested where each can actually be
    # reached.
    out = run_functions(
        '$b = [System.Text.Encoding]::UTF8.GetBytes("caf\\303\\251.txt`0")\n'
        '$r = ConvertFrom-NulCapture $b\n'
        '"{0}|{1}" -f $r.Fields[0], $r.Fields[0].Length')
    assert out == "caf\\303\\251.txt|15", out


def test_uppercase_escape_looking_field_text_is_never_interpreted():
    # THE SECOND DECODER DEFECT, pinned so it cannot return. PowerShell's
    # `switch` is case-INSENSITIVE by default, so the deleted decoder turned
    # `a\Tb.txt` into a TAB and `a\Nb.txt` into a NEWLINE - escapes C-style
    # quoting leaves undefined. Under -z the bytes are the pathname, so both
    # must arrive as their eight literal characters.
    out = run_functions(
        '$b = [System.Text.Encoding]::UTF8.GetBytes("a\\Tb.txt`0a\\Nb.txt`0")\n'
        '$r = ConvertFrom-NulCapture $b\n'
        '(@($r.Fields | ForEach-Object { ([int[]][char[]]$_) -join "," })'
        ' -join "|")')
    # a \ T b . t x t  and  a \ N b . t x t
    assert out == ("97,92,84,98,46,116,120,116|"
                   "97,92,78,98,46,116,120,116"), out


def test_a_backslash_bearing_index_entry_stops_the_enumeration():
    # The other half. git reads names from its INDEX, which can carry a
    # name Windows cannot represent. Join-Path would read the backslash as
    # a separator and resolve a DIFFERENT file, which the script would then
    # delete or hash under the name the baseline gave.
    out = run_functions(
        '$r = ConvertTo-StatusRecord @("?? caf\\303\\251.txt"); $r.Error')
    assert "cannot handle" in out, out
```

- [ ] **Step 4: Run the new tests to verify they pass**

Run:

```bash
python -m pytest evals/multi-model-verify/test_review_mirror.py::test_a_back_channel_under_a_spaced_directory_is_removed evals/multi-model-verify/test_review_mirror.py::test_a_spaced_baseline_entry_reaches_the_manifest evals/multi-model-verify/test_review_mirror.py::test_a_spaced_ignored_entry_reaches_the_manifest evals/multi-model-verify/test_review_mirror.py::test_a_rename_with_spaces_hashes_the_destination_not_the_source evals/multi-model-verify/test_review_mirror.py::test_a_rename_renders_in_the_baseline_as_source_arrow_destination evals/multi-model-verify/test_review_mirror.py::test_escape_looking_field_text_is_never_interpreted evals/multi-model-verify/test_review_mirror.py::test_uppercase_escape_looking_field_text_is_never_interpreted evals/multi-model-verify/test_review_mirror.py::test_a_backslash_bearing_index_entry_stops_the_enumeration -v
```

Expected: PASS, 8 tests.

**Amendment A20, self-caught before plan debate round 5.** A11 converted
Tasks 1, 3 and 4 from `-k` selectors to explicit node ids and left Tasks 2
and 6 behind. Task 6's selector was the dangerous one: `-k "spaced or
rename or ..."` also matches the pre-existing
`test_a_rename_whose_destination_was_deleted_blocks`, so the step would
have reported 9 where it verified 8. The same class as A7, A11 and A17,
found this time by checking the plan against itself rather than by
spending a round on it.

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
- Modify: `skills/multi-model-verify/references/backup-lane.md:225-235`,
  where THE STATUS COMMAND gains `-c core.quotepath=false`
- Modify: `skills/multi-model-verify/references/backup-lane.md:299-301`
- Modify: `evals/multi-model-verify/test_backup_lane.py:283-285`, the pins
  that quote the status command
- Modify: `evals/multi-model-verify/test_backup_lane.py:335-337`, the pin
  that quotes the rename sentence
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

- [ ] **Step 3b: Put `core.quotepath=false` into THE STATUS COMMAND**

**Amendment A12, plan debate round 3, both lanes (R7).** The primary lane
called this a FIX and the backup lane recorded it as an observation that
predates the amendments. Both are right, and it is a real hole either way.

`references/backup-lane.md:225` mandates
`git status --porcelain --ignored -uall` for every capture, with no
`core.quotepath` flag, and requires each round's output to EQUAL the
baseline. Git's default `core.quotepath` is TRUE. Measured 2026-07-29:
with the default, a `café.txt` untracked file prints
`?? "caf\303\251.txt"`; with `-c core.quotepath=false` it prints raw.

The script has recorded the raw form since 0.17.0, because its own capture
set the flag. So the documented command and the recorded baseline have
disagreed for non-ASCII paths all along. This plan does not create the
hole, but it is the plan that removes the flag from the script, so it is
the plan that must state the comparison command exactly.

In `skills/multi-model-verify/references/backup-lane.md`, change the
opening of THE STATUS COMMAND bullet from:

```markdown
- **THE STATUS COMMAND — `git status --porcelain --ignored -uall`, every
  capture without exception**
```

to:

```markdown
- **THE STATUS COMMAND — `git -c core.quotepath=false status --porcelain
  --ignored -uall`, every capture without exception**
```

Then add this sentence at the end of that bullet:

```markdown
  `core.quotepath=false` is load-bearing for COMPARABILITY, not for
  correctness of any single capture: git's default renders a non-ASCII
  pathname as a quoted display form carrying octal escapes, while the
  mirror's recorded baseline carries the same pathname raw, so a per-round
  capture taken without the flag reports a difference that does not exist.
  The escaped form is not written out here, because this file is checked
  for the absence of backslashes; it is in the design record. Measured
  2026-07-29.
```

Update the two pins in `evals/multi-model-verify/test_backup_lane.py` that
quote the command. Replace:

```python
    assert "`git status --porcelain --ignored -uall`, every" in body
```

with:

```python
    assert ("`git -c core.quotepath=false status --porcelain --ignored "
            "-uall`, every") in body
    assert ("git's default renders a non-ASCII pathname as a quoted "
            "display form carrying octal escapes, while the mirror's "
            "recorded baseline carries the same pathname raw") in body
```

`body` in that test is `_norm(...)`, a whitespace-normalized read
(`test_backup_lane.py:36-38`), so both pins are written as single-spaced
text and the markdown wrap does not matter.

**TWO suites ban backslashes in this file, not one.**
`test_backup_files_no_backslash_paths`
(`evals/multi-model-verify/test_backup_lane.py:75`) covers it as one of
three backup-lane artifacts, and `test_no_backslash_paths_anywhere`
(`evals/multi-model-verify/test_multi_model_verify.py:89`) covers it as
one of the required reference files. Both ban the same character, so the
backslash-free wording above satisfies both - but an editor who finds and
satisfies only one of them is still exposed. Found by the backup lane in
round 6 while sweeping for the class A21 belongs to.

Leave the second pin at `:284` alone. It quotes
``bare `git status --porcelain` OMITS ignored paths entirely``, which is
about the missing FLAGS, and that sentence is unchanged.

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

- [ ] **Step 4b: Update the pin that quotes that sentence**

**Amendment A4, plan debate round 1, Kimi lane (P14).** The first draft
rewrote the sentence and did not update the test that pins it, so its own
Step 6 full-suite run would have ended red while claiming PASS.
`test_contract_coverage.py` stays green either way, because the sentence
sits outside every marked region; the red is in `test_backup_lane.py`.

In `evals/multi-model-verify/test_backup_lane.py`, replace:

```python
    assert ("**Rename or copy entries** (`R`/`C`, `old -> new`): hash "
            "the CURRENT DESTINATION path. The source path is a "
            "deletion and falls under the rule above.") in body
```

with:

```python
    assert ("**Rename or copy entries** (`R`/`C`, recorded as "
            "`old -> new`): hash the CURRENT DESTINATION path. The "
            "source path is a deletion and falls under the rule "
            "above.") in body
    # The wire order is the opposite of the recorded order, so the
    # sentence that says so is pinned in its own right: a driver reading
    # only the display form would build a parser that hashes the source.
    assert ("the `-z` capture the mirror script reads emits the two "
            "pathnames in the opposite order, destination first") in body
```

Leave the history fixtures alone.
`evals/multi-model-verify/fixtures/contract-coverage-history/instance-10-pins.py:237`
and `instance-11-pins.py:248` quote the same sentence, but they read their
own FROZEN doc fixtures rather than the live reference, so editing them
would break the history they exist to record.

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
git add skills/multi-model-verify/references/backup-lane.md evals/multi-model-verify/test_backup_lane.py
git commit -m "record the -z rename field order in the baseline contract"
```

---

## Self-Review

**Spec coverage.**

| spec requirement | task |
|---|---|
| Capture: raw bytes, trailing NUL, split on NUL, strict UTF-8 | 1 |
| Empty trailing field discarded, interior empty field is a stop | 1 |
| Guard: not empty, no control character, no 0x7F, no `"`, no `\`, no `>` | 2 |
| Parse: structural, `XY` + space + path, four-character minimum | 3 |
| Parse: rename consumes the NEXT field as source | 3 |
| Parse: missing second field is a stop | 3 |
| Deletion-only omitted, `RD` is a stop, destination hashed | 5 |
| Render: git display order, its quoting, one way only | 4 |
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
`Format-StatusPathname` takes one pathname string and returns a string;
`Format-StatusRecord` takes one record, calls `Format-StatusPathname` per
pathname, and returns a string. Checked against every call site named in
Task 5.

**One case deliberately not end to end.** A filename containing a literal
backslash cannot exist on Windows, so `caf\303\251.txt` is tested at the
FIELD level, where the bytes can actually arrive, and its refusal is tested
at the parser, where the index entry would actually be caught. Building it
as one end-to-end case would have produced a test that passes because the
OS refused the setup.

---

## Amendments

Plan debate round 1, both lanes, 2026-07-29, at head `012fdf8`. Sol
session `019faceb-f689-7f72-a6e6-74daa14e3225`, effective route
confirmed; Kimi session
`ff776da3-b0a0-4018-9ba7-33e8ba5fb79a`, route line verified
(client-side), write probe PASS.

Each lane found something the other missed, and both findings were settled
by RUNNING the case rather than by weighing the lanes.

- **A1 — the guard did not refuse `>` (Sol, P2 and P4).** Its own comment
  named `>` as a character Windows refuses and the code did not check it.
  Task 4 also justified the ` -> ` render as unambiguous BECAUSE `>`
  cannot appear, so the argument was empty until the guard enforced it.
  Task 2 now refuses `>` and pins that direction.
- **A2 — the render dropped git's quoting (Sol, P11).** THE FINDING THAT
  WOULD HAVE SHIPPED A BROKEN CONTRACT. Run 2026-07-29 against the current
  script, a spaced untracked file records as `?? "M+ Timer/input.txt"`.
  `references/backup-lane.md` requires each round's status capture to equal
  the baseline, and a driver running THE STATUS COMMAND still gets the
  quoted line form, so a bare render would have made every space-bearing
  path read as a change on every round. Measured in the same session: git
  quotes each side of a rename INDEPENDENTLY, and once the guard has
  refused `"`, `\` and the control characters, a SPACE is the only
  remaining trigger. `Format-StatusPathname` is one condition for that
  reason. The manifest is unaffected and stays unquoted.
- **A3 — the second decoder defect was untested (Sol, P12).** The plan
  pinned the byte-versus-character defect and not the case-insensitive
  `\T` and `\N` one. Task 6 now pins both at field level.
- **A4 — the reference edit broke a pin in another suite (Kimi, P14).**
  Task 7 rewrote a sentence in `backup-lane.md` that
  `evals/multi-model-verify/test_backup_lane.py:335-337` quotes verbatim,
  while Step 6 claimed the full suite would pass. It would have ended red.
  Step 4b now updates that pin in the same step, and adds a second pin for
  the new wire-order sentence. The history fixtures that quote the same
  text read frozen doc copies and are deliberately left alone.
- **A5 — a stale line-range citation (Kimi, non-blocking).** Task 6's
  Files header cited `:270-296` for three edits, one of which lives at
  `:298-313`. Corrected to name each function with its own range.

**Where the lanes split.** Sol raised P11 and Kimi passed it; Kimi raised
P14 and Sol did not reach it. Kimi's P11 PASS checked the arrow shape
against the contract and did not check the quoting, which is what the run
settled. Neither lane is treated as authoritative: the current script was
executed against a spaced path, and the recorded output decided it.

### Round 2, Sol lane, 2026-07-29

Same session, effective route confirmed, at head `a9a788c`. Q2, Q4 and Q5
PASS; Q1 and Q3 FIX. All three findings are bookkeeping defects that
amendment A2 introduced, and all three are the same class: a declaration
that stopped matching the code beside it.

- **A6 — the sixth function was never declared.** A2 added
  `Format-StatusPathname` and left the Architecture paragraph saying five
  functions, Task 4's Files line saying one function, Task 4's Interfaces
  exposing only `Format-StatusRecord`, and the self-review type list
  without it. All four now name it.
- **A7 — a stale expected count.** Task 4 Step 4 still said "PASS, 3
  tests" after A2 took the render cases from three to six. Corrected to
  six. This is the class the plan is meant to catch in itself: a step
  whose stated expected result is not what would happen.
- **A8 — an off-by-one in a comment.** A3 called `a\Tb.txt` "seven
  literal characters" while its own assertion lists eight character
  codes. Corrected to eight. Kimi raised the same nit independently.

### Round 2, Kimi lane, 2026-07-29

Same session resumed, route line verified (client-side), at head
`a9a788c`. Q1, Q3, Q4 and Q5 PASS; Q2 FIX.

- **A9 — 0x7F broke A2's completeness argument, and the guard's name was
  false.** THE SHARPEST FINDING OF THE CYCLE. A2 argued the one-condition
  quoting rule was complete "because the guard has already refused `"`,
  `\`, `>` and every control character". The guard tested `< 32`, which
  admits 0x7F. Measured 2026-07-29 to settle it, exactly as A1 and A2 were
  settled: Windows CREATES `a<0x7F>b.txt`; `git status --porcelain` prints
  it `?? "a\177b.txt"` with AND without `core.quotepath=false`; `-z`
  returns the byte raw and it is valid single-byte UTF-8, so the strict
  decode passes it through. A legal file on a real disk therefore rendered
  bare where the direct capture quotes it - the P11 defect class, inside
  the residue A2 claimed to have excluded, and reachable from disk rather
  than only from the index.

  The repair is larger than one character test, because the CONTRACT was
  wrong and not just the code. `Test-WindowsPathname` is renamed
  `Test-SupportedPathname` and now states what it actually decides: can
  this tool handle the pathname EXACTLY, both as a file it can delete and
  hash AND as a name `Format-StatusPathname` can record in the line form.
  [Corrected by A19 in round 4: "a file it can delete and hash" is still
  too broad, and is the same overclaim in a smaller form. The first ground
  is narrower - would resolving the name risk the WRONG file. The guard
  validates no other Windows naming rule. Annotated in place rather than
  rewritten, for the reason given under the octal annotation below.]
  Windows legality was never the real question, and the old name was the
  same class of defect A1 fixed - a declaration that did not match what
  the code decides.

  Refusing 0x7F rather than rendering it is deliberate: git records the
  other triggers with OCTAL ESCAPES, and reproducing those would mean
  writing the encoder this cycle exists to delete.
  [Corrected by A14 in round 3: "the other triggers" is too broad. Tab,
  newline, `"` and `\` get NAMED escapes; octal is used for the rest,
  including the one reachable case, 0x7F as `\177`. The conclusion is
  unchanged. This record is left standing and annotated rather than
  rewritten, because an amendment log that edits its own history stops
  being evidence.]

**Where the lanes split, round 2.** Sol found three declaration defects A2
introduced and passed A2's substance; Kimi passed the declarations and
found A2's completeness argument false. Neither lane reached the other's
finding. Both were settled by running the case: Sol's by reading the
amended plan against itself, Kimi's by creating a 0x7F file on this disk
and capturing git's output three ways.

### Round 3, both lanes, 2026-07-29

At head `eb9f5e9`. Sol: R4, R5 PASS; R1, R2, R3, R6, R7 FIX. Kimi: R1, R2,
R5, R7 PASS; R3, R4, R6 FIX. Amendments A10 to A12 above, plus:

- **A13 — an off-by-count in a sibling comment (Kimi, R4).** The comment
  in `test_escape_looking_field_text_is_never_interpreted` said the
  decoder "turned those nine characters into two". `caf\303\251` is
  eleven characters and the test's own assertion expects length 15.
  Corrected to eleven and four. Same class as A8, one test away from it,
  and A8 did not look sideways.
  [SUPERSEDED by A17 in round 4: "four" was itself wrong. The old decoder
  turns those eleven characters into FIVE, and the full fifteen-character
  field into NINE. "Four" is the length of the CORRECT decode, which is
  the one result that defect never produced. Annotated in place, not
  rewritten.]
- **A14 — the octal claim was overgeneral (both lanes).** Both said it
  independently. "Git records every other trigger with an OCTAL ESCAPE" is
  false: tab, newline, `"` and `\` get NAMED escapes. True only of the one
  reachable case, 0x7F. Reworded in the plan and the spec.
- **A15 — three stale contract sites survived the rename (both lanes).**
  The spec's error list still said "Windows-path guard"; the spec still
  said the guard "can only fire" on an impossible Windows path, which A9
  made false; and `Get-BackChannelEntry`'s comment and message still
  reasoned from what the platform can name. All three rewritten. The spec
  also gains an explicit statement of what the guard does NOT claim,
  because two consecutive drafts of it advertised more than the code did.

**One finding NOT adopted, with the measurement that settles it.** Sol's
R1 asked for index-only coverage of every guard-admitted ASCII character
Windows cannot create, on the grounds that git's index can carry names the
filesystem cannot. Measured 2026-07-29: `git update-index --add
--cacheinfo` REFUSES every one of them on this platform - `x<y.txt`,
`x:y.txt`, `x|y.txt`, `x?y.txt`, `x*y.txt` each returned
`error: Invalid path`. There is no such residue to sweep here.

Two things keep that from being the whole answer, and both are recorded
rather than argued away. A clone of a repository authored elsewhere is a
different path into the index and was NOT measured. And independently of
that, none of those characters is a C-style quoting trigger, so even if
one arrived it would come back BARE from both the line form and `-z`, and
the render would match - the completeness claim concerns quoting and is
untouched. What such an entry would do downstream was stated too
strongly in the first draft of this paragraph and both lanes corrected
it in round 4: it does NOT reach a guaranteed stop. A cloned index entry
whose name the filesystem cannot create has no worktree file, so status
reports it as a deletion-only entry, and those are deliberately OMITTED
before `Get-ContentManifest` sees any subject. A name matching the
back-channel pathspec takes the remediation path instead. Neither route
was measured. The omission is benign on its own terms - HEAD binds the
content and there are no bytes to hash - but "the manifest already stops
on it" was not true, and is not claimed here. Recorded as an accepted
limit, not closed.

### Round 4, both lanes, 2026-07-29

At head `d731c05`. Sol: S1, S2 PASS; S3, S4, S5, S6 FIX. Kimi: S1, S2, S3,
S5 PASS; S4, S6 FIX.

- **A16 - the stated red was not the red that would happen (Sol, S3).**
  Every "run it to see it fail" step in Task 1 claimed the dot-sourced
  snippet exits non-zero and `run_functions` trips its own assert.
  Measured 2026-07-29 on BOTH hosts: an undefined function is
  NON-terminating, the host exits **0**, and `run_functions` returns the
  snippet's partial output, so the case would have failed on `'|1'`
  against `'True|0'` - a red that names nothing. New Task 1 Step 1 makes
  the generated file set `$ErrorActionPreference = "Stop"`, which fixes
  every red in the plan at once and makes a mistyped function name in any
  future snippet fail loudly. Task 1 renumbered to 1-8.
- **A17 - the count correction was itself miscounted, twice (both
  lanes).** A13 said "eleven characters into four". The old decoder turns
  `caf\303\251` (11 characters) into FIVE, and the full field
  `caf\303\251.txt` (15) into NINE; "four" is the length of the CORRECT
  decode, which is the one thing the defect never produced. A second stale
  "nine" survived two lines below, describing the 15-character field. The
  whole comment is rewritten. This is the fourth consecutive round to find
  a defect inside the previous round's fix, and the second inside a
  correction to a count.
- **A18 - the declined finding claimed a stop that does not happen (both
  lanes).** Its text said a foreign index entry "would name a file with no
  bytes behind it, which `Get-ContentManifest` already stops on". Both
  lanes traced the same counter-path: such an entry has no worktree file,
  so status reports it as deletion-only, and those are OMITTED before the
  manifest sees any subject; a back-channel match takes the remediation
  path instead. Neither route was measured. The guarantee is removed and
  the two routes are recorded.
- **A19 - two residual overclaims (Sol, S4).** The guard's first ground
  still read "can it name a file the script can delete and hash", which is
  the broad file-legality claim A15's own disclaimer contradicts, in both
  the spec and the implementation comment. Both narrowed to "would
  resolving it risk naming the WRONG file". A9's historical record still
  carried the pre-A14 octal sentence; it is annotated in place rather than
  rewritten, because an amendment log that edits its own history stops
  being evidence.

**Where the lanes split, round 4, and how it was settled.** Sol called S3
a FIX; Kimi called it a PASS and stated that the snippet "exits non-zero".
Kimi listed every execution-dependent claim as UNVERIFIED in the same
reply, which is exactly what that claim was. The case was RUN: exit code 0
on both hosts, output `'|1'`. Sol is right and the finding is adopted. The
lane that could not run it did not get the benefit of the doubt, and the
lane that was right did not get it for being right - the run decided.

### Round 5, primary lane, 2026-07-29

At head `1d77f92`. T1, T5 PASS; T2, T3, T4, T6, T7 FIX.

- **A21 - THE PLAN WOULD HAVE ENDED RED AT ITS OWN LAST STEP (T6, T7).**
  The sharpest finding since A9, and the only one in this debate that was
  fatal to execution rather than to a claim. `test_backup_files_no_backslash_paths`
  (`evals/multi-model-verify/test_backup_lane.py:75`) asserts that
  `backup-lane.md`, the agent yaml and the system prompt contain NO
  backslash at all. A12's new sentence wrote git's escaped display form,
  backslashes included, straight into `backup-lane.md`. Task 7 Step 6 runs
  the full suite and states PASS; it would have been red, and the cause
  would have looked like an unrelated pre-existing test.
  The sentence is rewritten to describe the escaped form without writing
  one, and it says why in the file itself so a later editor does not
  re-add it. The pin is rewritten to match. Weakening the no-backslash
  test was considered and rejected: it guards against Windows path
  separators reaching a document that documents commands, which is worth
  more than one worked example.
- **A22 - the mojibake I introduced survived into the record (T2).** My
  own scripted edit had octal-collapsed `caf\303\251` into an accented
  literal inside A17's amendment text, so the record labelled a
  five-character string as eleven. Restored.
- **A23 - two historical records needed annotating, not rewriting (T2,
  T4).** A13's "corrected to eleven and four" is superseded by A17, and
  A9's "a file it can delete and hash" is the same overclaim A19 narrowed.
  Both annotated in place, matching the treatment A19 gave the octal
  sentence. The rule this cycle is settling on: an amendment log that
  edits its own history stops being evidence, so corrections are appended
  inside the entry they correct.
- **A24 - the spec claimed a stop for all three routes (T3).** Its "What
  the guard does NOT claim" paragraph said a syntactically fine name with
  no file behind it "is caught downstream, where `Get-ContentManifest`
  already stops". True only when the entry becomes a manifest SUBJECT.
  Deletion-only entries are omitted before that, and back-channel matches
  take the remediation path. Now stated as three routes with two of them
  unmeasured, matching A18 in the plan.
- **A25 - one more overbroad ground (T4).** `Get-BackChannelEntry`'s
  comment described the first ground as "a name it cannot resolve to a
  file", which is wider than "would risk the WRONG file". Narrowed.

### Round 5, backup lane, 2026-07-29

Same session resumed, route line verified (client-side), at head
`1d77f92`. **All seven claims PASS**, with two non-striking observations
and an explicit refusal to manufacture a finding: "Given this debate's
record, I state that plainly rather than manufacture one."

- **A26 - a loose antecedent (observation a).** The comment on
  `test_a_non_ascii_field_arrives_as_one_character_not_two_bytes` said the
  decoder "turned `caf\303\251` into character codes 195,169 - two
  characters". The two characters are the ESCAPE PAIR's output; the whole
  name decoded to five. Rewritten to say which is which. Taken because
  this cycle has now produced three separate defects inside comments about
  character counts, and a loose antecedent is how the next one starts.
- Its second observation, that A13's record lacked an A17 annotation, was
  already addressed by A23 in the same round from the other lane.
- Its T4 observation, the `Get-BackChannelEntry` ground-1 wording, was
  raised as a FIX by the primary lane and is A25. The backup lane called
  it "a misdescription in the safe direction" and did not strike it. Both
  readings are recorded; the narrowing was made.

**Where the lanes split, round 5, and it is the reason this debate is not
finished.** The backup lane passed T6 and T7 - "executable as written" and
"nothing left to end the final run red" - after checking every cited line
number, every definition-before-use ordering, and every pin's whitespace
normalization. It even verified the new status-command pin as correct. It
did not check whether the TEXT that pin quotes is allowed in the file it
goes into. The primary lane did, and found
`test_backup_files_no_backslash_paths` (A21), which would have turned the
plan's own last step red.

The lesson is not that one lane is better. It is that a pin can be
verified correct against the text it quotes and still be fatal, because
the constraint lived in a different test than the one being reasoned
about. Both lanes reasoned carefully about the same edit and only one
looked outward from it.

### Round 6, both lanes, 2026-07-29

At head `c1228cc`. Sol: U1, U2, U4, U5 PASS; U3 FIX. Kimi: all five PASS,
with one observation. **No execution defect was found by either lane.**

Both lanes swept U2 - every live test constraining every file the plan
edits - and both reported no new violation. Both independently found the
same thing while sweeping, which is worth recording on its own:

- **A27 - there are TWO whole-file backslash bans on `backup-lane.md`, not
  one.** `test_backup_files_no_backslash_paths` covers it as a backup-lane
  artifact; `test_no_backslash_paths_anywhere`
  (`evals/multi-model-verify/test_multi_model_verify.py:89`) covers it as a
  required reference file. A21's wording satisfies both, so this changes no
  verdict - but an editor who finds and satisfies only one is still
  exposed, and Task 7 now says so in the step itself.

Sol's U3, three wording defects, all adopted:

- **A28 - a universal claim survived in the code comment.** A24 fixed the
  spec's "a name with no file behind it is caught downstream" and left the
  same sentence in the guard's implementation comment. Only one of the
  three routes is a stop. Rewritten to name all three.
- **A29 - `Get-ManifestSubject`'s header contradicted its own body.** It
  said a caller "must BLOCK, never skip" immediately above a deliberate
  `continue` for deletion-only entries. Rewritten to distinguish the two
  DEFINED dispositions, omit and stop, from the third thing that must
  never happen: an entry passed over because the function could not make
  sense of it.
- **A30 - the parser error misdescribed the `>` case.** It reduced every
  render refusal to "a quoting trigger the baseline render cannot
  reproduce". `>` is NOT a quoting trigger; the sweep in this spec
  measured that directly. It is refused to keep the ` -> ` separator
  unambiguous. The message now names the guard's actual two grounds.

**Self-caught while applying A30.** Changing that message broke three of
the plan's own assertions, which pinned the old substring. Both messages
and all three assertions now share one stable phrase. This is the class
the lanes have caught four times - a message edited without its pins - and
it appeared inside the fix for it.

Kimi's observation, a one-line slack in a cited line range, was corrected
in the same pass.
