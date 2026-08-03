# Fable per-task review — Task 3

**Range:** `d11be0c..c7a9c50` (one commit: the probe agent and the lane-contract
leak guard). **Seat:** `agents/fable-reviewer.md`, read-only.
**Verdict at issue: Ready to merge: Yes** — no Critical, no Important, three
Minors.

This is the reviewer's raw reply, retained as a range-bound artifact. The
session's adjudication of each finding is in `execution-deviations.md`.

---

### Strengths

- `tools/kimi-probe-agent.md` is verifiably the reviewer agent plus exactly the
  three frozen changes, compared line by line against the source rather than
  taken from the ledger: name changed (:2), `Skill` appended to `tools:` in the
  frozen order (:10), `Skill` absent from the 16-name deny list (:11-24), the
  PROBE ONLY block inserted (:30-41), and the description, deny-list order,
  `subagents: []` and body section byte-for-byte the same. No containment
  control beyond the single Skill move was weakened.
- The D15 vacuity fix is real, not cosmetic. The frozen plan's `_norm`-based
  pins could never match; `_lines` preserves newlines, and the non-emptiness
  anchors close the two-empty-sets hole: with `p_denied` empty,
  `r_denied - p_denied` returns 16 names, not `{"Skill"}`, so even the one set
  without its own count assert fails closed. No set difference is satisfiable by
  empty parses.
- Both `split("disallowedTools:")` parses fail closed: a file missing the marker
  raises IndexError rather than passing. A flow-style rewrite of the reviewer's
  `tools:` list, which would evade the line-anchored needle, is caught by
  `len(r_tools) == 5`.
- The leak-guard mutation evidence covers all three roots, one mutation per
  root, which is the right shape for a sweep: one mutation proves one root, and
  the plan's single-root Step 5 was correctly widened.
- The ledger states the UTF-8 deviation from ASCII with its reason (the
  constraint covers `tools/*.ps1`, not Markdown), confirmed against Global
  Constraints.

### Issues

**Critical:** none. **Important:** none.

The containment question resolves to: no path from `tools/kimi-probe-agent.md`
to a real review dispatch exists on this range. Verified by repo-wide grep that
the only files naming the path are the plan, the ledger, the round brief and the
test itself; `hooks/` and every `tools/*.ps1` are clean; and the load-bearing
control is not the sweep but the PINNED DISPATCH TEMPLATE, which names
`references/kimi-reviewer-agent.md` inside a contract pin (`backup-lane.md:25`,
pinned at `test_backup_lane.py:141`) plus the pinned "the ONLY agent
configuration" sentence (`backup-lane.md:277`, pinned at `:498`). A review
dispatched with the probe file requires diverging from that pinned template,
which is a separate red.

**Minor 1 — sweep evasion surface, enumerated as asked.** Caught by the
substring match: a leading `./` and any absolute forward-slash path. Real
mechanical evasions: a backslash spelling of the same path (the
backslash-absence check covers only `references/`); a bare
`kimi-probe-agent.md` with no directory; a paraphrase or variable-built path; a
non-Markdown file under the three roots (rglob is `*.md` only); a hook
(`hooks/hooks.json` and `hooks/superpowers-review-companion.ps1` exist and are
not swept); a script under `tools/`; any file outside the repo, including the
installed plugin cache. All theoretical today (verified clean by grep) and all
backstopped by the pinned template, but the sweep alone is a NAMING guard, not a
content guard: a new six-tool agent file copied under `references/` would pass
both new tests and be caught only by the pinned template and the "ONLY" pin. The
debate should record that the pinned template is the actual gate.

**Minor 2 — the `swept > 10` floor cannot see a vanished root.** The three
roots hold 9 + 5 + 3 = 17 Markdown files; `Path.rglob` on a missing directory
yields nothing without error, so a renamed `agents/` (12 survive) or
`commands/` (14 survive) narrows the sweep silently. Only losing `skills/` trips
the floor. Concrete failure: `commands/` becomes `cmds/` in a restructure, a
command file names the probe path, the sweep stays green. A per-root
non-emptiness assert would close it.

**Minor 3 — the `_lines` docstring claims one byte measurement for two files.**
"the agent files ARE CRLF on disk here (39 CRLF, 0 bare LF)" — 39 is the
reviewer file's line count; the probe file is 53 lines and its ending count is
not recorded, and per D15 the measurement predates the probe file. Functionally
moot since `read_text` folds either way, but the plural is a claim wider than
its evidence, in the helper whose docstring invokes exactly that rule.

### Scope of verification, stated by the reviewer

**Verified by reading:** the three-changes diff, the fail-closed parse paths,
the set-difference non-vacuity, the repo-wide absence of the probe path from
every dispatch-adjacent surface, the pinned-template backstop, the per-root file
counts. **Not verifiable from the seat, taken from the ledger:** the five
mutation runs and their messages, the 968/13 suite result, the byte-identical
reverts, the CRLF byte counts. Named as a gap, not assumed.

### Assessment

Ready to merge: Yes. The probe agent is exactly the frozen artifact, its guard
fails closed everywhere drivable on paper, no reachable dispatch path exists for
the loosened file, and the three Minors are debate inputs, not blockers; Task 4
can run without ambiguity, provided the debate records that the pinned dispatch
template, not the sweep, is the containment gate.
