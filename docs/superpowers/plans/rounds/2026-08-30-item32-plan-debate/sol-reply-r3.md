The revision closes four findings and leaves four open. The recurring defect class is still active: Task 5 once again allows prose to stand in for an executable detached launch.

## Changes 1–8

1. Unimplemented staleness rule

The output refusal is now executable and precedes `Start-Process` (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:441-445`). Task 2 also pins all six output paths in that loop (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:183-201`).

The input-creation defect is separate and addressed under item 2.

**CLOSES — PASS**

2. Unsatisfiable freshness rule

The contract now correctly distinguishes two inputs from six outputs (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:20`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:293-300`). The implementation does not provide the promised create-new semantics, however:

- Wrapper creation remains an instruction to “write this wrapper,” with no exclusive creation operation (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:407-413`).
- The empty file uses `WriteAllText`, which overwrites an existing file rather than failing when the path is taken (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:441-445`).
- Task 2 pins only output refusal and contains no input create-new assertion (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:183-201`).

**DOES NOT CLOSE — FIX: specify and pin atomic create-new operations for both wrapper and empty stdin, with creation failure stopping before `Start-Process`.**

3. State list

The marked region now enumerates the missing zero-without-reply state and calls it a transport failure (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:283-300`).

But the rest of the plan remains inconsistent:

- Global Constraints still says five states (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:19`).
- Task 4 tells the shipped `SKILL.md` reader to poll for five states (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:434-439`).
- The revised spec still says the poll distinguishes four states (`docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:185-193`).

The region pin can pass while the point-of-use instruction and design remain wrong.

**DOES NOT CLOSE — FIX: change every count to six, update the spec’s state model, and add a pin covering the point-of-use “six states” reference in `SKILL.md`.**

4. Kimi deferral

The deferral is withdrawn, and the two native wrapper lines preserve the documented flag order and inline `$b` payload (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:573-595`). That part is correct.

Detachment is still not implemented:

- There is no Kimi `Start-Process` command. Task 5 only says to launch using SKILL.md’s block “plus `-WorkingDirectory`” (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:597-601`).
- The raw test asserts the two native lines and that `-WorkingDirectory` appears somewhere, but never asserts `Start-Process`, PID publication, refusal, stream redirection, or a sidecar-bearing launch (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:517-550`).
- The write-probe is again implemented only as the sentence “the write-probe runs in a wrapper too” (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:548-550`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:608-614`).
- Successful Kimi wrappers write only `<transcript-file>` and `<exit-file>`, never the `<reply-file>` required for state six (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:575-594`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:288-292`). Every successful Kimi call therefore lands in state five, “zero but no reply,” and is discarded.
- Task 8 parses only wrapper bodies, while Task 9 measures only the Task 4/Codex launcher (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:785-818`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:845-873`).

**DOES NOT CLOSE — FIX: provide and pin a complete Kimi launch block; bind the write-probe to that executable block; define the Kimi reply artifact used by state six; and stub-run the actual Kimi launcher, not only its wrapper body.**

5. Stale enumeration in the spec

The spec now lists two Codex and three Kimi calls with explicit Task 4/Task 5 dispositions (`docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:56-76`). It also records why the Kimi deferral was reversed (`docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:78-86`).

What I read to pass it: the complete revised scope table and disposition explanation. Other spec sections remain stale, but the enumeration finding itself is closed.

**CLOSES — PASS**

6. Background-task naming

Naming now has its own marked region, explicitly says nothing enforces it, and limits its pin’s meaning to written documentation (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:321-337`). The planned test name and docstring also distinguish documentation presence from behavioral enforcement (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:366-370`).

**CLOSES — PASS**

7. Parse sensitivity

The proposed parser/stub task is substantially better, but two concrete extraction/execution holes remain:

- The documents contain wrapper and launch fences of the same language without unique IDs. For Codex, the wrapper fence is immediately followed by another PowerShell launch fence (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:416-445`). “Extract four fenced blocks” does not define which four or require exactly one match per intended wrapper (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:785-791`).
- The Kimi wrapper invokes an absolute `<kimi-code-binary>` path (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:575-594`), while Task 8 proposes intercepting `kimi.exe` by putting a stub first on `PATH` (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:806-818`). PATH ordering does not intercept an absolute executable path. The test must substitute the placeholder with the stub’s absolute path.

**DOES NOT CLOSE — FIX: give each wrapper a unique extraction marker, require exactly one exact match, preserve the Markdown-to-copied-code indentation transformation, assert no placeholder remains, and replace `<kimi-code-binary>` with the stub’s absolute path.**

8. Kill race

The stub now creates a deterministic thirty-second interval after publishing the reply, and the plan kills during that interval before polling (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:851-867`). This closes the nondeterministic real-client race.

**CLOSES — PASS**

## UNVERIFIED

