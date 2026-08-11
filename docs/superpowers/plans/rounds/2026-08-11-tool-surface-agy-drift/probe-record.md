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

The premise "there is no free tool-list view" does not stand and must be
retracted when the item is closed.

**What this source is, stated exactly** (narrowed at round 2). It
ENUMERATES THE OBSERVED SURFACE. An earlier draft called it the source of
evidence a design needs to VERIFY A REMOVAL; finding 6 below shows it
cannot do that, so the earlier wording claimed the one thing this record
goes on to disprove.

### Finding 2. With the shipped isolation flags, 125 fewer of 128 tools
### are REPORTED.

Measured twice, identical both times. The wording was corrected at round
2: this record measured what the client REPORTS, and finding 6 is the
reason that is not interchangeable with what was removed.

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

The reviewer's shipped isolation flags reduce the reported surface far
more than any document in this repo claimed, because nothing in this repo
had ever measured them. That is a claim-width correction in the repo's
favour, and it is still a correction.

`experimentalFeature/list` corroborates the same flags from a second
angle: under arm A the list reports `plugins: enabled=True`; under arm B
`plugins` is absent from the enabled set. The two views agree.

### Finding 3. `node_repl` SURVIVES the isolation flags.

Three tools survive: `js`, `js_add_node_module_dir`, `js_reset`. The
first executes JavaScript. Item 7 inferred this from `mcp:` lines in a
transcript AFTER spending the review call. It is now observable BEFORE
dispatch, which is the difference between a post-mortem and a detection.

Corrected at round 2: an earlier draft called this "a control". It is not.
It is a DETECTION of something observed. Nothing here establishes that
every tool present would be observed.

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
needs a two-pass shape, the same one the 0.17.0 skills probe already uses:
first demonstrate the probe CAN see the thing, then run the dispatch
configuration. If pass one does not see it, the instrument is not known to
work, the measurement is UNMADE, and the correct outcome is BLOCKED —
never clean.

**Corrected at plan round 1, and the correction matters.** An earlier
draft of this section called that pair a POSITIVE CONTROL for removal. It
is not one, and the reviewer refuted it from this record's own finding 6.
Pass 1 calibrates the INSTRUMENT under baseline conditions. It says
nothing about the MCP subsystem's health under pass-2 conditions, and an
empty pass 2 stays observationally identical to the deliberate crash in
arm F. So:

- pass 1 is an INSTRUMENT CALIBRATION;
- an unexpected tool SURVIVING pass 2 is a real detection, because
  detecting something present never depends on telling removal from
  silence;
- a tool ABSENT from pass 2 is a MITIGATION, not proof of removal.

The pair must never be described as a positive removal control unless
some pass-2 survivor or MCP failure diagnostic is first measured.

### Enumeration gap, RECONFIRMED rather than found

The preflight enumeration sweeps `*AGENTS.md`, `.agents/*` and
`.kimi-code/*`. It does NOT sweep `<repo>/.codex/*`. This repo's `.codex`
directory exists and is EMPTY, so nothing is reachable through it today.
That makes it a gap in the enumeration, not a live exposure.

**Two corrections at plan round 1.**

It was not newly found. `skills/multi-model-verify/references/model-prompting-notes.md:288-291`
already records it, in those words: "'.codex/' stays unswept — unprobed;
probe before adding." This record reconfirms standing text.

And an earlier draft asserted that "codex loads project-local skills from
`<repo>/.codex` even when the project is untrusted". That is RETRACTED. It
came from the client's own description, not from a measurement, and this
record retains no `.codex` canary artifact comparable to its tool-surface
reproductions. The reachability stays UNPROBED, exactly as the standing
text says. Anything else would be this record doing the thing it exists to
prevent.

Note the neighbouring distinction, since the two are easy to merge: the
round-1 preflight probe reported `global_agents_md_path` as
`C:\Users\Brandon\.codex\AGENTS.md`. That is the codex HOME, which the
probe DOES see and record. The repo-local `.codex` is a different
directory and is not evidence about it.

---

## Item 11 — the agy lane's contracts

Item 11 enumerates five agy-side contracts and observes that drift
watching records only a version string. Each contract was checked live.

### The version in the item text is already stale

