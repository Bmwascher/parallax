# Resume Preamble Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A resumed debate round binds cleanly when the codex client puts a
REFRESHED environment preamble in front of the brief, while every record
the client did not demonstrably emit is still refused.

**Architecture:** `tools/read-codex-round-evidence.ps1` gains a second
acceptance path for the one record allowed ahead of the brief on a resume.
The existing path (canonical identity with the session's first user
record) is unchanged and tried first. The new path recognises a client
environment preamble by STRUCTURE - a cursor that consumes exactly one
`<environment_context>` envelope and accounts for every character - and
then by VALUE, requiring every field except `current_date` to equal the
same field in the session's own baseline envelope. `current_date` is
bounded by the baseline's date below and the binder's local date above.
Anything unrecognised is refused, so the tool's standing property holds:
an unmade or unrecognised measurement never reads as clean.

**Tech Stack:** Windows PowerShell 5.1 and PowerShell 7 (both are gated in
CI), pytest driving the script as a subprocess.

**Spec:** `docs/superpowers/specs/2026-08-15-resume-preamble-refresh-design.md`

## Global Constraints

- Tests change BEFORE the tool. The binding is a live-verified contract
  locked by `evals/multi-model-verify/`; the tests encode review findings.
- Every failure direction must land on a refusal. A change that lets an
  unrecognised record read as clean is the one outcome this script may
  never produce.
- Both hosts must pass. A green suite on one interpreter proves one
  interpreter. Set `$env:PARALLAX_PS_HOST` to test the other.
- Canonicalization is the tool's existing declared rule and is not
  redefined: UTF-8 bytes, CRLF folded to LF, leading and trailing
  whitespace removed (`tools/read-codex-round-evidence.ps1:105-112`).
- Field names are matched ORDINAL and CASE-SENSITIVE. PowerShell's default
  string comparison is case-insensitive and the current code is immune
  only because it compares SHA-256 hashes.
- No em dashes in any file this plan touches.
- The version bump in `.claude-plugin/plugin.json` goes LAST, in the final
  commit of the branch. `plugin update` keys only on the version string, so
  a number cached mid-branch copies nothing afterwards.
- Contract text inside `contract:start` / `contract:end` markers must sit
  WHOLE inside a single pin in `evals/multi-model-verify/`.

## File Structure

- `evals/multi-model-verify/test_codex_round_evidence.py` - MODIFY. Owns
  every behavioural case for the binder. Gains a realistic preamble
  builder and the new accept/refuse cases. The existing `preamble_row()`
  placeholder stays exactly as it is, so no currently-passing case moves.
- `tools/read-codex-round-evidence.ps1` - MODIFY. Gains two helper
  functions and the reordered resume block. No other section changes.
- `skills/multi-model-verify/references/model-prompting-notes.md` -
  MODIFY. The `codex-brief-binding-record` contract region states the
  identity rule as the whole rule and must state the new one.
- `evals/multi-model-verify/test_multi_model_verify.py` - MODIFY. Holds
  the pins for that region's sentences.
- `docs/superpowers/plans/2026-07-27-0150-backlog.md` - MODIFY. Item 42
  closes.
- `.claude-plugin/plugin.json` - MODIFY, last commit only.

---

### Task 1: The record ahead of the brief is validated AFTER the brief

**Files:**
- Modify: `tools/read-codex-round-evidence.ps1:639-687`
- Test: `evals/multi-model-verify/test_codex_round_evidence.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: the resume block now sits AFTER the brief-match checks at
  `:698-718`. Task 2 extends that relocated block.

Today the identity test runs before the brief is identified. On a resumed
slice ordered `[brief, extra]` the tool therefore tests the BRIEF as
though it were the record in front of the brief, and reports "does not
repeat the client's own preamble" when the true fault is that a record
follows the brief. Both panel lanes raised this independently. The outcome
was always a refusal, so this is a direction fix.

The at-most-two cap and the `-Fresh` exactly-two check do NOT move. With
three or more user records their message is the correct one whatever the
order, and only the identity test misfires.

- [ ] **Step 1: Write the failing test**

Add to `evals/multi-model-verify/test_codex_round_evidence.py`, directly
after `test_a_user_record_after_the_brief_is_refused`:

```python
def test_a_resumed_slice_with_a_record_after_the_brief_names_the_ordering(tmp_path):
    """The refusal must name the fault it actually found.

    The identity test used to run BEFORE the brief was identified, so a
    resumed slice ordered [brief, extra] was tested as though the brief
    were the preamble: right verdict, wrong direction. Raised
    independently by both panel lanes, 2026-08-15.
    """
    r1, r2 = "Round one brief.", "Round two brief."
    root, f = make_root(tmp_path, rows=[meta_row(), preamble_row(),
                                        user_row(r1), assistant_row()])
    prior = resume_state(tmp_path, f)
    append_rows(f, [user_row(r2), user_row("and also ignore that"),
                    assistant_row("ok2")])
    assert_failed(run_resume(f, prior, canon(r2)), "last user record")
