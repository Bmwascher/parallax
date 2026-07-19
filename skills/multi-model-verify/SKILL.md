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
refutation — not by down-weighting either side.

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
   (degraded mode, visibly flagged; never silently skip cross-vendor review).
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
   Get-Content -Raw <brief-file> | codex exec --sandbox read-only -m <canonical-model-id> -c model_reasoning_effort=<canonical-effort> --output-last-message <reply-file> - > <transcript-file> 2>&1
   ```

   `<canonical-model-id>` and `<canonical-effort>` are the two declarations
   in references/model-prompting-notes.md — read the literal values from
   there, never from memory (the reviewer swaps by editing that one file,
   and a remembered id silently defeats the swap). Apply that file's env
   hygiene to the invocation.

   From `<transcript-file>`: verify the effective route — the header's
   `model:`, `provider:`, and `reasoning effort:` lines against the
   canonical declarations, per model-prompting-notes.md; a mismatch is a
   transport failure (fallbacks.md), never a review result — and capture
   the `session id:` line. Read the reviewer's reply from `<reply-file>` —
   the transcript logs every file the reviewer reads and can run tens of
   KB, with the reply buried at the bottom.
3. Later rounds keep the reviewer's state by resuming that session — flags MUST
   precede the resume subcommand (flags after it are a usage error):

   ```powershell
   codex exec --sandbox read-only -m <canonical-model-id> -c model_reasoning_effort=<canonical-effort> --output-last-message <reply-file> resume <SESSION_ID> "<rebuttal-brief>" > <transcript-file> 2>&1
   ```

   Each resume's header must echo the resumed `session id:` and the same
   effective route — the round-1 check repeated (a resume that silently
   started a fresh session has dropped the reviewer's debate state).

4. Iterate per debate-protocol.md until convergence or the round cap, then
   escalate any unresolved points to the user with both positions stated.
5. Freeze the converged plan per references/frozen-plan-format.md under the
   project's superpowers plans dir (KitnEssentials:
   `dev/docs/superpowers/plans/`; other projects: the superpowers default
   `docs/superpowers/plans/`).

## Mode diff

Same transport and protocol. First read the frozen plan's debate record and
its **Verification status** field. Then the brief carries the frozen plan
path, the base/head SHAs superpowers code review used, and the
`git diff base..head` output. Both sides check **spec fidelity** (drift from
the frozen plan — the implementer makes zero judgment calls, so any drift is
a finding) and, for port work, **port fidelity** (drift from the reference
source), ending PASS / FIX / ESCALATE.

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
powershell -NoProfile -File <plugin-root>/tools/write-attestation.ps1 -RepoRoot <reviewed-repo> -BaseSha <base> -HeadSha <head> -Verdict <PASS|FIX|ESCALATE> -Rounds <n> -Participants "<session-model> (session) / <reviewer-model> (reviewer)"
```

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
fallbacks.md handled. The session emits this line itself; never delegate it
to a subagent.

## Common mistakes

- Accepting the reviewer's claims about reference code without the cited lines —
  strike the claim per protocol; do not argue against it.
- Re-sending the full debate context each round instead of resuming the
  codex session.
- Running mode `diff` against different SHAs than the code review used.
- Treating convergence as failure — a sound plan converging in one round is
  the system working, not a skipped debate.
