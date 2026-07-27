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
    # 0.14.2 Kimi panel round 1: this pin used to stop at `-p`, and the
    # brief pointer was covered only by a position-free filename check
    # that the workspace section also satisfies - so deleting the -p
    # PAYLOAD from the dispatch line left both green. The payload is
    # load-bearing (headless stdin does not carry the brief), so the
    # pin now runs through it, same treatment `-w` already had.
    assert ("kimi --quiet --thinking -m <canonical-backup-model-id> "
            "--agent-file <plugin-checkout>/skills/multi-model-verify/"
            "references/kimi-reviewer-agent.yaml -w <review-mirror> "
            '-p "Read the file KIMI-REVIEW-BRIEF.md in this workspace '
            'and execute the review it describes."'
            ) in body
    # the re-pinned resume is load-bearing: bare -r restores full tools,
    # model/thinking inherit from CONFIG DEFAULTS, and -w does not
    # inherit at all (a resume without it runs in the shell's cwd -
    # caught live against the real tree).
    # 0.14.2 Kimi panel round 2: this pin stopped at -w while its own
    # comment claimed it covered the COMPLETE command - asserting
    # completeness over a command it truncated. The resume payload is
    # the same load-bearing class as the dispatch payload (headless
    # stdin carries nothing), so the pin now runs through it.
    assert ("kimi --quiet -r <session-id> --agent-file <same yaml> -m "
            "<canonical-backup-model-id> --thinking -w <same mirror> "
            '-p "<rebuttal>"') in body
    assert "loads the DEFAULT agent with full write and shell tools" in body
    assert BACKUP_ID not in body  # placeholder discipline


