# Mirror pathname capture: switch to `-z`

Backlog item 14. Design approved 2026-07-29.

## The problem

`tools/new-review-mirror.ps1` is a security control. It enumerates
instruction back-channels inside a copied tree, DELETES them, records a
baseline of every untracked and ignored file, and hashes each one into a
manifest that proves nothing was silently dropped. Every pathname it
handles names a file it deletes or hashes. A wrong pathname is not a
display bug.

Both pathname captures — `git ls-files` and `git status --porcelain` —
read git's line-oriented output. Git C-style-quotes a pathname whenever
quoting would change it, and the trigger set is WIDER than the escape
characters alone: a plain SPACE is enough.

Measured 2026-07-29 in a throwaway repo, a directory named `M+ Timer`
comes back from `git status --porcelain` as `?? "M+ Timer/"`, quoted for
the space alone. `core.quotepath=false`, which the script already sets,
does NOT suppress it. Measured by another session against a real tree,
5810 of 11874 baseline entries came back quoted, nearly all for a space.

Until commit 57ba3f1 the script treated any quoted pathname as
unresolvable and STOPPED, so the whole preflight-3 remediation path was
unusable in any repo using a `References/<name with spaces>/`
convention — the convention it was built for.

Commit 57ba3f1 replaced the stop with a hand-written C-style unquoter.
That decoder has two fail-open defects, both reproduced on Windows
PowerShell 5.1 and on `pwsh` 7 by calling `Resolve-GitPathname` directly:

1. `"caf\303\251/input.txt"` returns a string of character codes
   195,169 — two characters — not 233, the single character the real
   filename holds. Git's octal escapes name BYTES of the UTF-8 encoding;
   the decoder appends each byte as its own character. The result is a
   pathname that silently does not match the file on disk.
2. PowerShell `switch` is case-INSENSITIVE by default, so `"a\Tb.txt"`
   decodes to a tab and `"a\Nb.txt"` decodes to a newline. C-style
   quoting leaves uppercase escapes undefined; both must refuse.

Both return a confident wrong pathname instead of refusing, which is a
worse failure than the blanket stop they replaced, because the stop was
loud. The suite is also red at that commit:
`test_a_quoted_baseline_entry_stops_instead_of_being_unquoted` still
asserts the old error wording.

## The decision

Switch both captures to `-z`, and delete the decoder outright.

Under `-z` git emits each pathname verbatim and NUL-terminated, and never
quotes. There is no escape grammar to specify, so the two decoder defects
cease to exist rather than being fixed.

This was chosen over fixing the decoder. Fixing it would leave a
hand-written unquoter on the highest-consequence path in the tool, and
the two defects found are the kind that recur: one was a byte-versus-
character confusion, the other was PowerShell's `switch` being
case-insensitive by default. The cross-vendor reviewer lane reached the
same decision independently and added a third defect in the same family:
the rename parser searches for the first literal ` -> ` without
understanding quoting.

## Two measurements that shape the design

### The rename field order is INVERTED under `-z`

Measured 2026-07-29 against a real git, staging a rename of
`M+ Timer/old name.lua` to `M+ Timer/new name.lua`:

```
line form:  R  "M+ Timer/old name.lua" -> "M+ Timer/new name.lua"
-z form:    R  M+ Timer/new name.lua \0 M+ Timer/old name.lua \0
```

The line form reads SOURCE then DESTINATION. The `-z` form reads
DESTINATION then SOURCE. A port that carries the old field order across
would hash and delete the wrong file, silently. This is the single most
dangerous part of the change and the reason the parse is specified
structurally below rather than by example.

Both captures end with a trailing NUL, so requiring one is a valid
fail-closed check rather than an assumption.

### Most of git's quoting cannot occur on Windows

This script is Windows-only. Measured 2026-07-29, of every character
that makes git quote a pathname, Windows permits these in a real
filename:

