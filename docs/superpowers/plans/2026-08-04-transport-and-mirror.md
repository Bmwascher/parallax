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
