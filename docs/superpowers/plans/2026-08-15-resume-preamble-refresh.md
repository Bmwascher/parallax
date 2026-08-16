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

**Revised 2026-08-15 after plan-debate round 2 BLOCKED the first draft.**
Ten findings, every one verified against the repo and accepted. The two
that would have failed the build: rewriting the contract region breaks a
WHOLE-REGION pin the first draft never mentioned, and the scanner was fed
raw record text while the spec defines recognition over canonical text, so
a valid refresh with a trailing newline would have been refused. The task
count dropped from five to three because two of the findings were about
commit atomicity, not about content.

## Global Constraints

- Tests change BEFORE the tool, in the same task and the same commit. The
  binding is a live-verified contract locked by `evals/multi-model-verify/`.
- The contract text and the tool change in the SAME commit. A commit where
  the pinned contract says identity-only while the tool accepts a
  structural refresh is a commit whose record contradicts its code.
- Every failure direction must land on a refusal, and each refusal must
  name the direction it actually found. A refusal that reports the wrong
  direction sends the operator to the wrong place; a test that asserts
  only a generic phrase can pass for the wrong reason.
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
- **If any step's actual result differs from its stated expected result,
  STOP and report. Do not adapt, do not invent a workaround, do not
  proceed to the next step.** A step whose prediction is wrong is a
  finding about this plan.

## File Structure

- `evals/multi-model-verify/test_codex_round_evidence.py` - MODIFY. Owns
  every behavioural case for the binder. Gains a realistic preamble
  builder and the new accept/refuse cases. The existing `preamble_row()`
  placeholder stays exactly as it is, so no currently-passing case moves.
- `tools/read-codex-round-evidence.ps1` - MODIFY. Gains SIX helper
  functions and the reordered resume block. No other section changes.
- `skills/multi-model-verify/references/model-prompting-notes.md` -
  MODIFY. The `codex-brief-binding-record` contract region states the
  identity rule as the whole rule and must state the new one.
- `evals/multi-model-verify/test_multi_model_verify.py` - MODIFY. Holds
  BOTH the clause pins for that region and the whole-region pin.
- `docs/superpowers/plans/2026-07-27-0150-backlog.md` - MODIFY. Item 42
  closes and leaves the ranked build order.
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

This task stays separate from Task 2 because it is a behaviour-preserving
reorder: every input refused before is refused after, and only the message
changes. Task 2's gate then builds on the corrected order.

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

Expected: FAIL, and the reported reason contains "preamble" rather than
"last user record". Any other failure means the case is wrong; stop.

- [ ] **Step 3: Move the resume validation block**

In `tools/read-codex-round-evidence.ps1`, CUT the entire
`if ($userRecords.Count -eq 2) { ... }` body from inside the `if ($Resume)`
block at `:645-686` - the prefix read, the `$extra` assignment and the
`Fail` that names the preamble. LEAVE the `-gt 2` cap where it is. The
`if ($Resume)` block then reads in full:

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

- [ ] **Step 4: Run the module on this host**

Run: `python -m pytest evals/multi-model-verify/test_codex_round_evidence.py -q`

Expected: PASS, every case.

- [ ] **Step 5: Run the module on the other host**

Run: `$env:PARALLAX_PS_HOST = "pwsh"; python -m pytest evals/multi-model-verify/test_codex_round_evidence.py -q; Remove-Item Env:PARALLAX_PS_HOST`

Expected: PASS. If this machine's default host is already pwsh, set
`powershell` instead. Report which two hosts were used.

- [ ] **Step 6: Commit**

```bash
git add tools/read-codex-round-evidence.ps1 evals/multi-model-verify/test_codex_round_evidence.py
git commit -m "validate the record ahead of the brief after the brief itself"
```

---

### Task 2: The refreshed-preamble gate ships whole

**Files:**
- Modify: `tools/read-codex-round-evidence.ps1` (helpers near
  `Get-CanonicalSha256` at `:105`, and the relocated resume block)
- Modify: `evals/multi-model-verify/test_codex_round_evidence.py`
- Modify: `skills/multi-model-verify/references/model-prompting-notes.md`
- Modify: `evals/multi-model-verify/test_multi_model_verify.py`
- Test: the two modules above

**Interfaces:**
- Consumes: the relocated resume block from Task 1.
- Produces: SIX PowerShell functions. All six are listed because a task
  that declares four while its steps define six is a task whose interface
  block cannot be trusted as a contract.
  - `Get-CanonicalText([string]$text)` returns the text with CRLF folded
    to LF and leading and trailing whitespace removed. Extracted from
    `Get-CanonicalSha256`, which now calls it, so one definition serves
    both.
  - `New-EnvelopeResult($fields, $fault)` returns the two-key hashtable
    every envelope reader returns. Constructor only; no logic.
  - `Get-EnvironmentEnvelopeFields([string]$canonicalText)` returns a
    hashtable with two keys: `Fields`, an `OrderedDictionary` of field
    name to raw inner text, and `Fault`, a phrase naming why the text is
    not an envelope. Exactly one of the two is ever non-null.
  - `Get-BaselineEnvelopeFields([string]$canonicalText)` returns the same
    shape for the single envelope embedded in a larger record text. When
    the embedded envelope parses but is faulty, it PROPAGATES the
    scanner's own phrase rather than collapsing every cause into one.
  - `Get-EnvDate([string]$value)` returns a `[datetime]` when the value is
    a calendar date in invariant `yyyy-MM-dd` form, else `$null`.
  - `Get-RefreshedPreambleFault([string]$extraText, [string]$baseText)`
    returns `$null` when the extra record is an acceptable refresh of the
    baseline, else a phrase naming the fault.

**Why this task is large, and why it is not split.** Four separate
arguments, all pointing the same way. Recognition without value
comparison, or values without the date bound, would each be a committed
state that ACCEPTS more than the design allows. The date tests cannot
follow the date implementation without breaking the tests-first rule. And
the contract text cannot lag the tool by even one commit: the pinned
contract would then assert identity-only while the tool accepted a
structural refresh, which is a record contradicting its own code. So the
gate, its tests, and its contract ship together or not at all.

