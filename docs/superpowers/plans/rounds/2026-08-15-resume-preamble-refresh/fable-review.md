# Fable whole-branch review — range 748df15..e54709a

Seat: `agents/fable-reviewer.md`. Dispatched 2026-08-15 by the session
driver, read-only, against the 15-commit branch range with the frozen
plan, the design spec, the SDD ledger and a controller-built diff package
as its inputs.

This is the REQUIRED whole-branch review that precedes the mode-diff
debate. The reply below is retained verbatim as the range-bound artifact
the round-1 brief cites. The session's per-finding adjudications are
recorded separately in the SDD ledger and in the debate record; they are
NOT edited into this file.

One transport note, so a later reader does not mistake it for the
reviewer's own wording: the subagent channel escapes angle brackets, so
`&lt;` and `&gt;` below are the reviewer's literal `<` and `>`.

---

### Strengths

- Fail-closed direction holds on every path traced. `Get-RefreshedPreambleFault` (`C:\Users\Brandon\Documents\parallax\tools\read-codex-round-evidence.ps1:251-311` region) returns either a named fault string or `$null` only after the complete rule passes: extra-record structure, closed set (`:259`), required core, baseline resolution, baseline date validity, per-field canonical hash equality, then both date bounds. Every baseline failure (no envelope, several, any scanner fault, missing or invalid `current_date`) returns a fault and lands on refusal; there is no input where a malformed baseline widens acceptance instead of disabling the structural path.
- The acceptance surface matches the design exactly. I traced the cursor by hand: two back-to-back envelopes, text around the envelope, tags with attributes, empty names, self-closing tags, uppercase names, nested same-name reopens, and an envelope-named inner field all refuse; the only accepted shapes are one envelope, five-field closed set, three required, no repeats, non-date fields canonically equal to the baseline, and a real `yyyy-MM-dd` date bounded by the baseline below and `[datetime]::Now.Date` above (`tools/read-codex-round-evidence.ps1:296-308` region). The contract text (`skills/multi-model-verify/references/model-prompting-notes.md:487-512`) states that same rule clause for clause.
- Direction naming is disciplined: the refresh and baseline wrappers nest so a bare phrase cannot pass on the wrong side, zero-envelope and several-envelope baselines say different things, and the nested-`&lt;cwd&gt;` acceptance case is a genuine discriminator for the cursor rather than a case a broken scan would also pass.
- The order move is behavior-preserving and fixes the direction it claimed: a `[brief, extra]` slice now refuses at "not the last user record" (`tools/read-codex-round-evidence.ps1:866-931` block, validated after the brief checks).
- The record is clean of the old rule. A repo-wide search of `skills/`, `agents/`, `commands/`, `tools/` and `evals/` finds no surviving present-tense identity-only description; the tool comment, the test docstring, the pin comment and the contract region were all rewritten to past tense in the same commit as the code (51b7d50).
- The ledger itself is unusually honest: it declares its own plan defects, the post-bump commit, and the seat choices, instead of leaving them for this review to discover.

### Issues

#### Critical

None.

#### Important

1. Behavioural evals were not run, and this branch edits skill contract text. `model-prompting-notes.md` is skill text, and the project rule is that skill/prompt changes get `python evals/tools/run_behavioral_evals.py` (the `--changed` form runs only cases whose declared surface intersects the diff and prints every skip by name). The ledger left this as an open question for this review; the answer is to run it, because "nothing behavioural reads this region" is currently an assumption, not a measurement. A `--changed` run that selects zero cases and prints the skip list is itself an acceptable measured answer. Must run before merge.

#### Minor

2. Ledger minor 1 CONFIRMED independently, and it is real. The tag-name regex `-cnotmatch '^[a-z_]+$'` at `tools/read-codex-round-evidence.ps1:176` runs before any name reaches the Ordinal dictionary (`:162`) or `$script:EnvAllowed -cnotcontains` (`:259`), so every name reaching them is already lowercase and deleting either `-c` or the Ordinal comparer would keep all 90 cases green. The case-variant refusals fire at the regex, yet the docstring at `evals/multi-model-verify/test_codex_round_evidence.py:1276` and the BASELINE_FAULTS row at `:1445` attribute them to ordinal closed-set matching, and the tool comments at `:160-161` and `:174-175` describe protections that never discriminate. The layers themselves are good defence in depth and should stay; the misattribution is a record defect in two docstrings and two comments. Fix before merge (comments and docstrings only, no behavior change): reword to say the regex refuses first and the ordinal layers are defence in depth behind it. Note the ledger cites the regex at `:154`; the current head has it at `:176`.
3. Two unobserved compound shapes refuse with oblique wording: two concatenated envelopes in a refresh report "carries '/environment_context', which is not a recognised environment field" (`:176` branch), and a baseline whose value contains a stray `&lt;/environment_context&gt;` reports "more than one environment preamble" (`tools/read-codex-round-evidence.ps1:228-230` region). Both land on refusal, both name the exact text found, and neither shape has ever been observed. Record and move on.
4. Exactly one commit lands after the version bump: e54709a (status-block fix) follows 4878a3a. The dispatch brief said two; the package's commit list shows 15c5fcb (item 55) landed before the bump, not after. The rule the bump-last constraint protects is intact because no `plugin update` has run, per the ledger. Record and move on, with one operational condition: do not run `plugin update` until the branch merges, since 0.25.0 already exists at a non-final tree.
5. Process, recorded by the ledger itself: the three builds went to plain general-purpose subagents rather than the repo's declared implementer lanes, and no gate noticed. No code effect on this range; it is evidence for backlog items 45 and 46 and should be cited there. Record and move on.

### Ledger minors triage

- Dead discriminators and misattributing docstrings: fix before merge — cheapest possible edit, and this repo treats a docstring that pins the wrong mechanism as a record defect (see Issue 2).
- Two long lines at `model-prompting-notes.md:487` and `:512`: ride — lint passes, the pin normalizes whitespace, and the file already carries a pre-existing 95-character line at `:530`.
- Commit message trimmed the module-path prefix from FAILED lines: ride — names and parameter ids are verbatim and the untrimmed form is in the report.
- Four-line section banner comment not in the plan text: ride — house style, no contract surface.

### Assessment

Ready to merge: **With fixes.** The code is sound: every failure direction I could construct lands on a refusal, the acceptance surface is exactly the design's, and the record matches the code throughout the range. Before merge, run `run_behavioral_evals.py --changed` (the one unrun gate this change class requires) and correct the two docstrings plus two comments that attribute the case-variant refusal to a mechanism that never fires; everything else rides.
