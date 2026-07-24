# Jinn Intake Adoptions (0.10.0) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adopt the four probe-settled practices from the jinn intake (pinned `hristo2612/jinn` @ `6c46f57a817cccda257f13c3380dc251f2d02c9c`): the `.agents/*` back-channel preflight sweep, the missing-rollout skip-the-retry class, `CODEX_HOME` in the env denylist, and a non-failing doctor quota-headroom row.

**Architecture:** Four independent contract amendments, each tests-first (the locked eval suite changes before the contract file it pins, per CLAUDE.md), followed by one full verification battery. No new executables — every change is rule text, command text, or test text over existing surfaces.

**Tech Stack:** Markdown contract files, pytest (evals/multi-model-verify), PowerShell 5.1-safe script edits.

## Global Constraints

- Tests change BEFORE the contract file they lock (CLAUDE.md "Skill editing rules").
- `skills/multi-model-verify/references/model-prompting-notes.md` is the ONLY file that may carry a reviewer model literal; no new `-m <model-id>` literal anywhere else (enforced by `test_reviewer_id_has_single_source`).
- `tools/check-drift.ps1` must remain pure ASCII (PS 5.1; `test_is_pure_ascii`).
- No backslash paths in `skills/multi-model-verify/**` files (`test_no_backslash_paths_anywhere`).
- `fallbacks.md` never names models.
- Commits: lowercase imperative, no AI attribution (CLAUDE.md git basics).
- Probe provenance carried in rule text: date 2026-07-24, codex-cli 0.144.1, jinn pinned `6c46f57` where cited.

---

### Task 1: `.agents/*` preflight sweep

