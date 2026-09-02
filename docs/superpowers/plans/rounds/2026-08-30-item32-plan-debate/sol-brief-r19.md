# Round 19 - CONFIRMING ROUND. Your Task 8 fix, plus six the Fable lane found

You are the cross-vendor reviewer on backlog item 32 (detached dispatch) and
item 33 (automatic review mirror). This is round 19, and it is intended as
the CONFIRMING round before the plan is frozen.

The mirror is a fresh file copy of the working tree at source commit
`c36f8c2` on branch `item32-detached-dispatch`. Its own `HEAD` is the
builder's remediation commit, by construction. The plan file in the mirror
was hash-compared to the source before dispatch and is identical.

The plan is `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md`.
The spec is
`docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md`.

Ground every claim in a `path:line` you actually opened in this mirror.

## 1. Your round 18 finding - fixed

Task 8's oracle counted rows. The record now has a fixed field shape per
host, and the test asserts every value: `launch_return_seconds` parses as a
number and is under 15, `alive_in_later_call=true`,
`exit_file_after_sleep=true`; the three state names compared exactly against
`no-exit-file`, `no-receipt`, `reply-empty`; and `binder=accepted` with
matching hash and byte length. Plus a red demonstration: flip
`alive_in_later_call` in a scratch copy and confirm the test names that
field. The step also says that if a measurement comes out the other way,
write it as measured and STOP, because a probe that records what it hoped
for is worth less than no probe.

## 2. What you did not see: a second lane reviewed this plan

Because eighteen dispatches on one resumed session is a lot of anchoring, a
Claude-side reviewer read the plan cold at `061a2ee`. It found six defects
neither of us named. I reproduced all six in the repository before acting.
Two are mechanism-level, so YOUR round 18 verdict no longer covers this
head, which is why this round exists.

**A. The Kimi lane's reply encoding was never handled.** The wrapper
captured the client's stdout with `> $PSScriptRoot\reply`. That does not
copy bytes: PowerShell decodes native stdout using `[Console]::OutputEncoding`
- the OEM code page on Windows PowerShell 5.1, measured IBM437 in
`tools/new-review-mirror.ps1:64-66` - then re-encodes on write, UTF-16LE on
5.1 and UTF-8 on 7. A non-ASCII reply is mangled differently per host. This
is the class 0.23.0 fixed for the codex lane's OUTBOUND brief and item 51
owns for this lane's outbound argument; nobody had looked at the INBOUND
direction. The wrapper now sets `[Console]::OutputEncoding` to UTF-8 before
the call and writes the reply with .NET, no BOM. The passage explains why
`$OutputEncoding` still does not appear: it governs the opposite direction.
The codex lane is unaffected because `--output-last-message` is written by
the client itself and crosses no redirect.

**B. `${CLAUDE_PLUGIN_ROOT}` in skill TEXT is unverified, and I had been
treating it as settled.** In PowerShell `${NAME}` is variable syntax, so an
unsubstituted token expands to EMPTY and the path becomes the drive root -
failing exactly like item 58's mislocated tool. `hooks/hooks.json:10` uses
the token where the HARNESS substitutes it; skill body text today uses a
`<plugin-root>` placeholder instead (`SKILL.md:326`). Task 1 gains a step 0
that MEASURES which happens, and names both outcomes, including one in which
this plan's anchoring claim shrinks to "named, not resolved". It is also
listed as a third non-repo-verifiable harness fact in Global Constraints.

**C.** Region three claimed NO RECEIPT is the one case `taskkill /PID` cannot
clear. There is a second: a COMMITTED launch whose wrapper host died while
the client child lives. The pid on disk is the dead wrapper, so felling that
tree reports process-not-found and never reaches the orphan. The poll still
classifies it safely; only the remedy was overclaimed.

**D.** Task 3 told the implementer to keep everything from the
`verified-override-dispatch` marker onward verbatim, and that span includes
`SKILL.md:222-226`, whose `<reply-file>`/`<transcript-file>` freshness rule
names placeholders the rewrite removes. It now carries the same rule onto
the artifact that holds it: a fresh dispatch directory and a fresh receipt
path, refused by `-Launch` if either exists.

**E.** Task 8's Files list omitted `test_wrapper_probe_record.py`, which its
own commit stages.

**F.** The plan header still said "Revision 5"; and `design.md:208-210` says
a test counts four exact strings when it holds five. Both corrected, the
second added to Task 9's reconciliation list and its grep.

## What I want from you

1. Say CLOSES or DOES NOT CLOSE on your round 18 Task 8 finding, and give a
   verdict on each of A to F above, citing the `path:line` you read. Where
   you disagree with the other lane's diagnosis or my repair, say so plainly
   - I would rather have the disagreement than a rubber stamp. A is a real
   mechanism change and deserves your independent judgement, not agreement.

2. **The base rate is eighteen numbered dispatches out of eighteen** finding
   at least one completion-model hole, a non-binding oracle, or an internal
   contradiction - though rounds 10 through 18 found NO new false-completion
   path. State it. Then either name a new instance, or say explicitly that
   you searched and found none, and name what you searched.

3. This is the confirming round. If the plan is ready, say FREEZE without
   hedging. If it is not, name the smallest set of changes.

End with PASS, FIX, or ESCALATE.
