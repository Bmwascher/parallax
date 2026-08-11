Round 2. Same rules and verdict grammar. Ledger: 6 authorized, 1 spent,
this is unit 2, 4 remaining after it.

This is the FIX RE-REVIEW. Every finding you raised in round 1 was
accepted, and every one of the seven whole-branch findings I had already
accepted was applied alongside them. Nothing was refuted. The head moved,
so your round-1 verdict no longer covers it.

**New head:** `985ff7e` (was `28bfd07`). Run
`git diff 28bfd07..985ff7e` for the fix diff, or
`git diff 8ddda15..985ff7e` for the whole branch.

## Your ruling on the escalation, applied as ruled

`tools/check-drift.ps1` is UNCHANGED. `commands/doctor.md` is UNCHANGED.
The record and the narrowing landed instead:

- `CLAUDE.md` no longer lets its defective-form sentence read as a
  statement about the repo. It now says 0.23.0 fixed the SKILL.md dispatch
  ONLY, names both remaining sites, and points at the write-up.
- `finding-brief-encoding.md` gained a section headed "What 0.23.0 does
  NOT guard", naming three things: `check-drift.ps1:700` as LIVE and
  unguarded with no brief binding, `commands/doctor.md:70` as LATENT and
  ASCII-only, and the backup lane's argument path as UNMEASURED.
- Backlog item 30 closes the transport defect for this release and repeats
  the same three exclusions. Backlog item 31 is the open follow-up for the
  `check-drift.ps1` guard, and it records WHY it was not fixed here, citing
  the conjunctive rule and the unbudgeted state-machine suite.
- The application checkpoint states the narrowed certification unit
  explicitly: the documented multi-model-verify dispatch contract in
  `skills/multi-model-verify/`, EXCLUDING those two sites by name.

One correction to your round-1 mechanism, and it makes the defect
smaller rather than larger. The drift brief is written with `Set-Content`
and read back with `Get-Content -Raw`, both on the ANSI code page, so the
round trip is lossless for cp1252 characters and only the PIPE degrades.
That is ONE `?` per em dash there, not three. It is recorded that way in
both places. The absence of a brief binding is unchanged and is the part
that matters.

## Your four additional findings

**A. Sweep B was not the frozen product.** Rebuilt. Sweep B now
enumerates `4 keys x 3 presence x 5 forms x 3 escape placements x 2 line
endings = 360`, and a test asserts the product AXIS BY AXIS rather than
as a total, so a dropped axis names itself. Escape placement is its own
axis now instead of being folded into the form table. 16 cases sit
outside the product and are counted separately under an `X[` prefix, so
"how many cases" never has to mean "how many were specified".

Two readings the freeze does not settle, decided and recorded in both the
module and the plan rather than left implicit:

- `twice` crossed with form and escape means TWO occurrences of the SAME
  form and placement. A mixed pair is a different combination, and it is
  kept as a declared extra because it is the shape that separates
  counting labels from counting field lines.
- `absent` crossed with form and escape is degenerate: 30 of the 360
  cells per key render identical text. Generated anyway, because a
  quietly pruned product is a matrix nobody specified.

I also added a test that the escape axis NEVER changes a verdict. That
is rule 1 asserted over the matrix rather than trusted: 120 cells, each
with three placements, all three agreeing. If any triple disagreed, rule
1 would be false and the whole oracle would rest on something unwritten.

The rebuild changed which cases kill which mutants, which is the part
worth checking. Mutants 7 and 8 now die on `presence=twice` cells and
mutant 9 on a `presence=absent` cell — all three of them cells the 88-case
build could not generate. The full retained output is at
`docs/superpowers/plans/rounds/2026-08-11-budget-flake-generator/mutation-evidence.md`.

Counts, stated as two different numbers because they are: **498 generated
cases in 512 tests** (122 sweep A + 360 frozen sweep B + 16 extras, plus
10 mutants and 4 non-case tests).

**B. The upstream re-diff.** Performed. Upstream
`Shubhamsaboo/awesome-llm-apps`, path
`agent_skills/evals/tools/skill_lint.py`, fetched live 2026-08-11. Its
newest commit for that path is `ca8e5b3c56e51e336449a99d79b42b45ea690b86`,
dated 2026-07-09 — three days BEFORE this repo imported the file. Diffing
the imported copy at `acbf045` against current upstream gives exactly ONE
hunk: the four-line provenance header this repo substituted at import. The
body is byte-identical.

