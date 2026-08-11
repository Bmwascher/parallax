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

> **SUPERSEDED IN PART at 0.24.0.** "Not in the prompt" is still true and
> is why a separate instrument was needed. "Is not measured" is no longer
> true: `tools/codex-tool-surface-probe.ps1` reads
> `mcpServerStatus/list` from `codex app-server --stdio`, free and local,
> and backlog item 7 is CLOSED. The 0.24.0 cycle found this file by its
> own sweep, as the seventh standing surface carrying the retracted
> premise. Its record is at
> `docs/superpowers/plans/rounds/2026-08-11-tool-surface-agy-drift/`.
>
> Note what did NOT change: a clean prompt probe is still not full
> reviewer isolation, and the new probe's ABSENCE direction is a
> mitigation rather than proof of removal.

**Note on `skills-override-used.txt`: it is a HISTORICAL RECORD, not the
format.** It uses DOUBLE-quoted TOML paths, which is what the debate ran
with before the format defect was found. The shipped generator
(`New-SkillDisableOverride` in `tools/codex-context-probe.ps1`) emits
SINGLE-quoted TOML literal strings instead, because Windows PowerShell 5.1
strips embedded double quotes when passing an argument to a native command,
after which codex rejects the value with `invalid type: string`. Copy the
format from the generator, never from this file.
