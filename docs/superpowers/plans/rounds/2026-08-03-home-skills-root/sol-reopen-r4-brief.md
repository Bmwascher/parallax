Round 4. A SECOND cross-vendor reviewer ran this same question cold, from the same brief, with no sight of your answers. It agrees with you on most of it and splits from you on two things. I am putting its arguments to you unattributed. Defeat them or concede; do not split the difference to be agreeable.

FIRST, it found a refutation neither of us made, and I think it is right.

Your round 1 refuted "suppresses all four roots" on evidentiary grounds: the project roots were never canaried. The other lane says the claim is worse than unevidenced, it is incoherent: `--skills-dir <debate-home>/skills` SELECTS that directory as the discovery root. Cell E confirms that root is discovered. So the flag cannot suppress all four roots, because the fourth root IS the flag's own target. What it suppresses is the OTHER THREE. Do you accept that, and does it change any wording you gave me?

SECOND, and this is the real split: the per-call emptiness check.

You said ship it, at the dispatch boundary, as `-CheckSkillsEmpty` on the home tool, before EVERY fresh and resumed call. The other lane says do NOT, and would instead put ONE assert inside the builder, at the moment it creates the directory, plus contract text that DESCRIBES the precondition as unverified per round. Its argument, in full:

1. There is no measured writer to guard against. The debate home is built once per debate; nothing in the lane copies anything into it; the only exception in the whole run was cell E's probe-only canary copy. A check for content nobody introduces guards a hypothetical.
2. The flag is the SECOND layer. The deny list closes the shipped lane. A per-round check would be a guard on the precondition of a backup control, which is third-order machinery.
3. This repo's own adjudication names its surviving defect class as "a check that passes either way". Every new check is a new false-clean surface that itself needs pins and mutation tests. Built to this repo's standard for a real guard, it is scope creep; built cheaply, it IS the defect class.
4. The effective surface is already pinned per round through hashes, toolCount and exact-list equality, and a client that changed discovery semantics would move those or break the version bound.
5. The builder is the ONLY writer of that directory, so one assert inside the builder is a self-check on its own act: near-free, fail-closed at the single moment content can enter, and it adds no per-round surface.

I VERIFIED point 5 myself rather than taking it. Grepping every `tools/*.ps1` for writes to a debate-home skills directory returns exactly one site, `tools/new-kimi-lane-home.ps1:902`, the `New-Item` that creates it. No other writer exists in this repo's tooling.

Answer these, concretely:

(a) Does point 5, now verified, change your recommendation? If you still want the per-call check, name the WRITER it guards against. "Something could" is not a writer; the repo's rule is that a claim may not be wider than its evidence, and that cuts both ways. If your answer is that the guard is against the unknown rather than the known, say so plainly and justify it against argument 3.

(b) Argument 3 is the one I find hardest to dismiss. A per-call check that nothing can ever fail is indistinguishable, on every run forever, from a check that is broken. How would you make it PROVABLY able to fail, given nothing in the lane writes there? A mutation test that plants a file is the obvious answer, but a mutation test proves the check works on a case the lane cannot produce, which is a weaker thing than it looks. Address that, do not restate the check.

(c) If you concede to the builder-side assert, does your `home-skill-root-disposition-limit` text change, and how? Give the revised sentences.

THIRD split: contract regions.

You put both new bodies inside `contract:start` / `contract:end` markers using the two frozen ids, and add both to `DECLARED_REGIONS`. The other lane says its replacement introduces NO contract markers, so no `DECLARED_REGIONS` edit is needed, and the existing three asserts at `evals/multi-model-verify/test_backup_lane.py:861-867` simply become ordinary string asserts on the new text.

The frozen plan declares two new region ids under "Fixed names and values", which is why you kept them. But a frozen plan can be wrong, and this one has already been wrong twice today. Which is right, and what does the repo actually gain from a marked region here that an ordinary pin does not give? Answer in terms of what breaks if the text is later edited without the tests being updated, because that is the only thing the region machinery exists to catch.

End with anything unresolved. If you concede a point, say concede, not "that is a fair point".