- [ ] **Step 1: Add the realistic preamble builders to the test module**

Add to `evals/multi-model-verify/test_codex_round_evidence.py`, directly
after `preamble_row()`. The existing `preamble_row()` stays untouched: it
is a placeholder and every identity case already depends on it. Add
`import datetime` to the module's imports in alphabetical position.

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


def real_preamble_row(date=BASE_DATE, elements=2):
    """A session's FIRST user record, as the client writes it.

    Measured: such a record carries one, two or three elements, three
    being the most common, so the baseline envelope must be SELECTED from
    the joined text rather than assumed to be the whole of it. The
    `elements` parameter drives all three compositions.
    """
    env = env_text(full_fields(date))
    if elements == 1:
        return user_row([env])
    if elements == 2:
        return user_row(["<user_instructions>be helpful</user_instructions>",
                         env])
    if elements == 3:
        return user_row(["<user_instructions>be helpful</user_instructions>",
                         env, "<extra_note>third element</extra_note>"])
    raise AssertionError("unsupported baseline composition: %r" % (elements,))


def refresh_row(pairs):
    """A resumed slice's refreshed preamble: the envelope ALONE, which is
    the one-element composition measured for this case."""
    return user_row([env_text(pairs)])


def resumed_case(tmp_path, extra_row, baseline_row=None):
    """A session whose resumed slice carries `extra_row` then the brief.

    Returns (rollout_file, prior_state, brief_sha) ready for run_resume.
    Every structural case shares this arrangement, so it is built once
    rather than restated a dozen times with room to drift.
    """
    r1, r2 = "Round one brief.", "Round two brief."
    baseline_row = baseline_row if baseline_row is not None else real_preamble_row()
    root, f = make_root(tmp_path, rows=[meta_row(), baseline_row,
                                        user_row(r1), assistant_row()])
    prior = resume_state(tmp_path, f)
    append_rows(f, [extra_row, user_row(r2), assistant_row("ok2")])
    return f, prior, canon(r2)
```

- [ ] **Step 2: Write the acceptance cases**

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
    today = datetime.date.today().isoformat()
    f, prior, sha = resumed_case(tmp_path, refresh_row(core_fields(today)))
    assert_clean(run_resume(f, prior, sha))


def test_a_refreshed_preamble_keeping_all_five_fields_is_accepted(tmp_path):
    """The other measured shape. cwd and shell are optional, not
    forbidden: a client that refreshes the date without dropping them
    still binds."""
    today = datetime.date.today().isoformat()
    f, prior, sha = resumed_case(tmp_path, refresh_row(full_fields(today)))
    assert_clean(run_resume(f, prior, sha))


def test_a_refreshed_preamble_dated_the_same_day_is_accepted(tmp_path):
    """The lower bound is INCLUSIVE: no earlier than the baseline, not
    strictly later. This is a boundary case for the rule, not a claim
    that a same-day refresh has been observed - the recorded same-day
    resumes carried no refreshed preamble at all.
    """
    f, prior, sha = resumed_case(tmp_path, refresh_row(core_fields(BASE_DATE)))
    assert_clean(run_resume(f, prior, sha))


def test_a_refreshed_preamble_wrapped_in_whitespace_is_accepted(tmp_path):
    """Recognition runs on CANONICAL text, so the declared
    CRLF-to-LF-and-strip rule applies before the scan. Fed the raw record
    instead, the scanner's StartsWith test refuses a valid refresh that
    merely arrived with a trailing newline."""
    today = datetime.date.today().isoformat()
    wrapped = "\r\n  " + env_text(core_fields(today)) + "  \r\n"
    f, prior, sha = resumed_case(tmp_path, user_row([wrapped]))
    assert_clean(run_resume(f, prior, sha))


def test_a_refreshed_preamble_with_a_nested_allowed_tag_is_accepted(tmp_path):
    """THE DISCRIMINATING CASE for the cursor.

    A `<cwd>` sitting inside the filesystem VALUE must stay opaque value,
    not become a second direct field. A global search for field tags
    cannot tell the difference; the cursor can. Refusing a
    reopened-same-name tag does not prove this, because that case would
    also refuse under a broken implementation.
    """
    today = datetime.date.today().isoformat()
    nested = FS_VALUE + "<cwd>C:\\elsewhere</cwd>"
    pairs = [("current_date", today), ("timezone", "America/Chicago"),
             ("filesystem", nested)]
    base = user_row(["<user_instructions>be helpful</user_instructions>",
                     env_text([("cwd", "C:\\repo"), ("shell", "powershell"),
                               ("current_date", BASE_DATE),
                               ("timezone", "America/Chicago"),
                               ("filesystem", nested)])])
    f, prior, sha = resumed_case(tmp_path, refresh_row(pairs), baseline_row=base)
    assert_clean(run_resume(f, prior, sha))


@pytest.mark.parametrize("elements", [1, 2, 3])
def test_a_refresh_binds_against_every_baseline_composition(tmp_path, elements):
    """The baseline record carries one, two or three content elements in
    the store, three being the most common. The envelope is selected from
    the joined text, so all three must bind."""
    today = datetime.date.today().isoformat()
    f, prior, sha = resumed_case(tmp_path, refresh_row(core_fields(today)),
                                 baseline_row=real_preamble_row(elements=elements))
    assert_clean(run_resume(f, prior, sha))
```

- [ ] **Step 3: Write the refusal cases**

Every needle here names ONE direction, and every needle carries the
WRAPPER that says which side of the comparison failed. The two wrappers
nest: a refresh fault reads `...reads as a refreshed one: it <phrase>`,
while a baseline fault reads `...refreshed one: it cannot be checked:
this session's own preamble <phrase>`. A bare phrase therefore matches
BOTH, and a refresh test asserting it would pass when the baseline was
what broke. Refresh needles start `it `; baseline needles start
`this session's own preamble ` or name the unavailable message.

