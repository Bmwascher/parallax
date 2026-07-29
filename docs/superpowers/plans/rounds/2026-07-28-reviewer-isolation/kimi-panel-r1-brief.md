# Debate brief — parallax 0.17.0 "reviewer isolation" — mode diff, panel round 1

You are an independent cross-vendor reviewer in a hub-and-spoke panel. You
never speak to other reviewers. Reply to the driver only, in the verdict
grammar at the end of this brief.

## Subject revision (pinned)

- Repository: parallax (a Claude Code plugin, NOT a game addon).
- Base SHA: `e2e9242c6153d69e9a4f0c49055e7bf8c81a1dd0`
- Head SHA: `50c82029f178c747467e5a597b281731f70e4188`
- Your workspace is a REVIEW MIRROR of the head tree. `git rev-parse HEAD`
  in it reads the head SHA above. You have read-only tools
  (SetTodoList, ReadFile, ReadMediaFile, Glob, Grep). You have no shell.
- The diff for this range, excluding `docs/`, is in your workspace as
  `BRANCH-CODE.diff`. The `docs/` half is the frozen plan, the design
  spec, and the retained round artifacts; read those files directly at the
  paths below when you need them.

## What the change is

Before this branch, the skill's preflight step 3 enumerated instruction
back-channels (`AGENTS.md`, `.agents/skills/*/SKILL.md`) in the REVIEWED
TREE only. Every source that can hijack a cross-vendor review actually
lives on the REVIEWER'S OWN MACHINE: the codex client's home skills
directory and its plugin cache. The branch adds a client-side context
probe and wires it into dispatch.

Key artifacts:

- `tools/codex-context-probe.ps1` (new, 783 lines) — runs
  `codex debug prompt-input` twice, once as-is and once with skills
  suppressed, parses the two renders, and either BLOCKS or writes a
  VERIFIED OVERRIDE config file plus a JSON report.
- `tools/new-review-mirror.ps1` (new, 349 lines) — builds the review
  mirror, performs preflight-3 remediation inside it, captures the
  baseline and content manifest, and runs the probe.
- `skills/multi-model-verify/SKILL.md` — preflight 3 rewritten; both
  transport command blocks now carry a hash preamble plus
  `--disable plugins --disable apps -c $override`.
- `evals/multi-model-verify/test_codex_context_probe.py` (new, ~87 tests)
  and `evals/multi-model-verify/test_review_mirror.py` (new).
- Frozen plan: `docs/superpowers/plans/2026-07-28-reviewer-isolation.md`
  (read its `## Post-freeze amendments` section, A1 through A14).
- Design spec: `docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md`.

## The load-bearing invariant

**THE VERIFIED OVERRIDE IS THE DISPATCHED OVERRIDE.** The probe writes the
exact config bytes it proved produce an empty skills surface. Every
dispatch and every resume re-reads those bytes from the written file,
checks the SHA-256 against the probe's report, strict-decodes UTF-8, and
passes that in-memory value on the command line. A dispatch that verifies
one thing and sends another defeats the whole feature.

## The second rule

**Fail closed everywhere.** An unmade measurement, a failed measurement,
and an unreadable measurement are each never a clean measurement. A path
that lets any of those three read as `clean` is the single worst outcome
this branch can produce, and is a FIX at any severity.

## Session claims to verify or refute (each with evidence)

1. **Implementation fidelity.** The head tree implements the frozen plan
   plus amendments A1-A14, with no undeclared drift.
2. **Dispatch integrity.** The verified override reaches every codex
   invocation in SKILL.md unchanged, and a tampered or unreadable
   override file stops dispatch rather than degrading it.
3. **No false-clean path.** Within the probe's declared parser grammar,
   no input shape reaches a `clean` report without a successful
   suppression pass, an absent post-suppression skills block, a
   successfully written artifact, and validated artifact fields.
4. **Honest scope.** The branch claims to measure the reviewer's PROMPT
   surface only. It does NOT measure the reviewer's TOOL surface (MCP
   servers, tool-side plugins), and the documentation says so rather than
   implying full isolation. Check that no text in SKILL.md, the spec, the
   plan, or the README overstates the guarantee.
5. **Test integrity.** The new tests can actually fail. Look for
   assertions that pass vacuously, fixtures that do not exercise the
   claimed path, and any test whose literal no longer matches the code.
6. **Destructive or rejecting bugs.** `tools/new-review-mirror.ps1`
   deletes files and writes into paths derived from user arguments. Check
   path resolution, relative-path handling, `-Force` semantics, and the
   stale-artifact guard for anything that could delete the wrong tree or
   reject a legitimate run.

## Evidence rules (strict)

- Every claim cites `path:line` inside this workspace. A claim without a
  citation is struck without argument.
- Do not assert behavior you did not read. If you infer, say INFERRED.
- If you could not check something, list it under `## Unverified`. An
  honest gap is worth more than a confident guess.
- Do not propose refactors, style changes, or features. Defects only.

## Reply format

```
## Findings
(one numbered entry per finding: severity, path:line, what is wrong,
 what it lets happen, and the minimal fix)

## Unverified
(what you could not check, and why)

## Verdicts
1..6 — one of PASS / FIX / ESCALATE per numbered claim above

OVERALL: PASS | FIX | ESCALATE
```