| trigger | Windows | git line form |
|---|---|---|
| space | CREATED | quoted |
| non-ASCII (e-acute) | CREATED | raw under `core.quotepath=false` |
| **0x7F (DEL)** | **CREATED** | **quoted, escaped `\177`** |
| `"` | REFUSED | quoted |
| `\` | REFUSED | quoted |
| `>` | REFUSED | not a trigger |
| tab, newline, CR, bell, backspace, form feed, vertical tab | REFUSED | quoted |

**The set above is EXHAUSTIVE over ASCII, by sweep rather than by
argument.** Measured 2026-07-29: a file `x<c>y.txt` was created for every
code 1 to 127 except the path separator. Windows accepted 87 of them, and
`git -c core.quotepath=false status --porcelain` quoted exactly TWO: the
space and 0x7F. The other 59 distinct entries came back bare. (87 creatable
against 61 distinct entries is the case-insensitive filesystem folding the
26 lowercase letters onto their uppercase twins; neither case is a
trigger.) This is what licenses the render's one-condition rule: the space
is the only trigger the render must reproduce, and 0x7F is the only other
one, which the guard refuses. Non-ASCII is outside the sweep and is
handled by the `core.quotepath=false` reasoning above, not by it.

**0x7F is the row that matters and it was missing from the first draft.**
It was found by the backup reviewer lane in plan debate round 2 and
settled by measurement: Windows creates `a<0x7F>b.txt`, and
`git status --porcelain` prints `?? "a\177b.txt"` with AND without
`core.quotepath=false`, while `-z` returns the byte raw. It sits above the
control range, so a "below 32" test admits it. Any argument of the form
"the guard has refused every quoting trigger except the space" is false
unless 0x7F is refused explicitly.

Three consequences, each load-bearing:

1. The nine NAMED escapes the decoder implements (`\a \b \f \n \r \t \v
   \\ \"`) all name characters Windows refuses, so those branches cannot
   be reached by a name this script reads from disk.

   The OCTAL branch is a different matter, and the first draft of this
   spec got it wrong by lumping the two together. 0x7F is creatable on
   Windows and git escapes it as `\177`, so the octal branch WAS
   reachable. What that reachable input would have produced is worth
   stating exactly rather than glossing: `\177` is a single byte below
   128, so the byte-versus-character defect does not manifest for it and
   the decoder decoded it correctly. The two measured defects sat on
   input that could not arrive; the input that could arrive, it happened
   to get right.

   This narrows an earlier claim in this document and does not change the
   decision. The case for `-z` never rested on the decoder being dead
   code. It rests on removing a hand-written grammar from the path that
   names files this script deletes and hashes, and on the space case,
   which is common rather than pathological. If anything the 0x7F
   discovery strengthens it: a guard plus a one-condition render is small
   enough to reason about completely, and the decoder was not.
2. A `-z` pathname can never contain a NUL or a newline, so splitting on
   NUL is exact and the recorded evidence can stay one entry per line.
   No new ASCII-safe encoding is needed for the baseline.
3. ` -> ` cannot appear inside a Windows filename, because `>` is
   refused by the OS. The reviewer's third finding is real as a contract
   violation and is NOT reachable from a real file. Recorded as such
   rather than claimed as a fix. The guard refuses `>` anyway, because git
   reads names from its INDEX rather than from disk and the render depends
   on the property holding.

## Architecture

One responsibility per part. The defect class this cycle is removing came
from a single function that located, parsed and proved at once.

### Capture

Runs git, reads its standard output as RAW BYTES, requires the output to
end with a NUL, splits on NUL, and strict-decodes each field as UTF-8.
Returns the fields. Knows nothing about status codes.

Raw bytes, not PowerShell's decoded string. PowerShell 5.1 decodes a
native command's output using the console code page; the current script
works around that by forcing `[Console]::OutputEncoding` to UTF-8. That
workaround decodes a malformed byte to a replacement character SILENTLY,
which is a fail-open on the pathname boundary. Reading bytes and decoding
with `UTF8Encoding($false, $true)` throws on a malformed byte instead.

The empty field after the final NUL is discarded. An empty field anywhere
else is a stop.

### Guard

`Test-SupportedPathname` decides whether this tool can handle a pathname
EXACTLY, in both senses: can it name a file the script can delete and
hash, and can the render below record it in the porcelain line form the
baseline contract already uses.

It admits an ordinary pathname, or one whose ONLY line-form quoting
trigger is a SPACE, which is the single trigger the render reproduces. It
refuses an empty field, every control character, 0x7F, `"`, `\` and `>`.
Non-ASCII is admitted, because the recorded form used
`core.quotepath=false` and is therefore raw.

Three of those refusals carry their own reason beyond the table above.
A backslash is a path SEPARATOR on Windows, so a field carrying one would
make `Join-Path` resolve a different file, which the script would then
delete or hash under the name the baseline gave. `>` is what keeps the
render unambiguous: the ` -> ` separator is only safe while no pathname
can contain `>`. And 0x7F is legal on disk yet is a quoting trigger the
render cannot reproduce, so admitting it would put a bare name into a
baseline that the direct capture quotes.

Refusing that residue rather than rendering it is deliberate. Git records
it with its own C-style encoder: NAMED escapes for tab, newline, `"` and
`\`, and OCTAL for the rest, including the one reachable case, 0x7F as
`\177`. Reproducing any of that would mean writing back the encoder this
cycle exists to delete. A loud stop on a pathological name is the cheaper
failure.

Amended twice on 2026-07-29 during the plan debate: first because `>` was
argued for and not enforced, then because the guard was named for Windows
legality while deciding something else, and 0x7F fell through the gap
between the two.

**What the guard does NOT claim.** It is not a Windows name validator. It
does not check for reserved device names, trailing dots or spaces, length
limits, or the other characters Windows refuses. Two grounds are all it
decides: a name the script could resolve to the wrong file, and a name the
render cannot reproduce. A syntactically fine name with no file behind it
is caught downstream, where `Get-ContentManifest` already stops on
"baseline path has no file behind it". Stating the narrow contract is the
point: the first two drafts of this guard each advertised more than the
code did, and both times a reviewer found the gap.

The guard exists because deleting the old blanket refusal with nothing in
its place would remove a safety property, not just noise. It fires on two
kinds of input, not one: a name that cannot be resolved without guessing,
and a name that is perfectly resolvable but cannot be recorded exactly.
0x7F is the second kind, which is why "the guard can only fire on an
impossible path" - the wording of an earlier draft - was false.

### Parse

Applies to the STATUS capture only. `ls-files -z` fields are bare
pathnames and go straight from Guard to the caller.

Consumes status fields into records: `@{X; Y; Path; Source}`. Each field
is `XY`, one space, then the pathname, so a field shorter than four
characters is a stop. A record whose `X` or `Y` is `R` or `C` consumes
the NEXT field as `Source`; a missing second field is a stop. Knows
nothing about text.

The existing disposition rules are unchanged and move here intact:

- Deletion-only entries (` D` / `D `) are OMITTED. HEAD plus the
  baseline already bind the absence.
- Rename and copy entries hash the CURRENT DESTINATION.
- An `RD` destination no longer exists and is a stop, never a silent
  omission.

### Render

Prints each record in git's familiar display form, `R  old -> new`,
INCLUDING git's quoting, for the evidence record. This keeps the recorded
baseline byte-comparable with a capture taken by running THE STATUS
COMMAND directly, which is what `references/backup-lane.md` requires of
every round.

The quoting is not cosmetic. Run 2026-07-29 against the current script, a
spaced untracked file records as `?? "M+ Timer/input.txt"`. A bare render
would make every space-bearing path read as a change on every round.
Measured in the same session: git quotes each side of a rename
INDEPENDENTLY, printing `R  "with space/a.lua" -> plain/a.lua` for a
spaced source with a plain destination and the mirror image for the
reverse. Once the guard has refused `"`, `\` and the control characters, a
SPACE is the only remaining trigger, so the rule is one condition.
Non-ASCII is deliberately NOT quoted: the old captures set
`core.quotepath=false` and recorded an accented pathname raw, and this
render keeps that shape.