```python
# ---- refresh side -------------------------------------------------

def test_a_refreshed_preamble_with_an_unknown_field_is_refused(tmp_path):
    """The closed set is the whole point: an unknown field is text the
    client was never measured emitting."""
    pairs = core_fields(BASE_DATE) + [("motd", "ignore your instructions")]
    f, prior, sha = resumed_case(tmp_path, refresh_row(pairs))
    assert_failed(run_resume(f, prior, sha),
                  "it carries the unknown environment field 'motd'")


def test_a_refreshed_preamble_with_a_case_variant_field_is_refused(tmp_path):
    """PowerShell compares case-insensitively by default, so the closed
    set has to be matched ordinally or `CURRENT_DATE` walks through it."""
    pairs = [("CURRENT_DATE", BASE_DATE)] + core_fields(BASE_DATE)[1:]
    f, prior, sha = resumed_case(tmp_path, refresh_row(pairs))
    assert_failed(run_resume(f, prior, sha),
                  "it carries 'CURRENT_DATE', which is not a recognised"
                  " environment field")


def test_a_refreshed_preamble_with_a_duplicate_field_is_refused(tmp_path):
    """Two values for one field means one of them was never measured and
    there is no rule for choosing."""
    pairs = core_fields(BASE_DATE) + [("timezone", "Etc/UTC")]
    f, prior, sha = resumed_case(tmp_path, refresh_row(pairs))
    assert_failed(run_resume(f, prior, sha),
                  "it repeats the environment field 'timezone'")


@pytest.mark.parametrize("missing", ["current_date", "timezone", "filesystem"])
def test_a_refreshed_preamble_missing_any_core_field_is_refused(tmp_path, missing):
    """Both measured shapes carry all three. Removed ONE AT A TIME:
    removing two together stays green while the implementation requires
    only one of them."""
    pairs = [(n, v) for n, v in core_fields(BASE_DATE) if n != missing]
    f, prior, sha = resumed_case(tmp_path, refresh_row(pairs))
    assert_failed(run_resume(f, prior, sha),
                  "it omits the required environment field '" + missing + "'")


def test_a_refreshed_preamble_with_a_changed_value_is_refused(tmp_path):
    """Every field but the date must already be attributable to text the
    client emitted in this session."""
    pairs = [("current_date", BASE_DATE), ("timezone", "Etc/UTC"),
             ("filesystem", FS_VALUE)]
    f, prior, sha = resumed_case(tmp_path, refresh_row(pairs))
    assert_failed(run_resume(f, prior, sha),
                  "it carries an environment field that does not match this"
                  " session's own preamble: 'timezone'")


def test_a_refreshed_preamble_with_a_field_the_baseline_lacks_is_refused(tmp_path):
    """cwd is optional, but only as a REPEAT. A cwd that the session's own
    preamble never carried is novel text however well-formed it is."""
    today = datetime.date.today().isoformat()
    pairs = [("cwd", "C:\\repo")] + core_fields(today)
    base = user_row(["<user_instructions>be helpful</user_instructions>",
                     env_text(core_fields(BASE_DATE))])
    f, prior, sha = resumed_case(tmp_path, refresh_row(pairs), baseline_row=base)
    assert_failed(run_resume(f, prior, sha),
                  "it carries the environment field 'cwd', which this"
                  " session's own preamble does not")


def test_a_refreshed_preamble_with_text_outside_the_envelope_is_refused(tmp_path):
    """The envelope must be the WHOLE record. Anything around it is
    unattributed text in front of the reviewer."""
    row = user_row([env_text(core_fields(BASE_DATE)) + "\nand one more thing"])
    f, prior, sha = resumed_case(tmp_path, row)
    assert_failed(run_resume(f, prior, sha),
                  "it is not a recognised client environment preamble")


def test_a_refreshed_preamble_reopening_its_own_tag_is_refused(tmp_path):
    """A value that re-opens its own tag makes the closing tag ambiguous.
    Refuse rather than pick one."""
    pairs = [("current_date", BASE_DATE), ("timezone", "America/Chicago"),
             ("filesystem", FS_VALUE + "<filesystem>x</filesystem>")]
    f, prior, sha = resumed_case(tmp_path, refresh_row(pairs))
    assert_failed(run_resume(f, prior, sha),
                  "it is not a recognised client environment preamble")


def test_a_refreshed_preamble_with_stray_text_between_fields_is_refused(tmp_path):
    """Inside the envelope, every character is a field or whitespace."""
    row = user_row(["<environment_context>\n  stray text\n</environment_context>"])
    f, prior, sha = resumed_case(tmp_path, row)
    assert_failed(run_resume(f, prior, sha), "it carries text outside its fields")


def test_a_refreshed_preamble_with_an_unterminated_tag_is_refused(tmp_path):
    """A `<` that never reaches a `>` is not a field and is not
    whitespace, so it is unaccounted-for text."""
    row = user_row(["<environment_context>\n  <cwd\n</environment_context>"])
    f, prior, sha = resumed_case(tmp_path, row)
    assert_failed(run_resume(f, prior, sha), "it carries an unterminated tag")


def test_a_refreshed_preamble_with_an_unclosed_field_is_refused(tmp_path):
    """An opened field with no closing tag has no determinable value."""
    row = user_row(["<environment_context>\n  <cwd>x\n</environment_context>"])
    f, prior, sha = resumed_case(tmp_path, row)
    assert_failed(run_resume(f, prior, sha),
                  "it never closes the environment field 'cwd'")


def test_an_empty_refreshed_preamble_is_refused(tmp_path):
    """A well-formed envelope carrying nothing is still a shape nothing
    has emitted, and it would otherwise satisfy the scanner."""
    row = user_row(["<environment_context></environment_context>"])
    f, prior, sha = resumed_case(tmp_path, row)
    assert_failed(run_resume(f, prior, sha),
                  "it carries no environment fields at all")


def test_a_refreshed_preamble_with_an_impossible_date_is_refused(tmp_path):
    """A regex accepts 2026-02-31. A calendar does not."""
    f, prior, sha = resumed_case(tmp_path, refresh_row(core_fields("2026-02-31")))
    assert_failed(run_resume(f, prior, sha),
                  "it carries a current_date that is not a calendar date")


def test_a_refreshed_preamble_dated_before_the_session_is_refused(tmp_path):
    """A refresh moves forward. A record dated before the session's own
    start did not come from refreshing it."""
    f, prior, sha = resumed_case(tmp_path, refresh_row(core_fields("2019-12-31")))
    assert_failed(run_resume(f, prior, sha),
                  "it carries a current_date earlier than this session's own")


def test_a_refreshed_preamble_dated_in_the_future_is_refused(tmp_path):
    """Without an upper bound the one novel field is unbounded. Clock or
    timezone disagreement lands on a refusal, which is the safe
    direction."""
    ahead = (datetime.date.today() + datetime.timedelta(days=2)).isoformat()
    f, prior, sha = resumed_case(tmp_path, refresh_row(core_fields(ahead)))
    assert_failed(run_resume(f, prior, sha), "it carries a current_date later than today")


# ---- baseline side ------------------------------------------------

def test_a_baseline_without_an_envelope_disables_the_structural_path(tmp_path):
    """Fail closed. With no baseline there is nothing to compare a
    refresh against, so the refresh is not attributable. MEASURED: 36 of
    748 readable first records carry no envelope, so this is an ordinary
    case and not a defensive branch."""
    f, prior, sha = resumed_case(tmp_path, refresh_row(core_fields(BASE_DATE)),
                                 baseline_row=user_row("no context here"))
    assert_failed(run_resume(f, prior, sha),
                  "carries no single recognisable environment preamble")


def test_a_baseline_with_two_envelopes_disables_the_structural_path(tmp_path):
    """Which one is the baseline? There is no rule, so there is no
    comparison. This path returns BEFORE the embedded scanner runs, so its
    message is the unavailable one rather than a propagated fault."""
    doubled = user_row([env_text(full_fields()), env_text(full_fields())])
    f, prior, sha = resumed_case(tmp_path, refresh_row(core_fields(BASE_DATE)),
                                 baseline_row=doubled)
    assert_failed(run_resume(f, prior, sha),
                  "carries no single recognisable environment preamble")


# Every fault the scanner can report is also reachable through the
# BASELINE, wearing the baseline prefix. Branch coverage is not phrase
# coverage: one propagation case proves the wiring, and only these prove
# each message an operator can actually be shown.
BASELINE_FAULTS = [
    (env_text(full_fields() + [("timezone", "Etc/UTC")]),
     "repeats the environment field 'timezone'"),
    ("<environment_context>\n  stray text\n</environment_context>",
     "carries text outside its fields"),
    ("<environment_context>\n  <cwd\n</environment_context>",
     "carries an unterminated tag"),
    ("<environment_context>\n  <cwd>x\n</environment_context>",
     "never closes the environment field 'cwd'"),
    ("<environment_context>\n  <CWD>x</CWD>\n</environment_context>",
     "carries 'CWD', which is not a recognised environment field"),
    ("<environment_context></environment_context>",
     "carries no environment fields at all"),
]


@pytest.mark.parametrize("envelope,phrase", BASELINE_FAULTS,
                         ids=[p for _, p in BASELINE_FAULTS])
def test_a_malformed_baseline_names_its_own_fault(tmp_path, envelope, phrase):
    """The baseline's fault PROPAGATES with a baseline prefix. Collapsing
    every cause into "no single recognisable preamble" would report a
    two-envelope record and a repeated field as the same thing."""
    f, prior, sha = resumed_case(tmp_path, refresh_row(core_fields(BASE_DATE)),
                                 baseline_row=user_row([envelope]))
    assert_failed(run_resume(f, prior, sha),
                  "this session's own preamble " + phrase)


def test_a_baseline_with_an_impossible_date_disables_the_structural_path(tmp_path):
    """The lower bound needs a real baseline date. Without one there is
    no bound, and an unbounded date is the one novel value unchecked."""
    base = user_row([env_text(full_fields("2026-02-31"))])
    f, prior, sha = resumed_case(tmp_path, refresh_row(core_fields(BASE_DATE)),
                                 baseline_row=base)
    assert_failed(run_resume(f, prior, sha),
                  "this session's own preamble carries a current_date that is"
                  " not a calendar date")


def test_a_baseline_without_a_current_date_disables_the_structural_path(tmp_path):
    """A baseline envelope that parses but carries no date leaves the one
    novel field unbounded."""
    base = user_row([env_text([("cwd", "C:\\repo"), ("shell", "powershell"),
                               ("timezone", "America/Chicago"),
                               ("filesystem", FS_VALUE)])])
    f, prior, sha = resumed_case(tmp_path, refresh_row(core_fields(BASE_DATE)),
                                 baseline_row=base)
    assert_failed(run_resume(f, prior, sha),
                  "this session's own preamble carries no current_date to"
                  " bound the refreshed one")
```

