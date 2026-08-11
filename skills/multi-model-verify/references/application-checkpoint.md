# Application checkpoint

The debate has a hard contract (verdict grammar, evidence rules); without
one, the application phase reverts to act-immediately bias: a verdict
lands and the session starts editing with no record between "review
concluded" and "diffs happening". The checkpoint closes that gap by making
the missing state transitions explicit:

```
reviewed -> dispositioned -> authorized -> applied -> reverified
```

The checkpoint is the `dispositioned -> authorized` step. It — not the
verdict — is what authorizes touching files.

## When it applies

Whenever THIS SESSION applies file changes that follow from a review
verdict: mode-diff FIX application, post-adjudication fixes during a
debate, or interactive drift triage. Deliberately N/A: the headless drift
auto-triage lane — its script owns gates and commits, and its report plus
the untrusted-agent isolation is that lane's record.

## The checkpoint (before the first edit)

Emit BEFORE any Edit/Write other than writing the checkpoint artifact
itself. Required content — specificity is the contract, never length:

1. **Reviewed range and terminal outcome** — the base..head (or review
   round) the findings came from, and the verdict being applied.
2. **Dispositions** — every finding id from the review:
   `finding | accepted / refuted-with-evidence / deferred | why`.
3. **Planned changes** — one row per EXACT file path:
   `file | intended postcondition | finding id(s)`. Postconditions state
   the outcome ("threshold equals 0.2"), never implementation pseudocode —
   the reviewer catches a plausible-but-wrong fix by comparing outcomes.
   A code literal is implementation even when correct: write "the frame
   is 24x24", not `frame:SetSize(24, 24)`.
4. **Verification plan** — `gate | what passing proves`.
5. **Authorization** — `awaiting user` or
   `pre-authorized by: "<the instruction, quoted>"`.
6. **Scope line** — `no files beyond the rows above; amend this
   checkpoint before expanding`.

Ceremony (banned): debate recaps, implementation pseudocode, file plans
for refuted findings, directory globs, and non-falsifiable rows ("fix
issues"). A boilerplate checkpoint trains the reader to skip it and is
worse than none.

## Authorization gating

- **Attended (default): STOP after emitting** and wait for the user's go.
- **Pre-authorized**: an explicit whole-pipeline instruction ("build ->
  review -> apply fixes -> push") skips only the wait — emission is never
  optional — and the checkpoint quotes that instruction verbatim.
- **Invalidation**: a file not in the plan, a newly discovered finding, or
  any scope growth invalidates the authorization. Append an AMENDMENT
  section (same row format, dated) before touching the new file; an
  amendment inside the quoted instruction's scope proceeds once recorded,
  anything beyond it stops and asks. Pre-authorization changes STOP to
  CONTINUE — it never relaxes content, path, or amendment rules.

## After application (applied -> reverified)

`applied` is not the terminal state. After the last planned edit, EXECUTE
the verification plan and append its results to the artifact
(`gate | result`, plus any deviations); an unexecuted verification plan
is a plan, not a state transition, and the artifact update carrying those
results is the LAST write of the application phase. A re-review of the
fixed range follows (mode diff: the fix re-review exchange), and the
terminal PASS — and its attestation — come only after that.

## The artifact

Write the checkpoint to the reviewed repo's git dir — untracked, same
rationale as attestations (recording it cannot move HEAD, it never ships
in a commit, worktrees share it):

```
<git-common-dir>/parallax/application-checkpoints/<stamp>-<reviewed-head12>.md
```

At attestation time, pass it to the emitter via `-CheckpointFile`: the
attestation then records the checkpoint's hash and the emitter-computed
changed-path set of the attested range. The emitter refuses an artifact
outside the canonical directory above, and the verifier re-locates and
re-hashes the artifact — a record whose artifact is missing or modified,
or whose path set no longer matches the range, is rejected. Binding
metadata is all-or-none: stripping one field cannot evade the rest. An
attestation minted for a different change set fails mechanically.

Two things about that emitter call, moved here from SKILL.md in 0.23.0
because they are read only when a checkpoint actually governed the fixes.
The `<head>` passed with `-CheckpointFile` is the POST-fix, re-reviewed
head — never the head the FIX verdict was issued on. And the artifact must
ALREADY carry its appended verification results before the emitter runs,
because the recorded hash covers the final artifact; hashing it first and
appending afterwards records a file that no longer exists.

## Standalone contexts (no parallax machinery)

For a distilled skill outside this plugin, keep a `COLLABORATION.md` in
the project root, appended once per review/application cycle — decision
deltas, never transcript summaries:

```markdown
## Cycle N — <topic>
### Review input
### Dispositions
### Planned changes
### Verification
### Authorization
### Applied
### Verification results
### Deviations
```

Attended runs stop after `Authorization` and wait; the sections below it
are appended after execution. The file doubles as a process log — in a
course setting, it IS the evidence of how the work happened.
