Verdict on plan revision e5a59e3: FIX. Six defects, four of which make a task's own "Expected: all PASS" step false as written, and one leaves a decision open that the lint will force the implementer to make.

## Claim 1: coverage of spec Parts 1 to 3, Error handling, Testing

- Gap A. Spec `docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md:452-454` requires every hook script to exit 0 with a printed note when Python is missing. The plan's hook commands are `pwsh ... -Command "$input | python tools/backlog-hooks/stop.py"` (`docs/superpowers/plans/2026-09-04-backlog-rewrite.md:2062`, `:2074`, `:2085`). With no `python` on PATH, pwsh reports CommandNotFound and exits non-zero; nothing in Task 5 or 6 handles it, and no test covers it (Task 5 tests cover only missing git, `:1764-1776`). The self-review claims "hook scripts exit 0 with notes" at `:2849`, which is true for git only.
- Gap B. Spec `:452-454` promises the missing-Python note; the plan's self-review `:2849` lists no gap. So the self-review statement "Error handling: ... hook scripts exit 0 with notes (Task 5)" is a listed non-gap that is a gap.
- Everything else in Parts 1 to 3 and Testing has a task: rules 1 to 12 (Tasks 1 to 3), five rule-7 fixtures (`:703-732`), `--revision` temp-repo test (`:1040-1060`), real-file test (`:2758-2759`), dual-host hook tests (`:1575-1577`, `:1984-1990`), pre-push merge/squash/ff, docs-only, README/CLAUDE, unrelated-byte (`:2238-2279`), tracked settings test (`:2014-2016`), CI tiers (`:2447-2466`), CLAUDE.md line (`:2480`), inventory and grep (`:2509-2559`), pointer (`:2730-2736`).

Verdict: FIX. Wrap the three hook commands in a `.ps1` invoked with `-File` (the shape `hooks/hooks.json:10` already uses) that checks `Get-Command python` and prints a note and exits 0 when absent, then pipes `$input` to the script; add one test per host with `PATH` stripped of python asserting exit 0 and the note. This same fix removes the Claim 4 hazard below.

## Claim 2: 1c digest byte-exactness and fixtures

- `canonical_bytes` at plan `:816-827` builds heading, header lines minus `Verified`, body, strips only `" \t"` (`:434-436`), pops trailing blanks, joins with LF, appends `\n` + `group:` + header text after `###` stripped both ends + `\n`, encodes UTF-8. CRLF folded at `:440`. This matches spec `:116-130` clause by clause.
- Fixtures: U+00A0 differs and space/tab does not (`:765-774`); `###   Name  ` yields `\ngroup:Name\n` (`:776-781`); CRLF equals LF (`:783-788`); trailing blanks dropped (`:790-796`).
- One reading gap, not a defect: the spec's CRLF fixture says "from a CRLF working copy and from `--revision`" (`spec:130`); the plan's fixture compares CRLF and LF text in memory. `read_at_revision` goes through `subprocess.run(..., text=True)` (`:1077-1078`), which already folds CRLF, so the two paths cannot diverge; the fixture proves the parser, not the transport.

Verdict: PASS.

## Claim 3: every test can fail, no assertion satisfied by stub or absence

- Defect C. `test_rule_1_wrong_order` (`:205-210`) swaps Status and Cost, then asserts `"order" in f`. The implementation hits `names[:1] != ["Status"]` and returns the message `first field must be Status` (`:505-508`), which contains no "order". Task 1 Step 5 "Expected: all PASS" (`:650-653`) is false.
- Defect D. `test_parse_reads_items_groups_and_fields` (`:163-169`) pins the literal `("Verified", "2026-09-04 000000000000")`. Task 2 Step 4 (`:880-883`) replaces every `000000000000` in `clean.md` with the real digest and never touches that assertion. Task 2 Step 5 "Expected: all PASS" (`:885-888`) is false.
- Defect E. Task 5's `seed_repo` (`:1589-1612`) commits no `.gitignore`. `stop.py` imports `_common` (`:1932`) and `load_lint` runs `exec_module` (`:1810-1815`), both of which write `__pycache__/*.pyc` under `tools/backlog-hooks/` and `evals/tools/` before `git ls-files --others --exclude-standard` runs (`:1959`). Those paths are governed (`:1447-1449`), so `test_docs_only_change_passes` (`:1740-1746`) returns 2, not 0. The real repo is protected only by `.gitignore:1`.
- Every other assertion I traced has a complementary positive or negative fixture; none is satisfied by the stub alone.

Verdict: FIX. (C) change the early-return message at `:506-507` to `fields out of order: first field must be Status`, or swap `Cost`/`Pairs` in the test. (D) Task 2 Step 4 must also rewrite the `:169` assertion to check the field name and `VERIFIED_RE`. (E) `seed_repo` writes and commits a `.gitignore` containing `__pycache__/` before the seed commit.

## Claim 4: hook contract and the `pwsh -Command "$input | python"` shape on both hosts

- The scripts match what the spec records: exit 2 with reason on stdout (`:1967-1970`), `stop_hook_active` honoured first (`:1942-1943`), SessionStart reads `session_id` and `cwd` (`:1877-1884`), matcher `Edit|Write` (`:2070`). Whether the spec's reading of the Claude Code docs is itself right is UNVERIFIED (external document).
- The test runs on both hosts (`:1575-1577`, `:1984-1990`, `:2468-2473`) but drives pwsh as an argv element (`:1620`), so it never passes through the shell layer Claude Code uses to run the command string at `:2085`. If that layer is a POSIX shell, `"$input | python ..."` inside double quotes expands `$input` to empty before pwsh sees it. `hooks/hooks.json:10` avoids this by using `-File`. How Claude Code invokes hook commands on Windows is UNVERIFIED; the point that stands is that the test proves the argv path, not the settings-file path, and the plan's own `test_settings_command_shape_matches_the_tests` (`:2031-2035`) only proves the two strings are equal.

