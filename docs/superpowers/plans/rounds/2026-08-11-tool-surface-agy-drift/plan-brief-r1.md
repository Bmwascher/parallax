<role>Adversarial reviewer, equal weight, in a two-model debate. You are not
a rubber stamp and not a critic-for-hire: refute what is wrong, confirm what
stands.</role>

<task>Refute or confirm each numbered claim below about the 0.24.0
implementation plan for the `parallax` repo (a Claude Code plugin providing
cross-model verification plus its eval harness, at
C:\Users\Brandon\Documents\parallax, branch `0.24.0-tool-surface-agy-drift`,
HEAD ef428c3). The plan closes two open backlog items. Then answer the four
DESIGN QUESTIONS at the end.</task>

<rules>
Cite `path:line` from files you actually read for every claim you make or
contest; uncited claims will be struck rather than argued with. Do not
manufacture objections: if a claim stands, say PASS and move on. End every
numbered claim with PASS, FIX (with the specific fix) or ESCALATE. Then
answer each design question with a recommendation and the reason.

Three invariants govern this repo and are not under debate:
- a claim may never be wider than its evidence;
- an unmade, failed, or unreadable measurement is never a clean one;
- a test is not evidence until it has been watched to FAIL for the reason
  it claims.
A FIX is new code and gets no discount from any of them.
</rules>

<claims>

**Background.** The two backlog items are written up at
`docs/superpowers/plans/2026-07-27-0150-backlog.md` - item 7 at line 482,
item 11 at line 779. Both state a problem and explicitly leave the fix
shape undecided. The draft plan under review is
`docs/superpowers/plans/2026-08-11-tool-surface-agy-drift.md`. Every number
below was measured locally on 2026-08-11 and is written up at
`docs/superpowers/plans/rounds/2026-08-11-tool-surface-agy-drift/probe-record.md`.
Read all four.

---

**CLAIM 1 - item 7's central premise is false, and the surface it says does
not exist is free, local and reproducible.**

Item 7 states at backlog line 505-511: "`codex debug prompt-input` renders
prompt text and calls no model, which is what makes it free. It does not
render the tool list ... `codex debug` has only `models`, `app-server` and
`prompt-input`, so there is no free tool-list view to measure against."

The first two sentences are correct. The third is not. `codex app-server
--stdio` speaks JSON-RPC; after `initialize` with
`capabilities.experimentalApi = true`, the method `mcpServerStatus/list`
returns every resolved MCP server and, per server, the complete map of tool
names to JSON schemas. `experimentalFeature/list` returns every feature
flag with its resolved enablement. Neither starts a turn, so neither spends
model tokens.

Measured, twice, identical both times:

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

Two consequences the plan asserts:

(a) The shipped review flags remove 125 of 128 tools, which no document in
this repo had ever measured, and
(b) `node_repl` - whose `js` tool executes JavaScript - SURVIVES them. Item
7 inferred (b) from `mcp:` lines in a transcript AFTER the review call was
spent; it is now measurable BEFORE dispatch.

PASS or FIX: is the claim as stated wider than the measurement behind it?

---

**CLAIM 2 - `-c mcp_servers={}`, named as a candidate lever in item 7, is
inert, and item 7's warning about it was right.**

Item 7 at backlog line 512-518 says `-c mcp_servers={}` "parses" and warns
against shipping it "on the strength of parsing alone".

Measured: `codex app-server --stdio --disable plugins --disable apps -c
mcp_servers={}` parses, exits 0, and reports the SAME one server and SAME
three tools as arm B. It changes nothing.

Two levers DO work: `--disable memories` flips `memories` to
`enabled=False` in `experimentalFeature/list`, and `-c
mcp_servers.node_repl.enabled=false` takes the surviving server to zero
tools.

---

**CLAIM 3 - and this is the claim the whole design rests on - a REMOVED
server and a CRASHED server are indistinguishable in that record, so a
"zero tools" assertion is not a control.**

Two arms were compared field by field with the tool schemas stripped:

- E: `-c mcp_servers.node_repl.enabled=false` (deliberate removal)
- F: `-c mcp_servers.node_repl.command="cmd-that-does-not-exist"`
  (deliberate launch failure)

Both produce `serverInfo: null`, zero tools, and `authStatus:
"unsupported"`. No field separates them.

A check of the form "assert the tool count is zero" therefore reads a
CRASHED server as a CLEAN removal. Under this repo's second invariant that
is not a control; it is the same defect class item 7 exists to prevent,
rebuilt somewhere new.