So the answer is that upstream has not moved. The header now records both
baselines, names the upstream commit, and says the statement is dated
rather than standing. The old "which was not fetched" sentence is gone,
and its pin was replaced rather than removed.

You were right that honest disclosure does not discharge a frozen task.
The reason is worth stating: the question the task answers is whether
UPSTREAM moved, and a local diff cannot answer it at all. The disclosure
was accurate and the step was still missing.

**C. The UTF-8 backlog entry.** Written, as item 30, carrying the
measurement and the three exclusions above.

**D. Retained mutation evidence.** Written, as `mutation-evidence.md`, for
all eighteen mutants across both modules. It states what it proves and
what it does not: that with one clause removed a NAMED case disagrees with
the frozen oracle, not that either parser is correct and not that either
matrix is complete. Each run stops after three killers per mutant, and the
file says so, so the lists are the first three rather than all of them.

## Your two claim-width rulings

**E. "5227 tokens".** Accepted and narrowed in both places it appears. The
constant block in `skill_lint.py` now opens by saying both numbers are in
the tool's own `len(body) // 4` estimate, that they are not tokenizer
counts, and that swapping in a real tokenizer would move every number
without changing what the gate does. Backlog item 19 carries the same
narrowing. The old sentence said the numbers were rebased "from the
measured body, not from an estimate", which was exactly backwards about
the word that mattered.

**F. "the only outstanding task".** Accepted. Task 8 is the only
outstanding FROZEN-PLAN task. At the head you reviewed, seven accepted
findings were also unapplied; at this head they are applied, and Task 8 is
again the only outstanding item — this time truthfully, subject to your
verdict here.

## Your generated-oracle ruling

**G. Three undeclared oracle fields, not one.** All three are now frozen
invariants 6, 7 and 8, in the module AND in the plan, both marked as
round-13 additions:

6. `BlockPresent` is TRUE iff at least one OPENER survives masking. A
   closer with no opener reports the container ABSENT. Presence is
   independent of ambiguity.
7. Entries are read ONLY from the body of an unambiguous single ordered
   pair. Every ambiguous arrangement reports ZERO entries even with a
   heading inside it, because ambiguity means there is no single body to
   read from.
8. The entry grammar as a truth table: one line,
   `- <name>: <description> (file: <path>)`; the file marker is the LAST
   such marker on the line, so a description mentioning `(file: x)` still
   parses and a path with parentheses stays whole; joined entries and a
   missing file marker are each MALFORMED and yield no entry; malformed is
   reported, never dropped.

A new test fails if any of the four declarations is removed, so this
cannot quietly revert. Both records state that NOTHING about the code or
the expected values changed — the rules had been left implicit, which is
the whole defect.

## The one thing I want you to attack hardest

I wrote the rebuilt sweep B, and I wrote the three invariants that
justify the values it now asserts. Both were written AFTER seeing which
values the parser produces. I believe invariants 6, 7 and 8 are
derivable statements about what the report MEANS rather than descriptions
of what the code does, and I believe every expected value in the rebuilt
sweep B follows from rules 5 and 7 of the route grammar alone. Those are
the two beliefs most likely to be self-serving. Check them against the
freeze, not against the code.

## Gates on this head

- tiers 1, 1b, 1c, 2: pass. `skill_lint` 0 errors, 0 warnings.
- `python -m pytest evals -q`: **2415 passed, 14 skipped in 496.53s**, up from 2123.
- Both mutation runs: 18 of 18 killed, 0 survivors, output retained.
- PowerShell dual-host: the same 2415 passed, 14 skipped under PowerShell 7 (440.75s). Both hosts, not one.

## Outstanding

Task 8 — twelve live behavioural runs against the INSTALLED plugin under a
rule predeclared before the runs — after the version bump and cache
update. Backlog item 18's result block reads `RESULT: pending` until then.

<final-check>
If you have no new substantive finding, say PASS and say explicitly that
this is an ADJUDICATED DRY ROUND closing the fix re-review. If you do have
one, say it plainly.
</final-check>
