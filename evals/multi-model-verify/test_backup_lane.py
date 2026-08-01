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
AGENT_MD = REFS / "kimi-reviewer-agent.md"
NOTES = REFS / "model-prompting-notes.md"
FALLBACKS = REFS / "fallbacks.md"
PLAN_FORMAT = REFS / "frozen-plan-format.md"
BACKUP_ID = "kimi-code/k3-256k"
ALLOWLIST = ["Read", "Grep", "Glob", "ReadMediaFile", "TodoList"]
DENYLIST = ["Bash", "Write", "Edit", "WebSearch", "FetchURL",
            "EnterPlanMode", "ExitPlanMode", "Agent", "AgentSwarm",
            "AskUserQuestion", "Skill", "TaskList", "TaskOutput",
            "TaskStop", "CronCreate", "CronList", "CronDelete"]
# Every built-in tool documented for 0.31.1, written out INDEPENDENTLY of
# the two lists above. r3 defined this as their union and then compared the
# union back to it, which is a tautology that detects neither a swapped
# name nor an omission.
#
# Accepted limit, stated plainly because r4 caught the earlier wording
# overclaiming: NOTHING here detects a tool a future client adds. The
# floor check is a LOWER BOUND - it rejects releases below 0.31.1 and
# accepts every newer one, so it does not force a re-probe at upgrade.
# Re-probing the inventory is a manual step at any deliberate version
# bump, and the drift snapshot's recorded version is what makes such a
# bump visible.
KNOWN_TOOLS = {
    "Read", "Write", "Edit", "Grep", "Glob", "ReadMediaFile", "Bash",
    "WebSearch", "FetchURL", "EnterPlanMode", "ExitPlanMode", "TodoList",
    "Agent", "AgentSwarm", "AskUserQuestion", "Skill", "TaskList",
    "TaskOutput", "TaskStop", "CronCreate", "CronList", "CronDelete",
}


def _read(p):
    return p.read_text(encoding="utf-8")


def _norm(p):
    """Whitespace-normalized read, for pins that span a markdown wrap."""
    return " ".join(_read(p).split())


def test_backup_artifacts_exist():
    for p in (BACKUP_LANE, AGENT_MD):
        assert p.is_file(), str(p)
    assert not (REFS / "kimi-reviewer-agent.yaml").exists()
    assert not (REFS / "kimi-reviewer-system.md").exists()


def test_notes_backup_declarations():
    notes = _read(NOTES)
    assert "Canonical backup reviewer model id: `" + BACKUP_ID + "`" in notes
    assert "Canonical backup provider: `kimi`" in notes
    assert "Canonical backup reasoning effort: `high`" in notes
    assert ("Canonical backup thinking declaration: `[thinking] enabled = true`"
            in notes)
    assert "Canonical backup thinking flag: `--thinking`" not in notes
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


def test_agent_allowlist_and_denylist_exact():
    """Exact LIST equality. Omitting `tools:` means ALL tools on this
    client, so a silent parse failure is PERMISSIVE - hence the denylist
    as well."""
    import re
    body = _read(AGENT_MD)
    tools = re.search(r"^tools:\n((?:  - \w+\n)+)", body, re.M)
    assert tools
    assert [t.strip("- ").strip()
            for t in tools.group(1).strip().splitlines()] == ALLOWLIST
    denied = re.search(r"^disallowedTools:\n((?:  - \w+\n)+)", body, re.M)
    assert denied
    assert [t.strip("- ").strip()
            for t in denied.group(1).strip().splitlines()] == DENYLIST


def test_the_two_lists_partition_the_known_inventory():
    """Set equality, not a count. r2 asserted len(A)+len(B)==22, which
    stayed green if a real name were swapped for a nonexistent one.

    Accepted limit, stated so it stays deliberate: this cannot see a tool
    a FUTURE client adds, and nothing offline can. The floor is a LOWER
    bound and accepts every newer release, so it does not force a
    re-probe either - re-probing is a manual step at a deliberate version
    bump, made visible by the drift snapshot's recorded version."""
    assert not (set(ALLOWLIST) & set(DENYLIST))
    assert set(ALLOWLIST) | set(DENYLIST) == KNOWN_TOOLS


