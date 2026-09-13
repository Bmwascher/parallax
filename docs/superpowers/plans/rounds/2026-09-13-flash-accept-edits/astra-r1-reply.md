1. The complete dispatch fragment occupies one physical line at `agents/flash-implementer.md:88`. The no-flag controls, historical 1.1.7 limitation, command denial measurement, unmeasured new-file writes/deletes, and Windows log-path measurement match P1–P7 (`agents/flash-implementer.md:89-105`).

   Three assertions exceed those premises. “A drift in either direction” is not guaranteed to remove the mode line or deny an edit; expanded permissions could preserve both (`agents/flash-implementer.md:95-96`). “Command execution stays denied by design” promotes P2’s observed denial into a design guarantee (`agents/flash-implementer.md:97-99`). “It persists nothing” and “every tool call with its arguments” exceed P1(d)’s settings rewrite observation and P4’s file-action coverage (`agents/flash-implementer.md:100-102`). Limit these sentences to the measured behavior, explicitly acknowledge the settings rewrite, and describe the checks as detecting missing evidence or denied edits. **FIX.**

2. The prohibition explicitly covers `--dangerously-skip-permissions`, any approval-bypass flag, and persisted per-tool allow rules; the exception names only `--mode accept-edits`, followed immediately by the prohibition on other mode values (`agents/flash-implementer.md:138-143`). This is a specific lane-policy exception supported by the measured edit/command distinction. Its wording does not admit another flag or mode, and it makes no settings-immutability claim. **PASS.**

3. The rule is mechanically implementable: normalize both absolute paths, convert separators, compare case-insensitively, remove trailing separators, then require equality or the listed path followed by `/` as a prefix (`agents/flash-implementer.md:54-59`).

   Applied in that order, drive-letter case cannot reject a match; a listed trailing backslash becomes a removable trailing slash; UNC paths retain their leading `//`; and a sibling such as `C:/parent-other` cannot match `C:/parent`. A drive-root entry reduces to `C:` for comparison, whose descendant prefix is `C:/`. These follow directly from the specified comparison and require no policy judgment (`agents/flash-implementer.md:56-59`). No false acceptance or rejection arises in the requested cases. **PASS.**

4. Inputs assigns enforcement to the lane’s preflight, preflight 2 checks equality or ancestry, and the Lane note explains the same parent coverage (`agents/flash-implementer.md:39-45`, `agents/flash-implementer.md:54-63`, `agents/flash-implementer.md:166-172`). The remaining `allowNonWorkspaceAccess` mention records the measured values; it does not make the key a prerequisite (`agents/flash-implementer.md:43-45`). The three statements agree, and none describes either setting as granting the measured edit. **PASS.**

5. The new source line resolves P4’s specific ambiguity: the real UUID comes from `conversation=<uuid>, sending message`, and the empty startup field is explicitly rejected (`agents/flash-implementer.md:118-124`). The paragraph supplies no selection rule if a log contains multiple distinct conversation UUIDs; requiring exactly one distinct UUID associated with this dispatch would close that textual gap (`agents/flash-implementer.md:118-124`).

   The missing-mode-line inference is unsound. Absence establishes missing corroboration; it does not establish which permission mechanism allowed the edit. P4 supplies no such causal implication. Keep the blocking outcome, but replace “permitted by something other than the dispatch line” with “the requested mode is not corroborated by the log” (`agents/flash-implementer.md:114-117`). **FIX.**

