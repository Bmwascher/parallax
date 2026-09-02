# Benefit measurement: completion-coupled round dispatch

Task 10 of `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md`.

Measured 2026-09-01 by the driving session, against the branch at
`e60fce0` (`item32-detached-dispatch`). Every line below is what was
OBSERVED. Where something could not be observed, it says so and does not
say anything else. An unmade measurement and a clean one must not look
alike.

## The tree every round ran against

Built by `tools/new-review-mirror.ps1` from the live checkout at
`e60fce0`, with the client probe (NOT `-SkipProbe`):

| field | value |
|---|---|
| mirror | `C:\Users\Brandon\AppData\Local\Temp\kerev-t10` |
| source_head | `e60fce05b0a16c65935627911e7e173caa1504f4` |
| mirror_head | `e60fce05b0a16c65935627911e7e173caa1504f4` |
| source_status_sha256 | `3f96fa66dd45e72884c73cad8e6ec845537328e2e15b7e30490a320b37b3273b` |
| mirror_state_sha256 | `85acfa00fa0c05dbabf0cc2635b803f2dc75932778071fefe1c9c8603f23fa7a` |

The live checkout carries a gitignored `AGENTS.md`. `git status` reports
the tree clean and the enumeration still lists it, which is the case the
`--others` pathspec without `--exclude-standard` exists for. It was
removed in the mirror and left untouched in the checkout. Untracked, so
no remediation commit; the two heads are therefore equal, which is the
condition Task 1a's source-is-not-the-mirror refusal exists to stop from
being trivially satisfiable.

Probe: `status: clean`, `skills_before: 31`, `skills_after: 0`,
`plugin_cache_scoped: 0`, `repo_scoped: 0`, `project_agents_md: false`,
`global_agents_md: true` at `C:\Users\Brandon\.codex\AGENTS.md` -
recorded, not removed, exactly as the probe's scope limit states.

## Step 2, the success path, on both hosts

The heading is the frozen task's wording, and it is now accurate: all
five items in Step 2 are observed on BOTH hosts. It was NOT accurate for
most of this branch's life, and this paragraph carried the correction
while that was true. Item 6 below holds the per-item detail and the two
observations that closed it.

Two genuine reviewer rounds. Not stubs: real `codex exec` against
`gpt-5.6-sol` at effort `high`, using the wrapper body SKILL.md now
documents, dispatched by the printed `command` verbatim.

| | Sol R1 | Sol R2 |
|---|---|---|
| `-DispatchHost` | `powershell` (5.1) | `pwsh` (7) |
| task name printed by the tool | `Sol R1 debate round` | `Sol R2 debate round` |
| name the task actually ran under | same | same |
| harness output file, whole content | `reply-present` then `[exited with code 0]` | `reply-present` then `[exited with code 0]` |
| `classification` file | `reply-present` | `reply-present` |
| `exit` file | `0` | `0` |
| transcript `workdir:` | `C:\Users\Brandon\AppData\Local\Temp\kerev-t10` | same |
| `mirror.verify` | `identity: verified` TWICE | `identity: verified` TWICE |
| reviewer verdict | PASS | PASS |

1. **A named task row appeared, carrying the tool's own `taskName`.**
   Observed on both.
2. **The session answered a user message while the round ran.** Observed
   on BOTH hosts. On `powershell` (5.1) at Sol R1: the session composed
   and sent a full reply to the user between dispatch and notification.
   On `pwsh` (7) at the `Sol R2 debate round`: the session wrote to the
   user, the user replied, and the session answered again, all while the
   round was in flight. This is the property the foreground form did not
   have.
3. **A completion notification arrived** carrying the task id and the
   output file path. Observed on both.
4. **The trailer's exit code equals the classifier's mapping.** Observed
   on both: state `reply-present`, exit `0`, and stdout is that one line
   and nothing else.
5. **No console window appeared.** OBSERVED on `pwsh`, by the USER, on
   2026-09-01 during the `Sol R2 debate round` of this branch's own
   cross-vendor debate. The user watched the screen for the duration and
   reported that no console window appeared. The observation is theirs
   and is recorded as theirs: the measuring session cannot see a screen,
   which is why this item sat unmeasured until someone who could was
   asked. This is invariant D5, and it was the FIRST time it had been
   observed for a harness-run wrapper. OBSERVED AGAIN on `powershell`
   (5.1) during the `Sol R3 debate round` the same day, the same way,
   with the same report. So D5 is measured on BOTH hosts, by the user,
   for a harness-run wrapper. It sat unmeasured for the whole build
   because the only party who could make it was never asked.
