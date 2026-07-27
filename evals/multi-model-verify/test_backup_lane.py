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


def _norm(p):
    """Whitespace-normalized read, for pins that span a markdown wrap."""
    return " ".join(_read(p).split())


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
    # exact LIST equality: extra, missing, or reordered tool entries all
    # fail - presence checks alone would tolerate an added WriteFile
    tools = re.findall(r'-\s+"([^"]+)"', yaml_text)
    assert tools == ALLOWLIST
    for marker in FORBIDDEN_TOOL_MARKERS:
        assert marker not in yaml_text, marker
    assert "system_prompt_path: ./kimi-reviewer-system.md" in yaml_text


def test_backup_files_no_backslash_paths():
    for p in (BACKUP_LANE, AGENT_YAML, SYSTEM_MD):
        assert "\\" not in _read(p), str(p)


def test_backup_lane_dispatch_and_resume_pins():
    body = _read(BACKUP_LANE)
    # the dispatch pin covers the COMPLETE command through -w and -p:
    # a dropped -w would dispatch the reviewer in the shell's cwd (the
    # same class the resume pin below guards), and a bare substring
    # check would stay green through it (final-review finding, 0.13.0)
    assert ("kimi --quiet --thinking -m <canonical-backup-model-id> "
            "--agent-file <plugin-checkout>/skills/multi-model-verify/"
            "references/kimi-reviewer-agent.yaml -w <review-mirror> -p"
            ) in body
    assert "KIMI-REVIEW-BRIEF.md" in body
    # the re-pinned resume is load-bearing: bare -r restores full tools,
    # model/thinking inherit from CONFIG DEFAULTS, and -w does not
    # inherit at all (a resume without it runs in the shell's cwd -
    # caught live against the real tree), so the pin covers the
    # COMPLETE resumed command through -w
    assert ("kimi --quiet -r <session-id> --agent-file <same yaml> -m "
            "<canonical-backup-model-id> --thinking -w <same mirror>"
            ) in body
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
            "mirror status delta empty") in body
    assert "Never run `kimi export` inside a repo" in body


def test_backup_lane_workspace_is_a_mirror_not_a_clone():
    # 0.14.2, found live 2026-07-26 (KitnEssentials): the lane's
    # workspace was specified as a `git clone`, which carries TRACKED
    # FILES ONLY - and the review inputs are routinely gitignored (the
    # frozen plan under a project's docs dir, References/ for port
    # work). A cloned workspace hands the reviewer a tree with nothing
    # to review while every route and containment check stays green.
    body = _norm(BACKUP_LANE)
    assert "THROWAWAY REVIEW MIRROR" in body
    assert ("a FILE COPY of the working tree that PRESERVES `.git`, not "
            "a `git clone`") in body
    assert "a clone carries TRACKED FILES ONLY" in body
    # the failure is named concretely, not left as an abstraction
    assert "`dev/docs/` and `References/` are both gitignored" in body
    # inputs the mirror cannot inherit are copied in DELIBERATELY and
    # enumerated - the containment rule keys off a declared set, so an
    # unexpected delta still quarantines
    assert ("must equal the BASELINE plus exactly the expected untracked "
            "set — the brief plus any review inputs copied in, "
            "enumerated before the round — and nothing else") in body
    assert "is a gap in the review, not a silent omission" in body


def test_mirror_baseline_closes_the_dirty_tree_hole():
    # 0.14.2 whole-branch review, Important 1: a clone guaranteed an
    # empty porcelain; a file copy does not. Without a baseline, the
    # real tree's untracked files and uncommitted modifications ride
    # into the mirror and quarantine every round of a review that never
    # touched them - and a tracked modification can never be absorbed
    # by any "untracked set" wording.
    body = _norm(BACKUP_LANE)
    assert ("BASELINE, captured immediately after construction and "
            "BEFORE the brief is written") in body
    assert "A clone would have guaranteed this empty; a file copy does NOT" in body
    # identity: HEAD alone stops being sufficient once uncommitted work
    # can ride in, so the record carries path + HEAD + baseline
    assert ("The mirror's identity in the debate record is its path, its "
            "`git rev-parse HEAD`, AND its baseline") in body
    assert ("For a file copy HEAD alone does not identify the reviewed "
            "content") in body
    # a dirty tracked baseline means the reviewed content is not the
    # committed range - disclosed, and disallowed outright in mode diff
    assert ("in mode diff take the mirror from a tree whose tracked "
            "files are clean instead") in body


def test_backup_lane_eval_case_matches_the_mirror_contract():
    # 0.14.2 whole-branch review, Important 2: the manual eval case
    # declares backup-lane.md in its surface but still graded the
    # superseded clone contract. Manual cases never run in CI, so
    # nothing would have caught it until a future manual run failed
    # CORRECT mirror behavior.
    import json
    cases = json.loads(
        (REPO / "evals" / "multi-model-verify" / "evals.json").read_text(
            encoding="utf-8"))["evals"]
    case = next(c for c in cases
                if c["id"] == "backup-lane-consented-substitution")
    assert "skills/multi-model-verify/references/backup-lane.md" in case["surface"]
    joined = " ".join(case["expectations"])
    assert "review MIRROR (file copy preserving .git, not a clone)" in joined
    assert "baseline porcelain was captured before the brief was written" in joined
    assert "throwaway clone" not in joined