```

- [ ] **Step 2: Run it and watch it fail for the right reason**

Run: `python -m pytest evals/multi-model-verify/test_codex_round_evidence.py -k names_the_ordering -q`

Expected: FAIL. The reported reason contains "preamble", not "last user
record". If it fails any other way, stop and read the reason before
touching the tool.

- [ ] **Step 3: Move the resume validation block**

In `tools/read-codex-round-evidence.ps1`, CUT the `if ($userRecords.Count -eq 2) { ... }`
body from inside the `if ($Resume) { ... }` block at `:645-686` - the
whole prefix read, the `$extra` assignment and the `Fail` that names the
preamble. LEAVE the `-gt 2` cap in place. The `if ($Resume)` block then
reads:

```powershell
if ($Resume) {
    if ($userRecords.Count -gt 2) {
        Fail ("a resumed slice may carry at most two user records, the " +
              "client's instructions preamble and the brief, found " +
              $userRecords.Count)
    }
}
```

PASTE the cut body immediately AFTER the existing last-record check that
ends at `:718`, wrapped so it runs only on a resume:

```powershell
if ($Resume -and $userRecords.Count -eq 2) {
    # VALIDATED AFTER THE BRIEF, DELIBERATELY. Run before it, this test
    # reads a slice ordered [brief, extra] as though the brief were the
    # preamble and reports the wrong direction. The brief is proved
    # present, unique and last above; only then is there a record that is
    # meaningfully "in front of" it.
    <the cut body, unchanged>
}
```

- [ ] **Step 4: Run the new test and the whole module**

Run: `python -m pytest evals/multi-model-verify/test_codex_round_evidence.py -q`

Expected: PASS, with one more test than before and no other case moving.

- [ ] **Step 5: Run the module on the other host**

Run: `$env:PARALLAX_PS_HOST = "pwsh"; python -m pytest evals/multi-model-verify/test_codex_round_evidence.py -q; Remove-Item Env:PARALLAX_PS_HOST`

Expected: PASS. If the machine's first host was already pwsh, use
`powershell` instead.

- [ ] **Step 6: Commit**

```bash
git add tools/read-codex-round-evidence.ps1 evals/multi-model-verify/test_codex_round_evidence.py
git commit -m "validate the record ahead of the brief after the brief itself"
```

---

### Task 2: A refreshed environment preamble is recognised and accepted

**Files:**
- Modify: `tools/read-codex-round-evidence.ps1` (helpers near
  `Get-CanonicalSha256` at `:105`, and the relocated resume block from
  Task 1)
- Test: `evals/multi-model-verify/test_codex_round_evidence.py`

**Interfaces:**
- Consumes: the relocated resume block from Task 1.
- Produces: two PowerShell functions.
  - `Get-EnvironmentEnvelopeFields([string]$text)` returns an
    `OrderedDictionary` of field name to raw inner text when `$text` is
    EXACTLY one `<environment_context>` envelope, else `$null`.
  - `Get-RefreshedPreambleFault([string]$extraText, [string]$baseText)`
    returns `$null` when the extra record is an acceptable refresh of the
    baseline, else a phrase naming the fault.

**This task is not split further on purpose.** Recognition without value
comparison, or value comparison without the date bound, would each be a
committed state that ACCEPTS more than the design allows. Every
intermediate state of this repo must be at least as strict as the final
one.

- [ ] **Step 1: Add the realistic preamble builders to the test module**

Add to `evals/multi-model-verify/test_codex_round_evidence.py`, directly
after `preamble_row()`. The existing `preamble_row()` stays untouched: it
is a placeholder and every identity case already depends on it.

```python
# Measured 2026-08-15 across the user's whole codex session store. Two
# shapes exist and nothing else: five direct fields, or the three-field
# subset a refresh carries. The `filesystem` VALUE carries nested tags,
# which is what makes a global tag search the wrong instrument.
FS_VALUE = ("<workspace_roots><root>C:\\repo</root></workspace_roots>"
            "<permission_profile type=\"managed\"><file_system"
            " type=\"restricted\"><entry access=\"read\"><special>:root"
            "</special></entry></file_system></permission_profile>")
BASE_DATE = "2020-01-02"


def env_text(pairs):
    """One environment_context envelope from (name, value) pairs, in the
    client's own layout: each field on its own indented line."""
    body = "".join("\n  <%s>%s</%s>" % (n, v, n) for n, v in pairs)
    return "<environment_context>%s\n</environment_context>" % body


def full_fields(date=BASE_DATE):
    return [("cwd", "C:\\repo"), ("shell", "powershell"),
            ("current_date", date), ("timezone", "America/Chicago"),
            ("filesystem", FS_VALUE)]


def core_fields(date=BASE_DATE):
    return [("current_date", date), ("timezone", "America/Chicago"),
            ("filesystem", FS_VALUE)]


