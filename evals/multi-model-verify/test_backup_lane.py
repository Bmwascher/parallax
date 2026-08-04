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
    whose real config carries no hooks.

    Revised for the credential fix: the home no longer holds a COPY. Its
    `credentials` directory is a junction to a dedicated lane login, so
    the removal half is now pinned for a different reason, and the
    DEBATE home and the LANE home are named as two distinct
    directories because the superseded text blurred them."""
    assert (
            "Build the DEBATE home ONCE, before round 1, with "
            "`tools/new-kimi-lane-home.ps1`, and set "
            "`KIMI_CODE_HOME=<debate-home>` on EVERY call of that debate, "
            "fresh and resumed alike. Two directories matter here and the "
            "shipped text must not blur them: the DEBATE home is this "
            "debate's throwaway `KIMI_CODE_HOME`, and the LANE home is the "
            "persistent directory holding the lane's own login and the "
            "lock. Two INDEPENDENT reasons, either one sufficient: the real "
            "user-global `~/.kimi-code/config.toml` can carry lifecycle "
            "hooks that run a shell command on the reviewer's own approval "
            "path, and the home is where this lane's effort pin and this "
            "debate's session evidence live. One debate is ONE home: that "
            "debate's ROUNDS are one session, and the only other session "
            "the home may hold is the write-probe's own disposable one, "
            "created before round 1 and therefore already in the inventory "
            "the freshness rule captures. A home is never reused across "
            "DEBATES, because a reused home carries another debate's "
            "sessions into this one's evidence. The home holds NO COPY of "
            "any credential. Its `credentials` directory is a JUNCTION to a "
            "DEDICATED LANE LOGIN, distinct from the user's ordinary login, "
            "so a refresh writes THROUGH to one file and no copy can go "
            "stale; the lane never falls back to the ordinary credential. A "
            "home that cannot be built, or a lane credential that is "
            "absent, unreadable or structurally invalid, makes the lane "
            "UNAVAILABLE, never a reason to dispatch from the real home. "
            "Remove the home with `-Remove` when the debate ends. The lock "
            "protocol every one of those calls follows is the "
            "call-lifecycle region below.") in _norm(BACKUP_LANE)


def test_lane_lock_region():
    """One persistent file, never unlinked, and staleness that is LIVENESS
    rather than a clock. A predecessor of this lock decided staleness by
    AGE, so a live round past the threshold became breakable by anyone.

    The unmeasurable cases are pinned with the reclaimable ones on
    purpose: `held` is what a foreign-host, unreadable, empty, non-object
    or schema-violating record all resolve to, and a pin holding only the
    DEAD-reclaim half would let any of them be quietly reclassified as
    reclaimable, which is the one outcome this protocol may never
    produce."""
    assert (
            "The lane home is shared between debates and sessions, so one "
            "PERSISTENT lock file beside the credential guards it. That "
            "file is NEVER unlinked: acquire, reclaim and release are all "
            "state transitions written IN PLACE, each under one exclusive "
            "handle that serializes every writer. Staleness is LIVENESS and "
            "never a clock. A holder is stale only when no process carries "
            "its recorded id, or a process carries it with a different "
            "start time, which is the identity-reuse guard. A predecessor "
            "of this lock decided staleness by AGE, so a live round past "
            "the threshold became breakable by anyone; nothing here has a "
            "time-based expiry, and a wait budget bounds only caller "
            "patience and never widens what counts as stale. What cannot be "
            "evaluated is HELD: a record naming another machine, an "
            "unreadable file, a zero-length file, a file that is not a JSON "
            "object, or a JSON object that does not exactly satisfy the "
            "record schema \u2014 version 1, one of the two state literals, that "
            "state's exact field set, and every field's type and validation "
            "rule \u2014 are each held and reported rather than reclaimed, "
            "because an unmade measurement is never a clean one. A "
            "DEAD-holder reclaim reports the holder it replaced. An "
            "exhausted wait reports the LIVE or UNMEASURABLE holder it "
            "refused, or reports handle contention when no record could be "
            "read. Each confirmed override reports the record or bytes it "
            "displaced. Contention WAITS up to the caller-supplied budget "
            "and then refuses; a zero budget refuses at once, and no budget "
            "ever breaks a holder. Two human overrides exist because one "
            "cannot cover both states: a well-formed HELD record is freed "
            "by confirming its complete recorded identity, machine name "
            "included, and a record too damaged to trust its identity is "
            "freed by confirming the exact hash of its current bytes. Both "
            "are guarded human overrides, not authentication, and both "
            "leave the file in place.") in _norm(BACKUP_LANE)


def test_lane_lock_call_lifecycle_region():
    """Who the owner is, and why it is resolved once and passed rather
    than derived. The shell exits between calls, so a shell-derived owner
    makes every lock instantly stale, and under any wrapper the parent is
    an intermediate process that also exits.

    The four pre-acquisition filesystem interactions are enumerated
    rather than described, because 'only these' is the claim: each is
    either read-only or idempotent, and the builder never creates the
    directory. The nonce half is pinned with them - a hold nobody can
    release is a lane nobody else can use."""
    assert (
            "Ownership is RESOLVED ONCE per debate and PASSED EXPLICITLY "
            "thereafter. The owner is the harness session process, not the "
            "shell, which exits between calls and would make every lock "
            "instantly stale; deriving it from the invoking shell's parent "
            "is correct only for a DIRECT invocation, and under any wrapper "
            "it names an intermediate process that also exits. So run "
            "`tools/kimi-lane-lock.ps1 -ResolveOwner` once at the start of "
            "the debate, keep its `ownerPid` and `ownerStartTicksUtc`, "
            "generate one 32-character lowercase hexadecimal debate id, and "
            "hand all three to every later call. Build with "
            "`tools/new-kimi-lane-home.ps1 -Path <debate-home> -Model "
            "<canonical-backup-model-id> -Effort <canonical-backup-effort> "
            "-LaneHome <lane-home> -DebateId <id> -OwnerPid <pid> "
            "-OwnerStartTicksUtc <ticks>`; it acquires the lock before it "
            "validates the credential, because a login could otherwise "
            "write that credential in between, and it releases only when "
            "the build itself failed. Build prints one JSON line carrying "
            "`debateHome` and `nonce`: keep that nonce, because removal "
            "requires it and a hold nobody can release is a lane nobody "
            "else can use. Remove with `tools/new-kimi-lane-home.ps1 -Path "
            "<debate-home> -Remove -LaneHome <lane-home> -DebateId <id> "
            "-OwnerPid <pid> -OwnerStartTicksUtc <ticks> -Nonce <nonce>`; "
            "it confirms the complete identity BEFORE it deletes anything, "
            "so a caller who cannot release also cannot destroy, and it "
            "releases only after the home is gone. Log the lane in with "
            "`tools/new-kimi-lane-login.ps1 -LaneHome <lane-home> -OwnerPid "
            "<pid> -OwnerStartTicksUtc <ticks> -VerdictOut <path>`, passing "
            "the SAME lane home the build was given, because omitting it "
            "authenticates the default home while the debate dispatches "
            "from another; the wrapper generates its own debate id, takes "
            "the same lock with the lane home as its debate home, and "
            "releases it on the way out. A login outside that lock would be "
            "the one writer this protocol never sees. Only these filesystem "
            "interactions occur before lock acquisition, because the lock "
            "lives inside the lane directory: the login wrapper's "
            "fail-closed probe of the lane directory, the login wrapper "
            "creating that directory when the probe measured it missing, "
            "the login wrapper applying its access rules, and the builder's "
            "own read-only fail-closed probe of whether that directory is "
            "there. All four interactions are safe to repeat: both probes "
            "only read, and directory creation and ACL application are "
            "idempotent. The builder NEVER creates the directory: if it is "
            "missing the builder prints the login command and stops without "
            "taking the lock, and once the directory is confirmed the "
            "credentials directory and the credential file are both "
            "measured UNDER the lock. A debate that ends without removal "
            "leaves its home on disk and its record still HELD; that record "
            "is not freed by the session exiting, it merely becomes DEAD by "
            "liveness and is reclaimable at some later acquire. Read the "
            "state at any time with `tools/kimi-lane-lock.ps1 -Status "
            "-LaneHome <lane-home>`, which reports the holder and its "
            "liveness and reports LIVE to mean the process is running, "
            "never to mean the debate is still going.") in _norm(BACKUP_LANE)
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
    obvious wrong reading.

    0.21.0 extends the region to name the RESUME payload. The rule said
    "the brief", the resumed payload is a rebuttal, and the coverage was
    an inference: read narrowly, every round after the first had its
    delivery unchecked, which is the exact gap the rule exists to close.
    """
    assert (
            "Hash the brief BEFORE dispatch and require the recorded prompt "
            "to match: SHA-256 over the brief canonicalized as UTF-8 with "
            "CRLF normalized to LF, compared against the same hash of the "
            "concatenation of every `turn.prompt` `input[]` element's "
            "`text` field. The canonicalization is part of the rule rather "
            "than an implementation detail: the measured evidence matched "
            "only after newline normalization, so a rule saying merely that "
            "the two hash to the same value leaves a driver to invent that "
            "step. \"The brief\" here means the payload of EVERY call in the "
            "debate, fresh and resumed alike: a resumed round's payload is a "
            "rebuttal rather than the opening brief, and it is bound by this "
            "same rule. Stating it removes an inference - a rule that named "
            "only round 1 would leave every later round's delivery "
            "unchecked, which is the gap this rule exists to close."
            ) in _norm(BACKUP_LANE)


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
    assert "Rotation guard" not in body
    assert "Created new session:" not in body
    # `kimi-lane-lock.ps1` used to be forbidden by NAME here. It is back,
    # for an unrelated reason, so the guard moved to the RULE. The tool
    # that returned guards the PERSISTENT LANE LOCK FILE beside the
    # credential; the deleted one serialized rounds against one shared
    # append log and decided staleness by AGE. Forbidding the name would
    # now forbid the replacement, and forbidding nothing would let the
    # age rule come back under the new name - so these four needles are
    # the deleted rule's own distinctive wording, each verified present
    # in the superseded text at 79ec79f and absent from the current one.
    assert "-Acquire -Label" not in body
    assert "A BUSY result" not in body
    assert "The lock is advisory" not in body
    assert "breaks after 45 minutes" not in body


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
    # 0.20.0: two retired pins are replaced here. The first instructed
    # every round to record an unknown, and the probe resolved it. The
    # second called `--skills-dir` unmeasurable, which was true only of
    # the CONFOUNDED configuration it was measured in, where `Skill` was
    # denied so nothing could load either way.
    #
    # The disposition and the limit that binds it are SEPARATE regions
    # because one pin must lock a whole region, and each is long enough
    # alone. The prose after them is deliberately OUTSIDE both regions,
    # so the regions stay pinnable.
    assert ("`~/.agents/skills/` lives in the user's own home, is not "
            "relocated by `KIMI_CODE_HOME`, and NOTHING this lane runs "
            "removes it.") in body
    assert ("Enumerate that root before round 1 and record its COUNT, "
            "never its contents - the repo is public. MEASURED "
            "2026-08-03 on kimi-code 0.31.1, and no longer unprobed: a "
            "canary skill planted in that root was REACHABLE when "
            "`--skills-dir` was omitted - the wire carried the "
            "invocation and a `skill_activation` message delivering the "
            "body - and was NOT found when the flag was passed, the "
            "lookup returning the calibrated not-found result exactly. "
            "Treat the enumeration as an environment record of reachable "
            "external instruction inventory, not as a control and not as "
            "evidence that any real skill was invoked. Record: "
            "docs/superpowers/plans/rounds/2026-08-03-home-skills-root/"
            "probe-record.md") in body
    assert ("The disposition is bound to what the probe reached: one "
            "skill, named exactly, at the home root, on kimi-code "
            "0.31.1. Suppression was measured for that root ALONE; the "
            "two project roots were never canaried, and their exclusion "
            "rests on the client's own help text, which says the flag's "
            "target is used instead of auto-discovered directories - "
            "text evidence, never a measurement - and on preflight-3 "
            "remediation clearing the project roots in the mirror "
            "regardless. No cell passed the flag against a POPULATED "
            "target, so what the flag does to its own target is "
            "unmeasured; suppression was measured only for "
            "`~/.agents/skills/`, with that target EMPTY, and that "
            "measurement holds only while `<debate-home>/skills/` stays "
            "empty: the builder creates it empty and asserts that as "
            "its own postcondition, and no per-round check re-verifies "
            "it at dispatch. On that client "
            "`systemPromptChars` equalled the LF-normalized agent body "
            "in every cell, including both loaded-canary cells, so the "
            "measured delivery path was `skill_activation` and not "
            "system-prompt injection: the deny list controls that "
            "measured path, and the lane's system-prompt equality "
            "checks, not the deny list, would have to reject any future "
            "injection path. A client whose skill delivery changes shape "
            "retires this measurement rather than inheriting it.") in body
    # OUTSIDE the regions, and pinned separately: what actually holds the
    # lane closed as it ships, and the standing instruction to keep
    # passing the flag. Both lanes agreed this prose must not sit inside
    # region 2, because a region has to fit one pin.
    # CORRECTED after the per-task review. The first version of this pin
    # said the deny list was "measured in cells A and B". It was not: both
    # cells ALSO passed the flag at an empty target, so discovery was
    # already suppressed and no discovered skill was ever presented for
    # the deny list to block. What A and B do measure is the TOOL SURFACE
    # - five tools, `Skill` absent - which is a different claim. This is
    # the fourth instance on this branch of a claim wider than its
    # evidence, and the third about these same two cells.
    assert ("The load-bearing control as the lane ships is the `Skill` "
            "deny list, and what is MEASURED of it is the TOOL SURFACE: "
            "cells A and B advertised five tools with `Skill` absent, and "
            "the round validator compares that snapshot against the agent "
            "file by exact list equality on every session-creating call. "
            "Those cells passed the flag as well, so they measure the "
            "COMPOSITION and cannot attribute their null result to either "
            "layer alone.") in body
    assert ("Keep passing `--skills-dir` on every call, fresh and "
            "resumed, as a measured second layer, and claim for it "
            "exactly what was measured: suppression of the home root, "
            "conditional on an empty target, on 0.31.1.") in body
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
    # Task 4 Step 1 probed the cp1252 output hazard live, on this client
    # rather than the old kimi-cli one: from a console forced to code page
    # 1252, a reply containing an em-dash, an arrow and a katakana
    # character came back intact as valid UTF-8 and the process exited 0.
    # No hazard was observed on this client, so the Python-console guard
    # the old lane needed (PYTHONIOENCODING/PYTHONUTF8), the class that
    # named its failure, and the four-flags-re-pinned recovery all go with
    # it - none of them describe this client.
    lane = _norm(BACKUP_LANE)
    assert "PYTHONIOENCODING" not in lane
    assert "PYTHONUTF8" not in lane
    fb = _norm(FALLBACKS)
    assert "output-encoding" not in fb


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


