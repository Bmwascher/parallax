# Handoff — parallax field report from an 8-round mode-diff run

Written 2026-08-03 from a KitnEssentials session. **No parallax code was
changed.** This is a field report: I ran `parallax:multi-model-verify` mode
`diff` end to end on a real branch and hit six things worth the plugin's
attention — two of them outright defects in shipped surfaces.

Context for the run: KE branch `feat/character-panel-dedup`, range
`1b8af3c9..eeca9f0`, 14 commits, 9 files, +1163 / -266. Reviewer `gpt-5.6-sol`,
effort high, sandbox read-only, one session
(`019fc6ea-69c8-7ff1-ac25-0a1b97d73858`) resumed across all 8 rounds. Terminal
PASS, attested at
`.git/parallax/attestations/eeca9f0220eb56a4fec33db6127f97a5e23aed49.json`.

**Heads up on repo state:** `Documents/parallax` is on branch
`feat/home-skills-root-probe` at `6952556`, with an untracked
`docs/superpowers/plans/rounds/2026-08-03-home-skills-root/probe-record.md`.
That is somebody else's in-flight work. I did not touch it and this report does
not depend on it.

---

## 1. DEFECT — the documented `resume` command breaks on any brief containing `"`

**Severity: high. It fires on round 2 of every debate whose brief quotes
anything.**

`SKILL.md` mode-plan step 3 (and mode diff by reference) documents the resume
dispatch as:

```
codex exec ... --output-last-message <reply-file> resume <SESSION_ID> "<rebuttal-brief>" > <transcript-file> 2>&1
```

The brief goes in as a **positional string**. On Windows the npm wrapper
`~/AppData/Local/npm-global/codex.ps1` re-splits its arguments before handing
them to node, so every literal `"` inside the brief becomes an argument
boundary.

What it looks like:

```
node.exe : error: unexpected argument 'Gems off with the
Usage: codex exec resume [OPTIONS] [SESSION_ID] [PROMPT]
```

Exit 2. It reads exactly like a malformed command — wrong flag order, too many
positionals — so the first instinct is to rewrite the invocation. The
invocation was fine. My brief quoted an EllesmereUI setting as `"Show Gems"`.

**Round 1 is immune** because SKILL.md pipes it on stdin:
`Get-Content -Raw <brief-file> | codex exec ... -`. Only `resume` uses the
positional form.

### The fix, probed and confirmed 2026-08-03

`resume` accepts the stdin form. **Make both dispatches identical:**

```
Get-Content -Raw <brief-file> | codex exec ... resume <SESSION_ID> - > <transcript> 2>&1
```

Probe run this session against the live debate session, prompt deliberately
carrying two quoted phrases: **exit 0**, reply file written, header echoed the
resumed `session id: 019fc6ea-69c8-7ff1-ac25-0a1b97d73858`, quotes passed
through intact. Artifacts `scratchpad/reply-probe-stdin.md` and
`transcript-probe-stdin.txt`.

Memory `project_parallax_plugin.md` already recorded this syntax
(`... resume <SESSION_ID> -`); it just never made it into SKILL.md, which shows
the positional form in mode-plan step 3. So this is a doc-drift fix, not a
design change.

**Do NOT ship the sanitize workaround I used.** During the run I patched around
it with
`$brief = ($raw -replace "\`r\`n", "\`n") -replace '"', "'"`. It works, but it
silently alters the brief the reviewer reads — which is the wrong trade in a
tool whose whole value is that both sides argue over the same evidence. The
stdin form has no such cost.

Saved on the KE side as memory `feedback_codex_resume_quote_splitting.md`.

---

## 2. DEFECT — `new-review-mirror.ps1` fails on long mirror paths, and blames the wrong thing

**Severity: medium. Blocks the first mirror build; the message sends you
hunting in the wrong repo.**

Building the mirror inside the Claude session scratchpad — about 150 characters
deep before the repo contents start — produced:

```
BLOCKED: baseline path 'References/AugBuffTracker/AugBuffTracker v1.0.2_old/libs/CallbackHandler-1.0/CallbackHandler-1.0.lua' has no file behind it
```