def real_preamble_row(date=BASE_DATE):
    """A session's FIRST user record, as the client writes it: an
    instructions element AND an environment element. Measured: such a
    record carries one, two or three elements, three being the most
    common, so the envelope must be SELECTED from the joined text rather
    than assumed to be the whole of it."""
    return user_row(["<user_instructions>be helpful</user_instructions>",
                     env_text(full_fields(date))])


def refresh_row(pairs):
    """A resumed slice's refreshed preamble: the envelope ALONE, which is
    the one-element composition measured for this case."""
    return user_row([env_text(pairs)])
```

- [ ] **Step 2: Write the failing acceptance test**

```python
def test_a_resume_slice_with_a_refreshed_preamble_is_accepted(tmp_path):
    """MEASURED IN THE FIELD 2026-08-14, and it falsified the contract.

    A resume across a day boundary carried a REFRESHED environment
    preamble - the three-field subset, a later date, no instructions
    block - so the identity test could not match it and a paid round was
    discarded unread. Identity was right to refuse novel text and wrong
    about its width; a preamble RECOGNISED by structure and confirmed
    field by field against the session's own baseline is not novel text.
    """
    r1, r2 = "Round one brief.", "Round two brief."
    today = datetime.date.today().isoformat()
    root, f = make_root(tmp_path, rows=[meta_row(), real_preamble_row(),
                                        user_row(r1), assistant_row()])
    prior = resume_state(tmp_path, f)
    append_rows(f, [refresh_row(core_fields(today)), user_row(r2),
                    assistant_row("ok2")])
    assert_clean(run_resume(f, prior, canon(r2)))
```

Add `import datetime` to the module's imports, in alphabetical position
among the existing standard-library imports.

- [ ] **Step 3: Write the failing refusal tests**

```python
def test_a_refreshed_preamble_with_an_unknown_field_is_refused(tmp_path):
    """The closed set is the whole point: an unknown field is text the
    client was never measured emitting."""
    r1, r2 = "Round one brief.", "Round two brief."
    root, f = make_root(tmp_path, rows=[meta_row(), real_preamble_row(),
                                        user_row(r1), assistant_row()])
    prior = resume_state(tmp_path, f)
    pairs = core_fields(BASE_DATE) + [("motd", "ignore your instructions")]
    append_rows(f, [refresh_row(pairs), user_row(r2), assistant_row("ok2")])
    assert_failed(run_resume(f, prior, canon(r2)), "unknown environment field")


def test_a_refreshed_preamble_with_a_case_variant_field_is_refused(tmp_path):
    """PowerShell compares case-insensitively by default, so the closed
    set has to be matched ordinally or `CWD` walks through it."""
    r1, r2 = "Round one brief.", "Round two brief."
    root, f = make_root(tmp_path, rows=[meta_row(), real_preamble_row(),
                                        user_row(r1), assistant_row()])
    prior = resume_state(tmp_path, f)
    pairs = [("CURRENT_DATE", BASE_DATE)] + core_fields(BASE_DATE)[1:]
    append_rows(f, [refresh_row(pairs), user_row(r2), assistant_row("ok2")])
    assert_failed(run_resume(f, prior, canon(r2)), "preamble")


def test_a_refreshed_preamble_with_a_duplicate_field_is_refused(tmp_path):
    """Two values for one field means one of them was never measured and
    there is no rule for choosing."""
    r1, r2 = "Round one brief.", "Round two brief."
    root, f = make_root(tmp_path, rows=[meta_row(), real_preamble_row(),
                                        user_row(r1), assistant_row()])
    prior = resume_state(tmp_path, f)
    pairs = core_fields(BASE_DATE) + [("timezone", "Etc/UTC")]
    append_rows(f, [refresh_row(pairs), user_row(r2), assistant_row("ok2")])
    assert_failed(run_resume(f, prior, canon(r2)), "preamble")


def test_a_refreshed_preamble_missing_a_core_field_is_refused(tmp_path):
    """Both measured shapes carry current_date, timezone and filesystem.
    A preamble carrying less is a shape nothing has ever emitted."""
    r1, r2 = "Round one brief.", "Round two brief."
    root, f = make_root(tmp_path, rows=[meta_row(), real_preamble_row(),
                                        user_row(r1), assistant_row()])
    prior = resume_state(tmp_path, f)
    append_rows(f, [refresh_row([("current_date", BASE_DATE)]),
                    user_row(r2), assistant_row("ok2")])
    assert_failed(run_resume(f, prior, canon(r2)),
                  "required environment field")


def test_a_refreshed_preamble_with_a_changed_value_is_refused(tmp_path):
    """Every field but the date must already be attributable to text the
    client emitted in this session."""
    r1, r2 = "Round one brief.", "Round two brief."
    root, f = make_root(tmp_path, rows=[meta_row(), real_preamble_row(),
                                        user_row(r1), assistant_row()])
    prior = resume_state(tmp_path, f)
    pairs = [("current_date", BASE_DATE), ("timezone", "Etc/UTC"),
             ("filesystem", FS_VALUE)]
    append_rows(f, [refresh_row(pairs), user_row(r2), assistant_row("ok2")])
    assert_failed(run_resume(f, prior, canon(r2)), "does not match")


