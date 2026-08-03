## Verdict

Claim 1 stands. Claim 3 stands. Claim 2 overreaches, and Claim 4 is defensible only as an observation of the tested composition—not as two independently established controls.

### Claims adjudicated

1. **REACHABLE — confirmed.** Cell D records the exact `Skill` call, the matching result, and the separate `skill_activation` message containing the canary body and nonce from `~/.agents/skills/.../SKILL.md`. That is direct delivery evidence. [probe-record.md:136](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-03-home-skills-root/probe-record.md:136)

2. **“Replaces discovery and suppresses all four roots” — refuted at that reach.** C/D establish suppression of `~/.agents/skills/` when the flag points at an empty `<debate-home>/skills/`. They do not exercise either project root, and no cell passes the flag while the explicitly named directory contains the canary. Cell E proves only that `<debate-home>/skills/` is auto-discovered when the flag is omitted. [probe-record.md:39](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-03-home-skills-root/probe-record.md:39) [probe-record.md:127](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-03-home-skills-root/probe-record.md:127)

   The client help text supports “instead of auto-discovered directories,” but that is text evidence, not a four-root live measurement. [2026-08-03-home-skills-root-probe.md:84](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:84)

3. **The empty-directory precondition is unchecked — confirmed.** The builder writes `extra_skill_dirs = []` and creates `<debate-home>/skills` once. [new-kimi-lane-home.ps1:872](/C:/Users/Brandon/Documents/parallax/tools/new-kimi-lane-home.ps1:872) [new-kimi-lane-home.ps1:900](/C:/Users/Brandon/Documents/parallax/tools/new-kimi-lane-home.ps1:900)

   The round validator has no debate-home or skills-directory parameter, and its per-call checks cover prompt, route, model, tool surface, hashes, and prompt length—not directory contents. [read-kimi-round-evidence.ps1:15](/C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:15) [read-kimi-round-evidence.ps1:796](/C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:796) The written per-round contract names the same evidence set. [backup-lane.md:213](/C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/backup-lane.md:213)

4. **“No observed hole in the tested shipped composition” stands; “two independent things hold it” does not.** The committed agent explicitly denies `Skill`, and A/B showed neither primary readout firing. [kimi-reviewer-agent.md:4](/C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/kimi-reviewer-agent.md:4) [probe-record.md:74](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-03-home-skills-root/probe-record.md:74)

   But A/B ran with both the deny list and flag present. C/D isolate the flag only by switching to the probe agent. No cell isolates the reviewer deny list with the flag omitted, and no per-round check establishes the flag’s empty-target precondition. The controls are structurally separate; their end-to-end independence was not measured.

## Question 1: exact replacement text

For [SKILL.md:68](/C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/SKILL.md:68), replace the stale 2026-07-31 paragraph through “tree’s skills and agents” with:

```markdown
   The 2026-07-31 canary comparison was confounded: the reviewer denied
   `Skill`, so runs with and without `--skills-dir` could not distinguish
   "root not read" from "tool unavailable." A superseding invocation probe
   on 2026-08-03, kimi-code 0.31.1, showed that passing
   `--skills-dir <debate-home>/skills` while that directory was empty
   suppressed a named canary in `~/.agents/skills/` that loaded when the
   flag was omitted. That measurement covers the user-home root under that
   condition; it does NOT establish suppression of either project root,
   and no per-round check proves the named directory is still empty at
   dispatch. This enumeration remains the PRIMARY control for the reviewed
   tree's skills and agents.
```

For [backup-lane.md:341](/C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/backup-lane.md:341), replace the home-root disposition and obsolete mitigation paragraph with:

```markdown
  `~/.agents/skills/` lives in the user's own home, is not relocated by
  `KIMI_CODE_HOME`, and NOTHING this lane runs removes it.
  <!-- contract:start id=home-skill-root-disposition -->
  MEASURED 2026-08-03 on kimi-code 0.31.1: with `Skill` offered and
  `--skills-dir` omitted, a named canary planted in that root produced a
  `Skill` call, a successful result, and a separate
  `context.append_message` whose `origin.kind` was `skill_activation`,
  whose `origin.skillPath` named the canary's `SKILL.md`, and whose body
  carried the per-run nonce. This root is REACHABLE by the client; it is
  no longer unprobed. The committed reviewer still denies `Skill`.
  Enumerate the root before round 1 and record its directory count and
  whether it is non-empty, but do not record the directory names. This is
  an environment record of reachable external instruction inventory, not
  a control and not evidence that any real skill was invoked.
  <!-- contract:end -->
  <!-- contract:start id=skills-dir-conditional-control -->
  MEASURED in matched invocation cells: passing
  `--skills-dir <debate-home>/skills` while that directory was empty made
  the home-root canary match the calibrated not-found result; omitting the
  flag loaded and delivered it. This verifies suppression of
  `~/.agents/skills/` under the tested condition. It does not establish
  suppression of either project root or of the explicitly named skills
  directory.

  The flag is a CONDITIONAL control: its relevant precondition is that
  `<debate-home>/skills/` remains empty. The builder creates that directory
  empty and writes `extra_skill_dirs` empty, but the per-round evidence
  does not recheck the directory's contents at dispatch. Keep passing the
  flag, but until that precondition is checked for a round, describe it as
  measured suppression with an unverified precondition, not as an
  unconditional or per-round-verified control.
  <!-- contract:end -->
```