That file **does** exist in the source repo. I checked with `Test-Path`. The
reference path adds ~110 more characters, so the copy crosses the Windows
260-character limit and never lands the file; the manifest builder at
`tools/new-review-mirror.ps1:433-435` then correctly reports a hole.

Rebuilding at `C:\Users\Brandon\AppData\Local\Temp\kerev3` worked first try.
That is the evidence for the cause; I did not prove the limit directly.

**The stop itself is right** — failing loudly beats reviewing an incomplete
copy, and I want to be clear that the guard did its job. What is wrong is the
attribution. The message names a repo-relative path, so the reader looks at the
repo.

### The decision: pre-flight the path budget, do not try to support long paths

Add a length check at the TOP of `new-review-mirror.ps1`, before any copying:
measure the longest repo-relative path, add the mirror root length, and refuse
with both numbers plus the limit if the total crosses 260.

```
BLOCKED: mirror path is 152 chars; the deepest repo path adds 118; 270 > 260.
Choose a shorter -MirrorPath (e.g. C:\Users\<you>\AppData\Local\Temp\kerev).
```

Why this and not the alternatives:

- **It names the actual cause and the actual fix.** The current message sends
  you into the repo to investigate a file that is fine. I lost time there.
- **It fails before the copy**, so you do not pay a full repo duplication to
  learn the path is too long.
