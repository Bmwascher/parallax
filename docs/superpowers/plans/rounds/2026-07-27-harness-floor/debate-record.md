# Debate record — parallax 0.14.4 (mode diff, Kimi solo lane)

**Subject revision:** `f8bab1c..f992604` (final). Round 1 ran against
`f8bab1c..f5ed873`; retaining the gate artifact moved the head and
re-opened the lane, so round 2 verdicted the final revision.

**Verification status:** FULL — the reviewer lane is cross-vendor, so no
diversity was reduced and no failure class is recorded.

**Lane selection:** user-directed, on quota grounds — codex sat at 77% of
a 7-day window not resetting until Aug 1, and the user chose "Kimi solo,
2 rounds". This is fallbacks.md's "available on user request for anything
else" route, NOT a substitution for a failed primary: the codex lane was
probed healthy in the same session (doctor check 4, effective route
confirmed, `TRANSPORT-OK`). Recorded so the absence of a failure class is
not read as an omission.

## Origin — this cycle was not planned work

Drift triage. The weekly watch produced `tools/drift-reports/
2026-07-21_131702.txt`, whose headless auto-triage never ran: it exited 1
on `You're out of usage credits`, with a second error in the runner
(`Write(**) is not matched by file permission checks — use Edit(**)`).
Its findings therefore sat untriaged for six days across five releases.
Triaged by hand 2026-07-27.

## Participants and rounds

| seat | role | rounds | terminal verdict |
|---|---|---|---|
| Opus 5 | session driver, final adjudication | — | PASS (terminal) |
| `kimi-code/k3-256k` (kimi-cli) | cross-vendor reviewer lane | 2 | PASS |
| fable-reviewer | required whole-branch pre-merge review | 1 | Ready-with-fixes (all applied) |

## Route evidence

`effective route confirmed` under backup-lane.md's per-round rules. The
write-probe and both rounds each produced, past the captured offset,
exactly one `Using LLM model:` line carrying the canonical id, one
`Loading agent:` line naming the committed yaml, and one `Loaded tools:`
line equal to the five-tool allowlist. Mirror status delta equalled
baseline + `KIMI-REVIEW-BRIEF.md` exactly on every round. Rotation guard
satisfied throughout — the log grew 390333 → 394823 → 404435 → 411255,
with the now-familiar `WinError 32` rotation failure firing on each call.
Session `cf55eda8-50c2-4db3-a63b-5d338201123f`, all four flags re-pinned
on the resume. Evidence class: client-side.

**Effort evidence:** NO VERIFIED EFFORT PIN — `~/.kimi/config.toml` still
carries no `overrides` block for the canonical id.

**Environment notes (not findings):** `~/.codex/AGENTS.md` exists (user's
own). `merge_all_available_skills = true` at `~/.kimi/config.toml:10`
with `extra_skill_dirs = []` and no source dirs present — latent.
Preflight-3 sweep empty in both real tree and mirror.

## Workspace

File-copy mirror preserving `.git`, HEAD `f992604`, no tracked
modifications, so the reviewed content IS the committed range. Baseline
and content manifest captured together (122 entries at round 1, 121 at
round 2 after the evidence commit moved files from untracked to tracked).
Write-probe PASS on all three conditions.

## What was triaged

**Acted on (2):**

1. Claude Code 2.1.216 restored prompt and tool restrictions for resumed
   background agents. The Fable panel lane's containment argument — model
   pin plus read-only allowlist, with "agent death, which is loud" as the
   only failure mode — was therefore version-dependent and unqualified.
   Below the floor a resumed seat silently reverted to the default agent,
   dropping all three controls at once. Recorded as a floor in both files
   that carry the claim; below it the lane is UNAVAILABLE, not degraded.
2. superpowers 6.1.1 → 6.2.0 (Jul 24) left the pinned fixture stale. The
   hook was never inert — the canary checks literals against the
   *installed* template and passed throughout — but byte-equality is
   check-drift's job and would have raised a WARN on the Jul 28 run.
   Re-pinned across five sites.

