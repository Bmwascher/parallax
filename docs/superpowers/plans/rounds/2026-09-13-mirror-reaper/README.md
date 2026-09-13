# Debate record: review mirror reaper (items 106 and 98)

Plan: `docs/superpowers/plans/2026-09-13-mirror-reaper.md`
Spec: `docs/superpowers/specs/2026-09-13-mirror-reaper-design.md`

Mode: diff. Lane: codex, GPT-6 Astra at `high`, one session resumed
across all four rounds. Fix-verify budget declared before round 1: 4
dispatched exchanges; round cap 4 consecutive contested exchanges. All
four exchanges were used; the fourth closed the debate with PASS.

The plan was not debated before the build: the user directed the build
from a KitnEssentials handoff, so this diff debate was the first
cross-vendor gate on the work. Items were filed as 101 and 102 and
renumbered to 106 and 107 in commit `549c136` after main shipped its own
101 to 104 while the debate ran; every artifact below that predates the
renumber cites the old numbers, and the reviewer adjudicated the renumber
in round 3.

## Whole-branch review (Fable, same-harness, not a debate round)

Before round 1, one `parallax:fable-reviewer` pass read the range
`6038c37..6c38ec9` from the diff package `diff/diff-package-6038c37..6c38ec9.md`,
the plan, the spec and the SDD ledger. Verdict "With fixes": no
Critical, two Important (the spec's central claim did not hold for
plan-mode debates and nothing said so; the full gate at the head was not
on record), five Minor. Everything except Minor 4 (the opt-in behavioral
evals, surfaced to the user as a cost decision) was applied at `e9d2713`;
the fix brief and report are `fable-fix-brief.md` and
`fable-fix-report.md`. Artifacts: `brief-fable-diff-r1.md`,
`fable-diff-r1-reply.md`. It spent no Codex quota and counts toward
nothing; it is input.

## Preflight (2026-09-13)

