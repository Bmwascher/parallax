Round 2. I verified your load-bearing claims against the repo rather than taking them; results first, then four points where I want you to push back or concede.

VERIFIED, and one of them is stronger than you stated.

- Claim 2 narrowing: ACCEPTED without reservation. C and D differ only in the flag with an EMPTY named directory, no cell exercises either project root, and no cell passes the flag at a POPULATED named directory. My "suppresses all four roots" was a claim wider than its evidence. I withdraw it.
- Unchecked precondition: CONFIRMED, and worse than "no parameter". `tools/read-kimi-round-evidence.ps1` contains the substring "skills" ZERO times in the whole file. It is not that the check is weak; the concept is absent.
- Builder: confirmed, `extra_skill_dirs = []` at :874 and the skills directory created once at :902.
- Stale pins: confirmed present in `evals/multi-model-verify/test_backup_lane.py` for "UNMEASURABLE", "unprobed territory", "claim nothing for it" and "indistinguishable". Tests change FIRST in this repo, then the text.

CORRECTION TO YOU, small but it matters for scope. "suppresses nothing observable" in `skills/multi-model-verify/SKILL.md` is NOT pinned by any test in `evals/multi-model-verify/` - I checked both `test_backup_lane.py` and `test_multi_model_verify.py`. So that sentence is unlocked today. Does that change your view on how much of the correction belongs in SKILL.md versus in `references/backup-lane.md`?

Four points.

POINT 1, and it is the one I most want you to argue rather than agree with. You describe the flag as a CONDITIONAL control with an unverified precondition, and stop there. I think the honest options are two, and I want your recommendation with reasons, not a survey:

  (a) DESCRIBE the precondition as unverified, exactly as you wrote it, and change nothing operationally.
  (b) REQUIRE a per-round check that `<debate-home>/skills/` is empty at dispatch, and only then call the flag a verified control.

This repo's governing invariant is that an unmade measurement is never a clean one, and its recurring failure mode - stated in its own handoff - is a check that cannot fail. Option (a) writes down that we know a precondition is unverified and then dispatches anyway, every round, forever. Option (b) costs one directory listing per call. Argue the strongest case AGAINST (b) that you can, then tell me which you would ship. If (b), say exactly where the check belongs: the validator, the builder, or the dispatch step in `references/backup-lane.md`.

POINT 2, a drift question about your own proposal. The frozen plan declares, under "Fixed names and values", exactly two new contract region ids: `home-skill-root-disposition` and `home-skill-root-disposition-limit`. You proposed `home-skill-root-disposition` and `skills-dir-conditional-control`. In this repo an implementer makes zero judgment calls and any departure from a frozen plan is drift, so a rename needs a reason that beats "it reads better". Either justify the rename as a substantive scope change or withdraw it. Note the frozen name carries the word "limit", which suggests the second region was envisaged as the LIMIT of what the disposition claims - which is close to, but not the same as, a region about the flag.

POINT 3, budget. `skills/multi-model-verify/SKILL.md` already fails its own lint budget: roughly 5120 tokens against a budget of about 5000, a standing warning on every run. Your proposed SKILL.md replacement is longer than the paragraph it replaces. Given `references/backup-lane.md` is REQUIRED READING before any backup round and will carry the full measured detail, what is the SHORTEST correct thing SKILL.md can say? Consider seriously whether the preflight-3 paragraph there should stop asserting anything about the flag at all and simply point at the reference file. Give me the exact replacement text at that length.

POINT 4, a readout you have not commented on, and I want it either adopted or refuted. `systemPromptChars` was CONSTANT across every cell: 462 for the reviewer agent, 1195 for the probe agent, across five separate throwaway homes, with the canary variously absent, present-and-unreachable, and present-and-loaded. That is a measured negative for a delivery path distinct from invocation: this client does not merge discoverable skills into the system prompt. It matters because the reviewer's deny list blocks INVOCATION but would not block INJECTION, so if the client ever started enumerating skills into the prompt, the deny list would stop being sufficient. Is that worth a sentence in the disposition region, and if so what sentence? Or is it a claim I cannot support from five cells on one client version?

Keep your reply to the four points plus any refutation of my verifications. End with the points you still consider unresolved.
