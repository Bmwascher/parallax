# Diff debate, round 1

**Range base:** `8cc00d1345a75f164741f0ea847d86ea97546603`
**Head reviewed:** `6023043`
**Reviewer:** `gpt-5.6-sol`, provider `openai`, effort `high`, sandbox `read-only`
**Session id:** `01a00cb4-f0ae-7b21-8170-b8899674b64b`
**Brief digest (declared canonicalization):** `14f1bd192eac17b987737cb6a7d5fdc3f6984d2cf8e28ae7cf32d9b954d752fe`
**Prior state:** fresh, 770 rollouts known
**Round-evidence binding:** clean - the reply was bound to the brief this side sent
before it was read.
**Verdict:** FIX

**What it found.** One blocking finding: a lead record whose content container and element kinds were never established binds clean. Spec fidelity, the baseline reroute, the 16 new tests and the record sweep all came back clean.

---

## Reviewer reply, verbatim

## Blocking finding

A malformed lead user record can bind clean without the script establishing the content shape promised by the contract. The contract requires `payload.content[]` elements whose `type` is `input_text`, then concatenates their `text` fields.[model-prompting-notes.md](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/model-prompting-notes.md:475)

Use this as the lead record, followed by a proper brief record:

```json
{
  "type": "response_item",
  "payload": {
    "type": "message",
    "role": "user",
    "content": {
      "type": ["input_text"],
      "text": [
        "<environment_context><current_date></current_date><timezone></timezone><filesystem></filesystem></environment_context>"
      ]
    }
  }
}
```

`Get-UserText` coerces the non-array `content` object into an array, permits the array-valued `type` comparison, and casts the array-valued `text` to a string.[read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:919) The repository already documents the underlying PowerShell member-enumeration class as allowing properties to read through an array whose shape was never established.[test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:1136)

The resulting envelope passes: it ends the canonical record, all three core names are present, and their empty values are deliberately not examined.[read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:294) Thus the record is reported clean despite `content`, `type`, and `text` not having their contracted shapes. This violates **AN UNMADE MEASUREMENT AND A CLEAN ONE MUST NEVER LOOK ALIKE**.

The defect predates the range—the same extractor is present at base `8cc00d1:tools/read-codex-round-evidence.ps1:819-841`—but it lives in the named verification surface and violates the same invariant, so the brief’s pre-existing-defect rule requires fixing it.

Required change:

- In `Test-RecordIsUserMessage`, require `rec.type`, `payload.type`, and `payload.role` to be scalar strings before comparing them.[read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:618)
- In `Get-UserText`, require `payload.content` to be an actual array; require every element’s `type` and `text` to be scalar strings; then compare `type` and append `text`.[read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:908)
- Add refusal tests for object-valued `content`, array-valued `type`, and array/null/missing `text`, with a well-formed control.

## 1. Spec fidelity

Apart from the blocking pre-existing defect above, I found no diff-to-plan drift.

- Kimi gains the separate trimmed canonicalizer and two-way mismatch diagnostic exactly where the plan requires them.[fresh-preamble-gate.md](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:302) [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:124) [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:903)
- The two scanner changes match the plan: `\z` anchors the field name, and the date is canonicalized before parsing.[fresh-preamble-gate.md](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:488) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:186) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:335)
- `Find-EnvelopeSpan`, the baseline reroute, the fresh predicate, and its placement are the planned implementations.[fresh-preamble-gate.md](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:827) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:223) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:1097)
- The contract addition, backlog closures, and version bump match the frozen close-out.[fresh-preamble-gate.md](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:996) [2026-07-27-0150-backlog.md](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:3712) [plugin.json](C:/Users/Brandon/Documents/parallax/.claude-plugin/plugin.json:3)

## 2. Can the fresh gate be reached clean without measuring?

Yes, through the malformed content/property shape above. Within a properly shaped content array, I found no bypass of the intended envelope measurement:

- Non-whitespace after the envelope is refused; characters removed by canonical `.Trim()` are deliberately invisible to the end test.[read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:105) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:303)
- Multiple proper content elements are concatenated in order without delimiters, so splitting an envelope across elements does not bypass scanning, and joined trailing text remains trailing text.[read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:908)
- A syntactically unusual name such as `_` is accepted when the core exists; a newline-bearing name is refused by `^[a-z_]+\z`. That is the planned openness rule, not a bypass.[read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:192) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:315)
- A repeated direct field is refused by the ordinal dictionary.[read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:196)
- Empty `current_date`, `timezone`, and `filesystem` values bind because fresh checks presence only and compares no values.[read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:327) This limit is disclosed in the shipped region.[model-prompting-notes.md](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/model-prompting-notes.md:549)
- The count rule runs first; brief uniqueness and last-position follow; only then does the fresh lead-record check run.[read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:970) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:980) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:1097) The existing `[brief, extra]` regression test specifically avoids count interception and pins the last-record refusal.[test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:467)