def test_agent_empties_the_subagent_list():
    """Measured: `subagents` defaults to ALL, including `coder`. That was
    inert only because Agent and AgentSwarm are denied, and the
    coincidence of two controls is not a control."""
    assert "subagents: []" in _read(AGENT_MD)


def test_backup_files_no_backslash_paths():
    for p in (BACKUP_LANE, AGENT_MD):
        assert "\\" not in _read(p), str(p)


def test_backup_lane_dispatch_and_resume_pins():
    # normalized: the prose pins below span markdown wraps, and the
    # command lines carry single spaces either way
    body = _norm(BACKUP_LANE)
    # The dispatch pin covers the COMPLETE command through the -p
    # payload. Both halves of that reach are load-bearing history: a
    # dropped workspace argument used to dispatch the reviewer in the
    # shell's cwd (0.13.0 final review), and 0.14.2 Kimi panel round 1
    # found the pin stopping short of the payload while the payload was
    # covered only by a position-free filename check the workspace
    # section also satisfied - so deleting it left both green.
    #
    # kimi-code takes no workspace flag at all: the session binds to the
    # directory it was created in, and the client enforces it. So the
    # placeholder that must not be dropped here is `--agent-file`, which
    # is the only call in a debate that can carry it.
    assert ("<kimi-code-binary> -m <canonical-backup-model-id> "
            "--agent-file <plugin-checkout>/skills/multi-model-verify/"
            "references/kimi-reviewer-agent.md --skills-dir "
            '<debate-home>/skills -p "<the whole brief>"') in body
    # The resume pin runs through its own payload for the same reason.
    # `--agent-file` is absent from it because the client REJECTS it with
    # --session; see test_resume_inheritance_region for the measurement.
    assert ("<kimi-code-binary> --session <session-id> -m "
            "<canonical-backup-model-id> --skills-dir <debate-home>/"
            'skills -p "<rebuttal>"') in body
    # The command lines and the absolute-path instruction have to agree,
    # or the pin says one thing and the prose another.
    assert ("`<kimi-code-binary>` is the client's ABSOLUTE path" in body)
    # The brief travels INLINE. This is what makes the brief hash
    # meaningful - a pointer's hash proves the pointer arrived.
    assert ("**The brief is passed INLINE**, in the dispatch's own `-p` "
            "payload") in body
    assert ("A brief that exceeds what the inline transport carries is a "
            "TRANSPORT FAILURE to diagnose, not a reason to switch to a "
            "pointer.") in body
    assert BACKUP_ID not in body  # placeholder discipline


def test_lane_home_isolation_region():
    """The home is the lane's isolation boundary, and it is one call away
    from not existing at all.

    Two independent reasons are pinned together on purpose: a pin holding
    only the hook reason would let the evidence reason be deleted, and a
    home built for evidence alone would read as optional on a machine
    whose real config carries no hooks. The removal half is pinned too -
    the home holds a COPIED CREDENTIAL, so leaving it behind is not
    untidiness."""
    assert (
            "Build the lane home ONCE, before round 1, with "
            "`tools/new-kimi-lane-home.ps1 -Path <debate-home> -Model "
            "<canonical-backup-model-id> -Effort "
            "<canonical-backup-effort>`, and set "
            "`KIMI_CODE_HOME=<debate-home>` on EVERY call of that debate, "
            "fresh and resumed alike. Two INDEPENDENT reasons, either one "
            "sufficient on its own: the real user-global "
            "`~/.kimi-code/config.toml` can carry lifecycle hooks that run "
            "a shell command on the reviewer's own approval path, and the "
            "home is where this lane's effort pin and this debate's session "
            "evidence live. One debate is ONE home: that debate's ROUNDS "
            "are one session, and the only other session the home may hold "
            "is the write-probe's own disposable one, which is created "
            "before round 1 and is therefore already in the inventory the "
            "freshness rule captures. A home is never reused across "
            "DEBATES, because a reused home carries another debate's "
            "sessions into this one's evidence. A home that cannot be "
            "built, or a missing credential, makes the lane UNAVAILABLE — "
            "never a reason to dispatch from the real home. Remove the home "
            "with `tools/new-kimi-lane-home.ps1 -Path <debate-home> "
            "-Remove` when the debate ends, because it holds a copied "
            "credential.") in _norm(BACKUP_LANE)