# --- Task 1: the workflow path/host-parity checker -------------------------
#
# `775472c` deleted evals/multi-model-verify/test_kimi_lane_lock.py and
# tools/kimi-lane-lock.ps1 without touching the workflow, which still named
# the dead test path at .github/workflows/skill-evals.yml:84 and :95 - a
# merge-blocking break `python -m pytest <dead path> -q` reproduces (exit 4,
# "file or directory not found"). evals/tools/check_workflow_paths.py is the
# repair: pure Python (the ubuntu job runs it, no PowerShell, no platform
# branch) checking every referenced evals/...py token resolves to a READABLE
# REGULAR FILE (exists()/is_file() are both insufficient - only an actual
# open for binary reading establishes readability) and that a declared set
# of dual-host modules is present in BOTH Windows pytest steps.
import importlib.util as _importlib_util

CHECK_WORKFLOW_PATHS = REPO / "evals" / "tools" / "check_workflow_paths.py"
WORKFLOW = REPO / ".github" / "workflows" / "skill-evals.yml"


def _load_check_workflow_paths():
    spec = _importlib_util.spec_from_file_location(
        "check_workflow_paths", CHECK_WORKFLOW_PATHS)
    module = _importlib_util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_check_workflow_paths_flags_nonexistent_path(tmp_path):
    cwp = _load_check_workflow_paths()
    text = (
        "        run: >\n"
        "          python -m pytest\n"
        "          evals/multi-model-verify/test_does_not_exist.py -q\n"
    )
    errors = cwp.check_paths_readable(
        cwp.extract_py_tokens(text), tmp_path)
    assert any("test_does_not_exist.py" in e for e in errors)


