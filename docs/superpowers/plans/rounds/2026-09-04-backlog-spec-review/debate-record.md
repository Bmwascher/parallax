# Backlog rewrite spec: Sol plan-mode review, 2026-09-04

Subject: `docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md`.
Lane: codex, `gpt-5.6-sol` / openai / read-only / effort high, one
session `01a06d76-dad5-71b2-99f5-77dfe29aa450` resumed every round.
Mirror: `kerev415`, rebuilt at each reviewed head with a fresh override
file; context probe clean every build (31 home skills to 0, global
`~/.codex/AGENTS.md` present and recorded, project AGENTS.md untracked
and ignored, removed in the mirror). Tool-surface probe clean before
round 1 (dispatch tools 0, `node_repl` silent).

Every round was prepared with `tools/dispatch-round.ps1 -Prepare`,
dispatched as a named background task, classified `reply-present` by the
wrapper's exit code, route-checked from the transcript header, and bound
with `tools/read-codex-round-evidence.ps1` (`sealed: sealed`) before the
reply was read. Briefs, replies and receipts are retained beside this
file.

| Round | Reviewed head | Result |
|---|---|---|
| R1 | `1973843` | 9 FIX, 1 PASS, 2 new risks |
| R2 | `0a41110` | VOID: binding refused, see `round-2-void.txt`; reply never read |
| R2b | `0a41110` | 3 FIX, 2 PASS, 3 new risks (repeat of R2's brief) |
| R3 | `d8a481a` | 4 FIX, 2 new risks |
| R4 | `611fa14` | 3 FIX (two the same finding), 1 PASS |
| R5 | `70fbdb8` | 3 FIX, all wording or definition, no new risk |
| R6 | `ceca5f8` | DRY: 3 PASS, UNVERIFIED none (confirming round, user-authorized) |

Session dispositions per round are in the next round's brief under
`<position-changes>`. Two of the session's claims were refuted on
evidence and are recorded there: the claim that no tracked document
outside the round records cited the old backlog by line (the grep was
piped through `head`), and the claim that a citing document's own commit
resolves its line citations (a raw artifact cites an intermediate tree).
Item 35 was claimed closed by construction and is not; item 34 was found
to own a finding the session had filed as new.

**Budget.** No fix-verify budget was declared before round 1, which the
protocol requires. The session declared six dispatched exchanges after
round 3; round 5 was the sixth. No exchange was contested. Round 5's
three fixes were applied at `ceca5f8`. The user authorized a seventh
exchange as a confirming round; round 6 reviewed that head and was dry,
so the debate TERMINATED on an adjudicated dry round with the spec at
`ceca5f8` as the reviewed text.

**Cost.** Eight dispatches for seven answered exchanges; the voided round
spent its quota because this side sealed a malformed resume-state file.
