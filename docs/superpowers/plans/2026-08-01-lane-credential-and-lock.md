# Lane Credential Ownership and Concurrency Lock Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Status: FROZEN at revision 17.** The user lifted the round cap and directed that this plan iterate until the cross-vendor reviewer issued an actual PASS rather than stopping at "converged with amendments". It first did at round 13; the required whole-artifact fable review then reopened it, and four more rounds followed. The terminal PASS is round 18, on all ten tasks and on the implementer packet: "PASS. The implementation contract can freeze." Changes now require reopening the debate with a new round appended to the record; the implementer never edits this plan.

**Goal:** Stop the backup lane from copying the user's kimi-code credential. Give the lane its own login, reach it through a junction so one file holds it, guard the shared lane home with a liveness-anchored lock, stop the doctor touching credentials at all, and repair the Windows CI job this branch already broke.

**Architecture:** A persistent LANE HOME holds one credential produced by its own login. Each debate still gets a throwaway `KIMI_CODE_HOME`, but its `credentials` directory is a JUNCTION to the lane home's, so a refresh writes through to the single file instead of forking a copy. A persistent lock file in the lane home serializes access; every state transition is written in place under one exclusive handle, and the file is never unlinked. Staleness is decided by process liveness only, never by a clock.

**Tech Stack:** PowerShell 5.1 and 7 (both hosts, both gated), Python 3.12 + pytest, Markdown contract regions with the `contract:start`/`contract:end` checker.

## Revision history

