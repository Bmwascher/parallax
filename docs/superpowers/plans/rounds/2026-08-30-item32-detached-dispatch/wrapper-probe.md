# Wrapper probe record

Task 1 step 0 creates this record with the `harness` line below, which is
host-independent and appears once, above both host sections. Task 8 adds
the two host sections (`## host: <windows-powershell-5.1 | powershell-7>`)
beneath it; no other task writes here.

harness: plugin_root_token=substituted client_version=2.1.251

Re-taken 2026-08-31, in this session, on Claude Code 2.1.251: invoking the
`codex:codex-cli-runtime` skill (base directory
`C:\Users\Brandon\.claude\plugins\cache\openai-codex\codex\1.0.6\skills\codex-cli-runtime`)
delivered its body with the literal `${CLAUDE_PLUGIN_ROOT}` (present on disk
at `SKILL.md:12`, `node "${CLAUDE_PLUGIN_ROOT}/scripts/codex-companion.mjs"`)
already resolved to the absolute path
`C:/Users/Brandon/.claude/plugins/cache/openai-codex/codex/1.0.6/scripts/codex-companion.mjs`.
The harness substitutes `${CLAUDE_PLUGIN_ROOT}` in plugin skill body text
before the model sees it. Matches the paragraph this task's spec cites as
measured 2026-08-31 on the same client version.
