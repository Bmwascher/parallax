# Debate brief - round 3 - mode plan

Subject revision, pinned: the plan file at git blob
`44600c231e1f102f7d12b2797ba8254aaf4794c0`, commit `2f6dedf` on branch
`item51-inline-brief-transport`. Re-read it.

  docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md

Panel round. Findings are relayed anonymously and may be yours or the other
lane's. CONVERGENT means both lanes raised it independently.

## Disposition of round 2

Every finding below was ACCEPTED and applied. Nothing was refuted, nothing
struck. Each was verified against the repo by the session first.

CONVERGENT across both lanes:

- The verdict step gated on residuals collected in a LATER step, and no
  oracle withdrew the placeholder tolerance Step 1 granted. Steps are
  reordered so residuals are collected first; Step 4 now says explicitly to
  DELETE the placeholder line; a new Step 6 re-runs both gates and requires
  the placeholder grep to find nothing.
- `load_rows()` silently last-wins on duplicate keys. It now REFUSES
  duplicates, explicit and prefix alike. Exercised against five cases:
  duplicate explicit row, duplicate prefix row, unknown classification, the
  new `not-a-launch` value, and a legitimate two-family pair for one line.
- The scanner comment cited `.github/workflows/skill-evals.yml:70`; the
  `run:` match is at `:71`. Corrected.
- The named-parameter arm was inconsistent with the checks that read it.

Single-lane, verified, applied:

- The plan's own Architecture paragraph still said completeness "is
  enforced", and the record skeleton and scanner docstring still said "two
  regex families", while the code had three and called itself a filter. All
  three rewritten to say what the script does and three things it does not.
- The `docs/` exception named this plan as its reason but scoped itself to
  the record directory, which does not contain the plan. It now covers the
  plan file by name, AND is restated as a STANDING RULE, because Tasks 4
  and 7 create more matching files under the record directory afterwards
  and nothing re-applied it. Task 4 gains a step that classifies its own
  new files and asserts none is left prefix-covered.
- The named arm measured binding at the child while the parent still
  carried only `$args`. A `parent-named.ps1` with its own `param()` block
  now forwards its OWN bound values, `run_named` returns the SAME keys as
  `run`, records stage A, and `main()` is given verbatim rather than
  described.
- "Every shipped script declares named parameters" was false:
  `hooks/superpowers-review-companion.ps1:12-13` has no `param()` block and
  reads stdin. Narrowed to "most", with the counterexample named.
- The hook probe invoked the real hook with inherited stdin and no timeout.
  The real hook's first act is `[Console]::In.ReadToEnd()`, so the SUCCESS
  path would have hung with no oracle firing. Now `stdin=DEVNULL`,
  `timeout=60`, and a timeout is reported as a probe defect.
- Step 2b captured `git rev-parse --short HEAD` for a field reading "cut
  from `main` at". Now `git merge-base main HEAD`.
- "The ONLY one already running under PowerShell 7 in production" rested on
  the checkout while the plan itself says the installed cache is what runs.
  The step now requires either reading the cache and citing it, or writing
  the claim about the checkout only.
- Task 5's Linux command read about four lines of a job running from
  `.github/workflows/skill-evals.yml:16` to `:47`. Replaced with an awk
  range over the whole job; run here, it finds no `pwsh` invocation in that
  job at all.
- Task 6 called a module that INVOKES a script "proven behaviour". It now
  consumes Task 5's revision-bound successful run id, and writes
  "exercised, pass not evidenced here" where it has no green run to cite.
- Task 8 still asked for a sentence on how much of item 44's 57 minutes the
  change "would remove", after correctly saying net was undetermined. Now a
  gross upper bound only.
- The per-family split let a later task drop an earlier family's rows and
  still report green. Each family task now asserts every earlier family is
  still at zero, and commits its own rows.

## The narrowing, and what it cost

Round 2 asked whether the narrowing to invocation shapes dropped a real
entry point. Both lanes answered with live instances, and both were right:

- Call-operator through a VARIABLE: `tools/new-kimi-lane-home.ps1:152` and
  `tools/new-kimi-lane-login.ps1:214` run `& $LockScript @LockArgs` with
  the path assigned at `new-kimi-lane-home.ps1:96`;
  `tools/new-kimi-lane-login.ps1:442` runs `& $KimiBinaryPath "login"`.
- Flagless invocation in an instruction: `README.md:392` and `CLAUDE.md:41`.

Both shapes were added. Measured after: the added alternatives also catch
`evals/tools/drift_statemachine_tests.ps1:552`, which launches a HOST
through a variable - the dual-host harness itself, which no lane named and
no family previously saw.

The comment justifying the narrowing claimed the dropped lines "were prose
references that no migration would edit". That was a statement about 155
lines nobody had opened, and the counterexamples came from inside that set.
It now says the dropped lines were not read individually and claims nothing
about them.

Current counts from running the extracted scanner: 5169 matches, 4380 under
the `docs/` prefix row, 789 needing hand rows, split 120 host / 241 launch
/ 428 bare. A new `not-a-launch` class was added because some matches -
`tools/codex-tool-surface-probe.ps1:193`, `& $quote $_` - are function calls
through a variable and start no process, and forcing them into
`launch-nonhost` would put a false row in the inventory.

## What I want from this round

A. **Sweep the round-2 amendments for the class**, the same ask as last
   round and for the same reason: last round, seven of fifteen fixes
   carried the defect they were fixing. This round changed roughly twenty
   more things. Name each instance with a line reference, or report
   explicitly that you found none.

B. **The two new script files.** `parent-named.ps1` and the replaced
   `main()` are new code that nobody has executed. Read them as code, not
   as prose: wrong key names, a forward that does not forward, an arm that
   cannot fail, a `param()` block that binds differently than intended.

C. **The widened third family.** It now has seven alternatives. Does any of
   them match so broadly that a real entry point gets buried, or so
   narrowly that a shape is still dropped? Name an instance either way, or
   report none.

D. Anything else.

## Rules for your reply

- End with exactly one verdict line: PASS, FIX, or ESCALATE.
- If the plan is now sound, one line saying so is the right answer.
  Converging is the system working. Do not manufacture objections, and do
  not concede a point you can refute.
- Quote the line and give its number for every externally checkable claim.