def test_resume_inheritance_region():
    """The measured inheritance surface, stated at exactly its width.

    This region REPLACES the old lane's most dangerous rule (a bare `-r`
    silently restored the default agent with write and shell tools, and a
    resume without `-w` once landed in the REAL tree). Both halves
    inverted on this client, so the pin has to carry the new facts AND
    their bound: four flags were tested, three are accepted, one is
    rejected because the agent binds at session creation, and nothing is
    established about any flag outside that set. The version-bound
    sentence is inside the pin because it is what stops the measurement
    being read as permanent."""
    assert (
            "Measured on kimi-code 0.31.1: from the correct working "
            "directory, a bare resume carrying no `-m`, no `--agent-file` "
            "and no `--skills-dir` reproduced round 1's model alias, effort "
            "and tool count, and BOTH its `toolsHash` and its "
            "`systemPromptHash` byte for byte. A resume from the WRONG "
            "directory is REFUSED by the client before anything is "
            "dispatched, so a resume can no longer land in the real tree by "
            "omission. `--agent-file` is REJECTED with `--session` — the "
            "agent is bound at session creation — so it cannot be re-pinned "
            "at all; of the four flags tested, `-m`, `--skills-dir` and "
            "`--add-dir` are accepted, and the two the lane uses are "
            "re-pinned on every resumed call because it is free and it "
            "narrows the inheritance risk to the one flag that cannot be "
            "re-pinned. Nothing is established about any flag outside that "
            "tested set. All of this is VERSION-BOUND, which is why the "
            "drift floor exists, why what can be re-pinned is re-pinned, "
            "and why the per-round evidence below — not this paragraph — is "
            "what establishes the surface actually in force each round.") in _norm(BACKUP_LANE)


def test_round_freshness_boundary_region():
    """The surviving half of the deleted offset rule.

    The files are per-session now, so nothing needs attributing - but
    they are still CUMULATIVE, so a call still needs a boundary. Length
    alone is not that boundary: a file replaced, truncated and regrown
    passes it, which is why both files carry a prefix hash. The fresh
    branch is pinned in the same region because it is the case with no
    offset to capture at all, and the leaf-versus-container sentence is
    pinned because counting directories rejects a CLEAN first call - a
    false red in the one place the lane cannot afford one."""
    assert (
            "Both files are CUMULATIVE, so each call is read as a SLICE of "
            "them. Before every call capture, for BOTH the wire transcript "
            "and the per-session log, the file's BYTE length and a SHA-256 "
            "over exactly those bytes; after the call read only past those "
            "byte offsets, and require both prefix hashes unchanged. A file "
            "shorter than its offset, or absent, or whose prefix hash "
            "changed, was replaced: that is a route-attribution failure, "
            "and specifically NOT a reason to re-read from zero, because "
            "the replacement's opening records may belong to anything. Byte "
            "offsets and a hash over raw bytes are what make the boundary "
            "unambiguous, and hashing BOTH files is what makes the check "
            "prove IDENTITY rather than length — length alone passes a file "
            "that was replaced, truncated and regrown. A FRESH call has no "
            "offsets to capture, because its session does not exist until "
            "the client creates it; what is captured before a fresh "
            "dispatch is the session INVENTORY, and exactly one new SESSION "
            "LEAF must appear afterwards, matching the session id the "
            "client printed. A leaf is a directory whose name begins "
            "`session_`. Counting directories rather than leaves is wrong "
            "and would reject a clean first call: the measured layout nests "
            "leaves inside a `wd_`-prefixed workspace container, and a "
            "debate's first call in a workspace creates the container as "
            "well as the session. The slice must also BEGIN at a call "
            "boundary — the record `metadata` for a fresh call, "
            "`turn.prompt` for a resume, both measured — because an offset "
            "landing mid-call yields a slice mixing the previous call's "
            "trailing records with this one's while satisfying every count "
            "and value check.") in _norm(BACKUP_LANE)