A candidate objection is that zero tools is merely an early sample of a
server still connecting. Fifteen timed samples against a HEALTHY
`node_repl` at 0.4-second intervals reported three tools with `serverInfo`
populated at EVERY sample, earliest t+0.41s, latest t+6.02s. No transient
zero window was observed.

The plan states the width of that last measurement explicitly: one run, one
machine, one sampling rate, nothing sampled earlier than 0.41s. Enough to
say the ambiguity is not explained by a race. NOT enough to say a race
cannot exist. Is that width statement correct, or still too wide?

---

**CLAIM 4 - the fix shape that follows: a two-pass probe with a POSITIVE
CONTROL, and an allowlist comparison rather than a zero-count assertion.**

Plan Task 1. New script `tools/codex-tool-surface-probe.ps1`, deliberately
NOT an arm of `tools/codex-context-probe.ps1` (different transport, a
JSON-RPC session versus one rendered document; that file is already 1083
lines and its header at lines 1-23 declares the tool surface out of scope).

- Pass 1, BASELINE, no isolation flags. The instrument must be shown to
  work: at least one server with non-null `serverInfo` and at least one
  named tool. If pass 1 sees nothing, the probe is not known to be able to
  see anything, the measurement is UNMADE, and the verdict is BLOCKED. A
  clean pass 2 alone is never reported.
- Pass 2, DISPATCH, with the exact flags the review dispatch uses. The
  surviving tools are ENUMERATED, not counted, and compared against a
  declared allowlist. Any tool outside it blocks.

The reasoning for the allowlist direction: blocking on an UNEXPECTED tool
does not require distinguishing removal from silence, so claim 3's
ambiguity does not weaken it. The reverse direction - asserting a tool WAS
removed - does, and that is design question 1.

This mirrors the two-pass shape `tools/codex-context-probe.ps1` already
uses for skills (`Invoke-PromptInput` at line 708, pass 1 at line 776).

---

**CLAIM 5 - item 11's own version string moved four releases with no
contract check in between, which demonstrates the item rather than arguing
it.**

Item 11 at backlog line 782-785 quotes `"agy": "1.1.8"` from
`tools/drift-snapshot.json`. Live `agy --version` today is **1.1.12**, and
the snapshot already carries 1.1.12. `tools/check-drift.ps1:127-130` runs
`agy.exe --version` and stores the string; that is the entire agy check.
`commands/doctor.md:129-141` checks the binary exists and that `agy models`
contains the model literal.

So of the five contracts item 11 enumerates at backlog lines 787-800, three
have no check anywhere, and the fourth is checked only in the doctor, which
a dispatch does not run.

Measured today, each contract's state:

| contract | state |
|---|---|
| model literal `gemini-3.6-flash-medium` in `agy models` | present (11 models resolve) |
| `settings.json` exists, carries `trustedWorkspaces` | present, repo path listed |
| `brain/<id>/.system_generated/logs/transcript_full.jsonl` | present in all 33 conversation dirs |
| absence of approval-bypass / persisted allow rule | NOT clean, see claim 7 |

---

**CLAIM 6 - the plan NARROWS item 11's transcript-path contract, on
purpose, and says so.**

Item 11 lists the transcript path as a drift contract. A transcript only
exists AFTER a run, so a pre-dispatch drift check cannot assert it. Plan
Task 5 therefore asserts only that the brain ROOT exists, and leaves the
transcript path enforced where it already is - inside the Flash
implementer's own evidence step (`agents/flash-implementer.md:88-92`), where
a missing transcript is already blocked.

The plan states this narrowing rather than letting a weaker check inherit
the item's wording. Is naming it enough, or does the narrowing leave a real
gap that needs its own follow-up?

---

**CLAIM 7 - `settings.json` has exactly two keys and one of them is a
relaxation nothing in this repo reads.**

```json
{
  "allowNonWorkspaceAccess": true,
  "trustedWorkspaces": ["C:\\Users\\Brandon\\Documents\\parallax"]
}
```

Item 11's fifth declared dependency (backlog line 799-800) is "the absence
of any approval-bypass flag or persisted per-tool allow rule". A setting
permitting access OUTSIDE the workspace is at minimum adjacent to that
dependency, it is ON, and no check in the plugin looks at it.