6. Every listed positive phrase occurs on one physical line. The mappings below are to `agents/flash-implementer.md`; the assertions are in `evals/multi-model-verify/test_flash_implementer.py:50-60`, `evals/multi-model-verify/test_flash_implementer.py:85-98`, `evals/multi-model-verify/test_flash_implementer.py:121-137`, and `evals/multi-model-verify/test_flash_implementer.py:155-158`.

   | Pin | Agent line |
   |---|---:|
   | `--mode accept-edits` | 88, 89, 140 |
   | Complete model/mode/add-dir fragment | 88 |
   | `command execution stays denied` | 97, 142 |
   | `Windows spelling` | 56, 102 |
   | Applying-mode log line | 114 |
   | `Print mode: conversation=<uuid>` | 119 |
   | `conversationID=""` | 120 |
   | Listed-directory input | 39 |
   | Workspace or ancestor | 55 |
   | `agy itself does not consult it` | 41 |
   | `case-insensitive` | 57 |
   | `plus a separator` | 58 |
   | Named carve-out | 140 |
   | No other mode value | 143 |

   The coverage claim is nevertheless false. Added provisions without substantive pins include exclusive preflight enforcement, absolute-path normalization and trailing-separator removal, the interactive repair instruction, version boundaries and drift claims, the unmeasured-operation boundary, persistence/transcript assertions, missing-mode blocking, empty-ID rejection, and the Lane note’s parent-trust explanation (`agents/flash-implementer.md:40-42`, `agents/flash-implementer.md:56-62`, `agents/flash-implementer.md:89-105`, `agents/flash-implementer.md:115-124`, `agents/flash-implementer.md:166-172`).

   Plausible regressions also survive existing pins:

   - Deleting the Windows log-path instruction leaves “Windows spelling” in preflight (`evals/multi-model-verify/test_flash_implementer.py:60`; `agents/flash-implementer.md:56`, `agents/flash-implementer.md:102-105`).
   - Removing empty-ID rejection leaves both required log tokens (`evals/multi-model-verify/test_flash_implementer.py:96-98`; `agents/flash-implementer.md:119-122`).
   - Removing normalization or equality handling preserves “case-insensitive” and “plus a separator” (`evals/multi-model-verify/test_flash_implementer.py:135-136`; `agents/flash-implementer.md:56-59`).
   - Moving the dispatch fragment or carve-out into an obsolete example still satisfies whole-file substring checks (`evals/multi-model-verify/test_flash_implementer.py:55-56`, `evals/multi-model-verify/test_flash_implementer.py:155-158`).
   - Rewording or line-wrapping the old startup-ID parsing instruction defeats its exact absence pin (`evals/multi-model-verify/test_flash_implementer.py:98`).

   Pin the corrected operational sentences in their owning sections, preserving each raw-text phrase on one physical line. **FIX.**

7. Doctor correctly explains the missing-key preflight failure and treats the setting as informational (`commands/doctor.md:169-175`). Its measurement paragraph overstates P1–P3: there was no separate absent-key dispatch premise, no complete listed/unlisted × setting-value matrix, no no-flag control for every value, and no basis for “controls nothing the lane does” or a general next-run deletion guarantee (`commands/doctor.md:175-182`). Replace that paragraph with the actual initial settings, outcomes, and post-run removal observation.

   The missing-key verdicts themselves agree: “the Flash lane cannot write” can describe the consequence of its mandatory preflight. However, item 102 explicitly records a disagreement, and drift still reports the outside-workspace behavior as wholly “UNMEASURED,” while doctor describes its measurement (`tools/check-drift.ps1:359`, `tools/check-drift.ps1:645`, `tools/check-drift.ps1:656`; `BACKLOG.md:4471-4476`). Doctor explicitly says “two instruments that disagree about the same fact are worse than one instrument” (`commands/doctor.md:132-135`). My interpretation is that recording the disagreement does not satisfy that alignment requirement. Align the missing-key explanation and measurement wording on this branch. **FIX.**