def test_backup_lane_evidence_pins():
    # normalized: these pins now span markdown wraps, and a re-wrap is
    # not a semantic change (same reasoning as the write-probe pin)
    body = _norm(BACKUP_LANE)
    # 0.14.2 Kimi panel round 3 (instance 7, the worst of the class):
    # the rule has two halves - capture the offset, then require the
    # three lines PAST IT. Only the capture half was pinned, and
    # "past that offset" appeared in no file under evals/ at all.
    # Deleting it left every pin green while the check stopped
    # attributing anything: kimi.log is a shared append stream, so
    # without the offset the three lines can be satisfied by an earlier
    # debate's entries - the exact route-attribution failure this rule
    # exists to prevent.
    assert ("capture the byte length of `~/.kimi/logs/kimi.log`; after "
            "the call, past that offset") in body
    assert ("exactly one new `Using LLM model:` line carrying the "
            "canonical backup id") in body
    assert "`Loading agent:` line naming the committed yaml" in body
    assert "`Loaded tools:` line equal to the allowlist exactly" in body
    assert "DISCARDED unread" in body
    # 0.14.3: the offset rule assumes an append-only file and kimi's
    # client does not guarantee one. Rotation currently FAILS on
    # Windows (WinError 32, log still open), so offsets have held by
    # accident - if rotation ever succeeds, every byte position from
    # the earlier measurement is meaningless and the check would read
    # whatever happens to sit there.
    assert ("Rotation guard" in body)
    assert ("if after the call the file is SMALLER than the captured "
            "offset, or absent") in body
    # re-reading the rotated file from zero is the tempting wrong
    # answer: it attributes lines that may belong to any session
    assert ("not a reason to re-read from zero" in body)
    assert ("offsets have held by accident rather than by design" in body)
    # 0.14.3 fable review F1: DETECTION without a DISPOSITION leaves the
    # driver to invent a rule. The nearby "DISCARDED unread" pin above is
    # satisfied by the pre-existing bullet, so the guard's consequence
    # half needs its own pin or it deletes green - pin-integrity instance
    # ten in this file.
    assert ("That is a route-attribution failure" in body)
    # F4: the residual gap's CONTINGENCY is the only recorded instruction
    # for the day rotation starts succeeding.
    assert ("compare file identity (creation time) too, not just length"
            in body)
    # 0.14.3 Sol panel round 1 (claim 6), REVERSING the session's earlier
    # call that this paragraph was narrative and not worth pinning. It is
    # not narrative: it states that the detection check has a known
    # FALSE-NEGATIVE boundary, and a driver who reads only the detection
    # rule over-trusts the guard. What a driver believes about coverage
    # is contract.
    assert ("The size test is necessary, not sufficient: a rotation "
            "whose replacement file grew back PAST the captured offset "
            "within the same call would slip through.") in body
    # 0.14.2 Kimi panel round 2 (4b): the three PASS conditions were
    # pinned but the probe's CONFIGURATION FIDELITY was not - a probe
    # run under a stricter config than the debate's would pass while
    # the real debate config could still write. That is a silent
    # weakening in the dangerous direction, so the clause is pinned.
    # normalized, not raw: a pure re-wrap of this bullet is not a
    # semantic change and should not false-red the pin
    assert ("in a fresh disposable session with the exact debate "
            "configuration") in body
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
    # 0.14.2 Sol round 1, F2/F5: bare porcelain OMITS ignored paths and
    # COLLAPSES untracked directories, and ignored content is the whole
    # reason this workspace is a mirror - so the flags are the check,
    # not decoration. Probed: bare printed only "?? untr/".
    assert "`git status --porcelain --ignored -uall`, every" in body
    assert ("bare `git status --porcelain` OMITS ignored paths entirely "
            "and COLLAPSES an untracked directory to a single entry") in body
    assert ("a contained reviewer writing to any ignored path would not "
            "appear") in body
    # F4: HEAD binds tracked content only, and this lane's inputs are
    # deliberately outside it - so identity carries a content manifest
    # 0.14.2 Sol round 2, F4 held at FIX: naming a manifest is not
    # specifying one. The pin must constrain coverage, recursion,
    # ordering, and capture point - otherwise "content manifest" as a
    # phrase satisfies it while a driver cannot execute it.
    assert "AND a CONTENT MANIFEST" in body
    # 0.14.2 Sol round 3: the mirror preserves .git by design and HEAD
    # represents none of it, so the coverage test literally swept
    # repository metadata - objects, logs, index, hooks. The universe
    # must exclude .git, as a file OR a directory (worktree/submodule
    # checkouts make it a file).
    assert ("excluding the root git administrative entry `.git` entirely"
            in body)
    assert ("it may be a directory or, in a worktree or submodule "
            "checkout, a file — exclude it either way") in body
    # coverage is git's own reckoning, not a raw-byte comparison:
    # found by EXECUTING this contract 2026-07-26 - with
    # core.autocrlf=true a file git calls clean is not byte-identical
    # to its blob, and the byte rule ballooned to 283/287 files against
    # a 122-entry baseline
    assert ("Coverage within that universe is exactly the paths the "
            "BASELINE capture lists") in body
    assert ('Do NOT define coverage as "bytes differ from the HEAD blob"'
            in body)
    assert ("git applies clean/smudge filters" in body)
    # the classes an enumerated list would have dropped
    assert ("inherited untracked files whether ignored or not" in body)
    assert ("any tracked file modified relative to HEAD" in body)
    # recursion, format, order, timing
    assert "Directories expand RECURSIVELY to their files" in body
    # 0.14.2 Sol round 5: coverage said "exactly the baseline paths" and
    # the format said "SHA-256 of the file's raw bytes" - but a ` D`
    # entry is a path with NO file, and a rename entry is two paths.
    # Both left the driver inventing a rule, in a section whose whole
    # claim is that no judgment remains. (Cross-lane split: the other
    # lane saw this and rated it readability; adjudicated to Sol - an
    # undefined action on a real entry shape is an executability gap.)
    assert ("Two baseline entry shapes are not hashable as written, and "
            "each has a defined action") in body
    assert ("**Deletion-only entries** (` D` / `D `): OMIT them" in body)
    assert ("HEAD plus the baseline already bind the absence" in body)
    # instance 9, on text added two commits earlier: this pin stopped at
    # the destination rule, leaving the source half unpinned - and an
    # `R` source is not literally a ` D` entry, so without that sentence
    # a driver has a defined action for `new` and an invented one for
    # `old`. The class applies to new text the day it lands.
    assert ("**Rename or copy entries** (`R`/`C`, `old -> new`): hash "
            "the CURRENT DESTINATION path. The source path is a "
            "deletion and falls under the rule above.") in body
    # separator and encoding are pinned too: without them two captures
    # are equivalent but not byte-comparable
    assert ("the repo-relative path, a single space, then the SHA-256 of "
            "the file's raw bytes as lowercase hex") in body
    assert "sorted by path in byte order" in body
    assert ("Captured at the same moment as the baseline" in body)
    # F8: absence of an override pin proves neither an override nor
    # provider-default; the record must not manufacture either
    assert ("Record a round with no contemporaneous config evidence as "
            "having NO VERIFIED EFFORT PIN") in body
    assert ("establishes neither an override nor provider-default "
            "operation") in body
    assert "is a gap in the review, not a silent omission" in body