def test_check_workflow_paths_flags_directory_named_like_py_file(tmp_path):
    """A DIRECTORY whose name ends in `.py` exists happily, so a checker
    that stopped at exists() or is_file() would pass it. Only opening it
    for binary reading catches this."""
    cwp = _load_check_workflow_paths()
    (tmp_path / "evals" / "multi-model-verify").mkdir(parents=True)
    trap = tmp_path / "evals" / "multi-model-verify" / "test_trap.py"
    trap.mkdir()
    assert trap.exists() and not trap.is_file()
    errors = cwp.check_paths_readable(
        ["evals/multi-model-verify/test_trap.py"], tmp_path)
    assert any("test_trap.py" in e for e in errors)


def test_check_workflow_paths_flags_unreadable_file_deterministically(
        tmp_path, monkeypatch):
    """Simulated, never a real Windows ACL denial - machine ACL behaviour
    is not something a test may depend on. An is_file()-only implementation
    that never opens anything would pass this; opening it must not."""
    cwp = _load_check_workflow_paths()
    (tmp_path / "evals" / "multi-model-verify").mkdir(parents=True)
    real_file = tmp_path / "evals" / "multi-model-verify" / "test_real.py"
    real_file.write_text("# fixture\n", encoding="utf-8")
    assert real_file.is_file()

    def _raise_open(path):
        if Path(path).name == "test_real.py":
            raise PermissionError(13, "simulated permission denied")
        return open(path, "rb")

    monkeypatch.setattr(cwp, "_open_binary", _raise_open)
    errors = cwp.check_paths_readable(
        ["evals/multi-model-verify/test_real.py"], tmp_path)
    assert any("test_real.py" in e for e in errors)


def test_check_workflow_paths_flags_host_parity_gap():
    cwp = _load_check_workflow_paths()
    complete = " ".join(cwp.REQUIRED_DUAL_HOST_MODULES)
    text = (
        "      - name: PowerShell-facing tests under Windows PowerShell 5.1\n"
        "        env:\n"
        "          PARALLAX_PS_HOST: powershell.exe\n"
        "        run: >\n"
        "          python -m pytest " + complete + " -q\n"
        "\n"
        "      - name: PowerShell-facing tests under PowerShell 7\n"
        "        env:\n"
        "          PARALLAX_PS_HOST: pwsh.exe\n"
        "        run: >\n"
        "          python -m pytest "
        + " ".join(cwp.REQUIRED_DUAL_HOST_MODULES[1:]) + " -q\n"
    )
    host_steps = cwp.extract_windows_host_steps(text)
    assert {host for host, _ in host_steps} == {"powershell.exe", "pwsh.exe"}
    assert len(host_steps) == 2
    errors = cwp.check_host_parity(host_steps, cwp.REQUIRED_DUAL_HOST_MODULES)
    assert any(
        "pwsh.exe" in e and cwp.REQUIRED_DUAL_HOST_MODULES[0] in e
        for e in errors)
    assert not any("powershell.exe" in e for e in errors)


