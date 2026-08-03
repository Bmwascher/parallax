# Debate brief, round 1: a contract change forced by a live measurement

You are the cross-vendor reviewer in a two-advisor debate. We are equal weight.
Refute me where you can. Ground every claim in a file and line you actually
read in this repo; say plainly when you are reasoning from the text rather than
from evidence.

Repo: `C:\Users\Brandon\Documents\parallax`, a Claude Code plugin providing
cross-model verification. It is NOT a WoW addon; ignore any addon conventions.

## What happened

The plugin has a BACKUP reviewer lane: Kimi K3 driven through the `kimi-code`
CLI. That client discovers "skills" (directories holding a `SKILL.md` whose text
is injected into the model's context) from FOUR roots. Three are controllable.
The fourth, `~/.agents/skills/`, lives in the user's own home, is not relocated
by `KIMI_CODE_HOME`, and nothing the lane runs removes it. It holds 27 real
skill directories on this machine.

Until today the lane's contract called that root "unprobed territory". An
earlier probe was CONFOUNDED: canaries were planted at the two PROJECT roots
only, and the reviewer agent DENIES the `Skill` tool, so "no skills available"
could not be told apart from "root not read".

Yesterday's frozen plan
(`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md`, revision 6, which
you helped freeze over four rounds) built a probe that breaks the confound. Task
4 ran it live today. **The full record, which you should read first, is
`docs/superpowers/plans/rounds/2026-08-03-home-skills-root/probe-record.md`.**

## The measurement, stated at its true reach

Five cells, everything constant except two variables, plus a resumed
calibration. All eight client calls returned `status: clean` from the lane's own
round validator, brief hash matched, route verified client-side.

- **Cell D** (probe agent that ALLOWS `Skill`; `--skills-dir` OMITTED; canary
  planted in `~/.agents/skills/`): the wire carries a `tool.call` named `Skill`
  with `args.skill = parallax-home-root-canary`, a matching `tool.result`, and a
  `context.append_message` whose `origin.kind` is `skill_activation` and whose
  `skillPath` is `~/.agents/skills/parallax-home-root-canary/SKILL.md`, carrying
  the canary body and its per-run nonce. **The root reaches the model.**
- **Cell C** (identical, except `--skills-dir <debate-home>/skills` PASSED, and
  the builder creates that directory EMPTY): `{"isError":true,"output":"Skill
  \"<id>\" not found in the current skill listing."}`. This equals the
  calibrated not-found oracle from cell E2 EXACTLY, under the frozen comparison
  (complete `event.result` payload, ordinal, after one substitution of the
  requested identifier). So C looked and found nothing; it is not a tool failure
  wearing a negative's clothes.
- **Cell E** (canary in `<debate-home>/skills`, `--skills-dir` OMITTED): loaded.
  So the debate-home root is discovered WITHOUT the flag.
- **Cells A and B** (the REAL reviewer agent, which denies `Skill`; canary
  present in B, absent in A): neither fires on either primary readout.
- `systemPromptChars` is constant at 462 for the reviewer agent and 1195 for the
  probe agent, across five separate throwaway homes and every canary condition.
  Skills are NOT merged into the system prompt on this client. Delivery is
  invocation-time.

## What I claim, and where I think I am weakest

**Claim 1.** `~/.agents/skills/` is REACHABLE by the kimi-code client. Not
unprobed. Measured.

**Claim 2.** `--skills-dir` REPLACES discovery rather than adding to it, and so
it suppresses all four roots. Cells C and D differ only in that flag.

**Claim 3, and this is where I want you hardest.** The flag is a control only
CONDITIONALLY. `--skills-dir <debate-home>/skills` suppresses the home root only
because that directory is EMPTY. Cell E proves the same directory loads a skill
when it has one. The builder (`tools/new-kimi-lane-home.ps1`) creates it empty
and writes `extra_skill_dirs` empty, but **I can find no per-round check that it
is STILL empty at dispatch.** If that is right, calling the flag a control
without also checking emptiness states a guarantee wider than its evidence,
which is the exact fault this repo's rules forbid. Check me: is there such a
check anywhere in `tools/read-kimi-round-evidence.ps1` or the per-round evidence
rules in `references/backup-lane.md`?

**Claim 4.** The lane as it SHIPS has no hole today, and two independent things
hold it: `Skill` is on the reviewer agent's `disallowedTools` deny list
(`skills/multi-model-verify/references/kimi-reviewer-agent.md`), and the flag
points discovery at an empty directory. Cells A and B are the evidence.

## Question 1: what replaces the now-false text?

Two places assert something measurement has just contradicted.

`skills/multi-model-verify/SKILL.md:69-73` currently says the 2026-07-31 probe
found runs with and without the flag "indistinguishable", and that "that flag
suppresses nothing observable". `references/backup-lane.md:345-354` says
"`--skills-dir` is a MITIGATION whose effect is UNMEASURABLE in this
configuration, not a control", and "Keep passing `--skills-dir` ... but claim
nothing for it."

Both statements were TRUE of the configuration they were measured in, where
`Skill` was denied so nothing could be invoked either way. Both are FALSE as
general claims about the flag.

What exactly should each say now? I want wording, not direction. Note the
constraint that files under `references/` are checked for the ABSENCE of
backslashes, and that text inside `contract:start`/`contract:end` markers must
sit WHOLE inside a single test pin, with `DECLARED_REGIONS` in
`evals/multi-model-verify/test_contract_coverage.py` edited when a region is
added or removed.

## Question 2: what replaces the disposition for the root itself?

`references/backup-lane.md:340-344` currently instructs: "Enumerate that root
before round 1 and record what it holds; a non-empty one is unprobed territory,
recorded as such rather than assumed absorbed by the tool allowlist."

It is no longer unprobed. Should the enumeration survive at all, and what should
the recorded disposition say? Argue the case for KEEPING the enumeration as well
as the case for dropping it; I lean toward keeping it and changing only what it
means, but I have not tested that view against you.

## Question 3: a defect in the frozen plan's own gate, and how far it spreads

Three branches of Task 4's gate turn on "a matching `tool.result` carrying the
nonce". **No `tool.result` ever carries a skill body on this client, in any
cell, including both positive controls.** `Skill`'s result is a fixed
confirmation string; the body arrives as the separate `skill_activation`
message. Read literally, every positive branch fails its own clause and the run
is VOID; read against the clause's purpose, the run is decisive. Both readings
end at the same instruction, so the record states the verdict.

**Do not let me off lightly here.** The cause is a generalization ACROSS TOOLS.
The plan's measured fact 6b says "`tool.result` records carry the tool's raw
`output` into the wire transcript", which is TRUE, and cites the committed
fixture `evals/multi-model-verify/fixtures/kimi-round/fresh-wire.jsonl:13-18`.
That fixture's `tool.result` is a **Grep** result, whose raw output IS the
answer. The gate then assumed a **Skill** result's output would likewise be the
body. It is not.

I want two things from you on this:

1. Wording for how the gate clause should have read.
2. **A search, not an opinion.** Does the same generalization sit anywhere else
   in this repo's oracles: any check that reads a tool's EFFECT out of that
   tool's own result record? Name files and lines. If you find none, say you
   looked and where.

One correction I am making myself, so you do not adjudicate from a fiction: an
earlier version of the probe record said the committed fixture does not describe
this client's layout. **That was false.** The fixture matches record type for
record type, and the `tool.call` / `tool.result` cited are nested inside
`context.append_loop_event` exactly as they are live. Corrected at commit
`694f323`.

## What I am NOT asking

Do not propose new probes or new features. This debate settles contract text and
scope. The plan's Task 5 is deliberately unwritten until it does.

End your reply with a short list of the points you consider unresolved.
