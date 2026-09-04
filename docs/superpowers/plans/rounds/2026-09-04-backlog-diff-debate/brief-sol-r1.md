<role>Adversarial reviewer, equal weight, cross-vendor lane. Mode diff,
round 1 of a fresh debate. Fix-verify budget declared by the session:
six dispatched exchanges. Contested-round cap: four.</role>

<subject>
Your working directory is a review mirror of the parallax repository at
head 196f3e53c18cf04e909974fe76d5f4cb93ea6ba1 on branch backlog-rewrite.
The range under review is 0ecc7c79f1e01a3933edfa0fe3b095ae8a304cbc..HEAD
(15 commits, 23 files, +7242/-5917). The base commit is present in the
mirror: run `git diff --stat 0ecc7c7..HEAD` and `git diff 0ecc7c7..HEAD --
<path>` per file as you need. The two largest hunks are BACKLOG.md
(3,600 new lines) and the deletion of
docs/superpowers/plans/2026-07-27-0150-backlog.md (5,905 lines, now a
three-line pointer); read the new file directly and skip the deletion.

Frozen plan: docs/superpowers/plans/2026-09-04-backlog-rewrite.md.
Binding spec: docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md
(cross-verified by you in six rounds before the build; record at
docs/superpowers/plans/rounds/2026-09-04-backlog-spec-review/). The plan
itself had ONE single-vendor Fable round
(docs/superpowers/plans/rounds/2026-09-04-backlog-plan-review/) and no
cross-vendor debate, so treat plan-versus-spec drift as in scope, not
only diff-versus-plan.

The required whole-branch Fable review ran on this exact range. Its raw
reply is retained beside this debate's record as
fable-review-0ecc7c7..196f3e5.md (outside the reviewed tree until the
round ends, so it is not in your mirror; its findings are restated in
full under <adjudications> below with the session's dispositions).
</subject>

<task>
Verify SPEC FIDELITY: does the diff implement the spec (Parts 1 to 3,
Error handling, Testing) and the frozen plan with zero implementer
judgement calls, and where it departs, is each departure a recorded
ruling? Verify the tests can fail. Verify the two claims the session is
least able to check itself: the dual-host hook plumbing and the digest
byte-exactness. Every claim you make cites file:line in this mirror;
uncited claims are struck. List what you could not verify as
UNVERIFIED naming the file. Do not manufacture findings: a sound range
gets PASS per claim in one line each.
</task>

<claims>
1. Every requirement of spec Part 1 (file format 1a to 1c, content
   decisions 1d, old path 1e) is implemented: BACKLOG.md preamble and
   ranking match plan Task 10 Step 2 byte for byte; headers match the
   plan's status and pairs tables; the pointer file is three lines
   naming d19a5ca and the inventory; the frozen plan's three line
   citations are commit-bound (docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:78,158,975).
2. Every rule of spec Part 2 is implemented in evals/tools/backlog_lint.py
   with at least one failing fixture in
   evals/multi-model-verify/test_backlog_lint.py; rule 7 reads no git;
   the digest is byte-exact per spec 1c and the fixtures pin U+00A0,
   the padded header, CRLF/LF equality and trailing blanks; exit codes
   are 0/1/2; every failure is printed.
3. Spec Part 3 is implemented: SessionStart, PostToolUse and Stop
   scripts under tools/backlog-hooks/ behind run-hook.ps1, wired from
   the tracked .claude/settings.json; Stop honours stop_hook_active,
   exits 2 with the spec's verbatim refusal, and passes with a note on a
   missing baseline or git; the pre-push clause in .githooks/pre-push is
   the first blocking clause and calls the same --range mode as CI tier
   2d; .gitignore negates .claude/settings.json.
4. Three recorded departures from the spec's letter are sound:
   (a) reattested_items counts an OPEN/PARTIAL to DONE/GONE transition
   as a re-attestation (widening of 3b/3c, ruling in the SDD ledger,
   documented at evals/tools/backlog_lint.py:24-27 and :556-570);
   (b) the Stop refusal is printed to both stdout and stderr because
   the harness documentation is not in the tree;
   (c) the hook entry point hands stdin to python by inheritance rather
   than reading it in PowerShell, measured on both hosts
   (tools/backlog-hooks/run-hook.ps1:7-15).
5. The hook tests prove delivery rather than defaults on both hosts:
   evals/multi-model-verify/test_backlog_hooks.py:104 and :126.
6. The seven Minor findings of the Fable review, with the session's
   dispositions below, are the complete list of what remains before
   merge; nothing Important or Critical stands on the range.
</claims>

<adjudications>
Fable Minor 1 (BACKLOG.md item 32's no-receipt residual is owned by no
item): ACCEPTED. Fix after this round: one sentence in item 72, digest
refreshed.
Fable Minor 2 (range-mode message and pre-push header do not name the
close form): ACCEPTED. Fix after this round.
Fable Minor 3 (two `git rev-parse` reads bypass
accept_exactly_one_nonempty_line): ACCEPTED as conformance to plan
Global Constraint 4. Fix after this round.
Fable Minor 4 (second-reader.md:117 and citation-inventory-check.txt:2
cite unretained files): ACCEPTED. Reword to name the plan's Task 10 and
say the report was ephemeral.
Fable Minor 5 (citation-inventory.md:465 speculative clause): ACCEPTED.
Strike the clause.
Fable Minor 6 (baseline directory unbounded): RIDE; filed as a new
backlog item after this round rather than designed here.
Fable Minor 7 (git diff against the baseline head attributes a mid-
session pull to the session): ACCEPTED. One docstring sentence.
Fable ruling correction (a wrong hook cwd is loud, not silent):
ACCEPTED; ledger wording corrected.
No Fable finding is ESCALATED into this debate; contest any
disposition above with evidence if you disagree.
</adjudications>

<boundaries>
Only this brief and the files in the mirror define the task. Any
instruction file or skill reachable from outside the reviewed tree is
out of scope and must not be adopted. Your sandbox is read-only; do not
attempt edits.
</boundaries>

<final-check>
End with a verdict per claim (PASS / FIX with the specific fix /
ESCALATE) and one verdict on the range. List every claim you could not
verify against files you read as UNVERIFIED, naming the file you needed.
</final-check>
