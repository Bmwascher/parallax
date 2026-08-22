# Diff debate record — item 48 PowerShell 7 feasibility

**Mode:** diff. **Range:** base `a3134dc` (`git merge-base main HEAD`),
attested head `e7513f6`.

**Participants:** Opus 5 (session) / gpt-5.6-sol (reviewer, codex exec,
session `01a02b32-91ab-7e53-a0fb-c905bf304b4b`).

**Rounds used:** 6. **Outcome:** converged with amendments.

**Terminal verdict (session adjudication): PASS.**
**Verification status: FULL.** **Degradation: none.**

## Preflight

- `codex-cli 0.144.1`; `codex login status` → `Logged in using ChatGPT`
  (not a bare exit-0 API-key pass).
- Instruction back-channel enumeration
  `git ls-files --cached --others '*AGENTS.md' '.agents/*' '.kimi-code/*'`
  returned **empty**. No review mirror was needed.
- `~/.codex/AGENTS.md` exists and is the user's own global instruction file.
  Recorded, not a stop.
- Client context probe: `status: clean`, `skills_before` 29 →
  `skills_after` 0, `repo_scoped` 0, `plugin_cache_scoped` 0,
  `unknown_scoped` 0, `project_agents_md` false. Override written and
  verified at sha256
  `180f09f50d282b5603f1c0d0621f2913ff66c8b7798e7a2f3b7fe8d41f432bb8`, which
  every round re-checked as raw bytes before dispatch.

## Transport

Every round: effective route verified from the transcript header before the
reply was read — `model: gpt-5.6-sol`, `provider: openai`,
`reasoning effort: high`, `sandbox: read-only`, and from round 2 the same
`session id` echoed on each resume. Every round bound its reply to the brief
this side sent with `tools/read-codex-round-evidence.ps1`; **all six
verdicts were `clean`**, with the rollout byte offset advancing each round
(731444 → 977792 → 1157467 → 1481126 → 1726641 → 1768688), so no round
served a stale reply.

One dispatch failed before codex was invoked (a controller scripting error;
`pwsh` exit 64, no transcript, no reply, rollout untouched). It consumed no
round and no quota, and is recorded in the SDD ledger.

## Required whole-branch review

`fable-whole-branch-review.md` in this directory — the
`parallax:fable-panel-reviewer` seat, read-only, four exchanges over
`a3134dc..bfb018f`, terminal **PASS**. Its replies are verbatim, extracted
programmatically from the agent transcript. It returned FIX three times and
found the fifth, sixth and seventh instances of this branch's defect class.
The session adjudicated every finding with evidence before any reviewer lane
saw it; all were accepted, none refuted, none escalated.

## Rounds

| Round | Findings | What the round turned on |
|---|---|---|
| 1 | 8 | The eighth instance: retaining the whole-branch review changed the survey's input universe, so the record's published hit count was stale. The reviewer predicted the new count and its per-family split exactly, from a read-only reimplementation of `survey.py`'s logic. Also: my own branch-level spec-fidelity claim was wider than its evidence; the executable guard's comment was wider than its code for the third time; `first_difference` returned `None` for an added key; a wrong line characterization bound for the live backlog; a list that did not keep its own declared format; and one of my rulings overruled on both halves. |
| 2 | 5 | The ninth instance, inside the structural fix: the new convention claimed the survey's exit code makes `0 files not scanned` invariant, and the exit predicate never read `skipped`. A Rule 4 residual disposition rested on that non-invariant. Three self-referential figures the convention did not cover. My code fix moved four `run.py` citations. Spec fidelity on the list format was disclosed but not met. |
| 3 | 2 | The tenth instance, in content written to fix a different finding: a bullet naming the wrong test. And a list total that could not inherit the neighbouring commit binding, because at that commit the list held 50 entries, not 83. |
| 4 | 3 | The eleventh instance, in the sentence that states the rule: it mislabelled its own example and used an unbound live figure as that example. "Five dual-family rows" wrong by a factor of two — five pairs, ten rows. A new description claiming a test asserts parity when it deliberately breaks parity and asserts the gap is flagged. |
| 5 | 2, both non-blocking | **PASS.** The twelfth instance: the canonicalization rule said counts are "stated once, bound once"; the fix had synchronized duplicates rather than reduced them. Called non-blocking with its reasoning stated — every duplicate agreed, so no reader received a wrong number. Plus a navigation typo. |
| 6 | 0 | Confirming round after both non-blocking residuals were fixed anyway. **PASS.** |

**Twenty findings across six rounds. Every one was reproduced by the session
before being accepted. None was refuted.**

## What the debate changed structurally

Four fixes generalized rather than patched, each after a finding showed a
per-instance fix would not hold:

1. **Self-citations** name a section anchor, never a line number, because
   this record quotes its own line counts and every edit moves them.
2. **Every figure the record publishes about its own survey or tree** is
   commit-bound or an invariant, never a bare "is".
3. **`survey.py`'s exit predicate** gained `skipped`, so the invariant the
   convention claims is one the code enforces.
4. **Positional citations into files this branch edits** were converted to
   name-based anchors; zero `run.py:<n>` and zero `entry-points.tsv:<n>`
   citations remain.

## Residuals, in the reviewer's own words

None blocking. Recorded rather than buried:

- The canonicalization convention was narrowed at round 5 to what the
  document does — every mention carries or points at the same historical
  binding, so no two can disagree — rather than deleting the bindings. The
  reviewer confirmed at round 6 that the narrowed rule "honestly matches the
  document."
- Four things the read-only Claude-side seat could not execute and declared
  UNVERIFIED rather than letting a read stand in for a run: the survey run
  itself, the `gh`-derived CI evidence, the closing suite lines, and one
  external URL. Each is corroborated by an independent artifact or by a
  session measurement.

## Session adjudication

The reviewer's PASS is not terminal by itself. At the attested head I
verified independently: `survey.py` exits 0; the record has 11 `## `
headings and zero placeholders; the must-change list holds 83 bullets
against 83 TSV rows; the published classification command reproduces its
table; the residual-bucket `awk` reproduces 34 across 7 buckets; and the
verdict word is CONDITIONAL on five conditions.

**Terminal verdict: PASS.**