def test_per_round_session_evidence_region():
    """Two record classes, because one rule was measured to fail both.

    Revision 2 of this contract required "exactly one of each" across
    every slice. Measured, that fails a clean round 1 (`config.update` is
    2, `llm.request` is 4) and every resumed round (three of the four
    records do not appear in a resume's slice at all). So the split is
    the rule, and the ABSENCE requirement on a resume is what now catches
    a resume that silently started a new session - the check the deleted
    `Created new session:` line used to carry.

    This region also names the replacement for the dead `Loaded tools:`
    grep: an exact-list comparison against the committed agent file. That
    grep is the check backlog item 13 opened this cycle to remove,
    because it could match nothing and still read as clean."""
    assert (
            "The records fall into TWO CLASSES and one rule cannot cover "
            "both: a rule that assumed it could was measured to fail a "
            "clean round 1 and every resumed round. SESSION-SCOPED records "
            "— `config.update` twice, `tools.set_active_tools`, "
            "`llm.tools_snapshot` and `permission.set_mode` once each — "
            "appear ONLY in the session-creating call's slice. Require them "
            "there, checking the agent profile name, the system prompt, the "
            "model alias, the effort, the permission mode, and the "
            "configured allowlist, denylist and resolved tool snapshot by "
            "EXACT LIST EQUALITY against the committed agent file; and "
            "require their ABSENCE from a resume's slice, because their "
            "presence there means the resume silently started a new session "
            "and lost the reviewer's debate state. PER-CALL records appear "
            "in every slice: exactly one `turn.prompt`, one or more "
            "`llm.request` with EVERY one carrying the canonical provider, "
            "model and effort, and exactly one new `llm config` log line "
            "carrying those plus `toolCount` and `systemPromptChars`. "
            "`llm.request` tracks the tool loop, so it is bounded from "
            "below and never fixed. Run "
            "`tools/read-kimi-round-evidence.ps1` in its FRESH form for the "
            "session-creating call, passing the pre-dispatch session "
            "inventory and the session id the client printed, and in its "
            "RESUME form for every later call, passing the previous call's "
            "returned state. Require `status: clean`: a missing directory, "
            "a missing or miscounted record, an unreadable file, a "
            "malformed line, or any inequality is a route-attribution "
            "failure, the reply is DISCARDED unread, and the failure goes "
            "to the fallbacks.md consent gate.") in _norm(BACKUP_LANE)


def test_evidence_hash_continuity_region():
    """Recording the two hashes is the whole mechanism.

    Neither is pinned to a literal here on purpose - they cover tool
    schemas a client release may reword, and a committed literal would
    red every round for a reason that is not a route problem. That makes
    RECORDING them the only thing standing between a client upgrade and a
    silent rebaseline at the next round 1, so the pin carries the
    justification as well as the instruction."""
    assert (
            "Record round 1's `toolsHash` and `systemPromptHash` IN THE "
            "DEBATE RECORD and carry them forward: the validator itself "
            "requires every later round to match them, rather than leaving "
            "the comparison to a driver who might never make it. They are "
            "deliberately NOT pinned to a literal in this repo, because "
            "they cover tool schemas any client release may reword, and a "
            "committed literal would fail every round for a reason that is "
            "not a route problem. Recording them is what makes a client "
            "upgrade's change VISIBLE in the record instead of silently "
            "rebaselined at the next round 1.") in _norm(BACKUP_LANE)


def test_brief_hash_binding_region():
    """The canonicalization is part of the rule, not an implementation
    detail.

    The measured evidence matched only after CRLF was normalized to LF,
    so a contract saying merely that the brief and the recorded prompt
    "hash to the same value" leaves a driver to invent the step that
    makes it true. The concatenation over every `input[]` element is
    pinned for the same reason: hashing only the first element is the
    obvious wrong reading."""
    assert (
            "Hash the brief BEFORE dispatch and require the recorded prompt "
            "to match: SHA-256 over the brief canonicalized as UTF-8 with "
            "CRLF normalized to LF, compared against the same hash of the "
            "concatenation of every `turn.prompt` `input[]` element's "
            "`text` field. The canonicalization is part of the rule rather "
            "than an implementation detail: the measured evidence matched "
            "only after newline normalization, so a rule saying merely that "
            "the two hash to the same value leaves a driver to invent that "
            "step.") in _norm(BACKUP_LANE)


