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

## Astra R3 - COUNTED, verdict FIX

Dispatched 2026-09-12 against plan blob `ed25107` (HEAD `3459603`),
mirror rebuilt at `C:\Temp\pxar1` (probe clean, `override-r3.toml`,
same sha256), resumed session `01a0985e-1d0d-7940-b544-11e0ffeba5d9`,
background task `Astra R3 debate round`. Wrapper exit 0, `reply-present`.
Route confirmed as before, same session id echoed. Bound with `-Resume`,
`status: clean`, `sealed: sealed` (`binder-r3.json`).

Artifacts: `brief-astra-r3.md`, `astra-r3-reply.md`,
`astra-r3-transcript.txt`, `receipt-r3.json`, `binder-r3.json`.

**Reviewer verdict: FIX.** A PASS, B FIX, C PASS, D FIX. The round-2
repairs are confirmed present; B is a defect inside one of them.

### Session verification

- B, exit contract: `GetUnresolvedProviderPathFromPSPath` on an unknown
  drive throws, and under the script's `Stop` preference that is an
  uncaught terminating error, exit 1, where the header promises 2 for a
  parameter fault. Confirmed by reading the plan's helper: no catch.
  `IsPathRooted` on `bad|root` throwing on 5.1 and not on 7 is the same
  host asymmetry claim 5 of round 1 established for `<`. Confirmed on
  that basis. Fixed: the helper captures the failure and calls `Fail`
  outside its `try`; `-DocsRoot` is checked against one explicit
  forbidden-character set before any path API; the docs-root join goes
  through the same helper; four regression cases assert exit 2 with an
  `ERROR:` line.
- B, the explanation: the reviewer's two probes show PowerShell starting
  git in its own current location, so git answered for the right
  directory in round 2; the fault was the RELATIVE `.git` answer
  reaching .NET `GetFullPath`, which resolves against the process cwd.
  Confirmed against `tools/new-review-mirror.ps1:1234-1244`, which draws
  exactly that distinction. The round-2 fix was right for the wrong
  stated reason; the comment in the tool, the regression test's comment
  and the spec now state the mechanism correctly.
- D follows from B.

### Applied

All of B, in the commit that carries this section. Three of four
budgeted exchanges are spent; R4 is the last before the user's word is
needed to continue.

## Astra R4 - COUNTED, verdict PASS (terminal)

Dispatched 2026-09-12 against plan blob `257f656` (HEAD `cd7aea4`),
mirror rebuilt at `C:/Temp/pxar1` (probe clean, `override-r4.toml`, same
sha256), resumed session `01a0985e-1d0d-7940-b544-11e0ffeba5d9`,
background task `Astra R4 debate round`. Wrapper exit 0, `reply-present`.
Route confirmed as before, same session id echoed. Bound with `-Resume`,
`status: clean`, `sealed: sealed` (`binder-r4.json`).

Artifacts: `brief-astra-r4.md`, `astra-r4-reply.md`,
`astra-r4-transcript.txt`, `receipt-r4.json`, `binder-r4.json`.

**Reviewer verdict: PASS.** A PASS, B PASS, C PASS. The reviewer ran 22
read-only probe cases of the extracted resolver on each host and found no
remaining functional defect. No new finding, no contested point.

### Final adjudication (session)

An adjudicated dry round: no new substantive finding and no outstanding
contested point. The plan at blob `257f656` is HEAD's copy; every finding
from rounds 1 to 3 was verified against source and applied in its own
round, and R4 confirmed each application. Terminal verdict: **PASS**.
Budget: 4 of 4 declared exchanges used; the user's offered extension was
not needed. The plan is frozen at the commit that carries this section.

Status line: GPT-6 Astra (codex exec, session 01a0985e) with Opus 5
(session); 4 rounds; converged, 0 escalated; Verification status FULL;
effective route confirmed.

---

# Mode diff: range cd0e863..HEAD (branch artifact-roots; each round names its head)

## Preflight (2026-09-13)

`tools/artifact-roots.ps1 -RepoRoot <repo>` (SKILL.md preflight step 4)
ran against the real repository before the mirror build; its output is
retained here as `artifact-roots.txt` (`docs-root source: default`). It
resolves the mirror row's `<TEMP>` to the user's temp directory, so this
debate's mirror is built there; the plan debate's mirror at `C:/Temp/pxar1`
predates the declaration.

## Fable whole-branch review (required before round 1)

Dispatched 2026-09-13 via agents/fable-reviewer.md on the exact range
cd0e863..f12b703 with the frozen plan, its Global Constraints, the SDD
ledger and a controller-built diff package (retained round records in the
stat only). Brief: `brief-fable-diff-r1.md`. Raw reply:
`fable-diff-r1-reply.md`. Verdict: **Ready to merge: Yes**, no Critical,
no Important, seven Minor; every ledger minor triaged as ride or closed.

Session adjudication, each finding read against the live file:

