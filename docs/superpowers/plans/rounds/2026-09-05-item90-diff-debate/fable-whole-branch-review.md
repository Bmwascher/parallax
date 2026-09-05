# Fable whole-branch review, range eddacb668388f19657003e0d184edaf488240f52..34de1559073c51436df0400d7bf11e7869fdfc96

Dispatched 2026-09-05 as `parallax:fable-reviewer` (model alias `fable`, read-only tool grant) with the frozen plan, the SDD ledger and the controller-built diff package `review-eddacb6..34de155.diff`. Raw reply follows verbatim.

---

### Strengths

- The protection guards run before the first destructive act. `Test-PathOrAncestorIsLink`, the followed-target alias refusal and the target-overlap refusal sit at `C:\Users\Brandon\Documents\parallax\tools\new-review-mirror.ps1:1203-1270`, and the first `Remove-Item` is at line 1278. Every refusal is exit 2 with the reason on stdout, and the tests assert the target file's bytes survive (`test_review_mirror.py` diff lines 3006, 3025, 3044, 3076).
- The re-link is verified by reading the junction back and comparing its resolved target to the recorded one (`new-review-mirror.ps1:1586-1615`); a junction that points anywhere else is a BLOCKED exit 1, so the record's `links:` block cannot disagree with what the mirror holds.
- Writers after the re-link were checked one by one: `git rev-parse` (1649), `Get-BaselineRaw` (1655), the manifest (1675), the probe (1696) and the record print. None deletes, copies or commits. The mirror's own `.git/index` refresh is the only write and the walk refuses a `.git` that is a link (diff 3409-3415), so no path resolves through a junction. The remediation commit (1460-1466), the `-ExtraInput` copy (1527) and the remediation `Remove-Item` calls (1405, 1414) all precede the re-link block.
- `Get-FilesBeneath` (diff 3201-3280) cannot miss a nested link, because it starts a fresh listing at every reparse-point directory found beneath the start, and a double listing is harmless because `Get-ContentManifest` deduplicates with `Sort-Object -Unique` before hashing (`new-review-mirror.ps1:594-595`). The visited set is seeded with the repo root (577) and the depth bound closes the relative-link case the visited set cannot.
- Contract prose matches the pin word for word. I compared the test literal (diff 2550-2565) against the Markdown (diff 3132-3145): identical text, whitespace differs only inside `_norm`'s tolerance.
- 5.1 compatibility holds for every new construct I could check: hashtable stack frames, typed `catch` clauses, `New-Item -ItemType Junction`, `String.Equals(string, "OrdinalIgnoreCase")`, and the `.Target` collection-versus-string handling copied from the existing walk. Nothing uses a 7-only overload.
- The timing measurement (spec diff 2471-2492) is bound to an oracle (per-link name-and-hash equality, empty listings refused), not a file count, and the numbers made it into item 90 (diff 107-109).

### Issues

#### Critical

None.

#### Important

None.

#### Minor

- `C:\Users\Brandon\Documents\parallax\skills\multi-model-verify\references\backup-lane.md` (diff 3134-3137): "After the last writer into the mirror" is slightly stronger than the code. `Get-BaselineRaw` at `new-review-mirror.ps1:1655` runs `git status` in the mirror after the re-link, and git's optional index refresh writes the mirror's own `.git/index`. The plan's Global Constraints (line 19) acknowledge this writer; the contract sentence does not. Not a write through a link, so a prose precision point only.
- `new-review-mirror.ps1` diff 3437-3440 and 1586: a source link whose target lies INSIDE the source repo (for example `repo/j -> repo/real`) is now re-created as a junction onto the live source tree, where the old copy snapshotted its bytes. The identity gate still catches an edit there, but the reviewer reads live source through that path during a round. Neither the spec nor the contract region names this case. Worth one sentence in the region or the spec.
- `new-review-mirror.ps1` diff 3216-3219: the refusal text says "more than 16 directory links deep" while the count that triggers it is the seventeenth nested link below the subject link, so the chain that is refused is 18 links long including the subject. The test at diff 2960-2987 locks the behaviour; only the message wording is loose.
- Ledger line 32: the `test_review_mirror.py` module runs in 18m42s under PowerShell 7 against 94s under 5.1. The `powershell-hosts` CI job runs the module under both hosts, so this is a real CI cost. No cause was measured. Not a correctness issue.
- Gap, not a finding: ledger line 44 records the 5.1 and 7 full-suite gates as dispatched at 34de155 but not their results. The package shows 2879 passed on pwsh at Task 4 (ledger line 40) and the module green on 5.1 at Task 3 (line 32); the whole-suite 5.1 result at HEAD is what the debate should ask for.

### Ledger minors triage

- `$item` reused in the walk (ledger line 35): ride. The popped frame is consumed into `$dir` and `$underLink` at diff 3354-3356 before `Get-Item` overwrites it at line 1090, so no value is lost; a rename is cosmetic.
- Vanished-target, edit-behind-link and nested-drift cases green before the code change (line 36): ride. They lock behaviour the branch depends on and the ledger records their status honestly; the sixteen other cases were red first.
- pwsh 12x slowdown attributed to the second recursive enumeration (line 37): ride, but file a backlog item with the measured number, because the attribution is a guess and the cost lands on every CI run.
- Parked Important, files behind a link escape the path budget (line 34): ride as a follow-up, do not fix before merge. On 5.1 an over-long mirror-side path through the junction terminates `Get-ChildItem -ErrorAction Stop` inside `Get-FilesBeneath` (diff 3258-3263) and surfaces as `BLOCKED` exit 1 at `new-review-mirror.ps1:1677`; on 7 long paths enumerate. Neither host can read clean without a measurement, and the frozen spec and the pinned region both define the budget universe as what the copy creates. The cost is an error message that says "could not be enumerated" instead of "build the mirror at a shorter path", which is a backlog item, not a merge blocker.

### Assessment

Ready to merge: Yes

The range delivers what the frozen plan specifies with every failure path loud, the destructive guards ahead of the first delete, and nineteen cases that lock the behaviour on real junctions; the four minors are prose precision and cost, and the one gap is a missing gate result the debate can ask the session to supply.
