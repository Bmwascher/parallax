# Confirmation round — revised 0.14.0 spec

Re-read `docs/superpowers/specs/2026-07-26-seat-reshuffle-design.md` (396 lines, revised). Verified each resolution against the revised text and the repo surfaces it touches.

## Resolution check — my nine findings

**B1 (Fable panel-lane contract) — RESOLVED.** The lane is now a named agent file (`agents/fable-panel-reviewer.md`, §2 line 28) with pinned tools (Read, Grep, Glob — no Bash, no writes; §6 line 133-134), a defined per-round evidence class ("dispatch metadata — the round-1 dispatch names the model pin; the resume surface carries NO model parameter… round continuity is evidenced by transcript recall", §6 lines 136-141), a named failure class routing into the single namespace (`panel-lane-loss`, §6 line 141, §7 lines 151-167), and a dated probe settling resume semantics (§15, lines 368-379). Contract tests pin the file, tools line, and both evidence sentences (§11 lines 287-290). The evidence class is honestly named and self-reported identity is explicitly excluded as priming-class (§6 lines 142-143) — matching the vocabulary discipline of `skills/multi-model-verify/references/model-prompting-notes.md:98-102`.

**I1 (fable-reviewer containment) — RESOLVED.** Bash dropped; tools are Read/Grep/Glob only, with the controller building the diff package (§3 lines 39-45), explicitly citing the 0.13.0 lesson that prose refusal under live tools is priming (the lesson recorded at `skills/multi-model-verify/references/backup-lane.md:21,44-51`). The exact tools line is test-pinned (§11 lines 283-286), and the referenced pattern file exists (`evals/multi-model-verify/test_flash_implementer.py`). PASS.

**I2 (lane-loss consent + record fields) — RESOLVED.** §7 is now consent-first: the panel stops at the consent gate, options are enumerated (continue / substitute via existing kimi machinery / abort), and the lost lane's findings carry into the record as OPEN (lines 157-167). §8 defines the status fields: FULL requires every lane's per-round evidence clean AND terminal verdicts bound to the final subject revision; post-loss continuation records class + consent mirroring the lane-substitution shape of `skills/multi-model-verify/references/frozen-plan-format.md:79-86` (§8 lines 233-238). PASS.

**I3 (Kimi-in-panel charter) — RESOLVED.** Panel participation is a sanctioned second entry route, added to backup-lane.md as its only edit (§6 lines 129-132, §9 lines 256-257), with user invocation as the consent and the write-probe explicitly required in panels (§6 lines 127-129) — consistent with `backup-lane.md:52-56`. The paragraph is test-pinned (§11 lines 300-301). PASS.

**I4 (escalation report) — RESOLVED.** §5 no longer claims to mirror implementer.md; it states the six sections outright, retains `DEVIATIONS` with its existing must-be-`none` meaning, and bounds judgment inside a plan-enumerated decision envelope that mode diff adjudicates against (lines 83-94). Consistent with the zero-judgment contract at `agents/implementer.md:30-36`. PASS.

**M1 (dispositioned vocabulary) — RESOLVED.** §4 now has the session adjudicating each finding with evidence in final-adjudication vocabulary, "deliberately NOT the application-checkpoint's 'dispositioned'" (lines 62-66), and the round-1 brief cites the retained range-bound artifact defined in §3 (lines 50-54). PASS.

**M2 (attestation grammar) — RESOLVED.** §8 lines 239-248 define the mapping (max lane rounds; participants name driver + every lane; strictest-lane rule for the `effective route confirmed` literal) with emitter and verifier unchanged — compatible with `tools/verify-attestation.ps1:47-49`; schema extension explicitly deferred in §14 (lines 361-364). PASS.

**M3 (private-repo claims) — RESOLVED.** §9 lines 259-261 name both instances — `CLAUDE.md:39` and `README.md:188` — and §11 line 310 pins "no 'private' claim remains." PASS.

