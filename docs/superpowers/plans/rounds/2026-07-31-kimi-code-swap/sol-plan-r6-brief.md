<task>Round 6. Your round-5 structural finding was correct and is repaired. Re-read
docs/superpowers/plans/2026-07-31-kimi-code-swap.md. Evidence rules, verdict
grammar and boundaries as before.</task>

<applied>
You were right that the fresh-state identity was unexecutable, and right that
it was structural. It was also self-inflicted: r5's own session-binding fix
created it, which is the fix-carries-the-next-defect pattern this repo has now
hit six times across two cycles.

The repair takes your first suggested shape - different identity semantics per
kind - rather than looking for an undocumented session-id selection mechanism,
because none exists in the measured transport.

- -PriorState now has TWO shapes. Fresh: `kind: "fresh"` plus
  `knownSessionDirs`, the session-directory inventory captured immediately
  before dispatch, and nothing else - no offsets, no hashes, no sessionDir,
  because none of them can exist yet. Resume: kind, sessionDir, sessionId,
  both byte offsets, both prefix hashes, both continuity hashes.
- New rule 2 splits by kind. Fresh: enumerate session directories now, subtract
  knownSessionDirs, require EXACTLY ONE new directory - zero fails
  `session-not-resolvable`, and so does two, which is the concurrent-run case
  an isolated home does not prevent. Then require that directory's name to
  equal `-SessionIdFromStdout`, the id the client printed, so the directory is
  cross-checked against the client's own report rather than inferred from the
  filesystem alone. Resume: the exact path-and-id comparison you asked for in
  round 4, which is now in the only place it can hold.
- Rule 3's inconsistency check is restated against the two shapes.
- New rule 6: a fresh call's offsets are zero by definition, so the truncation
  and prefix-hash steps are skipped and the whole file is the slice.
- nextState is ALWAYS resume-shaped, whatever kind produced it, so the chain is
  uniform from round 2 onward.
- Six new session-identity test cases, covering both branches separately.

Destructive tests. You were right, and this one was worse than a defect - it
was dangerous. The instructions planted an AUTHORIZING sentinel on the real
USERPROFILE and a real drive root and then ran newly written recursive-deletion
code against them. Now: a subprocess with USERPROFILE pointed at a temporary
directory, a substituted drive via `subst` for the drive-root branch, a scratch
directory containing an empty .git for the repository branch, and sentinel
cleanup in a `finally` regardless of outcome. Nothing is ever pointed at a real
profile, drive root or repository.

Also fixed: the two surviving "every flag" statements, including the handoff
one you noted would persist the overclaim; the stale "session-creation record"
wording in Task 7, now `metadata`; the sub-item numbering that read as a
duplicate Step 6; and the stale "thirty-one cases" total, which is now not a
count at all, since every revision has added cases.

After applying these I swept the document myself and found three surviving
references to the deleted `sessionDirExisted` field, in the interface bullet,
rule 1 and rule 15. Those are fixed too; I mention it because it is the same
class you have been catching and I would rather record it than have you find it.
</applied>

<claims>
1. The fresh/resume identity split is correct and executable, and the repair
   introduced no new defect. Attack it specifically: the inventory diff, the
   exactly-one requirement, the `-SessionIdFromStdout` cross-check, rule 6's
   skip, and the always-resume-shaped nextState.

2. The destructive-test redesign is safe and still exercises every guard branch
   it claims to.

3. Nothing in the plan now claims more than its evidence supports.

4. This plan is ready to freeze and implement. Your round-5 answer to this was
   that the fresh-state protocol needed repair rather than another test-list
   round. If you still say no, name what is STRUCTURAL - a design that cannot
   be instantiated or cannot fail correctly - as distinct from a case that
   could be added. I am asking for that distinction explicitly, because
   everything remaining on your UNVERIFIED list is something only
   implementation can settle: the ACL, the transactional cleanup, the removal
   guards, cp1252 and log rotation are all live steps inside the plan.
</claims>

<final-check>
List anything you could not verify against files you read this session, as
UNVERIFIED.
</final-check>
