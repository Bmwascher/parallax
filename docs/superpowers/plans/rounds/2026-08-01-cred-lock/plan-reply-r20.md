## Shared implementer packet

The shared-constant placement is correct and preferable to duplication, but the constant has two blocking defects.

First, “emitted verbatim by every surface” is wider than its intended consumers. Task 2 directly reports `absent`, `unreadable`, and `malformed`; Task 5 reports those post-run verdicts; and Task 7 explicitly requires only a message naming the wrapper. A zero-judgment implementer must choose whether the global rule overrides each task. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:76-82`, `:129-140`, `:375-379`, `:446`

Narrow line 76 to:

> THE LANE LOGIN RECOVERY COMMAND, emitted by exactly two surfaces: Task 6’s builder refusal for an absent, unreadable or malformed lane credential, and Task 8’s corresponding doctor rows.

Second, the command is not fail-closed. It separates owner resolution and login with a semicolon but never checks the former’s exit code, and its JSON conversion lacks `-ErrorAction Stop`. The repository’s existing scripts capture `$LASTEXITCODE` immediately after an invoked command and use terminating JSON parsing where subsequent action depends on the result. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:78-82`, `tools/check-drift.ps1:145-149`, `tools/check-drift.ps1:208-210`, `tools/read-kimi-round-evidence.ps1:206-210`

Replace it with this one executable line:

```powershell
$ownerJson = & 'tools/kimi-lane-lock.ps1' -ResolveOwner; if ($LASTEXITCODE -ne 0) { throw "owner resolution failed with exit $LASTEXITCODE" }; $owner = $ownerJson | ConvertFrom-Json -ErrorAction Stop; & 'tools/new-kimi-lane-login.ps1' -LaneHome '<lane-home>' -OwnerPid $owner.ownerPid -OwnerStartTicksUtc $owner.ownerStartTicksUtc -VerdictOut (Join-Path $env:TEMP 'parallax-kimi-lane-login-verdict.json'); if ($LASTEXITCODE -ne 0) { throw "lane login failed with exit $LASTEXITCODE" }
```

Also make the escaping algorithm literal: replace every `'` in the resolved path with `''`, then enclose the result in single quotes. “Single-quote-escaped” otherwise still leaves the mechanical transformation implicit. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:82`

**Implementer packet — FIX (BLOCKING): narrow the consumers, make the command fail-closed, freeze escaping, and add the execution oracle described under Task 6.**

## Per-task verdicts

### Task 1

The path-existence, host-parity, and mutation oracles remain complete. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:96-121`

**Task 1 — PASS**

### Task 2

The task-local validator contract remains complete, but the current universal recovery-command rule contradicts its exact one-line JSON output. Narrowing the shared rule fixes this without changing Task 2. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:76-82`, `:125-152`

**Task 2 — FIX (BLOCKING, shared-packet edit only): narrow the recovery-command consumers.**

### Task 3

All three round-19 changes are correctly applied:

- Fresh acquisition now distinguishes empty stderr from nonce stdout.
- Both contention mechanisms and both liveness substitutions have failure-capable oracles.
- Both overrides have exact stderr contracts, empty stdout, and table rows consuming those contracts.

`docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:237-258`, `:269-287`

**Task 3 — PASS**

### Task 4

The OS-level gate remains correctly separated from Task 3’s implementation oracle. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:323-344`

**Task 4 — PASS**

### Task 5

The new stream rule and both caller-boundary tests correctly close the swallowed-diagnostic defect. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:361-381`

The only remaining conflict comes from the shared rule’s unintended claim that every credential-status surface emits the recovery command. Narrow that rule; do not change Task 5.

**Task 5 — FIX (BLOCKING, shared-packet edit only): narrow the recovery-command consumers.**

### Task 6

The stderr propagation and both integration oracles are correct. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:397-405`

The six-step B/A fixture is now deterministic and reaches the wrong-`-Path` assertion without contending during setup. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:417-429`

Two fixes remain:

1. Replace “recovery command below” with “recovery command from Fixed names and values”; the command is above Task 6, not below it. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:76-82`, `:429`

