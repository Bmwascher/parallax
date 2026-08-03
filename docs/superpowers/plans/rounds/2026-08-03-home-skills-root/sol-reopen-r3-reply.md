Appending a dated correction is better than editing the probe claims in place. The file explicitly distinguishes its prewritten header from results appended during execution; preserving the original interpretation plus its later adjudication maintains that chronology. [probe-record.md:6](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-03-home-skills-root/probe-record.md:6) The correction should explicitly retract both “verified control” and “REPLACE discovery” at [probe-record.md:211](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-03-home-skills-root/probe-record.md:211). I would not alter those original lines.

## Ask 1: final contract regions

Neither region is too long for one pin. Excluding markers, the first is 674 characters and the second 1,220; each fits comfortably in one exact triple-quoted or compile-time-concatenated Python string. Both contain zero backslashes.

```markdown
  <!-- contract:start id=home-skill-root-disposition -->
  Record this measured disposition for kimi-code 0.31.1: with `Skill`
  offered and `--skills-dir` omitted, a named canary in
  `~/.agents/skills/` was loaded and delivered by a `skill_activation`
  message carrying its source path and nonce. The root is REACHABLE by the
  client, not unprobed. Before round 1, enumerate the root and record only
  its directory count and whether it is non-empty; never record the
  directory names. Treat that enumeration as an environment record of
  reachable external instruction inventory, not as a control or evidence
  that any real skill was invoked. Cite the probe record at
  docs/superpowers/plans/rounds/2026-08-03-home-skills-root/probe-record.md.
  <!-- contract:end -->
```

```markdown
  <!-- contract:start id=home-skill-root-disposition-limit -->
  Bind the disposition to one named canary at one root on kimi-code 0.31.1.
  It does NOT establish `--skills-dir`'s effect on either project root or on
  a populated named directory. On that client, `systemPromptChars` equaled
  the LF-normalized selected agent-body length in every cell, including
  both loaded-canary cells: the measured delivery path was
  `skill_activation`, not system-prompt injection. The `Skill` deny list
  controls that measured invocation path; the lane's system-prompt equality
  checks, not the deny list, must reject any future injection path.

  Treat `--skills-dir <debate-home>/skills` as a control only for a call
  whose immediately preceding machine check reports that directory present,
  readable and empty. Before EVERY fresh or resumed call, run
  `tools/new-kimi-lane-home.ps1 -Path <debate-home> -CheckSkillsEmpty
  -LaneHome <lane-home> -DebateId <id> -OwnerPid <pid>
  -OwnerStartTicksUtc <ticks> -Nonce <nonce>`, require its one-line result to
  report `status: clean` and zero entries, and record that result. An absent,
  unreadable, non-directory or non-empty path makes the lane UNAVAILABLE
  before dispatch. A client-version or skill-delivery change retires this
  disposition rather than inheriting it.
  <!-- contract:end -->
```

The system-prompt statement stays inside the measured boundary supported by the five cells. [probe-record.md:74](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-03-home-skills-root/probe-record.md:74) [probe-record.md:85](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-03-home-skills-root/probe-record.md:85)

## Ask 2: choose (b)

Choose **(b): add `-CheckSkillsEmpty` as a third parameter set on `tools/new-kimi-lane-home.ps1`.**

I concede that (c) is technically possible. `read-kimi-round-evidence.ps1` could gain a pre-call parameter set and branch before its session-file logic. Its current architecture, however, is explicitly two post-call forms requiring session identity, model, provider, effort, agent, brief hash, and prior state. [read-kimi-round-evidence.ps1:10](/C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:10) [read-kimi-round-evidence.ps1:72](/C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:72) Adding a home-filesystem precondition there would require rescoping those parameters and creating an early path unrelated to the session evidence the rest of the script validates.

The home tool is the tighter owner:

- It creates the exact directory being checked. [new-kimi-lane-home.ps1:900](/C:/Users/Brandon/Documents/parallax/tools/new-kimi-lane-home.ps1:900)
- It already owns the debate-home path, sentinel, lock identity, and custody nonce. [new-kimi-lane-home.ps1:16](/C:/Users/Brandon/Documents/parallax/tools/new-kimi-lane-home.ps1:16)
- Its existing Build/Remove parameter sets already establish the pattern for a third, mutually exclusive home-state operation. [new-kimi-lane-home.ps1:32](/C:/Users/Brandon/Documents/parallax/tools/new-kimi-lane-home.ps1:32)

The new mode should:

1. Verify the same path and held-lock identity using the supplied debate ID, owner identity, and nonce.
2. Require `<debate-home>/skills` to be a directory.
3. Enumerate with hidden entries included and terminating error behavior.
4. Accept exactly zero entries.
5. On success, emit exactly one schema-valid JSON line and nothing on stderr:

```json
{"status":"clean","debateHome":"<resolved-path>","skillsDir":"<resolved-path>/skills","entryCount":0}
```

6. On absent, unreadable, non-directory, or non-empty: exit nonzero and emit no clean result.

This is still executed at the dispatch boundary; putting the implementation in the home tool does not move the check back to build time.

The cost is greater than four tests. Four failure-direction tests are necessary, but not sufficient. It also needs at least:

- clean-result schema and exact-zero success;
- hidden-entry rejection;
- wrong custody identity or nonce rejection;
- confirmation that every refusal leaves the home and lock unchanged;
- both `powershell.exe` and `pwsh.exe` coverage.

## Ask 3: amend the frozen plan

Make this **revision 7 of the existing plan**, not a new plan.

The plan explicitly reserved the observed `SUPPRESSED BY THE FLAG` branch for a reopened debate and made old Task 5 unreachable under that outcome. [2026-08-03-home-skills-root-probe.md:526](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:526) [2026-08-03-home-skills-root-probe.md:584](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:584) This is the planned reopening of the same objective, not a separate objective. A new plan would orphan the completed Tasks 1–4 and duplicate Task 6’s release bookkeeping.

Revision 7 should change exactly this scope:

- **Tasks 1–4:** unchanged and recorded complete. Add a revision note explaining that Task 4’s record now carries a dated correction; do not rewrite the executed task.

- **Task 5:** replace completely. The old Task 5 describes the unobserved `NOT REACHABLE` branch and cannot be patched into correctness. Its replacement owns:

  - probe-record correction appendix;
  - tests first;
  - `-CheckSkillsEmpty` parameter set and its dual-host tests;
  - replacement of the four stale backup-lane pins;
  - one direct pin for the shortened `SKILL.md` routing text;
  - the two whole-region pins above;
  - both `DECLARED_REGIONS` additions;
  - `SKILL.md` and `backup-lane.md` edits;
  - targeted and full validation.

- **Task 6:** amend, but retain its release role.

  - Rewrite backlog item 17’s resolution to say the root is reachable and the flag is controlled only after the new per-call machine check.
  - Rewrite the self-review claims at [2026-08-03-home-skills-root-probe.md:729](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:729); they currently describe the unobserved branch.
  - Retain the whole gate, behavioral eval, version bump, cache refresh, merge and push steps.
  - Add `CLAUDE.md` to the definite file list, not conditional: its live-verified backup-home contract currently names the tests governing this tool surface and should name the new check. [CLAUDE.md:76](/C:/Users/Brandon/Documents/parallax/CLAUDE.md:76)

The real cost is approximately nine implementation files plus the plan and probe-record amendment, a new security-sensitive parameter set in a 973-line PowerShell tool, and at least eight focused tests before the full dual-host gate.

The verification status does not silently transfer. Revision 6 remains historically `FULL`; revision 7 becomes `FULL` only when this reopened two-advisor debate is appended as verification of the amendment. The prior independent review remains valid for unchanged Tasks 1–4, while these rounds cover the replaced Task 5 and amended Task 6. The existing status is at [2026-08-03-home-skills-root-probe.md:753](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:753).

## Still unresolved

Only user authorization to expand Task 5 into revision 7. I see no remaining technical disagreement in the debate.

