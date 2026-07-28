---
name: multi-model-verify
description: Use when planning a reference port, an API-sensitive module, or any change risky enough to need cross-model verification before implementation, or when an implemented diff must be checked against its plan and reference before merge. Fires automatically alongside superpowers requesting-code-review via the review-companion hook.
---

# Multi-Model Verify

## Overview

Two equal-weight advisors — this session and a cross-vendor reviewer driven
through the codex CLI (canonical reviewer model:
references/model-prompting-notes.md) — verify and refute each other's
claims before the cheap implementer touches code. The reviewer lane's
documented fabrication risk (METR; see model-prompting-notes.md) is
mitigated by the debate structure — evidence grounding plus mutual
refutation — not by down-weighting either side. The PRIMARY reviewer
lane (codex) is the default; a second cross-vendor BACKUP reviewer lane
(references/backup-lane.md — REQUIRED READING before any backup round)
substitutes ONLY through the fallbacks.md consent gate — auto-qualified
by the classes named there, manual on user request — with the same
protocol, a different transport, and `Verification status: FULL`
preserved.
Mode diff's debate is preceded by a REQUIRED whole-branch review from
the fable-reviewer seat (agents/fable-reviewer.md), and the user may
convene multi-reviewer PANELS (references/panels.md) in either mode.

**REQUIRED READING before the first round:** references/debate-protocol.md.

Companion to superpowers, not a replacement: it fills the cross-model review
gap superpowers rules out of scope. `/codex:adversarial-review` remains the
human-invoked pre-merge gate; if the codex plugin's stop-review-gate is
toggled on, its stop-time review overlaps mode `diff` — expected, not a bug.

## When to use

- **Mode `plan`** — after superpowers brainstorming proposes approaches for a
  port or API-sensitive module, before the implementation plan is written.
- **Mode `diff`** — after implementation, alongside superpowers
  requesting-code-review (the review-companion hook injects this
  automatically with the matching base/head SHAs).
- NOT for plain bugfixes, docs or release chores, GUI tweaks, or lint sweeps.

## Preflight (both modes)

1. `codex --version` must succeed, and `codex login status` must report
   `Logged in using ChatGPT` — exit 0 alone also passes an API-key login,
   which rides different billing. On failure follow references/fallbacks.md
   (the consent gate may offer the cross-vendor backup lane —
   references/backup-lane.md — before any single-vendor degraded mode;
   never silently skip cross-vendor review).
2. For port work: the reference source must exist under `References/`
   (quote paths — some contain spaces, e.g. `References/M+ Timer`). Missing
   → **HARD STOP before any debate round runs**: ask the user for the path
   and go no further — do not run a codex exchange about the absence, do
   not debate from memory, do not start a degraded mode. If the folder
   holds version subdirectories (e.g. a `v1.4/` next to a `v1.1_old/`), use
   the newest unless the user names one, and cite the versioned path:
   `References/<name>/<version>/<file>:<line>`.
   For non-port work there is no reference folder — claims ground in the
   project's own source, specs, or upstream docs instead, same strike rule.