This wording deliberately does not preserve “all four roots”: the measurement does not support it.

Both new IDs must be added to `DECLARED_REGIONS`, and each complete region body must appear whole in one test pin. The existing stale pins at [test_backup_lane.py:842](/C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_backup_lane.py:842) through [test_backup_lane.py:867](/C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_backup_lane.py:867) must be replaced. `DECLARED_REGIONS` currently ends at [test_contract_coverage.py:672](/C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_contract_coverage.py:672). The proposed reference text contains no backslashes, satisfying the explicit test at [test_backup_lane.py:118](/C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_backup_lane.py:118).

## Question 2: retain the enumeration?

I would keep it, but strip it of control status.

The case for keeping it:

- The source is outside lane custody and nothing removes it. [backup-lane.md:339](/C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/backup-lane.md:339)
- Its contents are now known to be reachable by this client, so recording non-emptiness describes real external instruction inventory.
- A count supplies useful drift evidence without publishing private skill names; the probe record follows that privacy boundary. [probe-record.md:260](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-03-home-skills-root/probe-record.md:260)

The case for dropping it:

- The enumeration does not validate either actual control. It does not prove the reviewer deny list held, and it does not prove `<debate-home>/skills/` remained empty.
- Whether the home root holds one skill or 27 does not alter the measured reachability conclusion.
- Repeating a non-gating observation every round can be mistaken for a safety check.

On balance: keep only `directory count + non-empty`, label it an environment record, and explicitly say it is not a gate or control. Do not retain “record what it holds,” because that invites recording names and implies more operational significance than the enumeration has.

## Question 3: gate defect and oracle search

The clause should have read:

> A positive Skill invocation requires an exact `Skill` call for the canary, a matching non-error `tool.result`, and, after that pair in the same cell’s wire slice, a `context.append_message` whose `origin.kind` is `skill_activation`, whose `origin.skillPath` names the expected canary `SKILL.md`, and whose body carries the per-run nonce. The result establishes lookup completion and status; the activation message establishes delivery.

For C/E2, the calibrated complete `event.result` comparison remains appropriate because the question is specifically whether the lookup returned the client’s not-found result. [probe-record.md:113](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-03-home-skills-root/probe-record.md:113)

The defect spreads beyond the three gate branches inside the frozen plan:

- The “measured fact” generalizes raw output into readable Skill evidence. [2026-08-03-home-skills-root-probe.md:81](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:81)
- The prompt section says the measurement is the result record or its absence. [2026-08-03-home-skills-root-probe.md:131](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:131)
- Readout 1 says the canary body lands in `tool.result`. [2026-08-03-home-skills-root-probe.md:509](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:509)
- The positive and VOID branches repeat the nonce-bearing-result assumption. [2026-08-03-home-skills-root-probe.md:523](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:523)

Lines 517 and 571 are sound: a matching result can establish that a call completed, and its exact payload can serve as a calibrated not-found oracle. They do not require the result to contain the skill body. [2026-08-03-home-skills-root-probe.md:517](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:517) [2026-08-03-home-skills-root-probe.md:571](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:571)

I searched active code and oracle surfaces under `tools/`, `evals/`, `skills/`, `agents/`, `commands/`, `hooks/`, and `.github/`, plus current plans/specs.

There are other result-based oracles, but they are tool-specific rather than another generic Kimi assumption:

- A Read result must contain the startup header. [evals.json:16](/C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/evals.json:16)
- A range-read/Bash result must contain the diff evidence. [evals.json:27](/C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/evals.json:27)
- Edit/Write success results are followed by independent Read/Grep read-back before final state is accepted. [evals.json:67](/C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/evals.json:67)
- The behavioral harness merely preserves the structured result’s content, call ID, and error status for those tool-specific graders; it does not itself infer a tool effect. [run_behavioral_evals.py:396](/C:/Users/Brandon/Documents/parallax/evals/tools/run_behavioral_evals.py:396)
- `read-kimi-round-evidence.ps1` does not inspect nested `tool.call`, `tool.result`, or `skill_activation` records at all. [read-kimi-round-evidence.ps1:796](/C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:796)

So: **yes, other oracles read particular tools’ evidence from their results; no, I found no second active oracle that generalizes one tool’s result semantics to every tool.** The repeated generic mistake is concentrated in this frozen probe plan.

### Unresolved

- The flag’s effect on either project root and on a populated explicitly named directory remains unmeasured.
- Dispatch-time emptiness of `<debate-home>/skills/` remains unverified.
- The reviewer deny list’s independent causal protection was not isolated from the flag.
- Whether the home-root count remains mandatory is a policy choice; I recommend keeping it only as a non-gating environment note.