- **r17, this one** — after Sol plan round 17, which passed all ten tasks and confirmed both packet exclusions were right, then found that r16's packet boundary contradicted itself two ways. "Everything above this line" swallows the revision history, which the very next sentence excluded; and this section's own body is not above that line even though the packet must carry it, so the rule failed to include the rule. Both are the hazard of a RELATIVE boundary in a document that keeps growing. It is now an exhaustive numbered list of seven included blocks and a named list of what is excluded, with the failed wording recorded so nobody reintroduces it as a tidier phrasing.
- **r16** — after Sol plan round 16, which passed all three r15 content fixes and every one of the ten tasks on its own text, then found the last blocker OUTSIDE the tasks entirely: the HANDOFF. Fifteen rounds hardened what each task says while the packet the implementer would actually receive was never written down, and the one I stated when announcing the build — Global Constraints plus the task — is too narrow. `Fixed names and values` is a separate section, so under that packet Task 3 would have had to invent the token regex, the hostname comparer, the tick representation, the pid rule, the wait and poll bounds and the confirmation-hash rule, and Task 8 would have had to invent the lane-home path its recovery commands print, in a plan whose entire premise is that the implementer invents nothing. The packet is now a section of the plan rather than a habit of whoever dispatches it: the whole preamble plus one task, verbatim. Broadening it beats copying the values into each task, because duplicated constants drift and one edited copy becomes two contradictory definitions — which is the defect class this debate found three separate times, at r7, r14 and r15.
- **r15** — after Sol plan round 15, which passed seven of ten tasks and confirmed both consequences r14 drew beyond the literal instructions were correct, then found three blocking defects, two of them created by r14's own new semantics. The `debateHome` normalization trimmed a trailing separator UNCONDITIONALLY, which takes a drive root `C:\` to `C:` — a drive-relative path that resolves against that drive's current directory, so the comparison would have compared two different things — while nothing in Task 3 forbids a root-valued `-DebateHome` and the builder already treats a drive root as its own case at `tools/new-kimi-lane-home.ps1:89-99`; the trim is now guarded by a `GetPathRoot()` equality test, with root-spelling tests under both hosts. Task 5's exit code 3 still read "the exclusive handle OR a live holder" while Task 3's now covered LIVE or UNMEASURABLE, which is the same two-definitions-of-one-value shape r7 fixed for `host` and r14 fixed for the lock tool's own table; the wrapper's wording now matches. And the post-deletion release seam r14 added was described but never NAMED, while the other two seams carry exact shared strings precisely because production and tests must agree on them; it is now `PARALLAX_LANE_HOME_REMOVE_RELEASE_FAULT` with its scope, its skip-the-mutation behaviour, its fixed code 5, and its stderr sentinel all frozen. The fable artifact also gained an honest provenance limit — a subagent writes no transcript, so the file is this session's reproduction of a returned report and nothing can prove it was not altered in transcription, though every claim in it resolves against the repo — and the three remote checks were re-run rather than remembered, which corrected one of them: a bare `gh run list` is NOT empty, it returns runs on `main`, and only the branch-filtered form is evidence.
- **r14** — after Sol plan round 14, which agreed with both judgment calls r13 made rather than took (a `-DebateHome` mismatch is exit 2 because matching all five identity fields means there is no competing holder, so contention would be false; a same-host UNKNOWN liveness is `N/A` because staleness requires proof the owner is gone and the protocol's deliberate fail-closed outcome was reported successfully) and then found the execution detail around them defective in four tasks. r13 wrote that `debateHome` is "not part of the comparison" one paragraph above a table that compares it, and never said HOW to compare a path; it is now excluded from holder-identity equality but compared separately once all five identity fields match, under one frozen normalization. The new UNMEASURABLE liveness was defined but never routed through the acquire table, so the plan declared a third state and told the implementer nothing about it in the one mode that mutates. A foreign-host record's status liveness was still open, and could have been answered from a coincidentally matching local PID; it is now `UNKNOWN` always, with the local process table not consulted at all. Task 6's two new behaviours had no oracles that could fail: the wrong-`-Path` case tested "identity mismatch" when `debateHome` had just been excluded from identity, and post-deletion release failure had no test at all. Task 7 told the runner to build home C with "the same six steps" while writing no marker, when step 5 IS writing the marker. And Task 8's verification pinned "lock-status reporting" generically, which a wrong `UNKNOWN` mapping or a case-sensitive host comparison would have satisfied. Also retained: the fable-reviewer report, which round 14 correctly listed as UNVERIFIED because nothing inspectable existed, now sits at `rounds/2026-08-01-cred-lock/fable-whole-plan-review.md`.
- **r13** — REOPENED after the fable-reviewer whole-artifact read, which the thirteen adversarial rounds could not substitute for: every one of them read the plan task by task, and three consecutive rounds found defects inside text the previous round had just rewritten. No Criticals. TWO IMPORTANTS, both real and both invisible to a per-task read. The acquire table keyed on "identity fields" and never defined them, leaving `debateHome` in an undecided cell even though it is mandatory on every acquire, is a record field, and is what Task 6's Remove uses as its identity check; the five identity fields are now named, `debateHome` is recorded but excluded from the comparison with a mismatch as exit 2 rather than contention, and an idempotent re-acquire is frozen as writing NOTHING. And `-Status` declared a `UNKNOWN` liveness value that no rule ever assigned, because the only unmeasurable case was defined as ALIVE; liveness now has three outcomes, mutating modes treat unmeasurable as alive and refuse to reclaim while status reports UNKNOWN rather than claiming a measurement it did not make, and the doctor gains the row that consumes it plus the host comparison its foreign-host row always needed. Six Minors also folded in rather than deferred, each removing an invention: Remove-mode release precedence, the validator named in Task 5, C's creation sequence and its lack of a marker, the three-logins generalization recorded against measurement 11's two, the absolute-key fixture construction, and the debate-home/lane-home terminology collision in shipped contract text.
- **r12** — after Sol plan round 12. Two mechanical corrections, no behaviour added or cut. r11's new matrix was right, but an older sentence beside it still said the post-failure assertions are "the same in every case", which the matrix contradicts, so it is now scoped by the Remove outcome. And the matrix dropped one of the four main phases it was meant to cover: command and capture appeared in the production definition but not in either failure row, so a removal failure could have masked a command failure with nothing to catch it.
- **r11** — after Sol plan round 11. Nine tasks pass byte-unchanged. Both remaining defects were contradictions inside r10's own new oracle prose, not in the production contract. The combined cleanup oracle demanded an IMPOSSIBLE end state: a main-phase failure plus a removal failure, while also asserting the home absent and the lock free, when a deterministic sentinel refusal leaves the home present and the record unchanged. It is replaced by a three-row outcome matrix, which CUTS prose rather than adding it, on the reviewer's explicit advice that the state machine is converging and what to trim is duplicated oracle text. The seed matrix gained the direction that was never covered: a failing read with a SUCCEEDING release. And "every failure names only the field" contradicted the launch-failure and read-or-parse oracles, which have no matched field; it is now scoped to credential-match failures, with the other classes keeping their own sanitized messages.
- **r10** — after Sol plan round 10. Nine tasks pass byte-unchanged; all three remaining defects are Task 7 oracle gaps rather than design. The custody sequence had grown to four phases but the cleanup and precedence rules still named only the command, so a runner could mishandle a pre-command, merge or guard failure and pass every listed test; the MAIN OPERATION is now defined as all four phases, with combined oracles for each against a simultaneous removal failure, and the same rule applied to seeding. The helper promised to sanitize the timeout, launch-failure and error paths, but no test reached any of them; three exception-path oracles now do. And item 6, which deliberately has no lock, was still covered by a rule saying every post-command re-read happens while the hold is in force, which it cannot.
- **r9** — after Sol plan round 9. Nine of ten tasks pass byte-unchanged; every remaining defect is a consequence of r8's custody change and all three are in Task 7. r8 said the `finally` always calls `-Remove`, but a REFUSED build returns no nonce and Task 6 already released internally, so that path would have called removal with nothing to confirm; custody is now gated on a `custodyReceived` flag set only after Build exits 0 and its JSON parses, and item 4's routing row is split into successful and failed halves. The secret union had to be seeded while a hold was in force, but before the first build no hold exists; seeding is now the SOLE direct-acquire exception, with its own oracle. And the deliberate expiry writes had no declared place in the sequence, so an implementation could force expiry before the build, mutating a shared credential unlocked, and still pass everything; there is now an explicit PRE-COMMAND phase inside custody, and the contention oracle covers it.
- **r8** — after Sol plan round 8, which found a contradiction between two of my own tasks: Task 6 makes a successful build RETAIN its lock and return the nonce, while Task 7's routing told the runner to acquire again before every command and release in its own `finally`. The second acquire would have contended with the retained hold and the plain release would have broken `-Remove`'s identity confirmation. The builder is now the acquisition everywhere. Also: the shared helper had no file to live in, Task 7's own verification never collected the support suite, and one count said five modules where another said six.
- **r7** — after Sol plan round 7. Tasks 1, 2, 3, 4, 5, 6, 8, 9 and 10 now PASS; only Task 7 carried blocking defects, and all four were in the two surfaces r6 had just added. Its manual setup had no executable lifecycle: it must run the login wrapper, whose owner fields are mandatory, then write a marker under a lock, but the only owner rule resolved once per MODULE RUN and setup happens earlier. Its secret set had no timing contract, so a value ISSUED BY the command being scanned did not exist when the set was built, which is exactly C's rotation case. Neither the locking nor the guard had any oracle at all, so a runner with no locking and no helper passed all seven functional items. And four of the seven items never said which home they used. Also fixed: the exhaustive MALFORMED definition contradicted the per-state property rule by covering only UNKNOWN fields, leaving `host` on a free record with two definitions.
- **r6** — after Sol plan round 6. Preprocessing written in r5 was accidentally applied to `-Status` and `-ResolveOwner`, which would have made a read-only status of a malformed record exit 4 instead of reporting it. The custody-emission oracle pointed at the fault seam's OLD position, which cannot prove the boundary it exists to prove. The secret guard ran only at write time, while a pytest failure message prints captured streams first. That guard compared against optional credential fields that may be empty, and an empty string matches every output. And homes A and B were left unlocked despite performing authenticated dispatches that can refresh a 900-second token on their own.
- **r5** — after Sol plan round 5, with the cap lifted. Tasks 4 and 10 PASS. Two findings are SECURITY findings in a public repo and neither had occurred to me: Task 7 recorded the client's complete streams into a COMMITTED probe record, which can capture a credential value, and its token-rotation assertion compared token values inside an `assert`, where pytest's introspection prints both operands on failure. Both now have explicit guards. Three Task 3 partition defects survived r4: a free record carrying a held-only KNOWN field was not covered by the unknown-field rule, `-MalformedOverride` on a well-formed FOREIGN-HOST record had two different outcomes, and code 5's description covered only mismatch while three rows returned it for "nothing applicable". A mechanical preprocessing order now precedes the release table. Task 6's `$buildCompleted` was set before the custody JSON was emitted, so a failure to emit would retain a lock whose caller never received its nonce. Task 9's login literal omitted `-LaneHome`, so a custom lane home would build against one home and authenticate another. Task 2's fixture change had no oracle in its own task, and Task 5's exit table omitted two codes.
- **r4** — after Sol plan round 4, the cap. Every FIX accepted on the record; Sol stated they are mechanical and require no design escalation, and none was contested, so this is CONVERGED WITH AMENDMENTS per debate-protocol.md. The record-class partition is now total: `-MalformedOverride` covers every READABLE MALFORMED record rather than only unparseable bytes, an extra field on a FREE record is malformed too, exit 4 is narrowed so it cannot contradict the two overrides, the token regex is unified on 32 lowercase hex, and missing-file behaviour is frozen per mode. Also: the login wrapper's pre-lock bootstrap is now an explicit, bounded exception; its stream-inheritance oracle is TEMPORAL, because a wrapper that buffered both streams and replayed them would have passed the r3 test; the builder's cleanup needs TWO flags, since `!$buildCompleted` is also true when acquire itself failed; the doctor's aggregate is a total order including `N/A`; and the two-hash check no longer claims to establish WHO changed the bytes.
- **r3** — after Sol round 3, which found four CROSS-TASK contradictions r2 introduced: an acquire table that overlapped its own rows, a doctor override the lock forbade, a stream contract that was not jointly implementable, and a fixture contract that forbade what its own oracle required. Also fixed a region-comparison step that compared raw bytes which can never be equal.
- **r2** — after Sol rounds 1 and 2. Thirty findings. The load-bearing four: `OpenOrCreate` let a crash-truncated lock be stolen; idempotent acquire could not receive the nonce it required; the junction test was vacuous; and several live gates asserted invariance that holds when the command failed.
- **r1** — first draft, unreviewed.

Design spec: `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md` (revision 2, CONVERGED, PASS). Spec debate session `019fbb61-cc35-75b3-b34a-5b52219ad5bd`. Plan debate session `019fbb82-9e35-7b72-a64e-59fb60b981cd`. Replies retained at `docs/superpowers/plans/rounds/2026-08-01-cred-lock/`.

## Global Constraints

- **The invariant governing every check: an unmade, failed, or unreadable measurement is never a clean one.** A guard that cannot be evaluated REFUSES; it never skips. A live gate whose setup fails is a FAILED gate, never a skipped branch.
- **A claim may never be wider than its evidence.**
- **Every assertion of invariance requires a positive control first.** An unchanged file, hash, or absent side effect proves nothing unless the command that was supposed to act EXITED 0 and produced its expected output.
- The canonical backup model id may appear ONLY in `skills/multi-model-verify/references/model-prompting-notes.md` and `evals/multi-model-verify/test_backup_lane.py`.
- The client binary is `~/.kimi-code/bin/kimi.exe`, always by ABSOLUTE PATH.
- **Never print, log, or commit a credential VALUE.** Names, presence and file hashes only. Fixtures use obviously fake values.
- **Never `git add -A` and never `git add -u`.**
- Files under `skills/multi-model-verify/references/` are checked for the ABSENCE of backslashes.
- Contract regions must sit WHOLE inside a single pin. Adding or removing one means editing `DECLARED_REGIONS`.
- **Tests change FIRST for every live-verified contract, then the text.**
- Windows PowerShell 5.1 compatible, ASCII ONLY, in every `tools/*.ps1`. `-Encoding ascii`, never `utf8`.
- **Dual-host selection is `PARALLAX_PS_HOST`.** Copy `evals/multi-model-verify/test_codex_context_probe.py:35-67`. **Every module that touches Windows filesystem behaviour carries a module-level skip guard testing `os.name != "nt"`**, because Ubuntu supplies `pwsh` and a selector that merely finds a host will happily collect Windows tests there.
- **Every dual-host verification command in this plan is written TWICE, once per host.** A single invocation tests whichever selector happens to be in the environment, which is how this repo shipped a lock that did not lock on pwsh.
- Gate, all four: `skill_lint.py skills/multi-model-verify --strict`, `skill_scanner.py skills`, `run_trigger_evals.py`, `python -m pytest evals -q`.
- Destructive probes NEVER target the real `~/.kimi-code`, the real `$env:USERPROFILE`, or any drive root.

## Measured facts the plan is built on

**The fork (1-4).** `expires_in` 900s; a refresh rotates BOTH tokens; a copy that refreshes strands the source; the source's next use blanks it.
**Redirect is closed (5).** An absolute `oauth.key` does not resolve.
**The junction works (6-10).** Reads through; refresh writes THROUGH; no admin; an ACL does NOT propagate through; recursive delete does NOT delete through, BOTH hosts.
**Two logins coexist (11).**
**Concurrency was observed to survive (12, 13), n=1.** NOT relied on.
**The owner anchor (14, 21).** The harness-invoked shell's parent is stable and dies with the session; from a NESTED shell it names an intermediate process that exits. Resolve ONCE, pass EXPLICITLY.
**`provider list` proves nothing and mutates nothing (16, 17).**
**The credential schema (18).** Six keys.
**The exclusive-handle protocol is identical on both hosts (19).**
**Time representation (20).** Ticks round-trip as `Int64` on both; a date STRING is `String` on 5.1 and `DateTime` on 7.

## Fixed names and values

- Lane home `$env:USERPROFILE\.parallax-kimi-review`; credential `<lane-home>\credentials\kimi-code.json`; lock `<lane-home>\lane.lock`
- Lock `version` `1`. States `free`, `held`. No others.
- Required credential fields `access_token`, `refresh_token`, `expires_at`. Optional `scope`, `token_type`, `expires_in`.
- **`-DebateId` and `-Nonce` and their confirm forms match `\A[0-9a-f]{32}\z`** — exactly 32 lowercase hex, from `[System.Guid]::NewGuid().ToString("N")`. There is no second, broader token rule; r3 carried both and they conflicted.
- The DRIVER generates the debate id once, at the start of the debate, and retains it with the owner identity and the nonce for every later call.
- Hostname source `$env:COMPUTERNAME`, compared case-INSENSITIVELY. Tick strings `\A[0-9]+\z`, compared as STRINGS. `ownerPid` a JSON integer > 0. `-WaitSeconds` >= 0. `-PollSeconds` > 0. `-ConfirmSha256` exactly 64 hex, compared case-insensitively.

## The implementer's task packet

**Every implementer receives exactly these blocks, verbatim: (1) the `For agentic workers` instruction; (2) Goal, Architecture and Tech Stack; (3) Global Constraints; (4) Measured facts the plan is built on; (5) Fixed names and values; (6) this entire `The implementer's task packet` section; and (7) its ONE assigned task.** It receives none of the Status text, Revision history, design and debate session pointers, other tasks, Debate record, raw rounds, or debate conversation.

The list is exhaustive on purpose. An earlier wording said "everything above this line", which failed twice over: the revision history is above the line and the next sentence excluded it, and this section's own body is not above the line even though the packet must carry it.

The narrower packet of Global Constraints plus the task alone is WRONG and was caught before any building started. Task 3 validates against the token regex, the hostname comparer, the tick representation, the pid rule, the wait and poll bounds and the confirmation-hash rule, and Task 8 emits recovery commands against the fixed lane-home path; all of those live in `Fixed names and values`, so under the narrow packet both tasks would have had to INVENT them, in a plan whose whole premise is a zero-judgment implementer.

Broadening the shared packet is the fix rather than copying the values into each task, because duplicated constants drift and one edited copy is then two contradictory definitions — the exact defect class this debate found three separate times.

---

### Task 1: Repair the Windows CI job

**Do this first. It is a merge blocker independent of everything else and is already broken at HEAD.**

`.github/workflows/skill-evals.yml:84` and `:95` both pass `evals/multi-model-verify/test_kimi_lane_lock.py` to pytest. That file does not exist: `775472c` deleted it with `tools/kimi-lane-lock.ps1` and did not touch the workflow. `python -m pytest <that path> -q` exits 4 with `ERROR: file or directory not found`. Verified never pushed and never run: `git branch -r --contains HEAD` empty, `git ls-remote --heads origin` returns only `refs/heads/main`, `gh run list --branch feat/kimi-code-backup-lane` returns no runs.

Task 3 later creates a file at that path. **Do not rely on that coincidence.**

**Files:** modify `.github/workflows/skill-evals.yml:79-99`; create `evals/tools/check_workflow_paths.py`; append to `evals/multi-model-verify/test_backup_lane.py`.

- [ ] **Step 1:** Write `check_workflow_paths.py` — pure Python, no PowerShell, no platform branch, so the ubuntu job runs it. **Two checks, not one:**
  - every `evals/...py` token named in the workflow exists on disk;
  - **HOST PARITY**: a declared set of required dual-host modules is present in BOTH Windows pytest steps. Existence alone is not an oracle for Task 10, because a module omitted from one host step still exists and stays green.

  **The initial required set is exactly these four**, the modules that survive in the workflow once the orphan is removed. It is not the implementer's to choose:

  - `evals/multi-model-verify/test_attestation.py`
  - `evals/multi-model-verify/test_codex_context_probe.py`
  - `evals/multi-model-verify/test_review_mirror.py`
  - `evals/multi-model-verify/test_kimi_round_evidence.py`

  Task 10 adds its SIX named modules to this set.

  Add tests asserting both checks. The path check must FAIL now.
- [ ] **Step 2:** Remove the orphaned line from both steps. Add nothing else; Task 10 adds the new modules once they exist.
- [ ] **Step 3: Verify.** `python evals/tools/check_workflow_paths.py` prints nothing, exits 0; the tests pass. Mutation-test BOTH checks: add a nonexistent path and confirm it is reported; remove one required module from ONE Windows step and confirm parity fails. Revert both.

---

### Task 2: Credential structural validation

**Files:** create `tools/read-kimi-credential-state.ps1` and `evals/multi-model-verify/test_kimi_credential_state.py`; modify `evals/multi-model-verify/test_kimi_lane_home.py:316-317`.

Output is exactly one line: `{"status":"<status>","detail":"<detail>","fields":[<names>]}`.

| status | detail | when |
|---|---|---|
| `ok` | `valid` | every required field present and well-typed |
| `absent` | `no-file` | the path does not exist |
| `unreadable` | `read-failed` | the path exists but the bytes cannot be read |
| `malformed` | `not-json` | the bytes do not parse as JSON |
| `malformed` | `not-object` | it parses but is not an object |
| `malformed` | `missing-field` | a required field is absent |
| `malformed` | `wrong-type` | a required field is present with the wrong type |
| `malformed` | `blank-token` | `access_token` or `refresh_token` is empty after trimming |

**Defect precedence, frozen.** One document can carry several defects and only one `detail` is emitted. Evaluate in this order, return the FIRST that fires: `not-json`, `not-object`, `missing-field`, `wrong-type`, `blank-token`. Tests include a document carrying the last three at once, asserting `missing-field`.

**`fields`** lists names observed in the parsed object, sorted with `[System.StringComparer]::Ordinal`, and is `[]` for exactly `absent`, `unreadable`, `not-json`, `not-object`. Names only.

**Types.** `access_token`, `refresh_token`: .NET `String`, non-empty after `Trim()`. `expires_at`: `Int32` or `Int64`. Anything else is `wrong-type`, specifically a fractional number, a boolean, `null`, the string `"123"`, and an `Int64`-overflowing value. **No truthiness and no freshness test:** `0` is VALID, a past expiry is VALID. On a duplicate key both readers take the last occurrence; the validator validates what the reader returned. **That behaviour needs its own opposite-direction oracle**, because an implementation that rejects duplicates outright, or that keeps the FIRST value, passes every other case: one fixture with an invalid first value and a valid last value must be `ok`, and one with a valid first value and an invalid last value must report the LAST value's precise defect. Both run under both hosts.

- [ ] **Step 1: Write the failing tests.** One per row; the precedence case; `0` is `ok`; past expiry `ok`; fractional, boolean, `null`, `"123"`, overflow each `wrong-type`; all optional fields absent is `ok`; unknown extra field is `ok`; whitespace-only token is `blank-token`; `fields` sorted; `[]` for each of the four statuses; no output line contains a fixture token value. The `unreadable` fixture: create, deny read to the current identity with `icacls`, run, restore in a `finally`. Module guard `os.name != "nt"`; both hosts.
- [ ] **Step 2: Write the script.**
- [ ] **Step 3: Update the fixture** at `:316-317` to add a fake `refresh_token` and an integer `expires_at`.
- [ ] **Step 3b: Move the builder suite's host selector refactor HERE, out of Task 6.** Replace `shutil.which(...)` at `evals/multi-model-verify/test_kimi_lane_home.py:21` with the `PARALLAX_PS_HOST` pattern from `evals/multi-model-verify/test_codex_context_probe.py:35-67`, and add a module-level `os.name != "nt"` skip guard. Task 6 then treats this refactor as already done.
- [ ] **Step 3c: Give the fixture change its own oracle, in THIS task.** Without it, omitting step 3 still passes: the builder suite does not structurally validate `_fake_profile`'s credential, and until step 3b its selector ignored `PARALLAX_PS_HOST` entirely, so the advertised two-host gate ran one host. Add a test that builds `_fake_profile`, runs the new validator against the credential it wrote, and requires `status` of `ok` under EACH selected host.
- [ ] **Step 4: Verify, per host:**
```
$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals/multi-model-verify/test_kimi_credential_state.py evals/multi-model-verify/test_kimi_lane_home.py -q
$env:PARALLAX_PS_HOST = "pwsh.exe";       python -m pytest evals/multi-model-verify/test_kimi_credential_state.py evals/multi-model-verify/test_kimi_lane_home.py -q
```

---

### Task 3: The lock tool

`tools/kimi-lane-lock.ps1` is new. The previous file of that name was deleted at `775472c`; do NOT restore it. Read it once for the traps its header lists (`git show 775472c^:tools/kimi-lane-lock.ps1`), then write fresh. Its 45-minute clock, its last-writer-wins acquire, and its date-string timestamp are the three things this replacement exists to not have.

**Files:** create `tools/kimi-lane-lock.ps1` and `evals/multi-model-verify/test_kimi_lane_lock.py`.

**The record.** One line of ASCII JSON. Every time value is a DECIMAL STRING, never a number and never a formatted date: measurement 20 shows an integer is safe on both hosts and a date string is not, and a decimal string is safe by construction because neither reader coerces a non-date-shaped string.

```
{"version":1,"state":"held","host":"<name>","ownerPid":<int>,"ownerStartTicksUtc":"<digits>","debateId":"<32 hex>","nonce":"<32 hex>","debateHome":"<path>","acquiredTicksUtc":"<digits>"}
```

A free record is exactly `{"version":1,"state":"free"}`. `host` and `debateHome` must be non-blank strings.

**Property rules, stated per state so no reachable shape falls between them.** A HELD record carrying any property not named above is MALFORMED. **A FREE record carrying ANY property other than `version` and `state` is MALFORMED** — that wording, and not "unknown field", is what is required: a free record carrying `host` or `nonce` carries a KNOWN property that is simply illegal in that state, and an unknown-field rule does not reach it. Tests cover both a held-only known property and a wholly unknown one on a free record.

**Parameter sets.**

```
-Acquire  -LaneHome <p> -DebateId <t> -OwnerPid <n> -OwnerStartTicksUtc <s>
          -DebateHome <p> [-Nonce <t>] [-WaitSeconds <n>] [-PollSeconds <n>]
-Release  -LaneHome <p> -DebateId <t> -OwnerPid <n> -OwnerStartTicksUtc <s>
          -Nonce <t> [-WaitSeconds <n>] [-PollSeconds <n>]
-Status   -LaneHome <p> [-WaitSeconds <n>] [-PollSeconds <n>]
-ForceRelease -LaneHome <p> -ConfirmHost <s> -ConfirmOwnerPid <n>
              -ConfirmOwnerStartTicksUtc <s> -ConfirmDebateId <t> -ConfirmNonce <t>
              [-WaitSeconds <n>] [-PollSeconds <n>]
-MalformedOverride -LaneHome <p> -ConfirmSha256 <hex> [-WaitSeconds <n>] [-PollSeconds <n>]
-ResolveOwner
```

`-WaitSeconds` defaults to `0`; `-PollSeconds` to `2`. **Every LOCK-FILE mode accepts both, `-Status` included, because each takes the same exclusive handle. `-ResolveOwner` accepts neither**, because it touches no lock file at all.

**The exit-code guarantee is scoped to SUCCESSFULLY BOUND invocations**, and says so in the header. PowerShell's parameter binder rejects an unknown name, a missing mandatory value, or an ambiguous parameter set BEFORE any script code runs, and that failure exits 1. The deleted lock had exactly this shape — `[CmdletBinding]` with `[switch]` mode selectors and a typed `[int]$WaitSeconds` (`775472c^:tools/kimi-lane-lock.ps1:36-50`). Hand-rolling `$args` parsing to own that path was considered and rejected: it trades a documented, testable refusal for a large hand-written parser that can itself be wrong. **What the tests must guarantee instead is the property that matters: a binding failure exits nonzero and MUTATES NOTHING.** All value-shaped parameters are declared `[string]` and parsed inside the script, so no *value* can fail binding; only the invocation SHAPE can.

| Code | Meaning |
|---|---|
| 0 | the mode succeeded |
| 2 | a parameter value was refused, or owner resolution failed |
| 3 | contention: the handle, or a holder that is LIVE or UNMEASURABLE, and the wait budget expired |
| 4 | MUTATING FILE MODES ONLY: the record is MALFORMED or names a foreign host, and the applicable confirmed override is NOT the mode being run. `-Status` never emits it |
| 5 | a release or override was refused: either there was nothing applicable to release, or the supplied identity or hash did not match |
| 6 | the file is UNREADABLE, a write or flush failed, or any unclassified runtime failure |
| 1 | reserved for PowerShell's own parameter-binding refusal; never emitted by script code |

**The file-open protocol.** `OpenOrCreate` is FORBIDDEN: it cannot distinguish a file this call created from a pre-existing zero-length file, and a crash after `SetLength(0)` leaves exactly that, which it would read as free and STEAL.

1. Try `CreateNew`/`ReadWrite`/`None`. Success means this call created it.
2. On `IOException` because it exists, open `Open`/`ReadWrite`/`None`.
3. On `IOException` because another process holds the handle: CONTENTION. Wait `-PollSeconds`, retry until the budget expires, exit 3.
4. **A pre-existing zero-length file is MALFORMED, not free.**
5. Under the handle: read, decide, `SetLength(0)`, `Position = 0`, write, `Flush($true)`, close. **The file is never deleted by any path.** Close in a `finally`.

**Missing-file behaviour, frozen per mode.** Only ACQUIRE may create the file, initializing it to `free` and then proceeding through its table. `-Status` on a missing file reports `{"state":"free"}` and **creates nothing**. `-Release`, `-ForceRelease` and `-MalformedOverride` on a missing file exit 5 and **create nothing**. Every one of these has a test asserting the file's continued nonexistence.

**THE IDENTITY FIELDS ARE EXACTLY FIVE: `host`, `ownerPid`, `ownerStartTicksUtc`, `debateId`, `nonce`.** The table below said "identity fields" without ever defining them, which left `debateHome` in an undecided cell: it is mandatory on every acquire and it IS a record field, so an implementer could reasonably read it either way, and Task 6's Remove uses this very call as its identity check.

**`debateHome` is EXCLUDED from holder-identity equality but COMPARED SEPARATELY, after all five identity fields match.** Saying it was "not part of the comparison" contradicted the table, which does compare it. The two-stage shape is the point: the five fields decide WHO holds the lock, and `debateHome` then decides whether that holder is talking about the debate it thinks it is. Two callers cannot differ in `debateHome` while matching all five identity fields unless one is confused, so a mismatch is a caller error and exits 2, never 3: converting it to contention would be wrong, since it IS the same holder. This is what makes Task 6's Remove reject a wrong `-Path` at the lock rather than downstream at the sentinel.

**`debateHome` equality is normalized before comparison, by one stated algorithm:** `[System.IO.Path]::GetFullPath()` to an absolute path; then `[System.IO.Path]::GetPathRoot()` of that result; then, **only when the normalized string does NOT equal its own root under ordinal case-insensitive comparison**, a single trailing directory separator trimmed; then an ORDINAL CASE-INSENSITIVE comparison of the results. Without this the plan froze a comparer for the hostname and for the tick strings but left this one to invention. **The root guard is not decoration.** An unconditional trim takes a drive root `C:\` to `C:`, which is not the same path at all — it is drive-relative and resolves against that drive's current directory — and nothing in Task 3 forbids a root-valued `-DebateHome`, so the comparison would silently compare two different things. The builder already treats a drive root as its own case for exactly this reason, at `tools/new-kimi-lane-home.ps1:89-99`. Tests, under BOTH hosts: two EQUIVALENT SPELLINGS of one non-root path — a relative form and a trailing-separator form — compare equal; two equivalent spellings of a drive ROOT compare equal and normalize to the same absolute root rather than to a trimmed one; and a genuinely different path compares unequal.

**An idempotent re-acquire WRITES NOTHING.** It reprints the stored nonce and leaves the record byte-identical, `acquiredTicksUtc` included, so a re-acquire can never be mistaken for a fresh acquisition in the record.

**Acquire, over READABLE, WELL-FORMED, SAME-HOST records.** Foreign-host is exit 4, malformed is exit 4, unreadable is exit 6, handle contention is exit 3; all four are decided before this table and are not rows in it.

| Record state | `-Nonce` | Outcome |
|---|---|---|
| `free`, or `held` with a DEAD owner | absent | acquire or reclaim, generate a NEW nonce, print it |
| `free`, or `held` with a DEAD owner | supplied | exit 2 — a nonce may never be reused for a new acquisition |
| `held`, LIVE, all five identity fields equal, `-DebateHome` equal | supplied and equal | idempotent success, reprint the nonce, write NOTHING |
| `held`, LIVE, all five identity fields equal, `-DebateHome` DIFFERS | supplied and equal | exit 2 — caller error, not contention |
| `held`, LIVE, the four non-nonce identity fields equal | absent, or supplied and different | contention |
| `held`, LIVE, any of the four non-nonce identity fields differs | either | contention |

Rows 5 and 6 keep a lock debate-scoped rather than session-scoped: one session holds one debate's lock and never silently displaces its own other debate. After the split, row 4 is the `-DebateHome` refusal.

**A same-host UNMEASURABLE holder follows every row above that is not the DEAD row.** It is treated exactly as LIVE for routing: exact identity with an equal `-DebateHome` is idempotent, a differing `-DebateHome` is exit 2, any competing identity contends, and NOTHING reclaims it. Exit code 3's meaning covers contention against a LIVE or UNMEASURABLE holder alike. The fault seam tests BOTH directions: an exact-identity re-acquire under the seam succeeds idempotently, and a competing identity under the seam contends rather than reclaiming.

**Preprocessing for MUTATING FILE MODES ONLY — `-Acquire`, `-Release`, `-ForceRelease` and `-MalformedOverride`.** `-Status` does NOT run it and follows its own read-only rule below, which returns 0 on a malformed record; `-ResolveOwner` performs no lock-file operation at all. Applied before the release table so the partition is mechanically total, these four steps run in order and only what survives them reaches the table:

1. **Unreadable** file: exit 6, every mode.
2. **Readable but MALFORMED**: exit 4 for every mode EXCEPT `-MalformedOverride`, which proceeds to its hash rows.
3. **Readable, WELL-FORMED, FOREIGN-HOST held**: exit 4 for `-Acquire`, `-Release` and `-MalformedOverride`; `-ForceRelease` proceeds to its identity rows. This is the only mode permitted to act on a foreign-host record, and scoping it here is what removes the r4 overlap where a well-formed foreign-host record matched both "well-formed, exit 5" and "foreign-host, exit 4".
4. Everything remaining is a missing file, a `free` record, or a same-host well-formed `held` record.

**Release and the overrides, over what survives preprocessing.**

| Mode | Record | Outcome |
|---|---|---|
| `-Release` | missing file | exit 5, creates nothing |
| `-Release` | `free` | exit 5 — nothing applicable, the signature of a late duplicate release |
| `-Release` | `held`, complete identity equal | write `free`, exit 0 |
| `-Release` | `held`, any field differs | exit 5, record untouched |
| `-ForceRelease` | missing file, or `free` | exit 5 |
| `-ForceRelease` | `held` (same-host OR foreign-host), complete identity equal INCLUDING `-ConfirmHost` | write `free`, exit 0, report what it displaced |
| `-ForceRelease` | `held`, any field differs | exit 5, record untouched |
| `-MalformedOverride` | missing file | exit 5 |
| `-MalformedOverride` | readable, WELL-FORMED, free or same-host held | exit 5 — this mode is only for malformed records |
| `-MalformedOverride` | **any READABLE MALFORMED record**, hash equal | write `free`, exit 0 |
| `-MalformedOverride` | any readable malformed record, hash differs | exit 5 |

Tests cover every FOREIGN-HOST and mode pairing explicitly, because that intersection is where r3 and r4 both left an overlap.

**`-MalformedOverride` covers EVERY readable malformed class, not only unparseable bytes.** MALFORMED includes parseable objects with a missing, unknown, wrongly typed or invalid field, and those states are reachable; r3 scoped the override to "unparseable" and left them with no recovery. Tests cover each malformed class with a matching and a mismatching hash.

**`-ForceRelease` carries `-ConfirmHost` and may free an exactly-confirmed FOREIGN-HOST record.** That and `-MalformedOverride` are the only mutations permitted on records ordinary modes refuse, which is why exit 4 is scoped as it is in the table above. Ordinary acquire and release still refuse a foreign-host record outright.

**Liveness has THREE outcomes, and they are not the same for deciding and for reporting.** LIVE: a process with that pid exists and its start ticks match. DEAD: no process with that pid, or one whose start ticks differ. **UNMEASURABLE: the pid lookup succeeded but the start time could not be read**, which `Get-Process` does on another user's process. The catch wraps the start-time read specifically.

**Every MUTATING mode treats UNMEASURABLE as ALIVE and refuses to reclaim**, because an unevaluable measurement is never a clean one. **`-Status` reports it as `UNKNOWN`, never as `LIVE`**, because reporting LIVE would claim a measurement that was not made. r12 declared `UNKNOWN` in the status output while assigning only LIVE and DEAD, which left the third value with no rule at all.

**A FOREIGN-HOST record's status liveness is `UNKNOWN`, always, and the local process table is NOT consulted at all.** Its liveness cannot be checked from here, so the recorded pid may coincidentally match an unrelated local process, and reading that would report another machine's holder as LIVE or DEAD on the strength of a collision. Its own oracle: a foreign-host record whose recorded pid IS a live local process must still report `UNKNOWN`.

A **test seam** forces that branch: with `PARALLAX_LANE_LOCK_STARTTIME_FAULT` set, the start-time read throws AFTER the pid lookup succeeds. It is safe by construction — its only possible production effect is to classify a holder ALIVE and refuse a takeover, never to reclaim. Precedent `tools/new-kimi-lane-home.ps1:416-423`, tested at `evals/multi-model-verify/test_kimi_lane_home.py:102-106`. A SYSTEM-owned process is an OPTIONAL live confirmation only.

**MALFORMED** means any of: not JSON; not an object; `version` absent or not `1`; `state` not one of the two literals; a record missing any field required for its state; **a record carrying ANY PROPERTY FORBIDDEN FOR ITS STATE, which includes any unknown property in either state AND any held-only KNOWN property on a free record**; any field failing its type or pattern rule; a zero-length file. The forbidden-for-its-state wording is required: an unknown-field rule alone contradicts the per-state property rule above, because `host` on a free record is a known property, and two definitions of the same condition is two behaviours for an implementer to choose between. **Time fields that are date-shaped rather than digits are MALFORMED**, so the representation cannot regress to the shape measurement 20 shows diverging.

**`-Status`** is READ-ONLY, takes the handle only long enough to read, **creates nothing**, and exits 0 for every READABLE file state including MALFORMED; unreadable is exit 6.

```
{"state":"free"}
{"state":"held","host":...,"ownerPid":...,"ownerStartTicksUtc":"...","debateId":"...","nonce":"...","debateHome":"...","liveness":"LIVE"|"DEAD"|"UNKNOWN"}
{"state":"MALFORMED","bytes":<n>,"sha256":"<hex>"}
```

**The held object carries every field `-ForceRelease` requires, the nonce and host included.** That closes the lost-nonce deadlock: the nonce distinguishes two debates from one session, it is not a secret, and these overrides are not authentication. `liveness: LIVE` means the process is running and NOTHING MORE.

**`-ResolveOwner`** prints `{"ownerPid":<n>,"ownerStartTicksUtc":"<digits>"}` for the parent of the invoking shell, and its help states this is correct only for a DIRECT invocation (measurement 21). Failure to resolve is exit 2.

- [ ] **Step 1: Write the failing tests.** One per row of both tables, per exit code, per rule. Plus: a pre-existing zero-length file is MALFORMED and recoverable by `-MalformedOverride`; **each readable malformed class is recoverable by matching hash and refused by mismatching hash**; an extra field on a FREE record is MALFORMED; every mode's missing-file behaviour including the creates-nothing assertion; the file still exists after every mutating mode; a date-string time value is MALFORMED; a 4-second wait against a LIVE holder exits 3 and does NOT reclaim; status-provided identity force-releases, including a foreign-host record; an old nonce fails after a reclaim; status leaves the file byte-identical; **a binding-refused invocation exits nonzero and leaves the lock byte-identical**; and **exit-code exhaustiveness** across the bound-invocation matrix, asserting every observed code is in `{0,2,3,4,5,6}`. Module guard `os.name != "nt"`; both hosts.
- [ ] **Step 2: Write the script.**
- [ ] **Step 3: Verify, per host:**
```
$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals/multi-model-verify/test_kimi_lane_lock.py -q
$env:PARALLAX_PS_HOST = "pwsh.exe";       python -m pytest evals/multi-model-verify/test_kimi_lane_lock.py -q
```

---

### Task 4: Live gate for the lock protocol on both hosts

Task 3's tests are the implementation oracle. This gate proves the OS behaviour underneath. **It is not a regression gate for the implemented record format.**

**Files:** create `evals/multi-model-verify/test_lock_protocol_live.py`.

- [ ] **Step 1: Write the gate,** exercising the sequence production uses:

1. `CreateNew` succeeds fresh and raises `IOException` on an existing path; `Open` then succeeds.
2. A second exclusive open while held raises `IOException`.
3. Truncate-and-rewrite in place under the held handle succeeds; final bytes are exactly the new record.
4. **The crash oracle, synchronized so the crash point is proven.** The file starts with a VALID held record. A child opens it exclusively, calls `SetLength(0)`, flushes, writes a ready marker to a signal file, then blocks forever without writing a record. The parent waits for the marker, kills the child, asserts the file is EXACTLY zero bytes, and asserts `-Acquire` against it exits 4 rather than reclaiming. A second fixture repeats it with the child writing a fixed partial prefix before blocking, asserting those exact bytes survive and `-Acquire` still exits 4.
5. The tick/date-string divergence of measurement 20, asserting the DIVERGENCE.

Module guard `os.name != "nt"`; on Windows both hosts are REQUIRED and an unavailable host FAILS.

- [ ] **Step 2: Verify, per host:**
```
$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals/multi-model-verify/test_lock_protocol_live.py -q
$env:PARALLAX_PS_HOST = "pwsh.exe";       python -m pytest evals/multi-model-verify/test_lock_protocol_live.py -q
```
Then change the measurement-20 assertion to expect agreement between hosts and confirm it FAILS; revert.

---

### Task 5: The lane login wrapper

**Files:** create `tools/new-kimi-lane-login.ps1` and `evals/multi-model-verify/test_kimi_lane_login.py`.

```
-LaneHome <p>            default: $env:USERPROFILE\.parallax-kimi-review
-OwnerPid <s>            MANDATORY
-OwnerStartTicksUtc <s>  MANDATORY
-KimiBinary <p>          default: $env:USERPROFILE\.kimi-code\bin\kimi.exe
-VerdictOut <p>          MANDATORY
-Force                   switch
```

**Stream mechanism, frozen.** The child's stdout and stderr are INHERITED and untouched, so an interactive login renders normally. **The machine-readable verdict goes to `-VerdictOut`, never to stdout.** An inherited child writes to the wrapper's own stdout handle, so "inherited" and "stdout carries only JSON" cannot both hold; a dedicated file resolves it without touching the child's streams. The wrapper's own messages go to stderr.

**The bootstrap exception, stated explicitly.** The lock lives INSIDE the lane home, so it cannot guard the creation of that home. **The only pre-lock operations are: creating the lane-home directory if absent, and applying the ACL idempotently for the current identity.** Both are safe to race because both are idempotent and identity-scoped. Everything that reads or writes the CREDENTIAL happens under the lock.

**Order of operations, frozen.**

1. Validate parameters. 2. Create the lane home if absent; apply the ACL idempotently: inheritance disabled, every inherited rule removed, one full-control rule for the current identity. Measurement 9 shows the throwaway home's ACL does not propagate through the junction, so this target needs its own. 3. Generate a login debate id, 32 lowercase hex. 4. ACQUIRE, with **`-DebateHome` set to the resolved LANE-HOME path**, and set `$lockAcquired` only on success. 5. Read the existing credential verdict **with `tools/read-kimi-credential-state.ps1`**, the same validator Task 6 names explicitly. 6. If `ok` and no `-Force`, skip the client; otherwise invoke it. 7. Re-read the verdict with the same validator. 8. Write it to `-VerdictOut`. 9. In a `finally`, RELEASE using the captured nonce, but **only when `$lockAcquired`**.

**Success requires structural validity.** The post-run verdict decides the exit code, never the client's.

**Exit codes, scoped to SUCCESSFULLY BOUND invocations exactly as Task 3 is.** `0` success. `2` parameter refusal. `3` lock contention: the exclusive handle OR a holder that is LIVE or UNMEASURABLE, since a preserved lock code 3 covers all three. The wording matches Task 3's code 3 exactly; two definitions of the same propagated code is the defect this replaced. One test per exit code stays sufficient here, because the wrapper receives the identical lock-tool code 3 whichever holder produced it. `4` the lock is malformed or foreign-host. **`5` a release refusal propagated from the lock tool** — reachable, because the record can be freed or displaced between acquire and the `finally`. `6` an invalid post-run credential, a `-VerdictOut` write failure, or any unclassified runtime failure. `1` is reserved for PowerShell's binder and never emitted by script code, with the same mutation test: a binding-refused invocation exits nonzero and mutates nothing.

**Release-failure precedence, frozen.** If the MAIN operation already failed, preserve that original code and write the release failure to stderr only. If the main operation SUCCEEDED but the release failed, return the release code. Both directions are tested.

**The post-run verdict decides the exit code, in BOTH directions.** A client exit of 0 followed by an `absent`, `unreadable` or `malformed` credential FAILS with 6. **A client exit that is NONZERO followed by a structurally `ok` credential SUCCEEDS with 0.** Without that second test an implementation that simply propagates the client's exit code passes every other listed case.

- [ ] **Step 1: Write the failing tests.** Lock acquired before any credential read and released in a `finally` only when acquired; refuses when held by a live DIFFERENT owner with exit 3 and the stub recording NO invocation; the ACL asserted with `Get-Acl`, and asserted idempotent on a second run; **environment restoration asserted INSIDE the same shell** by a wrapper script that invokes the tool then prints `KIMI_CODE_HOME`, covering previously-set and previously-unset; never references `~/.kimi-code/credentials` and leaves a planted fake user credential byte-identical; existing-`ok` without `-Force` exits 0 with the stub not invoked; client exit 0 leaving `absent`, `unreadable` or `malformed` each fail with 6; `-VerdictOut` contains exactly one parseable JSON line; one test per exit code.

  **The stream-inheritance oracle must be TEMPORAL.** A wrapper that captured both streams and replayed them after the child exited would pass a mere both-streams-emitted check. So: the stub writes a distinct readiness marker to stdout AND a different one to stderr, then BLOCKS. The parent must OBSERVE BOTH MARKERS BEFORE the stub is allowed to finish, and neither marker may appear in `-VerdictOut`.
- [ ] **Step 2: Write the script.**
- [ ] **Step 3: Verify, per host:**
```
$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals/multi-model-verify/test_kimi_lane_login.py -q
$env:PARALLAX_PS_HOST = "pwsh.exe";       python -m pytest evals/multi-model-verify/test_kimi_lane_login.py -q
```

---

### Task 6: The builder stops copying

**Files:** modify `tools/new-kimi-lane-home.ps1` (credential source `:231-236`, the copy `:410-414`, new parameters, lock handling, and the fault seam's position) and `evals/multi-model-verify/test_kimi_lane_home.py` (tests only; its selector and module guard belong to Task 2).

**Added parameters, all MANDATORY `[string]` in BOTH modes:** `-LaneHome`, `-DebateId`, `-OwnerPid`, `-OwnerStartTicksUtc`. `-Nonce` is additionally MANDATORY on Remove. This matches the exact lifecycle invocation written into the contract in Task 9.

**Nonce custody, frozen.** Build's success output becomes exactly one line of JSON with exactly these two keys and no others:

```
{"debateHome":"<resolved path>","nonce":"<32 hex>"}
```

All output from the lock tool that build invokes internally is CAPTURED, so it cannot contaminate that line. **Remove's stdout stays exactly `removed <path>`**, the one line it prints today at `:131-133`, with internal lock output captured.

**Build order, frozen.** Lock FIRST, because a login can otherwise mutate the shared credential between validation and acquisition.

1. Validate parameters. 2. ACQUIRE, with **`-DebateHome` set to the resolved `-Path`**; set `$lockAcquired` on success. 3. Validate the lane credential via `tools/read-kimi-credential-state.ps1`. 4. Every existing gate, unchanged. 5. Create, junction, render. 6. Construct AND EMIT the custody JSON line. 7. **Only now set `$buildCompleted`.**

**`$buildCompleted` is set only after the success line is emitted, and JSON construction and emission stay INSIDE the guarded `try`.** Setting it after rendering, as r4 did, means a failure to construct or write that line leaves the flag true, the `finally` skips the release, and the lock is retained by a caller who never received the nonce it needs to release it. That is an unreleasable lane. Any failure before the line is out runs failed-build cleanup and releases.

**MOVE the existing `PARALLAX_LANE_HOME_FAULT` seam** from its current post-credential position at `tools/new-kimi-lane-home.ps1:416-423` to fire immediately AFTER custody JSON construction and immediately BEFORE emission. That placement is the whole oracle for the boundary above: a pre-render fault cannot distinguish an implementation that sets `$buildCompleted` after rendering from one that sets it after emission. Its test requires NO stdout, the home cleaned up, and the persistent lock record exactly `free`.

**Cleanup needs TWO flags.** The `finally` releases only when `$lockAcquired -and -not $buildCompleted`. One flag is not enough: `-not $buildCompleted` is also true when acquire itself failed, and releasing then would release a lock this call never took. If the failure cleanup cannot itself release, the ORIGINAL failure is what the script reports and the release failure goes to stderr only; a cleanup error never masks the error that caused the cleanup.

**Remove order, frozen.** Identity check BEFORE deletion.

1. Verify the caller's complete identity by an idempotent `-Acquire -Nonce`, with **`-DebateHome` set to the same resolved `-Path`** build used, which is what makes a wrong `-Path` exit 2 at the lock. A mismatch exits nonzero and leaves BOTH the home and the lock byte-identical. 2. The existing sentinel and dangerous-root guards. **If any refuses, no deletion occurs and the pre-existing held lock REMAINS HELD** — the caller still owns the debate. 3. Delete the home. 4. Release.

**Remove's own failure precedence, frozen.** A release that fails AFTER the deletion succeeded is reported as the failure and exits with the lock tool's code; the `removed <path>` line is printed only when BOTH the deletion and the release succeeded, so that line never reports a removal whose lock is still held. Build mode's precedence rule does not cover this path and r12 left it to inference.

**The junction oracle.** Three assertions, all required, each failing hard if its own measurement cannot be taken:

- **File identity is primary.** Open both credential paths and compare the full NTFS file identity, not a textual resolved path.
- **Write-through is required.** Mutate the obviously-fake lane fixture and observe the new bytes through the debate path in the same test.
- **A non-following physical inventory.** Enumerate the debate home WITHOUT traversing reparse points and assert no standalone credential file exists beneath it. The first two both pass on a correct junction that ALSO has a stray copy.

- [ ] **Step 1: Write the failing tests.** The three junction assertions; stdout is exactly one JSON line with exactly `debateHome` and `nonce`, and removal uses the RETURNED nonce rather than reading the lock file; the credential source is the LANE home and a planted differing user credential is never read; absent, unreadable and malformed lane credentials each refuse with a message naming `tools/new-kimi-lane-login.ps1`; acquire precedes validation and releases on every later refusal; **a successful build RETAINS the lock**; **a failure to emit the custody line runs cleanup and RELEASES**, proven by firing the relocated `PARALLAX_LANE_HOME_FAULT` seam at its new position between construction and emission, and asserting no stdout, the home gone, and the lock exactly `free`; **an acquire failure does NOT attempt a release**, proven with a REAL held-by-a-different-owner fixture rather than an invented seam, which is the stronger oracle; **a successful remove leaves the home ABSENT and the lock record exactly `free`** — without this, deletion-without-release passes; a cleanup-release fault seam named exactly `PARALLAX_LANE_HOME_CLEANUP_RELEASE_FAULT`, firing only after an original build failure and immediately before the cleanup release, proves the original failure stays primary while the release failure appears only on stderr; remove's identity mismatch leaves home and lock byte-identical; **the WRONG-`-Path` case has its own integration oracle, because Task 3 now excludes `debateHome` from identity and "identity mismatch" no longer covers it**: build home A, prepare a distinct valid disposable home B, then call `-Remove` on B carrying A's five identity fields and A's nonce, and require exit 2, NO deletion, and both homes and the lock byte-identical; **the post-deletion release failure has a failure-capable oracle**, through a seam named exactly `PARALLAX_LANE_HOME_REMOVE_RELEASE_FAULT` — the other two seams are given exact shared names because production and tests must agree on the string, and leaving this one unnamed left that agreement to invention — honored ONLY in Remove mode, firing immediately after a successful deletion and immediately before the release; when nonempty it SKIPS the lock mutation entirely and produces a simulated release result of code 5, writing exactly `PARALLAX_LANE_HOME_REMOVE_RELEASE_FAULT injected: simulated post-delete release refusal` to stderr and nothing to stdout; the test requires the home ABSENT, the original held record UNCHANGED, exit 5, that sentinel on stderr, and NO `removed <path>` on stdout, with a direct release performed as teardown — Task 7's matrix exercises the pre-deletion sentinel refusal and never reaches this branch; a sentinel or dangerous-root refusal after the identity check leaves home and lock unchanged; `-Remove` does not delete through the junction; the failed-build cleanup at `:482-489` does not either; every existing test still passes.
- [ ] **Step 2:** The host-selector refactor and the module guard were moved into Task 2 step 3b, because Task 2's own fixture change had no oracle without them. Confirm they are in place; do not repeat them.
- [ ] **Step 3: Modify the builder,** keeping every existing gate.
- [ ] **Step 4: Verify, per host:**
```
$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals/multi-model-verify/test_kimi_lane_home.py -q
$env:PARALLAX_PS_HOST = "pwsh.exe";       python -m pytest evals/multi-model-verify/test_kimi_lane_home.py -q
```

---

### Task 7: Live gates for the junction and credential facts

**Files:** create `evals/tools/lane_credential_live_support.py` (the shared production helper), `evals/multi-model-verify/test_lane_credential_live.py`, and `evals/multi-model-verify/test_lane_credential_live_support.py`.

**The helper lives in its own non-test module**, `evals/tools/lane_credential_live_support.py`, and BOTH test modules import it. It performs NO live-environment check at import time, so the offline support suite does not drag live setup in. Leaving it inside the opt-in live module, as r7 implied, would have done exactly that; leaving it unnamed would have made the import boundary the implementer's invention.

**Three homes, three roles.** `PARALLAX_LANE_LIVE_HOME_A` and `_B` are the coexistence pair; `_C` is the EXPENDABLE mutation fixture and **the only home the suite DELIBERATELY expires and requires to rotate**. That is narrower than r5's "the only home any test rotates", which was wrong: A and B perform authenticated dispatches, access tokens expire in 900 seconds (measurement 1), and a dispatch can therefore refresh them on its own. A and B may refresh NATURALLY, but only while locked. The suite never creates a login and never touches `~/.kimi-code`. Any variable unset, or any home lacking a structurally `ok` credential, FAILS the suite with a message naming `tools/new-kimi-lane-login.ps1`.

**The marker contract, frozen.** The documented manual setup runs the login wrapper for A, writes A's marker, then for B, writes B's. The marker is a file named exactly `.parallax-login-created-ticks-utc` in the home's root, ASCII, containing exactly one line: the UTC tick count as decimal digits, matching `\A[0-9]+\z`. The gate requires A's value to be strictly less than B's; a missing, empty or non-matching marker FAILS the suite.

**The manual setup sequence, frozen and executable.** It is performed once, by hand, before the suite runs. It cannot borrow the module's owner, because `-ResolveOwner` runs once per MODULE RUN and setup happens earlier. For A, then for B:

1. Run `tools/kimi-lane-lock.ps1 -ResolveOwner` in THAT setup shell, directly, and keep its two values for the rest of this setup.
2. Run `tools/new-kimi-lane-login.ps1 -LaneHome <home> -OwnerPid <pid> -OwnerStartTicksUtc <ticks> -VerdictOut <path>` and require the verdict `ok`.
3. Generate a fresh setup debate id, 32 lowercase hex.
4. Acquire that home's lock with the home as BOTH `-LaneHome` and `-DebateHome`; capture the nonce.
5. Write the ASCII marker.
6. Release with the complete identity.

A's tick must be strictly below B's, which the ordering of these two runs is what produces.

**C is created third, by steps 1 through 4 and 6, EXPLICITLY OMITTING step 5.** Step 5 is the marker write, so "the same six steps while writing no marker" was an instruction that contradicted itself. Only A and B are ordered against each other, so only they need a marker; C is the mutation fixture and nothing compares its creation time. r12 wrote the sequence as "for A, then for B" while also requiring C to carry a structurally `ok` credential, leaving C's creation to inference.

**Three coexisting lane logins plus the user's own is a GENERALIZATION of measurement 11, which established two.** The fail direction is safe and loud: if a third login cannot coexist, setup produces a home without an `ok` credential and the suite REFUSES rather than running degraded. Recorded here so the assumption is visible rather than buried in a fixture.

**The fixture routing table.** Every live item names its homes; r6 assigned only items 3 and 7.

| Item | Lane home | Debate home | Custody |
|---|---|---|---|
| 1 absolute-key, and its control | C | fresh builder-created | build holds C; `-Remove` releases |
| 2 junction read-through | C | fresh builder-created | build holds C; `-Remove` releases |
| 3 refresh write-through | C | fresh builder-created | build holds C; `-Remove` releases |
| 4a delete path, SUCCESSFUL build | C | fresh builder-created | build holds C; the real `-Remove` releases |
| 4b delete path, FAILED build | C | fresh builder-created | the builder's own internal cleanup releases; no nonce is returned and `-Remove` is never called |
| 5 coexistence | A and B | fresh builder-created per dispatch | build holds the dispatching home; `-Remove` releases |
| 6 `provider list` false positives | isolated disposable homes carrying a structurally valid FAKE credential, a garbage one, and no credential file | not applicable | NONE: no real credential exists to protect |
| 7 `provider list` is not a refresh path | C | fresh builder-created | build holds C; `-Remove` releases |

**The coexistence claim, narrowed to what a pre-provisioned fixture supports.** A pytest suite handed existing homes cannot observe the creation event. The gate asserts A's marker precedes B's, then dispatches A, then B, then A again, all requiring exit 0. **Its claim is "A remains usable after B was created", not "the creation of B was observed to be harmless"**, and the test docstring says exactly that.

**Locking is PER HOME, and THE BUILDER IS THE ACQUISITION.** Call `tools/kimi-lane-lock.ps1 -ResolveOwner` ONCE per module run and use one per-home debate id.

For every case that uses a builder-created debate home, **do NOT acquire separately and do NOT plainly release.** A successful build already holds that lane's lock and returns its nonce, and Task 6 deliberately stops a successful build from releasing it. A second acquire would CONTEND against that retained hold, and a plain release would then make Task 6's identity-confirming `-Remove` fail. So:

1. Pass the module owner and that home's debate id to `tools/new-kimi-lane-home.ps1`; the build acquires.
2. **Set `custodyReceived` ONLY after Build exits 0 AND its exact JSON line parses.** Retain the nonce.
3. **The PRE-COMMAND phase**, which exists only for `custodyReceived`: every deliberate credential mutation happens HERE, under builder custody, together with the pre-command hashes. Items 3 and 7 force expiry, and without this phase an implementation could force it BEFORE the build, mutating a shared credential unlocked, and still pass every functional assertion.
4. Run the command under that EXISTING hold.
5. Merge new credential values and run the stream guard while the hold is still in force.
6. In a `finally`, call the real `-Remove` with that nonce, which releases.

**Steps 3 through 6 run ONLY when `custodyReceived`.** A refused or failed Build returns no nonce and Task 6 already owns its own cleanup and release, so on that path invoke NEITHER the command NOR `-Remove`, and preserve the Build failure as the reported error. r7's blanket "`finally` always calls `-Remove`" would have called it with no nonce, against a lock the builder had already freed.

**The MAIN OPERATION is all four phases inside custody**, not just the command: the pre-command phase, the command and its capture, the post-command re-read and merge, and the stream guard. Naming only the command left three phases where a runner could skip `-Remove` or let a removal failure mask the real one.

**Cleanup coverage, frozen:** a failure in any main phase still ATTEMPTS the real `-Remove`. When Remove succeeds, the debate home is ABSENT and the lock is exactly `free`; when Remove fails, the required report and filesystem state are those in the support matrix below.

**Cleanup precedence, frozen:** a failure from ANY main phase stays PRIMARY even when `-Remove` also fails; a `-Remove` failure is primary only when every main phase succeeded.

**The same precedence governs seeding:** a seed-read failure stays primary if the release also fails, and a release failure is primary only after a successful seed read.

**A and B's setup markers are written under their own locks** by the manual setup below, which is a separate lifecycle because it precedes any build.

Freezing only C's custody, as r5 did, left every A and B dispatch able to refresh a shared credential outside the lock this suite exists to respect.

**Live command oracles are MEASURED ONCE, then pinned, with the normalization fully frozen and no fallback.** The dispatch prompt is `Reply with the single word PROBE.` and the reply must contain `PROBE`. For the absolute-key failure the implementer runs that case once and records, in `docs/superpowers/plans/rounds/2026-08-01-cred-lock/probe-record.md`: the exit code, which must be NONZERO, and stdout and stderr SEPARATELY.

The normalization is exactly: replace the resolved fixture root with the literal `<fixture-root>`, case-insensitively; normalize CRLF to LF; trim ONE terminal newline. **The pin is the COMPLETE normalized stderr.** Run the case TWICE. If the two normalized outputs differ, STOP and amend this plan; the implementer does not get to select a line instead. r4 offered "or if that is not stable, the single line matching a stated selector", which handed back the choice this rule exists to remove.

**SECRET GUARD — one helper, applied to EVERY live command, not only the probe record.** Restricting it to `probe-record.md` was too narrow twice over: other live commands capture client streams as well, and an ordinary pytest failure message can print a captured stream BEFORE any write-time guard runs.

So: one helper inspects both captured streams against a RETAINED UNION of **every NONEMPTY credential string value** across every fixture home, and it runs BEFORE any assertion or failure message that could surface those streams. On a match it fails naming ONLY the field. The nonempty restriction is load-bearing: `scope` and `token_type` are optional and unconstrained, an empty string is a substring of every output, and a guard comparing against one would fire on everything. The `probe-record.md` write uses this same helper, and that record is COMMITTED to a PUBLIC repo.

**The secret set's lifecycle, frozen, because a set built once is already stale.** C deliberately rotates, so a value ISSUED BY the command being scanned does not exist when that command starts:

- **Seed the union BEFORE any live command, through the one DIRECT-ACQUIRE exception to builder custody.** No build has run yet at that point, so there is no hold to borrow. For A, then B, then C: acquire with the module owner and that home as BOTH `-LaneHome` and `-DebateHome`, read and merge, then release with the captured nonce in a `finally`. **This is the ONLY place in the suite that acquires directly**; everywhere else the builder is the acquisition.
- **Item 6's disposable homes are the exception to the exception: their values are loaded and merged WITHOUT any lock**, because those homes are isolated, disposable, and contain no real shared credential. All values, locked and unlocked alike, still pass through the same stream guard.
- **After every command against A, B or C — the builder-custodied homes — and while that home's hold is STILL IN FORCE, re-read the home and MERGE any new values into the union before scanning the streams.** Item 6's disposable homes are re-read and merged after their command WITHOUT a lock, because they never had a hold to keep in force; the same stream guard then runs over their output unchanged.
- **Never discard an old value.** A rotated-away token is still a secret that must not be printed.

**The helper owns process capture**, so nothing can render a stream before the guard runs: it invokes the command without raising, and it sanitizes the timeout, launch-failure and error paths too, since those are exactly the paths a test framework prints captured output on.

**Token-rotation assertions must not disclose.** `assert $before -ne $after` on token values prints BOTH operands through pytest's assertion introspection on failure, into a log that may be pasted anywhere. Compare through an ordinary `if` and call `pytest.fail("access_token did not rotate")`, or the refresh-token equivalent. Neither value may appear in an assert expression or a failure message.

- [ ] **Step 1: Write the gate.** Each item begins with a POSITIVE CONTROL.

1. **Absolute `oauth.key`** (5): first a junction-based control with the same credential and config requiring exit 0 and `PROBE`, then the absolute-key case asserted to fail with the pinned normalized message. **The absolute-key home is built normally and its `config.toml` is then hand-edited in the throwaway copy** to replace the rendered `key = "oauth/kimi-code"` with an absolute path. The builder renders only the relative form (`tools/new-kimi-lane-home.ps1:456`) and gains no parameter for this; the edit is confined to the disposable home and never touches a real one.
2. **Junction read-through** (6): a dispatch through a junctioned credentials directory exits 0 and returns `PROBE`.
3. **Refresh write-through** (7), on C: force expiry IN THE PRE-COMMAND PHASE, dispatch, require exit 0 AND `PROBE`, then assert C's token fields rotated and no second credential file exists anywhere under the debate home.
4. **Both delete paths** (10): invoke the real `-Remove` and the real failed-build cleanup HERE, directly. This module's verification command runs only this module, so delegating the assertion elsewhere would assert nothing.
5. **Coexistence** (11), as narrowed above.
6. **`provider list` false positives** (16): garbage credential and absent credential file, each requiring exit 0 and each reporting `source=oauth`.
7. **`provider list` is not a refresh path** (17), on C: force expiry IN THE PRE-COMMAND PHASE and take the pre-command hash there, run it, require exit 0 AND the expected provider line, THEN assert byte-identity by SHA-256, length and mtime.

Opt-in on `PARALLAX_LANE_LIVE`; module guard `os.name != "nt"`.

- [ ] **Step 1b: Give the locking and the secret guard their OWN oracles, offline.** The seven items above test the CLIENT. None of them proves the runner acquired the intended home's lock, released it afterwards, or caught a credential value in a stream, so a runner with no locking and no helper at all passes every one of them. Create `evals/multi-model-verify/test_lane_credential_live_support.py`, which imports the SAME production helper the live suite uses and drives it against fake commands, with no real credential and no opt-in required:

- pre-hold A's, B's and C's locks individually under a DIFFERENT live owner and prove the BUILD refuses, the fake command is never invoked, **`-Remove` is never attempted, and the pre-held record is byte-identical afterwards**;
- pre-hold a SEED home and prove its credential is never read, and that a successful seed leaves that home's record exactly `free`;
- prove contention is observed against the BUILDER-RETAINED hold **during the PRE-COMMAND phase as well as during the client process**, since a second acquire must contend the whole time custody is held and not only while the client runs;
- prove cleanup after BOTH a zero and a nonzero command exit runs through the real `-Remove`, leaving the debate home ABSENT and the lock record exactly `free`;
- prove cleanup precedence with THIS MATRIX, which replaces the prose bullets rather than adding to them. The r10 wording demanded an impossible end state: a main-phase failure PLUS a `-Remove` failure, while also asserting the home absent and the lock free. Those cannot coexist. A deterministic sentinel or dangerous-root refusal leaves the home PRESENT and the held record unchanged (`tools/new-kimi-lane-home.ps1` remove order, frozen in Task 6), and a release that fails after deletion leaves the lock NOT free, because the release is what would have freed it.

| Main phases | `-Remove` outcome | Required state and report |
|---|---|---|
| pre-command, command/capture, merge or guard FAILS | succeeds | main failure primary; Remove attempted; home ABSENT; lock `free` |
| pre-command, command/capture, merge or guard FAILS | deterministic sentinel refusal | main failure primary; Remove attempted; home PRESENT; the original held record BYTE-IDENTICAL |
| all succeed | deterministic sentinel refusal | Remove failure primary; home PRESENT; the original held record BYTE-IDENTICAL |

  Repair the sentinel and run a normal `-Remove` as test TEARDOWN only, after the failure state has been asserted.

- prove seed precedence with the corresponding three directions, since two cases never showed a release happening after a failing read: a seed-read failure with a SUCCEEDING release reports the SEED failure and leaves the record `free`; a seed-read failure with a FAILING release reports the SEED failure, asserts the release was attempted, and pins the record state the chosen deterministic fault produces; a successful seed read with a failing release reports the RELEASE failure;
- **exercise the three exception paths the helper promises to sanitize, since none of the ordinary cases reaches them.** A fake command that emits a fake credential value and then BLOCKS UNTIL TIMEOUT must produce a field-only failure carrying neither the value nor the captured stream, write no probe record, and still clean up through `-Remove`. A NONEXISTENT EXECUTABLE must produce a sanitized launch failure and still clean up. A post-command credential read-or-parse FAULT must produce a value-free failure and still clean up;
- inject an existing fake credential value into stdout, and separately into stderr, and require the guard to fire on each;
- have a fake command ROTATE a credential and emit the NEW value, proving the merge-after-command rule, which a seed-once implementation fails;
- assert every CREDENTIAL-MATCH failure from the secret guard names ONLY the matched field, contains no value, and writes no probe record. That scoping is required: the launch-failure and read-or-parse cases have no matched field to name, so "every failure names only the field" would contradict the oracles directly above it. The timeout, launch, read-or-parse, phase and cleanup failures each keep their own individually specified sanitized message, and none of them may carry a credential value or a captured stream either.

Its lock cases are PowerShell-facing, so Task 10 adds this module to both Windows steps and to the host-parity required set.

- [ ] **Step 2: Verify, per host, because item 4 claims both:**
```
$env:PARALLAX_LANE_LIVE = "1"
$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals/multi-model-verify/test_lane_credential_live.py evals/multi-model-verify/test_lane_credential_live_support.py -q
$env:PARALLAX_PS_HOST = "pwsh.exe";       python -m pytest evals/multi-model-verify/test_lane_credential_live.py evals/multi-model-verify/test_lane_credential_live_support.py -q
```
Expected: all pass, ZERO skipped. **Both commands collect the support suite**; collecting only the live module would let a broken helper pass this task's own gate and be caught six tasks later.

---

### Task 8: The doctor stops touching credentials

**Files:** modify `commands/doctor.md:151-173` and `evals/multi-model-verify/test_backup_lane.py`.

**Aggregate verdict, a TOTAL order.** Check 8 observes several substates and emits ONE row. Binary absent short-circuits to `N/A`. Otherwise the row is the worst substate by **`BROKEN > STALE > N/A > OK`**, and every substate is still named in the detail text. `N/A` must be IN the order: `commands/doctor.md:6-9` defines it as a real row verdict that never contributes to overall failure, and without it a valid binary plus an absent credential plus a free lock has no defined row.

| Substate | Contribution |
|---|---|
| binary absent | `N/A`, short-circuit, "backup lane unavailable, primary unaffected" |
| binary present, version below floor or unreadable | `BROKEN` |
| lane credential `ok` | `OK` — "lane credential structurally present" |
| lane credential `absent` | `N/A`, **and no hash is taken at all** |
| lane credential `unreadable` or `malformed` | `BROKEN` |
| the validator itself fails to run | `BROKEN` |
| a hash cannot be taken on a PRESENT credential | `BROKEN` |
| the two hashes differ | `BROKEN` — "credential bytes changed during the check; actor not established" |
| lock `free` | `OK` |
| lock `held` and LIVE | `OK`, reported as held with the holder |
| lock `held` and DEAD | `STALE`, reclaimable at the next acquire |
| lock `held` and UNKNOWN | `N/A` — the doctor's own vocabulary for a surface that did not answer. Report that liveness could NOT be determined and that every mutating mode therefore treats the holder as alive and will not reclaim. It is not `OK`, because an unmade measurement is never a clean one, and not `STALE`, because nothing will reclaim it |
| lock foreign-host — the record's `host` differs from `$env:COMPUTERNAME`, compared case-insensitively, which is the comparison the doctor makes since `-Status` reports the field | `STALE`, with the `-ForceRelease -ConfirmHost ...` command |
| lock MALFORMED | `STALE`, with the `-MalformedOverride -ConfirmSha256 ...` command |
| **lock status cannot be measured** — unreadable lock, missing lock tool, or a status invocation failure | `BROKEN`, and **no recovery command is fabricated from evidence the check does not have** |

**The hash claim is narrowed.** Two hashes show only that bytes changed during the interval, not WHO changed them. Equal hashes are reported as "no net byte change observed", never as proof that nothing wrote the file.

**Hash procedure, as a seven-step algorithm.** The r4 prose said to confirm readability before hash 1 while also requiring the validator substate to be reported, and a hash-1 failure would then prevent the validator from ever running, leaving that substate unmeasured. This ordering has no such gap:

1. Test existence.
2. If ABSENT: run the validator, require `absent`, take NO hash.
3. If PRESENT: attempt hash 1 and record success or failure.
4. Run the validator REGARDLESS of hash 1's outcome.
5. If the file is still present, attempt hash 2. Disappearance between the two is `BROKEN`.
6. Compare ONLY if both hashes exist. **Never compare a missing value to anything.**
7. Any hash failure is `BROKEN`, and it does NOT suppress the validator detail.

**The two recovery commands, complete rather than described:**

```
tools/kimi-lane-lock.ps1 -ForceRelease -LaneHome <lane-home> -ConfirmHost <host> -ConfirmOwnerPid <pid> -ConfirmOwnerStartTicksUtc <ticks> -ConfirmDebateId <id> -ConfirmNonce <nonce>
tools/kimi-lane-lock.ps1 -MalformedOverride -LaneHome <lane-home> -ConfirmSha256 <sha256>
```

Every CONFIRMATION placeholder is a field `-Status` prints, which is why `-Status` carries the complete identity. `<lane-home>` is not: it is the configured lane home against which status was requested.

**The authenticated-probe literal, exact:**

> An AUTHENTICATED probe is a SEPARATE operation and is never part of check 8. It acquires the lane lock, it MAY REFRESH the dedicated lane credential, and it never touches the user's ordinary credential. Check 8 reports STRUCTURE only, so a structurally present credential is not a working one.

- [ ] **Step 1: Write the failing tests.** Pin the new text and the ABSENCE of the old: no home construction in check 8; no `provider list`; the string `credential present and OAuth-sourced` is gone, because measurement 16 shows the check could not support it. Pin the total-order precedence rule, the exact hash order, the narrowed hash wording, the lock-status reporting including the measurement-failure row, the statement that `LIVE` means the process is running and never that a debate was abandoned, **the authenticated-probe literal above**, both override commands, and the unchanged containment-artifact check at `:169-173`.

  **Two of those need EXPLICIT pins rather than the generic "lock-status reporting", because a wrong mapping would satisfy the generic one.** Pin the `UNKNOWN` row's `N/A` verdict TOGETHER WITH its required detail — that liveness could not be determined and that no mutating mode will reclaim — so an implementation mapping `UNKNOWN` to `OK` or `STALE` fails. And pin the foreign-host branch's CASE-INSENSITIVE comparison of the record's `host` against `$env:COMPUTERNAME`, together with its complete `-ForceRelease -ConfirmHost ...` recovery command, so a case-sensitive comparison fails.
- [ ] **Step 2: Rewrite check 8.**
- [ ] **Step 3: Verify.** `python -m pytest evals/multi-model-verify/test_backup_lane.py -q` and `python evals/tools/skill_lint.py skills/multi-model-verify --strict`

---

### Task 9: The contract

**Tests change first.** Three regions: one revised, two new. Forward slashes only.

**Files:** modify `evals/multi-model-verify/test_backup_lane.py:162-194`, `evals/multi-model-verify/test_contract_coverage.py` (`DECLARED_REGIONS`), and `skills/multi-model-verify/references/backup-lane.md:47-67`.

**Region `lane-home-isolation`, exact replacement text:**

> Build the DEBATE home ONCE, before round 1, with `tools/new-kimi-lane-home.ps1`, and set `KIMI_CODE_HOME=<debate-home>` on EVERY call of that debate, fresh and resumed alike. Two directories matter here and the shipped text must not blur them: the DEBATE home is this debate's throwaway `KIMI_CODE_HOME`, and the LANE home is the persistent directory holding the lane's own login and the lock. Two INDEPENDENT reasons, either one sufficient: the real user-global `~/.kimi-code/config.toml` can carry lifecycle hooks that run a shell command on the reviewer's own approval path, and the home is where this lane's effort pin and this debate's session evidence live. One debate is ONE home: that debate's ROUNDS are one session, and the only other session the home may hold is the write-probe's own disposable one, created before round 1 and therefore already in the inventory the freshness rule captures. A home is never reused across DEBATES, because a reused home carries another debate's sessions into this one's evidence. The home holds NO COPY of any credential. Its `credentials` directory is a JUNCTION to a DEDICATED LANE LOGIN, distinct from the user's ordinary login, so a refresh writes THROUGH to one file and no copy can go stale; the lane never falls back to the ordinary credential. A home that cannot be built, or a lane credential that is absent, unreadable or structurally invalid, makes the lane UNAVAILABLE, never a reason to dispatch from the real home. Remove the home with `-Remove` when the debate ends. The lock protocol every one of those calls follows is the call-lifecycle region below.

**Region `lane-lock`, exact text:**

> The lane home is shared between debates and sessions, so one PERSISTENT lock file beside the credential guards it. That file is NEVER unlinked: acquire, reclaim and release are all state transitions written IN PLACE, each under one exclusive handle that serializes every writer. Staleness is LIVENESS and never a clock. A holder is stale only when no process carries its recorded id, or a process carries it with a different start time, which is the identity-reuse guard. A predecessor of this lock decided staleness by AGE, so a live round past the threshold became breakable by anyone; nothing here has a time-based expiry, and a wait budget bounds only caller patience and never widens what counts as stale. What cannot be evaluated is HELD: a record naming another machine, an unreadable one, a truncated one, a zero-length one, one carrying a field this reader does not know, and one whose stored times are not plain digit strings are each held and reported rather than reclaimed, because an unmade measurement is never a clean one. Contention WAITS up to the caller-supplied budget and then refuses; a zero budget refuses at once, and no budget ever breaks a holder. Two human overrides exist because one cannot cover both states: a well-formed HELD record is freed by confirming its complete recorded identity, machine name included, and a record too damaged to trust its identity is freed by confirming the exact hash of its current bytes. Both are guarded human overrides, not authentication, and both leave the file in place.

**Region `lane-lock-call-lifecycle`, exact text:**

> Ownership is RESOLVED ONCE per debate and PASSED EXPLICITLY thereafter. The owner is the harness session process, not the shell, which exits between calls and would make every lock instantly stale; deriving it from the invoking shell's parent is correct only for a DIRECT invocation, and under any wrapper it names an intermediate process that also exits. So run `tools/kimi-lane-lock.ps1 -ResolveOwner` once at the start of the debate, keep its `ownerPid` and `ownerStartTicksUtc`, generate one 32-character lowercase hexadecimal debate id, and hand all three to every later call. Build with `tools/new-kimi-lane-home.ps1 -Path <debate-home> -Model <canonical-backup-model-id> -Effort <canonical-backup-effort> -LaneHome <lane-home> -DebateId <id> -OwnerPid <pid> -OwnerStartTicksUtc <ticks>`; it acquires the lock before it validates the credential, because a login could otherwise write that credential in between, and it releases only when the build itself failed. Build prints one JSON line carrying `debateHome` and `nonce`: keep that nonce, because removal requires it and a hold nobody can release is a lane nobody else can use. Remove with `tools/new-kimi-lane-home.ps1 -Path <debate-home> -Remove -LaneHome <lane-home> -DebateId <id> -OwnerPid <pid> -OwnerStartTicksUtc <ticks> -Nonce <nonce>`; it confirms the complete identity BEFORE it deletes anything, so a caller who cannot release also cannot destroy, and it releases only after the home is gone. Log the lane in with `tools/new-kimi-lane-login.ps1 -LaneHome <lane-home> -OwnerPid <pid> -OwnerStartTicksUtc <ticks> -VerdictOut <path>`, passing the SAME lane home the build was given, because omitting it authenticates the default home while the debate dispatches from another; the wrapper generates its own debate id, takes the same lock with the lane home as its debate home, and releases it on the way out. A login outside that lock would be the one writer this protocol never sees. Creating the lane directory and applying its access rules are the ONLY steps that run before the lock, because the lock lives inside that directory and both steps are safe to repeat. A debate that ends without removal leaves its home on disk and its record still HELD; that record is not freed by the session exiting, it merely becomes DEAD by liveness and is reclaimable at some later acquire. Read the state at any time with `tools/kimi-lane-lock.ps1 -Status -LaneHome <lane-home>`, which reports the holder and its liveness and reports LIVE to mean the process is running, never to mean the debate is still going.

- [ ] **Step 1: Rewrite the `lane-home-isolation` pin FIRST** to the exact text above.
- [ ] **Step 2: Add `lane-lock` and `lane-lock-call-lifecycle` pins** to the exact texts above.
- [ ] **Step 3: Add both identifiers to `DECLARED_REGIONS`.**
- [ ] **Step 4: Edit `backup-lane.md`.**
- [ ] **Step 5: Verify equality over NORMALIZED RUNTIME VALUES, not raw bytes.** Raw source bytes can never match: the Markdown is line-wrapped and the pin is Python adjacent string literals. `evals/multi-model-verify/test_contract_coverage.py:21-30` shows `parse_regions` collapsing whitespace, `:517-520` shows `collect_pins` doing the same, and `:523-526` shows coverage is a SUBSTRING test. So: call `parse_regions` on the edited Markdown and `collect_pins` on the edited test file, then for each region assert its normalized string is a substring of some normalized pin, printing both lengths. **A raw-byte length or hash comparison is the wrong equality and must not be used.**

```
python -m pytest evals/multi-model-verify/test_contract_coverage.py evals/multi-model-verify/test_backup_lane.py -q
```
Then delete one sentence from a new region and confirm the checker reports it UNLOCKED; revert.

---

### Task 10: CI wiring, version, and full gate

**Files:** modify `.github/workflows/skill-evals.yml:79-99` and `.claude-plugin/plugin.json`.

- [ ] **Step 1: Add every new offline dual-host module to BOTH Windows steps** — `test_kimi_lane_lock.py`, `test_lock_protocol_live.py`, `test_kimi_credential_state.py`, `test_kimi_lane_login.py`, the now-dual-host `test_kimi_lane_home.py`, and **`test_lane_credential_live_support.py` from Task 7 step 1b** — and add all SIX to the required-module set in `evals/tools/check_workflow_paths.py`. `test_lane_credential_live.py` is NOT added: it is opt-in and needs real logins, and CI must not acquire credentials merely to avoid a skip.
- [ ] **Step 2:** `python evals/tools/check_workflow_paths.py` — empty, exit 0, with host parity satisfied.
- [ ] **Step 3:** Bump `.claude-plugin/plugin.json` to `0.19.0`.
- [ ] **Step 4:** All four gates. Four exit-zero runs and a green pytest line.
- [ ] **Step 5: Re-run the opt-in live suite at FINAL HEAD, per host,** because Task 7 ran it mid-plan and later tasks changed the builder:
```
$env:PARALLAX_LANE_LIVE = "1"
$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals/multi-model-verify/test_lane_credential_live.py -q
$env:PARALLAX_PS_HOST = "pwsh.exe";       python -m pytest evals/multi-model-verify/test_lane_credential_live.py -q
```
Expected: ZERO skipped.
- [ ] **Step 6:** Skill text changed, so run `python evals/tools/run_behavioral_evals.py --head`.
- [ ] **Step 7: The history check, as a FAILING oracle.** `Select-String` prints matches without failing, so it is not an oracle on its own:
```powershell
$hits = git log --format=%B 6201e30..HEAD | Select-String -Pattern "Claude-Session"
if ($hits) { $hits; throw "AI-attribution trailer found; the repo forbids it" }
"clean"
```
Expected: `clean`. Mutation-test it against a controlled input string containing `Claude-Session` and confirm it throws. The three known carriers are `c79da41`, `9d50196` and `e3f98c2`.

---

## Debate record

**Participants:** Opus 5 (session) / gpt-5.6-sol (codex exec, session `019fbb82-9e35-7b72-a64e-59fb60b981cd`)
**Rounds used:** 18, cap lifted by the user
**Outcome:** converged, reviewer PASS on all ten tasks AND on the implementer packet at round 18
**Verification status:** FULL
**Degradation:** none
**Authorized by:** n/a
**Raw rounds:** `docs/superpowers/plans/rounds/2026-08-01-cred-lock/`

The user lifted the round cap and directed that this iterate to an actual reviewer PASS. Nothing has been struck and nothing is contested; every FIX in every round was accepted and applied. Rounds 4 and 5 both reported that no finding required design escalation.

### Resolved points

| # | Claim | Raised by | Outcome | Evidence |
|---|-------|-----------|---------|----------|
| 1 | `OpenOrCreate` reads a crash-truncated lock as free and steals it | reviewer | accepted into Task 3 | design spec `:237-250` |
| 2 | Idempotent acquire could not receive the nonce; lost-nonce deadlock | reviewer | accepted into Task 3 | plan r1 `:95-105` |
| 3 | Making the nonce visible in `-Status` closes the deadlock | session | accepted by reviewer | design spec `:211-215` |
| 4 | Junction "no file copied" oracle was vacuous | reviewer | accepted into Task 6 | plan r1 `:288-290` |
| 5 | Live gates asserted invariance that holds when the command failed | reviewer | accepted into Task 7 | design spec `:89-95` |
| 6 | Start-time fault needs a seam, not a SYSTEM process | reviewer | accepted into Task 3 | `tools/new-kimi-lane-home.ps1:416-423` |
| 7 | Builder could not release the lock it acquired | reviewer | accepted into Task 6 | plan r1 `:276-294` |
| 8 | Removal destroyed the home before discovering it could not release | reviewer | accepted into Task 6 | `tools/new-kimi-lane-home.ps1:65-133` |
| 9 | Host selector tests one host whatever CI sets | reviewer | accepted into Task 6 | `evals/multi-model-verify/test_kimi_lane_home.py:21` |
| 10 | Windows CI job runs a deleted test module | session | accepted, promoted to Task 1 | `.github/workflows/skill-evals.yml:84,95` |
| 11 | "Never pushed" was wider than the evidence | reviewer | accepted, then verified | no remote ref contains HEAD; `ls-remote` returns only `refs/heads/main`; no Actions runs |
| 12 | Contract lifecycle belongs in its own declared region | reviewer | accepted into Task 9 | `CLAUDE.md:55-92` |
| 13 | Acquire state table overlapped rows and overclaimed completeness | reviewer | accepted into Task 3 | plan r2 `:216-240` |
| 14 | Release and override behaviour on non-held records was undefined | reviewer | accepted into Task 3 | plan r2 `:232-265` |
| 15 | Task 8 promised a foreign-host override Task 3 forbade | reviewer | accepted; `-ConfirmHost` added | plan r2 `:181-206,436-452` |
| 16 | Inherited child streams and a JSON-only stdout are not jointly implementable | reviewer | accepted; verdict moved to a file | plan r2 `:316-341` |
| 17 | Task 7 forbade creating login B while its oracle required it | reviewer | accepted; claim narrowed | plan r2 `:399-426` |
| 18 | Unconditional `finally` released a SUCCESSFUL build's lock | reviewer | accepted into Task 6 | plan r2 `:369-375` |
| 19 | Region comparison compared raw bytes that can never be equal | reviewer | accepted, then verified | `evals/multi-model-verify/test_contract_coverage.py:21-30,517-526` |
| 20 | The history check printed matches without failing | reviewer | accepted into Task 10 | plan r2 `:529-535` |
| 21 | Three contract literals overstated their evidence | reviewer | accepted into Task 9 | design spec `:122-142` |
| 22 | `-MalformedOverride` covered only unparseable bytes, leaving reachable malformed classes unrecoverable | reviewer | accepted into Task 3 | plan r3 `:180-190` |
| 23 | An extra field on a FREE record was not malformed | reviewer | accepted into Task 3 | plan r3 `:118,190` |
| 24 | Exit 4 contradicted the two override exceptions | reviewer | accepted into Task 3 | plan r3 `:139-148` |
| 25 | Two conflicting token rules for `DebateId`/`Nonce` | reviewer | accepted; unified on 32 lowercase hex | plan r3 `:54-56` |
| 26 | The universal no-exit-1 claim cannot survive PowerShell's binder | reviewer | accepted; guarantee scoped to bound invocations, with a mutates-nothing test | `775472c^:tools/kimi-lane-lock.ps1:36-50` |
| 27 | Missing-file behaviour was undefined per mode | reviewer | accepted into Task 3 | plan r3 `:150-156` |
| 28 | The login wrapper wrote the home and ACL before taking the lock | reviewer | accepted; bootstrap made an explicit bounded exception | plan r3 `:51,252-254` |
| 29 | Stream inheritance was not actually tested; a buffer-and-replay wrapper would pass | reviewer | accepted; oracle made temporal | plan r3 `:250,258` |
| 30 | Cleanup needed two flags, not one | reviewer | accepted into Task 6 | plan r3 `:280-284` |
| 31 | The doctor's aggregate was not a total order; `N/A` had no rank | reviewer | accepted into Task 8 | `commands/doctor.md:6-9` |
| 32 | "The doctor mutated a credential" was wider than two hashes establish | reviewer | accepted; narrowed to bytes changed, actor not established | plan r3 `:346,355` |
| 33 | Adding modules to both CI steps had no oracle | reviewer | accepted; host parity added to the checker in Task 1 | `.github/workflows/skill-evals.yml:79-99` |
| 34 | The probe record commits complete client streams to a PUBLIC repo and can capture a credential value | reviewer | accepted; secret guard added to Task 7 | plan r4 `:29,346` |
| 35 | A token-rotation `assert` leaks both token values through pytest introspection | reviewer | accepted; comparison moved to `if` plus `pytest.fail` | plan r4 `:29,352` |
| 36 | `$buildCompleted` was set before the custody line was emitted, retaining an unreleasable lock | reviewer | accepted into Task 6 | plan r4 `:299-311` |
| 37 | The login literal omitted `-LaneHome`, authenticating a different home than the build used | reviewer | accepted into Task 9 | plan r4 `:261-266,423` |
| 38 | A free record carrying a held-only KNOWN field was not reached by the unknown-field rule | reviewer | accepted into Task 3 | plan r4 `:124-130,207` |
| 39 | `-MalformedOverride` on a well-formed foreign-host record had two outcomes | reviewer | accepted; preprocessing order added | plan r4 `:156,183-201` |
| 40 | Code 5's meaning covered only mismatch while three rows returned it for "nothing applicable" | reviewer | accepted into Task 3 | plan r4 `:151-159` |
| 41 | Task 2's fixture change had no oracle in its own task | reviewer | accepted; selector refactor moved into Task 2 | `evals/multi-model-verify/test_kimi_lane_home.py:21,310-320` |
| 42 | Task 5's exit table omitted binder code 1 and lock code 5 | reviewer | accepted into Task 5 | plan r4 `:279-281` |
| 43 | The doctor's hash prose could leave the validator substate unmeasured | reviewer | accepted; seven-step algorithm | plan r4 `:376-395` |
| 44 | The checker's initial required module set was not frozen | reviewer | accepted into Task 1 | `.github/workflows/skill-evals.yml:79-99` |
| 45 | Task 7's normalization retained an implementer-selected fallback | reviewer | accepted; complete normalized stderr, no fallback | plan r4 `:346` |

### Escalated points (user-decided)

None.