- Actual survival across the harness boundary remains unverified until Task 9 runs (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:845-849`).
- Fresh-shell and Agent-background behavior remain harness-contract facts rather than repo evidence (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:26`).
- Task 8’s extraction fidelity and guarantee that no real Kimi client runs are unverified because the test does not yet exist (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:770-829`).
- The real Kimi client was not used in item 51’s argv probe; that probe used a Python stub (`docs/superpowers/plans/rounds/2026-08-22-item51-inline-brief-probe/probe-record.md:27-39`).
- Hook suppression remains planned rather than implemented; current mirror code still invokes `git add` and `git commit` without the proposed isolation (`tools/new-review-mirror.ps1:1071-1089`).

## Sweeps

Base rate: round 1 found a killed wrapper that could combine with stale success artifacts and read clean; round 2 found a missing zero-without-reply state (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:947-950`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:969-974`). The prior that the completion class is exhausted is therefore weak.

### (a) Seventh state or unclassified combination

Yes. State six currently accepts “exit zero and a reply file” based only on path existence (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:284-292`). It does not classify:

> Exited with zero and a reply path present, but the reply is empty, unreadable, still incomplete, or rejected by the lane’s evidence binding.

That is not a review result. The existing Kimi evidence contract already says unreadable, malformed, missing, or unequal evidence discards the reply (`skills/multi-model-verify/references/backup-lane.md:248-274`).

For the two partial-write races:

- If the wrapper is still alive while the exit or reply is being written, state one must dominate. The contract should state that liveness is checked first and no files are interpreted while the recorded wrapper is live (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:284-290`).
- After confirmed wrapper exit, a partial or unreadable exit artifact belongs in state three, but state three should explicitly include unreadable, wrong-type, and failed reads rather than only “not a plain integer” (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:285-288`).

The refusal loop also has a check/use window: it tests absence and then starts the process without reserving the output namespace (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:441-445`). A prior orphan or concurrent attempt can create artifacts after the check. Round-numbered names alone are known not to be unique across concurrent debates (`skills/multi-model-verify/references/model-prompting-notes.md:279-295`). Use a per-dispatch unique directory or nonce-bound sidecar, not only round numbering.

**FIX — make state six a candidate until the fresh reply is readable and passes the lane’s existing binding; explicitly prioritize liveness; broaden state three to failed reads; and bind artifacts to a unique dispatch instance.**

### (b) Wrapper extraction false-green

A concrete false-green is wrong-fence selection. Adding or moving another `powershell` example before a wrapper can make an ordinal/regex extractor parse a launch or example block while the actual wrapper copied by the session contains a syntax error. The Codex section already has two adjacent PowerShell fences, wrapper and launcher (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:416-445`).

A second concrete false-green is normalization repair: an extractor that dedents or rewrites Markdown indentation can parse bytes different from those a session copies from the indented Kimi fences (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:573-595`).

A third is Kimi stub bypass: PATH shadowing leaves the absolute `<kimi-code-binary>` invocation untouched, so the supposed zero-quota gate can call the real client unless the renderer replaces that placeholder with the stub’s absolute path (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:575-594`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:806-818`).

**FIX — unique markers, exact-one extraction, an explicit copy-equivalent indentation algorithm, zero remaining placeholders, and absolute stub substitution.**

### (c) Verification that passes while its own change is absent or partial

Yes; several tasks have this shape.

- Task 1 can pass unchanged. Its budget tests read `BODY_TOKEN_CEILING` dynamically rather than asserting 5900 (`evals/multi-model-verify/test_skill_lint_budget.py:68-96`), and strict lint already passes under the current ceiling. Add an exact constant-and-comment assertion tied to the measured value (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:52-66`).

- Task 2’s targeted command does not select its newly added refusal test. The test is named `test_the_launch_refuses_a_pre_existing_output_path`, but the `-k` expression includes only `exit_code_file`, `launched_detached`, `here_string`, and `pre_client_failure` (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:183-225`). The later full suite catches it, but Task 2’s own fail-first verification does not.

- Task 4 can pass partially. No test pins create-new input semantics or the point-of-use state count, so `WriteAllText` overwrite behavior and “five states” survive its full suite (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:434-469`).

- Task 5 is the direct recurrence. Its test passes with no `Start-Process` command, no executable write-probe wrapper, and no Kimi reply artifact because it checks only two native lines, one `-WorkingDirectory` substring, and one prose sentence (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:517-550`).

- Task 8 can pass against the wrong extracted fences unless extraction identity is itself asserted, and its PATH Kimi stub does not intercept the documented absolute binary (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:785-818`).

- Task 9 still instructs its record to say the Kimi lane “was not detached,” directly contradicting Task 5 (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:879-883`). Task 10 repeats that stale closure statement (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:928-933`). Their gates can all pass while the committed records falsely describe scope.

- The spec’s scope table is corrected, but its constraints still say four states, its testing section still proposes obsolete region names, and its timeout remains an open question (`docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:185-205`, `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:222-258`). No plan task verifies plan/spec convergence.

**FIX — add task-local oracles for the exact intended changes, strengthen Task 5 around executable launches and reply artifacts, bind Task 8 extraction identities, correct the stale Task 9/10 records, and update/pin the remaining stale spec sections.**