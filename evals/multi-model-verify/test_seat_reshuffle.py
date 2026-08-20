"""Contract tests for the 0.14.0 seat reshuffle.

Pins the three Fable seat agents, the panels reference, the required
fable review, the escalation decision envelope, and their routing.
Written RED-first; plan tasks 2-7 flip them green.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
AGENTS = REPO / "agents"
SKILL_DIR = REPO / "skills" / "multi-model-verify"
REFERENCES = SKILL_DIR / "references"


def _read(p):
    return p.read_text(encoding="utf-8")


def _norm(p):
    """Whitespace-normalized read, for pins that span a markdown wrap.

    Same convention as test_backup_lane.py. A pin that must lock a whole
    operative sentence cannot be held hostage to where the paragraph
    happens to wrap - reflowing a file is not a contract change.
    """
    return " ".join(_read(p).split())


def _frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.DOTALL)
    assert m, "frontmatter block missing"
    return m.group(1)


def test_fable_reviewer_exists_and_pins():
    p = AGENTS / "fable-reviewer.md"
    assert p.is_file()
    body = _read(p)
    fm = _frontmatter(body)
    assert "model: fable" in fm
    # exact read-only grant - no Bash, no Edit/Write (0.13.0 lesson:
    # prose refusal under live tools is priming, not containment)
    assert "tools: Read, Grep, Glob" in fm
    assert "Bash" not in fm
    assert "raw reply is retained as a range-bound artifact" in body
    assert "never replaces the cross-vendor gate" in body


def test_fable_panel_reviewer_exists_and_pins():
    p = AGENTS / "fable-panel-reviewer.md"
    assert p.is_file()
    body = _read(p)
    fm = _frontmatter(body)
    assert "model: fable" in fm
    assert "tools: Read, Grep, Glob" in fm
    assert "Bash" not in fm
    assert "dispatch metadata" in body
    assert "the resume surface carries no model parameter" in body
    assert "probed 2026-07-26" in body
    assert "cite the subject revision" in body
    # 0.14.4 drift triage: the resume property is HARNESS-VERSION
    # DEPENDENT, not a platform invariant. Before Claude Code 2.1.216 a
    # resumed background agent silently reverted to the DEFAULT agent,
    # losing the model pin, this system prompt, AND the read-only tool
    # restriction - the exact containment the lane's evidence class
    # rests on. Both probes ran on 2.1.220, after the fix, so the
    # unqualified wording read as a platform guarantee. The floor must
    # travel with the claim.
    assert "Claude Code 2.1.216" in body
    assert "silently reverted to the default agent" in body
    # 0.14.4 fable review I1: the two pins above lock the DESCRIPTION of
    # the hazard. The operative half - that the driver checks the version
    # and that the lane is unavailable rather than degraded below the
    # floor - deleted green. Pin-integrity instance twelve, and once
    # again inside a fix for an overclaim.
    nbody = _norm(p)
    # 0.15.0: was two fragments; neither locked the reason, which is the
    # sentence's whole point.
    assert ("The driver checks `claude --version` against the floor "
            "before dispatching this seat; below it, the Fable lane is "
            "unavailable rather than degraded, because a silently "
            "unpinned fully-tooled agent is not a weaker reviewer, it "
            "is a different one.") in nbody
    # 0.27.0 item 50: this file stated flatly that "your conversation
    # state persists across the resume". Three `No transcript found`
    # failures were measured above the floor, so the seat must be told
    # the truth: usually, not always, and say so when it does not have it.
    assert ("Your conversation state USUALLY persists across a resume, "
            "and it is not guaranteed to. A resume can fail outright, or "
            "succeed with your earlier rounds gone. When the driver asks "
            "you to recall something from an earlier round, answer "
            "honestly - if you do not have it, say so plainly. A seat "
            "that guesses hides the lane's failure.") in nbody
    # The floor qualifies CONTAINMENT only; naming which half it bounds
    # is the whole point of the 0.27.0 change.
    assert "The CONTAINMENT half has a FLOOR" in nbody
    assert "your conversation state persists across the resume" not in nbody


def test_escalation_implementer_exists_and_pins():
    p = AGENTS / "escalation-implementer.md"
    assert p.is_file()
    body = _read(p)
    fm = _frontmatter(body)
    assert "model: fable" in fm
    assert "enumerated decision envelope" in body
    assert "DECISIONS" in body
    assert "DEVIATIONS - must be `none`" in body
    assert "only with user consent" in body


def test_skill_routes_required_review_and_panels():
    skill = _read(SKILL_DIR / "SKILL.md")
    required = ("Required before round 1: the agents/fable-reviewer.md "
                "whole-branch review runs on the same range, its raw "
                "reply is retained as a range-bound artifact, and the "
                "round-1 brief cites that artifact with the session's "
                "per-finding adjudications.")
    assert skill.count(required) == 1
    assert skill.count("Panels: any reviewer-lane combination per "
                       "references/panels.md.") == 2
    assert skill.count("a finding, with one carve-out: "
                       "envelope-designated escalation-lane DECISIONS") == 1


def test_panels_reference_pins():
    p = REFERENCES / "panels.md"
    assert p.is_file()
    body = _read(p)
    assert ("Valid compositions: Sol+Kimi, Sol+Fable, Kimi+Fable, "
            "Sol+Kimi+Fable.") in body
    assert ("Every panel contains at least one cross-vendor lane "
            "(Sol or Kimi); an all-Claude panel is invalid.") in body
    assert ("A terminal verdict counts only when it cites the FINAL "
            "subject revision; a verdict against a stale revision is "
            "input, never terminal.") in body
    assert "hub-and-spoke" in body
    # 0.14.4 drift triage: panels.md states the Fable lane's failure
    # mode as "agent death, which is loud". That is true only at or
    # above the floor - below it the lane had a SILENT failure mode
    # that defeats the pin and the allowlist together, so the floor
    # belongs next to the claim it qualifies, not only in the agent file.
    #
    # 0.14.4 fable review I1: "Claude Code 2.1.216" occurs TWICE here -
    # the floor header and the changelog citation - so on its own it does
    # not even lock the paragraph's EXISTENCE: delete the whole floor and
    # the citation keeps it green. Pin the operative sentences instead,
    # and pin the header string by a phrase that occurs exactly once.
    nbody = _norm(p)
    assert nbody.count("Harness floor: Claude Code 2.1.216") == 1
    # 0.15.0: was two fragments. The coverage checker proved neither
    # locked the routing half, which is the part that stops a quiet
    # reduction to a smaller panel.
    assert ("Check `claude --version` before dispatching the Fable "
            "lane; below the floor the lane is UNAVAILABLE, not "
            "degraded, and the case routes to fallbacks.md's "
            "`panel-lane-unavailable` - which, like every other lane "
            "loss, stops at the consent gate rather than quietly "
            "convening a smaller panel.") in nbody
    # I2: this file must not state class mechanics. The below-floor case
    # routes to the consent gate like every other lane loss; the earlier
    # wording claimed an automatic drop to remaining lanes, contradicting
    # fallbacks.md AND panels.md's own paragraph 22 lines below it.
    assert "drops to its remaining lanes" not in nbody
    assert "panel-lane-unavailable" in nbody
    # 0.27.0 item 50: this file said round continuity "is evidenced by
    # transcript recall" and nothing made the driver CHECK it, so a resume
    # that succeeded while state was quietly lost passed unnoticed. The
    # recalled item must never ride the resume message or a re-primed
    # agent echoes it back and the check self-satisfies.
    assert ("Round continuity is not assumed, it is CHECKED. Each "
            "resumed round the driver asks the seat for something "
            "established in an EARLIER round that the current message "
            "does not contain, and records the answer. An item that "
            "rides the resume message proves nothing, because a freshly "
            "re-primed agent echoes it back.") in nbody
    # The old text named ONE failure mode, agent death. A failed resume
    # leaves the agent not dead, so a driver meeting `No transcript found`
    # did not recognize the panel-lane-loss case and re-dispatched fresh.
    assert ("This lane has more than one failure mode. The agent can "
            "die; a resume can fail to reach its transcript; and a "
            "resume can succeed with the conversation state gone. All "
            "three are lost round continuity and all three route to "
            "fallbacks.md's panel-lane-loss. Only the first is agent "
            "death.") in nbody
    # The floor bounds CONTAINMENT, never continuity. Three failures were
    # MEASURED on 2.1.233, above this floor.
    assert ("The floor does NOT make resume reliable. Resume is "
            "best-effort at every version above it. A version above the "
            "floor buys containment, never continuity.") in nbody
    # The retired overclaim must be gone, not merely qualified elsewhere.
    assert "Everything in the paragraph above holds only at or above it" not in nbody
    # The evidence this whole change rests on must not be deletable-green.
    # 0.27.0 exists because a claim outran the probe behind it; shipping
    # the replacement claim with its own evidence unpinned would reproduce
    # that class exactly.
    assert ("Measured: `No transcript found` three times on 2.1.233, "
            "above this floor, and nine clean resumes across five "
            "conditions on 2.1.237, which is too few to bound an "
            "intermittent fault. Records: docs/superpowers/plans/rounds/"
            "2026-08-19-item50-resume-probe/probe-record.md.") in nbody


def test_backup_lane_panel_participation():
    bl = _read(REFERENCES / "backup-lane.md")
    assert ("Panel participation: a user-invoked panel per "
            "references/panels.md is a second sanctioned entry route - "
            "the invocation itself is the consent, with no fallbacks "
            "banner (nothing degraded); containment, per-round "
            "evidence, and the write-probe apply unchanged, and no "
            "failure class is recorded because nothing "
            "substituted.") in bl


def test_fallbacks_panel_lane_loss():
    fb = _read(REFERENCES / "fallbacks.md")
    assert "panel-lane-loss" in fb
    assert ("A lost lane stops the panel at the consent gate - "
            "continuing with fewer lanes never happens "
            "automatically.") in fb
    assert "records DEGRADED" in fb
    # 0.14.4 fable review I2: panel-lane-loss covers a lane failing
    # MID-panel. A lane the harness cannot host at all is a different
    # condition with a different disposition - nothing was dispatched, so
    # no round is spent and nothing is quarantined - and it had no home
    # here, which is what pushed class mechanics into panels.md where
    # they are barred.
    nfb = _norm(REFERENCES / "fallbacks.md")
    assert "panel-lane-unavailable" in nfb
    assert ("no round was dispatched, so nothing is spent and nothing "
            "is quarantined") in nfb
    # 0.15.0: was a fragment. The coverage checker proved all three
    # rules of the disposition unlocked - including the only place that
    # says the driver must state the convenable composition BEFORE
    # round 1, which is what stops a quiet reduction.
    assert ("The disposition is the same in the one respect that "
            "matters: the panel cannot silently convene without "
            "it.") in nfb
    assert ("Before round 1 the driver states which lanes it can "
            "actually convene and which it cannot, with the reason, and "
            "the user chooses - proceed with the convenable "
            "composition, substitute, or abort.") in nfb
    assert ("The panel invariant still binds whatever is chosen: at "
            "least one cross-vendor lane, so a composition reduced to "
            "Fable alone is not a panel and cannot proceed as "
            "one.") in nfb
    # 0.27.0 item 50: panel-lane-loss covered only "a dead Fable panel
    # subagent". A resume that cannot reach a transcript leaves the agent
    # NOT dead, so nothing routed it and the consent gate above was never
    # reached - the reported session re-dispatched fresh and the panel
    # still reported as a panel. The Kimi lane already carries this class
    # (fallbacks.md "resume failure: one same-parameters retry"), so this
    # mirrors a proven shape rather than inventing one.
    assert ("for the Fable panel seat, both a dead subagent and a resume "
            "that cannot reach its transcript are directly this "
            "class") in nfb
    assert ("Fable resume failure: a resume that returns no reachable "
            "transcript gets one same-parameters retry, then the consent "
            "gate. The agent is not dead, so this is not agent death; it "
            "is lost round continuity, and it is never resolved by a "
            "silent fresh dispatch.") in nfb
    assert ("A fresh dispatch the user consents to is RECORDED as a fresh "
            "dispatch, and the lane's round continuity is recorded as "
            "broken from that round on. A panel that lost continuity "
            "cannot report as an intact one.") in nfb


def test_plan_format_panel_and_envelope_pins():
    fmt = _read(REFERENCES / "frozen-plan-format.md")
    assert ("A panel records Verification status: FULL only when every "
            "participating lane's per-round evidence was clean AND "
            "every terminal verdict cites the final subject "
            "revision.") in fmt
    assert ("A task the plan routes to the escalation lane carries an "
            "enumerated decision envelope; DECISIONS inside the "
            "envelope are authorized outcomes, not drift.") in fmt


def test_notes_driver_seat_sections():
    notes = _read(REFERENCES / "model-prompting-notes.md")
    assert "## The session driver seat" in notes
    assert "### Fable 5" in notes
    assert "### Opus 5" in notes
    assert "## Fable 5 (the session side)" not in notes
    assert "subagent-resume-probe.md" in notes
    # both runtime parsers still resolve the primary declaration and
    # the ordering rule holds (backup declarations stay behind it)
    m = re.search(r"Canonical model id: `([^`\n]+)`", notes)
    assert m and m.group(1)
    assert (notes.index("Canonical model id:")
            < notes.index("Canonical backup reviewer model id:"))
    # 0.27.0 item 50, found by the Fable pre-build sweep: this bullet
    # asserted "conversation state persists across resume" for THREE
    # named seats, one of which (the whole-branch reviewer) has no resume
    # in its contract at all - verified by grep, zero hits. It is the same
    # class the 0.27.0 cycle exists to close, in the file every dispatch
    # reads, so leaving it would let the retired guarantee survive the fix.
    nnotes = " ".join(notes.split())
    assert ("Same-harness Fable seats that RESUME (panel lane, "
            "escalation - the whole-branch reviewer is single-dispatch "
            "and never resumes)") in nnotes
    assert ("Conversation state usually persists and is NOT guaranteed "
            "to - `No transcript found` was measured three times on "
            "2.1.233, above the 2.1.216 floor.") in nnotes
    assert "conversation state persists across resume and" not in nnotes


def test_readme_reshuffle_pins():
    readme = _read(REPO / "README.md")
    assert "## Panels" in readme
    assert "fable-reviewer" in readme
    assert "fable-panel-reviewer" in readme
    assert "escalation-implementer" in readme
    assert "private" not in readme.lower()
    # 0.13.0 pins survive the restructure byte-exact
    assert ('G -->|run backup lane| BK["cross-vendor backup reviewer'
            ) in readme
    assert ("references/backup-lane.md` | The cross-vendor backup "
            "reviewer lane") in readme
