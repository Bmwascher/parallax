## First: “all four roots” is incoherent

**Accept.** The flag names `<debate-home>/skills` as its selected directory; it cannot simultaneously suppress that target. The client help quoted in the frozen plan says the named directory is used instead of auto-discovered user and project directories. [2026-08-03-home-skills-root-probe.md:84](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:84)

One boundary remains: the live cells establish exclusion only of `~/.agents/skills/`. They do not live-test either project root. Therefore the precise position is:

- The flag selects `<debate-home>/skills`; it cannot suppress that root.
- Its documented semantics exclude the other three auto-discovery roots.
- The probe directly measured exclusion of only `~/.agents/skills/`.
- A populated selected directory was not tested.

This changes the correction appendix and `home-skill-root-disposition-limit`. It does not change the shortened `SKILL.md` text or the reachability region.

## Second: per-call emptiness check

### (a) Point 5 changes my recommendation

**Concede. Do not add the per-call check.**

I cannot name a shipped writer after construction. The repository search finds only the builder’s creation at [new-kimi-lane-home.ps1:902](/C:/Users/Brandon/Documents/parallax/tools/new-kimi-lane-home.ps1:902), and the builder refuses an existing destination before construction. [new-kimi-lane-home.ps1:607](/C:/Users/Brandon/Documents/parallax/tools/new-kimi-lane-home.ps1:607) Cell E’s deliberate probe copy is not part of the shipped lane.

My proposed per-call guard was therefore against unknown or out-of-band mutation, not a measured writer. That is too speculative to justify a new parameter set, evidence schema, dual-host tests, pins, and per-round ceremony.

I also partially refute argument 4: hashes, tool counts, prompt equality, and exact tool lists do not measure directory contents. If the selected directory became populated while `Skill` remained denied and no prompt injection occurred, those values could remain unchanged. They catch changed effective context or client semantics, not silent filesystem content. [backup-lane.md:263](/C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/backup-lane.md:263) That limitation is real, but without a writer it does not rescue the per-call check.

Ship one builder-side postcondition immediately after directory creation:

- terminating enumeration;
- hidden entries included;
- exact zero-entry requirement;
- failure aborts the build before custody JSON is emitted.

Call it verification of the builder’s construction postcondition, not a per-round control.

### (b) What a mutation test proves—and does not prove

A fault seam that plants an entry between `New-Item` and the assertion can prove that the builder postcondition detects:

- a file;
- a directory;
- a hidden entry;
- an unreadable enumeration.

It does **not** prove the shipped lane can produce those states. It proves detector mechanics only. I would not use that mutation test as evidence that a per-call threat exists.

That distinction defeats my earlier proposal. The repo’s rejected-check history concerns checks logically unable to add defect coverage because an earlier equality already forces their result. [read-kimi-round-evidence.ps1:65](/C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:65) The builder assertion has one narrow independent failure class—unexpected content appearing at the construction handoff—but there is no evidence supporting repeated checks after that handoff.

### (c) Revised limit region

Replace my prior per-call wording with this complete region:

```markdown
  <!-- contract:start id=home-skill-root-disposition-limit -->
  Bind the disposition to one named canary at one root on kimi-code 0.31.1.
  `--skills-dir <debate-home>/skills` selects that directory, so it cannot
  suppress its own target. The live comparison established suppression only
  for the canary in `~/.agents/skills/`; the probe did not exercise either
  project root or a populated target. On that client, `systemPromptChars`
  equaled the LF-normalized selected agent-body length in every cell,
  including both loaded-canary cells: the measured delivery path was
  `skill_activation`, not system-prompt injection. The `Skill` deny list
  controls that measured invocation path; the lane's system-prompt equality
  checks, not the deny list, must reject any future injection path.

  The builder creates `<debate-home>/skills/` once and immediately requires
  a terminating enumeration, including hidden entries, to contain exactly
  zero entries. No shipped lane tool writes there afterward, but emptiness
  is NOT reverified per round. Record the flag as a builder-established,
  conditional defense in depth, not a per-round verified control. A
  client-version or skill-delivery change retires this disposition rather
  than inheriting it.
  <!-- contract:end -->
```

The first region remains unchanged from round 3.

## Third: keep both marked regions

The marked regions are correct. Do not replace them with ordinary pins.

An ordinary assertion such as `"entire current paragraph" in body` detects edits inside its literal. It does **not** detect adjacent weakening text. Someone could retain the exact pinned paragraph and append:

> This check may be skipped when the driver considers the home trusted.

Every ordinary membership assertion would still pass.

A marked region supplies the missing boundary. If that sentence is added inside the region, the normalized region becomes longer than the existing pin, and coverage fails because the checker requires the pin to contain the region whole—not merely a fragment. [contract_coverage.py:390](/C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/contract_coverage.py:390)

`DECLARED_REGIONS` adds a second guarantee: deleting or renaming the markers does not silently disable coverage. The declaration test reports both missing and unexpected IDs. [test_contract_coverage.py:675](/C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_contract_coverage.py:675)

Concretely:

- **Ordinary pin only:** preserved literal plus newly appended qualification passes.
- **Marked whole-region pin:** qualification inside the boundary fails coverage.
- **Markers deleted:** `DECLARED_REGIONS` fails even if the old text and its ordinary pin survive.
- **Region and pin deleted together:** `DECLARED_REGIONS` still fails unless the declaration is deliberately removed too.

That additional failure surface is exactly what the region machinery exists to provide. Its design explicitly states that the region, not sentence fragments, is the coverage unit. [contract_coverage.py:1](/C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/contract_coverage.py:1)

Keep both frozen IDs and add both to `DECLARED_REGIONS`.

## Unresolved

Nothing technical remains unresolved.