3. The reviewed repo must carry no AGENTS.md and no `.agents/` entries:
   codex auto-ingests AGENTS.md as instructions, and it advertises
   repo-level `.agents/skills/*/SKILL.md` to the model, which read a
   planted one as its FIRST action (both probed 2026-07-24: the planted
   AGENTS.md controlled the reviewer's reply; the planted skill entered
   its context; see model-prompting-notes.md) — back-channels into the
   auditor that break independence. Enumerate the whole tree in one
   listing — `git ls-files --cached --others '*AGENTS.md' '.agents/*'` —
   which covers tracked, untracked, AND ignored files: `--others` without
   `--exclude-standard` lists ignored paths, re-verified 2026-07-28, and
   `.git` itself is never listed.
   <!-- contract:start id=enumeration-depth-asymmetry -->
   The two pathspecs do not reach equally far. `*AGENTS.md` carries a
   leading star, so it lists a nested AGENTS.md at any depth. `.agents/*`
   is anchored at the repo ROOT, so a nested `sub/.agents/skills/x/` is
   NOT listed. Measured 2026-07-28 on codex-cli 0.144.1: the harness
   advertises a ROOT `.agents/skills` entry and does not advertise a
   nested one, so the asymmetry is not reachable today, and the client
   probe below reads what was loaded rather than where it might live.
   Widen the pathspec if that ever changes.
   <!-- contract:end -->
   If present: STOP and surface it to the user — never dispatch a review
   over an instruction back-channel.

   Clearing it — only on the user's choice, never automatically: run
   `tools/new-review-mirror.ps1 -RepoRoot <repo> -MirrorPath <scratch>`.
   It builds the **review mirror** (references/backup-lane.md owns its
   construction, its baseline, and its identity fields — a file copy
   preserving `.git`, NOT a clone), deletes the offending entries THERE,
   commits when any were tracked, re-runs the enumeration above inside
   the mirror, captures the baseline and the content manifest, runs the
   client probe below with the mirror as the working directory, and
   prints the record block; empty enumeration output is
   the evidence, and the mirror's identity fields go in the debate
   record. The mirror is then the reviewed tree for every lane in that
   debate — dispatch codex with the mirror as cwd, and keep citations
   resolvable in the real repo. Whether the removal needs a commit
   branches on tracked-ness, and the difference misreads as a failure:
   a TRACKED entry's deletion shows as ` D` in `git status --porcelain`
   — a tracked MODIFICATION, which the post-remediation baseline would
   absorb, so the per-round check is not what forces the issue: an
   uncommitted ` D` leaves a tracked modification sitting in the
   baseline, which bars mode diff and breaks HEAD-identifies-content
   (references/backup-lane.md) — so commit the removal
   inside the mirror; an IGNORED or untracked entry's deletion shows
   nothing, no commit is possible, and HEAD legitimately stays where it
   was — `nothing to commit` alongside an unchanged HEAD is the CORRECT
   observation there, not an inconsistency to chase (both observed
   2026-07-26). The mirror carries the real repo's `.git`, hooks
   included, so a commit inside it runs that project's pre-commit hooks
   against the scratchpad copy: expect them to fire, and treat a hook
   failure as a mirror-construction problem, never as a finding about
   the reviewed work.

   Files above the repo's git root are NOT ingested (same probe), and
   `~/.codex/AGENTS.md` is the user's own
   global instruction file — note it in the debate record if it exists,
   but it is not a stop.

   **The reviewer's own machine is the second half of this check, and the
   enumeration above cannot see it.** Run
   `tools/codex-context-probe.ps1 -WorkDir <dispatch cwd> -SuppressSkills -OverrideOut <verified-override-file> -Json`
   before round 1, with a FRESH scratch path for the override file (the
   mirror script runs it for you and prints the same result). It renders
   the model-visible prompt with `codex debug prompt-input`, which spends
   no tokens, and sorts every instruction source it reveals: anything
   inside the reviewed tree STOPS and is remediated in the mirror,
   anything from the codex plugin cache must be empty, and the global
   `AGENTS.md` plus any surviving home-scoped skill is recorded in the
   debate record with its path.
   <!-- contract:start id=client-context-probe -->
   A probe that cannot be taken, that exits non-zero, that returns output
   this parser cannot read, or that finds a named block missing is a
   transport failure and stops the round. It is never read as a clean
   result: an unmade measurement and a clean one must never look alike.
   <!-- contract:end -->

   <!-- contract:start id=plugin-cache-reclassified -->
   The user's codex plugin cache is NOT a harmless environment note.
   Measured 2026-07-28 on codex-cli 0.144.1, it delivered 31 skills into
   the reviewer's context, one of whose descriptions alone instructs the
   model to invoke a skill before answering anything; a reviewer in
   another session adopted it and answered without opening the plan.
   `--disable plugins --disable apps` removes it, and the probe's second
   pass is what proves the removal happened.
   <!-- contract:end -->

## Mode plan

1. Draft the session position: chosen approach, port-fidelity claims, and the
   API/behavior risk register. Every reference claim cites a
   `References/<name>/<file>:<line>` actually read this session — anchor
   EVERY file with its full path the first time you cite it, manifests and
   secondary files included (shorthand only once that file is anchored);
   every API claim cites authoritative local docs (WoW projects:
   `.wow-api-reference/` or a dated in-game probe result) — never memory.
   The position has no separate artifact — it IS the claims section of the
   step-2 brief.
