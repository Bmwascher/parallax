# Debate record: artifact roots (item 100)

Plan: `docs/superpowers/plans/2026-09-12-artifact-roots.md`
Spec: `docs/superpowers/specs/2026-09-12-artifact-roots-design.md`

Mode: plan. Lane: codex, GPT-6 Astra at `high`.
Fix-verify budget declared before round 1: 4 dispatched exchanges; the
user said on 2026-09-12, while R1 ran, that it can be extended for a
proper fix, so exhaustion pauses for that word rather than ending.

## Spec pre-read (Fable, same-harness, not a debate round)

Before the plan was written, one `parallax:fable-panel-reviewer` pass read
the spec at blob `ed8674b`. Verdict FIX with ten findings, all verified by
the session and applied at commit `29d2376`. Artifacts:
`brief-fable-spec-r1.md`, `fable-spec-r1-reply.md`. It spent no Codex
quota and counts toward nothing; it is input.

## Preflight (2026-09-12)

- codex-cli 0.153.4; `codex login status` in a sanitized environment
  (`CODEX_API_KEY`, `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `CODEX_HOME`
  cleared): `Logged in using ChatGPT`. Controller host: `pwsh`, derived
  from `(Get-Process -Id $PID).Path`.
- Source enumeration (`git ls-files --cached --others '*AGENTS.md'
  '.agents/*' '.kimi-code/*'`) found `AGENTS.md` (ignored). Mirror built at
  `C:\Temp\pxar1` by `tools/new-review-mirror.ps1` at source head
  `100198d`; the mirror's enumeration is empty; mirror head equals source
  head, so no remediation commit was needed.
- Client context probe (run by the mirror build): `status: clean`,
  `skills_before: 31`, `skills_after: 0`, `plugin_cache_scoped: 0`,
  `repo_scoped: 0`, `project_agents_md: false`. The user's global
  `C:\Users\Brandon\.codex\AGENTS.md` exists and is recorded here; it is
  not a stop. Override file
  `C:\Temp\parallax-scratch\2026-09-12-artifact-roots\override-r1.toml`,
  sha256 `84d16007…79bb1`.
- Tool-surface probe against the mirror: `status: clean`; pass 1 saw four
  servers and 146 tools; pass 2 under the dispatch flags reported 0 tools,
  `node_repl` silent, `plugins=False`, `apps=False`, `memories=False`. A
  mitigation, never proof of removal.

## Astra R1 - COUNTED, verdict FIX

Dispatched 2026-09-12 against plan blob `090aec7` (HEAD `100198d`),
mirror `C:\Temp\pxar1`, as background task `Astra R1 debate round`.
Wrapper exit 0, classification `reply-present`.

Route confirmed from the transcript header: `model: gpt-6-astra`,
`provider: openai`, `reasoning effort: high`, `sandbox: read-only`,
`workdir: C:\Temp\pxar1`, session id
`01a0985e-1d0d-7940-b544-11e0ffeba5d9`. Round evidence bound with
`tools/read-codex-round-evidence.ps1 -Fresh` and
`-SealedPriorStateSha256` from the receipt: `status: clean`,
`sealed: sealed` (`binder-r1.json`).

Artifacts: `brief-astra-r1.md`, `astra-r1-reply.md`,
`astra-r1-transcript.txt`, `receipt-r1.json`, `binder-r1.json`.

**Reviewer verdict: FIX.** PASS on claims 2, 3, 4, 8, 9, 10 and 12. FIX on
1, 5, 6, 7 and 11, plus two class-sweep findings and one stated escape
form. Nothing was contested; the session verified each finding against
source before accepting it.

### Session verification

- Claim 1: `evals/multi-model-verify/test_contract_coverage.py:794-850`
  read. Every bare occurrence of a declared id in `skills/`, `agents/`
  and `commands/` must be preceded by `<file>.md's `; a `/` before or a
  `.` after does not exempt it, so `tools/artifact-roots.ps1` would be an
  unresolvable citation of a region named `artifact-roots`. Confirmed.
  Region renamed `round-artifact-roots` throughout the plan and spec.
- Claim 5: `IsPathRooted` throwing on `<` under .NET Framework is the
  documented invalid-path-character behaviour; the reviewer's probe
  result is accepted on that basis. `git -C <sub> rev-parse
  --git-common-dir` printing `../.git` and the plan joining it to the
  toplevel: confirmed by reading the plan's own code against
  `tools/write-attestation.ps1:61`, which joins to `$RepoRoot`. The `./`
  retention: confirmed by reading the plan's `Trim("/")`. All three fixed
  in the tool, each with a regression test. The JSON-whitespace sentence
  was in the brief, not the plan; nothing to change, and the tests
  already parse.
- Claim 6: measured the linter's way (`evals/tools/skill_lint.py:163-182`
  strips the frontmatter and joins with LF): 25987. Confirmed; the plan
  and spec now carry 25987 and the post-edit 25985.