def test_check_workflow_paths_refuses_when_host_steps_are_not_found():
    """An unmade measurement is never a clean one. Renaming
    PARALLAX_PS_HOST (simulated here, in a synthetic copy of the workflow
    text - not the real file) makes extract_windows_host_steps find zero
    host steps; check_host_parity must FAIL and say so, rather than pass
    vacuously because its loop over an empty list never ran."""
    cwp = _load_check_workflow_paths()
    complete = " ".join(cwp.REQUIRED_DUAL_HOST_MODULES)
    text = (
        "      - name: PowerShell-facing tests under Windows PowerShell 5.1\n"
        "        env:\n"
        "          PARALLAX_PS_HOST_RENAMED: powershell.exe\n"
        "        run: >\n"
        "          python -m pytest " + complete + " -q\n"
        "\n"
        "      - name: PowerShell-facing tests under PowerShell 7\n"
        "        env:\n"
        "          PARALLAX_PS_HOST_RENAMED: pwsh.exe\n"
        "        run: >\n"
        "          python -m pytest " + complete + " -q\n"
    )
    host_steps = cwp.extract_windows_host_steps(text)
    assert host_steps == []
    errors = cwp.check_host_parity(host_steps, cwp.REQUIRED_DUAL_HOST_MODULES)
    assert errors
    assert any("could not find the expected" in e for e in errors)


def test_check_workflow_paths_refuses_a_duplicate_host_step():
    """A dict keyed by host lets a SECOND step for the same host silently
    OVERWRITE the first: three steps - an incomplete powershell.exe step,
    a complete duplicate powershell.exe step, and a complete pwsh.exe step
    - collapse under such a dict to exactly the correct-looking pair
    {powershell.exe, pwsh.exe}, both showing the complete module set, and
    parity reports clean about a step it never examined. The discovered
    host MULTISET (two powershell.exe, one pwsh.exe) is not the required
    multiset (one of each) even though the SET matches, so this must fail
    and name the multiplicity problem."""
    cwp = _load_check_workflow_paths()
    complete = " ".join(cwp.REQUIRED_DUAL_HOST_MODULES)
    incomplete = cwp.REQUIRED_DUAL_HOST_MODULES[0]
    text = (
        "      - name: PowerShell-facing tests under Windows PowerShell 5.1"
        " (incomplete, first)\n"
        "        env:\n"
        "          PARALLAX_PS_HOST: powershell.exe\n"
        "        run: >\n"
        "          python -m pytest " + incomplete + " -q\n"
        "\n"
        "      - name: PowerShell-facing tests under Windows PowerShell 5.1"
        " (duplicate, complete)\n"
        "        env:\n"
        "          PARALLAX_PS_HOST: powershell.exe\n"
        "        run: >\n"
        "          python -m pytest " + complete + " -q\n"
        "\n"
        "      - name: PowerShell-facing tests under PowerShell 7\n"
        "        env:\n"
        "          PARALLAX_PS_HOST: pwsh.exe\n"
        "        run: >\n"
        "          python -m pytest " + complete + " -q\n"
    )
    host_steps = cwp.extract_windows_host_steps(text)
    # every step is preserved - nothing collapsed
    assert len(host_steps) == 3
    assert {host for host, _ in host_steps} == {"powershell.exe", "pwsh.exe"}
    errors = cwp.check_host_parity(host_steps, cwp.REQUIRED_DUAL_HOST_MODULES)
    assert errors
    assert any("could not find the expected" in e for e in errors)
    # the message names the multiplicity, not just the set
    assert any("powershell.exe" in e and "pwsh.exe" in e for e in errors)


def test_check_workflow_paths_real_workflow_is_clean():
    """The checker run against the real workflow, both checks. This is the
    TDD anchor: written before the orphaned test_kimi_lane_lock.py
    reference was removed from skill-evals.yml, it failed - confirming the
    checker catches the real break - and passes once the workflow is
    fixed."""
    cwp = _load_check_workflow_paths()
    assert cwp.check_workflow(WORKFLOW, REPO) == []


def test_check_workflow_paths_prints_nothing_and_exits_zero():
    import subprocess
    import sys
    result = subprocess.run(
        [sys.executable, str(CHECK_WORKFLOW_PATHS)],
        capture_output=True, text=True, cwd=str(REPO))
    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


# --- Task 8: the doctor stops touching credentials -------------------------
#
# commands/doctor.md check 8 used to build a scratch KIMI_CODE_HOME and run
# `provider list` against it - measurement 16/17 showed that proves nothing
# and mutates nothing, and a live round dispatch failed with
# `auth.login_required` even while `provider list` reported a healthy oauth
# source. The check now validates the lane credential's STRUCTURE via
# tools/read-kimi-credential-state.ps1 and reads the lane lock's STATUS via
# tools/kimi-lane-lock.ps1 -Status, both read-only, and aggregates every
# substate into ONE row by the total order BROKEN > STALE > N/A > OK.

DOCTOR = REPO / "commands" / "doctor.md"

# The lane login recovery command, from `Fixed names and values` in the
# frozen plan - the COMPLETE emitted form, not the wrapper's filename. Task 6's
# builder emits and executes the identical string; the doctor only prints it.
RECOVERY_COMMAND = '& { $ErrorActionPreference = \'Stop\'; try { $ownerLines = @(& \'tools/kimi-lane-lock.ps1\' -ResolveOwner); $ownerExit = $LASTEXITCODE; if ($ownerExit -ne 0) { throw "owner resolution failed with exit $ownerExit" }; if ($ownerLines.Count -ne 1 -or -not ($ownerLines[0] -is [string]) -or [string]::IsNullOrWhiteSpace([string]$ownerLines[0])) { throw \'owner resolution returned invalid output\' }; $owner = $ownerLines[0] | ConvertFrom-Json -ErrorAction Stop; if (-not ($owner -is [System.Management.Automation.PSCustomObject])) { throw \'owner resolution returned invalid schema\' }; $ownerFields = @($owner.PSObject.Properties.Name); if ($ownerFields.Count -ne 3 -or -not ($ownerFields -ccontains \'ownerPid\') -or -not ($ownerFields -ccontains \'ownerStartTicksUtc\') -or -not ($ownerFields -ccontains \'ownerName\') -or -not (($owner.ownerPid -is [int]) -or ($owner.ownerPid -is [long])) -or [long]$owner.ownerPid -le 0 -or -not ($owner.ownerStartTicksUtc -is [string]) -or $owner.ownerStartTicksUtc -notmatch \'\\A[0-9]+\\z\' -or -not ($owner.ownerName -is [string]) -or [string]::IsNullOrWhiteSpace($owner.ownerName)) { throw \'owner resolution returned invalid schema\' }; if ([string]::IsNullOrWhiteSpace($env:TEMP) -or -not (Test-Path -LiteralPath $env:TEMP -PathType Container -ErrorAction Stop)) { throw \'TEMP is not an existing directory\' }; $verdictOut = Join-Path -Path $env:TEMP -ChildPath \'parallax-kimi-lane-login-verdict.json\' -ErrorAction Stop; & \'tools/new-kimi-lane-login.ps1\' -LaneHome \'<lane-home>\' -OwnerPid ([string]$owner.ownerPid) -OwnerStartTicksUtc $owner.ownerStartTicksUtc -VerdictOut $verdictOut; $loginExit = $LASTEXITCODE; if ($loginExit -ne 0) { throw "lane login failed with exit $loginExit" } } catch { throw } }'

