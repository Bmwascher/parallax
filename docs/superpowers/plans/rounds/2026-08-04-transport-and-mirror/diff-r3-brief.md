Round 3, fix re-review. Rules as before.

All five round-2 findings are applied at `a1f0ddd`. Read
`git diff 43e45ef..a1f0ddd`. The full range is now `e94c0b5..a1f0ddd`.

WHAT I DID.

R2-6 / D21. Now reads: "None of those departures weakens coverage, and the
added assertions are strictly stronger; the rename and the second removal
helper change no assertion at all."

R2-6 / D24. Now says FOUR copies, names the test-module site as the fourth, and
carries a paragraph stating that the count was wrong when first written, that
the fourth did not match my grep, and that my round-2 brief asserted "All three
are now consistent" while it was open. It does not present itself as having been
complete.

R2-A. The `test_kimi_lane_home.py` section comment now matches the other three:
no shipped writer targets the directory, `New-Item` creates it, the only other
writers are the two env-gated seams, no shipped caller enables them, and they
can only make a build fail. Its point about the cases proving the DETECTOR is
untouched.

R2-7. Item 18 now reads: expectation 1 asks that the run invoke `codex exec`
with the reviewer model and `--sandbox read-only`, which means the grader has to
SEE that invocation; the harness's transcript rendering truncates the visible
PowerShell tool call before the `codex exec` command appears, so the grader
cannot observe what it is asked to judge however correctly the run behaved.

R2-additional. Item 17's Resolved block no longer says "the same cell, one flag
apart". It now says "the paired flag-on cell, differing from it in the flag and
in its own freshly built debate home".

ONE THING I DID BEYOND YOUR FINDINGS, and it is the one to check.

After fixing the fourth copy I swept the repository by MEANING rather than by
the quoted string, for all three corrected claims. That found three more live
occurrences of the write-site claim:

- `docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:1014`
- `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/kimi-reopen-r1-reply.md:77`
  and `sol-reopen-r2-brief.md:6`
- `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/reopened-debate-record.md:58-60`

I did NOT change any of them, and D24 now records why: every one was TRUE when
written, because the debate ran and the plan froze before Task 5 added the
seams; the plan is frozen and this ledger is its correction channel; and the
reviewer replies and the debate record are evidence, which must not be rewritten
to match a later state. The line I drew is between a dated record of a past
measurement and a present-tense claim about the code as it ships.

Judge that line. If you think any of those four artifacts states the claim in a
way a reader will take as current, say which and I will carry a correction into
it rather than editing it.

GATE RESULTS at `a1f0ddd`: all four fast tiers exit 0, and `pytest evals -q`
973 passed / 13 skipped / exit 0 on BOTH `powershell.exe` and `pwsh.exe`.

WHAT I AM ASKING.

- Does each of the five repairs close what it claims?
- Is any of them itself wider than its evidence? Three of five round-1 repairs
  were incomplete, so this remains the question that matters.
- Is the frozen-versus-evidence line above correct, and correctly drawn?
- Anything in `43e45ef..a1f0ddd` that regressed something already right.

Give one terminal verdict for `e94c0b5..a1f0ddd`.