Verdict: FIX, combined with Claim 1's fix: `-File` a wrapper script, and have `run_hook` build its command line from the settings file's command string so the test exercises what ships.

## Claim 5: pre-push clause

- Range `remote..local`, or `local` alone for a new remote branch (`:2362-2365`), matches spec 3c and 3d (`spec:397-398`, `:431-432`). Missing python refuses (`:2358-2361`), tested (`:2294-2300`). Attestation clause unchanged and non-blocking (`:2374-2383`). Header names the blocking clause, the governed list, README/CLAUDE as governed, the friction-free sentence rewritten (`:2323-2336`), which is what `spec:405-419` requires.

Verdict: PASS.

## Claim 6: Task 10 ranking, status table, pairs

- Defect F. Item 11 is PARTIAL (`:2682`, old file `:1811`) and appears in no ranking group (`:2610-2669`; groups hold 49 ids, the OPEN plus PARTIAL set holds 50). Rule 4 (`:575-580`) fails at Task 10 Step 6, and the plan gives the implementer no position. The old file also never ranked 11 (old `:90-377`), and spec 1d is silent on it, so this is a decision the plan must make.
- Status table agrees with the old file's own status block (old `:26-44`): 32 DONE, 16 GONE, 11/26/65 PARTIAL, 43 OPEN plus 47a/47b plus 80 to 82.
- 1d placements hold: 75 first with `none`; 49, 59, 67, 78 at entries 2 to 5 (`:2612-2615`); 68 in Fourth (`:2638`); 69 above 77 in Second (`:2623-2624`); 43 above 31 (`:2617-2618`); 73 in Fourth (`:2634`); 79 last (`:2669`); 71, 72 in Last (`:2667-2668`). Pairs table (`:2689-2709`) is symmetric and matches every 1d pairing including 76 with 38 (`spec:164-165`).

Verdict: FIX. Add `- 11` to a decided group. Recommendation: Last group, with a Cost line in the 71/72 form ("uncosted: ...", `spec:178-179`), since nobody has costed its remainder.

## Claim 7: names and signatures across tasks

- `check(..., rules=None, pointer_text=None)`, `lint_text`, `range_check`, `git_output`, `read_at_revision`, `reattested_items`, `is_governed`, `canonical_bytes`, `--repo-root`, `--pointer`, `--range`, `--digests` are defined before use and called with matching names (`:552`, `:1184`, `:1204`, `:1237`, `:1271`, `:1474`, `:1543`, `:1961-1966`).
- Minor: Task 1's interface text promises `Document.errors` (`:56`); the dataclass at `:421-425` has no such field and no task uses it.

Verdict: PASS (drop the `.errors` sentence at `:56` for accuracy).

## Claim 8: placeholders and undecided values

- Defect G. Task 9 Step 1 (`:2513-2517`) says the only tracked hits outside `rounds/` must be the probe plan's two lines, otherwise "stop to report it". The plan file itself carries `2026-07-27-0150-backlog.md:41` at `:2532`, so the grep run on the branch returns the plan as a third tracked hit and the step halts by its own rule. Also Task 9 Step 3 (`:2534-2535`) greps `0150-backlog\.md` and expects exactly two lines; the probe plan has five (`2026-08-03-home-skills-root-probe.md:78, 158, 288, 856, 975`), and line 158 carries `:577` and `:11-14` citations the `:[0-9]` pattern never sees.
- `<sha41>` and `<lastfull>` are read from git at the step that names them; not placeholders.
- Item 11's position (Claim 6) is the one decided-by-spec value left to the implementer (rule 4 decides it must exist; the plan decides nowhere).

Verdict: FIX. Step 1: exclude the plan file by name in the confirmation sentence, or grep with `:41\b`-free wording in the plan. Step 3: use the same `\.md:[0-9]` pattern and state the expected count from a run.

## Also found
- `xargs grep -n` at `:2513` without `-H` drops the filename if the last xargs batch holds one file.
- Task 7's `clone` fixture pushes the seed (`:2207`) with the hook active and without `PARALLAX_BACKLOG_TODAY`; it passes only while the machine date is at or after 2026-09-04.
- The workflow comment at `.github/workflows/skill-evals.yml:79-81` says hook tests are deliberately absent; Task 8 adds two without touching it.

## UNVERIFIED
- The Claude Code hooks documentation the spec cites (`spec:344-351`): whether exit 2 reads stdout or stderr, and how hook command strings are executed on Windows. No file in the repo records it.

## Verdicts
1. FIX (missing-Python exit-0 note for hook scripts; self-review lists it as covered)
2. PASS
3. FIX (C: rule 1 order message; D: Task 2 breaks the `:169` pin; E: seed repo lacks `.gitignore`, pycache reads as governed)
4. FIX (test proves argv path, not the settings command string; use `-File` wrapper)
5. PASS
6. FIX (item 11 unranked; rule 4 will refuse the file)
7. PASS
8. FIX (Task 9 Step 1 halts on the plan's own line 2532; Step 3 count is 5, not 2)

Plan as a whole, revision e5a59e3: FIX.