TOTAL_ORDER_RULE = 'row is the WORST substate observed, by `BROKEN > STALE > N/A > OK`, and every substate observed is still named in the detail text. N/A is IN that order'
BINARY_ABSENT = 'is N/A, short-circuit, "backup lane unavailable, primary unaffected"'
BINARY_OK_CLEAN = 'reports a usable version AT OR ABOVE the floor `0.31.1` is OK, with the reported version and the floor comparison both named in the detail — the CLEAN row this check used to omit.'
BINARY_BROKEN = 'A present binary that does not report a usable version, or reports below the floor, is BROKEN.'
FOUR_PART_RULE = "accept the measurement ONLY under the FOUR-PART ACCEPTANCE RULE: the process launched, it exited 0, stderr was EMPTY, and stdout was exactly one parseable line whose status/detail pairing is one of Task 2's table."
VALIDATOR_FAILS = 'pairing outside that table is "the validator itself fails to run": BROKEN, and NO credential recovery command is fabricated, because no credential state was measured.'
CRED_OK = '`ok` is OK — "lane credential structurally present".'
CRED_ABSENT = '`absent` is N/A, and no hash is taken at all.'
CRED_UNREADABLE_MALFORMED = '`unreadable` or `malformed` is BROKEN.'
RECOVERY_PRINT_STATEMENT = 'All three credential-failure rows above — `absent`, `unreadable` and `malformed` — print THE LANE LOGIN RECOVERY COMMAND from `Fixed names and values`, complete and executable, against the configured lane home:'
HASH_STEP1 = '1. Test existence of the credential file.'
HASH_STEP2 = '2. If ABSENT: run the validator, require `absent`, take NO hash.'
HASH_STEP3 = "3. If PRESENT: attempt hash 1 (SHA-256 of the file's bytes) and record success or failure."
HASH_STEP4 = "4. Run the validator REGARDLESS of hash 1's outcome."
HASH_STEP5 = '5. If the file is still present, attempt hash 2. Disappearance between the two hashes is BROKEN.'
HASH_STEP6 = '6. Compare ONLY if both hashes exist. Never compare a missing value to anything.'
HASH_STEP7 = '7. Any hash failure is BROKEN, and it does NOT suppress the validator detail.'
HASH_CANNOT_TAKE = 'A hash that cannot be taken on a PRESENT credential is BROKEN.'
HASH_NARROWED = 'differing hashes are BROKEN, "credential bytes changed during the check; actor not established"; equal hashes are reported as "no net byte change observed", never as proof nothing wrote the file.'
AUTH_PROBE_LITERAL = "An AUTHENTICATED probe is a SEPARATE operation and is never part of check 8. It acquires the lane lock, it MAY REFRESH the dedicated lane credential, and it never touches the user's ordinary credential. Check 8 reports STRUCTURE only, so a structurally present credential is not a working one."
LOCK_STATUS_CANNOT_MEASURE = 'status invocation that fails that rule is "lock status cannot be measured": BROKEN, and no recovery command is fabricated from evidence the check does not have.'
LOCK_FREE = '`free` is OK.'
LOCK_LIVE = "`held` and LIVE is OK, reported as held with the holder — LIVE means the holder's process is running, and never that a debate was abandoned."
LOCK_DEAD = '`held` and DEAD is STALE, reclaimable at the next acquire.'
LOCK_UNKNOWN_SAME_HOST = "`held`, SAME-HOST — the record's `host` equals `$env:COMPUTERNAME`, compared case-insensitively — and UNKNOWN is N/A: liveness could NOT be determined, and every mutating mode therefore treats the holder as alive and will not reclaim it. Same-host is what selects this row, because a foreign-host record also reports UNKNOWN liveness."
LOCK_FOREIGN_HOST = "foreign-host — the record's `host` differs from `$env:COMPUTERNAME`, compared case-INSENSITIVELY, which is the comparison the doctor makes since `-Status` reports the field — is STALE, with:"
FORCE_RELEASE_CMD = '`tools/kimi-lane-lock.ps1 -ForceRelease -LaneHome <lane-home> -ConfirmHost <host> -ConfirmOwnerPid <pid> -ConfirmOwnerStartTicksUtc <ticks> -ConfirmDebateId <id> -ConfirmNonce <nonce>`'
LOCK_MALFORMED = 'MALFORMED is STALE, with:'
MALFORMED_OVERRIDE_CMD = '`tools/kimi-lane-lock.ps1 -MalformedOverride -LaneHome <lane-home> -ConfirmSha256 <sha256>`'
CONTAINMENT_UNCHANGED = '**Containment artifact.** Verify the committed `skills/multi-model-verify/references/kimi-reviewer-agent.md` exists in the installed copy and its `tools:` allowlist is present (do not re-derive the list here; report presence/absence only). Missing file or allowlist is BROKEN.'


def test_doctor_check8_stops_touching_credentials():
    """The old check built a scratch home and ran `provider list`; measurement
    16/17 showed that proves nothing and mutates nothing, and the doctor now
    never dispatches to the credential at all."""
    body = _read(DOCTOR)
    assert "provider list" not in body
    assert "new-kimi-lane-home.ps1" not in body
    assert "credential present and OAuth-sourced" not in body


def test_doctor_check8_total_order_precedence():
    assert TOTAL_ORDER_RULE in _norm(DOCTOR)


def test_doctor_check8_binary_rows_including_the_clean_ok_row():
    """r25 (plan history): the substate table called itself total while having
    no row for the CLEAN binary, so every fixture in this task used to be a
    failure fixture and an implementation that never emitted OK would have
    passed all of them. This pin is the CLEAN row the table used to omit."""
    body = _norm(DOCTOR)
    assert BINARY_ABSENT in body
    assert BINARY_OK_CLEAN in body
    assert BINARY_BROKEN in body


def test_doctor_check8_four_part_rule_and_validator_failure_row():
    body = _norm(DOCTOR)
    assert FOUR_PART_RULE in body
    assert VALIDATOR_FAILS in body