def test_mirror_baseline_closes_the_dirty_tree_hole():
    # 0.14.2 whole-branch review, Important 1: a clone guaranteed an
    # empty porcelain; a file copy does not. Without a baseline, the
    # real tree's untracked files and uncommitted modifications ride
    # into the mirror and quarantine every round of a review that never
    # touched them - and a tracked modification can never be absorbed
    # by any "untracked set" wording.
    body = _norm(BACKUP_LANE)
    # timing is load-bearing and was WRONG in the first fix pass:
    # preflight-3 remediation runs between construction and the brief,
    # deleting entries and (tracked case) committing - so a baseline
    # taken at construction fails every round of a remediated debate
    # and pins a stale HEAD, reintroducing the false-quarantine on the
    # one path the mirror exists to support
    assert ("BASELINE, captured after construction AND after any "
            "preflight-3 remediation, immediately before the brief is "
            "written") in body
    assert ("a baseline taken before it fails every round of a "
            "remediated debate and pins a HEAD the mirror no longer "
            "has") in body
    assert "A clone would have guaranteed this empty; a file copy does NOT" in body
    # the check's reach is stated honestly rather than implied broader
    # reach is stated against the FLAGGED command: it sees appearance
    # and disappearance of any path including ignored ones, and is
    # honest that content changes to an already-present path are the
    # residue the allowlist, write-probe, and manifest cover
    assert ("it detects any path that APPEARS IN OR DISAPPEARS FROM the "
            "mirror, ignored and untracked paths included") in body
    assert ("It remains PATH-level, so a path already present in the "
            "baseline shows the same entry however its CONTENT changes") in body
    # identity: HEAD alone stops being sufficient once uncommitted work
    # can ride in, so the record carries path + HEAD + baseline
    assert ("The mirror's identity in the debate record is its path, its "
            "`git rev-parse HEAD`, its baseline, AND a CONTENT MANIFEST") in body
    assert ("HEAD binds tracked content only, and in this lane the inputs "
            "that matter are deliberately outside it") in body
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
    # 0.14.2 Sol round 1, F10a: the pin above checks only the mirror
    # VOCABULARY, so deleting the equality half of the expectation left
    # it green - the half that actually grades containment. Pin it.
    assert ("equals that baseline plus exactly KIMI-REVIEW-BRIEF.md and "
            "any enumerated copied-in review inputs") in joined


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
    # instance 8, same shape at lower severity: the comment claims both
    # keys are RECORDED, but only the disposition half was pinned.
    # Dropping "and RECORDED" leaves a driver reading the keys and
    # discarding them, which defeats the section's own justification -
    # the check is what makes the effort claim true rather than assumed,
    # and that only holds if the read reaches the record.
    assert "read and RECORDED in the debate record" in body
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
    # 0.14.2 Sol round 1, F10b: the assertions above pin the OBSERVATIONS
    # but never the imperative, so deleting "commit the removal inside
    # the mirror" left the pin green - and that commit is the whole
    # point of the tracked branch. Pin the imperative and the
    # consequence that justifies it.
    assert "so commit the removal inside the mirror" in skill
    assert ("bars mode diff and breaks HEAD-identifies-content" in skill)


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
    # 0.14.3 fable review F3: the class's stated no-retry rationale is
    # "nothing transient", which is true of a wrong id or a stray tool but
    # NOT of a rotation under the call - that one would yield clean
    # evidence on a re-dispatch. The disposition is still right, for a
    # different reason, and the reason has to be on the record or the two
    # files read as a contradiction.
    # 0.14.3 Sol panel round 1 (claim 5): the pin below MUST run to the
    # end of the justification. Stopping at "IS transient" named the
    # exception while leaving the operative half - WHY the retry is still
    # skipped, and WHO decides the re-spend - deletable green. That is
    # pin-integrity instance eleven, reproduced inside the very sentence
    # added this cycle to fix instance ten.
    assert ("a rotation under the call is the one member that IS "
            "transient — a re-dispatch with a freshly captured offset "
            "would produce clean evidence. It still skips the retry, "
            "because the round already spent is unattributable and no "
            "retry can make it attributable after the fact; the user "
            "decides at the gate whether to spend another.") in fb
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


# `docs/**` is DELIBERATELY out of scope and must stay that way. The
# requirement this sweep enforces is placeholder discipline on DISPATCH
# surfaces - the files an agent reads to build a command. docs/ holds
# design specs, plans, and retained round evidence that legitimately
# QUOTE model ids as historical record (92 occurrences across 20 files
# as of 63fa715); sweeping
# them would manufacture false reds, and the predictable response to a
# perpetually red test is to weaken it. Raised and correctly declined
# during the 0.14.2 panel; recorded here so it is not re-litigated.
# (Note: docs/superpowers/plans/2026-07-25-kimi-backup-lane.md claims the
# literal appears ONLY in notes.md and this file. That was true of
# operational surfaces when written and is false of docs/ itself - left
# as-is, being a historical record of what was planned, not a live rule.)
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