| # | Finding | Adjudication |
|---|---------|--------------|
| 1 | notes operating rule doubles "before" | accepted; sentence rewritten |
| 2 | frozen-plan-format.md plan-save citation lacks `-Expect frozenPlan` | accepted; clause added at the plan-save sentence |
| 3 | `-Expect frozenPlan` still accepts a dated directory in the plan parent, unstated | accepted as a stated limit; sentence added to the operating rule (the plan row names a file beside those directories; the rounds copy is the act that spread the record and `-Expect rounds` refuses it) |
| 4 | spec exit map reads code 1 as outside only | accepted; exit map now names the expect mismatch |
| 5 | assert guard refuses a provider-qualified path the resolver could take | accepted as a documented limit; header comment added, behaviour unchanged (no caller passes the form) |
| 6 | sweep glob `hooks/*` is non-recursive | accepted; `hooks/**/*` |
| 7 | writer test no longer observes the emitter creating `.git/parallax` | no change; the trade is stated in the test and test_attestation.py owns the emitter |

All six applications land in one commit ahead of round 1, so the
reviewed head carries them.

## Astra diff R1 - COUNTED, verdict FIX

Dispatched 2026-09-13 against head `aabab81` (range cd0e863..aabab81),
mirror built at the declared temp root (`C:/Users/Brandon/AppData/Local/Temp/pxar2`,
mirror head = source head, enumeration empty in the mirror, client probe
clean: 31 home-scoped skills before the override, 0 after, override sha256
`84d16007...`; tool-surface probe clean: 147 calibration tools, 0 under
the dispatch flags, `node_repl` silent), fresh session
`01a09943-2bbd-7442-bfb6-0692f161fe36`, background task
`Astra R1 debate round`. Wrapper exit 0, `reply-present`. Transcript
header: `model: gpt-6-astra`, `provider: openai`, `reasoning effort: high`,
`sandbox: read-only`, `workdir: C:\Users\Brandon\AppData\Local\Temp\pxar2`.
Bound with `-Fresh` against the sealed prior state: `status: clean`,
`sealed: sealed` (`binder-diff-r1.json`).

Artifacts: `brief-astra-diff-r1.md` (claims plus the code-surface diff),
`astra-diff-r1-reply.md`, `astra-diff-r1-transcript.txt`,
`receipt-diff-r1.json`, `binder-diff-r1.json`, `tool-surface-diff-r1.json`,
`mirror-build-diff-r1.txt`.

**Reviewer verdict: FIX.** Claims 1, 2, 3, 8 PASS. Findings, each read
against the live file before application:

| Claim | Finding | Adjudication |
|-------|---------|--------------|
| 4 | `TEMP=C:\bad\|temp` exits 1 on 5.1 and 0 on 7; conversions at :149, :157, :214 bypass `Resolve-Absolute`; the declaration read at :91 is unhandled | accepted: every conversion now goes through the helper, TEMP is screened with the forbidden set first, the read failure exits 2 |
| 4 | a missing `-RepoRoot`, a bare `-DocsRoot` and an unknown parameter exit 1 with no `ERROR:` line | accepted in part: `-RepoRoot` is optional-with-check and unbound tokens are captured, both exit 2; a named parameter with a missing VALUE stays a binding fault on both hosts, stated in the header and the spec. The new regression also caught a bare token binding POSITIONALLY to `-DocsRoot` (predates the round); binding is now named-only |
| 5 | the slashless-limit comment the brief claimed does not exist; `<git-common-dir>/parallax/...` spellings escape every shape, one of them a writing instruction at application-checkpoint.md:80 | accepted as FIX under the brief's own rule (same named class, on the swept surface): seventh shape added with controls, stated limits written into the sweep comment, the three spellings (application-checkpoint.md, verify-attestation.ps1, write-attestation.ps1) now cite the declaration |
| 6 | the fresh-parent writer case the plan's Task 4 specifies was dropped by the fix wave | accepted: the writer test is two cases sharing one driver, fresh (appeared set is the two directories and the file) and checkpoint-bound |
| 7 | body is 25,985 characters, SKILL citations are :153-154, :324, :389 | accepted, record only: the brief's 25,986 was counted before the linter's line joining; corrected here |

UNVERIFIED by the reviewer: fresh execution of Group 3b and the Python
suites (its Python could not launch); its writer conclusions were source
findings, and the session's both-host runs are the execution evidence.
Applied under the application checkpoint
`20260913-0110-aabab8133365.md` (pre-authorized by the user's answer
"Apply fixes, then finish the pipeline").

## Astra diff R2 - COUNTED, VOID (wrapper exit 1, `workdir-mismatch`)

Dispatched 2026-09-13 against head `cf7109b` (the R1 fix commit), mirror
rebuilt at the same path with `-Force` (mirror head = source head, probe
clean, same override sha256), resumed session
`01a09943-2bbd-7442-bfb6-0692f161fe36`, background task
`Astra R2 debate round`. The wrapper exited 1 and named
`workdir-mismatch` on its last line: the session passed `-WorkdirEvidence`
spelled with forward slashes from a Bash shell, and the transcript header
spells the working directory with backslashes. The wrapper's exit code is
the classification, so the reply is not evidence and was not bound or
read for a verdict; the exchange counts against the budget (2 of 4).
Retained for the record only: `brief-astra-diff-r2.md`,
`receipt-diff-r2.json`, `mirror-build-diff-r2.txt`.