def test_doctor_check8_a_nonzero_exit_with_a_valid_absent_report_stays_broken():
    """The plan's first boundary fixture. WHICH ROW FIRES is decided by the
    four-part acceptance rule, not by the report's contents: a nonzero exit
    carrying a perfectly valid-looking `absent` report is still "the
    validator itself fails to run", because nothing was measured. Two
    mutations, one per half of that claim."""
    body = _norm(DOCTOR)
    assert FOUR_PART_RULE in body
    assert VALIDATOR_FAILS in body
    # If exit 0 stopped being required, a nonzero exit could reach the
    # credential table and be read as a measured `absent`.
    without_exit_zero = body.replace("it exited 0, stderr was EMPTY",
                                      "stderr was EMPTY")
    assert FOUR_PART_RULE not in without_exit_zero
    # If the unmeasured case stopped being BROKEN, an unmade measurement
    # would read as a clean one.
    softened = body.replace('fails to run": BROKEN', 'fails to run": N/A')
    assert VALIDATOR_FAILS not in softened


def test_doctor_check8_an_exit_zero_valid_absent_report_is_na_and_takes_no_hash():
    """The plan's second boundary fixture, the other direction: a report
    that WAS accepted and says `absent` is an ordinary actionable reading,
    N/A rather than BROKEN, and it takes no hash at all."""
    body = _norm(DOCTOR)
    assert CRED_ABSENT in body
    assert RECOVERY_PRINT_STATEMENT in body
    wrong_verdict = body.replace("`absent` is N/A", "`absent` is BROKEN")
    assert CRED_ABSENT not in wrong_verdict
    hashing_anyway = body.replace("and no hash is taken at all",
                                   "and a hash is taken")
    assert CRED_ABSENT not in hashing_anyway


def test_doctor_check8_credential_status_mapping():
    body = _norm(DOCTOR)
    assert CRED_OK in body
    assert CRED_ABSENT in body
    assert CRED_UNREADABLE_MALFORMED in body


def test_doctor_check8_recovery_command_is_the_complete_emitted_form():
    """The pin covers the COMPLETE command, not the wrapper's filename - a
    message naming only tools/new-kimi-lane-login.ps1 must fail this pin."""
    body = _norm(DOCTOR)
    assert RECOVERY_PRINT_STATEMENT in body
    # RECOVERY_COMMAND is already single-line, so it needs no normalizing
    # of its own - normalizing a plain string (not a Path) would break _norm.
    assert RECOVERY_COMMAND in body
    # a message naming only the wrapper filename is not the complete command
    filename_only = body.replace(RECOVERY_COMMAND,
                                  "tools/new-kimi-lane-login.ps1")
    assert RECOVERY_COMMAND not in filename_only
    assert "tools/new-kimi-lane-login.ps1" in filename_only


def test_doctor_check8_hash_algorithm_seven_steps():
    body = _norm(DOCTOR)
    for step in (HASH_STEP1, HASH_STEP2, HASH_STEP3, HASH_STEP4, HASH_STEP5,
                 HASH_STEP6, HASH_STEP7):
        assert step in body
    # ordering: the seven steps appear in numeric order, not merely present
    positions = [body.index(step) for step in
                 (HASH_STEP1, HASH_STEP2, HASH_STEP3, HASH_STEP4, HASH_STEP5,
                  HASH_STEP6, HASH_STEP7)]
    assert positions == sorted(positions)


def test_doctor_check8_hash_wording_is_narrowed():
    body = _norm(DOCTOR)
    assert HASH_CANNOT_TAKE in body
    assert HASH_NARROWED in body


def test_doctor_check8_authenticated_probe_literal_exact():
    assert AUTH_PROBE_LITERAL in _norm(DOCTOR)


def test_doctor_check8_lock_status_measurement_failure_row():
    assert LOCK_STATUS_CANNOT_MEASURE in _norm(DOCTOR)


def test_doctor_check8_lock_free_live_dead_rows():
    body = _norm(DOCTOR)
    assert LOCK_FREE in body
    assert LOCK_LIVE in body
    assert LOCK_DEAD in body


def test_doctor_check8_unknown_same_host_pin_excludes_wrong_mappings():
    """Explicit pin, per the plan: the UNKNOWN row's N/A verdict TOGETHER WITH
    its required detail, so an implementation mapping UNKNOWN to OK or STALE
    fails - a generic "lock-status reporting" pin would not catch that."""
    body = _norm(DOCTOR)
    assert LOCK_UNKNOWN_SAME_HOST in body
    wrong_ok = body.replace("UNKNOWN is N/A:", "UNKNOWN is OK:")
    assert LOCK_UNKNOWN_SAME_HOST not in wrong_ok
    wrong_stale = body.replace("UNKNOWN is N/A:", "UNKNOWN is STALE:")
    assert LOCK_UNKNOWN_SAME_HOST not in wrong_stale


def test_doctor_check8_foreign_host_case_insensitive_pin_excludes_case_sensitive_wording():
    """Explicit pin, per the plan: the foreign-host branch's CASE-INSENSITIVE
    comparison of the record's host against $env:COMPUTERNAME, together with
    its complete -ForceRelease recovery command, so a case-sensitive
    comparison fails."""
    body = _norm(DOCTOR)
    assert LOCK_FOREIGN_HOST in body
    assert FORCE_RELEASE_CMD in body
    wrong = body.replace("case-INSENSITIVELY", "case-sensitively")
    assert LOCK_FOREIGN_HOST not in wrong


def test_doctor_check8_malformed_lock_row():
    body = _norm(DOCTOR)
    assert LOCK_MALFORMED in body
    assert MALFORMED_OVERRIDE_CMD in body


def test_doctor_check8_containment_artifact_is_unchanged():
    """This bullet is untouched by Task 8 - same text as before the rewrite,
    pinned in its own right per the plan's explicit instruction."""
    assert CONTAINMENT_UNCHANGED in _norm(DOCTOR)


