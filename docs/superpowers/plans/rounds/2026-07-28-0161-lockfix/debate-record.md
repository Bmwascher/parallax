# 0.16.1 mode-diff debate record

**Range:** `c408637..f41b95f`, branch `0.16.1-lockfix`.
**Mode:** diff. **Terminal verdict:** PASS (session adjudication, round 5).
**Verification status:** FULL. **Route:** effective route confirmed.
**Reviewer:** `gpt-5.6-sol`, effort high, sandbox read-only, session
`019fa920-1622-7cc2-895f-ec048087b865`, five rounds, header route confirmed
on every call.

## Why this release exists

0.16.0 shipped a lane lock that did not lock, on one of the two supported
hosts. `Get-LockAgeMinutes` required the parsed `stamp` to be a `[string]`.
Windows PowerShell 5.1 returns one; PowerShell 7 auto-converts an ISO-8601
string to a `DateTime` inside `ConvertFrom-Json`. So on pwsh every
well-formed lock read as unusable, every lock was immediately breakable, and
the lane provided no exclusion at all.

Nothing in the 0.16.0 process could have caught it. Seven cross-vendor
rounds, a whole-branch review and an independent backup-lane round all read
that code, and the local suite ran green every time — because the test
helper picks `powershell.exe` when both hosts are installed, and this
machine has both. CI, running an Ubuntu image with only pwsh, failed on the
release merge commit itself. The user surfaced it from a phone
notification.

The string check was not wrong. It came from round 3 of the 0.16.0 debate
and stopped an object-valued stamp throwing and wedging the lane. It was
wrong about the NORMAL case on the other host.

## Rounds

| round | verdict | what it found |
|---|---|---|
| 1 | FIX | The first fix reopened the wedge it inherited: converting `DateTime.MaxValue` with Kind Local or Unspecified overflows in any zone west of UTC, throwing before the negative-age guard. Also: `PARALLAX_PS_HOST` made both hosts SELECTABLE while nothing made anyone run both, so a 5.1-only regression could still ship |
| 2 | FIX | The "both hosts" claim was half false. `test_attestation.py` drives the same scripts, hard-selected `powershell`, and ignored the selector, so a run labelled pwsh tested 5.1 twice; the new Windows CI job covered only the lock module |
| 3 | FIX | The concurrency note asserted more than the probe showed: distinct session ids are necessary and not sufficient, because round-numbered reply and transcript names are unique within a debate and not across two at once |
| 4 | FIX | The same note omitted the BRIEF file, which is read back by the dispatch, so two debates sharing it collide even with distinct outputs. And "shared stores are not read as evidence" was false: `codex login status` is the auth preflight and config resolution is what the header reports |
| 5 | PASS | Every caller-selected file named, both collision modes explained, the round-2 relaxation correct against the resume transport, shared-state wording precise |

Three of the five rounds found a defect inside the previous round's fix,
continuing 0.16.0's rate. Two were in prose I wrote about my own probe.

## What changed

- The age routine takes a `DateTimeOffset` as-is, converts a `DateTime`
  inside a guard that returns the unusable sentinel on overflow, parses a
  string as before, and rejects everything else — then computes age ONCE.
  Three return paths each needed their own negative-age guard, which is
  three chances to forget one.
- `PARALLAX_PS_HOST` selects the interpreter in both dual-host test modules.
  The hook tests stay pwsh-only because `hooks.json` invokes the hook as
  pwsh; the drift state-machine test stays 5.1-only because the scheduled
  task pins `powershell.exe`.
- A `windows-latest` CI job runs both dual-host modules under each
  interpreter. The host gap is now gated, not merely reachable.
- `references/model-prompting-notes.md` records what this lane's
  concurrency actually is, since the user asked and nothing stated it.

## Independent confirmation

CI green on both jobs for `f527301`, `11f28ce` and `9ff5558` — the ubuntu
suite and the new windows dual-host job. The gate that found the defect
agrees the defect is gone.