**Dismissed (7), with independent concurrence from the whole-branch
review:** @-mentions/vim/statusline, PowerShell Unicode validation,
mid-session slash-menu refresh, `name:` frontmatter autocomplete prefix,
git/gh argument validation, dataviz palette, and `/verify` + `/code-review`
no longer auto-running.

## Findings, by round

**Whole-branch review (pre-round-1).** I1: both floor pins locked the
DESCRIPTION while the operative half deleted green — and worse than
reported, `Claude Code 2.1.216` occurs twice in panels.md, so the pin did
not lock even the paragraph's existence. **Pin-integrity instance
TWELVE**, the second consecutive cycle with an instance inside a fix.
I2: the new panels.md text claimed a below-floor panel "drops to its
remaining lanes under panel-lane-loss" — which that class contradicts,
and which panels.md itself contradicts ~20 lines below; it also put class
mechanics in a file barred from defining them. I3: the diff package's
exclusion note was false for one this-cycle commit. Two Minors. All
accepted and applied.

**Round 1.** PASS on all eight claims. The lane independently probed the
pin deletion cases — header-only, operative-only, whole-paragraph — and
confirmed each turns at least one pin red, which is a stronger check than
the session ran on its own fix. One non-blocking observation: no
gate-output artifact retained where 0.14.3 had one. Acted on rather than
carried.

**Round 2.** PASS, terminal. The lane verified the parent-commit gate
binding rather than accepting it, by two independent routes: diffstat
arithmetic closing exactly (19616 + 1193 = 20809 insertions, the delta
being precisely the six evidence files), and confirming no gate reads
`docs/`. It also upgraded its own round-1 UNVERIFIED on the changelog
quote by locating the drift watch's own capture at
`tools/drift-reports/2026-07-21_131702.txt:5,7`, matching panels.md
verbatim.

**Session final adjudication.** Re-verified the load-bearing claim
myself: no test module reads a `docs/` path — the single hit,
`evals/tools/run_behavioral_evals.py:313`, builds a path inside a temp
workspace and belongs to the opt-in suite, not the five gates. Diffstat
confirmed at 59 files / 20809 insertions. Terminal verdict PASS.

## Head beyond the attested review

The attestation names `f992604`, the revision round 2 verdicted. Commits
after it contain only this cycle's own retained evidence — the round-2
reply, the regenerated diff package and mirror baseline, and this record.
That is the same self-referential class the lane already scrutinized and
cleared for the gate artifact, and the same binding argument applies: no
gate and no contract surface reads `docs/`. The attestation is re-emitted
at the final head so the pre-push lane matches; nothing in the reviewed
contract differs.

## Retained artifacts

`fable-review.md`, `kimi-r1-reply.md`, `kimi-r2-reply.md`,
`diff-package.txt`, `gate-output.txt`, `mirror-baseline.txt`,
`mirror-manifest.txt`, and this record — all under
`docs/superpowers/plans/rounds/2026-07-27-harness-floor/`, tracked per
frozen-plan-format.md.

Application checkpoint:
`.git/parallax/application-checkpoints/20260727-021500-f9fd9b97e156.md`
(+ Amendment 1 and appended verification results, including the disclosed
first-run state-machine failure and its cause).

## Carried forward to 0.15.0

Unchanged from 0.14.3, now with more evidence behind the first:

- **The pin mechanism.** Instance twelve landed this cycle, again inside
  a fix. Three consecutive cycles have produced instances; hand-applied
  substring pinning is the common factor. Both reviewer seats have now
  said a follow-on cycle is the wrong vehicle for replacing it.
- **`verify-attestation.ps1`'s self-contradicting warning text**, which
  fires whenever `-RouteNote` carries anything but the exact token.

New this cycle:

- **The headless auto-triage lane failed silently for six days.** It died
  on out-of-credits and a permission-rule error (`Write(**)` vs
  `Edit(**)` in its `--allowed-tools`), and nothing surfaced that until a
  human looked. A lane whose whole purpose is unattended triage needs its
  own failure to be loud.