def test_no_module_claims_ci_skips_the_windows_suites():
    """The powershell-hosts job has covered the probe and the mirror since
    6a462f9. A comment saying otherwise is a false record of coverage,
    which is the same defect class as a false claim of a clean
    measurement: it tells a reader a gate is absent when it is present.

    A COUNT is not an oracle here. Two textual occurrences could both sit
    in one host step, or in a comment, while the count stays at 2 and the
    second interpreter runs nothing. Slice the file into the two host
    steps and require one occurrence in EACH, keyed on the
    PARALLAX_PS_HOST value that names the interpreter.
    """
    def uncommented(path):
        """Whitespace-normalized, with Python comment markers stripped.

        _norm alone is WRONG for a pin over a wrapped comment: it joins the
        lines but leaves each continuation line's `#` inside the sentence,
        so the live text reads "CI does # not exercise these 155 cases".
        A staleness assertion written against _norm is therefore vacuously
        true and can never fail - which is what the first run of this test
        demonstrated, and exactly the defect class this suite exists to
        remove.
        """
        lines = [re.sub(r"^\s*#\s?", "", ln)
                 for ln in path.read_text(encoding="utf-8").splitlines()]
        return " ".join(" ".join(lines).split())

    covered = (
        "evals/multi-model-verify/test_codex_context_probe.py",
        "evals/multi-model-verify/test_review_mirror.py",
    )
    workflow = _read(REPO / ".github" / "workflows" / "skill-evals.yml")
    assert "powershell-hosts:" in workflow
    steps = {}
    for host in ("powershell.exe", "pwsh.exe"):
        marker = "PARALLAX_PS_HOST: " + host
        assert marker in workflow, "no step sets " + marker
        tail = workflow.split(marker, 1)[1]
        # The step ends at the next step's `- name:` at list indentation.
        steps[host] = tail.split("\n      - name:", 1)[0]
    for rel in covered:
        body = uncommented(REPO / rel)
        assert "CI does not exercise these 155 cases at all" not in body
        assert "Backlog item 10 carries the fix" not in body
        assert "powershell-hosts" in body, (
            rel + " must name the CI job that covers it")
        for host, step in steps.items():
            assert step.count(rel) == 1, (
                rel + " must appear exactly once in the " + host + " step")


def _lines(path):
    r"""Raw read with CRLF folded to LF, for pins that are NEWLINE-ANCHORED.

    _norm is wrong for every assertion below and the frozen plan used it
    anyway. _norm is `" ".join(text.split())`, so `"\n  - Skill\n"` can
    never occur in its output: the "must not offer" assertion would be
    vacuously TRUE and the "must deny" assertion vacuously FALSE, and
    `re.findall(r"^  - (\w+)$", ..., re.M)` would return [] and make every
    frontmatter-delta comparison compare two empty sets. Measured
    2026-08-03. Same class as D4 in the execution-deviation ledger, third
    instance in this plan.

    On line endings, stated at its true reach and no wider. The two files
    this reads do NOT agree, measured 2026-08-03: the reviewer agent is 39
    CRLF and 0 bare LF, the probe agent is 0 CRLF and 53 bare LF, and git's
    own eol normalization means either can flip on a fresh checkout. An
    earlier version of this docstring said "the agent files ARE CRLF",
    which was a measurement of ONE file stated over two - the exact
    claim-wider-than-its-evidence fault the rest of this docstring is
    about. What actually makes the `\n` pins match, for both files and
    under either ending, is `read_text`'s universal-newline folding. The
    explicit fold below is belt-and-braces for a caller that ever switches
    to `newline=""`; it is NOT load-bearing today.
    """
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def test_the_review_agent_still_denies_skill():
    """The probe agent exists to offer `Skill` for a MEASUREMENT. The one
    way that becomes a defect instead of a measurement is if the loosened
    file, or the loosening, reaches a review round. Two separate things
    must hold, so they are two separate assertions."""
    review = _lines(REPO / "skills" / "multi-model-verify" / "references"
                    / "kimi-reviewer-agent.md")
    tools_block = review.split("disallowedTools:")[0]
    denied_block = review.split("disallowedTools:")[1].split("subagents:")[0]
    assert "\n  - Skill\n" not in tools_block, (
        "the review lane's agent must never offer Skill")
    assert "\n  - Skill\n" in denied_block, (
        "the review lane's agent must explicitly deny Skill")
    assert "\n  - Bash\n" in denied_block
    assert "\n  - Write\n" in denied_block
    assert "\n  - Edit\n" in denied_block
    assert "subagents: []" in review


def test_the_probe_agent_is_never_named_by_the_lane_contract():
    """A probe-only agent file that a dispatch command can reach is not
    probe-only. The lane contract, the skill and the commands must never
    name it; only this plan's probe record and the probe's own tests do."""
    probe_rel = "tools/kimi-probe-agent.md"
    probe = _lines(REPO / "tools" / "kimi-probe-agent.md")
    tools_block = probe.split("disallowedTools:")[0]
    denied_block = probe.split("disallowedTools:")[1].split("subagents:")[0]
    # The loosening is exactly one tool, and only that one.
    assert "\n  - Skill\n" in tools_block
    assert "\n  - Skill\n" not in denied_block
    # Every containment control the review agent has, this file keeps.
    for denied in ("Bash", "Write", "Edit", "WebSearch", "FetchURL",
                   "Agent", "AgentSwarm"):
        assert "\n  - " + denied + "\n" in denied_block, denied
    assert "subagents: []" in probe
    assert "PROBE ONLY" in probe
    # The ONLY permitted frontmatter delta against the review agent is the
    # Skill move. A named-document list would have been the defect this
    # guard exists to catch, in the guard itself: the lane contract is a
    # whole directory plus the agent and command surfaces, and a list goes
    # stale the moment a file is added. Sweep, do not enumerate.
    review = _lines(REPO / "skills" / "multi-model-verify" / "references"
                    / "kimi-reviewer-agent.md")
    r_tools = set(re.findall(r"^  - (\w+)$", review.split("disallowedTools:")[0], re.M))
    p_tools = set(re.findall(r"^  - (\w+)$", probe.split("disallowedTools:")[0], re.M))
    r_denied = set(re.findall(r"^  - (\w+)$",
                              review.split("disallowedTools:")[1].split("subagents:")[0], re.M))
    p_denied = set(re.findall(r"^  - (\w+)$",
                              probe.split("disallowedTools:")[1].split("subagents:")[0], re.M))
    # Non-emptiness first: every set difference below is satisfied by two
    # empty sets, so without this the whole comparison is vacuous - which
    # is precisely how the frozen version of this test read.
    assert len(r_tools) == 5, r_tools
    assert len(p_tools) == 6, p_tools
    assert r_denied, r_denied
    assert p_tools - r_tools == {"Skill"}, p_tools - r_tools
    assert r_tools - p_tools == set()
    assert r_denied - p_denied == {"Skill"}, r_denied - p_denied
    assert p_denied - r_denied == set()
    # And nothing on any dispatch surface may name the probe file.
    # PER ROOT, not a total. `Path.rglob` on a directory that does not
    # exist yields nothing and raises nothing, so a renamed root drops out
    # of the sweep in silence. A single total floor cannot see that: the
    # three roots hold 9 + 5 + 3 files, so losing `agents` leaves 12 and
    # losing `commands` leaves 14, both clearing any floor low enough to
    # survive ordinary churn. An unswept root is not a clean root.
    for root, floor in (("skills", 5), ("agents", 3), ("commands", 2)):
        paths = sorted((REPO / root).rglob("*.md"))
        assert len(paths) >= floor, (
            root + " swept only " + str(len(paths)) + " files; the root moved")
        for path in paths:
            assert probe_rel not in _lines(path), (
                str(path.relative_to(REPO)) + " must not name the probe agent file")