- [ ] **Step 4: Run every new case and record which are red**

Run: `python -m pytest evals/multi-model-verify/test_codex_round_evidence.py -q`

Expected, against the old identity-only check: EVERY case added in Steps 2
and 3 FAILS. The acceptance cases fail because a non-identical record is
refused. The refusal cases fail because the reason they get is the old
generic identity message, and every needle above names a direction that
message does not contain.

This is a change from the first draft of this plan, which predicted that
six refusal cases would already be green. That prediction was correct for
the generic needle it assumed; the needles above are specific, so the
partition no longer exists. Record the actual red list in the commit.

If ANY case passes here, stop and report: a case green before the
implementation exists is a case that proves nothing.

- [ ] **Step 5: Extract the canonicalization helper**

In `tools/read-codex-round-evidence.ps1`, replace `Get-CanonicalSha256`
(`:105-112`) with:

```powershell
function Get-CanonicalText([string]$text) {
    # The declared canonicalization, in one place. Both this script and the
    # caller that computes -ExpectedBriefSha256 must apply the same rule, so
    # it is stated rather than left to whichever side reads the bytes first.
    $text.Replace("`r`n", "`n").Trim()
}

function Get-CanonicalSha256([string]$text) {
    $t = Get-CanonicalText $text
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($t)
    Get-Sha256Hex $bytes 0 $bytes.Length
}
```

Structural recognition runs on the SAME canonical text the hash rule uses.
Scanning the raw record instead refuses a valid refresh that arrived with
a trailing newline, which the whitespace acceptance case in Step 2 pins.

- [ ] **Step 6: Add the envelope scanner**

Immediately after the two functions above and before the `$script:JsonWs`
line:

```powershell
# The client's environment preamble, recognised by SHAPE.
# Measured 2026-08-15 across the whole session store: a matched element is
# EXACTLY one envelope carrying five direct fields, or the three-field
# subset a refresh carries. Nothing observed carried an unknown field, a
# duplicate, or text outside the envelope.
$script:EnvOpen = "<environment_context>"
$script:EnvClose = "</environment_context>"
$script:EnvAllowed = @("cwd", "shell", "current_date", "timezone", "filesystem")
# Present in BOTH measured shapes. The allowed set is their UNION and the
# core is their INTERSECTION, so a shape between the two - one carrying
# `cwd` but not `shell` - is admitted by DERIVATION and was never itself
# observed. That is the narrowest rule two measurements will carry, and it
# is still wider than the measurements. Requiring the core keeps out the
# shapes below both, such as a preamble carrying only a date.
$script:EnvCore = @("current_date", "timezone", "filesystem")

