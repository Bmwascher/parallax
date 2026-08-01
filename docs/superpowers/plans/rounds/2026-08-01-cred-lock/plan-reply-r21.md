## Shared implementer packet

The new global constraint overreaches as written. Its first sentence covers every executable snippet, and its final sentence requires every user-facing snippet to be executed under both hosts in both directions. That conflicts with Task 8, which intentionally pins—but does not separately execute—the two single-invocation override commands. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:53`, `:602`, `:616-631`

Narrow it to:

> Every USER-FACING MULTI-STEP COMMAND emitted as one copy-paste unit, where a later step consumes an earlier step’s output, must fail closed at every dependency. Check an invoked command’s exit code before consuming its output, and parse dependent JSON with `-ErrorAction Stop`. A string pin is necessary but not sufficient: the emitting task executes the exact emitted command under every host it claims, covering every prerequisite-failure row and the all-success row. Standalone single-script commands, verification commands, parameter/JSON examples, and documented prose lifecycles remain governed by their task-local oracles.

That keeps the valuable runtime rule without forcing redundant suites for Task 8’s single-script overrides, Task 9’s prose lifecycle, or every standalone pytest invocation. Task 3 already tests both override modes under both hosts, while Task 8 pins their emitted syntax. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:248-262`, `:317-322`, `:616-631`

**Implementer packet — FIX (BLOCKING): narrow the runtime rule to emitted, dependent, multi-step commands.**

## Per-task verdicts

### Task 1

The portable path and parity checks remain failure-capable and mutation-tested.

**Task 1 — PASS.** `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:100-125`

### Task 2

The validator contract and dual-host fixture oracle remain complete; the recovery-command consumer narrowing no longer conflicts with its exact JSON output.

**Task 2 — PASS.** `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:129-160`

### Task 3

The direct-tool state partitions, exact diagnostics, both override reports, and handle/LIVE/UNMEASURABLE oracles remain complete.

**Task 3 — PASS.** `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:165-317`

### Task 4

The synchronized crash and partial-prefix gates remain decisive.

**Task 4 — PASS.** `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:327-348`

### Task 5

Lock stderr is now propagated unchanged with caller-boundary reclaim and contention tests, while client-stream inheritance remains separately tested temporally.

**Task 5 — PASS.** `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:352-390`

### Task 6

The recovery command itself is correct, but Step 1b still under-partitions its execution states.

The command has three dependent boundaries—owner exit, owner JSON parse, and login exit—while the oracle covers only owner-exit failure and all-success. An implementation/runtime defect at JSON parsing or the second exit check is not exercised. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:78-86`, `:434-437`

The escaping algorithm also has no failure-capable oracle: both execution tests can use an ordinary path, allowing an implementation that never doubles apostrophes to pass. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:86`, `:434-437`

Replace Step 1b’s “both directions” with this four-row matrix, under both hosts:

| Owner command | Owner JSON | Login | Required |
|---|---|---|---|
| nonzero | none | never invoked | command nonzero |
| zero | malformed | never invoked | terminating parse failure |
| zero | valid | nonzero | login invoked; command nonzero; no `ok` verdict |
| zero | valid | zero | command zero; `ok` verdict; structurally valid fake credential |

Use an apostrophe-containing resolved lane home in the success row and require:

- The emitted command contains the doubled apostrophe.
- It writes only to the intended lane home.
- The credential is structurally `ok`.

Freeze fixture routing so no judgment remains:

- Execute from a disposable current directory containing `tools/`.
- For the first three rows, place the specified owner/login stubs there and use invocation-marker files.
- For success, copy the actual lock, login wrapper, and validator scripts into that disposable `tools/` directory and provide the fake client under a disposable `USERPROFILE`.
- Execute the exact line extracted from the builder’s refusal.

The stderr-propagation and B/A wrong-path work are correctly applied. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:407-433`

**Task 6 — FIX (BLOCKING): replace the two-direction oracle with the four-row execution matrix and exercise apostrophe escaping.**

### Task 7

The live custody, setup, secret guard, and fixture routing remain complete once the global snippet rule is narrowed as specified.

**Task 7 — PASS.** `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:448-574`

### Task 8

Task 8’s local structure is correct: the shared login command is pinned here and executed once in Task 6, while the single-invocation override commands are directly exercised in Task 3. Its “no duplicate suite” decision should remain.

It conflicts only with the current overbroad global constraint.

**Task 8 — FIX (BLOCKING, shared-packet edit only): narrow the global runtime rule; do not add another suite.** `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:578-633`

### Task 9

The three exact regions remain consistent with the implementation rules and whole-region pinning.

**Task 9 — PASS.** `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:637-664`

### Task 10

The history oracle is still fail-open on its own measurement. `git log` feeds `$hits`, but its exit code is never checked; if the range cannot be read, `$hits` can remain empty and the snippet reaches `"clean"`. That contradicts the governing invariant and the newly added runtime rule. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:40`, `:684-690`

Replace it with:

```powershell
$messages = git log --format=%B 6201e30..HEAD
$gitExit = $LASTEXITCODE
if ($gitExit -ne 0) { throw "git log failed with exit $gitExit" }
$hits = $messages | Select-String -Pattern "Claude-Session"
if ($hits) { $hits; throw "AI-attribution trailer found; the repo forbids it" }
"clean"
```

Keep the controlled trailer mutation and add an invalid-revision mutation proving `git log` failure throws and never prints `clean`.

**Task 10 — FIX (BLOCKING): make the history measurement fatal before interpreting its output.**

## Answers

1. **Not yet PASS.** The blocking items are the global-rule scope, Task 6’s incomplete command-state oracle, and Task 10’s unchecked `git log`.

2. **Yes, the standing rule overreaches.** The useful scope is dependent, multi-step, user-facing commands. Applying it universally would force redundant execution suites for Task 8’s single-script override commands and blur the distinction between executable recovery commands, ordinary verification commands, examples, and prose lifecycles. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:53`, `:616-631`, `:643-653`

3. A fourth pair exists: **oracle versus reachable failure-state partition**. Fixture constructibility was its first example; Step 1b is another. Saying “both directions” hides four reachable rows, leaving JSON-parse failure and login failure unexercised. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:15-16`, `:434-437`

The previously found **plan versus implementer packet** is another already-closed boundary: the exact seven-block packet now makes it explicit. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:88-96`

I therefore do not consider the comparison set closed at revision 20. After the three fixes above, I see no additional unexamined artifact boundary in this scope: the plan has then been checked against the settled spec, current repository, task packet, serial task dependencies, runtime semantics, caller propagation, fixture/failure reachability, shipped contract, and CI gates. The abstract category can never be proven finite, but that is the complete operational matrix for this plan.

## Overall verdict

**FIX — BLOCKING.**

Round 20 correctly hardened the command, narrowed its consumers, froze escaping, and placed execution in Task 6. The remaining defects are in the scope and completeness of the new runtime rule’s own oracles.

## Final check

UNVERIFIED:

- Measurements 1–21 remain external measurements rather than repository-test results. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:57-68`
- Three lane logins plus the user’s login remains an explicit generalization from measurement 11. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:471`
- The retained fable report remains a session reproduction without an independent transcript. `docs/superpowers/plans/rounds/2026-08-01-cred-lock/fable-whole-plan-review-2.md:20-24`
- The remote-branch and Actions-history claims were not independently rerun here. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:104`
- No implementation exists yet, so none of the planned pytest gates can validate built behavior. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:165-169`

No absent implementation or unavailable pre-build pytest run is treated as a finding.