def test_mirror_path_budget_region():
    """The pre-flight's contract, locked whole (0.21.0, backlog item 21).

    Three clauses here are the ones a later reader is most likely to
    trim, and each has a measured reason to stay. The UNIVERSE names
    directories and `.git` explicitly, because a files-only reading
    passes this repo and then fails mid-copy. A directory link is
    FOLLOWED rather than refused, because robocopy follows it and a
    refusal measured a smaller universe than the copy produces - the
    refusal that survives is the cycle case, which is the one the copy
    cannot complete. The unenumerable-path rule BLOCKS, because the
    manifest builder's hole semantics apply here too: a path that cannot
    be measured is not a path known to fit.
    """
    assert (
            "The mirror is a copy into a NEW root, so a destination "
            "that was legal in the source can be illegal in the mirror. "
            "That failure lands MID-COPY and leaves a partially "
            "populated tree that reads exactly like a complete one, "
            "which is why the check runs before the root is created "
            "rather than after the copy reports a count. The UNIVERSE "
            "it measures is every file and directory destination "
            "implied by the source AS ENUMERATED at pre-flight time, "
            "including tracked, untracked, ignored, and all `.git` "
            "content: a directory holding no files is still a "
            "destination, and `.git` is copied so `.git` counts. It is "
            "NOT a guarantee that this universe equals the one "
            "`robocopy /E` later walks. The enumeration finishes before "
            "the mirror root exists and the copy runs after it, so a "
            "path created in that window is in robocopy's universe and "
            "not in the measured one. The contract said \"the exact "
            "`robocopy /E` operation\" and that read as a guarantee; the "
            "mode-diff debate was right that it is not one. Closing the "
            "window needs construction from an immutable snapshot, "
            "which this release does not do. The ARITHMETIC is the "
            "resolved mirror-root length, plus a separator, plus the "
            "relative destination path length. The LIMIT is 260 "
            "characters as a conservative policy across both supported "
            "PowerShell hosts. It is a deterministic refusal threshold, "
            "not a claim about the maximum any host, API, OS "
            "configuration, or downstream client could support. Three "
            "requirements sit OUTSIDE that universe and bind equally. "
            "The `-OverrideOut` path is written beside the mirror by "
            "the tool rather than by robocopy, so the copy universe "
            "never covers it and it carries its own check. A source "
            "directory reparse point is FOLLOWED, because the copy "
            "follows it: `robocopy /E` with neither /XJ nor /SL writes "
            "the target's contents as an ordinary directory at the "
            "link's relative path, so refusing to measure across one "
            "described a SMALLER universe than the copy produces. What "
            "the copy cannot survive is a cycle, so a link onto one of "
            "its own ancestors is refused, and so is a tree whose links "
            "reach one target twice, which is indistinguishable from a "
            "cycle without walking the whole graph. A repo root that is "
            "itself a reparse point stays refused. "
            "A source path that cannot be enumerated BLOCKS the build "
            "and is never skipped, the same hole semantics the manifest "
            "builder states: a path that cannot be measured is not a "
            "path known to fit. The refusal names the root length, the "
            "deepest relative destination length, their sum and the "
            "limit, because a refusal an operator cannot act on is a "
            "refusal they will work around."
            ) in _norm(BACKUP_LANE)


def test_mirror_identity_gate_region():
    """The identity gate's contract, locked whole (0.21.0, item 22).

    Three clauses carry the weight. TWO identities, because they differ
    whenever remediation committed and a record printing one twice would
    be wrong in the common case. The BRIDGE at steps three and four,
    because without it two individually valid commit ids prove nothing
    about whether one tree came from the other. And the fingerprint
    covering CONTENT rather than the status listing alone, which is
    measured: editing an already-ignored file leaves the listing
    byte-identical, so the listing-only version verified clean across
    exactly the drift the check exists to catch.
    """
    assert (
            "The record carries TWO identities and one fingerprint: "
            "`source_head`, `mirror_head` and `source_status_sha256`. "
            "The two heads differ whenever remediation committed, which "
            "is the ordinary case for a repo carrying a tracked "
            "back-channel, so a record printing one of them twice is "
            "wrong in the common case rather than the rare one. "
            "Construction is a six-step bridge. Capture the source head "
            "BEFORE the copy; copy; require the live source head still "
            "equals it; before remediation, require the COPIED tree's "
            "head equals it; remediate, then record `mirror_head`. "
            "Steps three and four are the bridge itself: without them "
            "the record can hold two individually valid commit ids "
            "while nothing proves the mirror was built FROM the "
            "recorded source commit, which is two true facts arranged "
            "to look like one. What the bridge proves is matching "
            "OBSERVED ENDPOINTS, and that is weaker than an "
            "uninterrupted construction: a source that moves away and "
            "back during the copy satisfies both the before-and-after "
            "head equality and the before-and-after fingerprint, while "
            "the copied worktree can still hold intermediate bytes. The "
            "debate named that gap and it is real; the only thing that "
            "would close it is building from an immutable snapshot, "
            "which this release does not do. Before every fresh and "
            "resumed dispatch, re-run the tool with `-VerifyIdentity` "
            "and the three recorded values. Missing, unreadable or "
            "unequal BLOCKS the round, and a value that was never "
            "recorded is never a value that matched. What the gate "
            "proves is narrow and stated so: the two-HEAD gate proves "
            "committed-HEAD freshness. Non-HEAD inputs are bound in the "
            "constructed mirror's manifest AT CONSTRUCTION TIME, and "
            "source-side changes after construction are detected by the "
            "source-status comparison below WHEN THEY ARE VISIBLE TO "
            "IT: that is, changes that move the status listing, or that "
            "alter the content of a path the listing names. A tracked "
            "file git reports CLEAN is in neither, so a raw-byte change "
            "that survives the clean filter unchanged - the autocrlf "
            "case measured below is the mild one, a content-stripping "
            "filter the severe one - moves neither HEAD nor this "
            "fingerprint and is NOT covered. Round 2 of the mode-diff "
            "debate found the unqualified claim. That comparison is a "
            "fingerprint over the status capture AND the content of "
            "every path status names, not the status listing alone: "
            "measured 2026-08-04, editing an already-ignored file "
            "leaves the listing byte-identical, so a listing-only "
            "fingerprint verified clean across exactly the drift this "
            "check exists to catch. Ignored and untracked content is "
            "the entire reason this workspace is a mirror, so a gate "
            "blind to its bytes would be blind in the middle of the "
            "feature."
            ) in _norm(BACKUP_LANE)