**M4 (Kimi budget authority) — RESOLVED.** §13 lines 338-340 name the Kimi dashboard as the budget authority, matching the precedent at `skills/multi-model-verify/references/fallbacks.md:148-151` (reset horizon from the kimi.com dashboard). PASS.

**M5 (seat-table label) — RESOLVED.** §2 line 31 now reads "Claude tier — implementer.md (frontmatter default `sonnet`; haiku per dispatch)" — accurate to `agents/implementer.md:4,40-41`. PASS.

## New content reviewed

- **§6 subject-revision rule (lines 118-124)** — generalizes the existing post-fix re-review binding (`skills/multi-model-verify/SKILL.md:152-157,183-186`) and the freeze rule (`frozen-plan-format.md:92-99`) to panels; consistent, test-pinned (§11 line 298). PASS.
- **§12/§13 coverage split** — manual Sol+Kimi case plus attended Sol+Fable smoke exercises the new lane live while the manual case covers the already-proven transport; the reasoning is stated honestly (§12 lines 319-322, §13 lines 333-337). PASS.
- **§15 probe** — the probe shape (stored token, resume, recall check) matches the continuity concern and satisfies the probe-gate of `commands/intake.md:53-55`; no writes or planted instruction files, so the real-repo prohibition does not bite. Two minors below.
- **Existing pins** — the additive backup-lane.md paragraph does not disturb the pinned command/evidence strings (`evals/multi-model-verify/test_backup_lane.py:75-109`); the revised §4 pinned sentence keeps the single-line count==1 discipline. PASS.

## New findings (all minor)

**N1 (minor).** The §15 probe record omits the harness **version** — the project's probe-record schema requires "date, tool and version, the exact command or fixture, the observed result, and the claim it settles" (`commands/intake.md:56-59`). Every comparable record in the repo carries the version (e.g. "codex v0.144.1" at `model-prompting-notes.md:102-103`). One clause fixes it.

**N2 (minor).** §7's "continue with the remaining lanes" option (lines 161-162) does not state the recording consequence when the remainder has **no cross-vendor lane** (Sol+Fable panel, Sol lost, consented continuation = Fable-only). The standing machinery covers it transitively — a same-vendor bilateral debate is the DEGRADED skeptic mode (`references/fallbacks.md:56-63,164-177`), and §7 says the remainder is "recorded as such, not as a panel," so §8's FULL condition (lines 233-235) cannot apply — but one clause ("a cross-vendor-free remainder records DEGRADED per the bilateral rules") would close the reading that a consented Fable-only continuation could pass as FULL, protecting the §2 invariant (lines 34-35).

**N3 (minor).** §16 line 396 retains the advisory raw replies "in the session scratchpad" — the raw-rounds convention flags scratchpad transcripts as temporary and demands either a durable path or an honest "not retained" (`references/frozen-plan-format.md:73-77`). Reword or copy.

## UNVERIFIED

1. §15's tool-schema claim ("the resume surface carries NO model parameter — only recipient and message", lines 372-374) — I have no harness access; taken as a dated probe result on the record. Residual: the probe used a general-purpose subagent (line 369) while the lane uses a custom agent file; the no-parameter claim, if accurate, covers tool-grant and model-pin continuity alike, but I cannot confirm the schema claim itself.
2. The external guide fetches cited in §8 (Opus 5, Fable 5, Kimi; lines 177-225) — still no web access; content claims unverifiable from the workspace.
3. The §16 advisory-record session ids and route claims (lines 384-388) — outside the workspace; not independently checkable.
4. "The 0.12.0 precedent" for the single-driver debate record (§13 line 347) — not checked against the 0.12.0 record.

## Verdict

**SOUND-WITH-FIXES.** All nine prior findings are resolved in the revised text with resolutions that cite the correct repo machinery and hold up against the pinned surfaces; nothing previously sound was broken. The three remaining items are one-clause minors (N1-N2-N3), all cheaper to fix now than in the plan.

To resume this session: kimi -r 493c77f6-7a26-4139-a369-34a2126c0c04
