# Backup lane live proof — a real two-round debate over the kimi-code lane

Run 2026-07-31 as Task 11 Step 2 of the kimi-code swap. This is the run that
backlog item 15 requires before `kimi-cli` may be removed in a later cycle:
until it existed, the new lane had reviewed nothing.

**Client:** kimi-code 0.31.1, invoked by absolute path
`~/.kimi-code/bin/kimi.exe`, never a bare `kimi` off PATH.

## Subject

The diff `bce3a09..45f1e95` (Task 10 of this same cycle: retire the stale
failure routing and update the doctor), read by the reviewer from
`.superpowers/sdd/2026-07-31-kimi-code-swap/review-bce3a09..45f1e95.diff`
inside the mirror. That path is gitignored, which is the case the file-copy
mirror exists to carry and a `git clone` would have dropped.

## Isolation

- Debate home built ONCE before round 1 with
  `tools/new-kimi-lane-home.ps1 -Model kimi-code/k3-256k -Effort high`,
  under the session scratchpad, outside any git work tree.
  `KIMI_CODE_HOME` set on both calls. Removed with `-Remove` at the end.
- Mirror built with `tools/new-review-mirror.ps1`, exit 0.
  HEAD `45f1e95bf50a1240213d07e821cfb916e1ecf0c1`; baseline 184 entries;
  content manifest 184 entries; client probe `status: clean`
  (`skills_before` 29 → `skills_after` 0).
- Mirror status after EACH round, captured with
  `git -c core.quotepath=false status --porcelain --ignored -uall`:
  equal to the BASELINE EXACTLY, both rounds. Nothing was copied in, so
  "baseline plus nothing" was the declared expectation in advance.

## Client config surface (recorded, not a finding)

- `default_effort = "high"` — debate home `config.toml:22`.
- `extra_skill_dirs = []` — debate home `config.toml:2`, written empty by
  the builder, so it is the note the contract asks for rather than a
  finding about the home.
- `~/.agents/skills/` is NON-EMPTY: 27 skill directories. That root lives in
  the user's own home, is not relocated by `KIMI_CODE_HOME`, and nothing
  this lane runs removes it. Recorded as unprobed territory, per the
  contract, not as absorbed by the tool allowlist. Nothing was observed
  loading from it: `systemPromptChars` equalled the committed agent body
  exactly on both calls, which leaves no room for an appended skill.

## Order of operations

The prior-state file was written BEFORE the dispatch, never after. The
freshness rule rests entirely on a measurement taken before the call.

Round 1's prior state is the FRESH shape, with no offsets and no hashes,
because the session did not exist yet:

```json
{ "kind": "fresh", "knownSessionDirs": [] }
```

`<debate-home>/sessions` did not exist at capture time; the empty inventory
is a measurement of that, not an assumption.

## Round 1 — fresh dispatch

`kimi.exe -m <canonical> --agent-file <checkout>/skills/multi-model-verify/references/kimi-reviewer-agent.md --skills-dir <debate-home>/skills -p "<brief>"`,
working directory the mirror. Brief passed INLINE. Exit 0, 131.4 s.

- Printed session line: `To resume this session: kimi -r session_8b10300c-a698-4d65-81ce-b16bc93cc0f6`.
  The printed id is the session LEAF's name exactly.
- Brief: 1627 characters, SHA-256 (UTF-8, CRLF normalized to LF)
  `be229e50ca43ee2c8deb6fbe204c55d01ed32eb93111436b1e90f2083a762b69`.
- Validator, FRESH form (`-Fresh -SessionsRoot ... -SessionIdFromStdout ...
  -PriorState <the file written before dispatch>`; the session directory was
  DISCOVERED, not passed): **`status: clean`**, exit 0.
- Slice record counts, matching the measured two-class rule exactly:
  `config.update` 2, `tools.set_active_tools` 1, `llm.tools_snapshot` 1,
  `permission.set_mode` 1, `turn.prompt` 1, `llm.request` 7.