The plan is deliberately narrow here. It claims only that the key exists,
that its value is `true`, and that nothing reads it. It does NOT claim what
agy does with it, whether the plugin set it, or whether it changes what the
Flash implementer can reach. Plan Task 5 records the value in the drift
snapshot so a CHANGE is visible; Plan Task 8 opens a backlog item for the
measurement.

Is that the right width, or is recording-without-measuring itself the
false-clean this repo forbids?

---

**CLAIM 8 - the plan declines to give agy a version FLOOR, and gives a
reason.**

Item 11 offers a floor as candidate 1, by analogy with the Fable panel
lane's Claude Code 2.1.216 floor. The plan declines. The only agy version
anything in this repo has been measured on is 1.1.12, which is simply the
version installed today. A floor asserted at whatever happens to be
installed has no measurement under it: it would not encode "below this the
lane is broken", only "this is what we happened to see".

Is declining correct, or does a floor at the measured version carry real
protection the contract checks do not?

---

**CLAIM 9 - two things this cycle found and deliberately does NOT act on.**

Plan Task 8.

(a) `allowNonWorkspaceAccess` - claim 7 above.

(b) The preflight enumeration sweeps `*AGENTS.md`, `.agents/*` and
`.kimi-code/*` but NOT `<repo>/.codex/*`, and codex loads project-local
skills from `<repo>/.codex` even when the project is untrusted. This
repo's `.codex` directory exists and is EMPTY, so nothing is reachable
through it today. The plan calls that a gap in the enumeration, not a live
exposure, and opens an item.

Is "gap, not exposure" the right characterisation, given that the probe run
for THIS round reported `global_agents_md_path` as
`C:\Users\Brandon\.codex\AGENTS.md` - the codex HOME, which the probe does
see - while the REPO-local `.codex` is a different directory the
enumeration does not sweep?

---

**CLAIM 10 - three pieces of standing text become false when this ships,
and the plan retires all three.**

Plan Task 3.

- `tools/codex-context-probe.ps1:1-23` tells the reader the script "does
  not read the reviewer's tool surface at all - see backlog item 7".
- `skills/multi-model-verify/SKILL.md`, contract region
  `client-probe-scope-limit`, says "`codex debug` offers no tool-list view
  to measure instead" and "Backlog item 7 holds the tool half".
- Item 7 itself.

The SKILL.md sentence is narrowly TRUE of `codex debug` and misleading
about codex as a whole, which is exactly how claim 1's premise survived
several cycles. Editing that region also means re-pinning it in
`evals/multi-model-verify/` per the contract-coverage rule.

Does the plan miss any other standing text that this change falsifies?

</claims>

<design-questions>

**DQ1 - the survivor control.** Under the plan's preferred shape, the
review dispatch gains `-c mcp_servers.node_repl.enabled=false` and pass 2
shows `node_repl` gone. Claim 3 says that is equally consistent with a
launch failure. Is there a sound SURVIVOR CONTROL - some server, feature
flag, or other signal that must REMAIN visible in pass 2 - which would
separate "the environment is healthy and the flag worked" from "the MCP
subsystem died"? Or is the honest answer that this direction is a
MITIGATION rather than a control, and must be labelled that way in the
contract text? Note that `experimentalFeature/list` answering correctly
proves the app-server is alive but says nothing about the MCP subsystem.

**DQ2 - shape A or shape B for `node_repl`.**
Shape A: add `-c mcp_servers.node_repl.enabled=false` to the dispatch;
the allowlist is then EMPTY and any tool blocks.
Shape B: leave the dispatch alone and declare `js`,
`js_add_node_module_dir`, `js_reset` accepted residuals with a rationale.
Session position is A, because B requires asserting that a code-execution
tool in a read-only reviewer is acceptable, and this repo has no
measurement of what `node_repl` can reach. What breaks A?

**DQ3 - the agy version floor.** See claim 8.

**DQ4 - `allowNonWorkspaceAccess: true`.** Watch it and open an item
(session position), or treat it as a defect this cycle fixes? The plugin
has no measurement of what it permits.

</design-questions>

<debate-meters>
Declared BEFORE round 1, per the protocol:
- ROUND CAP: 4 consecutive CONTESTED exchanges. Termination requires an
  adjudicated DRY round.
- TOTAL FIX-VERIFY BUDGET: 6 units, one unit = one dispatched exchange.
  Exhaustion PAUSES for user authorization; it does not silently continue.
These are two separate meters.
</debate-meters>
