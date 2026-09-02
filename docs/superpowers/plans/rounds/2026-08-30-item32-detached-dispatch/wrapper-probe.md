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

Method for both host sections below: a review mirror was built at
`%TEMP%\kerev-t8` via `tools/new-review-mirror.ps1` (source head
`ffc2f265`, `project_agents_md: false` after remediation, `skills_after:
0`), giving one override file (`sha256
84d16007...827579bb1`) reused for both hosts' encoding rounds. Boundary
and state measurements drive `tools/dispatch-detached.ps1` directly with
stub wrapper bodies (never the real client); the encoding measurement
launches the REAL `<!-- wrapper:codex-fresh -->` block from `SKILL.md`,
verbatim, against `gpt-5.6-sol` at the canonical effort, through the
tool, with `-WorkingDirectory` the mirror above. `kimi_reply` re-runs
Task 7's `test_kimi_wrapper_reply_bytes_match_the_payload_exactly` on
each host and reads its result; it does not touch a live Kimi client.

## host: windows-powershell-5.1
boundary: launch_return_seconds=0.405 alive_in_later_call=true exit_file_after_sleep=true
states: killed_tree=no-exit-file refused_receipt=no-receipt empty_reply=reply-empty
encoding: binder=accepted prompt_sha256_matches=true prompt_bytes_match=false
kimi_reply: bytes_match=true bom_present=false

## host: powershell-7
boundary: launch_return_seconds=0.432 alive_in_later_call=true exit_file_after_sleep=true
states: killed_tree=no-exit-file refused_receipt=no-receipt empty_reply=reply-empty
encoding: binder=accepted prompt_sha256_matches=true prompt_bytes_match=false
kimi_reply: bytes_match=true bom_present=false

**`prompt_bytes_match` measures false on BOTH hosts, and this is a real
result, not a fixture defect.** The brief fixture
(`task8-brief.md`, 89 bytes, no BOM, one em dash, one non-Latin
character, already in canonical form: no CR, no leading/trailing
whitespace) was dispatched through the real `codex-fresh` wrapper on
each host. On both, `read-codex-round-evidence.ps1 -Fresh` returned
`clean` (`prompt_sha256_matches=true`: the CANONICAL hash matches, per
that script's own declared canonicalization - CRLF folded to LF, ends
trimmed). Independently re-parsing each round's own rollout JSONL and
reading the matched user record's `input_text` byte-for-byte found 91
bytes ending `...ment.\r\n` against the fixture's 89 - a trailing CRLF
neither host's fixture carried.

Isolated to its cause before concluding anything about codex: piping a
same-process string through `|` to a native command's stdin - the exact
shape `$brief | codex exec ... -` uses - appends one CRLF terminator
line-object semantics dictate. Reproduced with NO codex or network
involved: `$brief | <stub .ps1 that captures raw stdin bytes>` on
Windows PowerShell 5.1 returned the fixture's 89 bytes plus a trailing
`\r\n`, byte for byte matching what both real rounds' rollouts recorded.
Independently re-confirmed the same shape and reason: an 85-byte brief
piped to a native child that reads raw stdin arrives as 87 bytes with
`0D 0A` appended, identical on both hosts, and the embedded em dash
survives intact - a trailing newline appended by PowerShell's own
pipe-to-native serialization, not mangling and not host-specific.

**THE BRIEF IS NOT BYTE-IDENTICAL END TO END, AND IT DOES NOT NEED TO
BE.** The load-bearing property is `prompt_sha256_matches`, not
`prompt_bytes_match`: `read-codex-round-evidence.ps1` canonicalizes
(CRLF folded to LF, ends trimmed) BEFORE hashing, precisely so a
transport-added trailing newline cannot fail a round, and
`prompt_sha256_matches=true` on both hosts is that mechanism working as
designed - it is what keeps every prior round in this project's whole
debate history binding CLEAN despite this same pipe behaviour.
`prompt_bytes_match=false` is the literal, first-time measurement of a
stricter property nothing before this task checked: it is pinned here
as MEASURED, not hoped for, and a future change that made the raw bytes
match end to end would turn this pin red ON PURPOSE - that is the whole
point of pinning a measured value instead of an assumed one. This
task's own Step 5 instruction governs the outcome: "if any value comes
out the other way, WRITE IT AS MEASURED and stop." Step 6's oracle
below asserts these values exactly as measured, including
`prompt_bytes_match=false`; it does not delete or redefine the field,
because doing so would hide the one measurement this record exists to
carry.