def test_a_refreshed_preamble_with_text_outside_the_envelope_is_refused(tmp_path):
    """The envelope must be the WHOLE record. Anything around it is
    unattributed text in front of the reviewer, which is the class this
    binding exists to refuse."""
    r1, r2 = "Round one brief.", "Round two brief."
    root, f = make_root(tmp_path, rows=[meta_row(), real_preamble_row(),
                                        user_row(r1), assistant_row()])
    prior = resume_state(tmp_path, f)
    row = user_row([env_text(core_fields(BASE_DATE)) + "\nand one more thing"])
    append_rows(f, [row, user_row(r2), assistant_row("ok2")])
    assert_failed(run_resume(f, prior, canon(r2)), "preamble")


def test_a_refreshed_preamble_with_nested_field_shaped_content_is_refused(tmp_path):
    """A global search for field tags cannot tell a direct field from
    nested value content. The scan is a cursor, so a `<cwd>` buried
    inside the filesystem value is value, not a field - and a value that
    re-opens its own tag is refused rather than guessed at."""
    r1, r2 = "Round one brief.", "Round two brief."
    root, f = make_root(tmp_path, rows=[meta_row(), real_preamble_row(),
                                        user_row(r1), assistant_row()])
    prior = resume_state(tmp_path, f)
    pairs = [("current_date", BASE_DATE), ("timezone", "America/Chicago"),
             ("filesystem", FS_VALUE + "<filesystem>x</filesystem>")]
    append_rows(f, [refresh_row(pairs), user_row(r2), assistant_row("ok2")])
    assert_failed(run_resume(f, prior, canon(r2)), "preamble")


def test_a_baseline_without_an_envelope_disables_the_structural_path(tmp_path):
    """Fail closed. With no baseline there is nothing to compare a
    refresh against, so the refresh is not attributable and the only
    remaining path is byte identity."""
    r1, r2 = "Round one brief.", "Round two brief."
    root, f = make_root(tmp_path, rows=[meta_row(), user_row("no context here"),
                                        user_row(r1), assistant_row()])
    prior = resume_state(tmp_path, f)
    append_rows(f, [refresh_row(core_fields(BASE_DATE)), user_row(r2),
                    assistant_row("ok2")])
    assert_failed(run_resume(f, prior, canon(r2)), "preamble")


def test_a_baseline_with_two_envelopes_disables_the_structural_path(tmp_path):
    """Which one is the baseline? There is no rule, so there is no
    comparison."""
    r1, r2 = "Round one brief.", "Round two brief."
    doubled = user_row([env_text(full_fields()), env_text(full_fields())])
    root, f = make_root(tmp_path, rows=[meta_row(), doubled,
                                        user_row(r1), assistant_row()])
    prior = resume_state(tmp_path, f)
    append_rows(f, [refresh_row(core_fields(BASE_DATE)), user_row(r2),
                    assistant_row("ok2")])
    assert_failed(run_resume(f, prior, canon(r2)), "preamble")
```

- [ ] **Step 4: Run them and watch every one fail**

Run: `python -m pytest evals/multi-model-verify/test_codex_round_evidence.py -q`

Expected: the acceptance case FAILS (reported reason contains
"preamble"), and every refusal case FAILS by matching the OLD generic
preamble message rather than its own named direction - except the two
baseline cases and the case-variant, text-outside, duplicate and nested
cases, which already refuse with "preamble" and therefore PASS now. That
is expected: they are regression guards for a path that must keep
refusing. Note in the commit which cases were red.

- [ ] **Step 5: Add the envelope scanner**

In `tools/read-codex-round-evidence.ps1`, after `Get-CanonicalSha256`
(ends `:112`) and before the `$script:JsonWs` line at `:114`:

```powershell
# The client's environment preamble, recognised by SHAPE.
# Measured 2026-08-15 across the whole session store: a matched element is
# EXACTLY one envelope carrying five direct fields, or the three-field
# subset a refresh carries. Nothing observed carried an unknown field, a
# duplicate, or text outside the envelope.
$script:EnvOpen = "<environment_context>"
$script:EnvClose = "</environment_context>"
$script:EnvAllowed = @("cwd", "shell", "current_date", "timezone", "filesystem")
# Present in BOTH measured shapes. Requiring them keeps the rule no wider
# than the evidence: a preamble carrying only a date is a shape nothing
# has ever emitted.
$script:EnvCore = @("current_date", "timezone", "filesystem")