**Files:**
- Modify (first): `evals/multi-model-verify/test_multi_model_verify.py` (inside `test_agents_md_backchannel_check`, after the `"--cached --others"` assertion, currently near line 176)
- Modify (second): `skills/multi-model-verify/SKILL.md` (preflight item 3, lines 50-62)
- Modify (third): `skills/multi-model-verify/references/model-prompting-notes.md` (the `.agents/skills` probe bullet's "Settles:" clause)

**Interfaces:**
- Produces: preflight enumeration command `git ls-files --cached --others '*AGENTS.md' '.agents/*'` (Task 5's behavioral run exercises the skill text carrying it).

- [ ] **Step 1: Add the failing test assertions** — inside `test_agents_md_backchannel_check`, immediately after the existing `assert "--cached --others" in text` block:

```python
        # codex also advertises repo-level .agents/skills/*/SKILL.md to
        # the model (probed 2026-07-24, v0.144.1: a planted skill was
        # read into the reviewer's context as its first action) - the
        # sweep must cover that surface too. .codex/ stays out: unprobed.
        assert "'.agents/*'" in text, (
            "the preflight enumeration must sweep .agents/ skill"
            " droppings alongside AGENTS.md"
        )
        assert ".agents/skills" in notes, (
            "the .agents ingestion probe must be documented in the notes"
        )
```

(Note: `notes` is already read later in the existing test — move the `notes = read(...)` line ABOVE the new assertions so both uses share it.)

- [ ] **Step 2: Run to verify it fails** — `python -m pytest evals/multi-model-verify/test_multi_model_verify.py::TestTransportContract::test_agents_md_backchannel_check -q` — Expected: FAIL on `'.agents/*'` (SKILL.md does not carry it yet).

- [ ] **Step 3: Edit SKILL.md preflight item 3** — replace the item's first two sentences and the enumeration sentence so the item reads (keep the rest of the item — the STOP sentence, the above-git-root and `~/.codex/AGENTS.md` sentences — unchanged after it):

```text
3. The reviewed repo must carry no AGENTS.md and no `.agents/` entries:
   codex auto-ingests AGENTS.md as instructions, and it advertises
   repo-level `.agents/skills/*/SKILL.md` to the model, which read a
   planted one as its FIRST action (both probed 2026-07-24: the planted
   AGENTS.md controlled the reviewer's reply; the planted skill entered
   its context; see model-prompting-notes.md) — back-channels into the
   auditor that break independence. Enumerate the whole tree in one
   listing — `git ls-files --cached --others '*AGENTS.md' '.agents/*'` —
   which covers tracked, untracked, AND ignored files at any depth
   (`.git` itself is never listed); a root-only or tracked-only check
   misses a nested drop.
```

   And append, after the `~/.codex/AGENTS.md` sentence: `Skills from the user's own codex plugin cache load the same way — note them in the debate record like the global AGENTS.md; not a stop.`

- [ ] **Step 4: Update the notes bullet** — in the `.agents/skills` probe bullet, replace `Settles: the AGENTS.md-only preflight sweep has a coverage gap; fix shape pending the 0.10.0 debate — SKILL.md's current preflight is the live contract until then.` with `Settles: the preflight enumeration sweeps '.agents/*' alongside AGENTS.md (adopted 0.10.0, debate 2026-07-24). '.codex/' stays unswept — unprobed; probe before adding.`

- [ ] **Step 5: Run to verify it passes** — same pytest command as Step 2. Expected: PASS.

- [ ] **Step 6: Commit** — `git add -A && git commit -m "0.10.0: sweep .agents/ in the back-channel preflight (probed 2026-07-24)"`

### Task 2: missing-rollout skip-the-retry class

**Files:**
- Modify (first): `evals/multi-model-verify/test_multi_model_verify.py` (new test in `TestFallbacks`, after `test_quota_limit_is_named_class`)
- Modify (second): `skills/multi-model-verify/references/fallbacks.md` (bounded-recovery paragraph lines 27-34; session-loss section lines 98-103)
- Modify (third): `README.md` (mermaid diagram line 87 area; bullet list line 97-99 area)
- Modify (fourth): `skills/multi-model-verify/references/model-prompting-notes.md` (lost-rollout bullet, C7 wording)

**Interfaces:**
- Produces: failure-class name `missing-rollout` referenced by fallbacks.md and README.

- [ ] **Step 1: Add the failing test** to `TestFallbacks`:

```python
    def test_missing_rollout_is_named_class(self):
        # Probed 2026-07-24 (codex-cli 0.144.1): resuming a nonexistent
        # session id fails deterministically with "no rollout found for
        # thread id <id> (code -32600)" and writes NO reply file. Never
        # transient: skip the retry, straight to the session-loss
        # consent gate (jinn intake, pinned 6c46f57).
        text = self.fallbacks()
        assert "no rollout found" in text
        assert "-32600" in text
        assert re.search(r"rollout.{0,240}skip the retry", text,
                         re.IGNORECASE | re.DOTALL), (
            "the missing-rollout signature must skip the retry"
        )
```

- [ ] **Step 2: Run to verify it fails** — `python -m pytest evals/multi-model-verify/test_multi_model_verify.py::TestFallbacks::test_missing_rollout_is_named_class -q` — Expected: FAIL.

- [ ] **Step 3: Edit fallbacks.md** — (a) in the bounded-recovery paragraph, change the parenthetical class list to `(codex-missing, model-rejected, auth-expired, route-mismatch, quota-exhausted, and a missing-rollout resume go straight to the gate — retrying those changes nothing)`. (b) In "Session id lost or resume fails", append:

```text
One resume failure is deterministic and skips the retry: output matching
`no rollout found for thread id ... (code -32600)` — class
`missing-rollout` (probed 2026-07-24; the reply file is not written).
The rollout is gone and a retry changes nothing: go straight to this
class's consent gate with the same fresh-per-round option.
```

- [ ] **Step 4: Edit README.md** — (a) add a mermaid edge directly under the quota edge: `X -. "missing-rollout resume:<br/>skip the retry" .-> G` (b) extend the quota bullet's paragraph with: `A resume failing with the missing-rollout signature ("no rollout found ... code -32600", probed 2026-07-24) also skips the retry — the rollout is gone; straight to the session-loss consent gate.`

- [ ] **Step 5: Fix the notes bullet wording (debate C7)** — in the lost-rollout bullet, replace `its response (silently restarting a fresh thread) is the opposite of the consent gate and was not adopted.` with `its response (a warning-logged but automatic, unconsented fresh-thread restart) is the opposite of the consent gate and was not adopted.` Also replace `a skip-the-retry candidate under fallbacks' session-loss class (adoption pending the 0.10.0 debate; fallbacks.md's one-retry rule is the live contract until then)` with `class missing-rollout in fallbacks.md skips the retry (adopted 0.10.0, debate 2026-07-24)`.

- [ ] **Step 6: Run to verify it passes** — same command as Step 2, then `python -m pytest evals -q`. Expected: PASS, full suite green.

- [ ] **Step 7: Commit** — `git add -A && git commit -m "0.10.0: missing-rollout resume failures skip the retry (probed 2026-07-24)"`

### Task 3: `CODEX_HOME` joins the env denylist

**Files:**
- Modify (first): `evals/multi-model-verify/test_multi_model_verify.py` — the drift tuple at line 1303, the runner assertion near line 1326, the doctor anchors near line 1391
- Modify (second): `evals/tools/run_behavioral_evals.py:479`
- Modify (third): `tools/check-drift.ps1:546`
- Modify (fourth): `commands/doctor.md:44-45`
- Modify (fifth): `README.md:110`
- Modify (sixth): `skills/multi-model-verify/references/model-prompting-notes.md` (env-hygiene bullet and CODEX_HOME probe bullet)

**Interfaces:**
- Produces: the four-variable denylist `CODEX_API_KEY, OPENAI_API_KEY, OPENAI_BASE_URL, CODEX_HOME` on every consumer surface.

- [ ] **Step 1: Make the tests demand four variables** — (a) line 1303 becomes `for var in ("CODEX_API_KEY", "OPENAI_API_KEY", "OPENAI_BASE_URL", "CODEX_HOME"):`. (b) After the existing `assert "CODEX_ENV_DENYLIST" in runner` add:

```python
        assert re.search(
            r'CODEX_ENV_DENYLIST = \("CODEX_API_KEY", "OPENAI_API_KEY",'
            r'\s*"OPENAI_BASE_URL", "CODEX_HOME"\)', runner), (
            "the denylist tuple must carry all four reroute-capable vars"
            " - CODEX_HOME redirects auth+config wholesale (probed"
            " 2026-07-24)"
        )
```

   (c) In `test_covers_all_six_checks`, add four anchors to the tuple: `"CODEX_API_KEY", "OPENAI_API_KEY", "OPENAI_BASE_URL", "CODEX_HOME",`.

- [ ] **Step 2: Run to verify it fails** — `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q -k "cross_review_route or reviewer_model_derives or covers_all_six"` — Expected: FAIL (three surfaces lack CODEX_HOME).

- [ ] **Step 3: Edit the executables** — (a) `run_behavioral_evals.py:479` → `CODEX_ENV_DENYLIST = ("CODEX_API_KEY", "OPENAI_API_KEY", "OPENAI_BASE_URL", "CODEX_HOME")` — one line or wrapped after the second element; Step 1b's regex accepts both. (b) `check-drift.ps1:546` → `foreach ($v in @("CODEX_API_KEY", "OPENAI_API_KEY", "OPENAI_BASE_URL", "CODEX_HOME")) {` (ASCII only).

- [ ] **Step 4: Edit the instruction surfaces** — (a) `doctor.md:44-45` → `clear \`CODEX_API_KEY\`, \`OPENAI_API_KEY\`, \`OPENAI_BASE_URL\`, and \`CODEX_HOME\` (\`Remove-Item Env:<name>\`)`. (b) `README.md:110` → `(\`CODEX_API_KEY\`, \`OPENAI_API_KEY\`, \`OPENAI_BASE_URL\`, \`CODEX_HOME\`)`. (c) notes env-hygiene bullet: the clear-list becomes `clear \`CODEX_API_KEY\`, \`OPENAI_API_KEY\`, \`OPENAI_BASE_URL\`, and \`CODEX_HOME\` FIRST`, and append: `\`CODEX_HOME\` redirects auth.json and config.toml wholesale (see its probe bullet below); clearing it reverts codex to the default home, so a legitimately relocated home fails the auth preflight LOUDLY instead of silently rerouting the lane.` (d) CODEX_HOME probe bullet: replace `Settles: \`CODEX_HOME\` is denylist-shaped; adoption pending the 0.10.0 debate — the three-var denylist above is the live contract until then.` with `Settles: \`CODEX_HOME\` is in the env denylist (adopted 0.10.0, debate 2026-07-24).`

- [ ] **Step 5: Run to verify it passes** — same command as Step 2, then `python -m pytest evals -q`. Expected: PASS.

- [ ] **Step 6: Commit** — `git add -A && git commit -m "0.10.0: codex-home joins the env denylist on all consumer surfaces (probed 2026-07-24)"`

### Task 4: doctor quota-headroom row and `N/A` verdict grammar

**Files:**
- Modify (first): `evals/multi-model-verify/test_multi_model_verify.py` (new test in `TestDoctorCommand`)
- Modify (second): `commands/doctor.md` (grammar line 5-7; new section after check 4)
- Modify (third): `README.md:176-179` (doctor capabilities sentence)

**Interfaces:**
- Consumes: the four-variable denylist wording from Task 3 (same doctor.md paragraph — apply Task 3 first).

- [ ] **Step 1: Add the failing test** to `TestDoctorCommand`:

```python
    def test_quota_row_is_nonfailing(self):
        # Probed 2026-07-24 (codex-cli 0.144.1): codex app-server
        # answers account/rateLimits/read locally. Experimental
        # surface: the row may be N/A, and N/A never contributes to
        # overall failure (jinn intake, pinned 6c46f57; Sol round 2).
        body = read(self.DOCTOR)
        assert "OK / STALE / BROKEN / N/A" in body, (
            "the table grammar must formally admit N/A"
        )
        assert re.search(r"N/A[^.]{0,160}never[^.]{0,80}overall",
                         body, re.IGNORECASE), (
            "N/A must be defined as never contributing to overall"
            " failure"
        )
        assert "app-server" in body and "account/rateLimits/read" in body
        assert "experimental" in body.lower()
```

- [ ] **Step 2: Run to verify it fails** — `python -m pytest evals/multi-model-verify/test_multi_model_verify.py::TestDoctorCommand -q` — Expected: FAIL.

- [ ] **Step 3: Edit doctor.md** — (a) the intro line becomes: `Run the parallax operational checks below and present ONE table: check | state | verdict (OK / STALE / BROKEN / N/A) | fix. N/A marks a check that cannot apply here or an experimental surface that did not answer; an N/A verdict never contributes to overall failure. End with a one-line overall summary. Report only - fix nothing without being asked.` (b) insert a new section between checks 4 and 5:

````markdown
## 4b. codex quota headroom (best effort, experimental)

Same sanitized shell as check 4. `codex app-server --stdio` answers the
JSON-RPC method `account/rateLimits/read` locally (probed 2026-07-24;
experimental capability — drift is expected and is exactly what N/A is
for). Hold stdin OPEN — the server exits when it closes.

```powershell
python -c "import json,shutil,subprocess,threading;bin=shutil.which('codex');p=subprocess.Popen([bin,'app-server','--stdio'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);r={};t=threading.Thread(target=lambda:[r.update(m=l) for l in p.stdout if '\"id\":2' in l.replace(' ','')],daemon=True);t.start();p.stdin.write(json.dumps({'id':1,'method':'initialize','params':{'clientInfo':{'name':'parallax-doctor','version':'0'},'capabilities':{'experimentalApi':True}}})+'\n'+json.dumps({'id':2,'method':'account/rateLimits/read','params':None})+'\n');p.stdin.flush();t.join(timeout=10);p.kill();print(r.get('m','NO-ANSWER'))"
```

Answer received: report `usedPercent`, `windowDurationMins` (as days/hours),
`resetsAt` (as local time), and `planType` in the state column — verdict
OK. `NO-ANSWER`, a spawn error, or malformed JSON: verdict
`N/A (experimental surface unavailable)` — NEVER BROKEN from this row
alone, and never retry in a loop. This row reads account state only; it
sends no review traffic and must not replace check 4's transport probe.
````

- [ ] **Step 4: Edit README.md:176-179** — the sentence becomes: `/parallax:doctor reports both, plus the fingerprint, the codex transport, quota headroom (best-effort, experimental), and any unresolved drift — in one table.`

- [ ] **Step 5: Run to verify it passes** — same command as Step 2, then `python -m pytest evals -q`. Expected: PASS.

- [ ] **Step 6: Commit** — `git add -A && git commit -m "0.10.0: doctor gains a non-failing quota-headroom row; verdict grammar admits n/a"`

### Task 5: full verification battery

**Files:** none (verification only)

- [ ] **Step 1:** `python evals/tools/skill_lint.py skills/multi-model-verify --strict` — Expected: `PASS - 0 error(s)`.
- [ ] **Step 2:** `python evals/tools/skill_scanner.py skills` — Expected: `0 CRITICAL, 0 WARN`.
- [ ] **Step 3:** `python evals/tools/run_trigger_evals.py` — Expected: `all clear`.
- [ ] **Step 4:** `python -m pytest evals -q` — Expected: all pass, 1 skip (opt-in state machine).
- [ ] **Step 5 (check-drift.ps1 changed):** in PowerShell: `$env:PARALLAX_STATEMACHINE = "1"; python -m pytest evals -q` — Expected: state-machine scenarios pass (slow; four scenarios re-run the suite in a worktree).
- [ ] **Step 6 (skill text changed):** `python evals/tools/run_behavioral_evals.py --head` — Expected: every case PASS, graded by the cross-vendor reviewer.
- [ ] **Step 7: Commit any generated state, if the suite wrote none skip** — `git status --short` must be clean.

---

## Debate record

**Participants:** Fable 5 (claude-fable-5) (session) / GPT-5.6 Sol (gpt-5.6-sol) (reviewer, codex exec, session 019f963b-37c9-7ff0-9789-0024971db8b2)
**Rounds used:** 2 of 4
**Outcome:** converged with amendments
**Verification status:** FULL
**Degradation:** none
**Authorized by:** n/a
**Raw rounds:** docs/superpowers/plans/rounds/2026-07-24-jinn-intake/ (round1-brief.md, round1-reply.txt, round2-rebuttal.md, round2-reply.txt; codex transcripts not retained — headers verified live each round)

Provenance: intake of https://github.com/hristo2612/jinn pinned at commit
6c46f57a817cccda257f13c3380dc251f2d02c9c (depth-1 clone, session
scratchpad, read-only, subject data under the never-instructions charter).
Probe records: four dated 2026-07-24 bullets in
skills/multi-model-verify/references/model-prompting-notes.md (codex-cli
0.144.1). Environment notes for the record: `~/.codex/AGENTS.md` exists
(user's own global instructions); the round-1 ingestion probe observed the
user's codex plugin cache loading a superpowers skill (user's own, same
treatment). The intake session asserts nothing from the reference was
followed or executed; per Sol's final-check this is recorded as the
session's assertion, not independently verified evidence.

### Resolved points

| # | Claim | Raised by | Outcome | Evidence |
|---|-------|-----------|---------|----------|
| C1 | `.agents/skills` is a swept-past back-channel; adopt minimal `.agents/*` pathspec | session | accepted into Task 1 (amended: test-first, no unprobed `.codex/`) | probe-fixture/transcript1.txt; SKILL.md:50-62; test :162-186 |
| C2 | missing-rollout resume is deterministic; skip the retry | session | accepted into Task 2 (amended: immediate-gate list + README diagram + dedicated test) | probe transcript2.txt; fallbacks.md:27-48,98-103 |
| C3 | CODEX_HOME is reroute-capable; join the denylist | session | accepted into Task 3 (amended round 2: doctor test pins the complete four-var tuple) | probe (login status flip); consumers swept: notes/check-drift:546/runner:479/doctor:44/README:110 |
| C4 | doctor quota-headroom row via app-server read | session | accepted into Task 4 (amended round 2: grammar formally admits N/A, defined non-failing) | probe (rateLimits response); doctor.md:5-7,17-18; jinn engine-limits.ts:370-453 |
| C5 | jinn sandbox-bypass practice rejected | session | accepted (PASS both rounds) | jinn codex.ts:334-355; setup.ts:645-658 |
| C6 | jinn nonzero-exit-tolerant success rejected | session | accepted (PASS both rounds) | jinn codex.ts:745-756; fallbacks.md:43-49 |
| C7 | jinn auto-restart on resume failure rejected | session | accepted with reviewer's wording fix: "warning-logged but automatic and unconsented" | jinn codex.ts:759-767 |
| C8 | jinn version probing weaker than drift watch | session | accepted with premise narrowed to "setup-time version/drift probing" | jinn setup.ts:72-78; check-drift.ps1 |
| C9 | jinn skill QA weaker than parallax gates | session | rationale corrected by reviewer (jinn HAS targeted template-contract tests); rejection retained | jinn template-company-doctrine.test.ts:210-330 |
| C10 | reference carries agent-instruction surfaces (release skill: 2FA-bypassing token publish) | session | accepted with precise surface naming; non-execution recorded as session assertion (reviewer UNVERIFIED note) | jinn .claude/skills/release-jinn-cli/SKILL.md:61-77 |

### Post-freeze approved deviations

| # | Deviation | Why | Approved by |
|---|-----------|-----|-------------|
| D1 | Task 2 Step 3(b) prose implemented as "The rollout is gone; skip the retry and go straight to this class's consent gate..." instead of the plan's "...and a retry changes nothing: go straight to..." | The plan's own Step 1 test regex (`rollout.{0,240}skip the retry`) cannot match the plan's Step 3(b) literal text — an internal plan wording defect; the test is the debate-locked contract, so the prose must satisfy it. Meaning-preserving; disclosed by the implementer; verified necessary by the task reviewer. | session adjudication, 2026-07-24 (task-2 review; surfaced to user in the execution report) |

### Escalated points (user-decided)

| # | Question | Session position | Reviewer position | Owner's call |
|---|----------|------------------|-------------------|--------------|
| A1 | structured `codex exec --json` transport | flag, do not smuggle | (not debated — user-deferred) | deferred, this release (user, 2026-07-24) |
| A2 | second reviewer vendor lane | flag, do not smuggle | (not debated — user-deferred) | deferred, this release (user, 2026-07-24) |