def test_backup_lane_containment_and_probe_pins():
    """The containment controls, and the two checks that verify them.

    0.14.2 Kimi panel round 2 (4b): the write-probe's three PASS
    conditions were pinned but its CONFIGURATION FIDELITY was not - a
    probe run under a stricter config than the debate's would pass while
    the real debate config could still write. Normalized, not raw: a pure
    re-wrap of the bullet is not a semantic change.

    The three-control sentence is pinned because two of the three used to
    be a coincidence rather than a control: measured, the subagent list
    defaulted to ALL profiles and was inert only because `Agent` and
    `AgentSwarm` happened to be denied.
    """
    body = _norm(BACKUP_LANE)
    assert ("The committed `kimi-reviewer-agent.md` (this directory) is "
            "the ONLY agent configuration the lane dispatches with, and "
            "it carries THREE controls rather than one.") in body
    assert ("Each is a control in its own right rather than a coincidence "
            "of two lists") in body
    # Fix round 1: this sentence used to say the three lists are verified
    # "per round by the exact-list comparison". They are not. Rule 12 of
    # tools/read-kimi-round-evidence.ps1 is FRESH-ONLY - every
    # Compare-Object sits inside `if ($Fresh)`, because a resume's slice
    # carries none of those records - so the claim was wider than any
    # round's evidence, which is the exact defect class (a check reading
    # clean without measuring) that retiring the `Loaded tools:` grep was
    # meant to remove. A resumed round IS covered, by toolCount equality
    # and by toolsHash/systemPromptHash continuity; the pin now runs
    # through BOTH reaches and through the sentence that refuses to
    # conflate them, so neither half can be dropped or widened.
    assert ("the SESSION-CREATING call's slice compares the configured "
            "allowlist, the denylist and the resolved tool snapshot "
            "against this file by EXACT LIST EQUALITY, while a RESUMED "
            "call — whose slice carries none of those records at all — "
            "is covered instead by `toolCount` equality against this "
            "file's allowlist length and by `toolsHash` and "
            "`systemPromptHash` continuity with the call that was "
            "compared.") in body
    assert ("Both are real checks; only the first is an exact-list "
            "comparison, and saying otherwise would claim a reach no "
            "round has.") in body
    assert ("in a fresh disposable session with the exact debate "
            "configuration") in body
    assert ("explicit refusal in the reply, marker absent on disk, "
            "mirror status delta empty") in body
    # `kimi export` still exists on 0.31.1 (`kimi export [sessionId]`,
    # read from the client's own help), so the warning is retargeted
    # rather than deleted - and it now names what the archive carries,
    # because the default bundles the global diagnostic log too.
    assert "Never run `kimi export` inside a repo" in body
    assert ("by default it bundles the global diagnostic log into it as "
            "well") in body