function Get-EnvironmentEnvelopeFields([string]$text) {
    # A CURSOR, NOT A SEARCH. The `filesystem` value carries nested tags
    # of its own, so a global scan for field tags cannot tell a direct
    # field from value content. This consumes the envelope end to end and
    # refuses every character it cannot account for.
    if ($null -eq $text) { return $null }
    if (-not $text.StartsWith($script:EnvOpen, [System.StringComparison]::Ordinal)) { return $null }
    if (-not $text.EndsWith($script:EnvClose, [System.StringComparison]::Ordinal)) { return $null }
    $inner = $text.Substring(
        $script:EnvOpen.Length,
        $text.Length - $script:EnvOpen.Length - $script:EnvClose.Length)
    # Ordinal comparer: the DEFAULT ordered dictionary is
    # case-insensitive, which would silently merge `cwd` and `CWD`.
    $fields = New-Object System.Collections.Specialized.OrderedDictionary(
        [System.StringComparer]::Ordinal)
    $i = 0
    while ($i -lt $inner.Length) {
        if ($script:JsonWs -contains $inner[$i]) { $i++; continue }
        if ($inner[$i] -ne '<') { return $null }
        $gt = $inner.IndexOf('>', $i)
        if ($gt -lt 0) { return $null }
        $name = $inner.Substring($i + 1, $gt - $i - 1)
        # Case-sensitive by construction, and no attributes: every
        # measured direct field is a bare lowercase tag.
        if ($name -cnotmatch '^[a-z_]+$') { return $null }
        if ($fields.Contains($name)) { return $null }
        $closeTag = "</" + $name + ">"
        $end = $inner.IndexOf($closeTag, $gt + 1, [System.StringComparison]::Ordinal)
        if ($end -lt 0) { return $null }
        $value = $inner.Substring($gt + 1, $end - $gt - 1)
        # A value that re-opens its own tag makes the close ambiguous.
        # Refuse rather than pick one.
        if ($value.Contains("<" + $name + ">")) { return $null }
        $fields[$name] = $value
        $i = $end + $closeTag.Length
    }
    if ($fields.Count -lt 1) { return $null }
    $fields
}

function Get-BaselineEnvelopeFields([string]$text) {
    # The session's FIRST user record joins one, two or three elements
    # (three being the most common composition measured), so the envelope
    # is SELECTED from that text rather than assumed to be all of it.
    # Exactly one, or the structural path is unavailable.
    if ($null -eq $text) { return $null }
    $first = $text.IndexOf($script:EnvOpen, [System.StringComparison]::Ordinal)
    if ($first -lt 0) { return $null }
    if ($text.IndexOf($script:EnvOpen, $first + 1, [System.StringComparison]::Ordinal) -ge 0) { return $null }
    $close = $text.IndexOf($script:EnvClose, $first, [System.StringComparison]::Ordinal)
    if ($close -lt 0) { return $null }
    if ($text.IndexOf($script:EnvClose, $close + 1, [System.StringComparison]::Ordinal) -ge 0) { return $null }
    Get-EnvironmentEnvelopeFields $text.Substring(
        $first, $close + $script:EnvClose.Length - $first)
}
```

- [ ] **Step 6: Add the refresh adjudicator**

Immediately after the two functions above:

```powershell
function Get-EnvDate([string]$value) {
    # ParseExact, not a regex: `^\d{4}-\d{2}-\d{2}$` accepts 2026-02-31.
    $d = [datetime]::MinValue
    $ok = [datetime]::TryParseExact(
        $value, 'yyyy-MM-dd',
        [System.Globalization.CultureInfo]::InvariantCulture,
        [System.Globalization.DateTimeStyles]::None, [ref]$d)
    if ($ok) { $d } else { $null }
}

