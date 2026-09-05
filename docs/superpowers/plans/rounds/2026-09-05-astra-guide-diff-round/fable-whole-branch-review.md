# Fable whole-branch review: c30a686..3990f9c

Range-bound artifact. Reviewer: `agents/fable-reviewer.md` (model fable), dispatched
2026-09-05 by the session over a controller-built package
(`review-c30a686..3990f9c.diff` and `.stat`, written to the session scratchpad,
outside the reviewed tree; merge-base c30a686, head 3990f9c, one commit). No frozen
plan and no SDD ledger exist for this range; the user's request was the spec. The
reply below is retained verbatim.

---

### Strengths

- Every Astra claim is attributed and bounded. The set opens by naming the page and fetch date and states that nothing in it is measured under `codex exec` (`C:\Users\Brandon\Documents\parallax\skills\multi-model-verify\references\model-prompting-notes.md:187-193`); each bullet uses "the guide says" with quoted phrases (`:196-198`, `:223-226`, `:240-241`, `:250-251`), and the `persistent_instructions` note keeps its "observation, not a measurement" label (`:219-221`).
- The precedence rule is stated once, in the intro, and pinned (`:179-180`; `C:\Users\Brandon\Documents\parallax\evals\multi-model-verify\test_multi_model_verify.py:1188-1189`). The two heading pins sit on single physical lines (`model-prompting-notes.md:185`, `:275`), and all five new assertions are positive `in` clauses that can go red.
- No contract markers were added or removed, so `DECLARED_REGIONS` is unaffected; the one pre-existing RAW-read pin on this section (`test_multi_model_verify.py:1158`) is untouched by the reflow. A sweep of `evals/` for the moved and deleted phrases finds no other pin on them.
- The Sol-era bullets are textually intact apart from two "Astra" -> "the reviewer" edits (`:281`, `:306`) and the removal of the non-interactive bullet (see Important 1). The closing note ties the new sentences to concrete brief sections (`:323-325`).
- Item 89 has the OPEN header shape the lint requires (Status, Cost, Pairs, Verified; `C:\Users\Brandon\Documents\parallax\BACKLOG.md:3834-3837`), is ranked in a group (`:55`), and its closure condition is concrete: one retained Astra round plus a behavioural-suite pass (`:3880-3888`).

### Issues

#### Critical

None.

#### Important

1. The non-interactive rule left the shared set, so a named-Sol round and the Kimi backup lane no longer carry it. Before this commit the "Non-interactive round, verdict required" bullet was model-neutral and sat in the one list every brief followed (diff `:207-219`). It now lives only under `#### Astra (the default lane)` (`model-prompting-notes.md:195-217`), while the intro says the Sol-era set is "the whole guidance set" when Sol is named (`:179`, `:279`) and lists only the tags, strike rule and final check as conventions that apply under both (`:180-182`). A Sol round under `codex exec` still has no one to answer a question, so the rule should apply there too; the pinned sentence itself still says "Every brief" (`:199-200`), which contradicts its placement under an Astra-only heading. The backup lane is in the same gap: `C:\Users\Brandon\Documents\parallax\skills\multi-model-verify\references\fallbacks.md:61` briefs the Kimi skeptic "with the same XML-style brief", and the intro's "both models" (`:182-183`) names Astra and Sol only, so nothing says which set a Kimi brief follows now. Fix: state in the intro that the non-interactive/verdict-required rule applies under every model, and name what the backup lane carries.

#### Minor

1. "Every Astra brief states ..." (`:199`, `:230`, `:256`) versus the Sol-era "Lean briefs, rules stated ONCE: ... later rounds REFERENCE them, never restate" (`:297-299`). The conflict rule says Astra wins, but the Astra set never says whether its three sentences go into every resume brief or only round 1, so the session decides per round. One clause resolves it.
2. Two claims about the transport are stated as fact without a measurement or a "guide's claim" tag: "`codex exec` passes none of the removed parameters" and "`configuration_update` ... has no `codex exec` surface" (`:270-273`). The rest of the set is careful about this; these two should be marked UNVERIFIED or cited.
3. "with the guide's exclusions carried as written" (`:244`) precedes a list that is paraphrased, not quoted, apart from two phrases. Either quote them or drop "as written".
4. Item 89's Cost line says "six instruction sentences" (`BACKLOG.md:3835`). The set has six bullets, but two of them (testing, parameters) put nothing into a brief (`:263-264`, `:266-273`), and the initiative bullet contributes a multi-sentence block. The count is a self-quoting figure that is already wrong; say "the Astra set's sentences" instead.
5. The session's description says only "tell Astra" changed in the Sol-era set; the Final check bullet also changed "asking Astra" to "asking the reviewer" (`:306`). Harmless, but the commit record should name both edits.

### Ledger minors triage

No SDD ledger exists for this range; nothing to triage.

### Assessment

Ready to merge: With fixes

The Astra set is faithful, attributed, and pinned in the red-capable forms, and no pin elsewhere breaks; the one thing to fix before merge is that moving the non-interactive rule under the Astra heading silently removed it from the Sol and Kimi briefs, which the intro's "Astra wins on conflict" rule does not address because it is an omission, not a conflict.
