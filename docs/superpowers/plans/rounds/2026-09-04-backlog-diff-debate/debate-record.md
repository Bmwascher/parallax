# Backlog rewrite: mode-diff debate record, 2026-09-04

Subject: branch `backlog-rewrite`, base `0ecc7c79f1e01a3933edfa0fe3b095ae8a304cbc`
(the plan revision after its single Fable review), head moving as fixes
land. Spec: `docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md`
(cross-verified, six Sol rounds, record beside this one under
`2026-09-04-backlog-spec-review/`). Plan:
`docs/superpowers/plans/2026-09-04-backlog-rewrite.md`.

Lane: codex, `gpt-5.6-sol`, `model_reasoning_effort=high`, sandbox
`read-only`, one session `01a06e4e-9918-7390-9e45-734da4ff802b` resumed
across rounds. Fix-verify budget declared before round 1: six exchanges.
Contested cap: four. No round was contested.

Mirror: `C:\Users\Brandon\AppData\Local\Temp\kerev416`, rebuilt at the same
path with `-Force` before each round. Preflight found the repo's own
ignored `AGENTS.md`, so the mirror was built automatically; the mirror
enumeration was empty before every round; the client probe was clean each
time (31 home skills to 0; the global `~/.codex/AGENTS.md` present and
recorded; override sha `84d16007…`, written fresh per round as
`kerev416-r<N>.skills-override.txt`); the tool-surface probe was clean
before round 1 (dispatch_tools 0, node_repl silent, a mitigation not a
proof).

## Required Fable whole-branch review

`agents/fable-reviewer.md` on `0ecc7c7..196f3e5`: Ready to merge With fixes,
no Critical or Important, seven Minors. Raw reply retained verbatim at
`../2026-09-04-backlog-rewrite/fable-review-0ecc7c7..196f3e5.md`. Every
Minor was accepted and applied except Minor 6, filed as item 83.

## Rounds

| round | head reviewed | brief sha256 (first 8) | binding | verdict |
|---|---|---|---|---|
| Sol R1 (fresh) | 196f3e5 | 7b0023f5 | clean, sealed | FIX: 3 Important, 4 Minor |
| Sol R2 (resume) | 24ab582 | 17a69fe8 | **UNBOUND** (see below) | FIX (audit artifact only) |
| Sol R3 (resume) | a6c4431 | 547a2aa8 | clean, sealed | FIX on the round-2 record wording only; every claim and sweep otherwise clean |

Per-round files beside this record: `brief-sol-rN.md`, `reply-sol-rN.md`,
`receipt-rN.json`.

**Round 2 is not evidence.** The session wrote that round's prior-state
file through a shell `echo` that produced invalid JSON (single
backslashes in the rollout path). `-Prepare` sealed that file's hash into
`receipt-r2.json` without parsing it and the round ran to exit 0. The
binder then refused the sealed file. The session wrote a readable copy of
the same five fields (`prior-state-r2.json`; the sealed original is
`prior-state-r2.malformed.json`) and ran the binder against it, which
returned clean, and the session first recorded that as a clean binding.
Round 3 rejected that: the seal covers bytes the binder refused, and a copy
written after the round cannot prove it existed before dispatch, which is
the substitution the seal exists to refuse. So round 2 is UNBOUND, its
reply is retained as an audit artifact, and the fixes it prompted are
evidenced by round 3, which bound clean and verified each of them against
the tree. The dispatch-tool defect is item 85.

## Findings and dispositions

Round 1 (all accepted, applied in `24ab582`): (1) `git diff --name-only`
with rename detection hid a governed file moved to an ungoverned path from
Stop, range mode, pre-push and CI; (2) rule 10 accepted `..` and absolute
paths; (3) six OPEN bodies had lost citations and measurements the plan
said to keep; (4) `GROUP_RE` accepted `###Name`; (5) the preamble lacked the
commit and the inventory its closing paragraph; (6) a lone CR was folded by
universal-newline reads; (7) PostToolUse had no missing-git note. Rule
12's second clause is a recorded ruling (rule 3 is the single reporter), not
a fix.

Round 2 (applied in `a6c4431`, verified by round 3): whitespace-only
headers; preamble length; item 65's recorded loss; `stop.py` byte reads;
`run_behavioral_evals.py --changed` rename listing; the attestation
writer/verifier listing deferred to item 84; gate log to be retained at the
final head.

Round 3: the round-2 record wording, corrected in item 85, the ledger and
this record.

Application checkpoint (untracked, in the git dir):
`.git/parallax/application-checkpoints/2026-09-04T2140-196f3e53c18c.md`,
amended after each round.

## Close

(To be completed at the terminal round.)