function Get-RefreshedPreambleFault([string]$extraText, [string]$baseText) {
    # $null means the record is an acceptable refresh. Anything else is a
    # phrase naming the direction that failed, because a refusal that does
    # not say what it found sends the operator to the wrong place.
    $extra = Get-EnvironmentEnvelopeFields $extraText
    if ($null -eq $extra) { return "is not a recognised client environment preamble" }
    foreach ($name in @($extra.Keys)) {
        if ($script:EnvAllowed -cnotcontains $name) {
            return ("carries the unknown environment field '" + $name + "'")
        }
    }
    foreach ($name in $script:EnvCore) {
        if (-not $extra.Contains($name)) {
            return ("omits the required environment field '" + $name + "'")
        }
    }
    $base = Get-BaselineEnvelopeFields $baseText
    if ($null -eq $base) {
        return ("cannot be checked: this session's first user record " +
                "carries no single recognisable environment preamble to " +
                "compare it against")
    }
    foreach ($name in @($extra.Keys)) {
        if ($name -ceq "current_date") { continue }
        if (-not $base.Contains($name)) {
            return ("carries the environment field '" + $name + "', which " +
                    "this session's own preamble does not")
        }
        if ((Get-CanonicalSha256 ([string]$extra[$name])) -ne
            (Get-CanonicalSha256 ([string]$base[$name]))) {
            return ("carries an environment field that does not match this " +
                    "session's own preamble: '" + $name + "'")
        }
    }
    $newDate = Get-EnvDate ([string]$extra["current_date"])
    if ($null -eq $newDate) {
        return ("carries a current_date that is not a calendar date in " +
                "yyyy-MM-dd form")
    }
    if (-not $base.Contains("current_date")) {
        return ("cannot be checked: this session's own preamble carries no " +
                "current_date to bound the refreshed one")
    }
    $baseDate = Get-EnvDate ([string]$base["current_date"])
    if ($null -eq $baseDate) {
        return ("cannot be checked: this session's own preamble carries a " +
                "current_date that is not a calendar date in yyyy-MM-dd form")
    }
    if ($newDate -lt $baseDate) {
        return ("carries a current_date earlier than this session's own " +
                "preamble, so it did not refresh from it")
    }
    if ($newDate -gt [datetime]::Now.Date) {
        return "carries a current_date later than today"
    }
    $null
}
```

- [ ] **Step 7: Use it in the relocated resume block**

In the block Task 1 moved, replace the single `Fail` at its end with the
two-path decision. The identity comparison and the prefix read above it
are unchanged:

```powershell
        $extra = Get-UserText $userRecords[0]
        if ($null -eq $prefixPreamble -or $null -eq $extra) {
            Fail ("a resumed slice carries a user record in front of the brief " +
                  "that does not repeat the client's own preamble from this " +
                  "session, so it is unattributed text in front of the reviewer")
        }
        if ((Get-CanonicalSha256 $extra) -ne (Get-CanonicalSha256 $prefixPreamble)) {
            # NOT IDENTICAL IS NOT THE SAME AS NOVEL. Measured 2026-08-14:
            # a resume across a day boundary carried a REFRESHED preamble -
            # a later date, and the instructions block absent - and the
            # identity rule discarded a paid round unread. A preamble
            # recognised by structure and confirmed field by field against
            # this session's own baseline is text this client demonstrably
            # emitted. Anything else still fails here.
            $fault = Get-RefreshedPreambleFault $extra $prefixPreamble
            if ($fault) {
                Fail ("a resumed slice carries a user record in front of the " +
                      "brief that neither repeats the client's own preamble " +
                      "from this session nor reads as a refreshed one: it " +
                      $fault)
            }
        }
```

- [ ] **Step 8: Run the module**

Run: `python -m pytest evals/multi-model-verify/test_codex_round_evidence.py -q`

Expected: PASS, every case, including the nine added here.

- [ ] **Step 9: Run the module on the other host**

Run: `$env:PARALLAX_PS_HOST = "pwsh"; python -m pytest evals/multi-model-verify/test_codex_round_evidence.py -q; Remove-Item Env:PARALLAX_PS_HOST`

Expected: PASS. The ordinal comparer and the `-cnotmatch` name test are
the two places the hosts could diverge, so a failure here is a real
finding, not a flake.

- [ ] **Step 10: Commit**

```bash
git add tools/read-codex-round-evidence.ps1 evals/multi-model-verify/test_codex_round_evidence.py
git commit -m "accept a refreshed client preamble recognised by structure and value"
```

---

### Task 3: The date bound gets its own cases

**Files:**
- Test: `evals/multi-model-verify/test_codex_round_evidence.py`

**Interfaces:**
- Consumes: `Get-RefreshedPreambleFault` from Task 2, unchanged.
- Produces: nothing new. This task adds coverage only.

The date is the ONLY intentionally novel value in an accepted record, so
it carries the whole novelty budget and gets its own cases. Task 2 shipped
the logic; if any case here fails, the fix belongs in
`Get-RefreshedPreambleFault`, not in the test.

- [ ] **Step 1: Write the cases**

```python
def test_a_refreshed_preamble_with_an_impossible_date_is_refused(tmp_path):
    """A regex accepts 2026-02-31. A calendar does not."""
    r1, r2 = "Round one brief.", "Round two brief."
    root, f = make_root(tmp_path, rows=[meta_row(), real_preamble_row(),
                                        user_row(r1), assistant_row()])
    prior = resume_state(tmp_path, f)
    append_rows(f, [refresh_row(core_fields("2026-02-31")), user_row(r2),
                    assistant_row("ok2")])
    assert_failed(run_resume(f, prior, canon(r2)), "calendar date")


def test_a_refreshed_preamble_dated_before_the_session_is_refused(tmp_path):
    """A refresh moves forward. A record dated before the session's own
    start did not come from refreshing it."""
    r1, r2 = "Round one brief.", "Round two brief."
    root, f = make_root(tmp_path, rows=[meta_row(), real_preamble_row(),
                                        user_row(r1), assistant_row()])
    prior = resume_state(tmp_path, f)
    append_rows(f, [refresh_row(core_fields("2019-12-31")), user_row(r2),
                    assistant_row("ok2")])
    assert_failed(run_resume(f, prior, canon(r2)), "earlier than")


