# Mode-diff debate record — the home skills root probe

**Range reviewed:** `e94c0b5..2b0e1da`
**Terminal verdict:** PASS. **Verification status:** FULL.
**Rounds:** 5 cross-vendor, preceded by the required whole-branch review.

## Participants

| seat | model | transport | role |
|---|---|---|---|
| session | Claude Opus 5 | this session | position, adjudication, terminal verdict |
| whole-branch review | `agents/fable-reviewer.md` | subagent | required input to round 1 |
| reviewer lane | `gpt-5.6-sol` | `codex exec`, session `019fc98a-a780-78e3-8d7a-8467f21ad407` | cross-vendor adversarial review |

Route confirmed on every call, round 1 and all four resumes: `model: gpt-5.6-sol`,
`provider: openai`, `reasoning effort: high`, `sandbox: read-only`, and the same
session id echoed on each resume. Every round wrote fresh round-numbered reply
and transcript paths.

## Preflight

- `codex-cli 0.144.1`, `Logged in using ChatGPT`.
- Repo sweep `git ls-files --cached --others '*AGENTS.md' '.agents/*' '.kimi-code/*'`
  returned empty. No mirror was needed.
- Client context probe: `status: clean`, 29 advertised skills before and 0 after,
  `repo_scoped` 0, `plugin_cache_scoped` 0, `home_scoped` 29, override SHA-256
  `180f09f5...f432bb8`. The override hash was re-verified before each of the five
  dispatches.
- Environment note, not a stop: the user's own `~/.codex/AGENTS.md` exists and
  instructs the reviewer. A clean probe does not remove it.

## Artifacts

- Whole-branch review, range-bound, with per-finding session adjudications:
  `fable-review-e94c0b5-5b312d8.md`
- Application checkpoint, five amendments, all verification results appended:
  `.git/parallax/application-checkpoints/20260803T164113-5b312d883a83.md`
  (untracked by design)
- Execution ledger, D1 to D27: `execution-deviations.md`

## What each round found

| round | head reviewed | verdict | findings |
|---|---|---|---|
| whole-branch | `5b312d8` | with fixes | 0 Critical, 2 Important, 4 Minor |
| 1 | `5b312d8` | FIX | both Important diagnoses confirmed, **both of my proposed repairs refuted as still too wide**, plus a sixth claim-width instance, a test that cannot fail, a checker docstring wider than its code, and two unrecorded departures |
| 2 | `43e45ef` | FIX | 5, of which **3 were places a round-1 repair of mine fell short** |
| 3 | `9e7bd21`* | FIX | 2, both in ledger prose I wrote at round 2 |
| 4 | `9e7bd21` | FIX | 1, in the sentence I wrote at round 3 to repair round 2 |
| 5 | `2b0e1da` | **PASS** | none |

\* round 3 reviewed `a1f0ddd`; `9e7bd21` is the commit that applied its findings.

## Convergence

Everything converged. Nothing was escalated to the user, and no point was left
unresolved between the lanes. The finding count fell 6, 5, 2, 1, 0.

One judgment call was put to the reviewer explicitly rather than decided quietly:
whether the falsified write-site claim should also be corrected where it survives
in the frozen plan and in retained reviewer replies. The reviewer agreed it
should not. Each of those statements was true when written, before the seams
existed; the plan is frozen and the ledger is its correction channel; and
rewriting reviewer replies to match a later state would be rewriting evidence.
The line is between a dated record of a past measurement and a present-tense
claim about the code as it ships.

## The thing worth carrying forward

**Five of the repairs applied at this gate were themselves found defective by a
later round, and three of those were written by me.**

- My repair for "it measured the deny list" still attributed the null to the
  deny list.
- My repair for the locked region still said suppression was measured for "the
  other roots", plural, when one root was measured.
- My sweep paragraph, written to demonstrate rigour about overwide claims, said
  "three" while listing four artifacts, named a file that does not carry the
  claim, and omitted three that do.
- My repair for that said "nothing in the pipeline before the review would have"
  caught it, a counterfactual over every component.

By round 4 the response was to adopt the reviewer's wording verbatim instead of
paraphrasing it, and round 5 passed. That is the operational lesson: on this
specific defect class, a paraphrase of a correct narrower sentence is a fresh
draft, and a fresh draft is where the next overclaim enters.

The 0.19.0 cycle recorded the same shape at its rounds 41 to 47. It is now
observed on two consecutive cycles, which makes it a property of the work rather
than an accident of one branch.

## Gate evidence

Run in full after every application, at `43e45ef`, `a1f0ddd`, `9e7bd21` and
`2b0e1da`:

- `skill_lint.py --strict`, `skill_scanner.py`, `check_exact_line_oracles.py`,
  `run_trigger_evals.py` — all exit 0.
- `pytest evals -q` on **both** `powershell.exe` and `pwsh.exe` — 973 passed,
  13 skipped, exit 0, every time. 974 before this gate; the difference is the
  one deleted test.

The reviewer flagged as UNVERIFIED, correctly, that it could not rerun these
itself: its sandbox has no Python. Those results are the session's evidence, not
the reviewer's, and the verdict does not rest on the reviewer having checked
them.

## Note on the attested head

The final commit on this range adds only this record and changes no executable
file. It is included in the attested range so the attested head and the pushed
head match. The reviewed code range is `e94c0b5..2b0e1da`, and round 5 issued
PASS on it.