- codex-cli 0.153.4; `codex login status` in a sanitized environment
  (`CODEX_API_KEY`, `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `CODEX_HOME`
  cleared): `Logged in using ChatGPT`. Controller host: `pwsh`, derived
  from `(Get-Process -Id $PID).Path`.
- The branch lives in a linked worktree
  (`C:\Users\Brandon\Documents\_worktrees\parallax-mirror-reaper`), whose
  `.git` is a file, so the mirror was built from a `--no-checkout` clone
  bridge at `C:\Users\Brandon\AppData\Local\Temp\kvs-pxmr` checked out at
  the reviewed head, never from the worktree. The bridge is the reviewed
  source for every round; the quiet period covered it.
- Source enumeration (`git ls-files --cached --others '*AGENTS.md'
  '.agents/*' '.kimi-code/*'`) on the bridge: empty (`baseline:` and
  `manifest:` blank in every `mirror-build-diff-r<n>.txt`). Mirror built at
  `C:\Users\Brandon\AppData\Local\Temp\pxmr` by the branch's own
  `tools/new-review-mirror.ps1`; mirror head equals source head and
  `git status` is empty on both sides in every build, so no remediation
  commit was needed.
- Client context probe (run by each mirror build): `status: clean`,
  `skills_before: 31`, `skills_after: 0`, `plugin_cache_scoped: 0`,
  `repo_scoped: 0`, `project_agents_md: false`. The user's global
  `C:\Users\Brandon\.codex\AGENTS.md` exists and is recorded here; it is
  not a stop. Override files `override-r1.toml` to `override-r4.toml`
  (scratch), each with sha256 `84d16007…79bb1`, checked by every wrapper.
- Tool-surface probe against the mirror before round 1
  (`tool-surface-diff-r1.json`): `status: clean`; pass 1 saw four servers
  and 147 tools; pass 2 under the dispatch flags reported 0 tools and
  `node_repl` silent. A mitigation, never proof of removal.
- `tools/artifact-roots.ps1` output retained as `artifact-roots.txt`.

Every round: wrapper prepared by `tools/dispatch-round.ps1 -Prepare`
with `-DispatchHost pwsh` and `-WorkdirEvidence` spelled with backslashes,
dispatched as a harness background command under the printed task name,
wrapper exit 0 (`reply-present`), route confirmed from the transcript
header (`model: gpt-6-astra`, `provider: openai`, `reasoning effort:
high`, `sandbox: read-only`, `workdir: C:\Users\Brandon\AppData\Local\Temp\pxmr`),
session id `01a09a87-7417-7040-8d98-ce77917ec971`, reply bound to the
brief with `tools/read-codex-round-evidence.ps1` and
`-SealedPriorStateSha256` from the receipt: `status: clean`,
`sealed: sealed` in every `binder-diff-r<n>.json`. The mirror was
rebuilt in place with `-Force` before rounds 2, 3 and 4 so the resumed
session kept its `cwd`.

## Astra R1 - COUNTED, verdict FIX

Dispatched against head `e9d2713` (range `6038c37..e9d2713`) as
`Astra R1 debate round`, fresh session, `-PriorStateFile` an inventory of
the sessions root. Artifacts: `brief-astra-diff-r1.md` (nine claims plus
the code diff), `astra-diff-r1-reply.md`, `astra-diff-r1-transcript.txt`,
`receipt-diff-r1.json`, `binder-diff-r1.json`, `mirror-build-diff-r1.txt`.

PASS on claims 1, 2, 4, 5, 6, 7, 9; FIX on 3 and 8:

- `Set-Content -Path $outFile` expands wildcard characters, so a
  repository named `repo[1]` beside a `repo1` could have its record land
  in the sibling while the literal `File.Exists` read-back accepted an
  old record there and the reap proceeded. Both hosts' read-only probes
  confirmed the expansion.
- The sidecar inspection caught every exception as absence, so an access
  or I/O error skipped the sidecar silently and the run could exit 0.
- The sidecar delete announced `reaped sidecar` with no absence
  read-back, unlike the tree root.
- The plan's Task 3 (f) block was the origin of the two sidecar defects.
- Class sweep: no further unchecked removal or write, and no
  upward-discovering git read, on the certification unit.

Session verification: each finding read against the live emitter before
acceptance; the wildcard expansion is the same class the mirror tool's
own round-6 bracket finding closed. Checkpoint
`20260913-0700-e9d2713bc606.md` written under the attestation root before
the fix. Applied at `fafc4ce` by a fresh implementer from `r1-fix-brief.md`
(report `r1-fix-report.md`): literal write, serialize once, content
read-back exiting 2 on absence, unreadable or unequal; typed sidecar
catches with any other inspection exception exiting 3; post-delete
read-back exiting 3 on survival or re-examination failure; the plan block
superseded by a dated paragraph. One requested test could not be built:
`icacls /deny (RA)` does not make `GetAttributes` throw on either host,
so the inspection-failure branch is covered by reading only, stated to
the reviewer in round 2.

## Astra R2 - COUNTED, verdict FIX

Dispatched against head `fafc4ce` as `Astra R2 debate round`, resumed.
Artifacts: `brief-astra-diff-r2.md`, `astra-diff-r2-reply.md`,
`astra-diff-r2-transcript.txt`, `receipt-diff-r2.json`,
`binder-diff-r2.json`, `mirror-build-diff-r2.txt`.

PASS on claims 2 to 6; FIX on claim 1: the read-back comparison
`$writtenText -ne $json` is case-insensitive, so unequal contents
differing only in letter case passed; the reviewer evaluated the live
expression on both hosts. Two secondary observations: the bracketed test
compared the decoy by parsed JSON rather than bytes and planted no prior
record in the bracketed repository, so it did not exercise the old
false-success branch; and the ordering pin in
`test_sidecar_success_is_read_back` is a string-position assertion a
refactor could satisfy without a runtime read-back (a named test
follow-up, since no non-administrator mechanism makes a file survive
`File.Delete` without throwing). The non-ASCII repository-name consequence
the session declared was accepted as correctly classified.

Session verification: `'{"p":"Session"}' -ne '{"p":"session"}'` is False
on pwsh and on powershell.exe. Applied at `c77d0df` from `r2-fix-brief.md`
(report `r2-fix-report.md`): ordinal `[string]::Equals`, a source pin on
the comparison form, the bracketed case planting a stale record at the
literal path and comparing the decoy by bytes, and the untaken read-back
failure test recorded as follow-up 3 of the reaper follow-up item. The
checkpoint carries the R2 section.

## Astra R3 - COUNTED, verdict FIX

Dispatched against head `549c136` (the merge of main `a8a168f` plus the
renumber) as `Astra R3 debate round`, resumed. Artifacts:
`brief-astra-diff-r3.md` (the R2 fix diff, the branch-side renumber
hunks, and the BACKLOG.md renumber hunks with main's merged items
omitted), `astra-diff-r3-reply.md`, `astra-diff-r3-transcript.txt`,
`receipt-diff-r3.json`, `binder-diff-r3.json`, `mirror-build-diff-r3.txt`.

PASS on claims 1, 2, 3, 5, 6 (the ordinal fix, the stale-record fixture,
the follow-up wording, the merge leaving the certification unit unchanged
beyond the renumber, the class sweep). FIX on claim 4: one reaper
reference survived the renumber because a line wrap split `backlog item`
from `102` in the spec, so the sweep's `item 102` pattern missed it. The
reviewer independently reproduced all three re-attested backlog digests.

Session verification: confirmed at spec line 54; a bare-number sweep
found only byte-value literals elsewhere. Applied at `dcad556`.

## Astra R4 - COUNTED, verdict PASS

Dispatched against head `dcad556` as `Astra R4 debate round`, resumed;
the last declared exchange. Artifacts: `brief-astra-diff-r4.md`,
`astra-diff-r4-reply.md`, `astra-diff-r4-transcript.txt`,
`receipt-diff-r4.json`, `binder-diff-r4.json`, `mirror-build-diff-r4.txt`.

PASS on both claims and **PASS on the range `a8a168f..dcad556`**: every
finding from rounds 1 to 3 has an application the reviewer read, and no
blocking finding remains. UNVERIFIED, stated by the reviewer and not
folded into the verdict: end-to-end runs of the tests and the session's
gate results, since the sandbox is read-only.

## Outcome

Four dispatched exchanges, all bound clean. Round 1 found a real
write-elsewhere path and two swallowed sidecar outcomes; round 2 found a
case-insensitive comparison inside round 1's own fix; round 3 found one
stale number the renumber's own sweep could not see. Nothing was
contested by the session. Residuals are recorded in backlog item 107.
Full six-command gate at `dcad556` on both hosts (`gate-final-dcad556.txt`):
powershell.exe 3073 passed, 14 skipped; pwsh.exe 3072 passed, 15 skipped;
the six lint and checker commands exit 0.

The attestation for `dcad556` (PASS, FULL, 4 rounds, bound to checkpoint
`20260913-0700-e9d2713bc606.md`) reaped this debate's own mirror, its
sidecar and its bridge through `-ReapMirror` and `-ReapBridge`, the first
live use of the feature; the emitter's output is `attestation-dcad556.txt`
and `tools/verify-attestation.ps1` reads the record back as `attested`.
The eight `C:\kv-bl-*` and `C:\kvs-bl-*` directories other chats own
were not named and were not touched.