2. Compose the reviewer's debate brief per references/model-prompting-notes.md, write
   it to a scratchpad file, then run round 1:

   ```powershell
   $bytes = [System.IO.File]::ReadAllBytes("<verified-override-file>")
   $seen = ([System.BitConverter]::ToString(([System.Security.Cryptography.SHA256]::Create()).ComputeHash($bytes)) -replace '-', '').ToLower()
   if ($seen -cne "<override-sha256>") { throw "the override file changed after the probe verified it" }
   $override = (New-Object System.Text.UTF8Encoding($false, $true)).GetString($bytes)
   Get-Content -Raw <brief-file> | codex exec --sandbox read-only --disable plugins --disable apps -c $override -m <canonical-model-id> -c model_reasoning_effort=<canonical-effort> --output-last-message <reply-file> - > <transcript-file> 2>&1
   ```

   <!-- contract:start id=verified-override-dispatch -->
   The `-c` value MUST be the file the probe wrote with `-OverrideOut`, on
   round 1 and on every resume, read as raw bytes whose hash is checked
   against the probe's report before use. The two feature flags alone
   still leave the user's own skills directory and codex's built-in skills
   advertised, which was 29 of the original 60 when this was measured;
   only the generated override removes those, and only the probe's second
   pass proves it did. A dispatch that omits the override, or carries a
   value the probe did not verify, is a transport failure, because the
   measurement then describes a configuration the reviewer never received.
   <!-- contract:end -->

   `<canonical-model-id>` and `<canonical-effort>` are the two declarations
   in references/model-prompting-notes.md — read the literal values from
   there, never from memory (the reviewer swaps by editing that one file,
   and a remembered id silently defeats the swap). Apply that file's env
   hygiene to the invocation.

   Backup lane: same protocol, transport and per-round evidence per references/backup-lane.md.

   Panels: any reviewer-lane combination per references/panels.md.

   From `<transcript-file>`: verify the effective route — the header's
   `model:`, `provider:`, and `reasoning effort:` lines against the
   canonical declarations, and the `sandbox:` line reads `read-only`, per
   model-prompting-notes.md; a mismatch is a transport failure
   (fallbacks.md), never a review result — and capture the `session id:`
   line. Read the reviewer's reply from `<reply-file>` — the transcript
   logs every file the reviewer reads and can run tens of KB, with the
   reply buried at the bottom. Every round writes FRESH round-numbered
   `<reply-file>`/`<transcript-file>` paths: after a failed call, a reused
   path serves the previous round's reply and reads exactly like success —
   a reply not freshly written by this round's call is a stale reply, a
   transport failure (fallbacks.md), never a review result.
3. Later rounds keep the reviewer's state by resuming that session — flags MUST
   precede the resume subcommand (flags after it are a usage error):

   ```powershell
   $bytes = [System.IO.File]::ReadAllBytes("<verified-override-file>")
   $seen = ([System.BitConverter]::ToString(([System.Security.Cryptography.SHA256]::Create()).ComputeHash($bytes)) -replace '-', '').ToLower()
   if ($seen -cne "<override-sha256>") { throw "the override file changed after the probe verified it" }
   $override = (New-Object System.Text.UTF8Encoding($false, $true)).GetString($bytes)
   codex exec --sandbox read-only --disable plugins --disable apps -c $override -m <canonical-model-id> -c model_reasoning_effort=<canonical-effort> --output-last-message <reply-file> resume <SESSION_ID> "<rebuttal-brief>" > <transcript-file> 2>&1
   ```

   The preamble repeats in full every round. Rounds are separate shell
   invocations, so a `$override` set in round 1 does not exist in round 3,
   and one verification does not cover a file that can change between
   rounds.

   Each resume's header must echo the resumed `session id:` and the same
   effective route — the round-1 check repeated, `sandbox:` included (a
   resume that silently started a fresh session has dropped the reviewer's
   debate state). Sandbox mode has NO continuity across resumes: a resume
   missing `--sandbox read-only` resolves to the config default — on a
   `workspace-write` default the read-only auditor becomes a writing agent
   mid-review (probed 2026-07-24, the write landed; see
   model-prompting-notes.md). The header's `sandbox:` line is where that
   surfaces.

4. Iterate per debate-protocol.md until convergence or the round cap, then
   escalate any unresolved points to the user with both positions stated.
5. Freeze the converged plan per references/frozen-plan-format.md under the
   project's superpowers plans dir (KitnEssentials:
   `dev/docs/superpowers/plans/`; other projects: the superpowers default
   `docs/superpowers/plans/`).

## Mode diff

Same transport and protocol. First read the frozen plan's debate record and
its **Verification status** field.

