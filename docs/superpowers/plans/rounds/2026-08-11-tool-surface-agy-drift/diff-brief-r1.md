<role>Adversarial reviewer, equal weight, in a two-model DIFF debate. Neither side's claim outranks the other's; only evidence does.</role>

<task>Refute or confirm each numbered claim about the range `ef428c3..835226b` on branch `0.24.0-tool-surface-agy-drift` in the parallax repo at C:/Users/Brandon/Documents/parallax, read-only. The frozen plan is `docs/superpowers/plans/2026-08-11-tool-surface-agy-drift.md` (frozen at 7072889). The debate that produced it, six rounds plus one void round, terminal DRY at round 6, is in `docs/superpowers/plans/rounds/2026-08-11-tool-surface-agy-drift/`. The backlog items it closes (7, and 11 partially) and files (36, 37, 38, 39, 40) are in `docs/superpowers/plans/2026-07-27-0150-backlog.md`. Read whatever you need.</task>

<rules>
Cite repo-relative file:line for every claim you make or contest; uncited claims will be struck. Do not manufacture objections: if a claim stands, say PASS and move on. End each numbered claim with PASS, FIX (with the specific fix) or ESCALATE.

Three project invariants bind this repo, and a violation of any is a finding regardless of whether the design works:
- A claim may never be wider than its evidence.
- An unmade, failed, or unreadable measurement is never a clean one.
- A test is not evidence until it has been watched to FAIL for the reason it claims. A FIX is new code and gets no discount.

TWO Fable whole-branch reviews already ran and both are retained verbatim beside the round records:
- `docs/superpowers/plans/rounds/2026-08-11-tool-surface-agy-drift/fable-review-1-ef428c3-5133f98.md` — ready to merge WITH FIXES; 2 Important, 4 Minor.
- `docs/superpowers/plans/rounds/2026-08-11-tool-surface-agy-drift/fable-review-2-ef428c3-710d74f.md` — ready to merge YES; 0 Important, 4 Minor, run over the range INCLUDING the fixes because a fix is new code.

The session's per-finding adjudications are amendments 7 and 8 of the build checkpoint at `.git/parallax/application-checkpoints/2026-08-11-1630-7945ac1-0240-build.md`. ATTACK THE DISPOSITIONS, not just the code. Two are worth your attention: review 2's Minor 1 was FILED as backlog item 40 rather than fixed, on the scope rule; review 2's Minor 4 was recorded as verified-by-reading rather than tested. A finding both Fable passes missed is worth more than one either made.

This cycle's own plan debate produced nineteen findings and every one was the same class: the session's claim being wider than its evidence, with fixes applied only where the reviewer had cited them rather than everywhere the class occurred. Hunt that shape specifically.
</rules>

<claims>

1. **Every failure direction of the new tool-surface probe lands on BLOCKED, and no unmade measurement can produce a clean report.** `tools/codex-tool-surface-probe.ps1`. The blocked directions are: process not started, launcher unresolvable, stdin preamble present, stdin preamble unreadable, timeout, non-zero exit, RPC error, unreadable JSON anywhere in the stream, no frames at all, no answer to `mcpServerStatus/list`, and an uncalibrated pass 1. `Test-Transport` is the single funnel and there is one caller. Attack it: find a state where the probe reports clean without having read a surface, or a blocked reason that misdescribes its own cause.

2. **The clean report is stated as a MITIGATION and as a PROXY, and never wider, on every surface that carries it.** Absence in pass 2 cannot be distinguished from a server that failed to launch (measured: null `serverInfo`, zero tools, `authStatus: unsupported`, no separating field), and the probe reads `codex app-server` while the review dispatches `codex exec`, which was measured only to ACCEPT the flags. That second caveat now appears in `README.md`, the probe header, `skills/multi-model-verify/references/model-prompting-notes.md` (outside the pinned contract regions), backlog item 7's record, and new item 39. Attack it: find an instance that says something the others do not, or any surviving sentence anywhere in the repo that claims the reviewer's tool surface is measured rather than proxied.

3. **Two host-shaped transport defects were found AFTER the probe's tests passed, and the repairs are placed where they can actually work.** The launcher: `codex` resolves to `.ps1`, `.cmd` and an extensionless file with no `.exe`, and `Process.Start` can launch none directly. The stdin preamble: under Windows PowerShell 5.1 the first JSON-RPC frame arrived as `EF BB BF 7B 22 ...` because `Process.Start` builds stdin from `Console.InputEncoding` and sets AutoFlush, which flushes; two other repairs were tried and measured to fail before the encoding was moved BEFORE `Process.Start`. Attack it: is there a THIRD host-shaped assumption still unexamined in that script, and is the self-check that blocks on a surviving preamble reachable in every case it claims?

4. **`tools/check-drift.ps1` and `commands/doctor.md` check 7 now assert the same agy contracts, verdict for verdict, across every fact they share.** Eleven facts were compared, not just the one a review cited. Attack it: find a twelfth fact, or a state where the two still disagree. Note that two OTHER version probes in the same file do not check exit codes; that is known, pre-existing, outside the plan's enumerated surface, and filed as item 40. If you think the scope rule was misapplied there, say so as a finding against the DISPOSITION.

5. **Item 11 is closed NARROWER than it asks, deliberately, and says so.** No version FLOOR, because no agy breakage boundary has been measured and the Fable seat's floor exists only because one was. No transcript-path assertion, because a transcript exists only after a run. The security contract it lists is UNMEASURED and the item stays partially open on it, with item 36 carrying the two questions on `allowNonWorkspaceAccess`. Attack the narrowing: is a lane with contract checks but no floor actually protected, and does calling item 11 partially closed overstate what shipped?

6. **The state-machine scenarios discriminate, and the two fixture repairs inside them were real defects rather than tidying.** Fifteen agy scenarios including a positive control. The fixture repairs: `LOCALAPPDATA` was unredirected, so an offline suite would have made a real network call; and the `.cmd` stubs inherited the harness source's line endings, so they worked only because git rewrites that file at checkout, and an LF-only batch file cannot resolve a `goto` label. Attack it: find a scenario whose assertions a watcher that never looked at agy could satisfy another way.

7. **The five filed items (36, 37, 38, 39, 40) are each at the width their evidence supports, and the retracted claims are retracted rather than restated.** Item 36 names TWO questions because naming only one would promote a version-bounded measurement into a present-tense requirement. Item 37 is narrow because two wider drafts were refuted in debate: promotion HAS happened and `debate-protocol.md` IS the home, so the gap is the missing STEP. Item 38 retracts the claim that codex loads project-local skills from `<repo>/.codex` when untrusted; that was the client's own description, never a measurement. Attack any of them for being wider than its evidence, or for restating something this cycle retracted.

8. **The stated limits are complete.** Look for a limit this branch plainly has that it admits nowhere: not in the plan, not in the build checkpoint, not in the shipped text, not in a backlog item, not in a test comment.

</claims>

<boundaries>
Already decided and NOT under debate: the release grouping; that this branch closes items 7 and 11 and no others; that the fix-verify budget and round cap for THIS debate are 4 and 4, set before round 1 and authorized by the user.

Explicitly out of scope, named BEFORE any finding: `tools/check-drift.ps1:700` and `commands/doctor.md:70`, which carry backlog item 31's defective dispatch form. Item 31 is open and this cycle does not close it. Also out of scope: backlog items 12, 15, 26-remainder, 29, 32, 33, 34, 35.
</boundaries>

<final-check>List any claim you could not verify against files you actually read, as UNVERIFIED. Do not fold unverified material into your verdict.</final-check>
