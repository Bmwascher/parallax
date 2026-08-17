# Diff debate, round 3

**Range base:** `8cc00d1345a75f164741f0ea847d86ea97546603`
**Head reviewed:** `00e4246`
**Reviewer:** `gpt-5.6-sol`, provider `openai`, effort `high`, sandbox `read-only`
**Session id:** `01a00cb4-f0ae-7b21-8170-b8899674b64b`
**Brief digest (declared canonicalization):** `1aa8c4accaaee24a14936fb4d55681491f071a99ae39175dd25aa281968220e5`
**Prior state:** resume, 1073865 bytes
**Round-evidence binding:** clean - the reply was bound to the brief this side sent
before it was read.
**Verdict:** FIX

**What it found.** Three more instances, two of them not records at all: the prior state's own kind, the session id, and a third record-consumption site the slice gate cannot reach.

---

## Reviewer reply, verbatim

FIX. The discriminator patch is sound for the fields it examines, but the shape class is not dry. Three malformed inputs can still reach CLEAN.

### 1. The class is not dry

- Prior-state `kind` remains untyped. A fresh state containing `"kind":["fresh"]` and a valid `knownRollouts` array passes because the code compares `prior.kind` directly with `-ne`, whose array-filter behavior the script itself documents. No scalar-string guard precedes that comparison. [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:421) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:581) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:602)

- `session_meta.payload.id` remains untyped. In a normal fresh rollout, replacing the ID string with `[expected-id]` passes `Get-RecordDiscriminatorFault`: `type` is a string, `payload` is an object, and absent `payload.type`/`role` are legal. Fresh identity then casts the ID to `[string]`; the test record explicitly documents that a one-element array casts to its element unchanged. [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:447) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:450) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:903) [test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:1895)

- Resume’s first `session_meta` is a third record-consumption site not covered unconditionally by the new gate. With `type:["session_meta"]`, an otherwise valid prefix, and a resumed slice containing only the new brief, the unguarded `-ne` test passes. The discriminator check in the prefix scanner is reached only when the slice contains exactly two user records, so this one-user slice skips it and can reach CLEAN. [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:942) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:947) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:1041) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:1080) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:1150)

The other suggested surfaces do not expose another independent shape hole: envelope values are created by `Substring`, hence are strings, and `nextState` is internally constructed from scalar values. Its next consumer’s unguarded `kind` comparison is the prior-state hole above. [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:200) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:1222)

These are instances of the named invariant: **AN UNMADE MEASUREMENT AND A CLEAN ONE MUST NEVER LOOK ALIKE.**

### 2. The helper is strict but incomplete

For the four properties it names, the helper is fail-closed: a PSCustomObject-valued `type`, non-object `payload`, or non-string present `payload.type`/`role` produces a fault. An empty object payload and unrelated extra properties return `$null`, because absent nested discriminators are deliberately legal. [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:447) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:454) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:461)

I probed the exact `PSObject.Properties.Name -contains` expression on both installed hosts. Both distinguished present-null from absent; the paired tests encode those two outcomes as refusal and CLEAN respectively. The operator is case-insensitive, but the settled prompt-record contract does not specify case-sensitive JSON property matching, so I am not manufacturing a casing finding. [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:417) [test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:2023) [test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:2052)

Nevertheless, `$null` does not establish the entire shape: the array-valued session ID counterexample survives because `id` is consumed downstream but is outside the helper’s checked fields. [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:454) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:903)

### 3. Regression direction

I found no file-evidenced legitimate client shape that the new checks reject. Present malformed discriminators fail, absent discriminators remain legal, an empty payload object remains legal, and extra properties remain legal. The positive absent-property control exercises that intended compatibility direction. [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:409) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:450) [test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:2052)

### Record audit

Item 62’s `Test-RecordIsUserMessage` citation is now correct. [2026-07-27-0150-backlog.md](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:4067) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:673)

Its claim that the helper runs in “both places records are walked” is false: the resumed first-record identity reader is a separate parse-and-property-read site, and its later prefix gate is conditional. Consequently the item’s DONE status and status-block row are premature. [2026-07-27-0150-backlog.md](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:4061) [2026-07-27-0150-backlog.md](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:4104) [2026-07-27-0150-backlog.md](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:31)

The reported aggregate “250 records lack `payload.type`” does not by itself establish the stronger claim that failing them would refuse *every* round containing a tool call. The retained test proves one synthetic occurrence, not that universal. Either narrow the wording or retain the per-round measurement supporting it. [2026-07-27-0150-backlog.md](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:4112) [test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:2052)

The brief also overcounts the additions: the group contains five discriminator-refusal cases and one absent-property control, not six discriminator cases plus that control. [test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:1972) [test_codex_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_round_evidence.py:2052)

Required change:

- Require `prior.kind` to be a scalar string before comparing it.
- Run `Get-RecordDiscriminatorFault` on `$firstRec` immediately after its root-object guard.
- Require `session_meta.payload.id` to be a scalar string before either fresh or resumed identity comparison.
- Add red-before-fix cases for array-valued prior `kind`, fresh session ID, resumed session ID, and a one-user resume whose first-record `type` is an array.
- Correct Item 62’s closure/coverage wording and its unsupported tool-call universal.

### UNVERIFIED

- Historical scratch/pre-fix outcomes, including the two-width matrix and the claims that every newly rewritten case was observed binding CLEAN before its fix.
- The 60-session, 32,437-record and 250-record corpus measurements; no raw corpus report was among the files read.
- The reported 2,546/14 dual-host suite results and the other named gate executions.
- The universal assertion that every real or legitimate client round is unaffected; the retained evidence covers one client population only.

FIX