def test_deleted_machinery_does_not_return():
    """Restoration guards for the machinery the kimi-code swap deleted.

    Stated plainly, because it is easy to mistake this for coverage:
    every assertion here is an ABSENCE check, and an absence check LOCKS
    NOTHING under the pin grammar in CLAUDE.md. The contract-coverage
    checker will never read one as covering a region, and it is not
    meant to. These are restoration guards - they fail if deleted
    machinery is written back into the contract - and they are kept
    deliberately for that and nothing else.

    Each name below lost its subject rather than its wording. kimi-code
    writes a per-session wire transcript and a per-session log, so there
    is no shared append stream to serialize against
    (`tools/kimi-lane-lock.ps1`), no rotation of a user-global log to
    guard (`Rotation guard`), and no session-startup line to bind
    evidence to by order (`Created new session:`). Restoring any of them
    would mean restoring a rule that no longer describes this client.
    """
    body = _norm(BACKUP_LANE)
    assert "kimi-lane-lock.ps1" not in body
    assert "Rotation guard" not in body
    assert "Created new session:" not in body


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
    # unexpected delta still quarantines.
    # kimi-code swap: the brief LEFT this set. It is passed inline and
    # never lands in the mirror, so the expected set is now the copied-in
    # inputs alone - and on a debate that copies nothing in, the baseline
    # exactly. The pin runs through that sentence because "baseline plus
    # nothing" is the case a driver would otherwise read as a broken
    # capture and start hunting for a missing file.
    assert ("must equal the BASELINE plus exactly the expected untracked "
            "set — the enumerated review inputs copied in before the "
            "round, and nothing else — so a debate that copies nothing "
            "in expects the BASELINE EXACTLY.") in body
    assert ("The brief is not in that set, because the brief is passed "
            "inline and never lands in the mirror.") in body
    # 0.14.2 Sol round 1, F2/F5: bare porcelain OMITS ignored paths and
    # COLLAPSES untracked directories, and ignored content is the whole
    # reason this workspace is a mirror - so the flags are the check,
    # not decoration. Probed: bare printed only "?? untr/".
    assert ("`git -c core.quotepath=false status --porcelain --ignored "
            "-uall`, every") in body
    assert ("git's default renders a non-ASCII pathname as a quoted "
            "display form carrying octal escapes, while the mirror's "
            "recorded baseline carries the same pathname raw") in body
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
    assert ("**Rename or copy entries** (`R`/`C`, recorded as "
            "`old -> new`): hash the CURRENT DESTINATION path. The "
            "source path is a deletion and falls under the rule "
            "above.") in body
    # The wire order is the opposite of the recorded order, so the
    # sentence that says so is pinned in its own right: a driver reading
    # only the display form would build a parser that hashes the source.
    assert ("the `-z` capture the mirror script reads emits the two "
            "pathnames in the opposite order, destination first") in body
    # separator and encoding are pinned too: without them two captures
    # are equivalent but not byte-comparable
    assert ("the repo-relative path, a single space, then the SHA-256 of "
            "the file's raw bytes as lowercase hex") in body
    assert "sorted by path in byte order" in body
    assert ("Captured at the same moment as the baseline" in body)
    # 0.14.2 F8's two effort pins used to sit here ("NO VERIFIED EFFORT
    # PIN", "establishes neither an override nor provider-default
    # operation"). Their subject was a USER-GLOBAL config read after the
    # fact, which this lane no longer has: effort is written into the
    # debate home and read back out of the round's OWN evidence, so a
    # round can never lack contemporaneous effort evidence and still be
    # clean. The reasoning they recorded - absence of evidence is not
    # evidence of a value, and writing one in manufactures a fact the
    # lane never observed - is repointed onto the measurement in
    # test_backup_lane_client_config_sweep rather than dropped.
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
    # preflight-3 remediation runs between construction and the round,
    # deleting entries and (tracked case) committing - so a baseline
    # taken at construction fails every round of a remediated debate
    # and pins a stale HEAD, reintroducing the false-quarantine on the
    # one path the mirror exists to support.
    # kimi-code swap, fix round 1: the END of that window used to be "the
    # brief is written", which was a real event only while the brief was
    # planted in the mirror. It is passed inline now, so that wording
    # named a moment that never arrives - the timing rule pointed at
    # nothing while reading unchanged. The window now closes at the
    # dispatch, which is the event that could actually change the tree.
    assert ("BASELINE, captured after construction AND after any "
            "preflight-3 remediation, immediately before the first round "
            "is dispatched") in body
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
    assert "baseline porcelain was captured before the round" in joined
    assert "throwaway clone" not in joined
    # 0.14.2 Sol round 1, F10a: the pin above checks only the mirror
    # VOCABULARY, so deleting the equality half of the expectation left
    # it green - the half that actually grades containment. Pin it.
    # kimi-code swap: the equality half survives, minus the planted brief
    # file. The brief is passed inline now, so a graded run that finds it
    # in the mirror is a CONTRACT VIOLATION rather than the expected
    # state - which is why this pin is repointed instead of relaxed.
    assert ("equals that baseline plus exactly the enumerated copied-in "
            "review inputs, and the baseline exactly when none were "
            "copied in") in joined
    # the case must not go on grading the superseded transport either:
    # the agent yaml, the workspace flag, the thinking flag and the
    # `Loaded tools:` grep are all gone from the contract it declares as
    # its surface, and a manual case never runs in CI to say so.
    assert "kimi-reviewer-agent.yaml" not in joined
    assert "KIMI-REVIEW-BRIEF.md" not in joined
    assert "Loaded tools:" not in joined


