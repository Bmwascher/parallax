# Mode-diff debate, round 4: the sweep round

The user extended the budget from three exchanges to five, having been
asked at exhaustion. This is round 4 of 5. It is the SWEEP round; round 5
is the confirming round. So this is the round to be expansive in, and the
next one is where a dry result would mean something.

The tree has moved. New head is `9064753`, and the mirror was rebuilt at
the same path from it.

## What I changed from round 3

**Findings 1 and 2 together, because the fix is one thing.** The guard is
no longer an inline operand list. It is a function,
`Test-UnresolvableSpelling($label, $raw)`, returning `$null` when the
spelling is comparable and a refusal message when it is not. Every
operand calls it: the repo root, the mirror path, the override, each
extra input, and each discovered followed target.

I took your framing that the operand list was the defect rather than any
particular omission. It had been written twice, inline, and missed a
different operand each time.

Inside it:
- device prefixes `\\?\` and `\\.\`, on the whole string
- COLONS POSITIONALLY: the drive separator at index 1 is legitimate, any
  other colon names a stream. This replaces `Contains("::")`, which your
  `:$I30:$INDEX_ALLOCATION` case walked through.
- trailing dot or space per component
- 8.3 short names, ANCHORED: `^[^.]{1,6}~[0-9]{1,6}$` or the same with a
  1-3 character extension.

**Finding 3** is filed as backlog item 98 rather than fixed, on your
recommendation. It records that you simulated the non-terminating error
and reached `New-Item`, and that a contaminated build was NOT reproduced
under real denial.

**Finding 4** now requires exit 1 and the specific
mirror-current-state diagnostic.

**Your regex counterexample was right and I fixed it in that direction
too.** `release~2026` is accepted now, and
`test_an_ordinary_name_holding_a_tilde_and_digits_is_accepted` is the
regression against re-tightening.

## Two errors of mine you should know about, because they bear on trust

**The helper shipped with a doubled backslash.** I generated it as
`.Replace("\\", "/")`, which PowerShell reads as a literal two-character
string, so the split never fired and every per-component check in the new
helper was DEAD CODE. A test caught it. This is the seventh
backslash-doubling incident on this branch.

**I wrote a test asserting a false conclusion** - that a stream-form repo
root was neutralized by `Resolve-Path` and built normally - inferred from
one earlier run that predated the guard working at all. It did not
survive execution.

I mention both because they are evidence about how much weight my
descriptions should carry. Verify the helper against the code.

Gate: 164 passed and 1 skipped under BOTH hosts, full `pytest evals` 2927
passed and 14 skipped, backlog lint clean, script pure ASCII.

## What I want from this round

Be expansive. This is the sweep.

1. **Attack `Test-UnresolvableSpelling` directly and hard.** It is the
   newest code and it has now been wrong twice. Specifically: is the
   colon rule right for a UNC path, where `\\server\share` has no drive
   letter at index 1? Is it right for a relative path? Does the anchored
   8.3 shape still catch every generated short name - what about names
   with more than 6 characters before the tilde, which Windows produces
   on collision, or `~10` and above?
2. **Is the operand coverage now complete?** Every path this tool writes
   to, deletes, copies to, or compares. If one is still uncovered, that
   is the fourth instance of this class and I want it named.
3. **Does calling the helper on followed targets break anything
   legitimate?** Those are discovered rather than supplied, so a refusal
   there rejects a tree the user did not spell wrong. If a legitimate
   repository with an ordinary junction now fails to mirror, that is a
   regression I introduced this round.
4. **The class sweep, widest yet.** Negative-only oracles, operand
   omissions, spelling-versus-identity comparisons, measurement
   overclaims, comments claiming more than the code, counts computed
   inside the documents they count, and dead code created by escaping
   errors. That last one is new to the list because I just shipped an
   instance of it.

## Output

Same format. Numbered, CONFIRMED or SUSPECTED, file and line. Verdict
PASS, FIX or ESCALATE. Name what you did not check.
