# Backup lane (Kimi K3), reopened debate, round 2 reply

RESUMED call in the same debate home and session. Validator `status: clean`
in RESUME form, so the session-scoped records were correctly ABSENT and the
resume did not silently start a new session. Mirror delta 0. `toolsHash` and
`systemPromptHash` matched round 1 byte for byte. Final reply only; the
client's tool-call narration is not retained.

---

## q1 — Concede

  I concede, and I verified the mechanism against the checker source before conceding, same as the other lane did:

  - Region bodies are whitespace-normalized and collected from between the markers (`contract_coverage.py:54-55`, `:112-145`), and coverage is containment in ONE direction: the pin must contain the region whole, and "a pin that the region contains is a fragment" (`contract_coverage.py:390-396`). So a weakening sentence appended INSIDE the region grows the normalized body beyond any existing pin, `uncovered()` reports it, and `test_every_marked_region_is_locked_by_a_pin` fails (`test_contract_coverage.py:689-692`). Confirmed.
  - Deleting or renaming the markers trips `test_declared_regions_match_the_documents` (`test_contract_coverage.py:675-686`). Confirmed.
  - My ordinary `"paragraph" in body` assert detects edits inside its literal and nothing else. I have no answer to the appended-sentence case under my own proposal — nothing in my mechanism catches it. That is precisely the hole.

  Two additions, not defenses. First, my no-markers proposal also contradicted the frozen plan, which already declares exactly these two ids — `home-skill-root-disposition` and `home-skill-root-disposition-limit` (plan:133) — and the standing rule that adding a region means editing DECLARED_REGIONS (plan:58). The plan's mechanism is strictly stronger than mine on the four cases, so there is nothing to defend with. Second, an honest residual the other lane's table does not cover: a weakening sentence appended AFTER the region's `contract:end` marker still passes everything — the region bounds in-region growth and marker deletion, not adjacency outside its own markers. That residue is shared by every available mechanism and is strictly smaller than the plain-pin hole, so it changes nothing about the concession.

  And one acknowledgment from the round result: my argument 4 is refuted and I accept it — `toolsHash`, `systemPromptHash`, `toolCount` and exact-list equality pin the effective CONTEXT surface, not directory contents; a populated `<debate-home>/skills/` with `Skill` denied and no prompt change would move none of them. The conclusion survived on the no-shipped-writer argument (`tools/new-kimi-lane-home.ps1:902` as the only write site), not on argument 4.

  ## q2 — The two region bodies

  Both replace `backup-lane.md:342-354` (the "Enumerate that root..." sentence through "...claim nothing for it."). The pinned sentence at :340-342 ("`~/.agents/skills/` lives in the user's own home...") is still true and stays put, outside the regions, as the frozen plan's own Task 5 kept it (plan:603-605). No backslashes in either body.

  ```
  <!-- contract:start id=home-skill-root-disposition -->
  Enumerate that root before round 1 and record its COUNT, never its
  contents - the repo is public. MEASURED 2026-08-03 on kimi-code 0.31.1,
  and no longer unprobed: a canary skill planted in that root was
  REACHABLE when `--skills-dir` was omitted - the wire carried the
  invocation and a `skill_activation` message delivering the body - and
  was NOT found when the flag was passed, the lookup returning the
  calibrated not-found result exactly. Record:
  docs/superpowers/plans/rounds/2026-08-03-home-skills-root/probe-record.md
  <!-- contract:end -->
  ```

  ```
  <!-- contract:start id=home-skill-root-disposition-limit -->
  The disposition is bound to what the probe reached: one skill, named
  exactly, at the home root, on kimi-code 0.31.1. Suppression was measured
  for that root ALONE; the two project roots were never canaried, and
  their exclusion rests on the flag's measured replacement semantics and
  the client's own help text, with preflight-3 remediation clearing them
  in the mirror regardless. The flag REPLACES discovery with its target
  rather than adding to it, so it does not suppress its own target - it
  selects it - and its suppression of the other roots holds only while
  `<debate-home>/skills/` is EMPTY: the builder creates it empty and
  asserts that at build, and no per-round check re-verifies it at
  dispatch. A client whose skill delivery changes shape retires this
  measurement rather than inheriting it.
  <!-- contract:end -->
  ```

  Immediately after the second region, ordinary prose with its own updated pins (replacing the three asserts at `test_backup_lane.py:861-867`, tests first per plan:59):

  > The load-bearing control as the lane ships is the `Skill` deny list — a discovered skill cannot be invoked, measured in cells A and B of the same record. Keep passing `--skills-dir` on every call, fresh and resumed, as a measured second layer, and claim for it exactly what was measured: replacement, conditional on an empty target, on 0.31.1.

  Length judgment, as requested: the first region wraps to about 8 lines, the second to about 10. Each fits one pin — adjacent string literals fold into a single constant for the checker (`contract_coverage.py:175-176`), so line count is not the binding constraint, and both bodies are comparable to existing multi-literal pins (`test_backup_lane.py:848-853` is six literals for a shorter text; the `lane-lock` region is far longer and pinned whole). Neither is too long for one pin. I moved the keep-passing/load-bearing prose OUT of region 2 precisely to keep it that way.

  ## q3 — Concede the narrow version

  There is no cost to the narrow version, and I should have stated it from the start. The project roots are cleared by preflight-3 remediation in the mirror regardless (backup-lane.md:338-340, :378-382), so no lane decision consumes the wide claim — it protects nothing and buys nothing. The narrow claim loses exactly zero coverage.

  Why I stated the wide one: I treated the home-root measurement plus the replacement semantics as licensing a general statement about all auto-discovered roots. That is reasoning from semantics, not from evidence — the same move I attacked in claim 2's original wording, and I even flagged it myself in round 1 as "1 measured + 3 inferred" before letting the inferred half into my contract text anyway. Tidiness of the general statement is not evidence, and the help text is documentation — plan:84 itself carried it as UNVERIFIED before this probe, and the probe's canaries did not touch the project roots (probe-record.md:39-45). The region bodies above state the narrow version: "Suppression was measured for that root ALONE."

  ## q4 — Agree, and the check still earns its place on a narrower justification

  Yes, that is the honest framing, and it matches this repo's own standard. A fault seam proves the detector fires for the reason it claims — "a test is not evidence until it has been watched to FAIL for the reason it claims" (plan:52) — and the round-2 verification established that no shipped writer exists after construction (`tools/new-kimi-lane-home.ps1:902` is the only write site). So the mutation test demonstrates the check CAN fail, not that the state it detects ever WILL occur in the shipped lane. Presenting it as threat evidence would be exactly the defect class this cycle keeps naming: a claim wider than its evidence.

  The check still earns its place, re-scoped: it is a POSTCONDITION on the one measured writer, not a guard against adversarial ones. The builder is code, and code changes — a future edit that seeds content, a copy that starts following a junction, a refactor that swaps creation order. Asserting that the directory the builder just created is empty fails closed at the single moment content could legitimately enter, and its cost is one assertion against an act the builder is already performing. What it is not is a control against unknown writers, and the contract text should not say or imply that it is — my region 2 wording says "the builder creates it empty and asserts that at build," which claims exactly the postcondition and nothing more.

  ## Still unresolved

  1. The SKILL.md replacement passage (round 1, q2) remains ordinary unpinned prose, as its predecessor was. The appended-sentence hazard from q1 applies to it in principle; I have not proposed a region there because the frozen plan declares the two ids for backup-lane.md only, and SKILL.md preflight prose has historically lived under targeted string pins rather than regions. If the debate wants uniformity, that is a third region decision; otherwise it stands as accepted historical practice.
  2. The residual I named in q1: a weakening sentence appended AFTER a region's `contract:end` passes every check. Both lanes' mechanisms share it; no proposal on the table closes it.
  3. The pins and DECLARED_REGIONS edits themselves remain unexecuted — this debate has produced the text, and the tests-first ordering (plan:59) plus the `test_backup_lane.py:848-853` and `:861-867` rewrites are still to be done by whoever implements.

  Nothing else.