Item 11 quotes `"agy": "1.1.8"`. Live `agy --version` is **1.1.12** and
`tools/drift-snapshot.json` already carries 1.1.12. The version string
moved four releases and no DRIFT-SIDE contract check ran, which is the
item's own thesis demonstrated rather than argued.

The wording matters and was corrected at round 2: the operational checks
DID run, per dispatch, inside the Flash implementer. What never ran was
anything on the drift side, and `check-drift` does not even emit a note
when the agy version changes, which is why four releases passed unremarked.

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
`allowNonWorkspaceAccess` is set to **true**, and no CHECK in this repo
reads it.

**Corrected at plan round 1: it HAS been measured once, and this record
missed it.** An earlier draft said the repo has no measurement of what agy
does with this key. False.
`docs/superpowers/plans/2026-07-25-flash-implementer.md:590-603` records a
deliberate bounded probe during the 0.12.0 build: set the key to `false`,
run a print-mode write against a still-trusted directory, observe the
result. The write was soft-denied. The value was restored to `true` and
the finding recorded as "allowNonWorkspaceAccess=true required for
print-mode writes as of agy 1.1.7".

So `true` is not an unexamined default. It was a documented requirement of
the lane, measured once, ON AGY 1.1.7.

Claim width, restated, and narrowed again at round 2. This record
establishes: the key exists; its value is `true`; no check reads it; and
`false` broke the lane's intended writes on 1.1.7.

TWO things stay open on 1.1.12, and an earlier draft named only the
second, which quietly turned a version-bounded result into a present-tense
requirement:

1. Does `false` STILL soft-deny those writes? If it no longer does, `true`
   is no longer needed and the setting can go.
2. What does `true` permit OUTSIDE the workspace?

Item 11's security contract stays explicitly UNMEASURED rather than clean,
and the follow-up must test both.

### What actually watches agy today

**Corrected at plan round 1.** An earlier draft said "three of the five
declared contracts have no check anywhere". That is FALSE and the reviewer
refuted it with citations this record should have carried.

`agents/flash-implementer.md:45-59` runs a five-item preflight before
EVERY dispatch, and three of item 11's contracts are in it: `agy models`
must contain the model literal (item 1), `trustedWorkspaces` must contain
the workspace (item 2), and the settings file must carry NO file-writing
per-tool allow rule at all (item 3, which is item 11's fifth contract).
`agents/flash-implementer.md:100-105` forbids any approval-bypass flag,
and lines 81-92 block a missing transcript after the run.

So the KNOWN OPERATIONAL CHECKS are enforced, per dispatch and post run,
at the point of use.

**Not "the contracts ARE enforced", which round 2 caught as an
overcorrection.** Item 11's fifth contract is the absence of ANY
approval-bypass flag or persisted per-tool allow rule. The wrapper checks
one known rule CLASS, `write_file(` in any spelling
(`agents/flash-implementer.md:54-59`), and forbids bypass FLAGS within its
own lane (`:97-105`). That is not the same as establishing the absence of
any such mechanism, and this record's own settings finding below leaves
the broader security property UNMEASURED. Replacing an understatement with
an overstatement is not a correction.

The real gap is narrower and still real:

- `tools/check-drift.ps1:127-130` runs `agy.exe --version` and stores the
  string. That is the whole of the WEEKLY DRIFT WATCHER's agy coverage.
  None of the contracts above is watched there, and no note is emitted
  when the version itself changes.
- `commands/doctor.md:129-144` covers MODEL DECLARATION AND REACHABILITY:
  the binary exists, and `agy models` contains the declared literal, with
  its own note that the route language it offers is client-side
  requested/propagated only. Round 2 corrected an earlier draft that
  called this two mirrored item-11 contracts; it is not, and counting it
  that way inflates what exists today. It does not read the settings file
  at all.
- So a drift in any of these surfaces is discovered when a task is
  DISPATCHED and blocked, not before. That is safe but late: the failure
  lands mid-build, on a frozen plan, with the round's budget already
  committed.

The claim this record now makes: the known operational checks are enforced
at dispatch, the full security contract remains UNMEASURED, nothing is
covered by the drift watcher, and the doctor covers model declaration and
reachability only.

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