def test_backup_lane_client_config_sweep():
    # 0.14.2: the primary lane was hardened against instruction
    # back-channels (SKILL.md preflight 3) while the backup lane's own
    # client config was never swept. Both keys are recorded, neither
    # is a stop - and neither is observable from the route evidence.
    body = _norm(BACKUP_LANE)
    assert "## Client config surface" in body
    assert '`[models."<canonical-backup-model-id>".overrides]`' in body
    assert "runs at PROVIDER DEFAULT with no verifiable effort evidence" in body
    assert "`merge_all_available_skills`" in body
    assert ("the same class of instruction back-channel as codex's "
            "repo-level `.agents/skills` advertisement") in body
    assert "never a finding" in body
    assert "do not infer either key's value" in body
    # the key alone is not the surface - a true key over empty sources
    # merges nothing, so the check reads key AND sources together
    # (probed 2026-07-26: true key, every source absent = LATENT)
    assert "plus the SOURCES it merges from" in body
    assert "`extra_skill_dirs`" in body
    assert "a LATENT surface with nothing to merge, not an active one" in body
    # the populated-source case is honestly marked unprobed rather than
    # waved through on the tool allowlist
    assert ("treat a true key with a NON-EMPTY source as unprobed "
            "territory") in body


def test_skill_preflight_names_the_remediation():
    # 0.14.2: preflight 3 said STOP and never said how to clear it.
    # The tracked/ignored branch is the part that misreads as a bug:
    # deleting an IGNORED back-channel leaves HEAD untouched and
    # `nothing to commit`, which looks like a failed remediation and
    # is in fact the correct one (both observed 2026-07-26).
    skill = _norm(REPO / "skills" / "multi-model-verify" / "SKILL.md")
    assert "review mirror" in skill
    assert "empty output is the evidence" in skill
    assert ("a TRACKED entry's deletion shows as ` D` in "
            "`git status --porcelain`") in skill
    assert ("`nothing to commit` alongside an unchanged HEAD is the "
            "CORRECT observation there, not an inconsistency to chase"
            ) in skill


def test_output_encoding_class_is_wired():
    # 0.14.2, observed live 2026-07-26 (Windows, kimi-cli 1.49.0): the
    # round completed and UnicodeEncodeError killed the WRITE. The
    # catch-all would have spent a second real call on a retry that
    # cannot succeed, and the honest recovery (resume the surviving
    # session with UTF-8 forced) had no path in the rules at all.
    lane = _norm(BACKUP_LANE)
    assert "`PYTHONIOENCODING=utf-8` and `PYTHONUTF8=1`" in lane
    assert "AFTER the model has already answered" in lane
    # the unprobed part is marked, not papered over
    assert ("Which of the two variables is load-bearing, and whether the "
            "same guard is needed for kimi's own session-log write, is "
            "UNVERIFIED") in lane
    fb = _norm(FALLBACKS)
    assert "class `output-encoding`" in fb
    assert "**Skip the retry**" in fb
    # the resume's -p carries no rebuttal in recovery, but must not be
    # empty - say what to send (whole-branch review, Minor 2)
    assert ("ask the session to re-emit its previous reply verbatim" in fb)
    # the class must NOT be filed under the two evidence-tainting
    # classes - nothing reached disk, so nothing is suspect
    assert ("neither a route-attribution nor an integrity failure" in fb)
    assert ("Recovery is a RESUME of the surviving session" in fb)


def test_fallbacks_backup_wiring():
    fb = _norm(FALLBACKS)
    assert "[run backup lane (cross-vendor preserved)]" in fb
    # the integrity class names the mirror's declared-set rule, not a
    # bare "clone delta" (0.14.2 rename)
    assert ("integrity failure (write-probe fail, or a mirror delta "
            "beyond the expected untracked set)") in fb
    # the banner itself carries the conditional-offer semantics and the
    # backup option's own consequence line, not just an Options entry
    assert "offered when a class below qualifies it; on request otherwise" in fb
    assert "reviewer reasoning effort" in fb
    # transport-broken mapping names its member classes
    assert "codex-missing" in fb and "model-rejected" in fb
    assert "quota-exhausted" in fb and "auth-expired" in fb
    assert "route-attribution" in fb
    assert "LLM not set" in fb
    assert "access_terminated_error" in fb


def test_plan_format_lane_substitution_pin():
    fmt = _read(PLAN_FORMAT)
    assert "lane substitution is NOT degradation" in fmt
    assert "backup cross-vendor lane substituted" in fmt


def test_skill_and_readme_route_the_lane():
    skill = _read(REPO / "skills" / "multi-model-verify" / "SKILL.md")
    assert "backup-lane.md" in skill
    # BOTH dispatch sections (mode plan and mode diff) carry the pointer
    # - "backup-lane.md somewhere in the file" would let either mode
    # drop it while staying green
    assert skill.count("Backup lane: same protocol, transport and "
                       "per-round evidence per "
                       "references/backup-lane.md.") == 2
    readme = _read(REPO / "README.md")
    # the table row alone also contains "run backup lane" - pin the
    # mermaid edge exactly so the flowchart cannot drop it while green
    assert ('G -->|run backup lane| BK["cross-vendor backup reviewer'
            ) in readme
    assert ("references/backup-lane.md` | The cross-vendor backup "
            "reviewer lane") in readme


SWEEP_GLOBS = [
    "skills/**/*.md", "skills/**/*.yaml", "commands/*.md", "tools/*.ps1",
    "hooks/*", "evals/**/*.py", "evals/**/*.json", "evals/**/*.ps1",
    "README.md", "CLAUDE.md", "agents/*.md",
    ".claude-plugin/*.json", ".githooks/*",
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
