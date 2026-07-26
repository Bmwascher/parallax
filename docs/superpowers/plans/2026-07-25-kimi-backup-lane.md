# Kimi Backup Reviewer Lane Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**STATUS: CANDIDATE — awaiting the dual plan debate (Sol + Kimi, user-directed)**

**Goal:** Codify the field-proven Kimi K3 backup reviewer lane into the plugin: consent-gated cross-vendor substitution when the primary (codex) transport is down, with mechanical per-round route AND containment evidence.

**Architecture:** A new `references/backup-lane.md` owns all lane mechanics; `model-prompting-notes.md` gains the only backup model-id declarations; `fallbacks.md` gains the consent-gate option, the transport-broken mapping, and the backup failure table; `frozen-plan-format.md` pins the lane-substitution recording; SKILL.md/README route the lane; doctor/drift watch the transport; offline pins lock all of it. Spec: docs/superpowers/specs/2026-07-25-kimi-backup-lane-design.md (probe record inside — all five plan-time probes RESOLVED).

**Tech Stack:** kimi-cli 1.49.0 (pip), pytest offline pins, PowerShell drift probes.

## Global Constraints

- All new test and eval content is pure ASCII.
- Commits: lowercase imperative, prefixed `0.13.0:`, no AI-attribution trailers.
- The backup model literal `kimi-code/k3-256k` appears ONLY in `skills/multi-model-verify/references/model-prompting-notes.md` (the declarations) and `evals/multi-model-verify/test_backup_lane.py` (the enforcement pin). Every other surface uses the placeholder `<canonical-backup-model-id>` or parses the notes file.
- The backup declaration labels are exactly `Canonical backup reviewer model id:` and `Canonical backup thinking flag:`; the primary declarations MUST precede them in the notes file (probe 12.4: both runtime parsers keep resolving the primary; no case-insensitive collision).
- Probed kimi-cli facts this plan treats as fixed (2026-07-25, kimi-cli 1.49.0; spec section 12): bare `kimi -r` loads the DEFAULT agent with full write/shell/web tools; the re-pinned resume loads the committed yaml and exactly the five-tool allowlist; kimi.log appends per-invocation `Using LLM model:`, `Loading agent:`, and `Loaded tools:` lines (offset-attributable); self-authored system prompt needs no template args; `LLM not set` exit 1 is the loud bad-model signature; `python -c "import kimi_cli.tools.file, kimi_cli.tools.todo"` succeeds non-billably.
- Implementer lane: `parallax:flash-implementer` per task (its debut production cycle); the classic haiku lane is the consent-gated fallback per the 0.12.0 contract. Long suites (pytest, state-machine, behavioral) are CONTROLLER-run, never inside implementer subagents (0.10.0 lesson).
- Main checkout only. No new trusted directories: kimi review clones live in the session scratchpad and are not agy workspaces.
- Frozen after debate: changes require reopening the debate.

---

### Task 1: Contract tests (all failing first)

**Files:**
- Create: `evals/multi-model-verify/test_backup_lane.py`
- Modify: `evals/multi-model-verify/test_multi_model_verify.py` (REQUIRED_REFERENCE_FILES list)
- Test: same files (this task is the test suite)

**Interfaces:**
- Consumes: nothing (first task).
- Produces: the executable contract every later task builds against. Tasks 2-6 make these tests pass; nothing may weaken a pin to get green.

- [ ] **Step 1: Write the failing test file**

Create `evals/multi-model-verify/test_backup_lane.py` with EXACTLY this content:

