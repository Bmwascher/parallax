<round>2</round>

<result>
Your round 1 was strong and it moved the other lane. Two outcomes first, so you know where you stand.

YOU WON the per-call check argument. The other cross-vendor reviewer had recommended a new `-CheckSkillsEmpty` parameter set run before EVERY fresh and resumed call. I put your five arguments to it unattributed, along with my own verification that `tools/new-kimi-lane-home.ps1:902` is the ONLY site in the entire repository that writes to a debate-home skills directory. It CONCEDED, in its words: "I cannot name a shipped writer after construction. My proposed per-call guard was therefore against unknown or out-of-band mutation, not a measured writer." It adopted your builder-side postcondition instead.

It also partially REFUTED your argument 4, and I think it is right. You wrote that the effective surface is already pinned per round through hashes, toolCount and exact-list equality. It answered: those do not measure directory contents. If the selected directory became populated while `Skill` stayed denied and no prompt injection occurred, every one of those values could be unchanged. They catch changed effective context or client semantics, not silent filesystem content. Your conclusion survives, because without a writer the per-call check is still unjustified, but that particular support does not.

YOUR "the fourth root IS the flag" point was accepted by both of us. Neither the other lane nor I had seen it. It is now in the contract wording.
</result>

<split>
One thing remains split, and it is yours to defend or concede.

You wrote: "My replacement introduces no contract markers, so no DECLARED_REGIONS edit is needed; the pins become ordinary string asserts."

The other lane says keep both marked regions, using the two ids the frozen plan declares, and add both to DECLARED_REGIONS. Its argument, which I VERIFIED against the checker's own source before putting it to you:

An ordinary assertion of the form `"the entire paragraph" in body` detects edits INSIDE its literal. It does NOT detect ADJACENT weakening text. Someone can leave the pinned paragraph byte-identical and append one sentence after it, for example "This may be skipped when the driver considers the home trusted." Every ordinary membership assertion still passes.

A marked region supplies the missing boundary. `evals/multi-model-verify/contract_coverage.py:3` states that every marked region must sit WHOLE inside some pin string, and `:391-394` reports a region as UNCOVERED when what the pin contains is only a fragment. So a sentence appended INSIDE the region grows the region beyond the pin and coverage FAILS. And `test_contract_coverage.py:673-686` fails separately if the markers are deleted or renamed, so removing the region cannot silently disable its own coverage.

The four cases, laid out:
- ordinary pin only, weakening sentence appended: PASSES. The defect ships.
- marked region, same sentence appended inside the region: coverage FAILS.
- markers deleted, old text and its ordinary pin kept: DECLARED_REGIONS FAILS.
- region, pin and declaration all deleted together: only then does it pass, and that is three deliberate acts.
</split>

<questions>
<q1>
Defeat that argument or concede it. If you concede, say concede. If you defend, you must explain what stops the appended-sentence case, because that is the failure this repository's region machinery was built for and your proposal removes the only thing that catches it.
</q1>

<q2>
If you concede q1, your q2 and q3 replacement wording has to be re-cut to fit INSIDE two regions with the frozen ids `home-skill-root-disposition` and `home-skill-root-disposition-limit`, and each region body must be short enough that ONE string literal can carry it whole. Your q2 backup-lane replacement is currently one long paragraph and your q3 disposition is another. Give me the two final region bodies, complete and ready to paste, with the enumeration instruction and the reachability finding in the first and the limits in the second. No backslashes. Judge the length yourself and tell me if either is too long for one pin.
</q2>

<q3>
Your own unresolved point 1: you say suppression of the two PROJECT roots can rest on replacement semantics plus the client help text, without its own canary. The other lane draws the line harder: the live cells establish exclusion of `~/.agents/skills/` ONLY, and the help text is documentation, not measurement. Both of you then wrote contract text that differs on exactly this. Since a claim may not be wider than its evidence, and since the project roots are ALSO cleared by preflight-3 remediation in the mirror anyway, is there any cost to stating the narrow version? If not, why did you state the wide one?
</q3>

<q4>
Your unresolved point 4 asks whether the builder self-check needs its own pin and mutation test. The other lane says a fault seam can prove the detector's mechanics but CANNOT prove the shipped lane can produce the state it detects, and it would not present that mutation test as evidence that a threat exists. Do you agree that is the honest framing, and does the check still earn its place under it?
</q4>
</questions>

<constraints>
Answer only these four. End with anything still unresolved, and say plainly if nothing is.
</constraints>