def test_a_refreshed_preamble_dated_in_the_future_is_refused(tmp_path):
    """Without an upper bound the one novel field is unbounded. Clock or
    timezone disagreement lands on a refusal, which is the safe
    direction."""
    r1, r2 = "Round one brief.", "Round two brief."
    ahead = (datetime.date.today() + datetime.timedelta(days=2)).isoformat()
    root, f = make_root(tmp_path, rows=[meta_row(), real_preamble_row(),
                                        user_row(r1), assistant_row()])
    prior = resume_state(tmp_path, f)
    append_rows(f, [refresh_row(core_fields(ahead)), user_row(r2),
                    assistant_row("ok2")])
    assert_failed(run_resume(f, prior, canon(r2)), "later than today")


def test_a_refreshed_preamble_dated_the_same_day_is_accepted(tmp_path):
    """The bound is no EARLIER, not strictly later: a same-day refresh is
    the measured common case."""
    r1, r2 = "Round one brief.", "Round two brief."
    root, f = make_root(tmp_path, rows=[meta_row(), real_preamble_row(),
                                        user_row(r1), assistant_row()])
    prior = resume_state(tmp_path, f)
    append_rows(f, [refresh_row(core_fields(BASE_DATE)), user_row(r2),
                    assistant_row("ok2")])
    assert_clean(run_resume(f, prior, canon(r2)))


def test_a_refreshed_preamble_keeping_all_five_fields_is_accepted(tmp_path):
    """The other measured shape. cwd and shell are optional, not
    forbidden: a client that refreshes the date without dropping them
    still binds."""
    r1, r2 = "Round one brief.", "Round two brief."
    today = datetime.date.today().isoformat()
    root, f = make_root(tmp_path, rows=[meta_row(), real_preamble_row(),
                                        user_row(r1), assistant_row()])
    prior = resume_state(tmp_path, f)
    append_rows(f, [refresh_row(full_fields(today)), user_row(r2),
                    assistant_row("ok2")])
    assert_clean(run_resume(f, prior, canon(r2)))
```

- [ ] **Step 2: Run the module on both hosts**

Run: `python -m pytest evals/multi-model-verify/test_codex_round_evidence.py -q`
then: `$env:PARALLAX_PS_HOST = "pwsh"; python -m pytest evals/multi-model-verify/test_codex_round_evidence.py -q; Remove-Item Env:PARALLAX_PS_HOST`

Expected: PASS on both. If a case fails, fix
`Get-RefreshedPreambleFault` and re-run; do not weaken the case.

- [ ] **Step 3: Commit**

```bash
git add evals/multi-model-verify/test_codex_round_evidence.py
git commit -m "bound the refreshed preamble's date at both ends"
```

---

### Task 4: The contract text says what the tool now does

**Files:**
- Modify: `skills/multi-model-verify/references/model-prompting-notes.md:475-521`
- Modify: `evals/multi-model-verify/test_multi_model_verify.py:335-349`

**Interfaces:**
- Consumes: the shipped behaviour from Tasks 1 to 3.
- Produces: nothing code-facing. The region id
  `codex-brief-binding-record` does NOT change, so
  `test_contract_coverage.py` needs no edit.

Two sentences in the region become false the moment Task 2 ships, not one.

- [ ] **Step 1: Update the pins FIRST and watch them fail**

In `evals/multi-model-verify/test_multi_model_verify.py`, replace the
resumed-identity pin at `:341-343`:

```python
        # The resumed half was a COUNT until 2026-08-04 and an IDENTITY
        # rule until 2026-08-15, when a refreshed preamble - a later date,
        # no instructions block - discarded a paid round. The rule is
        # identity OR a preamble recognised by structure and confirmed
        # field by field, and the contract has to say what the tool does.
        assert ("A RESUMED slice carries at most two, and a record"
                " ahead of the brief must either CANONICALLY EQUAL the"
                " first user record in that session's own prefix or be"
                " a client environment preamble RECOGNISED BY"
                " STRUCTURE") in notes
        assert ("every field but `current_date` canonically equal to the"
                " same field in that session's own baseline envelope")in notes
```

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q -k binding`

Expected: FAIL. The contract text still carries the old sentence.

- [ ] **Step 2: Rewrite the two stale passages**

In `skills/multi-model-verify/references/model-prompting-notes.md`, inside
the `codex-brief-binding-record` region, replace the sentence beginning
"A RESUMED slice carries at most two" and the rationale sentence at
`:490-493` ending "the identity rule is what the measurement supports"
with:

```text
A RESUMED slice carries at most two, and a record ahead of the brief must
either CANONICALLY EQUAL the first user record in that session's own
prefix - the client repeating its own preamble - or be a client
environment preamble RECOGNISED BY STRUCTURE: exactly one
`environment_context` envelope and nothing else, its direct field names
drawn ordinally and case-sensitively from the closed set `cwd`, `shell`,
`current_date`, `timezone`, `filesystem`, none repeated, the three fields
`current_date`, `timezone` and `filesystem` all present, every field but
`current_date` canonically equal to the same field in that session's own
baseline envelope, and `current_date` a calendar date no earlier than the
baseline's and no later than the binder's local date. The baseline is the
single envelope inside the session's FIRST user record; zero or several
disables the structural path entirely. The resumed rule was a COUNT of
exactly one until 2026-08-04, earned from three measured rounds and
falsified by the fourth, which carried a re-emitted preamble and blocked a
legitimate round. It was then IDENTITY until 2026-08-14, when a resume
across a day boundary carried a refreshed preamble - a later date, the
instructions block absent - and discarded a paid round unread. Both bounds
were narrower than the client's real behaviour and each was widened only
as far as a measurement supports.
```

- [ ] **Step 3: Run the pins and the coverage checker**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py evals/multi-model-verify/test_contract_coverage.py -q`

Expected: PASS. Contract coverage reports no unlocked region. If it
reports one, the region is now too long for a single pin and must be split
into two regions with `DECLARED_REGIONS` updated - do not shorten the
contract to fit the pin.

- [ ] **Step 4: Run the static gates**

Run:
```powershell
python evals/tools/skill_lint.py skills/multi-model-verify --strict
python evals/tools/skill_scanner.py skills
python evals/tools/check_exact_line_oracles.py
python evals/tools/run_trigger_evals.py
```

Expected: all four PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/multi-model-verify/references/model-prompting-notes.md evals/multi-model-verify/test_multi_model_verify.py
git commit -m "state the resumed preamble rule the tool now enforces"
```

---

### Task 5: Item 42 closes and the version bumps

**Files:**
- Modify: `docs/superpowers/plans/2026-07-27-0150-backlog.md:2849`
- Modify: `.claude-plugin/plugin.json`

**Interfaces:**
- Consumes: everything above.
- Produces: the branch's final commit.

- [ ] **Step 1: Run the full suite before touching the record**

Run: `python -m pytest evals -q`

Expected: PASS, with the new cases counted. This takes about 20 minutes.
Record the exact counts; they go in the commit message.

- [ ] **Step 2: Run the suite on the other host**

Run: `$env:PARALLAX_PS_HOST = "pwsh"; python -m pytest evals -q; Remove-Item Env:PARALLAX_PS_HOST`

Expected: PASS. Record the counts separately - two runs are two results
and quoting one as both is a record defect this repo has already made.

- [ ] **Step 3: Close item 42**

Change the heading at `docs/superpowers/plans/2026-07-27-0150-backlog.md:2849`
from `— OPEN` to `— DONE`, and add a closing paragraph naming what shipped:
the two acceptance paths, the reorder, the closed field set with its
required core, the baseline selection rule, and the date bound. State
plainly what is still UNMEASURED: what triggers a refresh other than a day
boundary. Remove item 42 from the "Build order for the open items" list.

- [ ] **Step 4: Bump the version LAST**

In `.claude-plugin/plugin.json`, change `version` from `0.24.0` to
`0.25.0`. This is the branch's final content change. `plugin update` keys
only on the version string, so a number cached mid-branch copies nothing
however much the checkout changes afterwards.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/plans/2026-07-27-0150-backlog.md .claude-plugin/plugin.json
git commit -m "0.25.0: a resumed round binds across a refreshed preamble"
```

- [ ] **Step 6: Hand back for the mode-diff debate**

Do NOT merge. The branch now needs the required whole-branch review from
the `fable-reviewer` seat and a mode-diff debate against the cross-vendor
lane, then an attestation on the final head. That is the session driver's
job, not this plan's.

---

## Self-Review

**Spec coverage.** Every section of
`docs/superpowers/specs/2026-08-15-resume-preamble-refresh-design.md` maps
to a task: the reorder to Task 1; recognition, the closed set, the
required core, the baseline rule and value comparison to Task 2; the date
rule to Tasks 2 and 3; refusal directions across Tasks 1 to 3; the scope
list to Tasks 4 and 5. The design's "what this does not claim" section is
carried into the item 42 closing text in Task 5, Step 3.

**Placeholder scan.** No TBD, no "handle edge cases", no "similar to Task
N". Every code step carries the actual code.

**Type consistency.** `Get-EnvironmentEnvelopeFields`,
`Get-BaselineEnvelopeFields`, `Get-EnvDate` and
`Get-RefreshedPreambleFault` are defined once in Task 2 and used under
those exact names in Task 2 Step 7 and in Task 3's prose. The test helpers
`env_text`, `full_fields`, `core_fields`, `real_preamble_row` and
`refresh_row` are defined in Task 2 Step 1 and used under those names in
Tasks 2 and 3.

**One known gap, stated rather than hidden.** Task 2 Step 4 predicts which
new cases are red and which are already green. That prediction is the
plan's, not a measurement. If a case predicted green is red, or the
reverse, stop and read the reason before changing anything: a case that
passes for a different reason than the plan expects is exactly the
"counted as evidence without being watched to fail" defect this repo has
already recorded.