```python
"""Contract pins for the Kimi backup reviewer lane (0.13.0).

Design spec: docs/superpowers/specs/2026-07-25-kimi-backup-lane-design.md.
These pins lock the lane's transport command shape, containment
allowlist, per-round route+containment evidence rules, single-source
discipline, and fallback wiring - all offline, zero CLI calls.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REFS = REPO / "skills" / "multi-model-verify" / "references"
BACKUP_LANE = REFS / "backup-lane.md"
AGENT_YAML = REFS / "kimi-reviewer-agent.yaml"
SYSTEM_MD = REFS / "kimi-reviewer-system.md"
NOTES = REFS / "model-prompting-notes.md"
FALLBACKS = REFS / "fallbacks.md"
PLAN_FORMAT = REFS / "frozen-plan-format.md"
BACKUP_ID = "kimi-code/k3-256k"
ALLOWLIST = [
    "kimi_cli.tools.todo:SetTodoList",
    "kimi_cli.tools.file:ReadFile",
    "kimi_cli.tools.file:ReadMediaFile",
    "kimi_cli.tools.file:Glob",
    "kimi_cli.tools.file:Grep",
]
FORBIDDEN_TOOL_MARKERS = ["WriteFile", "StrReplaceFile", "Shell",
                          "SearchWeb", "FetchURL", "tools.web",
                          "tools.shell"]


def _read(p):
    return p.read_text(encoding="utf-8")


def test_backup_artifacts_exist():
    for p in (BACKUP_LANE, AGENT_YAML, SYSTEM_MD):
        assert p.is_file(), str(p)


def test_notes_backup_declarations():
    notes = _read(NOTES)
    assert "Canonical backup reviewer model id: `" + BACKUP_ID + "`" in notes
    assert "Canonical backup thinking flag: `--thinking`" in notes
    # primary parse must survive the amendment, in BOTH parser dialects
    m = re.search(r"Canonical model id: `([^`]+)`", notes)
    assert m and m.group(1) and m.group(1) != BACKUP_ID
    mi = re.search(r"Canonical model id: `([^`]+)`", notes, re.IGNORECASE)
    assert mi and mi.group(1) == m.group(1)
    # backup labels collide with neither primary regex, case-insensitive
    assert not re.search(r"Canonical model id:",
                         "Canonical backup reviewer model id:",
                         re.IGNORECASE)
    # ordering: primary declarations precede the backup block
    assert notes.index("Canonical model id:") < notes.index(
        "Canonical backup reviewer model id:")


def test_agent_yaml_allowlist_exact():
    yaml_text = _read(AGENT_YAML)
    for tool in ALLOWLIST:
        assert '"' + tool + '"' in yaml_text, tool
    for marker in FORBIDDEN_TOOL_MARKERS:
        assert marker not in yaml_text, marker
    assert "system_prompt_path: ./kimi-reviewer-system.md" in yaml_text


def test_backup_lane_dispatch_and_resume_pins():
    body = _read(BACKUP_LANE)
    assert "--quiet --thinking -m <canonical-backup-model-id>" in body
    assert "--agent-file" in body
    assert "KIMI-REVIEW-BRIEF.md" in body
    # the re-pinned resume is load-bearing: bare -r restores full tools
    assert ("kimi --quiet -r <session-id> --agent-file" in body)
    assert "loads the DEFAULT agent with full write and shell tools" in body
    assert BACKUP_ID not in body  # placeholder discipline


def test_backup_lane_evidence_pins():
    body = _read(BACKUP_LANE)
    assert "capture the byte length of" in body
    assert ("exactly one new `Using LLM model:` line carrying the "
            "canonical backup id") in body
    assert "`Loading agent:` line naming the committed yaml" in body
    assert "`Loaded tools:` line equal to the allowlist exactly" in body
    assert "DISCARDED unread" in body
    assert ("explicit refusal in the reply, marker absent on disk, "
            "clone status delta empty") in body
    assert ("must list exactly the brief file and nothing else") in body
    assert "Never run `kimi export` inside a repo" in body


def test_fallbacks_backup_wiring():
    fb = _read(FALLBACKS)
    assert "[run backup lane (cross-vendor preserved)]" in fb
    assert "reviewer reasoning effort" in fb
    # transport-broken mapping names its member classes
    assert "codex-missing" in fb and "model-rejected" in fb
    assert "quota-exhausted" in fb and "auth-expired" in fb
    assert "route-attribution" in fb
    assert "LLM not set" in fb


def test_plan_format_lane_substitution_pin():
    fmt = _read(PLAN_FORMAT)
    assert "lane substitution is NOT degradation" in fmt
    assert "backup cross-vendor lane substituted" in fmt


def test_skill_and_readme_route_the_lane():
    skill = _read(REPO / "skills" / "multi-model-verify" / "SKILL.md")
    assert "backup-lane.md" in skill
    readme = _read(REPO / "README.md")
    assert "run backup lane" in readme


SWEEP_GLOBS = [
    "skills/**/*.md", "skills/**/*.yaml", "commands/*.md", "tools/*.ps1",
    "hooks/*", "evals/**/*.py", "evals/**/*.json", "evals/**/*.ps1",
    "README.md", "CLAUDE.md", "agents/*.md",
]
ALLOWED = {NOTES.resolve(), Path(__file__).resolve()}


def test_backup_literal_single_source():
    offenders = []
    for pattern in SWEEP_GLOBS:
        for p in REPO.glob(pattern):
            if not p.is_file() or p.resolve() in ALLOWED:
                continue
            if BACKUP_ID in p.read_text(encoding="utf-8",
                                        errors="replace"):
                offenders.append(str(p))
    assert offenders == []
```

- [ ] **Step 2: Register backup-lane.md in the structural pins**

In `evals/multi-model-verify/test_multi_model_verify.py`, find the `REQUIRED_REFERENCE_FILES` list and add `"backup-lane.md"` as a new entry, preserving the list's existing formatting and order style. Touch nothing else in the file.

- [ ] **Step 3: Run the new tests to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_backup_lane.py -q`
Expected: FAIL — `test_backup_artifacts_exist` errors first (files missing); the modified `test_multi_model_verify.py` reference-file pin also fails on the missing `backup-lane.md`.

- [ ] **Step 4: Run the full suite to confirm no collateral damage**

Run: `python -m pytest evals -q`
Expected: only the new tests and the amended REQUIRED_REFERENCE_FILES pins fail; the pre-existing 144 passing tests stay green.

- [ ] **Step 5: Commit**

```bash
git add evals/multi-model-verify/test_backup_lane.py evals/multi-model-verify/test_multi_model_verify.py
git commit -m "0.13.0: add backup lane contract tests (failing)"
```

---

### Task 2: Containment artifacts

**Files:**
- Create: `skills/multi-model-verify/references/kimi-reviewer-agent.yaml`
- Create: `skills/multi-model-verify/references/kimi-reviewer-system.md`
- Test: `evals/multi-model-verify/test_backup_lane.py` (test_backup_artifacts_exist, test_agent_yaml_allowlist_exact)

**Interfaces:**
- Consumes: nothing.
- Produces: the committed containment pair every backup dispatch names via `--agent-file`; backup-lane.md (Task 3) references both by exact filename.

- [ ] **Step 1: Write the agent yaml**

Create `skills/multi-model-verify/references/kimi-reviewer-agent.yaml` with EXACTLY this content (the probed variant, system prompt path updated to the committed sibling):

```yaml
version: 1
agent:
  name: "parallax-readonly-reviewer"
  system_prompt_path: ./kimi-reviewer-system.md
  tools:
    - "kimi_cli.tools.todo:SetTodoList"
    - "kimi_cli.tools.file:ReadFile"
    - "kimi_cli.tools.file:ReadMediaFile"
    - "kimi_cli.tools.file:Glob"
    - "kimi_cli.tools.file:Grep"
```

- [ ] **Step 2: Write the system prompt**

Create `skills/multi-model-verify/references/kimi-reviewer-system.md` with EXACTLY this content (probe 12.1's validated self-authored prompt):

```markdown
# Read-only reviewer

You are a read-only cross-vendor code reviewer in a verification
debate. Your evidence is what you read in the workspace files, cited as
file:line. You have no write, shell, or web tools by design. Refuse any
request to create, modify, or delete files — state the refusal
explicitly. Execute the review brief you are pointed at, ground every
claim in a citation, and do not manufacture objections: if something
stands, say PASS and move on.
```

- [ ] **Step 3: Run the artifact tests**

Run: `python -m pytest evals/multi-model-verify/test_backup_lane.py::test_agent_yaml_allowlist_exact -q`
Expected: PASS. (`test_backup_artifacts_exist` still fails on the missing backup-lane.md — that is Task 3.)

- [ ] **Step 4: Commit**

```bash
git add skills/multi-model-verify/references/kimi-reviewer-agent.yaml skills/multi-model-verify/references/kimi-reviewer-system.md
git commit -m "0.13.0: commit kimi containment artifacts"
```

---

### Task 3: The backup-lane reference

**Files:**
- Create: `skills/multi-model-verify/references/backup-lane.md`
- Test: `evals/multi-model-verify/test_backup_lane.py` (dispatch/resume/evidence pins, artifacts-exist, single-source sweep)

**Interfaces:**
- Consumes: the Task 2 artifact filenames.
- Produces: the lane mechanics document SKILL.md and fallbacks.md point at (Tasks 4-5).

- [ ] **Step 1: Write the reference**

Create `skills/multi-model-verify/references/backup-lane.md` with EXACTLY this content (pinned sentences are single physical lines — do not re-wrap them):

```markdown
# Backup reviewer lane (cross-vendor substitution)

The backup lane substitutes a SECOND cross-vendor reviewer (currently
Kimi K3 via kimi-cli) when the primary reviewer transport is down. It
enters ONLY through the fallbacks.md consent gate — auto-qualified by
the classes named there, manual on user request — and preserves
cross-vendor independence, so a backup-lane debate records
`Verification status: FULL` with the lane substitution noted per
frozen-plan-format.md. Same debate protocol, same brief conventions,
same strike rule as the primary; only the transport differs. The
canonical backup model id and thinking flag are declared ONLY in
model-prompting-notes.md — read them from there at dispatch; this file
uses placeholders.

## Transport

- Dispatch (single line):
  `kimi --quiet --thinking -m <canonical-backup-model-id> --agent-file <plugin-checkout>/skills/multi-model-verify/references/kimi-reviewer-agent.yaml -w <throwaway-clone> -p "Read the file KIMI-REVIEW-BRIEF.md in this workspace and execute the review it describes."`
- Resume (single line — every flag below is load-bearing):
  `kimi --quiet -r <session-id> --agent-file <same yaml> -m <canonical-backup-model-id> --thinking -p "<rebuttal>"`
  A bare `kimi -r` loads the DEFAULT agent with full write and shell tools while the route line still reads clean (probed 2026-07-25: the behavioral refusal came from conversation priming with WriteFile and Shell live underneath); model and thinking inheritance come from CONFIG DEFAULTS, not the session. Re-pin all three on every resumed call.
- The session id is printed at the end of every run ("To resume this
  session: kimi -r <uuid>"). Capture it from round 1.
- Reviewer reasoning effort has NO CLI flag and NO log field: it is
  pinned via `[models.<id>.overrides]` in `~/.kimi/config.toml`
  (evidence class: config validation only — the consent banner names
  this gap when the backup option is offered).

## Per-round evidence (fresh AND resumed calls alike)

`~/.kimi/logs/kimi.log` is a shared, user-global append stream — a bare
"the line appears somewhere" check attributes nothing. The rule:

- Before every dispatch capture the byte length of `~/.kimi/logs/kimi.log`; after the call, past that offset, require all three: exactly one new `Using LLM model:` line carrying the canonical backup id, a `Loading agent:` line naming the committed yaml, and a `Loaded tools:` line equal to the allowlist exactly.
- Zero matching new lines, more than one, a wrong id, a wrong agent path, or any extra tool entry is a route-attribution failure: the reply is DISCARDED unread and the failure goes to the fallbacks.md consent gate.
- This evidence is client-side: report it as "route line verified
  (client-side)" in the record prose. Server-side substitution is not
  detectable from this class; the finish line's normalized
  `effective route confirmed` means every round's evidence matched THIS
  lane's canonical declarations under these rules.

## Containment

- The committed pair `kimi-reviewer-agent.yaml` +
  `kimi-reviewer-system.md` (this directory) is the ONLY agent
  configuration the lane dispatches with. The yaml's five-tool
  allowlist (SetTodoList, ReadFile, ReadMediaFile, Glob, Grep) carries
  no write, shell, or web tool — kimi print mode auto-approves ALL
  tools and `--plan` does not block writes (probed), so the allowlist
  is the load-bearing control and the per-round `Loaded tools:` check
  is its verification.
- WRITE-PROBE (before round 1 of every backup-lane debate): in a fresh
  disposable session with the exact debate configuration, ask the
  contained agent to create a named marker file. PASS requires all of: explicit refusal in the reply, marker absent on disk, clone status delta empty.
  Anything else means the lane is BROKEN (integrity failure class in
  fallbacks.md) — never dispatch a review over it.

## Clone isolation and the brief

- Reviews run in a THROWAWAY CLONE of the repo in the session
  scratchpad — never the real tree.
- The brief is written into the clone as the untracked
  `KIMI-REVIEW-BRIEF.md`; the `-p` pointer tells the reviewer to read
  it (headless stdin does not carry the brief).
- After every round, `git status --porcelain` in the clone must list exactly the brief file and nothing else; any other delta quarantines that round's reply (integrity failure class).
- The brief is retained as evidence per the raw-rounds convention.
- Never run `kimi export` inside a repo — it writes a session zip into the current directory; export only from a scratch directory. Nothing in this lane uses export.

## Failure handling

All failure classes, retries, and consent-gate dispositions live in
fallbacks.md (the single failure-class namespace) — this file defines
none of its own. Record fields for a substituted debate live in
frozen-plan-format.md.
```

- [ ] **Step 2: Run the tests**

Run: `python -m pytest evals/multi-model-verify/test_backup_lane.py -q`
Expected: test_backup_artifacts_exist, dispatch/resume pins, evidence pins, and single-source sweep now PASS; fallbacks/plan-format/SKILL pins still FAIL (Tasks 4-5).

- [ ] **Step 3: Commit**

```bash
git add skills/multi-model-verify/references/backup-lane.md
git commit -m "0.13.0: add backup lane reference"
```

---

### Task 4: Declarations, fallbacks, and record format

**Files:**
- Modify: `skills/multi-model-verify/references/model-prompting-notes.md` (append new section at end of file)
- Modify: `skills/multi-model-verify/references/fallbacks.md` (banner options line; new section before "## Degraded-mode output requirements")
- Modify: `skills/multi-model-verify/references/frozen-plan-format.md` (after the Degraded-mode note explanation)
- Test: `evals/multi-model-verify/test_backup_lane.py` (notes declarations, fallbacks wiring, plan-format pin) + full suite

**Interfaces:**
- Consumes: backup-lane.md (Task 3) as the pointer target.
- Produces: the declarations both runtime parsers and the doctor row read; the consent-gate wiring SKILL.md references.

- [ ] **Step 1: Append the backup declarations to model-prompting-notes.md**

Append at the END of the file (after the "## Reusable recipes" section) EXACTLY:

```markdown

## The backup reviewer lane (currently Kimi K3 via kimi-cli)

THE single source for the BACKUP reviewer's identity — the same
swap-by-one-edit rule as the primary declarations above, and the same
consistency-test enforcement (the backup literal is forbidden
everywhere else; command surfaces carry `<canonical-backup-model-id>`).
The primary declarations above MUST stay ahead of this block: both
runtime parsers match the first `Canonical model id:` occurrence, and
the drift script's PowerShell match is case-insensitive.

Canonical backup reviewer model id: `kimi-code/k3-256k`

Canonical backup thinking flag: `--thinking`

Everything else about the lane — transport, containment, per-round
evidence, clone isolation, failure routing — lives in
references/backup-lane.md. The lane enters only through the
fallbacks.md consent gate.
```

- [ ] **Step 2: Add the banner option in fallbacks.md**

In the consent-gate banner fenced block, replace the line:

```text
Options: [fix codex] [run degraded] [abort]
```

with:

```text
Options: [fix codex] [run backup lane (cross-vendor preserved)] [run degraded] [abort]
```

- [ ] **Step 3: Insert the backup-lane section in fallbacks.md**

Insert a new section immediately BEFORE the `## Degraded-mode output requirements (after consent)` heading, EXACTLY:

```markdown
## Backup reviewer lane (cross-vendor substitution)

A SECOND cross-vendor reviewer (transport, containment, and per-round
evidence: references/backup-lane.md; identity declared in
model-prompting-notes.md) can substitute for the primary WITHOUT
reducing vendor diversity — so a substituted debate stays
`Verification status: FULL`, recorded per frozen-plan-format.md's lane
substitution note. Substitution is still a consented transition: the
gate offers it, the user picks it, and `Authorized by:` records the
choice.

- Auto-qualified (the gate OFFERS the backup option) for:
  `quota-exhausted` (standing user ruling), codex-missing,
  model-rejected, auth-expired, and a route-mismatch or
  missing-rollout that survives its own gate. Available on user
  request for anything else.
- When the backup option is offered, the banner's
  `What it would NOT verify:` line names the backup lane's known
  evidence gap: reviewer reasoning effort (config-validation only —
  no per-call evidence).
- Backup-lane failures (detection → retry → disposition):
  - kimi-missing: `kimi --version` fails → no retry, consent gate.
  - kimi-bad-model: `LLM not set` (exit 1, loud) → no retry, consent
    gate.
  - route-attribution failure (offset rule in backup-lane.md): nothing
    transient → no retry, reply DISCARDED unread, consent gate.
  - resume failure: one same-parameters retry, then the consent gate
    with the fresh-per-round option (full brief re-sent each round).
  - integrity failure (write-probe fail, or a clone delta beyond the
    brief): no retry, reply quarantined, consent gate.
  - catch-all: one same-parameters retry, then the consent gate —
    mirrors the primary catch-all.
- BOTH lanes down: the honest choices are wait for a reset, the
  single-vendor DEGRADED skeptic, or abort — never a silent third
  vendor.
```

- [ ] **Step 4: Pin lane substitution in frozen-plan-format.md**

Immediately AFTER the fenced template block's closing fence and its explanatory paragraph ("The three status fields are structured on purpose..."), append EXACTLY this paragraph as its own block:

```markdown
Lane substitution (backup reviewer): `Verification status: FULL` MAY
carry a `Degradation:` class plus `Authorized by: user at round N` when
a backup cross-vendor lane substituted for the primary — lane substitution is NOT degradation; the Degradation field then names the
PRIMARY-lane failure that triggered substitution, and the Participants
line names the actual backup participant, e.g.
`Kimi K3 (kimi-cli, session <id>)`. This codifies the combination first
used by the 0.12.0 record. The Degraded-mode note stays bound to
DEGRADED status; a debate in which a backup cross-vendor lane substituted for the primary is recorded with this combination, never as DEGRADED.
```

- [ ] **Step 5: Run the tests**

Run: `python -m pytest evals/multi-model-verify/test_backup_lane.py evals/multi-model-verify/test_multi_model_verify.py -q`
Expected: notes/fallbacks/plan-format pins PASS; the pre-existing consent-banner and catch-all pins in test_multi_model_verify.py stay green (the banner test regex is an alternation; verified against the amended line during design review). SKILL/README pin still FAILS (Task 5).

- [ ] **Step 6: Commit**

```bash
git add skills/multi-model-verify/references/model-prompting-notes.md skills/multi-model-verify/references/fallbacks.md skills/multi-model-verify/references/frozen-plan-format.md
git commit -m "0.13.0: wire backup lane into declarations, fallbacks, record format"
```

---

### Task 5: SKILL.md and README routing

**Files:**
- Modify: `skills/multi-model-verify/SKILL.md` (Overview sentence; Preflight item 1; finish-line note)
- Modify: `README.md` (consent-gate flowchart; box list)
- Test: `evals/multi-model-verify/test_backup_lane.py::test_skill_and_readme_route_the_lane` + full suite + skill lint

**Interfaces:**
- Consumes: backup-lane.md and the fallbacks wiring (Tasks 3-4).
- Produces: the routed lane a session actually follows.

- [ ] **Step 1: SKILL.md Overview**

In the Overview paragraph, replace the sentence fragment:

```text
Two equal-weight advisors — this session and a cross-vendor reviewer driven
through the codex CLI (canonical reviewer model:
references/model-prompting-notes.md) — verify and refute each other's
claims before the cheap implementer touches code.
```

with:

```text
Two equal-weight advisors — this session and a cross-vendor reviewer driven
through the codex CLI (canonical reviewer model:
references/model-prompting-notes.md) — verify and refute each other's
claims before the cheap implementer touches code. A second cross-vendor
BACKUP reviewer lane (references/backup-lane.md — REQUIRED READING
before any backup round) substitutes through the fallbacks.md consent
gate when the primary transport is down; same protocol, different
transport, `Verification status: FULL` preserved.
```

- [ ] **Step 2: SKILL.md Preflight item 1**

Replace:

```text
   On failure follow references/fallbacks.md
   (degraded mode, visibly flagged; never silently skip cross-vendor review).
```

with:

```text
   On failure follow references/fallbacks.md
   (the consent gate may offer the cross-vendor backup lane —
   references/backup-lane.md — before any single-vendor degraded mode;
   never silently skip cross-vendor review).
```

- [ ] **Step 3: SKILL.md finish line note**

In the Finish line section, after the sentence ending "the route note: `effective route confirmed` when every round's header matched the canonical declarations, else the transport-failure class that fallbacks.md handled.", append to the same paragraph:

```text
The route-note grammar is lane-agnostic: for a backup-lane debate,
`effective route confirmed` means every round satisfied
references/backup-lane.md's per-round evidence rules against the backup
declarations; the evidence class is recorded in the debate record prose.
```

- [ ] **Step 4: README flowchart and box list**

In the mermaid consent-gate flowchart, after the line `G -->|fix codex| OK`, insert:

```text
    G -->|run backup lane| BK["cross-vendor backup reviewer<br/>(FULL, lane substitution recorded)"] --> OK
```

In the "What's in the box" list, after the row/line describing `references/fallbacks.md`, add a line matching the list's existing style:

```text
`references/backup-lane.md` — the cross-vendor backup reviewer lane (consent-gated substitution when codex is down; the gate's "run backup lane" option)
```

- [ ] **Step 5: Run tests and lint**

Run: `python -m pytest evals -q` — Expected: ALL tests pass now (the full new-pin set green, no regressions).
Run: `python evals/tools/skill_lint.py skills/multi-model-verify --strict` — Expected: PASS 0/0 (backup-lane.md referenced and existing).
Run: `python evals/tools/skill_scanner.py skills` — Expected: clean.
Run: `python evals/tools/run_trigger_evals.py` — Expected: all clear.

- [ ] **Step 6: Commit**

```bash
git add skills/multi-model-verify/SKILL.md README.md
git commit -m "0.13.0: route backup lane in skill overview, preflight, finish line, readme"
```

---

### Task 6: Doctor row and drift coverage

**Files:**
- Modify: `commands/doctor.md` (new check 8 after check 7)
- Modify: `tools/check-drift.ps1` (kimi version probe + snapshot field, flag-surface probe, vocabulary probe — carry-forward style, agy precedent)
- Modify: `evals/tools/drift_statemachine_tests.ps1` stub CLIs/assertions as needed for the new probes
- Test: full pytest suite + the offline state-machine suite (CONTROLLER-run)

**Interfaces:**
- Consumes: the notes declarations (Task 4) — both surfaces PARSE, never hardcode, the backup id.
- Produces: operational watch for the kimi transport.

- [ ] **Step 1: Doctor check 8**

Append after check 7 in `commands/doctor.md`, matching the numbered-check format of the file, a check with EXACTLY this content:

```markdown
8. **Backup reviewer transport (kimi).** Run `kimi --version`. Parse the
   backup id from the line `Canonical backup reviewer model id:` in
   skills/multi-model-verify/references/model-prompting-notes.md (this
   check carries no model literal). Verify both containment artifacts
   exist: references/kimi-reviewer-agent.yaml and
   references/kimi-reviewer-system.md. Report the version, the parsed
   id, and the artifact presence. Any failure is reported as
   BACKUP-LANE UNAVAILABLE (the primary lane is unaffected) — the fix
   pointer is references/backup-lane.md.
```

- [ ] **Step 2: Drift script — version snapshot (carry-forward)**

Mirror the agy field exactly: add a `$kimiVersion` probe beside the agy probe (`kimi --version`, tolerate absence), a `$kimiVersionToSave` carry-forward inside the existing `if ($snapshot)` block, and `kimi = $kimiVersionToSave` in `$newSnapshot` — same pattern, same failure tolerance as the agy field. No inline `if` in the hashtable (PS 5.1 hazard).

- [ ] **Step 3: Drift script — flag-surface and vocabulary probes**

Beside the codex flag probe, add a kimi probe block: capture `kimi --help` once; require each of `--quiet`, `--thinking`, `-m`, `--agent-file`, `-w`, `-p`, `-r` to appear in the help text; then run `python -c "import kimi_cli.tools.file, kimi_cli.tools.todo"` and require exit 0. Each miss appends a drift finding naming the missing flag or module (finding style copied from the codex flag probe's findings). Both probes are skipped with a single carried-forward note when `kimi --version` failed (no cascade).

- [ ] **Step 4: State-machine suite stubs**

Extend the stub CLIs in `evals/tools/drift_statemachine_tests.ps1` so the existing scenarios still drive the script end-to-end offline: a stub `kimi` answering `--version` and `--help` (help text containing all seven flags) and a stub `python` import success where the harness fakes binaries. Add one scenario assertion: a help text MISSING `--agent-file` produces a drift finding naming it.

- [ ] **Step 5: Run the suites (CONTROLLER-run)**

Run: `python -m pytest evals -q` — Expected: all green.
Controller runs: `evals/tools/drift_statemachine_tests.ps1` — Expected: ALL SCENARIOS PASS including the new assertion. This suite is run by the CONTROLLER, never inside the implementer subagent (0.10.0 lesson).

- [ ] **Step 6: Commit**

```bash
git add commands/doctor.md tools/check-drift.ps1 evals/tools/drift_statemachine_tests.ps1
git commit -m "0.13.0: doctor kimi row and drift flag, vocabulary, version coverage"
```

---

### Task 7: Behavioral eval case

**Files:**
- Modify: `evals/multi-model-verify/evals.json` (one new case)
- Test: `python evals/tools/run_behavioral_evals.py --list` (case parses; manual cases are runner-skipped)

**Interfaces:**
- Consumes: the shipped fallbacks/backup-lane text (Tasks 3-4).
- Produces: the versioned behavioral expectation for backup routing.

- [ ] **Step 1: Add the case**

Append to the `evals` array in `evals/multi-model-verify/evals.json` (comma-correct, preserving formatting) EXACTLY:

```json
{
  "id": "backup-lane-consented-substitution",
  "setup": { "manual": true, "no_codex": true, "with_reference": true },
  "surface": ["skills/multi-model-verify/SKILL.md", "skills/multi-model-verify/references/fallbacks.md", "skills/multi-model-verify/references/backup-lane.md"],
  "prompt": "Plan the port of References/DemoWidget into a module for this project. Use multi-model verification before freezing the plan. (Environment: codex CLI is not installed; kimi-cli is installed and authenticated; the user has already answered the consent gate: 'run backup lane'.)",
  "expected_output": "The debate runs over the BACKUP lane per references/backup-lane.md: contained dispatch with the committed agent yaml, per-round offset-attributed route AND containment evidence from kimi.log, and a debate record showing Verification status FULL with the lane substitution and the user authorization recorded.",
  "expectations": [
    "The codex preflight failure is reported and the recorded consent ('run backup lane') is quoted - substitution is never inferred",
    "Every kimi dispatch uses the committed kimi-reviewer-agent.yaml via --agent-file, and resumed calls re-pin --agent-file, -m, and --thinking (a bare kimi -r is a violation)",
    "Per-round evidence follows backup-lane.md: pre-dispatch log offset captured; exactly one new Using LLM model: line with the canonical backup id, a Loading agent: line naming the committed yaml, and a Loaded tools: line equal to the allowlist - all past the offset",
    "The write-probe precedes round 1 (refusal + absent marker + clean delta) and the review runs in a throwaway clone whose post-round git status lists exactly KIMI-REVIEW-BRIEF.md",
    "The debate record shows Verification status FULL with Degradation naming the primary-lane failure class and Authorized by recording the user - never DEGRADED"
  ]
}
```

- [ ] **Step 2: Verify the runner parses it**

Run: `python evals/tools/run_behavioral_evals.py --list`
Expected: the new case listed (marked manual/skipped); no parse errors.

- [ ] **Step 3: Run the full offline suite**

Run: `python -m pytest evals -q` — Expected: all green (the evals.json sweep pins tolerate the new case; the backup literal does not appear in it — the expectations say "canonical backup id" by name).

- [ ] **Step 4: Commit**

```bash
git add evals/multi-model-verify/evals.json
git commit -m "0.13.0: behavioral case for consented backup substitution"
```

---

### Task 8: Version bump, dev loop, live verification (ATTENDED; runs only after the plan debate converges)

**Files:**
- Modify: `.claude-plugin/plugin.json` (version 0.13.0)
- None else in-repo (scratch clone + probe records; SDD ledger notes)

**Interfaces:**
- Consumes: the installed 0.13.0 cache (dev loop: bump, `claude plugin update parallax@parallax`, restart — skills/ changed, so the restart is REQUIRED before any live step tests anything).
- Produces: the live evidence the diff debate's brief cites.

- [ ] **Step 1: Bump and commit BEFORE the dev loop**

Set `.claude-plugin/plugin.json` version to `0.13.0`, commit (`0.13.0: bump plugin version`), verify `git status --porcelain` is empty.

- [ ] **Step 2 (ATTENDED - user): Dev loop**

User runs `claude plugin update parallax@parallax` and restarts the session. Without the restart the installed skill text is the cached pre-0.13.0 set — a live run before restart tests nothing (0.12.0 lesson, twice-proven: verify by evidence content, not report status).

- [ ] **Step 3: Behavioral evals for the touched surfaces (CONTROLLER-run, billable — budget note)**

Run: `python evals/tools/run_behavioral_evals.py --changed`
Expected selection: the cases whose surfaces intersect this branch (SKILL.md, model-prompting-notes.md, fallbacks.md changed → at least plan-mode-debate-runs, diff-mode-spec-fidelity, degraded-consent-gate, no-manufactured-objections; the new manual case prints as SKIPPED). These are REAL headless runs graded over the primary reviewer lane — confirm codex quota headroom first (doctor check 4b); if quota blocks, record the deferral in the ledger and surface it in the diff-debate brief rather than skipping silently.

- [ ] **Step 4: Live backup-lane verification through the CODIFIED machinery**

All commands built by reading the INSTALLED skill text (cache), resolving `<canonical-backup-model-id>` from the installed notes file:
1. Fresh throwaway clone of the repo in the session scratchpad; write a scratch review brief as `KIMI-REVIEW-BRIEF.md` (any small real review target, e.g. "review agents/flash-implementer.md's report format section for internal consistency; cite lines").
2. WRITE-PROBE per backup-lane.md (fresh disposable session, exact debate configuration, marker request): expect refusal + absent marker + clean delta.
3. Round 1 dispatch per the pinned command; per-round evidence checks (offset, route line, Loading agent, Loaded tools) — all three past the offset.
4. One resumed exchange with the re-pinned resume form; the same per-round checks repeat and pass.
5. Post-round clone check: exactly `KIMI-REVIEW-BRIEF.md`, nothing else.
6. Negative probe: run the round-1 command with `-m kimi-code/nonexistent-model` in the clone — expect `LLM not set`, exit 1, no reply file consumed.
7. Record all outcomes with log offsets and session ids in the SDD ledger.

- [ ] **Step 5: Record**

Write the dev-loop, behavioral-run, and live-verification outcomes into the SDD ledger (`.superpowers/sdd/2026-07-25-kimi-backup-lane/`) — the diff-debate brief cites them.

---

## Debate record

(to be completed at freeze: dual plan debate — Sol primary check-off + Kimi second lane, both user-directed for this cycle — per frozen-plan-format.md)
