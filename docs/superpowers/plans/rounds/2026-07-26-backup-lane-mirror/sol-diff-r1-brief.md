<role>Adversarial reviewer, equal weight, in a two-model debate. You are not confirming my work; you are trying to break it.</role>

<task>Mode-diff verification of parallax 0.14.2, range c73ca2f48a91bef2c42ed4ae92613fb09026ab0a..5b976f7b8160fb153924562a265869a691972a16 (7 commits, docs and tests only). Refute or confirm each numbered claim below. The change edits CONTRACT DOCUMENTS that instruct future agents; the question is whether the instructions are correct, internally consistent, and honestly scoped — not whether code runs.</task>

<rules>
Cite file:line for every claim you make or contest; uncited claims are struck, not debated. You have read-only access to the repo at its current checkout, which IS head 5b976f7 — read the files directly.
Do not manufacture objections: if a claim stands, say PASS and move on. A sound change converging in one round is the expected outcome, not a failure.
End every claim with PASS, FIX (naming the specific fix), or ESCALATE, then ONE overall verdict line.
Severity: distinguish "this instruction will produce a wrong action" from "this wording could read better". Only the first is a FIX.
</rules>

<subject>
Range: c73ca2f..5b976f7. Verify with `git log --oneline c73ca2f..HEAD` and `git diff c73ca2f..HEAD`.
No frozen plan exists for this range. It is a rider: the defects came from a live Sol+Kimi panel run in a different repo (KitnEssentials) on 2026-07-26, plus one deferred finding from the 0.14.0 cycle. There is therefore NO spec-fidelity check to perform and no plan to drift from — judge the change on internal consistency and correctness instead.
This is not a port, so there is no reference source; claims ground in the repo's own files.
</subject>

<claims>

1. WORKSPACE MODEL. The Kimi backup lane's review workspace was specified as a `git clone`; it is now a file copy preserving `.git` ("review mirror"), because a clone carries tracked files only and review inputs are routinely gitignored — so a cloned workspace silently hands the reviewer a tree with nothing to review while every route and containment check still passes. Claim: this is a real defect correctly fixed, and the rationale in backup-lane.md:119-127 is accurate about what `git clone` does.

2. BASELINE CORRECTNESS. A file copy does not inherit the clone's empty-porcelain guarantee, so the real tree's untracked files and uncommitted modifications ride into the mirror and would quarantine every round. backup-lane.md:138-148 fixes this with a BASELINE porcelain capture, and backup-lane.md:155 makes the per-round check "BASELINE plus exactly the expected untracked set". Claim: the check remains EXACT — both halves are declared before the round, so nothing is adjudicated after the fact — and this is not a loophole that lets a driver excuse an unexpected delta.

3. BASELINE TIMING. backup-lane.md:138 captures the baseline "after construction AND after any preflight-3 remediation, immediately before the brief is written". SKILL.md:75-95 runs remediation between construction and the brief, and that remediation deletes entries and in the tracked case commits. Claim: the timing in these two files agrees end to end, and a baseline captured at any OTHER point would break a remediated debate. Attack the ordering specifically — an earlier version of this change got it wrong.

4. IDENTITY. backup-lane.md:156-162 records path + HEAD + baseline as the mirror's identity, states that for a file copy HEAD alone does not identify reviewed content, and requires mode diff to take the mirror from a tree whose tracked files are clean (disclosure only in other modes). Claim: this is sufficient to identify what was reviewed, and the mode-diff/other-mode split is drawn in the right place.

5. HONEST SCOPE OF THE CHECK. backup-lane.md:149-154 states the porcelain check is path-level, not content-level, and that the tool allowlist and write-probe remain the load-bearing controls. Claim: this is an accurate description of what `git status --porcelain` does and does not detect, and the contract now claims no more than it can deliver.

6. PREFLIGHT REMEDIATION. SKILL.md:75-95 tells a driver how to clear an AGENTS.md / `.agents` back-channel: remediate in the mirror, re-run the enumeration there, empty output is the evidence. It branches on tracked-ness — a tracked deletion shows ` D` and must be committed inside the mirror; an ignored/untracked deletion shows nothing, cannot be committed, and leaves HEAD unchanged, which SKILL.md:93 calls the CORRECT observation. Claim: both branches are factually right about git's behavior, and the tracked-case commit is justified by the correct consequence (SKILL.md:86-90 — a tracked modification left in the baseline bars mode diff and breaks HEAD-identifies-content).

7. OUTPUT-ENCODING CLASS. fallbacks.md:154-172 adds class `output-encoding` for a completed Kimi round lost to `UnicodeEncodeError` on a Windows console. It skips the retry (deterministic re-encode), recovers by RESUMING the surviving session with all four flags re-pinned and UTF-8 forced, and is explicitly neither route-attribution nor integrity because nothing reached disk. Claim: the disposition is correct on all three points, and filing it under either evidence-tainting class would have been wrong.

8. CONFIG SWEEP AND ITS EVIDENCE. backup-lane.md:74-110 adds a client-config sweep reading the effort-override block and `merge_all_available_skills` together with the SOURCES it merges from. Probed locally 2026-07-26 (kimi-cli 1.49.0): zero `overrides` blocks; key true at config.toml:10; `extra_skill_dirs` empty and no skill directories present. Claim: every assertion in that section stays inside what the probe supports, the populated-source case is honestly marked UNVERIFIED rather than waved through on the tool allowlist, and the section does not overclaim what earlier rounds ran at.

9. ARCHITECTURE INVARIANTS. fallbacks.md remains the single failure-class namespace and backup-lane.md defines none of its own; the backup model literal appears only in model-prompting-notes.md; the transport command placeholders carry no hardcoded model id. Claim: all three hold across this range.

10. TEST-LOCK INTEGRITY. Per this repo's rule, tests changed before the docs. evals/multi-model-verify/test_backup_lane.py pins the new contract text, and a new pin asserts the manual eval case in evals.json matches the mirror contract and no longer says "throwaway clone". Claim: each pin actually constrains what its comment says it constrains, and no pin is satisfied by text weaker than the claim it is supposed to lock. This is the claim I most want attacked — a pin that looks strict but matches loose text is invisible until it matters.

</claims>

<boundaries>
Already decided, not under debate: that these four items ship together in 0.14.2 (the user's scope call); the mirror-over-clone design itself; the decision to record rather than block on the two config-surface findings.
The required same-vendor whole-branch review already ran over this exact range across four passes and returned "Ready to merge: Yes". Its raw report is retained at docs/superpowers/plans/rounds/2026-07-26-backup-lane-mirror/fable-review.md (untracked by design so binding it would not move the reviewed head), SHA-256 246444485FF6A906456B10A0B09725D22DF4F00BB08D9E7D02C479286BCBF658. It found 2 Important and 5 Minor findings; ALL were accepted and fixed in-range, none refuted, none escalated. That review is same-vendor and is input to you, never a substitute for you. You may read it, and you are explicitly invited to disagree with any disposition in it.
One pattern from that review you should weigh rather than take on trust: three of its four passes found a defect introduced by the immediately preceding fix. Treat the most recently changed text as the least settled.
Verification suites on this head: skill_lint PASS strict, scanner 0/0/0, trigger evals all clear, pytest 170 passed / 1 skipped. Run nothing; you are read-only.
</boundaries>

<final-check>
List anything you could NOT verify against files you actually read, as UNVERIFIED. Do not fold unverified material into your verdict.
</final-check>
