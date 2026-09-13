# Diff package: 2772e4e7fcbff2a45e15005b32eec9b0e8db513e..2ff9e5f5ea901501ecdd5b3414717b848ed86829 (branch flash-accept-edits)

## Commits
2ff9e5f5ea901501ecdd5b3414717b848ed86829 adopt agy accept-edits mode in the flash implementer lane, accept a trusted ancestor in preflight 2, and parse the conversation id from the line that carries it

## Stat
 BACKLOG.md                                         | 36 +++++++++++----
 agents/flash-implementer.md                        | 53 ++++++++++++++++------
 commands/doctor.md                                 |  6 ++-
 evals/multi-model-verify/test_flash_implementer.py | 42 +++++++++++++++--
 tools/check-drift.ps1                              |  2 +-
 5 files changed, 112 insertions(+), 27 deletions(-)

## Diff (10 lines of context)
```diff
diff --git a/BACKLOG.md b/BACKLOG.md
index 3e8f26b..46c288c 100644
--- a/BACKLOG.md
+++ b/BACKLOG.md
@@ -1182,52 +1182,70 @@ written as a footnote to a parameter after it.
 
 **Constraint that must survive any fix.** A round whose reply cannot be
 bound must stay a transport failure with the reply discarded unread. No
 fix may add a path where a late or reconstructed inventory reads as a
 timely one.
 
 ## 36. agy `allowNonWorkspaceAccess` is watched but UNMEASURED
 Status: OPEN
 Cost: the basis for a setting the lane has carried for four releases is missing, and whether the question survives depends on what item 45 decides about the agy lane
 Pairs: none
-Verified: 2026-09-04 29053f8f5802
+Verified: 2026-09-13 ac70b76d5fee
 
 Opened by 0.24.0, which deliberately did not answer it. Item 11's security
 contract stays partially open on this point while the rest of item 11
 closes.
 
 **What IS measured, and its boundary.** The 0.12.0 build set the value to
 `false`, watched a trusted-workspace print-mode write get soft-denied,
 restored `true`, and recorded "allowNonWorkspaceAccess=true required for
 print-mode writes as of agy 1.1.7"
 (`docs/superpowers/plans/2026-07-25-flash-implementer.md:590-603`). That is
-a real measurement, and it is BOUND TO AGY 1.1.7. The lane now runs 1.1.12.
+a real measurement, and it is BOUND TO AGY 1.1.7. The lane now runs 1.2.2.
+
+**Measured 2026-09-13 on agy 1.2.2, and it moves the ground under
+question 1.** With `true` set, unchanged, print mode soft-denied a
+trusted-workspace edit (`ReplaceFileContent`) until the dispatch line
+carried `--mode accept-edits`, and under that flag the edit landed while
+a `run_command` call was still auto-denied. So on 1.2.2 `true` is NOT
+SUFFICIENT for the lane's writes; the flag is. Whether `true` is still
+NECESSARY alongside the flag is the open half of question 1, and one
+run with `false` plus `--mode accept-edits` settles it. Record:
+`C:/Users/Brandon/Documents/KitnDev/KitnEssentials/dev/docs/handoffs/agy-accept-edits-probe-2026-09-13.md`
+(outside this repo). The flag itself shipped into
+`agents/flash-implementer.md` on the same day; that is a lane contract
+change and does not close this item.
 
 **The residual is TWO questions, not one.** An earlier draft of this item
 named only the second, and in naming only it quietly promoted a
 version-bounded measurement into a present-tense requirement:
 
 1. Does `false` STILL soft-deny the lane's intended trusted-workspace
-   writes on 1.1.12? The 1.1.7 result does not answer it. If it no longer
-   denies, `true` is not required and the setting can simply go.
-2. What does `true` permit OUTSIDE the workspace, on 1.1.12?
+   writes when the dispatch line carries `--mode accept-edits`? The 1.1.7
+   result does not answer it, and the 1.2.2 measurement ran with `true`
+   only. If it no longer denies, `true` is not required and the setting
+   can simply go.
+2. What does `true` permit OUTSIDE the workspace, on the current version?
+   Also unmeasured under `--mode accept-edits`: whether the flag permits
+   NEW files and deletes, not only in-place edits (the 1.2.2 run was one
+   in-place edit).
 
 **What 0.24.0 did instead.** `tools/check-drift.ps1` now RECORDS the value
 in the snapshot and reports a change to it as a drift note that names this
 item. Recording a value answers neither question and must never be
 presented as closing them: a watched setting is not an understood one.
 
 **Shape of a fix, not decided.** Re-run the 1.1.7 experiment on the
-current version for question 1. Question 2 needs a positive probe - a
-write attempt at a path outside every trusted workspace - and its result
-is a security finding either way, so the probe design belongs in a plan
-rather than in an ad-hoc run.
+current version with the flag on the dispatch line, for question 1.
+Question 2 needs a positive probe - a write attempt at a path outside
+every trusted workspace - and its result is a security finding either
+way, so the probe design belongs in a plan rather than in an ad-hoc run.
 
 Nothing is known to be broken; what is missing is the basis for a setting
 the lane has carried for four releases. Whether this survives at all depends
 on what item 45 decides about the agy lane, so do not build it before that
 is settled.
 
 ## 37. No documented step REQUIRES promoting an adjudicated rule
 Status: OPEN
 Cost: it breaks nothing and silently discards rules the repo has already paid for
 Pairs: none
diff --git a/agents/flash-implementer.md b/agents/flash-implementer.md
index 4a61b84..eb12edc 100644
--- a/agents/flash-implementer.md
+++ b/agents/flash-implementer.md
@@ -29,35 +29,38 @@ never-write rule, and it never survives to the evidence checks.
   path the task names, STOP and report the gap. Never invent or guess the
   missing piece.
 - Run the task's verification commands yourself and read the output. Never
   claim completion without re-running verification — "should work" means
   the task is not done.
 <!-- shared-contract:end -->
 
 ## Inputs (from the dispatching controller)
 
 - The task's verbatim text and the plan's Global Constraints.
-- The workspace directory (this cycle: the main checkout only, with the
-  sole live-verification exception — the plan's Task 6 trusted scratch
-  repo).
+- The workspace directory: any directory listed in `trustedWorkspaces`,
+  or under one - a listed parent covers its child worktrees (measured
+  2026-09-13 on agy 1.2.2: with only the worktrees parent listed, an edit
+  landed in an unlisted worktree beneath it). Preflight 2 is the
+  mechanical gate.
 - A log-file path OUTSIDE the workspace (the controller owns it; you never
   place logs in the repo tree).
 
 ## Preflight (all five must pass BEFORE dispatch)
 
 1. `agy models` (binary at `$LOCALAPPDATA/agy/bin/agy.exe`) — output must
    contain `gemini-3.8-flash-high`. Anything else (missing binary,
    sign-out, missing model) is blocked.
 2. `~/.gemini/antigravity-cli/settings.json` — `trustedWorkspaces` must
-   contain the workspace directory. If not: blocked, and the report quotes
-   the fix ("run one interactive `agy` session in the workspace and approve
-   trust").
+   contain the workspace directory or an ancestor of it, compared as
+   normalized absolute paths. If not: blocked, and the report quotes the
+   fix ("run one interactive `agy` session in the workspace, or in the
+   parent directory that holds the worktrees, and approve trust").
 3. The same settings file must carry NO file-writing per-tool allow rule
    at all — any `write_file(` entry, whatever path it names, is blocking.
    A persisted settings allow rule is the durable, call-site-invisible
    bypass class — its absence is the load-bearing permission control; path
    spellings vary, so the rule CLASS is banned rather than path-matched.
    If present: blocked, quoting the rule.
 4. `git status --porcelain` in the workspace must be EMPTY. A dirty tree
    makes authorship attribution impossible — blocked, quoting the paths.
 5. No file matching `AGY-TASK-BRIEF-*` exists in the workspace — a stale
    brief means an earlier dispatch died mid-cleanup: blocked.
@@ -68,48 +71,71 @@ never-write rule, and it never survives to the evidence checks.
    heredoc — `<unique>` is the dispatch log file's basename, so briefs
    never collide. Content: the task's verbatim text, the Global
    Constraints, the exact files list, and this exact closing line:
    `Do not run commands or attempt verification - the wrapper runs all verification after you finish; your only job is the file edits.`
    (Print mode auto-denies command execution, so a verification attempt
    by Flash soft-denies and blocks the run — live-verified 2026-07-25.
    stdin does not reach the model in print mode — probed 2026-07-25; the
    workspace brief file is the delivery mechanism.) This file is the sole
    transient exception to your never-write rule.
 2. Run (single line):
-   `agy -p "Read the file AGY-TASK-BRIEF-<unique>.md in the workspace and execute it exactly." --model gemini-3.8-flash-high --add-dir <workspace> --log-file <log-path>`
+   `agy -p "Read the file AGY-TASK-BRIEF-<unique>.md in the workspace and execute it exactly." --model gemini-3.8-flash-high --mode accept-edits --add-dir <workspace> --log-file <log-path>`
+   `--mode accept-edits` is agy's own scoped mode and the one switch that
+   lets print mode land file edits: without it every write is soft-denied
+   on a trusted workspace, with all five preflights green (measured
+   2026-09-12 on agy 1.2.0 and 2026-09-13 on 1.2.2). It opens file edits
+   ONLY - command execution stays denied by design, and the wrapper runs
+   all verification (measured 2026-09-13 on 1.2.2: a `run_command` call
+   under the same flag was auto-denied). It persists nothing in
+   `settings.json`, and the brain transcript still records every tool
+   call with its arguments. Pass `<log-path>` in Windows spelling
+   (`C:/...` or `C:\...`): a Git-Bash `/c/...` spelling produced NO log
+   file at all (measured 2026-09-13), and a missing log is a missing
+   route line.
 3. Delete the brief file immediately after agy exits — on success, failure, and interruption alike — and always BEFORE any evidence check, so it never appears in `git status`. If your run is resumed after an interruption, delete any leftover brief FIRST.
 
 ## Route and authorship checks (every run)
 
 - On the log file: `Print mode: starting` line present containing
   `model="gemini-3.8-flash-high"`.
 - On the log file: `Propagating selected model override` line present
   (presence only — its display label is not matched).
-- Transcript/tree corroboration: parse `conversationID="<uuid>"` from the
-  log's `Print mode: starting` line, then read the brain transcript at
+- On the log file: `Print mode: applying agent mode accept-edits` line
+  present (measured 2026-09-13 on agy 1.2.2). A landed edit with no mode
+  line means the edit was permitted by something other than the dispatch
+  line - blocked, quoting the log.
+- Transcript/tree corroboration: parse the uuid from the log's
+  `Print mode: conversation=<uuid>, sending message` line. The
+  `Print mode: starting` line also carries a `conversationID=""` field,
+  and it is EMPTY (measured on agy 1.2.0 and 1.2.2, 2026-09-13); an empty
+  id is a missing transcript, not a wildcard. Then read the brain
+  transcript at
   `~/.gemini/antigravity-cli/brain/<conversationID>/.system_generated/logs/transcript_full.jsonl`
   (the `--log-file` log itself carries NO file actions — probed). Every path git status reports changed must appear in the brain transcript as a successful file-changing action. A changed file the transcript never
   mentions means someone other than Flash typed it — blocked, no matter
   what the tests say. A missing transcript is blocked.
 - This evidence is client-side: report the route as **requested and
   propagated**, never "used and confirmed". Server-side substitution is
   not detectable from this evidence class.
 
 ## Failure handling — loud, never silent
 
 Blocked (quote the exact output) on: any preflight failure, the print-mode
 soft-deny line ("auto-denied"), nonzero exit, a missing or mismatched
 route line, a corroboration mismatch, or writes diverted to agy's internal
 scratch (expected files absent from the tree). Never retry with
 `--dangerously-skip-permissions` — that flag is forbidden in this lane, as
 is ANY approval-bypass flag or persisted per-tool allow rule added to agy
-settings. Never complete the work yourself: rerouting a blocked task to a
+settings. `--mode accept-edits` is not a member of that class: it is the
+lane's declared mode, on the dispatch line where every reader sees it, it
+opens file edits only, and command execution stays denied under it. No
+other `--mode` value is used in this lane. Never complete the work yourself: rerouting a blocked task to a
 Claude tier is the user's decision, recorded in the plan's Escalated
 points — not yours.
 
 ## Report format (your final message)
 
 - **STATUS:** done | blocked | INPUT GAP: <exactly what is missing>
 - **ROUTE:** the resolved model ID as requested and propagated, plus the
   retained log file's path AND the brain transcript's path
 - **FILES CHANGED:** actual paths from `git status` — on blocked, STILL
   list every path Flash already touched so the session can revert a
@@ -118,13 +144,14 @@ points — not yours.
   (condensed)
 - **DEVIATIONS:** must be "none" — anything else means you stopped and are
   explaining why the task could not be built as written
 
 ## Lane note
 
 This agent pins the Flash implementation lane. Canonical model literal:
 `gemini-3.8-flash-high` (Gemini 3.8 Flash, high reasoning effort,
 Antigravity CLI resolved ID). The literal lives ONLY here;
 `implementer.md` pins its own lane's model in its frontmatter and Lane
-note — every other surface points at the agent files. Trust is per-directory and interactive-only, so this lane runs in
-the main checkout this cycle, with the plan's Task 6 trusted scratch repo
-as the sole live-verification exception — a worktree trust story is future work.
+note — every other surface points at the agent files. Trust is
+per-directory and interactive-only, and a listed directory covers what
+is beneath it: one interactive `agy` session in the parent that holds the
+worktrees, with trust approved, is enough for every worktree under it.
diff --git a/commands/doctor.md b/commands/doctor.md
index dfbadd9..e142c89 100644
--- a/commands/doctor.md
+++ b/commands/doctor.md
@@ -165,21 +165,25 @@ substate observed is still named in the detail text.
   `$env:USERPROFILE\.gemini\antigravity-cli\settings.json`. A missing
   file is BROKEN, because the lane blocks on it at dispatch. A file that
   does not parse as JSON is BROKEN, and an unreadable settings file is
   never reported as an empty one. A parsed file with no
   `trustedWorkspaces` key is BROKEN, because the lane cannot write in any
   workspace. A `trustedWorkspaces` that is present but NOT an array is
   BROKEN: the lane's preflight reads it positionally, so a changed shape
   is not a shorter list. Report `allowNonWorkspaceAccess` in the detail
   when the key is present, as an informational VALUE and never as a
   verdict, and say plainly that what it permits outside the workspace is
-  UNMEASURED (backlog item 36).
+  UNMEASURED (backlog item 36). Do not read `true` as what lets the lane
+  write: on agy 1.2.2 with `true` set, print mode denied every write
+  until the dispatch line carried `--mode accept-edits` (measured
+  2026-09-13); the agent file owns that flag, and this check does not
+  assert it.
 
 - **Authorship evidence root.** Verify
   `$env:USERPROFILE\.gemini\antigravity-cli\brain` exists. Missing is
   BROKEN: it is where the lane's authorship evidence is read from, and a
   lane whose evidence cannot be located must stop rather than proceed
   unverified.
 
 Report the resolved client path, the version, the model literal with
 whether `agy models` listed it, the trustedWorkspaces verdict with
 `allowNonWorkspaceAccess` when present, and the brain root. Report the
diff --git a/evals/multi-model-verify/test_flash_implementer.py b/evals/multi-model-verify/test_flash_implementer.py
index 00811d3..24baedf 100644
--- a/evals/multi-model-verify/test_flash_implementer.py
+++ b/evals/multi-model-verify/test_flash_implementer.py
@@ -34,20 +34,32 @@ def test_flash_frontmatter_pins_model_and_tools():
     assert m, "tools allowlist missing"
     tools = [t.strip() for t in m.group(1).split(",")]
     assert sorted(tools) == ["Bash", "Glob", "Grep", "Read"]
 
 
 def test_flash_dispatch_contract():
     body = _read(FLASH)
     assert "--model " + CANONICAL_ID in body
     assert "--add-dir" in body
     assert "--log-file" in body
+    # agy's own scoped mode opens file edits in print mode and leaves
+    # command execution denied (measured 2026-09-13 on agy 1.2.2: without
+    # it every write is soft-denied, with it a run_command call still
+    # is). It is the ONE switch between a lane that blocks on every
+    # dispatch and one that lands edits, and it is on the dispatch line
+    # where every reader sees it, unlike a persisted allow rule.
+    assert "--mode accept-edits" in body
+    assert body.count("--mode accept-edits") >= 2
+    assert "command execution stays denied" in body
+    # a Git-Bash /c/... log path produced NO log file (measured
+    # 2026-09-13); the log is where the route evidence lives
+    assert "Windows spelling" in body
     # unique-suffix brief name + full lifecycle, pinned by exact sentence
     # fragments so a regression cannot pass on loose keywords
     # (Sol check-off round 2, finding 3)
     assert "AGY-TASK-BRIEF-" in body
     assert "sole transient exception" in body.lower()
     assert "the dispatch log file's basename" in body
     assert "on success, failure, and interruption alike" in body
     # brief-borne no-commands line (Sol diff-debate F1: a task whose text
     # carries a verification command otherwise soft-denies in print mode
     # and blocks the green path - live-verified 2026-07-25)
@@ -56,60 +68,84 @@ def test_flash_dispatch_contract():
             "the file edits.") in body
     # stdin is probed-dead in print mode; the body must not suggest it
     assert "stdin" not in body.lower() or "does not reach" in body.lower()
 
 
 def test_flash_route_check_strings():
     body = _read(FLASH)
     assert 'Print mode: starting' in body
     assert 'model="' + CANONICAL_ID + '"' in body
     assert "Propagating selected model override" in body
+    # the mode the dispatch line asks for, echoed by the client
+    # (measured 2026-09-13 on agy 1.2.2, P2 log line 98)
+    assert "Print mode: applying agent mode accept-edits" in body
     assert "requested and propagated" in body
     assert "used and confirmed" not in body.replace(
         'never "used and confirmed"', "")
     # transcript/tree corroboration (Sol check-off F1: the log carries no
     # file actions; evidence lives in the brain transcript)
     assert "transcript_full.jsonl" in body
-    assert "conversationID" in body
+    # the id is on the session.go "Print mode: conversation=<uuid>, sending
+    # message" line; the starting line's conversationID field is EMPTY on
+    # agy 1.2.0 and 1.2.2 (both logs measured 2026-09-13), so a wrapper
+    # parsing the starting line gets no id and blocks a good run
+    assert "Print mode: conversation=<uuid>" in body
+    assert 'conversationID=""' in body
+    assert "parse `conversationID=" not in body
     assert ("every path git status reports changed must appear in the "
             "brain transcript as a successful file-changing action"
             ) in body.lower()
 
 
 def test_flash_preflight_pins():
     body = _read(FLASH)
     assert "agy models" in body
     assert "trustedWorkspaces" in body
     # conservative rule-class ban + clean baseline + stale-brief check,
     # pinned by exact sentence fragments (Sol check-off round 2,
     # finding 3): loose keyword pins would still pass a regression to
     # path-scoped matching or a dropped preflight
     assert "any `write_file(` entry, whatever path it names" in body
     assert "allow rule" in body
     assert "git status --porcelain" in body
     assert "No file matching `AGY-TASK-BRIEF-*`" in body
-    # main-checkout scope with its one declared carve-out (Sol round 3)
-    assert "sole live-verification exception" in body
+    # scope is the trust list itself, not a named checkout: preflight 2
+    # is the mechanical gate and a worktree needs its own entry (measured
+    # 2026-09-12: preflight passed in a trusted worktree on agy 1.2.0).
+    # The 0.12.0 "main checkout only" carve-out named a plan task that no
+    # longer exists.
+    assert "any directory listed in `trustedWorkspaces`" in body
+    # a parent entry covers a child worktree (measured 2026-09-13 on agy
+    # 1.2.2: one entry for the worktrees parent, an edit landed in a
+    # worktree under it that was not listed itself); preflight 2 must
+    # accept an ancestor or it blocks the configuration that works
+    assert "the workspace directory or an ancestor of it" in body
+    assert "a worktree needs its own entry" not in body
+    assert "Task 6" not in body
 
 
 def test_flash_route_report_carries_transcript():
     body = _read(FLASH)
     assert "AND the brain transcript's path" in body
 
 
 def test_flash_forbidden_bypass_class():
     body = _read(FLASH)
     assert "--dangerously-skip-permissions" in body
     idx = body.find("--dangerously-skip-permissions")
     window = body[max(0, idx - 200):idx + 200].lower()
     assert "never" in window or "forbidden" in window
     assert "persisted" in body and "settings" in body
+    # the scoped mode is named as NOT a member of the banned class, in
+    # the same section, so a reader of the ban cannot mistake the
+    # dispatch line for a violation of it
+    assert "`--mode accept-edits` is not a member of that class" in body
 
 
 def test_flash_report_headings():
     body = _read(FLASH)
     for heading in ("**STATUS:**", "**ROUTE:**", "**FILES CHANGED:**",
                     "**VERIFICATION:**", "**DEVIATIONS:**"):
         assert heading in body, heading
     # the four shared headings are pinned in BOTH files so a unilateral
     # rename in implementer.md cannot pass the suite (ROUTE is
     # lane-specific to the flash file)
diff --git a/tools/check-drift.ps1 b/tools/check-drift.ps1
index 7c4d8f0..a2dd5b8 100644
--- a/tools/check-drift.ps1
+++ b/tools/check-drift.ps1
@@ -125,21 +125,21 @@ if (-not $codexVersion) {
 }
 
 # --- agy: the Flash implementer lane's CONTRACTS, not just its version ---
 #
 # 0.24.0, backlog item 11. Until now this block ran `agy --version` and
 # stored the string, and nothing compared it to the snapshot. That is how
 # the item's own quoted version, 1.1.8, became 1.1.12 across four releases
 # without a word in any report.
 #
 # The lane's KNOWN OPERATIONAL CHECKS are enforced -
-# `agents/flash-implementer.md:45-59` runs three of them as a per-dispatch
+# `agents/flash-implementer.md` (its Preflight section) runs three of them as a per-dispatch
 # preflight and blocks a missing transcript after the run. That is not the
 # same as the lane's contracts being enforced: the security property in
 # backlog item 11 is UNMEASURED and stays open. What was missing is any
 # check EARLIER than dispatch, so a drift surfaced mid-build on a frozen
 # plan with the round's budget already committed. These checks move the
 # discovery earlier. They do not replace the enforcement, and they do not
 # cover what was never measured.
 $agyVersion = ""
 $agyExe = ""
 # The VALUE, kept with its JSON TYPE. `[string]` was applied here and at
```
