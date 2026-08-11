# Probe record — backlog items 7 and 11, measured 2026-08-11

Everything below is a LOCAL measurement. No turn was started against any
model, so no reviewer quota was spent. Every arm is reproducible from the
scripts named at the end.

This record exists because both items say "shape of a fix, not decided"
and both forbid a design argued from parsing alone. A plan debate opened
without these numbers would have been wider than its evidence.

---

## Item 7 — the reviewer's TOOL surface

### Finding 1. The surface item 7 says does not exist, DOES exist.

Item 7 states: "`codex debug` has only `models`, `app-server` and
`prompt-input`, so there is no free tool-list view to measure against."

That is true of `codex debug`. It is NOT true of `codex app-server`.
Speaking JSON-RPC over `codex app-server --stdio`, after `initialize`,
the method `mcpServerStatus/list` returns every resolved MCP server, and
for each server the complete map of tool names to their JSON schemas. A
sibling method `experimentalFeature/list` returns every feature flag with
its resolved enablement.

Neither starts a turn. Both are reads.

The premise "a design that verifies a tool removal needs a new source of
evidence" therefore stands, and this IS that source. The premise "there
is no free tool-list view" does not stand and must be retracted when the
item is closed.

### Finding 2. The shipped isolation flags remove 125 of 128 tools.

Measured twice, identical both times.

```
ARM A: (no flags)
MCP SERVERS: 2
  - codex_apps: 125 tool(s)
  - node_repl: 3 tool(s)
TOTAL TOOLS: 128

ARM B: --disable plugins --disable apps
MCP SERVERS: 1
  - node_repl: 3 tool(s)
      js
      js_add_node_module_dir
      js_reset
TOTAL TOOLS: 3
```

The reviewer's shipped isolation flags are far more effective than any
document in this repo claimed, because nothing in this repo had ever
measured them. That is a claim-width correction in the repo's favour, and
it is still a correction.

`experimentalFeature/list` corroborates the same flags from a second
angle: under arm A the list reports `plugins: enabled=True`; under arm B
`plugins` is absent from the enabled set. The two views agree.

### Finding 3. `node_repl` SURVIVES the isolation flags.

Three tools survive: `js`, `js_add_node_module_dir`, `js_reset`. The
first executes JavaScript. Item 7 inferred this from `mcp:` lines in a
transcript AFTER spending the review call. It is now measurable BEFORE
dispatch, which is the difference between a post-mortem and a control.

### Finding 4. `-c mcp_servers={}` is a NO-OP.

Item 7 named this as a candidate lever and warned it was unverified.
The warning was right and the lever is worse than unverified: it is
inert. `codex app-server --stdio --disable plugins --disable apps -c
mcp_servers={}` parses, exits 0, and reports the SAME 1 server and SAME 3
tools as arm B. It changes nothing.

This is the exact false-clean the 0.17.0 probe exists to forbid: a flag
that looks like a control, is accepted by the parser, and does nothing.
It must never ship as a control.

### Finding 5. Two levers DO work.

- `--disable memories` flips `memories` to `enabled=False` in
  `experimentalFeature/list`.
- `-c mcp_servers.node_repl.enabled=false` takes the surviving server to
  0 tools.

### Finding 6 (decisive for the design). "Removed" and "crashed" are
### INDISTINGUISHABLE in this record.

Two arms were compared field by field with the tool schemas stripped:

- E: `-c mcp_servers.node_repl.enabled=false` (deliberate removal)
- F: `-c mcp_servers.node_repl.command="cmd-that-does-not-exist"`
  (deliberate launch failure)

Both produce a record with `serverInfo: null`, zero tools, and
`authStatus: "unsupported"`. There is no field that separates them.

Therefore a check of the form "assert the tool count is zero" reads a
CRASHED server as a CLEAN removal. Under this repo's standing invariant
— an unmade, failed or unreadable measurement is never a clean one —
that check is not a control. It is the defect class item 7 was opened to
prevent, rebuilt in a new place.

### Finding 7. The ambiguity is representational, not a startup race.

