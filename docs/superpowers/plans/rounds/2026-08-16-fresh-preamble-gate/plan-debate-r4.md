# Plan debate, round 4 - 0.26.0 fresh-preamble gate

Same session `01a00b96-1d26-77f2-bb53-13702ab58e1a`, resumed a third time.
Route re-confirmed against the transcript header - `gpt-5.6-sol`, openai,
read-only, effort high - and the reply bound by
`tools/read-codex-round-evidence.ps1 -Resume` before it was read: verdict
`clean`, brief digest `4c43c31b158ca635be9ba9bacb73dba79d735b440fb2218ca7f92b4401c95472`,
over round 3's `nextState` verbatim as the prior state.

The round asked whether the hardened checker is sound, and then swept the
third class - oracle vacuity - across the WHOLE plan rather than the
checker.

Verdict: **FIX**. Two more vacuity paths inside the checker, and one
OUTSIDE it, in a shipped gate this branch does not own. All three accepted.
The external one is filed as backlog item 60 rather than fixed here, under
the debate protocol's rule for pre-existing defects: same named class,
different verification surface.

The reply is retained verbatim.

---

The five hardening changes work as intended, but two checker gaps and one external oracle-vacuity path remain.

## 1. Hardened checker

The accepted fixes are correctly implemented:

- A duplicate heading appends a permanent failure and preserves the first heading instead of silently overwriting it ([plan:1353](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1353)). The `continue` is safe: later checks use the retained first heading, while the duplicate failure remains in `fail` and therefore forces exit 1 ([plan:1459](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1459)).

- Duplicate status rows likewise append a permanent failure and retain the first row ([plan:1377](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1377)).

- An empty ranked section now fails explicitly ([plan:1417](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1417)).

- Whole-entry scanning is correct. Each span runs to the next numbered entry or the section boundary ([plan:1428](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1428)). The intervening group headers contain bold prose but no `**N**`: First, Second, Third, Fourth, Fifth, and Last are all nonnumeric ([backlog:62](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:62), [backlog:109](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:109), [backlog:124](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:124), [backlog:163](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:163), [backlog:185](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:185), [backlog:194](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:194)).

- Empty block files now fail explicitly ([plan:1440](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1440)).

- `body.endswith(want)` correctly proves that the complete raw block is terminal after insignificant trailing whitespace is removed ([plan:1445](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1445), [plan:1452](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1452)). It also catches a missing blank line between Item 56’s two paragraphs because that blank line is inside `want` ([plan:1465](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1465)).

Two gaps remain:

1. A ranked item with no status-bearing heading passes. Check 3 asks only whether each bold number belongs to `closed`; an unknown number such as `**999**` is not in `closed`, so no failure is added ([plan:1426](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1426)). The checker therefore reports OK without knowing that ranked item’s status. Require every extracted item number to exist in `from_headings` before testing whether it is closed.

2. The surrounding blank-line requirement is still unverified. Step 2 requires one blank line on each side of every closing block ([plan:1198](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1198)), but `.strip()`, `.rstrip()`, and `endswith()` discard or ignore those surrounding separators ([plan:1440](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1440), [plan:1454](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1454)). Pasting the block directly against preceding prose can still pass. Either verify the raw separators or remove that requirement from Step 2.

## 2. Class 3 sweep

One new instance exists outside the checker.

`run_trigger_evals.py`, invoked by Task 3 Step 13 and Task 4 Step 6 ([plan:1107](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1107), [plan:1564](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1564)), can report success after measuring no cases for a skill:

- A missing `trigger-cases.json` produces only a warning and continues ([run_trigger_evals.py:99](C:/Users/Brandon/Documents/parallax/evals/tools/run_trigger_evals.py:99)).
- Cases marked `lexical: false` are skipped ([run_trigger_evals.py:104](C:/Users/Brandon/Documents/parallax/evals/tools/run_trigger_evals.py:104)).
- The actual comparison runs only when both filtered `pos` and `neg` are nonempty; otherwise no failure is recorded ([run_trigger_evals.py:117](C:/Users/Brandon/Documents/parallax/evals/tools/run_trigger_evals.py:117)).
- It then prints `all clear` and exits 0 whenever no other failure occurred ([run_trigger_evals.py:131](C:/Users/Brandon/Documents/parallax/evals/tools/run_trigger_evals.py:131)).

The schema test does not close the filtered-case path: it requires positive and negative cases before considering `lexical`, but never requires a lexical positive and lexical negative ([test_multi_model_verify.py:1256](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_multi_model_verify.py:1256)). Require a case file and at least one lexical positive and negative per skill; absence must increment `failures`.

The rest of the Class 3 sweep is dry:

- Misspelled explicit node IDs cannot pass by selecting nothing; the three commands name concrete nodes and pytest returns a collection error for an unknown node rather than a green zero-test run ([plan:273](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:273), [plan:470](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:470), [plan:799](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:799)).

- Contract coverage cannot pass over a deleted region: declared-but-missing and found-but-undeclared regions both fail, and every surviving region must sit whole inside a collected pin ([test_contract_coverage.py:720](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_contract_coverage.py:720), [test_contract_coverage.py:734](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_contract_coverage.py:734)).

- Task 3 Step 2 is not count-only in practice. `preamble_row()` is called throughout the exercised module, including fresh construction and resumed cases, so passing the module actually executes the changed fixture ([test_codex_round_evidence.py:211](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:211), [test_codex_round_evidence.py:333](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:333), [test_codex_round_evidence.py:675](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:675)). The unchanged count is a collection guard, not the sole oracle ([plan:623](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:623)).

**Verdict: FIX** — reject ranked numbers without a status-bearing heading, verify or remove the surrounding blank-line requirement, and make the trigger runner refuse missing or one-sided post-filter case sets.

**UNVERIFIED**

- The ten claimed checker executions have no retained artifact; only their description remains in the plan ([plan:1276](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1276)).
- Postimplementation static-check and dual-host suite results cannot be verified until execution.
- The session-store sweeps remain unreproducible from the reviewed files.