# Debate record: the mirror identity window

Plan: `docs/superpowers/plans/2026-09-05-mirror-identity-window.md`
Spec: `docs/superpowers/specs/2026-09-05-mirror-identity-window-design.md`

Mode: plan. Lane: codex, GPT-6 Astra at `high`.
Fix-verify budget declared before round 1: 4 dispatched exchanges.

## Astra R1 - VOIDED

Dispatched 2026-09-05 against subject `c723066`, mirror `C:\Temp\pxr1`.

The wrapper classified `workdir-mismatch` and exited 1. The cause was the
driver's own argument: `-WorkdirEvidence` was passed as `C:/Temp/pxr1`
with forward slashes, and the codex transcript header records
`workdir: C:\Temp\pxr1` with backslashes. The classifier compares those
strings literally, so it refused.

**The round is not evidence and this is not a debate round.** The
dispatch contract is that the wrapper's exit code IS the classification,
and `0` is the only value that means `reply-present`. The reply is
retained here as INPUT, on the precedent of item 87's voided Astra R1,
and it was used to amend the plan and the design before a fresh round.
It counts as one unit of the fix-verify budget, because a unit is one
dispatched exchange whatever it returns.

The effective route WAS confirmed in the transcript header before the
classification failed: `model: gpt-6-astra`, `provider: openai`,
`sandbox: read-only`, `reasoning effort: high`, session id
`01a073d8-8ced-7fd0-aefb-02867c5fad74`. Both wrapper identity checks
passed, so the mirror did not move during the round. None of that makes
the round countable; it is recorded because a later reader will ask.

Artifacts:
- `brief-r1-voided.md` - the brief as sent
- `astra-r1-voided-reply.md` - the reply, input only
- `astra-r1-voided-transcript.txt` - the client transcript

### What the voided reply changed, before any countable round

Accepted and applied to the plan and the design:

1. "Fusing build and prepare is not constructible" was WRONG. The fusion
   is constructible; it simply does not close the round-length window.
   The design now says that.
2. The sidecar's destination had NO guards. A hard link or symbolic link
   at the derived path would carry the write to its target, and an
   explicitly supplied `-OverrideOut <MirrorPath>.source-manifest` would
   be silently overwritten, breaking the wrapper's override hash. The
   sidecar now takes the override's whole guard set plus create-new
   semantics.
3. A root-shaped mirror path such as `D:\` derived the drive-relative
   `D:.source-manifest` rather than a sibling. Now refused.
4. PowerShell hashtables compare keys case-insensitively, so a case-only
   rename would have reported no drift while the digest changed. Now
   ordinal dictionaries.
5. `appeared` and `vanished` overstated what manifest membership means.
   Now `entered manifest coverage` and `left manifest coverage`.
6. "No content difference, so the status listing itself changed" was an
   unsupported inference: a replaced sidecar produces the same result.
   Now says the manifest did not identify the cause.
7. Malformed records were silently dropped. Now counted and reported.
8. "Returns no value a caller could branch on" misstated PowerShell:
   `Write-Output` emits into the pipeline. The real protection is that
   the caller ignores it and exits unconditionally.
9. "Never throws" covered only the read. The whole body is now wrapped.
10. The quiet-period contract text claimed every trip spends quota. Only
    the post-client check does. It now states that and its two
    measurement limits.
11. Unbounded read and unescaped names in the printed explanation. Now
    bounded, with control characters rendered.
12. The reference told the operator to rebuild without reading the
    explanation first, and gave no route to `mirror.verify` for the
    wrapper's own refusals. Both fixed.

Pre-existing findings outside this plan's range are recorded as backlog
follow-ups rather than fixed here, per the debate protocol's scope rule.