2. Asserting the emitted string whole is not an adequate oracle for an executable recovery command: the current broken semicolon form would satisfy that assertion. Add dual-host tests that:

   - Execute the emitted command with a failing `-ResolveOwner` stub, require nonzero, and prove the login stub was never invoked.
   - Execute it with successful owner resolution and the real wrapper against a disposable fake binary, require an `ok` verdict and structurally valid fake lane credential.
   - Use no real credential or real user profile.

   Task 6 currently asserts only the command text, so neither execution direction is reached. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:429-435`

**Task 6 — FIX (BLOCKING): correct the pointer and add success/failure execution oracles for the hardened shared command.**

### Task 7

The local custody and support contracts remain sound, but its preflight currently promises only a message naming the wrapper, contradicting the shared rule’s “every surface” wording. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:440-463`

Narrow the shared rule to Tasks 6 and 8; do not expand Task 7.

**Task 7 — FIX (BLOCKING, shared-packet edit only): narrow the recovery-command consumers.**

### Task 8

The three credential statuses now consume one shared command and the complete string is pinned, which is the correct anti-drift structure. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:570-594`, `:621-625`

Its command remains broken until the shared constant is made fail-closed. Task 8 needs no duplicated literal or separate execution suite once Task 6 executes the shared command and Task 8 pins its complete emitted form.

**Task 8 — FIX (BLOCKING, shared-constant edit only): use the hardened recovery command.**

### Task 9

The malformed summary now matches Task 3’s schema rule, including non-object, version/state, state-specific field-set, type, and validation failures. Its visibility sentences match the direct-tool contracts. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:299`, `:629-649`

**Task 9 — PASS**

### Task 10

The final dual-host, live, behavioral, and mutation-tested history gates remain complete. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:660-682`

**Task 10 — PASS**

## Answers

1. **Not yet PASS.** The shared recovery command needs the precise fixes above.

2. **Do not duplicate it.** Keeping one command in `Fixed names and values` is the correct packet design because every implementer receives that block. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:68-92` Narrow its consumers and harden its execution rather than copying it into Tasks 6 and 8.

3. The third comparison is **plan prose versus actual interpreter/runtime semantics**. Plan-versus-spec found missing behavior; tool-versus-caller found swallowed behavior; prose-versus-runtime finds a command that looks complete but continues after a failed prerequisite. The repository itself uses explicit exit capture and terminating JSON parsing where later operations depend on earlier measurements. `tools/check-drift.ps1:145-149`, `tools/check-drift.ps1:208-210`, `tools/read-kimi-round-evidence.ps1:206-210`

Before building, the remaining executable snippets should receive that audit under both declared PowerShell hosts, including their failure direction—not merely string pins. The recovery command is the concrete survivor. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:49-52`, `:76-82`

## Overall verdict

**FIX — BLOCKING.**

Round 19’s direct-tool, caller-propagation, fixture, doctor, and shipped-contract changes are otherwise correctly applied. The only behavioral blocker is the new shared recovery command and the overbroad scope assigned to it.

## Final check

UNVERIFIED:

- Measurements 1–21 remain externally obtained; the spec expressly says they were measured on this machine and distinguishes them from repository live gates. `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:35-43`, `:45-67`
- Three lane logins plus the user’s login remains a generalization from the two-login measurement. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:463`
- The second fable artifact is now inspectable and accurately identifies its revision-17 subject and round-19 adjudication. Its provenance remains unverifiable by design because it is a session reproduction rather than an independent transcript. `docs/superpowers/plans/rounds/2026-08-01-cred-lock/fable-whole-plan-review-2.md:1-5`, `:20-24`, `:81-90`
- The remote-branch and Actions-history claims were not independently rerun here. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:100`
- No implementation exists yet; the second review likewise records that no code or SDD ledger existed. `docs/superpowers/plans/rounds/2026-08-01-cred-lock/fable-whole-plan-review-2.md:3-5`, `:60-62`

The absence of runnable pytest gates at this pre-build stage is not a finding.