Required before round 1: the agents/fable-reviewer.md whole-branch review runs on the same range, its raw reply is retained as a range-bound artifact, and the round-1 brief cites that artifact with the session's per-finding adjudications.
The session adjudicates each review finding with evidence — accept,
refute, or ESCALATE into the debate — before any reviewer lane sees
them; the review is the debate's required input, never its verdict,
and the debate record names the artifact path.

Then the brief carries the frozen plan
path, the base/head SHAs superpowers code review used, and the
`git diff base..head` output. Both sides check **spec fidelity** (drift from
the frozen plan — the implementer makes zero judgment calls, so any drift is
a finding, with one carve-out: envelope-designated escalation-lane DECISIONS
are adjudicated against their frozen envelope per
references/frozen-plan-format.md, and only envelope overruns are drift) and,
for port work, **port fidelity** (drift from the reference
source), ending PASS / FIX / ESCALATE.

Backup lane: same protocol, transport and per-round evidence per references/backup-lane.md.

Panels: any reviewer-lane combination per references/panels.md.

A FIX this session applies itself goes through the **application
checkpoint** (references/application-checkpoint.md) before the first edit.
The fixed range is then re-reviewed, and only the post-re-review terminal
PASS is attested — with the emitter's `-CheckpointFile` binding the
checkpoint; a FIX verdict whose fixes are still unapplied is never the
attested verdict.

**Degraded-plan poisoning rule:** a plan whose Verification status is
DEGRADED cannot produce an ordinary diff PASS. Mode diff must first reopen
and cross-verify the plan's claims and approved deviations (the
retrospective pass the plan never got), and only then verify the
implementation against it — confirming a diff matches an unsound plan
verifies nothing. If cross-vendor verification is STILL unavailable, the
only terminal state is `ESCALATE — CROSS-VENDOR GATE UNSATISFIED`: merging
then requires the user's explicitly recorded risk acceptance, never a PASS.

## Finish line

Before it: the session's final-adjudication step (debate-protocol.md) —
verify the last round's findings against the repo and issue the terminal
verdict; a reviewer's PASS/FIX is never terminal by itself.

**Mode diff only — record the verdict mechanically.** After the terminal
verdict, run the attestation emitter from this plugin's checkout:

```powershell
powershell -NoProfile -File <plugin-root>/tools/write-attestation.ps1 -RepoRoot <reviewed-repo> -BaseSha <base> -HeadSha <head> -Verdict <PASS|FIX|ESCALATE> -VerificationStatus <FULL|DEGRADED> -RouteNote "<effective route confirmed | the transport-failure class>" -Rounds <n> -Participants "<session-model> (session) / <reviewer-model> (reviewer)" [-CheckpointFile <application-checkpoint-artifact>]
```

When an application checkpoint governed fix application, pass it via
`-CheckpointFile`: the record then also binds the checkpoint's hash and
the emitter-computed changed-path set, `<head>` is the POST-fix,
re-reviewed head — never the head the FIX verdict was issued on — and
the artifact must already carry its appended verification results (the
recorded hash covers the final artifact).

It writes `.git/parallax/attestations/<head-sha>.json` inside the reviewed
repo — untracked by design, so recording the verdict cannot move HEAD out
from under its own SHA. The pre-push lane (`tools/verify-attestation.ps1`)
later warns when a `main` push has no matching attestation for the pushed
head (fast-forward: pushed sha == attested head; merge commit: parent1 ==
attested base, parent2 == attested head — a squash changes the sha and
correctly forces re-review).

End with one status line: participating models, rounds used, converged vs
escalated points, the verification status — `FULL`, or
`DEGRADED (<class>, authorized by user at round N)` per fallbacks.md — and
the route note: `effective route confirmed` when every round's header
matched the canonical declarations, else the transport-failure class that
fallbacks.md handled. The route-note grammar is lane-agnostic: for a backup-lane debate,
`effective route confirmed` means every round satisfied
references/backup-lane.md's per-round evidence rules against the backup
declarations; the evidence class is recorded in the debate record prose. The session emits this line itself; never delegate it
to a subagent.

## Common mistakes

- Accepting the reviewer's claims about reference code without the cited lines —
  strike the claim per protocol; do not argue against it.
- Re-sending the full debate context each round instead of resuming the
  codex session.
- Running mode `diff` against different SHAs than the code review used.
- Treating convergence as failure — a sound plan converging in one round is
  the system working, not a skipped debate.
