# Diff debate, round 2

**Range base:** `8cc00d1345a75f164741f0ea847d86ea97546603`
**Head reviewed:** `7e8aa3d`
**Reviewer:** `gpt-5.6-sol`, provider `openai`, effort `high`, sandbox `read-only`
**Session id:** `01a00cb4-f0ae-7b21-8170-b8899674b64b`
**Brief digest (declared canonicalization):** `9901b1c78d2c039d84d21aa638e3cfef8c8b64045c93869f99548f35392cf80c`
**Prior state:** resume, 847668 bytes
**Round-evidence binding:** clean - the reply was bound to the brief this side sent
before it was read.
**Verdict:** FIX

**What it found.** Falsified this session's own round-1 refutation with a slice: the malformed record in the BRIEF position binds clean under the wide filter. Also showed two of the six new cases were not regression oracles.

---

## Reviewer reply, verbatim

## Blocking result

The `Get-UserText` half is correct, but the filter refutation is only positionally sound. A malformed kind-array record can itself be the expected brief and produce CLEAN. Item 62’s “fail-closed in every direction” conclusion is therefore false.

## 1. Fix correctness and completeness

Within `Get-UserText`, the fix completely establishes the content shape before scanning:

- `payload.content` must be an actual array.[read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:919)
- It must be nonempty, every member must be an object, and each member’s `type` and `text` must be scalar strings.[read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:928)
- Missing properties and null, array, scalar, or non-object alternatives return `$null` before comparison or append.[read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:935)

All four consumers handle `$null` fail-closed:

1. The brief-candidate loop excludes a null text; a malformed brief therefore produces no match and refuses.[read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:997)
2. The prefix-baseline call assigns null and breaks at the first user record; the later joint null guard refuses rather than adopting another baseline.[read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:1065) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:1088)
3. A malformed resumed extra record reaches that same joint null guard and refuses.[read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:1088)
4. A malformed fresh lead is refused directly as not text-only.[read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:1129)

So the applied fix closes the `content`/element-property class. It does not close the larger record-property class because array-valued discriminator fields still pass the user-record filter and can reach `Get-UserText` and the envelope scanner.[read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:618)

## 2. Refutation

The scratch measurement correctly refutes adding scalar guards only inside the filter: in its three-record arrangement, dropping the malformed middle record changes the count from three to two and permits clean. The counter-control constructs exactly that arrangement and pins the count refusal.[test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:1917)

But the conclusion that the current width is universally fail-closed is wrong. Consider this fresh slice:

```text
1. proper real preamble
2. response_item/message record with:
     role = ["user"]
     content = [{"type":"input_text","text":"Round one brief."}]
```

With the expected hash for `Round one brief.`:

- The current filter counts the array-role record as user; item 62 itself records that array comparison behavior.[2026-07-27-0150-backlog.md](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:4071)
- The fresh count is exactly two.[read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:987)
- `Get-UserText` accepts the proper content array, the second record matches the expected hash, and it is last.[read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:997)
- The proper lead passes the fresh gate, after which the script writes CLEAN.[read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:1114) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:1143)

A scalar filter would drop that malformed brief, leaving one user record and refusing at the count rule. More importantly, the contract says the binding candidate is a record whose `payload.role` is `user`, not an array containing that value.[model-prompting-notes.md](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/model-prompting-notes.md:475)

Therefore:

- The naive scalar-filter patch is unsafe for malformed middle records.
- The shipped broad filter is unsafe when the malformed record occupies a required position such as the expected brief.
- The complete solution is the one item 62 already sketches: validate discriminator shapes before filtering and explicitly fail malformed records, rather than making them invisible.[2026-07-27-0150-backlog.md](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:4093)

## 3. Six new cases

Four are meaningful; two do not test their claimed fix.

- Object-valued `content`: live. The old implementation bound clean, so the refusal assertion fails without the fix.[test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:1870)
- Array-valued `type`: live for the same reason.[test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:1877)
- Array-valued `text`: not a regression oracle for the shape guard. Its own docstring says the selected multi-element array already refused before the fix, while the assertion accepts the same generic `environment preamble` substring before and after.[test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:1888) Use a one-element array containing the full envelope; the pre-fix cast binds it and the new scalar guard refuses it.
- Null `text`: also not a regression oracle. With null as the sole text value, the old cast produced an empty lead, which already refused for carrying no envelope; the generic needle accepts both paths.[test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:1901) Put a null-text element beside a second valid-envelope element: before the fix null disappears and the envelope binds; after the fix the record refuses.
- Well-formed control: live; it catches an implementation that rejects all records.[test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:1909)
- Array-role counter-control: live for the specific unsafe scalar-filter-only patch.[test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:1917) Its exact count-message assertion will need changing when malformed records are correctly refused before filtering.

## Item 62 record

Item 62 has three record defects:

- Its citation `:618-624` does not cover the three comparisons. They are at lines 625, 627, and 628; the citation should be `:625-628`.[read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:618)
- “Widening this filter can only add refusals” is disproved by the malformed-brief slice above: widening supplies the required matching brief and changes refusal to clean.[2026-07-27-0150-backlog.md](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:4086)
- “Nothing is currently reachable through it” and the ranked-list claim that the shape is fail-closed contradict the item’s own first measurement, which records a malformed array-kind lead binding clean.[2026-07-27-0150-backlog.md](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:4077) [2026-07-27-0150-backlog.md](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:202)

Required changes:

1. Add explicit malformed-discriminator failure before constructing `$userRecords`; do not merely narrow `Test-RecordIsUserMessage`.
2. Add the malformed-expected-brief reproduction above.
3. Make the array-`text` and null-`text` cases red against the pre-fix extractor as described.
4. Correct item 62’s citation and replace its universal fail-closed claims with the position-dependent result: broad filtering can clean a malformed required record; narrow filtering can hide a malformed extra record; explicit failure closes both.

Non-substantive bookkeeping correction: the commit changed four tracked files, not three; it also added the retained whole-branch review, whose content still identifies the earlier `6023043` range.[fable-wholebranch-review.md](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-16-fresh-preamble-gate/fable-wholebranch-review.md:1)

## UNVERIFIED

- I did not independently rerun the reported 2542-pass dual-host suites, the 117-case binder module, static gates, trigger evals, or backlog checker; no corresponding exact-head execution record was present in the files read.
- I did not independently rerun the scratch-copy scalar-filter experiment or the two-host PowerShell type probes; I verified their recorded control flow against the source and tests.[test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:1921)
- The private rollout-corpus measurements and prior-round runtime reproductions remain independently unverified, as in round 1.

FIX