Before re-dispatching, the session probed the binder residual its own
brief had called "ONE": a parameter given twice is a second binding fault
(exit 1 on both hosts, no `ERROR:` line), so the header and the spec now
name two. Checkpoint amendment 2 records the edit.

## Astra diff R3 - COUNTED, verdict FIX

Dispatched 2026-09-13 against head `166501e` (cf7109b carries the R1 fixes,
166501e the residual wording), mirror rebuilt at the same path with
`-Force` (mirror head = source head, probe clean, override sha256
`84d16007...`), resumed session `01a09943-2bbd-7442-bfb6-0692f161fe36`,
background task `Astra R3 debate round`, `-WorkdirEvidence` spelled with
backslashes this time. Wrapper exit 0, `reply-present`. Route confirmed
(`gpt-6-astra`, `openai`, `high`, `read-only`, same session id). Bound
with `-Resume` against a prior state captured from the rollout immediately
before dispatch (the voided R2 advanced it): `status: clean`,
`sealed: sealed` (`binder-diff-r3.json`).

Artifacts: `brief-astra-diff-r3.md`, `astra-diff-r3-reply.md`,
`astra-diff-r3-transcript.txt`, `receipt-diff-r3.json`,
`binder-diff-r3.json`, `mirror-build-diff-r3.txt`.

**Reviewer verdict: FIX.** Claims 3, 4, 5, 6 PASS (the class sweep found no
further hand-spelled root). Claims 1 and 2 FIX:

| Claim | Finding | Adjudication |
|-------|---------|--------------|
| 1 | a third binding-fault class, argument conversion: `-Json:$true` and `-Json:$false` exit 1 on 5.1 and 0 on 7; `-Json:invalid` and `-ErrorAction invalid` exit 1 on both without `ERROR:` | accepted, reproduced on both hosts. Typed binding cannot deliver one exit map, so the tool now has NO param block and parses `$args` itself: unknown, abbreviated or bare tokens, a missing value, a duplicate, a bad `-Json` value and a common parameter all exit 2 with `ERROR:` on both hosts; `-Json true/false` (either host's spelling of the split `-Json:$true`) selects the format |
| 2 | the "TWO residuals" statement is still an undercount; the test comment still says "one" | accepted: header, spec and test comment now state there is no binding residual, with the measured history (one, two, then the conversion class) kept in the spec paragraph |

Session probe of the hand parser on both hosts before the tests were
written: fourteen command lines, identical exit codes and message text on
Windows PowerShell 5.1 and PowerShell 7. Regressions:
`test_every_command_line_fault_is_a_script_fault` (nine cases) and
`test_json_switch_forms_select_the_format_on_both_hosts` (five forms).
Applied under checkpoint amendment 3.

## Astra diff R4 - COUNTED, verdict ESCALATE (budget exhausted, then extended)

Dispatched 2026-09-13 against head `8556599`, mirror rebuilt at the same
path with `-Force` (mirror head = source head, probe clean, same override
sha256), resumed session `01a09943-2bbd-7442-bfb6-0692f161fe36`,
background task `Astra R4 debate round`. Wrapper exit 0, `reply-present`.
Route confirmed. Bound with `-Resume` (prior state = R3 binder's
`nextState`): `status: clean`, `sealed: sealed` (`binder-diff-r4.json`).

Artifacts: `brief-astra-diff-r4.md`, `astra-diff-r4-reply.md`,
`astra-diff-r4-transcript.txt`, `receipt-diff-r4.json`,
`binder-diff-r4.json`, `mirror-build-diff-r4.txt`.

**Reviewer verdict: ESCALATE.** Claim 3 PASS (scope; the sweep still finds
zero offenders). Claims 1 and 2: one NEW substantive finding at exchange
4 of 4, which paused the debate under the budget rule:

| Claim | Finding | Adjudication |
|-------|---------|--------------|
| 1 | an EMPTY inline value is dropped by `-File` preprocessing before `$args` exists, on both hosts: `-Assert:` as the last token vanishes, `-Json:` loses its colon; the resolver then exits 0 with no assertion line, a false clean against the spec's missing-value clause | accepted, reproduced with exact `ArgumentList` on both hosts. The parser now reads the RAW process command line (`[Environment]::GetCommandLineArgs()`, tokens after the script's own path; `$args` only as a fallback when the path is not on that line), which carries every token on both hosts; an empty inline value exits 2 with `ERROR:`. Four regressions plus one that a quoted path with spaces survives the raw split |
| 2 | the "every fault reaches the parser" claim was contradicted by claim 1 | accepted: header, spec and test comment now name the raw command line and record why `$args` was not enough |

The user extended the budget by two exchanges (6 in total) on the
session's recommendation; the fix is applied under checkpoint amendment
4 and R5 is the confirming round.
