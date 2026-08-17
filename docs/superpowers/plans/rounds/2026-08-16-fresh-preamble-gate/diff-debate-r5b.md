# Diff debate, round 5b

**Range base:** `8cc00d1345a75f164741f0ea847d86ea97546603`
**Head reviewed:** `eb089ad`
**Reviewer:** `gpt-5.6-sol`, provider `openai`, effort `high`, sandbox `read-only`
**Session id:** `01a00cb4-f0ae-7b21-8170-b8899674b64b`
**Brief digest (declared canonicalization):** `efb389ba5b1401775c4b08342f6887b36dde900f251be2a9ab5aa628b4a50b4f`
**Prior state:** resume, 1998755 bytes
**Round-evidence binding:** clean - the reply was bound to the brief this side sent
before it was read.
**Verdict:** FIX

**What it found.** Two findings in the backup lane's binder. One was right about the defect and wrong about its consequence, and reproducing it uncovered a third that neither side had named: an empty byte sequence hashed one 0x00 byte.

---

## Reviewer reply, verbatim

The class is not complete. Two Kimi paths still reach CLEAN without making the measurement they claim.

### 1. Empty `turn.prompt.input` binds an empty brief

Concrete slice: take the valid fresh fixture’s sole `turn.prompt`, replace `input` with `[]`, and pass the SHA-256 of the empty string as `-ExpectedBriefSha256`.

`Test-TurnPromptShape` requires an array but not an element, so its loop executes zero times and returns true. [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:522) [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:525)

The record is then counted as the one required prompt; concatenating its zero elements yields `""`, whose hash equals the accepted empty digest. Nothing else requires a text element before CLEAN. [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:941) [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:1036) [test_kimi_round_evidence.py](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_kimi_round_evidence.py:166)

That is the vacuity class directly: no `input[].text` was measured, but the brief binding succeeds. The contract describes hashing the recorded prompt through its `input[]` elements, so the shape predicate must require at least one such element. [backup-lane.md](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/backup-lane.md:290) [backup-lane.md](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/backup-lane.md:293)

Required change: reject `input.Count -lt 1`, with a case using `input: []` and the empty expected digest.

### 2. The log parser can compare decoy fields before the selected marker

Concrete log slice: replace the valid `llm config` line with one line shaped as:

```text
provider=<expected> model=x modelAlias=<expected> thinkingEffort=<expected> systemPromptChars=<expected> toolCount=<expected>
... llm config ... provider=wrong model=wrong modelAlias=wrong thinkingEffort=off systemPromptChars=0 toolCount=0
```

The line selector counts it because it contains `llm config`. `Parse-LlmConfigLine` then applies an unanchored regex to the entire line, so it captures the expected decoy sequence before the marker rather than the mismatching fields following the marker. [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:992) [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:693) [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:695)

All subsequent provider, alias, effort, tool-count and prompt-length comparisons consume those decoy captures and pass. [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:1000) [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:1009) [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:1021)

The retained fixture establishes the intended ordering: `llm config`, then `turnStep`, then the configuration fields. [fresh-log.log](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/fixtures/kimi-round/fresh-log.log:1)

Required change: locate exactly one `llm config` marker and parse the marker-relative suffix, rejecting a missing/ambiguous marker or malformed suffix. Add the decoy-before-marker case above.

### Other results

The round-4 fixes are present: both external JSON roots use the raw-text object gate, wire `type` is string-guarded, and `config.update` rejects the neither-group shape. [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:362) [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:644) [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:648) [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:595)

The deviation from XOR is sound. With exactly two configuration records, a both-groups record contributes to both exact-one shape counts; the other record must therefore carry neither group to reach both counts as one, and that arrangement is now rejected at the shape predicate. [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:855) [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:870) [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:876)

The resume continuity fields are type-guarded before casts or comparisons: offsets must be nonnegative integers, and all four hashes must be strings matching the digest shape. [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:404) [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:415)

Both record corrections are accurate: Item 62 now points to the current function span, and the code comment states the per-session measurement rather than the struck universal. [2026-07-27-0150-backlog.md](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:4067) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:685) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:413)

### UNVERIFIED

- The reported pre-fix reproduction matrix and dual-host execution of the four round-4 cases.
- The reported literal-XOR full-suite failure.
- The private 60-session corpus figures.
- The reported 2,554/14 suite, 140-case Kimi module, static-tier and backlog-checker executions.
- The historical total of sixteen closed instances.
- The attestation tools; I did not inspect them because they are outside this branch’s declared change surface.

FIX
