# Fable whole-branch review — parallax 0.14.4

Range: `f8bab1c..f9fd9b9` (branch `fix/harness-version-floor`)
Seat: `agents/fable-reviewer.md` (fresh subagent, read-only: Read/Grep/Glob)
Dispatched: 2026-07-27
Verdict: **Ready to merge — With fixes** (3 Important, 2 Minor, 0 Critical)

Raw reply retained verbatim below.

---

### Strengths

- The floor finding itself is real and correctly reasoned. The quoted changelog line (skills/multi-model-verify/references/panels.md:77-80) places the resume fix in Claude Code 2.1.216, so 2.1.216 as the floor follows directly from the cited source; the observation that both probes ran on 2.1.220 (agents/fable-panel-reviewer.md:26, panels.md:72) and therefore could not have exposed the pre-fix silent revert is exactly right — the original wording genuinely read as a platform guarantee it never had.
- UNAVAILABLE rather than degraded is the correct disposition. Below the floor the failure drops the model pin, the system prompt, and the tool allowlist in one silent step (agents/fable-panel-reviewer.md:27-33), leaving no signal on which a "degraded" mode could operate; and since Fable is never a panel's only cross-vendor lane (panels.md:14-19), declaring it unavailable can never strand the merge gate. The closing formulation — "a silently unpinned fully-tooled agent is not a weaker reviewer, it is a different one" (fable-panel-reviewer.md:31-33) — is the right containment argument.
- The floor was placed next to both claims it qualifies, not just one: the agent file's resume paragraph (fable-panel-reviewer.md:22-33) and panels.md's "agent death, which is loud" evidence-class paragraph (panels.md:66-80), with the test comments explaining why (evals/multi-model-verify/test_seat_reshuffle.py, per diff-package.txt:140-162). Tests-first was honored and the red-before-fix confirmation is claimed for all four pins.
- The fixture re-pin is substantively complete and correct: the new fixture carries the attribution header dated 2026-07-27 naming obra/superpowers (MIT) at version 6.2.0 (evals/multi-model-verify/fixtures/superpowers-code-reviewer-6.2.0.md:1-4) and both fingerprint literals ("Senior Code Reviewer" at :16, "Git Range to Review" at :28); all four declared sites updated (diff-package.txt:118-131, 174-216, 254-255). Grep confirms no live-code 6.1.1 path references remain except one comment (see Issues).
- The 7b0b904 correction is accurate. frozen-plan-format.md:84-87 does establish `docs/superpowers/plans/rounds/<date>-<topic>/` as the canonical tracked retention location, and the corrected text (docs/superpowers/plans/rounds/2026-07-27-rotation-guard/debate-record.md:112-120) both cites it correctly and correctly re-scopes "untracked by design" to `.git/parallax/` attestations/checkpoints, whose rationale (recording a verdict must not move the head it names) it states accurately.
- The floor's scoping to the panel lane only is correct: a grep of agents/ shows the resume surface is used only by fable-panel-reviewer (agents/fable-panel-reviewer.md:3,18-19); the whole-branch fable-reviewer and escalation seats are single-dispatch, and fallbacks.md's "resume" mentions are all codex/Kimi transport classes.
- plugin.json bumped 0.14.3 → 0.14.4 in its own commit (diff-package.txt:81-82), matching the repo's release convention.

### Issues

#### Critical

None.

#### Important

1. **Both new floor pins lock the descriptive half, not the operative half — the repo's own declared top defect class, reproduced inside the fix for a wording-overclaim.** In panels.md, the sole pinned string "Claude Code 2.1.216" (test_seat_reshuffle.py, diff-package.txt:162) lives in the bold header at panels.md:66. Everything operative comes after it: "Check `claude --version` before dispatching the Fable lane" (panels.md:73-74) and "the lane is UNAVAILABLE, not degraded" (panels.md:74-75) can be deleted while the pin stays green. Same shape in the agent file: both pins ("Claude Code 2.1.216", "silently reverted to the default agent"; diff-package.txt:148-149) sit in the descriptive sentences at fable-panel-reviewer.md:23-27, while the operative sentence — "The driver checks `claude --version` against the floor before dispatching this seat; below it, the Fable lane is unavailable rather than degraded" (fable-panel-reviewer.md:29-33) — is unpinned. This is pin-integrity instance 12 by the repo's own counting (nine in 0.14.2, two in 0.14.3, the last found inside a fix — precisely this pattern). Fix: add asserts on the check instruction and the disposition phrase in both bodies.

2. **The new panels.md text contradicts the panel-lane-loss class it invokes, and characterizes a failure condition outside fallbacks.md.** panels.md:75-76 says "a panel drops to its remaining lanes under panel-lane-loss," but the class itself (fallbacks.md:190-196) — echoed in the same file at panels.md:94-97 — mandates the opposite mechanics: "the panel stops at the consent gate, never continues automatically." Additionally, panel-lane-loss is defined for "a reviewer lane failing mid-panel" (fallbacks.md:192); a pre-dispatch version-floor unavailability is a different condition with no fallbacks.md home, and the binding rule is that panels.md must not define failure classes. This cycle added no fallbacks.md entry (grep confirms no 2.1.216 or floor mention there). Fix: reword panels.md:74-77 to route through the consent gate, and extend panel-lane-loss (or add a sibling class) in fallbacks.md to cover pre-dispatch floor unavailability.

