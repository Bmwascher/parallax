# 0.21.0 — transport and mirror Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close backlog items 20, 21, 22 and 23 — the four defects and gaps on the dispatch, mirror and attestation path an operator touches on an ordinary run.

**Architecture:** Three of the four are contract changes with test pins; one (item 20's binding) adds a new evidence reader. Nothing changes the debate protocol itself. Every change follows the repo's standing order: the assertion is written and watched to FAIL before the shipped text or tool changes.

**Tech Stack:** PowerShell 5.1-compatible ASCII tools under `tools/`, pytest oracles under `evals/multi-model-verify/`, Markdown contracts under `skills/multi-model-verify/`.

## Global Constraints

- **Tests first, always.** The skill's transport commands are LIVE-VERIFIED contracts locked by `evals/multi-model-verify/test_multi_model_verify.py`. Change the tests first, watch them fail for the reason they claim, then change the skill.
- **`tools/*.ps1` are ASCII ONLY and Windows PowerShell 5.1 compatible.** Markdown may carry non-ASCII.
- **The gate is six commands** and must be clean on BOTH hosts before any task is considered done: `skill_lint --strict`, `skill_scanner`, `check_exact_line_oracles`, `run_trigger_evals`, and `pytest evals -q` under `PARALLAX_PS_HOST=powershell.exe` and again under `pwsh.exe`.
- **Contract regions must sit WHOLE inside a single pin** in one of the three clause forms `CLAUDE.md` names, and `DECLARED_REGIONS` in `test_contract_coverage.py` must be edited when a region is added or removed.
- **Never `git add -A` or `git add -u`.** Stage by explicit path.
- **BUMP THE VERSION LAST**, in Task 6 only. A mid-branch bump gets consumed by `plugin update` before the branch is finished. After updating, verify cache CONTENT, not the version number.
- **Token accounting is mandatory.** `SKILL.md` is at roughly 5129 tokens against a ~5000 budget. Every task that touches it records the measured token delta and states why the text belongs in `SKILL.md` rather than a reference. Detailed parser rules, mirror-universe detail and evidence semantics belong in references or tool comments; `SKILL.md` keeps point-of-use commands and the mandatory failure rule.
- **Vocabulary.** The new binding is a CLIENT-ECHO binding. It proves what the measured client recorded for this call. It never proves what the server or the model received, and no shipped text may imply otherwise.

## Evidence this plan rests on

`docs/superpowers/plans/rounds/2026-08-04-transport-and-mirror/resume-transport-probe.md`, five parts, measured on `codex-cli 0.144.1` across Windows PowerShell 5.1 and PowerShell 7. Plan debate: 3 rounds, both lanes (`gpt-5.6-sol` session `019fca2e-b7d3-7892-8a37-688f74e3d67b`; `kimi-code/k3-256k` session `session_58bce784-3e3d-45a6-92f6-0cc7833c08dc`).

---

## File Structure

| file | responsibility in this release |
|---|---|
| `evals/multi-model-verify/test_multi_model_verify.py` | pins for the stdin resume form, the binding rule, and item 23's paragraph |
| `skills/multi-model-verify/SKILL.md` | the two dispatch commands, the binding's mandatory failure rule, item 23's paragraph |
| `skills/multi-model-verify/references/model-prompting-notes.md` | the binding's full contract text; correction to the concurrency paragraph |
| `skills/multi-model-verify/references/fallbacks.md` | the new `brief-attribution` failure class |
| `skills/multi-model-verify/references/backup-lane.md` | the kimi resume-payload clarification; mirror identity fields; mirror universe |
| `tools/read-codex-round-evidence.ps1` | NEW — the client-echo binding reader |
| `evals/multi-model-verify/test_codex_round_evidence.py` | NEW — its oracles |
| `tools/new-review-mirror.ps1` | path-budget pre-flight; `source_head` capture; construction-time bridge |
| `evals/multi-model-verify/test_review_mirror.py` | pre-flight boundary cases and identity-field cases |

---

## Task 1: The codex resume dispatch uses stdin

**Files:**
- Modify: `evals/multi-model-verify/test_multi_model_verify.py` — `test_resume_flags_before_subcommand`
- Modify: `skills/multi-model-verify/SKILL.md:237`

**Interfaces:**
- Produces: the stdin resume form, which Task 2's binding contract references.

- [ ] **Step 1: Write the failing assertions.** Add to `TestTransportContract`, beside the existing resume test:

```python
    def test_resume_pipes_the_brief_on_stdin(self):
        """The brief must never be a POSITIONAL argument on resume.

        Measured 2026-08-03 on codex-cli 0.144.1 (resume-transport-probe.md).
        The npm wrapper splats $args to node. On Windows PowerShell 5.1 a
        quoted span splits the argument and strips the quotes; when the span
        contains no space the argument COUNT is unchanged, so nothing fails
        and the reviewer reads a brief this side never wrote. Round 1 was
        always immune because it pipes. This makes resume identical to it.
        """
        text = read(SKILL_MD)
        assert re.search(
            r"Get-Content -Raw <brief-file> \| codex exec"
            r" --sandbox read-only --disable plugins --disable apps"
            r" -c \$override -m <canonical-model-id>"
            r" -c model_reasoning_effort=<canonical-effort>"
            r" [^\n]*resume <SESSION_ID> -", text
        ), (
            "the resume dispatch must pipe the brief on stdin and end"
            " `resume <SESSION_ID> -`, matching round 1"
        )
        assert 'resume <SESSION_ID> "<rebuttal-brief>"' not in text, (
            "the positional brief form is live-proven defective on"
            " PowerShell 5.1 and must not return"
        )
```

- [ ] **Step 2: Run it and watch it fail.**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py::TestTransportContract::test_resume_pipes_the_brief_on_stdin -v`
Expected: FAIL on the first assertion. If it fails on the second instead, STOP — `SKILL.md` is not what this plan measured.

- [ ] **Step 3: Change the one line in `SKILL.md`.** Replace the resume dispatch line at `:237` with:

```
   Get-Content -Raw <brief-file> | codex exec --sandbox read-only --disable plugins --disable apps -c $override -m <canonical-model-id> -c model_reasoning_effort=<canonical-effort> --output-last-message <reply-file> resume <SESSION_ID> - > <transcript-file> 2>&1
```

Leave the preamble, the flags-before-subcommand rule and the surrounding prose untouched.

- [ ] **Step 4: Run both resume tests.** Both must pass. `test_resume_flags_before_subcommand` must STILL pass — it is unchanged and its regex still matches.

- [ ] **Step 5: Record the token delta.** Run the strict lint and note the before/after token count in the ledger. This step's text is a command replacement, so the delta should be near zero; a surprise here means something else changed.

- [ ] **Step 6: Commit.**

```bash
git add evals/multi-model-verify/test_multi_model_verify.py skills/multi-model-verify/SKILL.md
git commit -m "pipe the codex resume brief on stdin"
```

---

## Task 2: The codex client-echo brief binding

The largest task. Item 20's real gap is not the argument shape — it is that the backup lane verifies brief delivery and the codex lane never did.

**Files:**
- Create: `tools/read-codex-round-evidence.ps1`
- Create: `evals/multi-model-verify/test_codex_round_evidence.py`
- Modify: `skills/multi-model-verify/references/model-prompting-notes.md` — add the contract, correct the concurrency paragraph
- Modify: `skills/multi-model-verify/references/fallbacks.md` — add the failure class
- Modify: `skills/multi-model-verify/SKILL.md` — the point-of-use rule only
- Modify: `evals/multi-model-verify/test_multi_model_verify.py`, `test_contract_coverage.py`

**Interfaces:**
- Produces: `read-codex-round-evidence.ps1 -SessionId <id> -ExpectedBriefSha256 <hex> -PriorState <path> [-StateOut <path>]`, exiting 0 with one JSON line on stdout when the binding holds, and non-zero with the failure class on stderr otherwise.

### The frozen contract text

Adopted verbatim from the primary lane's round-3 amendment, with the continuity requirement the backup lane's round-3 reply required. This text goes in `model-prompting-notes.md`, inside contract markers.

> **Codex brief binding — fresh calls.** Before dispatch, hash the brief under the declared canonicalization and inventory the rollout files under the effective Codex session root. After the call, read the session ID only from the verified startup-header block. Require exactly one newly created rollout whose filename and first `session_meta` record both carry that session ID. Parse the file as strict UTF-8 JSONL. Malformed JSON, a missing terminal record boundary, no matching rollout, or multiple matching rollouts is a brief-attribution failure.
>
> **Codex brief binding — resumed calls.** Before dispatch, resolve exactly one rollout whose first `session_meta` record and filename match the resumed session ID; capture its byte length and SHA-256 over exactly those bytes. After the call, require the file still exists, is not shorter, and has the identical prefix hash. Parse only complete JSONL records after that byte boundary. A missing, replaced, truncated, or prefix-modified rollout is a brief-attribution failure.
>
> **Prompt record.** In the current-call slice, require exactly one record where `type` is `response_item`, `payload.type` is `message`, `payload.role` is `user`, and every `payload.content[]` element has `type` `input_text`. Concatenate those elements' `text` fields in order, canonicalize exactly as the pre-dispatch brief was canonicalized — UTF-8, CRLF normalized to LF, trailing whitespace stripped — and require SHA-256 equality. Missing, duplicated, malformed, undecodable, or unequal prompt evidence blocks the round; discard the reply unread.
>
> **Evidence limit.** This is a client-echo binding: it proves what the measured Codex client recorded for this call, never what the server or model received.

**The record shape above is MEASURED**, not assumed: probe part 5, three rounds of one session, exactly one matching record each with no cross-matches. Do NOT identify the record by content-element count — the preamble carries 2 elements and briefs carried 1 on that sample, but nothing prevents a client splitting a long prompt.

- [ ] **Step 1: Write the failing contract pins.** In `test_multi_model_verify.py`, assert each of the four paragraphs above appears in `model-prompting-notes.md`, and assert `brief-attribution` appears in `fallbacks.md`. Add the region ids to `DECLARED_REGIONS` in `test_contract_coverage.py`.

- [ ] **Step 2: Run them and watch them fail**, each naming the missing text. Expected: FAIL, one per absent paragraph.

- [ ] **Step 3: Write the failing tool oracles** in `test_codex_round_evidence.py`, against synthetic hand-authored rollout fixtures — never a raw recording, the repo is public. Minimum cases, each watched to fail:
  - a clean fresh call binds and exits 0
  - a clean resumed call binds using the byte boundary and exits 0
  - **prefix modified** after capture → non-zero, `brief-attribution`
  - **file shorter** than captured length → non-zero
  - **file replaced** (session id mismatch in `session_meta`) → non-zero
  - **two matching rollouts** for one session id → non-zero
  - **zero matching rollouts** → non-zero
  - **malformed JSON** in the slice → non-zero
  - **a trailing partial record** with no terminating newline → non-zero
  - **two user-prompt records** in the slice → non-zero
  - **zero user-prompt records** in the slice → non-zero
  - **hash mismatch** → non-zero, and the reply path is not read
  - **an adversarial brief** whose body contains `session_meta`-shaped and `response_item`-shaped JSON text → binds correctly, because the payload is a JSON string value and cannot create a record boundary (probe part 4)
  - a **stale rollout** — no new records appended by this call → non-zero. This is the continuity case; without it a stale rollout reads exactly like a fresh one.

- [ ] **Step 4: Implement `read-codex-round-evidence.ps1`** to make them pass. ASCII only, 5.1 compatible. It reads; it never writes into the session root. Every failure direction exits non-zero and prints its class; an unreadable or unparseable input is a failure, never a clean result.

- [ ] **Step 5: Run the tool oracles.** All pass.

- [ ] **Step 6: Write the contract text** into `model-prompting-notes.md` inside contract markers, and the `brief-attribution` class into `fallbacks.md` — no automatic retry, reply discarded unread, consent gate, matching the disposition already used for unattributable kimi evidence.

- [ ] **Step 7: Correct the concurrency paragraph.** `model-prompting-notes.md` currently states that session storage is not parsed for attribution. This release makes that false. Amend it to say the rollout IS parsed, by this binding, and that concurrent codex sessions are disambiguated by session id in both the filename and the first `session_meta` record.

- [ ] **Step 8: Add the point-of-use rule to `SKILL.md` only.** One sentence beside the dispatch blocks: the brief is hashed before dispatch and bound against the client's recorded prompt after it, and a brief-attribution failure blocks the round and discards the reply unread. The full contract stays in the reference. Record the token delta.

- [ ] **Step 9: Clarify the kimi resume payload.** In `backup-lane.md`, state explicitly that the `brief-hash-binding` rule covers the RESUME payload as well as round 1's brief. The region says "the brief" and the resume payload is a rebuttal; the coverage was an inference and is now stated.

- [ ] **Step 10: Run the whole gate on both hosts. Commit.**

```bash
git add tools/read-codex-round-evidence.ps1 evals/multi-model-verify/test_codex_round_evidence.py evals/multi-model-verify/test_multi_model_verify.py evals/multi-model-verify/test_contract_coverage.py skills/multi-model-verify/references/model-prompting-notes.md skills/multi-model-verify/references/fallbacks.md skills/multi-model-verify/references/backup-lane.md skills/multi-model-verify/SKILL.md
git commit -m "bind the codex brief to the client's recorded prompt"
```

---

## Task 3: The mirror path-budget pre-flight

**Files:**
- Modify: `evals/multi-model-verify/test_review_mirror.py`
- Modify: `tools/new-review-mirror.ps1`
- Modify: `skills/multi-model-verify/references/backup-lane.md`

**The frozen universe**, converged by both lanes:

> Every file and directory destination that the exact `robocopy /E` operation may create beneath the resolved mirror root, including tracked, untracked, ignored, and all `.git` content.

**Three requirements sit OUTSIDE that sentence and are equally binding:**

1. The `OverrideOut` path is written BESIDE the mirror, not by robocopy, and gets its own budget check.
2. Source reparse points are REFUSED before measuring. Do not assume the enumerator and robocopy traverse an identical universe without evidence.
3. An unreadable or unmeasurable source path BLOCKS the build. It is never skipped — that is the hole semantics the manifest builder already states.

**The frozen wording for the limit**, adopted verbatim after the primary lane struck the backup lane's API-boundary rationale as unmeasured:

> The tool enforces 260 characters as a conservative policy across both supported PowerShell hosts. It is a deterministic refusal threshold, not a claim about the maximum any host, API, OS configuration, or downstream client could support.

**Arithmetic:** resolved mirror-root length, plus separator, plus the relative destination path length.

- [ ] **Step 1: Write the failing tests.** Boundary cases: just under the threshold builds; at or over refuses. The refusal must name the mirror-root length, the deepest relative path length, the sum, and the limit. Assert the mirror does NOT exist after a refusal. Add a case where the deepest path is a DIRECTORY with no files, and a case where the deepest path is under `.git`. Add an `OverrideOut` over-budget case. Add a reparse-point refusal case. Add an unreadable-source-path case that blocks rather than skips.

- [ ] **Step 2: Run and watch every one fail.**

- [ ] **Step 3: Implement the pre-flight** in `new-review-mirror.ps1`, placed AFTER provider resolution and the overlap safety checks, and BEFORE `New-Item` or `robocopy`.

- [ ] **Step 4: Run the tests.** All pass, on both hosts.

- [ ] **Step 5: Document it** in `backup-lane.md` with the universe sentence and the policy wording, and add one `SKILL.md` line telling operators to build the mirror at a short path such as `%TEMP%\kerev<n>`, never inside the session scratchpad. Record the token delta.

- [ ] **Step 6: Commit.**

---

## Task 4: Mirror identity and the staleness gate

**Files:**
- Modify: `evals/multi-model-verify/test_review_mirror.py`
- Modify: `tools/new-review-mirror.ps1`
- Modify: `skills/multi-model-verify/references/backup-lane.md`

**The frozen six-step construction bridge:**

1. Capture `source_head_before`.
2. Copy the tree.
3. Require the live source HEAD still equals `source_head_before`.
4. Before remediation, require the copied mirror HEAD equals that source HEAD.
5. Remediate; then record `mirror_head`.
6. Before every fresh and resumed dispatch, compare live source HEAD to `source_head` and live mirror HEAD to `mirror_head`. Missing, unreadable or unequal BLOCKS the round.

Steps 3 and 4 are the bridge. Without them the record can hold two individually valid SHAs without proving the mirror was built from the recorded source commit.

**The frozen claim, narrowed:**

> The two-HEAD gate proves committed-HEAD freshness. Non-HEAD inputs are bound in the constructed mirror's manifest AT CONSTRUCTION TIME, and source-side changes after construction are detected by the source-status comparison below.

**The worktree-drift disposition — CHOSEN, not left as an OR.** The backup lane required this and it is right: the two-HEAD gate detects source COMMITS, but an edit to an untracked or ignored review input after construction moves nothing the gate compares, and that is precisely the content class the mirror exists to carry. Leaving "rebuild or fingerprint" unchosen would be an undetected failure mode wearing a decision.

**Chosen:** capture the source's status output at construction using the same status command the mirror already uses, and compare it at dispatch. It reuses existing machinery and makes both the common case and the edge case loud.

- [ ] **Step 1: Write the failing tests.** A stale mirror (source HEAD moved) blocks. A mirror whose HEAD was tampered blocks. A copied-but-not-from-this-source mirror blocks at step 4. Source worktree drift in an IGNORED file blocks at dispatch. Missing or unreadable identity fields block. A clean build and a clean dispatch both pass — the positive controls.

- [ ] **Step 2: Run and watch them fail.**

- [ ] **Step 3: Implement.** Add `source_head` and the construction-time source status capture to the record the script prints; add the bridge assertions.

- [ ] **Step 4: Run the tests on both hosts.**

- [ ] **Step 5: Document** the identity fields and the dispatch-time comparison in `backup-lane.md`, inside a contract region with its pin and `DECLARED_REGIONS` entry. State the narrowed claim verbatim.

- [ ] **Step 6: Commit.**

---

## Task 5: A PASS is terminal only for its own head

**Files:**
- Modify: `evals/multi-model-verify/test_multi_model_verify.py`
- Modify: `skills/multi-model-verify/SKILL.md` — finish-line section

- [ ] **Step 1: Write the failing assertion** beside the existing post-re-review finish-line pins.

- [ ] **Step 2: Run it and watch it fail.**

- [ ] **Step 3: Add the paragraph** to the finish-line section:

```
A PASS is terminal only for the exact head it was issued on. If you apply
anything the reviewer raised — including observations it labelled
non-blocking — the head moves and the verdict no longer covers it. Either
leave them for a follow-up branch, or run one confirming round.
```

- [ ] **Step 4: Run it.** Passes. Record the token delta.

- [ ] **Step 5: Commit.**

---

## Task 6: Ship

- [ ] **Step 1: Close backlog items 20, 21, 22 and 23**, each naming the evidence and what is NOT covered. Move them to Done in the status block.
- [ ] **Step 2: Run the whole gate on both hosts.** Six commands, zero unexpected skips.
- [ ] **Step 3: Run the opt-in behavioural evals**, because `skills/` changed: `python evals/tools/run_behavioral_evals.py --changed --head`. Expect the known-flaky `plan-mode-debate-runs` case to be unreliable — that is backlog item 18, not a regression from this branch. Print every skip by name.
- [ ] **Step 4: Record the total `SKILL.md` token delta** for the release and state whether the budget question (item 19) got worse. It will have; say by how much.
- [ ] **Step 5: BUMP THE VERSION** in `.claude-plugin/plugin.json` to `0.21.0`. Last, not earlier.
- [ ] **Step 6: Whole-branch Fable review, then the mode-diff debate**, then attest, then merge and push.
- [ ] **Step 7: `claude plugin update parallax@parallax`, restart, and verify the CACHE CONTENT** — grep the cached `SKILL.md` for the stdin resume form. The version string is not the check.

---

## Self-review

**Spec coverage.** Item 20 → Tasks 1 and 2. Item 21 → Task 3. Item 22 → Task 4. Item 23 → Task 5. All four backlog items have a task.

**Placeholder scan.** The one placeholder both lanes rejected — "identified by structure" — is now the measured four-condition shape in Task 2's contract. The 260 rationale is now pure policy wording with no unmeasured claim. Item 22's "rebuild or fingerprint" OR is resolved to a chosen disposition.

**Type consistency.** `read-codex-round-evidence.ps1`'s interface is declared once in Task 2 and referenced nowhere else. The mirror identity field names `source_head` and `mirror_head` are used identically in Task 4's steps and its contract text.

**Known gap, stated rather than hidden.** This release makes `SKILL.md` longer, worsening item 19. Tasks 1, 2, 3 and 5 each record their delta and Task 6 totals it. Item 19 is scheduled for 0.23.0.

---

## Amendments

Deviations from the frozen text, recorded at the moment they were taken.
A frozen plan that quietly changes under the implementer is not frozen.

### Amendment 1 (2026-08-04, Task 2) - the prompt-record rule was unsatisfiable

**Frozen text:** "In the current-call slice, require exactly one record
where `type` is `response_item`, `payload.type` is `message`,
`payload.role` is `user` ..."

**What implementation measured:** on a FRESH call the slice is the whole
file, and it always carries TWO such records - codex prepends its own
instructions preamble, which is also `role` `user`. The frozen rule
therefore fails every clean fresh round. The plan's own Step 3 note
already said the preamble is a second user record; the contract sentence
above it did not follow.

**Adopted instead:** consider every user record in the slice; require
exactly one of them to hash to the declared brief, and require it to be
the LAST user record in the slice. The trailing-record requirement is the
part that still refuses an injected extra prompt, which is what "exactly
one" was reaching for.

**Direction of the change:** exactly one case that previously failed now
passes, and it is the one the rule was breaking - a clean fresh round.
No case the rule exists to CATCH was loosened: a slice with a second
matching record still fails as ambiguous, and a slice with any user
record after the match still fails.

**Corrected 2026-08-04 after the Fable whole-branch review**, which
found this paragraph originally claimed "no case that previously failed
now passes" two sentences before naming one. It also found two real
widenings this amendment had not recorded. Both are now CLOSED in the
code rather than merely recorded, so the shipped rule is no wider than
the frozen one on either point:

- The frozen shape required EVERY `content[]` element to be
  `input_text`. The first implementation hashed only the `input_text`
  elements, so a record carrying the brief text plus something else
  bound clean. A record is now a binding candidate only if every
  element is `input_text`. Pinned by
  `test_a_record_carrying_a_non_text_element_does_not_bind`.
- The last-user-record rule refused a prompt injected AFTER the brief
  but accepted any number of non-matching user records before it. On a
  fresh call that is required, because the preamble is one. On a
  RESUMED call the measured slices carried exactly one user record, so
  the slack was unearned: a resumed slice must now carry exactly one.
  Pinned by `test_a_resume_slice_with_two_user_records_is_refused`.

**Locked by:** `test_a_user_record_after_the_brief_is_refused` and
`test_a_hash_mismatch_is_refused` in
`evals/multi-model-verify/test_codex_round_evidence.py`, both watched to
flip under mutation of the rule they claim to cover.

### Amendment 2 (2026-08-04, Task 2) - the validator's interface

**Frozen text:** "`read-codex-round-evidence.ps1 -SessionId <id>
-ExpectedBriefSha256 <hex> -PriorState <path> [-StateOut <path>]`,
exiting 0 with one JSON line on stdout when the binding holds, and
non-zero with the failure class on stderr otherwise."

**Adopted instead:** the shape its sibling `read-kimi-round-evidence.ps1`
already uses - two parameter sets (`-Fresh -SessionsRoot
-SessionIdFromStdout` / `-Resume -RolloutFile`), a `-Json` switch, and
ONE JSON line on stdout in both directions carrying `status`, `reason`
and, when clean, `nextState`.

**Why:** a fresh call cannot be handed the rollout it exists to discover,
so one `-SessionId` signature asks the fresh branch for its own answer.
Putting the reason on stdout rather than stderr is what lets the oracles
read it through `accept_exactly_one_nonempty_line()`, which CLAUDE.md
requires of every new single-line parser. `nextState` replaces
`-StateOut`: the script that establishes the byte boundary is the one
that hands it forward, so no caller can invent it.

**Direction of the change:** exit codes are unchanged (0 clean, 1
failed). Nothing that fails under the frozen shape passes under this one.

### Amendment 3 (2026-08-04, Task 2) - canonicalization is two-sided

**Frozen text:** "UTF-8, CRLF normalized to LF, trailing whitespace
stripped."

**Adopted instead:** LEADING and trailing whitespace stripped.

**Why:** the tool and every caller must apply the identical rule or the
hash never matches, and a one-sided strip leaves the leading case for a
driver to guess. Recorded rather than silently taken, because the
reviewer was right that it had drifted without an entry.

**Direction of the change:** neutral for delivery integrity - stripping
is applied to BOTH the sent brief and the recorded prompt, so a
transport that alters leading whitespace and nothing else is no longer
caught. That is accepted: the failure this binding exists to catch
(measured 5.1 quote stripping) alters the body, not the margins, and a
rule that fires on incidental margin differences would be retried into
irrelevance.

### Amendment 4 (2026-08-04, Task 2) - four permissive-direction fixes from the Fable review

The whole-branch review found four gaps between "no unmade or unreadable
measurement reads clean" and what the tool did. All four are closed, each
pinned by an oracle watched to fail first:

1. **Lenient decode.** `[Encoding]::UTF8.GetString` substitutes U+FFFD
   for invalid bytes and never throws (measured 2026-08-04), so a slice
   the contract called undecodable read clean. Now
   `UTF8Encoding($false, $true)`, which throws.
2. **Absent prior-state fields read as made measurements.** An absent
   `knownRollouts` and a legitimately empty one are both falsy, so the
   newly-created check was skipped exactly when nobody had built the
   inventory; an absent `bytes` casts to 0, which reads as "measure from
   the start of the file". Every field is now checked by NAME.
3. **Swallowed enumeration errors.** `Get-ChildItem -ErrorAction
   SilentlyContinue` turned "two rollouts, one unreadable" into "exactly
   one". Now `-ErrorAction Stop` inside a catch that fails the round.
   NOT covered by an oracle: no portable way was found to force an
   enumeration error in a temp directory, so this one rests on reading
   the code, not on a watched failure.
4. **Non-object JSON lines.** `null`, a bare scalar and an array all
   parse and were silently ignored. Now refused.

### Amendment 5 (2026-08-04, Task 3) - three deviations the Fable review found unrecorded

None changes behaviour; all three are text or file-list drift that the
plan calls frozen, and a frozen plan that quietly changes is not frozen.

1. **The limit sentence's lead-in.** The plan freezes "The tool enforces
   260 characters as a conservative policy across both supported
   PowerShell hosts" as verbatim text. The shipped region reads "The
   LIMIT is 260 characters as a conservative policy across both
   supported PowerShell hosts". Everything after the lead-in is
   verbatim and the meaning is unchanged; the region needed a
   sentence-initial label because it runs inline with the universe and
   the arithmetic rather than standing alone.
2. **Files outside Task 3's list.** The task named three files. Four
   more changed: `test_backup_lane.py` holds the region's pin,
   `test_contract_coverage.py` declares the region, the backlog carries
   item 26, and `SKILL.md` was already listed. The first two follow
   mechanically from putting a contract region in `backup-lane.md`,
   which the task itself directs; the backlog edit is deliberately
   outside this plan and is recorded as its own item.
3. **The token delta had no durable record.** Measured and reported at
   the time but written nowhere in the repo. Now in "Token deltas
   measured" below.

### Amendment 6 (2026-08-04, Task 3) - two permissive-direction fixes from the Fable review

1. **The repo ROOT was never attribute-checked.** Only entries beneath
   it were, so a repo root that is itself a junction was measured and
   copied straight through while the contract says a source reparse
   point is refused before measuring. This machine really does use
   junctions for lane homes. Fixed, and pinned by
   `test_a_repo_root_that_is_itself_a_reparse_point_is_refused`, watched
   to fail first: the old tool BUILT the mirror.
2. **`budget_error()` in the tests matched the wrong refusal.** It
   scanned for "path budget", and the unenumerable-path message says
   "the path budget was never measured", so three refusal cases would
   have accepted an enumeration block as a budget refusal. Now matches
   "path budget exceeded".

Also taken, from the review's minor 6: the relative path is now cut with
a rebuilt prefix rather than `root.Length + 1`. A drive root trims to
`C:`, where that arithmetic under-measures every relative path, which is
the permissive direction. Not covered by a test - a drive-root repo
mirrored to another drive is not a shape worth building a fixture for.

## Token deltas measured

`SKILL.md` body, by the strict lint's own estimator, against a ~5000
budget:

| point | tokens | delta |
|---|---|---|
| branch base `50575a3` | 5129 | - |
| after Task 1 | 5133 | +4 |
| after Task 2 (incl. review fixes) | 5273 | +140 |
| after Task 3 | 5334 | +61 |
| after Task 4 | 5334 | 0 |
| after Task 5 | 5404 | +70 |

**Release total: 5129 to 5404, +275, or 5.4 percent.** That is 404
tokens over the ~5000 budget, about 8 percent over. Task 4 cost nothing
here because the identity gate is documented entirely in
`references/backup-lane.md`; the three tasks that did cost tokens each
added a point-of-use rule an operator has to see before dispatching.

Item 19 is scheduled for 0.23.0 and this release makes it worse, as this
plan predicted it would. Item 27, filed by the Task 5 review, belongs
with it: both rewrite the same file and item 19 will be re-reading every
paragraph anyway.

### Amendment 7 (2026-08-04, Task 4) - the chosen drift disposition did not catch its own case

**Frozen text:** "capture the source's status output at construction using
the same status command the mirror already uses, and compare it at
dispatch." Its stated rationale: "an edit to an untracked or ignored
review input after construction moves nothing the gate compares, and
that is precisely the content class the mirror exists to carry."

**What implementation measured 2026-08-04:** the disposition as literally
written does NOT catch that case. `git status --porcelain --ignored
-uall -z` reports the PATH, not its bytes. Editing an already-ignored
file leaves the capture byte-identical, and the status-only fingerprint
verified CLEAN across exactly the drift the check exists to catch. The
oracle `test_source_drift_in_an_ignored_file_blocks_the_dispatch` was
watched to pass wrongly before the fix, which is how this surfaced.

**Adopted instead:** the fingerprint covers the status capture AND the
content manifest of every path status names, reusing the two functions
the mirror already has. Appearance and disappearance are still caught by
the status half; content edits are caught by the content half.

**Direction of the change:** strictly stricter. Nothing that blocked
before passes now. The cost is hashing the source's untracked and
ignored files at construction and again at each dispatch, which is work
the mirror already does once for its own manifest.

### Amendment 8 (2026-08-04, Task 4) - the dispatch gate needed an executable mode

**Not in the frozen text.** Bridge step 6 is written as a rule for the
driver, but Task 4's own Step 1 requires a case where "a clean dispatch"
passes, and a rule with nothing to run cannot have a passing case.

**Adopted:** a second parameter set on the same tool, `-VerifyIdentity
-RepoRoot -MirrorPath -SourceHead -MirrorHead -SourceStatusSha256`,
exiting 0 on a verified identity and 1 on any block. The three values
are passed as ARGUMENTS rather than re-read from a file the build wrote,
for the reason the codex brief binding states about its own expected
hash: a file re-read later is mutable and would silently redefine the
value it is supposed to pin.

**Two test seams**, `PARALLAX_MIRROR_COPY_SOURCE_OVERRIDE` and
`PARALLAX_MIRROR_MOVE_SOURCE_HEAD`, both environment variables rather
than parameters, following the lane-home builder's convention and its
rule: no shipped caller sets either, and each can only make a build
FAIL, never turn a failing build into a successful one.

### Amendment 9 (2026-08-04, Task 4) - the Fable review's CRITICAL finding did not reproduce

**The claim:** the two parameter sets have no
`[CmdletBinding(DefaultParameterSetName)]`, so the shipped build call
`-RepoRoot <repo> -MirrorPath <scratch>` is ambiguous and dies with
"Parameter set cannot be resolved" before any code runs; the suite
cannot see it because every build test adds the Build-only `-SkipProbe`.

**Measured, both hosts, the exact shipped invocation with no
`-SkipProbe`:** it resolves to Build and exits 0 after a real probe. The
Verify set declares four mandatory parameters that were not supplied, so
PowerShell has one satisfiable candidate and picks it. No default set is
needed.

**Recorded rather than dropped** because the reasoning was sound and the
conclusion was not, and the next reader deserves the measurement rather
than a silent absence. Nothing changed in the code for this finding.

### Amendment 10 (2026-08-04, Task 4) - three fixes from the Fable review, and one claim narrowed

1. **A failed read was silently given the previous file's hash.**
   Measured on both hosts: `[IO.File]::ReadAllBytes` failing is
   NON-terminating, so `$bytes` kept the prior iteration's contents and
   `Get-ContentManifest` recorded that hash for the file it could not
   read - deterministically, so the wrong value reproduces forever. Now
   caught and returned as an error. `Get-ChildItem -Recurse` gained
   `-ErrorAction Stop` for the same reason: a swallowed enumeration
   error omits everything under an unreadable subdirectory and the
   manifest then reads as coverage of a tree it never saw. Pinned by
   `test_an_unreadable_source_input_is_named_not_silently_hashed`,
   watched to fail under mutation.

   **The review's version of this finding was wider than what is
   reachable, and the narrower claim is the true one.** It said an
   unreadable file present at construction would produce a clean build
   whose wrong values reproduce at verify time and compare EQUAL. They
   cannot: robocopy fails with exit 9 on an unreadable source file and
   the build stops first. No false-clean identity was reachable. What
   was reachable, and is now fixed, is a verify-time read failure being
   reported as ordinary DRIFT rather than as a measurement that could
   not be made.

2. **Both test seams are rewritten, and the one-way claim now holds
   literally.** The review was right twice. A copy-source override aimed
   at a same-HEAD tree with different ignored content would have BUILT,
   carrying the wrong non-HEAD content under a record attesting the real
   source - so that seam was not one-way, by Amendment 7's own reasoning
   about what the mirror is for. And the head-moving seam committed into
   `$RepoRoot`, contradicting this tool's promise three lines from its
   top that it never writes to the real tree; any parent process can set
   these variables, so a seam that mutates user state is a hazard
   whatever its gating. Both now perturb ONE CAPTURED VALUE and nothing
   else. Neither changes what is copied, neither writes anywhere, and
   each can therefore only create a mismatch, which is a build that
   fails.

3. **The status fingerprint is now taken before AND after the copy, and
   required equal.** Taken only afterwards, an edit landing during the
   copy was baked into the record while the mirror carried older bytes,
   and every later verify passed. That direction is fail-open, which
   this gate may not be.

Also taken: the hex guards use `-cnotmatch`, so the lowercase-only
regexes mean what they say.

**Correction to Amendment 8.** It said verify exits "1 on any block".
Verify exits 1 on every identity block and 2 when the source root does
not exist, through the pre-existing path shared with build. Both are
refusals and neither can read as clean, but the earlier wording was
imprecise.


## Behavioural evals, measured 2026-08-04

`python evals/tools/run_behavioral_evals.py --changed --head`, nine cases
selected, all against `skills/multi-model-verify/SKILL.md`.

PASS: `diff-mode-spec-fidelity` 4/4, `degraded-consent-gate` 4/4,
`missing-reference-refusal` 3/3, `fix-application-checkpoint` 4/4,
`fix-checkpoint-attended-stop` 3/3, `no-manufactured-objections` 3/3.

SKIPPED(manual), both named as the plan's step required, both needing
state the harness cannot build: `backup-lane-consented-substitution`,
`panel-blind-relay`.

FAIL: `plan-mode-debate-runs` 2/4. This is backlog item 18's case and
its two misses are item 18's two documented causes, not a regression
from this branch:

- MISS 1 is the KNOWN, non-flaky cause item 18 names: the harness's
  transcript rendering truncates the PowerShell tool call before
  `codex exec` appears, so the grader cannot see the invocation it is
  asked to judge, however correctly the run behaved. An expectation the
  grader cannot observe is an unmade measurement wearing a verdict.
- MISS 3 is the residual flakiness: the plan made reference-specific
  claims without citing the reference file.

Item 18 measured this case at 2 of 6 passes on an UNCHANGED tree and 1
of 7 on the 0.20.0 branch, same expectations failing in both arms. Two
runs of it tonight disagreed with each other, 2 failures then 1, which
is the same flakiness observed again rather than new information.

**What this does NOT establish.** One run cannot exonerate a branch
against a case that fails two runs in three. The argument here is that
the failing expectations are the ones item 18 already attributes to the
harness and to the case itself, not that a single green run would have
proved anything.


### Amendment 11 (2026-08-04, whole-branch review) - the seams still were not one-way

**The claim the branch made three times** - in the tool comment, in the
test docstring, and in Amendment 10 item 2 - was that each seam perturbs
a captured value and can therefore only ever create a mismatch.

**That was false as implemented, and the whole-branch review caught it.**
Both seams REPLACED a measured value with the environment variable's
value. A parent that set `PARALLAX_MIRROR_SEAM_SOURCE_HEAD_AFTER` to the
repo's own current HEAD - trivially readable in advance - suppressed the
genuine post-copy measurement, so a source that really moved mid-copy
passed bridge step 3. The same substitution on the other seam neutralized
step 4. That turns a failing build into a passing one, which is the exact
inverse of the claim.

**Adopted:** both seams are now BOOLEANS that OR one extra block
condition into their comparison. `PARALLAX_MIRROR_SEAM_FAIL_SOURCE_STABLE`
and `PARALLAX_MIRROR_SEAM_FAIL_COPIED_HEAD`. Neither can supply a value,
so neither can suppress a measurement, and setting either can only ADD a
reason to fail. The property is now STRUCTURAL rather than a property of
the value someone passes, and it is asserted by
`test_the_seams_cannot_supply_a_value` rather than argued in a comment:
the case sets each flag to a real commit id and requires the build to
block anyway, with the specific reason checked because `-SkipProbe` also
exits 1.

**Correction to Amendment 8**, which named `PARALLAX_MIRROR_COPY_SOURCE_OVERRIDE`
and `PARALLAX_MIRROR_MOVE_SOURCE_HEAD`. Those were the FIRST pair and no
longer exist. The names above are the shipped ones.

**This is the third shape these seams have taken, and the third was found
by review rather than by reasoning.** Recorded that way on purpose: the
lesson is that a one-way claim about a test seam needs a test, not a
careful comment.

### Amendment 12 (2026-08-04, whole-branch review) - the fresh slice keeps its earned bound

Amendment 1 tightened the RESUMED slice to exactly one user record, on
the argument that the measured slices carried exactly one so anything
looser was unearned slack. The measured FRESH slices carried exactly two,
the instructions preamble and the brief, and the identical argument was
not applied to them. It is now: a fresh slice must carry exactly two.

**Direction:** strictly stricter. What it closes is a fresh slice
carrying preamble, an unexplained user record, and the brief last, which
bound clean because only the LAST record's position was checked.
Unattributed text in front of the reviewer is precisely the class this
binding exists to refuse.

**Also taken from the same review:** the verify mode resolved
`-MirrorPath` before this fix through the provider only in build mode,
so verify compared a relative path resolved against a different
location - the same provider-versus-process divergence this tool's own
history block calls an ordinary PowerShell condition. And the round-1
`-PriorState` schema existed only inside the tool's comment header, so
an operator reading `SKILL.md` and the references end to end could run
everything in this release except author that one file. Both fixed.

### Amendment 13 (2026-08-04, mode-diff debate round 1) - six findings from the cross-vendor lane

`gpt-5.6-sol`, effort high, sandbox read-only, session
`019fcb9a-e5a2-7ff3-be29-c38f0977b9ac`, brief binding `clean`. Eight
claims: 2 and 5 PASS, the rest FIX. Every finding was reproduced in this
session before it was accepted; none was rejected, and the application
checkpoint carries the dispositions.

**Two code defects, both permissive-direction, both closed.**

`knownRollouts` present but NULL passed the presence check that Amendment
12's sibling fix had just created. `@($null | ForEach-Object {...})`
yields a one-element array, so the inventory became a single garbage
entry, the "this rollout is new" comparison never fired, and a
PRE-EXISTING rollout could bind as if this call had created it. The
region's own fail-closed claim was therefore false. The prior state's
`knownRollouts` is now required to be a non-null array of non-empty
strings.

Resume never read the prefix's own `session_meta`. The contract said a
resumed rollout is resolved by that record AND its filename; the code
checked the filename and the prior state's recorded id, so the
provenance was trusted rather than re-measured. Resume now parses the
prefix's FIRST line under strict UTF-8 and requires its `payload.id` to
equal the resumed session id. Only the first line: the prefix hash
already pins the rest.

**Three claims were wider than their evidence, and were narrowed rather
than engineered away.** Sol's alternative in each case was construction
from an immutable filesystem snapshot. That is a real design and it is
not in this release's scope, so the honest move is the smaller claim.

- The path budget is measured before the mirror root exists and robocopy
  runs after it. "The exact `robocopy /E` operation" read as a guarantee
  of identical universes; the region now says the source AS ENUMERATED
  and names the window.
- The identity bridge compares ENDPOINTS. A source that moves away and
  back during the copy satisfies both the head equality and the
  fingerprint while the copied worktree holds intermediate bytes. The
  region now says observed endpoints and names the gap.
- Two backlog closures omitted limits the code plainly has. Item 20's
  closure now records the residue that survives the two code fixes: the
  tool validates the prior state's SHAPE, not its truthfulness, so an
  inventory taken at the wrong moment still binds clean. Item 22's
  records ABA and the path-universe mutation window.

**One shipped-guidance contradiction.** `SKILL.md` said never build the
mirror inside the session scratchpad; `references/backup-lane.md` said
reviews run in a mirror in the session scratchpad. I introduced the
`SKILL.md` half in Task 3 without reading the reference. One rule now,
stated in the reference and matching `SKILL.md`.

**What the round says about the release.** The two code defects were both
in text this branch ADDED, and one of them was inside a fix applied hours
earlier by the previous review. A fix is new code and gets no discount.

**The application itself failed the gate once, and the gate was right.**
The comments written to explain F1 and F2 named the reviewer model
literally, in `tools/read-codex-round-evidence.ps1` and
`evals/multi-model-verify/test_codex_round_evidence.py`. The
single-source sweep in `test_multi_model_verify.py` exists precisely so
that a reviewer swap changes ONE file, and it does not care that the
literal sat in a comment: a stale id in a comment is a stale id an
operator reads. Both now name the LANE rather than the model. Worth
recording because the literal arrived while writing prose about
correctness, which is exactly when the sweep stops being on anyone's
mind.

### Amendment 14 (2026-08-04, mode-diff debate round 2) - the fixes had defects, and one was older than the branch

Same reviewer session resumed against the applied diff. Claim 6, scope,
PASS. Claims 1 to 5 carried defects. Two of the reviewer's sub-claims did
NOT survive checking and were narrowed rather than accepted.

**Two reachable holes in the round-1 fixes.** The resume half still
validated field PRESENCE only, exactly the defect F1 closed on the fresh
half: a `rolloutFile` that was null or empty is present, and the
comparison tying the caller's file to the one the state measured was
gated on truthiness, so it was skipped. It runs unconditionally now, over
a validated schema. Separately, the F2 first-line check read `.type` and
`.payload.id` without proving it had an object.

**Two sub-claims narrowed.** The reviewer also said `bytes`,
`prefixSha256` and `sessionId` were permissive. They were not: each was
already refused downstream, by a failed coercion, a failed comparison and
a filename disagreement respectively. What was actually wrong is the
REASON each printed - a schema fault reported as a changed rollout sends
the operator to re-measure a file that is fine. The shape checks landed
anyway, on that narrower ground, and the closure says so.

**G9, which the reviewer did not find and its finding uncovered.** The
obvious instrument for the object check is `-is [PSCustomObject]`, and it
does not work. Measured on
`'[{"type":"session_meta",...}]' | ConvertFrom-Json`: Windows PowerShell
5.1 returns `System.Object[]`; PowerShell 7.6.3 UNROLLS the single
element and returns the object inside it. The SHIPPED slice parser used
that test, so its contract-stated rule that a non-object line blocks the
round was true on 5.1 and false on 7 - and older than this branch. Both
call sites now decide on the RAW TEXT beginning with `{` plus a
successful parse.

This is the 0.16.0 lane-lock class, second occurrence: a green suite on
one interpreter proves one interpreter. Both oracles were watched to
fail on PowerShell 7 by mutating the raw-text check out, and both PASSED
on 5.1 before the fix. That asymmetry is the evidence, and no single-host
run could have produced it.

**Four over-wide statements corrected.** The mirror-location text claimed
a single source while `SKILL.md` restates the rule in full; it now says
the rule lives in both files and must be changed in both. The identity
region claimed post-construction source changes are detected, when the
fingerprint only sees what `git status` sees - a raw-byte change
surviving the clean filter moves neither HEAD nor fingerprint, and the
autocrlf case this repo already measured is the mild version of it. Item
20's oracle-count sentence read as one-of-36 rather than one-of-six-new.
The test module dated every refusal to "before the validator exists",
which is stale for oracles a later review added.

**What round 2 says about round 1.** Every defect it found was in text
round 1 produced. Two rounds, two rounds' worth of fixes carrying their
own defects. The fix-gets-no-discount rule is not a slogan here; it is
the measured behaviour of this branch.
