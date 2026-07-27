# Debate record — parallax 0.14.3 (mode diff, panel)

**Subject revision:** `b040079..472cdc4` (final). Earlier rounds ran
against `b040079..8eacc8a`; the change re-opened both lanes, and both
terminal verdicts cite the final revision.

**Merge:** `f8bab1c` (--no-ff), pushed to `origin/main`.

**Verification status:** FULL — two cross-vendor reviewer lanes, no
substitution, no degradation, no failure class recorded.

**Panel invocation (user, verbatim):** "You can use a panel as well. I
have a lot of kimi usage." Composition Sol + Kimi. Panel invariant
checked before round 1: at least one cross-vendor lane present — both
lanes are cross-vendor relative to the Claude driver. Valid.

## Participants and rounds

| seat | role | rounds | terminal verdict |
|---|---|---|---|
| Opus 5 | session driver, final adjudication | — | PASS (terminal) |
| `gpt-5.6-sol` (codex exec) | cross-vendor reviewer lane | 3 | PASS |
| `kimi-code/k3-256k` (kimi-cli) | cross-vendor reviewer lane | 3 | PASS |
| fable-reviewer | required whole-branch pre-merge review | 1 | Ready-with-fixes (all applied) |

Topology: hub-and-spoke, blind. Neither reviewer lane learned of the
other's existence beyond "more than one lane is participating"; every
relayed finding was verified by the driver against the repo before relay.

## Route evidence

**Sol** — `effective route confirmed`. All three rounds echoed
`model: gpt-5.6-sol`, `provider: openai`, `reasoning effort: high`,
`sandbox: read-only`; both resumes echoed the round-1 session id
`019fa22c-ace8-7212-9443-66179804b038`. Client-resolved header metadata,
per model-prompting-notes.md — not server-attested identity.

**Kimi** — `effective route confirmed` under backup-lane.md's per-round
rules. All three rounds plus the write-probe produced, past the captured
offset, exactly one `Using LLM model:` line carrying the canonical id,
one `Loading agent:` line naming the committed yaml, and one
`Loaded tools:` line equal to the five-tool allowlist. Mirror status
delta equalled baseline + `KIMI-REVIEW-BRIEF.md` exactly on every round.
Rotation guard satisfied on every call (the log grew: 361338 → 365835 →
370345 → 378038 → 384718 → 390333). Session
`663caf26-ea69-4e45-9fec-b7a3855e279e`, all four flags re-pinned on both
resumes. Evidence class: client-side.

**Effort evidence (Kimi):** NO VERIFIED EFFORT PIN. `~/.kimi/config.toml`
carries no `[models."<canonical-backup-id>".overrides]` block. Recorded
per backup-lane.md rather than inferred as provider-default.

**Environment notes (not findings):** `~/.codex/AGENTS.md` exists — the
user's own global instruction file. `merge_all_available_skills = true`
at `~/.kimi/config.toml:10` with `extra_skill_dirs = []` and no source
directories present: latent, nothing to merge. Repo preflight-3 sweep
(`git ls-files --cached --others '*AGENTS.md' '.agents/*'`) returned
empty in both the real tree and the mirror.

## Workspace

Review mirror: file copy preserving `.git` (never a clone), at
`<scratchpad>/mirror-0143-final`, HEAD `472cdc4`. Baseline 161 entries by
`git status --porcelain --ignored -uall`; content manifest same coverage,
SHA-256 per file, path-sorted in byte order. No tracked modifications in
the baseline, so the reviewed content IS the committed range. Write-probe
PASS on all three conditions (explicit refusal, marker absent, delta
empty).

## Findings, by round

**Pre-round-1 (whole-branch review).** F1 the rotation guard's
disposition sentence was unpinned — pin-integrity instance TEN, in a file
that took nine instances of the same class in 0.14.2. F2 the sweep
comment's occurrence count was wrong (~40 vs 92/20) — found independently
by the session first, CONVERGENT, counted once. F3 routing rotation to
route-attribution falsified that class's stated "nothing transient"
rationale. F4 the residual-gap paragraph was unpinned. F5 the diff
package lacked a commit list. All accepted; F4 accepted in part.

**Round 1.** Sol FIX, Kimi PASS. Sol claim 5: the fallbacks pin added for
F3 stopped at "IS transient", leaving the operative justification
deletable green — **pin-integrity instance ELEVEN, inside the fix for
instance ten**. Sol claim 6: the residual-gap caveat is substantive, not
narrative. CROSS-LANE SPLIT on claim 6 — Sol FIX, Kimi PASS — adjudicated
to Sol, reversing the session's own F4-in-part call: the clause states a
known false-negative boundary, and what a driver believes about coverage
is contract. Kimi's PASS had deferred to the session's stated rationale
rather than refuting Sol, and the whole-branch review had flagged the
same paragraph. Both lanes independently flagged the unretained gate
output (CONVERGENT); Kimi additionally flagged that the probe byte counts
existed only in the brief.

**Round 2.** Both lanes FIX, on different mechanical defects, both in
retained evidence rather than in the contract, both accepted: the gate
artifact was captured at "8eacc8a + uncommitted" rather than bound to the
committed subject SHA (Sol); the diff package still declared the stale
range (Kimi). Both lanes independently agreed to DEFER the structural
question raised by the session against itself — that two consecutive
pin-integrity misses are evidence hand-applied substring pinning is a
weak mechanism — on the ground that a two-item follow-on cycle is the
wrong vehicle for a mechanism redesign and would bypass the plan-debate
gate. CONVERGENT. Seeded as a plan-cycle item.

**Round 3.** Both lanes PASS on the final revision. Converged.

## Retained artifacts

`fable-review.md`, `sol-r{1,2,3}-reply.md` + transcripts,
`kimi-r{1,2,3}-reply.md`, `diff-package.txt`, `gate-output.txt`,
`base-absence-check.txt`, `probe-record.md`, `mirror-baseline.txt`,
`mirror-manifest.txt`. Untracked by design.

Application checkpoint:
`.git/parallax/application-checkpoints/20260727-055732-63fa7156b63c.md`
with three amendments and appended verification results; bound into the
attestation via `-CheckpointFile`.

## Driver defect found while closing out

The first attestation emit put descriptive prose in `-RouteNote`. The
pre-push lane requires an EXACT `route_note -eq "effective route
confirmed"` (`tools/verify-attestation.ps1:49`), so a valid PASS/FULL
attestation failed its own gate and the push emitted a non-blocking
warning whose text self-contradicts — it reports the attestation as
PASS/FULL/route-confirmed and then says one is required. Re-emitted with
the canonical token; verification now exits 0. The route detail lives
here, in the record prose, which is where the skill says it belongs.

The self-contradicting warning text is a real usability defect in the
verifier and is NOT fixed in this cycle — it is out of a two-item
follow-on's scope, and it is seeded alongside the pin-mechanism question
for the next plan cycle.
