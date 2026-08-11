# Third-party notices

The three Python tools in this directory are vendored from
[Shubhamsaboo/awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps)
(`agent_skills/evals/tools/`, fetched 2026-07-12), licensed under the
**Apache License 2.0**:
<https://github.com/Shubhamsaboo/awesome-llm-apps/blob/main/LICENSE>

- `skill_lint.py` — provenance header + BODY TOKEN BUDGET ENFORCEMENT
  (0.23.0, 2026-08-11): adds `BODY_TOKEN_CEILING`, makes a body over the
  ceiling an ERROR where upstream only ever warned, and rebases both
  numbers from a measured body. Re-diffed against live upstream the same
  day: upstream's newest commit for this path is
  `ca8e5b3c56e51e336449a99d79b42b45ea690b86` (2026-07-09), and apart from
  the header and this delta the file is byte-identical to it. The earlier
  "unmodified except the provenance header" line here was left standing
  when that delta landed and was false from then until this correction.
- `skill_scanner.py` — unmodified except the provenance header.
- `run_trigger_evals.py` — provenance header + explicit `utf-8` encoding on
  both `open()` calls (Windows defaults to cp1252) + `SKILLS_ROOT` pointed
  at this repo's `skills/` directory (upstream keeps skills at the tree
  root).

## A frozen copy outside this directory

`evals/multi-model-verify/fixtures/skill_lint_pre_change.py` is ALSO
Apache-2.0 code from the same upstream. It is `skill_lint.py` frozen
exactly as it stood at commit `dd0db13`, immediately before the budget
delta above, and it exists so the fail-first proof for that delta can
EXECUTE the pre-change implementation instead of describing it. Changes
from upstream: the provenance header this repo substituted at import, plus
a banner marking it uneditable. It must never be updated.

What is hash-pinned, exactly: the COPIED TEXT BELOW THE BANNER, by
`evals/multi-model-verify/test_skill_lint_budget.py`. The banner itself is
prose and is EXCLUDED from the hash, so banner edits do not break any
pin. An earlier draft of this paragraph said "its content is hash-pinned",
which claimed the whole file and was wider than the test.

It is named here because the paragraph above scopes this notice to "the
three Python tools in this directory", which would otherwise leave a
fourth Apache-2.0 file uncovered.

The rest of this repository is under its own license (see the repo root);
these files remain under Apache-2.0. Changes are stated per file above, per
Apache-2.0 section 4(b).