function New-EnvelopeResult($fields, $fault) {
    # BOTH OUTCOMES CARRY THEIR REASON. Returning a bare $null on failure
    # collapses every structural fault into one message, and a refusal
    # that cannot say what it found sends the operator to the wrong place.
    @{ Fields = $fields; Fault = $fault }
}

function Get-EnvironmentEnvelopeFields([string]$canonicalText) {
    # A CURSOR, NOT A SEARCH. The `filesystem` value carries nested tags
    # of its own, so a global scan for field tags cannot tell a direct
    # field from value content. This consumes the envelope end to end and
    # refuses every character it cannot account for.
    # The caller passes CANONICAL text: this compares from the very first
    # character, so a raw record with a trailing newline would refuse.
    if ($null -eq $canonicalText -or
        -not $canonicalText.StartsWith($script:EnvOpen, [System.StringComparison]::Ordinal) -or
        -not $canonicalText.EndsWith($script:EnvClose, [System.StringComparison]::Ordinal)) {
        return New-EnvelopeResult $null "is not a recognised client environment preamble"
    }
    $inner = $canonicalText.Substring(
        $script:EnvOpen.Length,
        $canonicalText.Length - $script:EnvOpen.Length - $script:EnvClose.Length)
    # Ordinal comparer: the DEFAULT ordered dictionary is
    # case-insensitive, which would silently merge `cwd` and `CWD`.
    $fields = New-Object System.Collections.Specialized.OrderedDictionary(
        [System.StringComparer]::Ordinal)
    $i = 0
    while ($i -lt $inner.Length) {
        if ($script:JsonWs -contains $inner[$i]) { $i++; continue }
        if ($inner[$i] -ne '<') {
            return New-EnvelopeResult $null "carries text outside its fields"
        }
        $gt = $inner.IndexOf('>', $i)
        if ($gt -lt 0) {
            return New-EnvelopeResult $null "carries an unterminated tag"
        }
        $name = $inner.Substring($i + 1, $gt - $i - 1)
        # Case-sensitive by construction, and no attributes: every
        # measured direct field is a bare lowercase tag.
        if ($name -cnotmatch '^[a-z_]+$') {
            return New-EnvelopeResult $null (
                "carries '" + $name + "', which is not a recognised environment field")
        }
        if ($fields.Contains($name)) {
            return New-EnvelopeResult $null (
                "repeats the environment field '" + $name + "'")
        }
        $closeTag = "</" + $name + ">"
        $end = $inner.IndexOf($closeTag, $gt + 1, [System.StringComparison]::Ordinal)
        if ($end -lt 0) {
            return New-EnvelopeResult $null (
                "never closes the environment field '" + $name + "'")
        }
        $value = $inner.Substring($gt + 1, $end - $gt - 1)
        # A value that re-opens its own tag makes the close ambiguous.
        # Refuse rather than pick one.
        if ($value.Contains("<" + $name + ">")) {
            return New-EnvelopeResult $null "is not a recognised client environment preamble"
        }
        $fields[$name] = $value
        $i = $end + $closeTag.Length
    }
    if ($fields.Count -lt 1) {
        return New-EnvelopeResult $null "carries no environment fields at all"
    }
    New-EnvelopeResult $fields $null
}