- Log line: `turnStep=0.1 provider=kimi model=k3-256k
  modelAlias=kimi-code/k3-256k thinkingEffort=high systemPromptChars=462
  toolCount=5`.

`systemPromptChars=462` is the COMMITTED agent body's length, derived by the
validator at run time. Nothing hardcodes it. The 431 in the earlier probe
record was the probe's own scratch agent file.

## Round 2 — resume

`kimi.exe --session session_8b10300c-... -m <canonical> --skills-dir
<debate-home>/skills -p "<rebuttal>"`, same working directory,
`KIMI_CODE_HOME` still set. `-m` and `--skills-dir` re-pinned, per the
measured resume-inheritance rule. `--agent-file` was NOT passed, because a
resume rejects it. Exit 0, 37.0 s.

- Rebuttal: 1719 characters, SHA-256
  `482ff3ea32edcf4c25bb1eb136406ed503aab322ee9ea72a384df614a911083d`.
- Validator, RESUME form (`-Resume -SessionDir <the path nextState names>
  -PriorState <the persisted nextState>`): **`status: clean`**, exit 0.
- It was validating ROUND 2's records, not round 1's, on three independent
  signs: the slice's log line is `turnStep=1.1` where round 1's was
  `turnStep=0.1`; the slice carries ZERO session-scoped records
  (`config.update`, `tools.set_active_tools`, `llm.tools_snapshot` and
  `permission.set_mode` all absent, which the validator itself requires);
  and the slice's own brief hash matched round 2's rebuttal, not round 1's
  brief.
- Slice record counts: `turn.prompt` 1, `llm.request` 1.
- The resume printed the SAME session id, so it continued the session rather
  than silently starting a new one.

## Hash continuity — nothing was rejected

Recorded here per the contract, because they are deliberately not pinned to
a literal in this repo:

- `toolsHash` = `3174a328b87a197903a223344c2acc973389f87147e3529a7185dc8d99678777`
- `systemPromptHash` = `f4410bdc723b724082088ba5b82ea44a108e6d84953b38d0288537334f2a048d`

Both identical across round 1 and round 2. The validator REQUIRED the match
on the resume and rejected nothing.

## Negative confirmation on live data

A freshness rule never seen to reject anything on real data is untested
where it matters. Round 2's validation was re-run against a prior state
identical in every field except that both byte offsets were zeroed:

```
{"status":"failed","reason":"prefix-replaced: wire.jsonl's prefix no longer hashes to wirePrefixSha256"}
```

Exit 1. The rule rejects on real data, and the offsets are load-bearing
rather than decorative.

## The debate itself

Round 1: PASS on four of five files, one Minor against
`fallbacks.md:140` — the `kimi-missing` class still detects with a bare
PATH-resolved `kimi --version`, which the lane's own text disqualifies as
evidence. `VERDICT: FAIL`.

Round 2 challenged the finding on scope, on severity direction, and on the
verdict. The reviewer CONCEDED scope (the line is outside the diff, cited
against the diff's own hunk boundaries) and CONCEDED the verdict, worked
both ambiguity directions separately and showed each fails CLOSED, and HELD
a narrowed form of the observation. `VERDICT: PASS (revised from FAIL)`.

So the lane produced a real bilateral exchange: it found something, defended
part of it, conceded the rest against evidence, and revised its verdict.
It did not simply agree, and it did not manufacture objections.

The surviving observation is recorded here rather than acted on: this task
does not edit `fallbacks.md`.

## Route line verified (client-side)

Every check above is client-side evidence. Server-side substitution is not
detectable from this class. What the two clean rounds establish is that
every round's evidence matched this lane's canonical declarations under the
contract's rules.

## Credential instrumentation — see the task report

The debate home carries a COPY of the real OAuth credential. Fingerprints
taken before and after this debate show the copy's tokens ROTATED while the
real file was never written. The full measurement, and what it does and does
not establish, is in
`.superpowers/sdd/2026-07-31-kimi-code-swap/task-11-report.md`.
