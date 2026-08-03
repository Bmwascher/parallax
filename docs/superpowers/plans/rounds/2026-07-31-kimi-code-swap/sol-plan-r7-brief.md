<task>Round 7. You named three things that had to be fixed before this plan could
freeze. All three are done. Re-read
docs/superpowers/plans/2026-07-31-kimi-code-swap.md. Evidence rules, verdict
grammar and boundaries as before.</task>

<applied>
Your three freeze conditions:

1. Fresh and Resume PARAMETER SETS. The validator no longer has one signature.
   Fresh takes `-Fresh -SessionsRoot <dir> -SessionIdFromStdout <id>
   -PriorState ...` and NO -SessionDir, because that is an output. Resume takes
   `-Resume -SessionDir <dir> -PriorState ...` and neither fresh-only argument.
   Crossing them is a parameter-binding error, not a runtime check.
2. The sessions root is now an input, so rule 3 can actually enumerate.
3. INVENTORY MEMBER DEFINITION. This was the best catch of the debate and it
   came out of my own retained probe record, which you read more carefully than
   I did. Measured topology is sessions/wd_<workspace>/<session-id>/, so a
   debate's FIRST call creates TWO new directories - the workspace container
   and the session inside it. "Exactly one new directory" would have rejected
   the clean first call of every debate. A member is now defined as a directory
   whose name begins `session_`, and nothing else; the wd_ container is never a
   member. There is a test case for exactly that shape, asserting clean.

Everything else you raised:

- New rule 2 requires PriorState.kind to equal the invocation's parameter set,
  failing `state-kind-mismatch`. Neither the shape check nor the consistency
  check stated that equality.
- Validator rules renumbered 1-16; my insertion had produced a duplicate 4.
- Rule 7 states that a fresh call's offsets are zero so rules 8 and 9 are
  skipped, and the cross-references were corrected with the renumber.
- Substituted-drive test: select an unused letter rather than hard-coding X:,
  verify the mapping resolves to the intended temp directory BEFORE planting
  anything, skip the branch loudly if either step fails, and unmap with
  `subst <letter>: /d` in the finally.
- Added the ancestor-of-profile case; equality alone never exercised the "or
  above it" half of the production rule.
- Task 9's test docstring no longer claims discovery. It now says the entries
  are removed because they are READABLE - measured - and states that whether
  this client would ever discover them is unverified and that the sweep does
  not depend on it.
- The contract no longer says "with the captured offsets" for every kind; it
  names the fresh form and the resume form separately.
- Task 11's walkthrough passes the actual parameter sets.
- Fixed the stale clean-case line that gave a fresh round "correct offsets".

I also swept for residuals of every renamed thing afterwards and found none.
</applied>

<claims>
1. Your three freeze conditions are met, and meeting them introduced no new
   defect. Attack the new material specifically: the two parameter sets, the
   session-leaf member definition and its exactly-one rule, the kind-equality
   rule, and the renumbered cross-references.

2. The destructive-test redesign is now fail-closed.

3. Nothing in the plan claims more than its evidence supports.

4. This plan is ready to freeze. You set the criterion in round 6 yourself:
   once the parameter sets, the sessions root and the inventory-member
   definition were fixed, the remainder were addressable implementation
   details. If you now say otherwise, say why the criterion changed.

   Everything left on your UNVERIFIED list - the ACL, transactional cleanup,
   removal guards, cp1252, per-session rotation, and the stdout marker's
   extraction contract - is a live step INSIDE this plan. None can be settled
   by a seventh, eighth or ninth reading of a document. At some point a plan
   that has survived six adversarial rounds should be built, and the remaining
   risk carried by the tests it mandates rather than by more prose.
</claims>

<final-check>
List anything you could not verify against files you read this session, as
UNVERIFIED.
</final-check>