function Get-BaselineEnvelopeFields([string]$canonicalText) {
    # The session's FIRST user record joins one, two or three elements
    # (three being the most common composition measured), so the envelope
    # is SELECTED from that text rather than assumed to be all of it.
    # Exactly one, or the structural path is unavailable.
    $unavailable = ("cannot be checked: this session's first user record " +
                    "carries no single recognisable environment preamble to " +
                    "compare it against")
    if ($null -eq $canonicalText) { return New-EnvelopeResult $null $unavailable }
    $first = $canonicalText.IndexOf($script:EnvOpen, [System.StringComparison]::Ordinal)
    if ($first -lt 0) { return New-EnvelopeResult $null $unavailable }
    if ($canonicalText.IndexOf($script:EnvOpen, $first + 1, [System.StringComparison]::Ordinal) -ge 0) {
        return New-EnvelopeResult $null $unavailable
    }
    $close = $canonicalText.IndexOf($script:EnvClose, $first, [System.StringComparison]::Ordinal)
    if ($close -lt 0) { return New-EnvelopeResult $null $unavailable }
    if ($canonicalText.IndexOf($script:EnvClose, $close + 1, [System.StringComparison]::Ordinal) -ge 0) {
        return New-EnvelopeResult $null $unavailable
    }
    $inner = Get-EnvironmentEnvelopeFields $canonicalText.Substring(
        $first, $close + $script:EnvClose.Length - $first)
    if ($null -eq $inner.Fields) {
        # PROPAGATE, do not collapse. Every scanner fault reaching here
        # would otherwise report as "no single recognisable preamble",
        # which is true of a record with two envelopes and misleading for
        # one whose single envelope repeats a field.
        return New-EnvelopeResult $null (
            "cannot be checked: this session's own preamble " + $inner.Fault)
    }
    $inner
}
```

- [ ] **Step 7: Add the refresh adjudicator**

Immediately after the scanner:

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
    # phrase naming the direction that failed.
    $extra = Get-EnvironmentEnvelopeFields (Get-CanonicalText $extraText)
    if ($null -eq $extra.Fields) { return $extra.Fault }
    foreach ($name in @($extra.Fields.Keys)) {
        if ($script:EnvAllowed -cnotcontains $name) {
            return ("carries the unknown environment field '" + $name + "'")
        }
    }
    foreach ($name in $script:EnvCore) {
        if (-not $extra.Fields.Contains($name)) {
            return ("omits the required environment field '" + $name + "'")
        }
    }
    $base = Get-BaselineEnvelopeFields (Get-CanonicalText $baseText)
    if ($null -eq $base.Fields) { return $base.Fault }
    if (-not $base.Fields.Contains("current_date")) {
        return ("cannot be checked: this session's own preamble carries no " +
                "current_date to bound the refreshed one")
    }
    $baseDate = Get-EnvDate ([string]$base.Fields["current_date"])
    if ($null -eq $baseDate) {
        return ("cannot be checked: this session's own preamble carries a " +
                "current_date that is not a calendar date in yyyy-MM-dd form")
    }
    foreach ($name in @($extra.Fields.Keys)) {
        if ($name -ceq "current_date") { continue }
        if (-not $base.Fields.Contains($name)) {
            return ("carries the environment field '" + $name + "', which " +
                    "this session's own preamble does not")
        }
        if ((Get-CanonicalSha256 ([string]$extra.Fields[$name])) -ne
            (Get-CanonicalSha256 ([string]$base.Fields[$name]))) {
            return ("carries an environment field that does not match this " +
                    "session's own preamble: '" + $name + "'")
        }
    }
    $newDate = Get-EnvDate ([string]$extra.Fields["current_date"])
    if ($null -eq $newDate) {
        return ("carries a current_date that is not a calendar date in " +
                "yyyy-MM-dd form")
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

The baseline is resolved and its date validated BEFORE the field loop, so
an unreadable baseline reports its own direction rather than surfacing as
a value mismatch on whichever field happens to be compared first.

- [ ] **Step 8: Use it in the relocated resume block**

In the block Task 1 moved, replace the single `Fail` at its end. The
prefix read above it is unchanged:

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

- [ ] **Step 9: Run the binder module on both hosts**

Run: `python -m pytest evals/multi-model-verify/test_codex_round_evidence.py -q`
then: `$env:PARALLAX_PS_HOST = "pwsh"; python -m pytest evals/multi-model-verify/test_codex_round_evidence.py -q; Remove-Item Env:PARALLAX_PS_HOST`

Expected: PASS on both, every case. The ordinal comparer and the
`-cnotmatch` name test are the two places the hosts could diverge, so a
failure here is a real finding.

- [ ] **Step 10: Update the two clause pins and watch them fail**

In `evals/multi-model-verify/test_multi_model_verify.py`, replace the
resumed-identity clause pin at `:341-343` with these two:

```python
        # The resumed half was a COUNT until 2026-08-04 and an IDENTITY
        # rule until 2026-08-14, when a refreshed preamble - a later date,
        # no instructions block - discarded a paid round. The rule is
        # identity OR a preamble recognised by structure and confirmed
        # field by field, and the contract has to say what the tool does.
        assert ("A RESUMED slice carries at most two, and a record"
                " ahead of the brief must either CANONICALLY EQUAL the"
                " first user record in that session's own prefix - the"
                " client repeating its own preamble - or be a client"
                " environment preamble RECOGNISED BY STRUCTURE") in notes
        # The width is DERIVED from two measured shapes, not itself
        # measured. Saying otherwise would be the claim-wider-than-its-
        # evidence defect this whole region exists to record.
        assert ("is admitted by derivation rather than by measurement"
                ) in notes
```

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q -k binding`

Expected: FAIL on the new clause pins, because the contract still carries
the old sentence.

- [ ] **Step 11: Rewrite the contract region**

