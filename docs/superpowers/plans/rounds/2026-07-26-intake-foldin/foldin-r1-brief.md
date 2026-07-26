<role>Adversarial reviewer, equal weight, in a two-model re-review of a
pinned document edit.</role>

<task>commands/intake.md is whole-document hash-pinned: its clause-locked
tests catch deletion and negation but NOT additive contradictions, so ANY
edit requires a full-document adversarial re-review before the new pin is
accepted. Three additions were made (diff below; the PINNED_SHA256 line in
the diff is the mechanical pin update itself). Refute or confirm each
numbered claim.</task>

<rules>Read the full current documents at commands/intake.md and
skills/multi-model-verify/references/frozen-plan-format.md in this repo
(read-only). Cite file:line for every claim you make or contest; uncited
claims will be struck. Do not manufacture objections: if a claim stands,
say PASS and move on. End with PASS, FIX (with the specific fix), or
ESCALATE per claim.</rules>

<claims>
1. The `argument-hint: <reference url or path>` frontmatter line is a UI
   affordance only (dimmed hint text after the command name); it adds no
   behavioral rule and contradicts nothing in intake.md.
2. The appended sentence at the end of intake.md section 2 ("Sequencing is
   cost-aware: rank the dispositions first with needs-live-probe labels
   standing, and run probes only for the adoptions the user picks — an
   unpicked candidate never spends quota") is consistent with the whole
   document — in particular with section 2's rule that no runtime-behavior
   claim becomes rule text until a dated live probe settles it (probes
   still strictly precede adoption-into-rule-text; only their scheduling
   relative to the ranked scope pick changes), and with section 3's
   needs-probe disposition ("blocked on a probe not yet run").
3. The appended sentence in frozen-plan-format.md's Raw rounds paragraph
   ("The canonical retained location is
   docs/superpowers/plans/rounds/<YYYY-MM-DD>-<topic>/ next to the frozen
   plans — prefer it over ad-hoc paths...") states established practice
   accurately (rounds directories 2026-07-24-jinn-intake and
   2026-07-26-seat-reshuffle exist in-tree at that location) and, being a
   preference ("prefer", not "must"), contradicts neither the `not
   retained` honesty rule in the same paragraph nor the practice of
   keeping some diff-phase evidence intentionally untracked.
</claims>

<diff>
diff --git a/commands/intake.md b/commands/intake.md
index 268caf0..aeedae7 100644
--- a/commands/intake.md
+++ b/commands/intake.md
@@ -1,5 +1,6 @@
 ---
 description: Intake review of an external reference (repo, skill, article) for practices worth incorporating - untrusted-data discipline, delta grounding, probe-gated adoption, then the debate
+argument-hint: <reference url or path>
 ---
 
 Review the external reference the user named (URL or local path) for
@@ -61,7 +62,10 @@ conflicts with a live-verified parallax contract, the probe decides —
 never the authority or age of either document. Both directions happen:
 0.8.0's intake found one external claim provably wrong (never pin `-m`)
 and one right and critical (resume sandbox fallback) — only probes told
-them apart.
+them apart. Sequencing is cost-aware: rank the dispositions first with
+needs-live-probe labels standing, and run probes only for the adoptions
+the user picks — an unpicked candidate never spends quota (established
+by the 2026-07-24 jinn intake).
 
 ## 3. Dispositions, ranked, to the user
 
diff --git a/evals/multi-model-verify/test_multi_model_verify.py b/evals/multi-model-verify/test_multi_model_verify.py
index 0b8abc9..f0ef753 100644
--- a/evals/multi-model-verify/test_multi_model_verify.py
+++ b/evals/multi-model-verify/test_multi_model_verify.py
@@ -1663,7 +1663,7 @@ class TestIntakeCommand:
     # that: ANY edit to intake.md fails here until the document is
     # re-reviewed and the pin updated - tests-first, made mechanical
     # (same pattern as the drift watch's pinned superpowers fixture).
-    PINNED_SHA256 = "2a05942fc396c9e35555c69514364eb897c51d18c81b58ed29482f52de9256fc"
+    PINNED_SHA256 = "18c3bd98849887a8a73453811d28ba719ed52ffbb8784fde41bc724913e588d6"
 
     def norm(self):
         return " ".join(read(self.INTAKE).split())
diff --git a/skills/multi-model-verify/references/frozen-plan-format.md b/skills/multi-model-verify/references/frozen-plan-format.md
index eec4c9f..27d9191 100644
--- a/skills/multi-model-verify/references/frozen-plan-format.md
+++ b/skills/multi-model-verify/references/frozen-plan-format.md
@@ -81,7 +81,10 @@ verbatim reviewer replies live (scratchpad transcripts are temporary — if
 they were not copied somewhere durable, say `not retained`): the summary
 tables above are the adjudication, not the provenance, and a later dispute
 about what the reviewer actually said needs the raw text or an honest
-"gone".
+"gone". The canonical retained location is
+`docs/superpowers/plans/rounds/<YYYY-MM-DD>-<topic>/` next to the frozen
+plans (established by the 2026-07-24 jinn intake) — prefer it over ad-hoc
+paths so retention survives scratchpad cleanup by default.
 
 Lane substitution (backup reviewer): `Verification status: FULL` MAY
 carry a `Degradation:` class plus `Authorized by: user at round N` when
</diff>

<boundaries>The three additions' intent is user-approved and not under
debate; under review is their consistency with the full documents and the
accuracy of their practice claims. The pin update line is mechanical and
not under review. The gates already ran green (lint, scanner, trigger
evals, pytest 164/1; behavioral suite: no declared surface touched).</boundaries>

<final-check>List any claim you could not verify against files you read as
UNVERIFIED — do not fold unverified material into your verdict.</final-check>
