# 0.16.0 mode-diff debate record

**Range:** `c6b7c85..b9ff705`, branch `0.16.0-backlog`.
**Mode:** diff. **Terminal verdict:** PASS (session adjudication, round 7).
**Verification status:** FULL. **Route:** effective route confirmed.

## Lanes

| lane | model | evidence |
|---|---|---|
| Required whole-branch review | `agents/fable-reviewer.md` | `fable-review-c6b7c85-efe4fa0.md`, run before round 1 over `c6b7c85..efe4fa0` |
| Primary cross-vendor | `gpt-5.6-sol`, effort high, sandbox read-only, session `019fa7a8-a3c5-73f2-b9ca-8f62bbed9e6c` | seven rounds, header route confirmed on every call, resumed id matched every time |
| Second cross-vendor (user-requested) | `kimi-code/k3-256k` with `--thinking`, session `b708b188-ccca-4909-8161-0d4c94bcad1c` | one round, block-attributed route evidence retained as `kimi-backup-lane-0160-r1-log-window.txt` |

The kimi lane was reviewed with no knowledge of the Sol rounds, deliberately.
It is the first round in this project recorded with a VERIFIED effort pin:
`default_effort = "high"` was added to `~/.kimi/config.toml` for the
canonical backup model before the round, on the user's instruction. Earlier
backup-lane rounds were recorded as having no verified effort pin, which was
true and remains true of them.

Containment before that round: write-probe PASS — explicit refusal, no
marker on disk, mirror status delta empty. Client config surface recorded:
`merge_all_available_skills = true` at `~/.kimi/config.toml:10` with
`extra_skill_dirs = []` and neither `~/.kimi/skills` nor `~/.kimi/agents`
present, so the surface is latent with nothing to merge.

## Rounds

| round | verdict | what it found |
|---|---|---|
| Sol 1 | FIX | BLOCKED classified as a deliberate handoff on a NONZERO exit; `-MaxAgeMinutes 0` stole a fresh lock without `-Force`; a future stamp wedged the lane; unlabelled locks were freeable |
| Sol 2 | FIX | The staleness env seam gated on the lock path being REDIRECTED, not on it differing from the default, so pointing it at the default path stole the real per-user lane; ownership tested by truthiness let `label: 0`, `null`, blank and absent through a bare release |
| Sol 3 | FIX | Age depended on how the instant was WRITTEN: a current `Z` stamp read 300 minutes in the future and was broken on sight, a five-hour-old one read as fresh; a non-string stamp threw and left the lock reading "held 0 min" forever |
| Sol 4 | PASS | Parse path, both display paths, record and contract agreed |
| kimi 1 | PASS, 3 minor | The behavioral runner still carried the `Write(**)` rule this branch removed as invalid; the record named a pre-existing scenario as newly added; a non-ASCII label was rewritten to `?` and stranded its own lane |
| Sol 5 | FIX | The colour fix WIDENED a hole: searching the whole output per field let an omitted header field be supplied by an agent-authored payload line, and global stripping manufactured header lines that never existed |
| Sol 6 | FIX | "Exactly once" counted only lines that PARSED, so a valid line plus a bare `model:` passed; the duplicate test used two valid values and could not reach the boundary |
| Sol 7 | PASS | Label counting exact, anchored and escaped; each new test confirmed to fail against the old code |

**Four of the six substantive rounds found a defect inside the previous
round's fix.** Rounds 2, 3, 5 and 6 each attacked a fix applied in response
to the round before it. Two of those defects were in code I had written
while reasoning about the wrong threat.

## Scope expansion, disclosed

Verifying the kimi lane's first finding required running the mutation-lane
behavioral case, because that finding narrows what the lane may write. The
run failed with an empty route header. Cause, reproduced immediately: codex
colours its startup header whenever `FORCE_COLOR` is set, a Claude Code
session sets it to `3`, and the runner's anchored regex could not match
through the escapes. The route check exists to fail closed on a WRONG route
and was failing closed on a COLOURED one, so every graded behavioral case
returned no verdicts regardless of what the agent did. The suite that grades
this project's behaviour was inert in the environment it is run from. Fixed
inside this release rather than filed, because the alternative was shipping
a permission change that could not be verified.

## Amber, not green

The mutation-lane behavioral case returned 4/4, then 3/4 on a later run of
the same code. The miss is the executor not re-reading files before
recording verification; the harness path — route matched, verdicts parsed —
worked in both. Recorded as run-to-run variance rather than a regression,
because nothing in this branch touches that contract. It is not claimed as
a green gate.

## Residuals carried forward

- A live lock holder past 45 minutes is breakable, because nothing checks
  liveness.
- Acquire is last-writer-wins, so the race is narrowed rather than closed.
- Two debates passing the same label are indistinguishable; the contract
  requires a per-round label and the script cannot enforce it.
- A foreign kimi session starting inside this round's sub-second startup
  block still truncates it and fails the round.