8. Item 36 has the claimed OPEN status and shipping-version Cost line, and item 102 records the residual as OPEN (`BACKLOG.md:1189-1192`, `BACKLOG.md:4443-4446`). The substantive text needs these corrections:

   - The four-run account enumerates only three cases and conflates a listed directory with an unlisted worktree beneath a listed parent. Enumerate P1(a)–(d) separately (`BACKLOG.md:1206-1214`).
   - The absent key is correctly described initially as the file’s post-run state. Later, “agy then removed” introduces an edit-before-removal ordering that P1(d) does not establish. Say the run began with `false` and agy removed it during that run (`BACKLOG.md:1212-1214`, `BACKLOG.md:1226-1229`).
   - “Neither necessary nor a restriction,” “Nothing that false does not,” and “not a control of anything the lane does” exceed the measured in-place edits, especially beside the explicit unmeasured new-file/delete boundary (`BACKLOG.md:1216-1218`, `BACKLOG.md:1230-1235`).
   - The claim that removal is unreported and `true` is carried forward indefinitely is contradicted by the script. Parsed absence generates a removal note; carry-forward requires settings parsing to have failed (`BACKLOG.md:1237-1243`; `tools/check-drift.ps1:654-656`, `tools/check-drift.ps1:705-712`).
   - Item 102’s “writes wherever” should describe the demonstrated absence of trust-list enforcement for the measured edit. Its sentence initially saying both instruments “still describe” the old interpretation also needs updating to match its subsequent doctor-correction statement (`BACKLOG.md:4459-4463`, `BACKLOG.md:4471-4476`).

   The original 1.1.7 finding is explicitly historical, and the new-file/delete boundary matches P7 (`BACKLOG.md:1199-1204`, `BACKLOG.md:1234-1235`). **FIX.**

9. The three dated corrections are present at `docs/superpowers/specs/2026-07-25-flash-implementer-design.md:54-57`, `docs/superpowers/specs/2026-07-25-flash-implementer-design.md:74-75`, and `docs/superpowers/specs/2026-07-25-flash-implementer-design.md:244-246`. The sweep found no fourth assertion that accept-edits remains ineffective in print mode.

   Main-checkout-only wording survives in the historical spec’s dated 0.12.0 decisions and setup discussion (`docs/superpowers/specs/2026-07-25-flash-implementer-design.md:3`, `docs/superpowers/specs/2026-07-25-flash-implementer-design.md:102`, `docs/superpowers/specs/2026-07-25-flash-implementer-design.md:123-128`, `docs/superpowers/specs/2026-07-25-flash-implementer-design.md:259-260`). The live agent permits listed ancestors; README points to that agent, and the relevant skill reference says only “the checkout,” without a main-only restriction (`agents/flash-implementer.md:54-59`; `README.md:100`; `skills/multi-model-verify/references/model-prompting-notes.md:846-849`). **PASS.**

10. Beyond the new measurements already discussed, the agent retains these client-behavior statements:

   - Print-mode command auto-denial is explicitly dated 2026-07-25 and supplemented by the new 1.2.2 measurement (`agents/flash-implementer.md:82-83`, `agents/flash-implementer.md:97-99`).
   - stdin not reaching the model is explicitly dated 2026-07-25 (`agents/flash-implementer.md:84-85`).
   - The dispatch log carrying no file actions says only “probed,” leaving the behavior as a standing property. The spec identifies its historical measurement date (`agents/flash-implementer.md:125`; `docs/superpowers/specs/2026-07-25-flash-implementer-design.md:65-71`).
   - Trust being “per-directory and interactive-only” reads as a standing client property. The following September measurement qualifies trust-list enforcement, not this separate assertion about how trust can be granted (`agents/flash-implementer.md:166-172`).

   Add explicit measurement boundaries to the last two assertions; their present-day validity is not established by the supplied premises. **FIX.**

UNVERIFIED:

- Claim 8’s supplementary observations about exactly two trust entries, no trust log line, and no trust flag in `--help` are outside P1–P7; their underlying evidence was unavailable in the reviewed files (`BACKLOG.md:4453-4459`).
- Claim 9’s corrections assert flag-enabled success on **1.2.0**. P3 establishes only its no-flag failure; flag-enabled success on that version remains unverified (`docs/superpowers/specs/2026-07-25-flash-implementer-design.md:55`, `docs/superpowers/specs/2026-07-25-flash-implementer-design.md:75`, `docs/superpowers/specs/2026-07-25-flash-implementer-design.md:246`).

File-instruction effects: none caused a pause, refusal, or change of task.