6. **Both hosts.** COMPLETE. All five items are observed on BOTH hosts.
   Cross-vendor round 1 was right that the earlier "Done, above" counted
   the items that were done and skipped the two that were not: item 2
   was one host and item 5 was nowhere. Three rounds of this branch's own
   cross-vendor debate closed both, by dispatching R2 on `pwsh` and R3 on
   `powershell` and asking the user to watch the screen each time. The
   debate rounds were the measurement vehicle; no round was run for the
   measurement's own sake.

`mirror.verify` holding `identity: verified` twice is the evidence that
the SECOND verification ran. An earlier draft of this design shipped a
second verification that could not run at all, and whose guard would have
read the client's own success as its own.

## Step 2a, the failure surface, which is the design's premise

### A round that FAILS

First attempt, `Sol FAIL`: the stub wrote no `workdir:` header, and the
round classified `workdir-unconfirmed`, exit `1`. That is the documented
order - the workdir states sit ahead of the exit states on purpose - so
the attempt measured the ordering rather than the exit map. Recorded
rather than discarded.

Second attempt, `Sol FAIL2`, header written, client exits 3:

- harness output file: `exit-nonzero` then `[exited with code 1]`
- notification: `Background command "Sol FAIL2 debate round" failed with exit code 1`
- `classification`: `exit-nonzero`
- `exit` file: `3`
- no `reply` file

### A round that is KILLED

`Sol KILL`, dispatched with `PARALLAX_DISPATCH_HOLD_AFTER_EXIT_WRITE`
set, held at the seam, then stopped through the harness.

Disk state AT the seam - everything a post-hoc reader would look at says
success:

- `exit` file: `0`
- `reply`: 9 bytes, non-empty
- `classification`: `classifying:232e7201d3e1493ea64e3dd7fce1e86f`

After the kill:

- **harness output file: empty, then `[killed]`.** Not an exit code, and
  not "completed". A caller reading this surface cannot mistake it for
  success.
- disk state UNCHANGED: `exit` still `0`, `reply` still present. The
  directory that would have fooled a post-hoc classifier is still there.
- `classification` still holds `classifying:<nonce>`. The reservation was
  consumed BEFORE the successful-looking `exit` file was written.
- a hand-run `-Classify` with a guessed nonce: `already-classified`,
  exit `1`.

**Neither came back reporting success, so the design's premise holds as
measured.** The trailer for a killed task is the literal `[killed]`
rather than a numeric exit code; residual 4 already states that nothing
in this repo parses the trailer mechanically, and this measurement does
not change that.

## Step 2b, what each client says about its working directory

- **codex REPORTS it.** The transcript header's third line is
  `workdir: <resolved path>`, before any model text. Confirmed on Sol R1
  and Sol R2 above, and independently on a plan-review round earlier in
  the same cycle. The codex call sites therefore pass `-WorkdirEvidence`.
- **kimi does NOT report it.** Its transcript is the client's own stderr
  and opens directly with the model's reasoning text, with no header
  block at all. A second route was swept before concluding: the lane's
  real captured wire fixtures under
  `evals/multi-model-verify/fixtures/kimi-round/` carry no `cwd`,
  `workdir`, `working_directory`, `project_root` or `rootPath` field.
  This is Task 7 Step 3's STOP condition. It was raised with the user and
  the user decided to ship the lane with the gap RECORDED. The kimi call
  sites therefore pass `-NoWorkdirEvidence`, and each states the limit in
  the shipped text.

## What this measurement does not cover

- The transcripts written by `>` under Windows PowerShell 5.1 are UTF-16.
  The classifier read the `workdir:` header out of them correctly on both
  hosts. That is observed here but was not the object of the test, and no
  test in this branch pins it.
- Only `-DispatchHost powershell` was used for the FAIL and KILL rounds.
  A successful wrapper EXECUTION ran on both hosts; the failure path ran
  on one. That is narrower than "the success path was measured on both
  hosts", which this line said until cross-vendor round 2 pointed out
  that it contradicted item 6 immediately above it - the summary was
  still carrying the overclaim after the itemized list had been
  corrected.
