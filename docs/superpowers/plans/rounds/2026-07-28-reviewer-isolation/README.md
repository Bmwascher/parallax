# Round artifacts — 0.17.0 reviewer isolation

- `sol-plan-r{1,2,3,4}-{brief,reply,header}` — the four-round cross-vendor
  plan debate that froze `docs/superpowers/plans/2026-07-28-reviewer-isolation.md`.
- `fable-review-e2e9242-5a0293d.md` — the required whole-branch review, raw
  reply, bound to the range in its filename.
- `skills-override-used.txt` — the 2313-byte `skills.config` override this
  debate itself dispatched with.

**Every file here is a RAW RECORD of what was said at the time, and two
claims inside them are now known to be wrong.** The artifacts are not
rewritten; the corrections live here.

**Superseded scope claim.** `sol-plan-r1-brief.md` says
`codex debug prompt-input` reveals the "whole instruction surface". It
does not. It renders the PROMPT. The reviewer's tool surface, meaning
configured MCP servers and the memories feature, is not in the prompt and
is not measured: observed 2026-07-28, an MCP tool ran inside a round that
passed every check the probe makes. The shipped wording is the
`client-probe-scope-limit` region in SKILL.md, and the gap is backlog
item 7.

**Note on `skills-override-used.txt`: it is a HISTORICAL RECORD, not the
format.** It uses DOUBLE-quoted TOML paths, which is what the debate ran
with before the format defect was found. The shipped generator
(`New-SkillDisableOverride` in `tools/codex-context-probe.ps1`) emits
SINGLE-quoted TOML literal strings instead, because Windows PowerShell 5.1
strips embedded double quotes when passing an argument to a native command,
after which codex rejects the value with `invalid type: string`. Copy the
format from the generator, never from this file.