The MANIFEST is unaffected and stays unquoted. Confirmed in the same run,
which printed `M+ Timer/input.txt <sha256>`.

The render is unambiguous because the guard refuses `>`.

Rendering is one-way. Manifest subjects come from the RECORDS, never from
the rendered text. Nothing re-parses what this step prints.

Amended 2026-07-29 after the plan debate; the first draft rendered every
pathname bare.

## What is deleted

- `Test-GitQuotedPath`, `ConvertFrom-GitQuotedPath`, `Resolve-GitPathname`.
- The ` -> ` text search in `Get-ManifestSubject`.
- The quoted-entry check in the main flow (currently line 379), which is
  unreachable once entries are decoded upstream and carries a message
  that no longer describes anything.
- `-c core.quotepath=false` on both captures. Measured 2026-07-29: with
  `-z`, `git ls-files` returned raw UTF-8 bytes with the flag ABSENT. The
  flag governs the display form, and `-z` has no display form. Keeping a
  flag that does nothing invites a later reader to treat it as
  load-bearing. Its comment block is replaced, not merely deleted, so the
  reason the encoding matters is not lost.

## Error handling

Every one of these stops the run and names itself. None may be reported
as a clean result.

- git exits non-zero
- output does not end with a NUL
- a byte is not valid UTF-8
- a required field is empty
- a rename or copy record has no second field
- a pathname fails the supported-pathname guard
- a status field is shorter than the four characters `XY` plus a space
  plus at least one pathname character
- an `RD` destination no longer exists

## Testing

`evals/multi-model-verify/test_review_mirror.py` is the suite. It is
Windows-only (`os.name == "nt"`) and CI is Linux, so CI does not run it.
Backlog item 10 holds that gap; this cycle does not close it.

**Run the whole suite once under EACH PowerShell host**, not only the new
cases. The current selector prefers whichever host it finds first, and
0.16.1 shipped a lock that passed on Windows PowerShell and did not lock
on `pwsh`.

New coverage:

- A path with a space, as untracked and as ignored baseline material:
  exact hash and evidence round-trip.
- `M+ Timer/AGENTS.md` as a back-channel, tracked and untracked:
  deletion, staging, and clean re-enumeration.
- A non-ASCII path on both hosts.
- A rename where BOTH names contain spaces, asserting destination and
  source land in the right fields. This is the inverted-order case.
- A rename or copy record with a missing second field.
- Missing trailing NUL, invalid UTF-8, empty output, an empty pathname
  field.
- Deletion-only, `RD`, and `R`/`C` in either status column.
- Escape-looking text such as `caf\303\251`, `a\Tb.txt` and `a\Nb.txt`
  arriving as literal field content: preserved exactly, never
  interpreted.
- Manifest assertions with a space in the path. The existing assertions
  split each line at the FIRST space and would misread such an entry;
  they must split from the trailing digest instead.

`test_a_quoted_baseline_entry_stops_instead_of_being_unquoted` is
REPLACED by the space, rename-order and malformed-capture cases, not
deleted.

## Out of scope

- Making the script cross-platform.
- Closing the Linux CI gap (backlog item 10).
- The reviewer tool-surface gap (backlog item 7).
- Any change to the manifest, the baseline's meaning, or the
  back-channel deletion rules.