A candidate objection is that zero tools is merely an early sample of a
server still connecting. Probe 5 sampled a HEALTHY `node_repl` fifteen
times at 0.4-second intervals and it reported 3 tools with `serverInfo`
populated at every sample, the earliest at t+0.41s, the latest at
t+6.02s. No transient zero window was observed.

Claim width: that is ONE run, on ONE machine, at ONE sampling rate, with
no sample earlier than 0.41s. It is enough to say the ambiguity in
finding 6 is not explained by a race. It is NOT enough to say a race
cannot exist, and no design should rest on it.

### What findings 6 and 7 together imply for the fix

A one-pass "the tool is absent" assertion cannot be sound. The measurement
needs a POSITIVE CONTROL, the same two-pass shape the 0.17.0 skills probe
already uses: first demonstrate the probe CAN see the thing, then
demonstrate the flag removes it. If pass one does not see it, the
instrument is not known to work, the measurement is UNMADE, and the
correct outcome is BLOCKED — never clean.

### Unrecorded gap found alongside

The preflight enumeration sweeps `*AGENTS.md`, `.agents/*` and
`.kimi-code/*`. It does NOT sweep `<repo>/.codex/*`, and codex loads
project-local skills from `<repo>/.codex` even when the project is
untrusted. This repo's `.codex` directory exists and is EMPTY, so nothing
is reachable through it today. That makes it a gap in the enumeration,
not a live exposure.

---

## Item 11 — the agy lane's contracts

Item 11 enumerates five agy-side contracts and observes that drift
watching records only a version string. Each contract was checked live.

### The version in the item text is already stale

Item 11 quotes `"agy": "1.1.8"`. Live `agy --version` is **1.1.12** and
`tools/drift-snapshot.json` already carries 1.1.12. The version string
moved four releases and no contract check ran, which is the item's own
thesis demonstrated rather than argued.

### Contract-by-contract, measured

| contract | state today |
|---|---|
| model literal `gemini-3.6-flash-medium` in `agy models` | **present** |
| `settings.json` exists and carries `trustedWorkspaces` | **present**, the repo path is listed |
| transcript at `brain/<id>/.system_generated/logs/transcript_full.jsonl` | **present in all 33** conversation directories |
| absence of approval-bypass / persisted allow rule | **NOT clean, see below** |

`agy models` currently resolves 11 models. The lane's literal is one of
them.

### The settings file has exactly two keys, and one of them is a relaxation

```json
{
  "allowNonWorkspaceAccess": true,
  "trustedWorkspaces": ["C:\\Users\\Brandon\\Documents\\parallax"]
}
```

`trustedWorkspaces` is the key the lane depends on and it is correct.
`allowNonWorkspaceAccess` is set to **true**, and nothing in this repo
reads it. The lane's fifth declared dependency is "the absence of any
approval-bypass flag or persisted per-tool allow rule". A setting that
permits access OUTSIDE the workspace is at minimum adjacent to that
dependency, it is currently ON, and no check in the plugin has ever
looked at it.

Claim width: this record establishes that the key exists, that its value
is `true`, and that nothing checks it. It does NOT establish what agy
does with it, whether the plugin set it, or whether it changes what the
Flash implementer can reach. Those are open questions for the debate, not
findings.

### What actually watches agy today

`tools/check-drift.ps1:127-130` runs `agy.exe --version` and stores the
string. That is the whole of it. `commands/doctor.md:129-141` checks the
binary exists and that `agy models` contains the literal. Neither reads
the settings file, the transcript path, or `allowNonWorkspaceAccess`.

So three of the five declared contracts have no check anywhere, and the
fourth is checked only in the doctor, which a dispatch does not run.

---

## Reproduction

Scripts, all local and token-free:

- `probe3.py <cwd> [-- extra codex args]` — arm summary: servers, tool
  names, feature enablement.
- `probe4.py <label> <extra codex args>` — full server record minus tool
  schemas, which is what showed findings 4 and 6.
- `probe5.py` — fifteen timed samples against a healthy server, which is
  finding 7.

They live in the session scratchpad and are deliberately NOT committed:
they are throwaway instruments, and the repo's rule is that only
hand-normalized fixtures are committed. If the debate settles on a
shipped probe, that probe is new code and gets no discount from these.