- Claim 7: confirmed by reading the plan's `test_sweep_can_fail`; the
  ledger shape had only its exemption exercised. Positive assertions
  added for the ledger shape and for the new `.git/parallax/` shape.
- Claim 11: confirmed by reading `tree_paths`; `is_file()` dropped
  directories. Snapshot now includes directories, the expected set names
  the two parent directories the emitter creates, and an empty-directory
  control was added.
- Class sweep, `agents/flash-implementer.md:36-40`, `:67`, `:79`: read.
  The Flash brief is written into the checkout and deleted before any
  evidence check. Recorded as an implementation-time artifact outside
  the contract, in the declaration prose and the spec's out-of-scope
  list, and as a stated limit of the writer test (endpoint sampling).
- Class sweep, `SKILL.md:389`: read. The sentence says `.git/parallax/…`
  "inside the reviewed repo"; the emitter writes under the git common
  dir. The user authorized a third SKILL.md edit on 2026-09-12 (it also
  saves 11 characters), and the sweep gained a `.git/parallax/` shape.
- UNVERIFIED (reviewer): the 54 MB copy's attribution to a Codex
  controller. The session read the rollout on 2026-09-12; the spec now
  names the file so a later reader can. It carries no weight in the
  verdict either way.

### Applied

Every finding above, to the plan (`docs/superpowers/plans/2026-09-12-artifact-roots.md`)
and the spec, in the commit that carries this record.

## Astra R2 - COUNTED, verdict FIX

Dispatched 2026-09-12 against plan blob `29cc87d` (HEAD `5d3b251`), the
mirror rebuilt at the same path `C:\Temp\pxar1` with `-Force` (probe
clean again, override `override-r2.toml`, same sha256), resumed session
`01a0985e-1d0d-7940-b544-11e0ffeba5d9`, background task
`Astra R2 debate round`. Wrapper exit 0, `reply-present`. Route
confirmed: same model, provider, effort, `sandbox: read-only`, same
session id echoed, `workdir: C:\Temp\pxar1`. Bound with `-Resume`,
`status: clean`, `sealed: sealed` (`binder-r2.json`).

Artifacts: `brief-astra-r2.md`, `astra-r2-reply.md`,
`astra-r2-transcript.txt`, `receipt-r2.json`, `binder-r2.json`.

**Reviewer verdict: FIX.** A FIX, B FIX, C PASS, D PASS, E PASS. All
eight round-1 applications confirmed present. Nothing contested.

### Session verification

- A, the writer test: `.git/parallax` is in the expected set and the
  loop asserted `-Assert` exit 0 on every member; that parent is not
  under a declared root, so the tool answers 1 and a correct tool would
  fail the test. Confirmed by reading the plan's own loop against its
  own `-Assert` membership rule. The negative control's `mkdir` creates
  `rounds` as well as `rounds/x`. Confirmed. Both fixed: membership is
  asserted for the attestation directory and file, refusal for the
  shared parent, and the exact-set assertion bounds it; the control
  expects both paths.
- B, relative `-RepoRoot`: a native `git` child inherits the PROCESS
  cwd, not PowerShell's location, so `-RepoRoot .` is resolved wherever
  the host was launched. The same trap is guarded in
  `tools/new-review-mirror.ps1:1234-1244` with the provider-path helper
  the plan's tool already defines as `Resolve-Absolute`. Confirmed.
  `-RepoRoot` is now resolved through it before git runs, and a
  regression with differing PowerShell location and process cwd was
  added, in the shape of `test_review_mirror.py:537-565`.
- Date: the reviewer read the rollout the spec names and found the
  copy's execution record dated 2026-09-08 in a session started
  2026-09-07; the KitnEssentials directory's mtime is Sep 8. Confirmed.
  Corrected in the spec, the plan's declaration prose and its backlog
  paragraph. The 54 MB figure is the cleanup's own and stays
  UNVERIFIED; nothing rests on it.

### Applied

All three, in the commit that carries this section.