- `\\?\` extended-length prefixes would *support* long paths, but that means
  every downstream consumer — git, codex, the probe — has to tolerate the
  prefixed form too. Much larger surface for a problem a short path solves for
  free.
- Distinguishing "missing in source" from "missing in mirror" in the manifest
  error is a good secondary hardening, but it is a better *message* for a
  failure the pre-flight should have prevented. Do it after, or not at all.

Plus one line in SKILL.md: build the mirror at a short path such as
`%TEMP%\kerev<n>`, never inside the session scratchpad.

---

## 3. GAP — no documented flow for refreshing the mirror when HEAD moves

Mode diff's normal shape is: review, session applies fixes, re-review. That
means **HEAD moves every round**, and the mirror built for round 1 is stale for
round 2.

Nothing in SKILL.md or `backup-lane.md` says so. The mirror is described as a
construction step, singular. I built seven mirrors by hand (`kerev3` through
`kerev9`), one per round, each a full re-copy plus a fresh probe.

Two things to consider:

- **The silent-failure mode is real.** Resume the session against a stale
  mirror and the reviewer confidently reviews code you already changed. Nothing
  in the current flow catches that — the route header verifies the reviewer, not
  the tree.
- A `-Refresh` switch that re-syncs an existing mirror and re-runs the probe
  would cut most of the cost. Or, at minimum, one line in SKILL.md: rebuild the
  mirror at the new head before every round that follows an applied fix, and
  state the head in the brief so a stale tree is at least visible to the
  reviewer.

I put the head SHA and the incremental range in every brief for exactly this
reason. That is a workaround, not a control.

---

## 4. GAP — applying a nit from the PASS round silently invalidates the attestation

The reviewer's round-7 PASS ended with one **non-blocking** cleanup it had
noticed. I applied it. That moved HEAD from `b3158c7` to `eeca9f0` — and the
PASS no longer covered the tree.

SKILL.md does say "only the post-re-review terminal PASS is attested", but it
frames that around a **FIX** verdict. The case that actually bit me is a PASS
that carries observations, which reads as terminal. Attesting `eeca9f0` with a
verdict issued on `b3158c7` would have been a false record, so I spent round 8
confirming a 1-insertion / 4-deletion delta.

Suggested line for SKILL.md's finish-line section:

> A PASS is terminal only for the exact head it was issued on. If you apply
> anything the reviewer raised — including observations it labelled
> non-blocking — the head moves and the verdict no longer covers it. Either
> leave them for a follow-up branch, or run one confirming round.

Cheap to state, and it removes a whole class of quietly-wrong attestations.

---

## 5. GAP — the round cap does not describe a fix-verify loop

`debate-protocol.md:53` sets the default cap at **4 exchanges**, framed as
"the signal to stop spending tokens on an argument evidence hasn't settled".

I ran **8**, and I want that on the record as an overrun of the documented
default. But the framing did not fit what happened. Nothing was ever contested:
every round the reviewer found a **new, real** defect, I verified it
independently, accepted it, and fixed it. Zero refutations, zero escalations,
zero repeat findings. Stopping at 4 would have shipped defects 5 and 6.

Those are two different regimes sharing one counter:

- **Contested**: the same point argued across rounds. A cap is exactly right —
  more rounds will not settle it, the user must.
- **Fix-verify**: each round finds something new and it is accepted. The cap
  is measuring the wrong thing; the real signal is a round that finds nothing
  new, which is the `loop-until-dry` shape.

Worth distinguishing in `debate-protocol.md`. Something like: the cap counts
rounds with **contested** points; rounds that end in accepted findings reset it,
and the debate ends when a round produces no new accepted finding. Otherwise
the honest operator either stops early or, like me, silently overruns.

---

## 6. GAP — no guidance for pre-existing defects found by a diff review

Rounds 4 through 7 all landed on defects that **predate the range**. Not spec
drift, not port drift — bugs in adjacent code the diff happened to walk past.
One of them I traced to a commit from a much earlier branch with `git log -S`.

Mode diff's brief tells both sides to judge "spec fidelity, port fidelity,
correctness, internal consistency". It says nothing about **scope**.

I invented a policy mid-debate and declared it to the reviewer in the round-6
brief: fix pre-existing defects that are the same class as what the branch is
already fixing and are live on the surface the smoke pass will exercise; record
anything else for a follow-up branch. The reviewer accepted it and, on the
next finding, explicitly said it "can be a separate follow-up commit, but I
would not certify the module before that follow-up lands" — which is a useful
formulation the skill could adopt.

The tension is real and worth resolving in the docs rather than per-debate:
surgical-changes discipline says leave it; certifying a module you know is
broken says fix it. Either answer is defensible. Having no answer means each
session improvises, and the attestation record then means slightly different
things run to run.

---

## What worked, unprompted

Recording these so the next change does not regress them.

- **Session resume held state across 8 rounds.** The reviewer referred back to
  its own earlier acceptances correctly in round 8 without re-reading them.
- **Route header verified every round**: `model: gpt-5.6-sol`,
  `provider: openai`, `sandbox: read-only`, `reasoning effort: high`, and the
  same `session id:` echoed back. Never drifted once.
- **Client-context probe clean on all seven mirrors**: `repo_scoped 0`,
  `plugin_cache_scoped 0`, `skills_after 0` (from 29 before). Only
  `~/.codex/AGENTS.md` survived, recorded not stopped, exactly as documented.
- **The override SHA was identical across all seven mirrors**
  (`180f09f5...`), so the generated override is deterministic. The
  read-bytes-and-hash verification before each dispatch is therefore cheap. It
  also means a changed hash would be a genuinely strong signal.
- **The attestation emitter worked first try** and refused nothing it should
  have accepted.
- **The reviewer never fabricated.** Every one of the six findings was real and
  survived my independent verification against the repo. Several cited exact
  line ranges in a third-party addon's source outside the repo, correctly. It
  also corrected one of my own claims in the final round — I had written that
  `Refresh()` always reaches `ApplySettings()`; it does not, there is an
  `Enabled` guard, and the behaviour is equivalent for a different reason than
  I gave.

---

## Build these two. Brandon's call, 2026-08-03.

**§1 — the codex resume split.** Decided and probed. Replace the positional
form in SKILL.md with the stdin form. Both dispatches then look the same, which
is also easier to read. Roughly a two-line doc change plus whatever dispatch
snippets the references carry.

**§2 — the mirror path pre-flight.** Decided above: a length check at the top
of `new-review-mirror.ps1` that refuses with both numbers, plus one line in
SKILL.md telling operators to use a short path. Do not pursue `\\?\`.

Both are small and both are in shipped surfaces that an operator hits on an
ordinary run. §1 will bite the very next debate that quotes anything.

### The other four — recorded, not scheduled

§3 (stale mirror when HEAD moves), §4 (applying a PASS-round nit invalidates
the attestation), §5 (the round cap does not describe a fix-verify loop), §6
(no scope guidance for pre-existing defects). All real, none blocking. §4 is
the cheapest of them if somebody wants a third: one paragraph in the finish-line
section.

Nothing here is urgent enough to interrupt the `feat/home-skills-root-probe`
work.