3. **The diff package's exclusion note is false for commit 7b0b904.** diff-package.txt:66-69 justifies excluding `docs/superpowers/plans/rounds/2026-07-2[67]-*` as "retained round evidence... Not authored this cycle," but 7b0b904 (diff-package.txt:7) edits debate-record.md inside that glob this cycle — so a this-cycle-authored change is invisible in the package under a justification that does not hold for it. I verified the correction by reading the tree directly; a debate lane relying on the package alone could not. Fix: include the 7b0b904 hunk in the package (or amend the note to declare the authored edit explicitly).

#### Minor

1. **Fifth re-pin site missed:** hooks/superpowers-review-companion.ps1:4 still reads "the rendered code-reviewer.md template (superpowers 6.1.1)". The literals it names are unchanged in 6.2.0 so the hook behaves correctly, but the comment is now stale — and it is the very comment that instructs "Re-check the template after superpowers updates" (:6-7). One-line fix to 6.2.0.
2. The agent file states as fact that "the driver checks `claude --version`... before dispatching this seat" (fable-panel-reviewer.md:29-31); the only place instructing the driver to do so is panels.md:73-74. That instruction is currently unpinned (Issue 1) — once pinned, this cross-reference is sound; noting it so the dependency is on the record.

### Ledger minors triage

No SDD ledger exists for this cycle (no frozen plan — drift triage). The outstanding deferred minors on record are the 0.14.3 seeds:

- **Verifier self-contradicting warning text** (debate-record.md:138-141): ride — explicitly seeded for the next plan cycle, untouched by this range, non-blocking warning only.
- **Pin-mechanism structural question** (debate-record.md:98-103, seeded per :140-141): ride as the seeded cycle item, but note this range adds two more pins with exactly the class weakness (Issue 1), which strengthens the case for that cycle; the Issue 1 asserts themselves should land now, not wait for it.
- **Dismissed changelog lines**: concur on all seven. @-mentions/vim/statusline, slash-menu refresh, `name:` autocomplete prefix, and dataviz palette touch no parallax surface. PowerShell Unicode validation is harness-side; check-drift.ps1 and the statemachine suite run via powershell.exe directly. /verify + /code-review auto-run: parallax's hook fires on superpowers' Task dispatch fingerprint (hooks/superpowers-review-companion.ps1:27-29), not on built-in commands — dismissal correct. git/gh argument validation is the only one with any plausible surface (headless behavioral runs execute git), but that suite is opt-in, local, and self-evidencing, so riding is acceptable.

### Assessment

Ready to merge: With fixes

The floor claim, its disposition, the fixture re-pin, and the record correction are all substantively correct; but the two new pins reproduce the repo's dominant pin-integrity defect around their own operative text, and the panels.md routing sentence contradicts the fallbacks.md class it cites — both are small text/test fixes that should land before the mode-diff debate treats this contract as locked.

---

## Session adjudication (before Kimi round 1)

| finding | adjudication | evidence |
|---|---|---|
| I1 | **ACCEPTED, and worse than reported** | Verified. Additionally `Claude Code 2.1.216` occurs TWICE in panels.md (`:66` header, `:77` citation), so the pin did not lock even the paragraph's existence — deleting the whole floor leaves it green via the citation. Fixed by pinning the operative sentences plus a `count(...) == 1` on a phrase unique to the header. |
| I2 | **ACCEPTED** | Verified: `fallbacks.md:196` says the panel stops at the consent gate; `panels.md:97` repeats that rule 22 lines below the contradicting sentence. Added class `panel-lane-unavailable` to fallbacks.md for a lane the environment cannot host at all, distinct from one lost mid-panel; panels.md now routes to it and states no mechanics. |
| I3 | **ACCEPTED** | True by construction. Package regenerated: `debate-record.md` is now included, and the exclusion note states precisely which paths are omitted and why, naming the earlier note as false. |
| Minor 1 | **ACCEPTED** | `hooks/superpowers-review-companion.ps1:4` updated to 6.2.0; re-verified the file is still ASCII-only, which a separate pin requires. |
| Minor 2 | **ACCEPTED, resolved by I1** | The cross-reference is sound once the instruction is pinned, which it now is. |
| Ledger seeds | **RIDE** | Both remain 0.15.0 plan-cycle items; the reviewer's point that this range adds two more instances of the same class strengthens the case and is recorded. |
| 7 dismissed changelog lines | **RIDE — independently concurred** | Reviewer checked each and agreed with all seven. |

Application governed by checkpoint
`.git/parallax/application-checkpoints/20260727-021500-f9fd9b97e156.md`.
