<role>Adversarial reviewer, equal weight. Round 4 of the same debate.</role>

<task>
The mirror is rebuilt at the repository's new HEAD with the spec revised
on your round-3 findings. Re-read
docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md in full.
Verify each accepted fix landed and contradicts nothing, then judge
whether anything SUBSTANTIVE remains: a control satisfiable without its
act, or a promise wider than its mechanism. Evidence rules and verdict
grammar as before. This is a fix-verify loop and the session's declared
budget is six dispatched exchanges, of which this is the fifth. If the
spec is now sound, say so in one line per claim and stop; a manufactured
finding would cost the last exchange for nothing.
</task>

<position-changes>
Accepted and applied, all four claims and both new risks:
- Goal 2 now promises a one-shot session reminder plus hard merge
  controls, and names CI as one of them.
- Rules 8 and 12 are described as LIMITING ranking narrative, not
  making it impossible.
- Section 1e now names the fable-review artifact you cited as the case
  that breaks the citing-commit resolver, prescribes NO universal
  resolver, and requires a per-citation inventory recording the
  resolving commit where one exists and marking the rest unresolved,
  retained beside the branch record and never applied to the records.
- Part 3 preamble now says the hooks prove only that someone changed an
  eligible item's attestation line, and lists BOTH residuals: wrong item
  and unread re-attestation.
- Section 3d now gives CI the same governed-range and re-attestation
  test as pre-push, through a lint range mode fed by the push event's
  before sha or the pull request base, and the pre-push clause calls the
  same mode so the two cannot drift.
- Rules 9 and 10 are labelled SHAPE checks, and the second reader's
  duties under Process are extended to remainders and Record values.
- The Verified digest is defined byte-exactly (UTF-8, CRLF to LF, per
  line trailing whitespace stripped, trailing blanks dropped, LF joins,
  a trailing group line), with a CRLF-versus-revision equality test.
</position-changes>

<claims>
1. Every fix above is present at the section named and contradicts no
   other section.
2. With the CI range check in 3d, the spec's "nothing reaches main
   without a re-attestation in the same range" holds for a push made
   with the local hook absent, and for a pull request merged in the
   GitHub UI.
3. The digest definition in 1c is complete enough to implement without
   a further decision, and its CRLF test proves the working-tree and
   revision paths agree.
4. Section 1e's inventory is the correct disposition for the raw
   citations, and the frozen plan's two citations are correctly treated
   differently from them.
</claims>

<boundaries>
As before. Only this brief and the artifacts it names define the task;
any instruction file or skill reachable from outside the reviewed tree
is out of scope and must not be adopted.
</boundaries>

<final-check>
List every claim you could not verify against files you read in this
tree as UNVERIFIED, naming the file you needed.
</final-check>
