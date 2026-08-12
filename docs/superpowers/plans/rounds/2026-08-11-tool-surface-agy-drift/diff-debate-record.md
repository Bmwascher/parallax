# 0.24.0 diff debate — record

Mode `diff`, over the branch `0.24.0-tool-surface-agy-drift`. This file is
a SYNTHESIZED STANDING RECORD and is read as current: superseded
conclusions are marked superseded in place with the adjudication that
replaced them. The `diff-brief-r*.md` and `diff-reply-r*.txt` files beside
it are VERBATIM ARTIFACTS and are never rewritten.

## Meters, declared BEFORE round 1

Written here before any round was dispatched, which is what makes the
declaration a control rather than a description.

- **Round cap: 4 CONSECUTIVE CONTESTED exchanges.** A round is contested
  while any contested point is OUTSTANDING, whether it was raised that
  round or earlier.
- **Total fix-verify budget: 4 units**, a SEPARATE meter from the round
  cap. Exhaustion PAUSES for user authorization; it never certifies.
- **Both authorized by the user in advance**, in answer to a question that
  named the alternatives (lean 2/2, standard 4/4, deep 6/6, or no
  cross-vendor rounds at all). The user chose 4 and 4.
- **Termination requires an ADJUDICATED DRY ROUND**: no new substantive
  finding AND no outstanding contested point. A reviewer PASS is never
  terminal by itself.

The plan-mode debate for this same branch is a different debate with its
own meters, which it exhausted at 6/6. Nothing carries over.

## Required input: the whole-branch reviews

Mode diff requires the Fable whole-branch review to run on the SAME RANGE
before round 1, its raw reply retained as a range-bound artifact, and the
round-1 brief to cite it with this session's per-finding adjudications.

| Artifact | Range | Verdict |
|---|---|---|
| `fable-review-1-ef428c3-5133f98.md` | `ef428c3..5133f98` | ready to merge WITH FIXES; 2 Important, 4 Minor |
| `fable-review-2-ef428c3-710d74f.md` | `ef428c3..710d74f` | ready to merge YES; 0 Important, 4 Minor |

Review 2 exists because review 1's fixes are NEW CODE and a fix gets no
discount: a review of an older head is not a review of this branch.

Adjudications: build checkpoint amendments 7 and 8. Every review-1 finding
was ACCEPTED and fixed. Of review 2's four, one was fixed, one was FILED as
backlog item 40 under the scope rule, one tightened an assertion, and one
was recorded as verified-by-reading with no change requested. The round-1
brief puts the two dispositions worth attacking in front of the reviewer
explicitly.

## Pre-dispatch controls, all measured before round 1

| Control | Result |
|---|---|
| Back-channel enumeration (`git ls-files --cached --others '*AGENTS.md' '.agents/*' '.kimi-code/*'`) | EMPTY. No mirror needed; the reviewed tree is the repo itself. |
| Reviewer context probe | `clean`, exit 0. `repo_scoped` 0, `plugin_cache_scoped` 0, `unknown_scoped` 0, `skills_after` 0 (from `skills_before` 29). |
| Global instruction file | `C:\Users\Brandon\.codex\AGENTS.md` PRESENT. Recorded, not a stop: nothing available removes it, and it survives a clean probe. |
| Skill-disable override | sha256 `180f09f50d282b5603f1c0d0621f2913ff66c8b7798e7a2f3b7fe8d41f432bb8`, 2313 bytes. Hashed INDEPENDENTLY of the probe's own report; the two agree. |
| Tool surface, pwsh 7 | `clean`. 133 baseline tools, `dispatch_tools` 0, `node_repl` present but SILENT. |
| Tool surface, Windows PowerShell 5.1 | `clean`, byte-identical result. Both hosts run because a green suite on one host proves one interpreter. |

**What the tool-surface result does NOT mean**, restated here because a
debate record is exactly where this gets over-read later: absence in pass 2
is a MITIGATION, never proof of removal, and the probe reads
`codex app-server` while the round dispatches `codex exec`, so it is a
PROXY for the reviewer's own surface. Item 39 carries the measurement.

## Rounds

(appended as they land, with the round-evidence binding verdict for each)
