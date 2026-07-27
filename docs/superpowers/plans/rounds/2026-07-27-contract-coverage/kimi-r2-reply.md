# Round 2 — Verification of applied fixes at `18f948d`

Both documents re-read at their same paths. Position on the mechanism is unchanged from round 1; this round is verification of the three accepted corrections.

## A1 — Claim 11 count replaced with a selection rule: PARTIALLY LANDED — one residual

The replacement text at `docs/superpowers/plans/2026-07-27-contract-coverage.md:921-930` is verifiable and accurate in its new factual claims:

- "ten `###`-headed entries" — confirmed exactly: `skills/multi-model-verify/references/fallbacks.md:55, 65, 73, 84, 90, 100, 113, 190, 210, 247`.
- "Five entries name a class in backticks" — confirmed under the entry-identity reading: `fallbacks.md:73`, `:90`, `:162`, `:190`, `:210`. `missing-rollout` (`fallbacks.md:109`) is named *inside* the session-id entry, not by an entry of its own, so it correctly does not count.
- Both anchors are exact: `panel-lane-loss` is the `###` heading at `fallbacks.md:190`; `panel-lane-unavailable` at `fallbacks.md:210`.
- The selection rule (mark the two with recorded failures) replaces the total, as agreed.

**Residual:** the last sentence of the same paragraph — "The other nine get marked as they are next edited" (`...contract-coverage.md:930`) — is unchanged from the round-1 text and still encodes the invented total by arithmetic: two marked + nine others = eleven. It also contradicts the paragraph's own new shapes: under "ten `###`-headed entries," the unmarked remainder is eight, and there is no reading of the file under which "the other nine" derives from anything. This is precisely the decorative-number defect the amendment set out to remove, surviving in compressed form. **Fix: "The rest get marked as they are next edited."**

## A2 — "the operative sentence": LANDED, with a cosmetic leftover

The instruction body now reads "wrap only the operative sentence. The narrative sentences before it, and the changelog source note after it, stay outside." (`...contract-coverage.md:809-811`) — matching the exact one-sentence body at `:818-820` and the live text at `panels.md:73-77`. Leftover: the step heading at `:807` still reads "Mark the operative sentence**s** in panels.md" (plural). Trivial; the exact-body specification governs. Noting it so the record is complete, not as a gate.

## A3 — 529 → 633 with the glob named: LANDED

- `docs/superpowers/specs/2026-07-27-contract-coverage-design.md:33`: "Do not replace the 633 existing assert statements in `evals/**/test_*.py`."
- `...design.md:151`: "never has to search 633 assertions."
- `...contract-coverage.md:19`: same figure, same glob.

Consistency check from my seat: grep finds 640 lines containing "assert" across the five suite modules (`test_multi_model_verify.py:360`, `test_backup_lane.py:115`, `test_seat_reshuffle.py:61`, `test_attestation.py:60`, `test_flash_implementer.py:44`), so 633 assert *nodes* after excluding comment mentions is plausible — the exact node count requires `ast` and stays UNVERIFIED, but it is now scoped, sourced, and internally consistent. No remnant of 529 anywhere in either document.

## A4 / A5 — not acted on, reasons accepted

The instance-12 fixture merge (A4) and the absent weakening valve (A5) were notes, not findings; the stated reasons for leaving both alone are sound and on the record.

## UNVERIFIED (not folded into the verdict)

- The exact 633 assert-node count (requires `ast`; corroborated only by the line-level grep above).
- Round-1 UNVERIFIED items stand unchanged: the 172/40 string-constant counts, the lint/scanner/git prerequisite runs, and the historical blob contents at `4d8a121`/`8eacc8a`/`f9fd9b9`.

## Terminal verdict: **FIX**

One specific fix: `docs/superpowers/plans/2026-07-27-contract-coverage.md:930` — replace "The other nine" with "The rest." It is the last trace of the invented eleven, sitting inside the very paragraph amended to remove it. Everything else verified landed; my position on the mechanism, the six regions, the containment direction, and the task order is unchanged from round 1's ten PASSes. Once that one word is corrected, this is a PASS.

To resume this session: kimi -r 049ce8a8-b55a-4be2-a41d-d3d81104faba