def test_backup_lane_client_config_sweep():
    # 0.14.2: the primary lane was hardened against instruction
    # back-channels (SKILL.md preflight 3) while the backup lane's own
    # client config was never swept. Both keys are recorded, neither
    # is a stop.
    #
    # kimi-code swap: every pin below is REPOINTED, not dropped. The
    # config being swept is the DEBATE HOME's now, because the lane no
    # longer runs out of the user-global one - so the class of concern is
    # identical and the sweep has to move with it. Dropping it would
    # leave this lane's own client config unswept, which is exactly what
    # 0.14.2 added it to fix.
    body = _norm(BACKUP_LANE)
    assert "## Client config surface" in body
    # The effort pin moves from the old client's `[models.<id>.overrides]`
    # block to the home's `default_effort`, and its DISPOSITION inverts:
    # "runs at PROVIDER DEFAULT with no verifiable effort evidence" is
    # replaced by the measurement, not merely deleted. Measured
    # 2026-07-31, a home pinning `low` produced `thinkingEffort=low` in
    # the session log and in every llm.request, so effort is confirmed
    # PER CALL rather than by config validation alone.
    #
    # This is also where 0.14.2 F8's reasoning lands. That finding said
    # absence of an override pin establishes neither an override nor
    # provider-default operation, and that writing either into the record
    # manufactures a fact the lane never observed. The lane can no longer
    # reach that state - the value is written by the home builder and
    # read back out of the round's own evidence - so the pin holds the
    # measurement and the mechanism that makes the old failure mode
    # unreachable.
    assert "EFFORT is written into the debate home and CONFIRMED PER CALL" in body
    assert ("a home pinning `default_effort = \"low\"` produced "
            "`thinkingEffort=low` in both surfaces") in body
    # Thinking is NOT confirmed, and must not be listed beside effort as
    # though it were. Measured: `enabled = false` produced output
    # identical to `enabled = true`.
    assert ("THINKING is CONFIG-ASSERTED AND NOT RUNTIME-VERIFIED" in body)
    assert ("`[thinking] enabled = false` produced output identical to "
            "`enabled = true`") in body
    # The `merge_all_available_skills` back-channel pin becomes the four
    # skill roots plus the `--skills-dir` wording. Same class, renamed
    # subject: the question is still what can inject instructions into
    # this lane's reviewer from outside the brief.
    assert ("SKILL DISCOVERY has FOUR roots — `.kimi-code/skills/`, "
            "`.agents/skills/`, `<debate-home>/skills/` and "
            "`~/.agents/skills/`") in body
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
    # `extra_skill_dirs` is named in the section's opening as one of the
    # two recorded keys, so the bullets have to say what recording it
    # means. The builder writes it EMPTY, which is what makes a non-empty
    # value a finding about the home rather than a note about the client.
    assert ("The home's own `extra_skill_dirs` is the key recorded "
            "alongside them: the builder writes it EMPTY, so a non-empty "
            "value in a debate's home was written by something other "
            "than the builder and is a finding about the home, not a "
            "note.") in body
    # The retired "unprobed territory" pin carried a DISPOSITION for the
    # source this lane cannot clear. Its successor names which roots are
    # covered by what, and that `~/.agents/skills/` is covered by
    # nothing: preflight-3 operates on the MIRROR and KIMI_CODE_HOME does
    # not relocate the user's home, so an uneven coverage claim here
    # would be the same overclaim in a new place.
    assert ("`~/.agents/skills/` lives in the user's own home, is not "
            "relocated by `KIMI_CODE_HOME`, and NOTHING this lane runs "
            "removes it. Enumerate that root before round 1 and record "
            "what it holds; a non-empty one is unprobed territory, "
            "recorded as such rather than assumed absorbed by the tool "
            "allowlist.") in body
    # The old "LATENT surface" pin recorded that a back-channel key's
    # presence says nothing about whether anything is actually being
    # merged. Its successor is stronger and states the same restraint:
    # `--skills-dir` is a MITIGATION whose effect is UNMEASURABLE here,
    # not a control - measured, runs with and without it were
    # indistinguishable because nothing loaded either way. Claiming it as
    # a control is the overclaim this pin exists to block.
    assert ("`--skills-dir` is a MITIGATION whose effect is UNMEASURABLE "
            "in this configuration, not a control") in body
    assert ("The load-bearing controls are that allowlist and preflight-3 "
            "remediation.") in body
    assert ("Keep passing `--skills-dir`, because it costs nothing and "
            "covers a future release that advertises regardless, but "
            "claim nothing for it.") in body
    # And the files stay an injection surface by a different route, which
    # is why remediation deletes them rather than trusting the reviewer:
    # in the measured round the reviewer READ both canaries and declined
    # on judgment. Prompt text is never a control.
    assert ("Prompt text is never a control, which is why remediation "
            "REMOVES the files rather than trusting the reviewer to "
            "ignore them.") in body


