# Round artifacts — 0.17.0 reviewer isolation

- `sol-plan-r{1,2,3,4}-{brief,reply,header}` — the four-round cross-vendor
  plan debate that froze `docs/superpowers/plans/2026-07-28-reviewer-isolation.md`.
- `fable-review-e2e9242-5a0293d.md` — the required whole-branch review, raw
  reply, bound to the range in its filename.
- `skills-override-used.txt` — the 2313-byte `skills.config` override this
  debate itself dispatched with.

**Note on `skills-override-used.txt`: it is a HISTORICAL RECORD, not the
format.** It uses DOUBLE-quoted TOML paths, which is what the debate ran
with before the format defect was found. The shipped generator
(`New-SkillDisableOverride` in `tools/codex-context-probe.ps1`) emits
SINGLE-quoted TOML literal strings instead, because Windows PowerShell 5.1
strips embedded double quotes when passing an argument to a native command,
after which codex rejects the value with `invalid type: string`. Copy the
format from the generator, never from this file.