Non-user records remain unmeasured, but that separate channel is explicitly disclosed rather than claimed closed.[read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:618) [model-prompting-notes.md](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/model-prompting-notes.md:568)

## 3. Baseline reroute

The `Get-BaselineEnvelopeFields` reroute is behavior-preserving.

The base checks null/no-open, second open, missing close, and second close in that order, then extracts from the first open through the first close and propagates scanner faults (`8cc00d1:tools/read-codex-round-evidence.ps1:230-250`). `Find-EnvelopeSpan` preserves that order and arithmetic, and the rerouted caller preserves the old messages and scanner-fault wrapper.[read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:223) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:248)

The date canonicalization does intentionally change resumed behavior, but it is the separately authorized item-57 change, not a consequence of the span reroute.[read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:335)

## 4. Do the new tests test anything?

Yes. None of the 16 new assertions is incapable of failing.

| Test/property | What makes its assertion fail |
|---|---|
| Newline field name | Retaining `$` reaches the different closed-set message.[test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:1628) |
| Padded refresh date | Omitting canonicalization refuses instead of cleaning.[test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:1643) |
| Padded baseline date | Omitting canonicalization disables the refresh path.[test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:1656) |
| Invalid calendar date | An over-permissive parser makes the refusal fail.[test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:1670) |
| Novel lead text | Removing the new gate returns clean.[test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:1694) |
| Pre-envelope text | A too-strict envelope-only gate refuses.[test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:1705) |
| Envelope alone | Requiring pre-envelope instructions refuses.[test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:1718) |
| Text after envelope | Omitting the end check returns clean.[test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:1725) |
| Trailing whitespace | Checking raw rather than canonical text refuses.[test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:1737) |
| Missing core | Omitting the core loop returns clean.[test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:1747) |
| One-field envelope | An openness-only implementation returns clean.[test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:1762) |
| Unknown field | Applying the resumed closed set refuses.[test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:1770) |
| Two envelopes | Omitting uniqueness returns clean.[test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:1781) |
| Repeated field | Omitting duplicate detection returns clean.[test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:1792) |
| Fresh newline name | Restoring `$` returns clean on the open fresh path.[test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:1801) |
| Value not checked | Adding a value filter refuses.[test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:1811) |

Their shared assertions check parsed status, process exit code, and a reason needle.[test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:262) The output parser uses the strict single-line helper, which rejects blank-line padding.[exact_line.py](C:/Users/Brandon/Documents/parallax/evals/tools/exact_line.py:23) The mechanical checker covers only the documented discard-blanks/list-comprehension shape, and these assertions do not use it.[check_exact_line_oracles.py](C:/Users/Brandon/Documents/parallax/evals/tools/check_exact_line_oracles.py:38)

The amended `preamble_row()` is also live: it now produces a real two-element preamble through `real_preamble_row`, and the clean fresh control depends on that fixture reaching clean.[test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:105) [test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:152) [test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:305)

The tests are not vacuous; they simply omit the malformed container/scalar shape used by the blocking reproduction because every `user_row()` fixture constructs an array of objects with scalar string fields.[test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:90)

## Record sweep

The two numeric closing citations are correct: item 52’s `:105-110` identifies Codex canonicalization, and item 57’s `:192` identifies the `\z` check.[2026-07-27-0150-backlog.md](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:3712) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:105) [2026-07-27-0150-backlog.md](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:4052) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:192)

Item 52’s canonicalization and diagnostic claims match the Kimi implementation.[read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:128) [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:903)

Item 56 and the new contract region overstate the current implementation when they say the lead “record is checked by SHAPE”: the environmental string is checked, but the content-container and scalar-property shapes can remain unestablished and still bind.[2026-07-27-0150-backlog.md](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:3987) [model-prompting-notes.md](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/model-prompting-notes.md:543)

## UNVERIFIED

- I did not independently rerun the reported static gates, trigger evals, or two 2536-pass full-suite executions; I only read their retained ledger record, as the brief instructed.[progress.md](C:/Users/Brandon/Documents/parallax/.superpowers/sdd/2026-08-16-fresh-preamble-gate/progress.md:207)
- I did not independently inspect the private rollout corpus underlying the 658/767, 372-dispatch, or 60-of-60 empirical measurements; I verified only that the settled design and shipped contract record those limits.[fresh-preamble-gate-design.md](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-08-16-fresh-preamble-gate-design.md:55) [model-prompting-notes.md](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/model-prompting-notes.md:562)
- I did not independently reproduce the pre-branch control runs against the shipped 0.25.0 executable; I read their retained design and backlog records.[fresh-preamble-gate-design.md](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-08-16-fresh-preamble-gate-design.md:14) [2026-07-27-0150-backlog.md](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:3940)

FIX