def test_skill_preflight_names_the_remediation():
    # 0.14.2: preflight 3 said STOP and never said how to clear it.
    # The tracked/ignored branch is the part that misreads as a bug:
    # deleting an IGNORED back-channel leaves HEAD untouched and
    # `nothing to commit`, which looks like a failed remediation and
    # is in fact the correct one (both observed 2026-07-26).
    skill = _norm(REPO / "skills" / "multi-model-verify" / "SKILL.md")
    assert "review mirror" in skill
    # 0.17.0: "empty output" became "empty ENUMERATION output". The mirror
    # now produces two measurements - the re-enumeration and the client
    # probe - so an unqualified "empty output" no longer says which one
    # carries the evidence.
    assert "empty enumeration output is the evidence" in skill
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

# evals/multi-model-verify/fixtures/contract-coverage-history/ is EXCLUDED
# by directory, not by file, so a fixture added there later does not
# reopen this. Same reasoning as docs/** above: this sweep's subject is
# DISPATCH surfaces, the files an agent reads to build a command. That
# directory holds frozen historical evidence - verbatim old test-file
# snapshots - which cannot drift and is not read to build anything.
# Raised and ruled on during the 0.15.0 contract-coverage work.
EXCLUDED_DIRS = (REPO / "evals" / "multi-model-verify" / "fixtures"
                  / "contract-coverage-history",)


def test_backup_literal_single_source():
    offenders = []
    for pattern in SWEEP_GLOBS:
        for p in REPO.glob(pattern):
            if not p.is_file() or p.resolve() in ALLOWED:
                continue
            if any(p.resolve().is_relative_to(d) for d in EXCLUDED_DIRS):
                continue
            if BACKUP_ID in p.read_text(encoding="utf-8",
                                        errors="replace"):
                offenders.append(str(p))
    assert offenders == []


DRIFT = REPO / "tools" / "check-drift.ps1"
STATEMACHINE = REPO / "evals" / "tools" / "drift_statemachine_tests.ps1"
KIMI_CODE_FLOOR = "0.31.1"


def test_drift_probes_the_new_cli_not_the_old_one():
    body = _read(DRIFT)
    assert '"--agent-file", "--skills-dir", "-m", "-p", "--session"' in body
    assert "--quiet" not in body
    assert "--thinking" not in body
    assert "import kimi_cli.tools.file" not in body


def test_drift_does_not_assert_a_hidden_alias():
    """`-r` works but is absent from --help on 0.31.1. Asserting it would
    manufacture the exact false finding this task removes."""
    assert '"-r"' not in _read(DRIFT)


def test_the_version_probe_can_actually_reach_its_failure_branch():
    """r2's floor check was unreachable: $kimiVersion was assigned only
    inside a successful numeric regex, so TryParse could never see a
    malformed value and the fail-closed branch was dead code. A check
    that cannot fail is the defect this whole task is repairing."""
    body = _read(DRIFT)
    assert "$kimiVersion = $kimiRaw" in body
    assert "KimiCodeFloor" in body
    assert KIMI_CODE_FLOOR in body


def test_the_production_lookup_accepts_a_cmd_stub():
    """A .cmd renamed .exe does not execute on Windows, so an absolute
    .exe-only lookup cannot be stubbed offline at all. Production
    therefore resolves either name in that directory - which is also true
    of real Windows CLIs - and the harness stubs the .cmd."""
    body = _read(DRIFT)
    assert "kimi.exe" in body
    assert "kimi.cmd" in body


def test_the_state_machine_stubs_moved_with_the_probe():
    body = _read(STATEMACHINE)
    assert "kimi_cli" not in body
    assert "--thinking" not in body
    # the production lookup is an absolute path under the fake profile,
    # not a PATH entry, so the harness must place the stub there or every
    # kimi scenario silently takes the "absent" branch and asserts nothing
    assert ".kimi-code" in body
    assert "--session" in body
    assert "KIMI_STUB_MODE" in body


def test_a_present_but_unusable_binary_is_a_finding_not_a_note():
    """r3 fixed the regex pre-filter but left a second path open: a binary
    that exists while --version fails or prints nothing still fell into
    the 'absent' note. Absent is a note; present-and-broken is a finding."""
    body = _read(DRIFT)
    assert "$versionExit" in body
    assert "did not report a usable version" in body