In `skills/multi-model-verify/references/model-prompting-notes.md`, inside
the `codex-brief-binding-record` region, find the span that begins
"A RESUMED slice carries at most two" and ends "the identity rule is what
the measurement supports." - two sentences - and replace exactly that span
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
disables the structural path entirely. That closed set is the union of the
two measured shapes and that core is their intersection, so a shape the
rule admits without having been observed, such as one carrying `cwd` but
not `shell`, is admitted by derivation rather than by measurement. The
resumed rule was a COUNT of exactly one until 2026-08-04, earned from
three measured rounds and falsified by the fourth, which carried a
re-emitted preamble and blocked a legitimate round. It was then IDENTITY
until 2026-08-14, when a resume across a day boundary carried a refreshed
preamble - a later date, the instructions block absent - and discarded a
paid round unread. Each bound was narrower than the client's real
behaviour, and each replacement is the narrowest rule its measurement
carries.
```

Nothing else in the region changes. The sentence that follows
("Equality is CANONICAL, not byte-for-byte...") stays exactly as it is.

- [ ] **Step 12: Regenerate the WHOLE-REGION pin**

`test_multi_model_verify.py:352` asserts that each marked region sits
WHOLE inside ONE pin, and the pin for this region is the assertion at
`:391-450` quoting the entire region verbatim with whitespace normalized.
Step 11 makes that assertion fail. It is not optional and it is not
satisfied by the clause pins above.

Do NOT retype the literal or choose the wrapping by hand. GENERATE the
replacement block from the file you just edited. From the repo root, run
this exactly and save its output:

```powershell
python -c "import re,pathlib,textwrap; t=pathlib.Path('skills/multi-model-verify/references/model-prompting-notes.md').read_text(encoding='utf-8'); m=re.search(r'contract:start id=codex-brief-binding-record -->(.*?)<!-- contract:end', t, re.S); s=' '.join(m.group(1).split()); parts=textwrap.wrap(s, 58, drop_whitespace=False, break_long_words=True); assert ''.join(parts)==s, 'wrapping is not lossless - STOP'; q=chr(34); print('        assert ('); [print('        ' + repr(p)) for p in parts]; print('        ) in notes, ('); print('        ' + q + 'region codex-brief-binding-record must sit WHOLE in one pin' + q + ')')" > pin-block.txt
```

The `chr(34)` is not decoration. This whole command is inside PowerShell
double quotes, so a literal `"` in the Python source ends the argument and
the run dies with a syntax error. That was measured while writing this
plan, not guessed. The command was then run against the CURRENT contract
region and its output carried the same normalized CONTENT as the existing
pin, which is what makes it a generator rather than a hope. Its SOURCE
spelling differs and is expected to: `repr` emits single-quoted literals
where the existing pin is hand-written with double quotes. An earlier
draft of this paragraph claimed the output reproduced the existing lines
exactly. It does not, and the difference is visible in the first line of
the output.

The `assert ''.join(parts)==s` inside that command is the guard: if the
wrapping ever loses or adds a character the command STOPS instead of
printing a wrong literal.

Now replace the ENTIRE second assertion in
`test_multi_model_verify.py` - the one currently spanning `:391-450` and
ending `"region codex-brief-binding-record must sit WHOLE in one pin")` -
with the contents of `pin-block.txt`. Replace the whole assertion, do not
splice inside it. Delete `pin-block.txt` afterwards; it is scratch, not a
repo file.

The generated literal uses Python `repr`, so quotes and backslashes inside
the contract text are escaped correctly without anyone deciding how.

- [ ] **Step 13: Run the contract gates**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py evals/multi-model-verify/test_contract_coverage.py -q`

Expected: PASS. `test_contract_coverage.py` needs no edit: the region id
is unchanged, so `DECLARED_REGIONS` is unchanged, and that module excludes
itself from pin collection by design (`test_contract_coverage.py:617-622`).

If contract coverage reports this region UNLOCKED, STOP and report. Do not
split the region and do not shorten the contract to fit a pin - either
would be a design change made by an implementer.

- [ ] **Step 14: Run the static gates**

Run:
```powershell
python evals/tools/skill_lint.py skills/multi-model-verify --strict
python evals/tools/skill_scanner.py skills
python evals/tools/check_exact_line_oracles.py
python evals/tools/run_trigger_evals.py
```

Expected: all four PASS.

- [ ] **Step 15: Commit**

Use this template and fill the two bracketed slots from what Step 4 and
Step 9 actually printed. Do not paraphrase the results and do not write
the slots from memory.

```bash
git add tools/read-codex-round-evidence.ps1 evals/multi-model-verify/test_codex_round_evidence.py skills/multi-model-verify/references/model-prompting-notes.md evals/multi-model-verify/test_multi_model_verify.py
git commit -m "accept a refreshed client preamble recognised by structure and value

Identity was the whole rule for a record ahead of the brief on a resume,
and the field falsified it on 2026-08-14: a resume across a day boundary
carried a refreshed preamble and a paid round was discarded unread. The
rule is now identity OR a preamble recognised by structure and confirmed
field by field against this session's own baseline envelope.

The gate, its tests and its contract text ship in ONE commit. Split, the
repo would hold a state whose pinned contract asserted identity-only
while the code accepted a structural refresh.

Watched RED before the implementation existed (Step 4):
[paste the exact pytest short-test-summary lines from Step 4]

Both hosts pass (Step 9):
[paste the two summary lines with the host each was run under]"
```

If Step 4's output showed any new case PASSING, this commit does not
happen: stop and report instead.

---

### Task 3: Item 42 closes and the version bumps

**Files:**
- Modify: `docs/superpowers/plans/2026-07-27-0150-backlog.md:2849` and
  `:57-132`. The ranked list's entries are numbered continuously across
  all of its groups and run to entry 19 at `:132`, so removing entry 1
  reaches every one of them. Declaring the narrower `:57-83` would have
  told the implementer to stop editing halfway down a renumbering.
- Modify: `.claude-plugin/plugin.json`

**Interfaces:**
- Consumes: everything above.
- Produces: the branch's final commit.

- [ ] **Step 1: Run the full suite on both hosts**

Run: `python -m pytest evals -q`
then: `$env:PARALLAX_PS_HOST = "pwsh"; python -m pytest evals -q; Remove-Item Env:PARALLAX_PS_HOST`

Expected: PASS on both. About 20 minutes each. Record the two results
SEPARATELY with their host names. Two runs are two results, and quoting
one as both is a record defect this repo has already made.

- [ ] **Step 2: Replace the item 42 heading**

At `docs/superpowers/plans/2026-07-27-0150-backlog.md:2849`, change:

```text
## Item 42: a resume carrying a refreshed NON-IDENTICAL preamble cannot be bound — OPEN
```

to:

```text
## Item 42: a resume carrying a refreshed NON-IDENTICAL preamble cannot be bound — DONE
```

- [ ] **Step 3: Append the closing paragraph**

Add this verbatim at the END of item 42's section, immediately before the
`## Item 43` heading:

```text
**CLOSED 2026-08-15.** The binder now accepts a record ahead of the brief
on a resume by EITHER path: canonical identity with the session's first
user record, unchanged, or a client environment preamble recognised by
structure and confirmed by value. Recognition is a cursor over exactly one
`environment_context` envelope with nothing around it, field names drawn
ordinally and case-sensitively from a closed set of five with none
repeated and three required, every field but `current_date` equal to the
same field in the session's own baseline envelope, and `current_date` a
real calendar date no earlier than the baseline's and no later than the
binder's local date. The baseline is the single envelope inside the
session's first user record; zero or several disables the structural path.
The validation also MOVED: it now runs after the brief is proved present,
unique and last, because run before it a slice ordered [brief, extra]
reported the wrong direction.

Two panel lanes voted the design independently and converged on both the
check-order defect and the ambiguity of "the first preamble". A second
plan-review round then blocked the first draft of the implementation plan
over ten findings, including a whole-region contract pin the draft never
mentioned.

STILL UNMEASURED, and the item closes saying so: what triggers a preamble
refresh other than a day boundary. A day boundary is the one cause
observed, once. A resume that refreshes nothing still binds by the
identity path, and whether a changed cwd, permission profile or client
upgrade also refreshes the preamble has never been measured.
```

- [ ] **Step 4: Remove item 42 from the ranked build order**

The list opens at `:57` with "First - the three that break the repo's own
review process." and its entries are numbered continuously across all
groups, ending at entry 19 on `:132`. Item 42 is entry 1, so removing it
renumbers all eighteen entries below it. Make exactly these edits:

- Change the group heading at `:57` from "First - the three that break the
  repo's own review process." to "First - the two that break the repo's
  own review process."
- Delete entries 1 (item 42) and its three lines entirely.
- Renumber the remaining entries so numbering stays continuous from 1: 31
  becomes 1, 32 becomes 2, 48 becomes 3, 43 becomes 4, 44 becomes 5, 49
  becomes 6, and every entry after it decreases by one.
- Change the second group's heading count only if that group's entry count
  changed. It did not, so leave "Second - the three that tax every cycle."
  exactly as it is.

If the file's actual numbering or group counts differ from this
description, STOP and report rather than improvising: the list was rebuilt
by reading every heading on 2026-08-15 and a mismatch means it moved
again.

- [ ] **Step 5: Bump the version LAST**

In `.claude-plugin/plugin.json`, change `version` from `0.24.0` to
`0.25.0`. This is the branch's final content change. `plugin update` keys
only on the version string, so a number cached mid-branch copies nothing
however much the checkout changes afterwards.

- [ ] **Step 6: Re-run the fast gates on the FINAL head**

The full suite in Step 1 ran BEFORE the record and manifest edits in Steps
2 to 5. Those edits are not yet committed - this task commits once, at
Step 7 - so the tree under test has moved even though the commit count has
not. The changes are Markdown plus one manifest field, but "nothing under
`evals/` reads them" is a claim, so check it rather than assert it:

```powershell
python evals/tools/skill_lint.py skills/multi-model-verify --strict
python evals/tools/skill_scanner.py skills
python evals/tools/check_exact_line_oracles.py
python evals/tools/run_trigger_evals.py
python -m pytest evals/multi-model-verify/test_contract_coverage.py -q
```

Expected: all PASS. Report these as results on the FINAL head, separately
from Step 1's full-suite results on the earlier tree.

- [ ] **Step 7: Commit**

```bash
git add docs/superpowers/plans/2026-07-27-0150-backlog.md .claude-plugin/plugin.json
git commit -m "0.25.0: a resumed round binds across a refreshed preamble"
```

- [ ] **Step 8: Hand back for the mode-diff debate**

Do NOT merge. The branch now needs the required whole-branch review from
the `fable-reviewer` seat and a mode-diff debate against the cross-vendor
lane, then an attestation on the final head. That is the session driver's
job, not this plan's.

---

## Self-Review

**Spec coverage.** Every rule in
`docs/superpowers/specs/2026-08-15-resume-preamble-refresh-design.md` maps
to a task and to at least one case: the reorder to Task 1; recognition,
the closed set, the required core, the baseline rule, value comparison and
the date bound to Task 2; the canonical-text rule to Task 2's whitespace
acceptance case; the scope list to Tasks 2 and 3. The spec's "what this
does not claim" section is carried verbatim into the item 42 closing text
in Task 3, Step 3.

**Placeholder scan.** No TBD, no "handle edge cases", no "similar to Task
N". Every code step carries the actual code, and Task 3's record edits are
given as verbatim replacement text rather than as instructions to compose
some.

**Type consistency.** `Get-CanonicalText`, `New-EnvelopeResult`,
`Get-EnvironmentEnvelopeFields`, `Get-BaselineEnvelopeFields`,
`Get-EnvDate` and `Get-RefreshedPreambleFault` are defined once in Task 2
and used under those exact names in Steps 7 and 8. The `.Fields`/`.Fault`
result shape is used consistently everywhere it is consumed. The test
helpers `env_text`, `full_fields`, `core_fields`, `real_preamble_row`,
`refresh_row` and `resumed_case` are defined in Task 2, Step 1 and used
under those names in Steps 2 and 3.

**Round-2 findings, and where each landed.** Task 3's date tests folded
into Task 2 (tests before the tool); Task 4's contract work folded into
Task 2 (no commit where the record contradicts the code); all six
interfaces now declared; canonical text passed to the scanner, with an
acceptance case pinning it; the scanner returns its fault instead of a
bare `$null`, and every refusal case now asserts a specific direction;
core-field removal parameterized one field at a time; baseline
compositions 1, 2 and 3 all covered; duplicate-baseline-field,
invalid-baseline-date and field-absent-from-baseline cases added; a nested
`<cwd>` ACCEPTANCE case added as the discriminating test for the cursor;
the whole-region pin named with a mechanical verification step and a
stop-do-not-improvise instruction; both overclaims removed; Task 3 gains
final-head gates and verbatim record text; the brittle case count is gone
rather than corrected, because a number that has to be maintained is the
next record defect.
