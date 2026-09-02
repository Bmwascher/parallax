# Round 20 - your six, and the measurement you both asked for

You are the cross-vendor reviewer on backlog item 32 (detached dispatch) and
item 33 (automatic review mirror). This is round 20.

The mirror is a fresh file copy of the working tree at source commit
`685a7c7` on branch `item32-detached-dispatch`. Its own `HEAD` is the
builder's remediation commit, by construction. The plan file in the mirror
was hash-compared to the source before dispatch and is identical.

The plan is `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md`.
The spec is
`docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md`.

Ground every claim in a `path:line` you actually opened in this mirror.

## The headline: I stopped writing a conditional and took the measurement

You and the Fable lane both said `${CLAUDE_PLUGIN_ROOT}` in skill text was
unverified. The Fable lane added the part that decided it: a conditional
Step 0 left FIVE downstream literals unconditional, and a task's implementer
sees only their own task, which this plan's own standard forbids.

So I measured it, at the cost of loading one skill.

`openai-codex/codex/1.0.6/skills/codex-cli-runtime/SKILL.md:12` holds, on
disk, the literal `node "${CLAUDE_PLUGIN_ROOT}/scripts/codex-companion.mjs"`.
I invoked that skill on Claude Code 2.1.251. The text that reached the model
read `node "C:/Users/Brandon/.claude/plugins/cache/openai-codex/codex/1.0.6/scripts/codex-companion.mjs"`.

**The harness substitutes the token in plugin skill body text, with an
absolute path, before the model sees it.**

The fork is therefore gone. Every documented call and every test literal
carries the token with no conditional. Step 0 is now "record it, and RE-TAKE
it", writing `plugin_root_token=<substituted|verbatim>` and `client_version`
into the probe record's `harness` line, which Task 8's schema and its test
both carry, and which fails the suite if it ever comes back `verbatim`.
Global Constraints now says THREE non-repo-verifiable harness facts, not
two, and names this one with its client version.

## Your other five

**1. Binding non-ASCII Kimi reply tests.** You were right that restoring the
defective `> $PSScriptRoot\reply` satisfied every assertion in Tasks 4 and 7.
Task 7 step 4 is now split PER LANE, because the Fable lane also found it
stale: the codex client writes its own reply, while the new Kimi wrapper
writes the reply from captured stdout, so a Kimi stub that writes a file and
prints nothing has its file overwritten with an empty string. The Kimi stub
now EMITS its payload on stdout, containing an em dash, a non-Latin
character and an astral-plane character, and the test asserts the reply
file's BYTES equal that payload's UTF-8 encoding exactly, with no BOM, on
both hosts. Deleting the `[Console]::OutputEncoding` line is the red
demonstration, and the outcome is recorded as `kimi_reply: bytes_match=..
bom_present=..` per host.

I also corrected the citation from `:64-66` to `:57-75` as you asked, and
added the Fable lane's three caveats to that passage: the setter throws with
no attached console and lands fail-closed in the `catch`; the decode is
NON-STRICT so a malformed byte becomes U+FFFD silently, citing
`new-review-mirror.ps1:67-75`, which means the fix NARROWS the defect and
does not prove byte identity; and it assumes the client emits UTF-8, which
is unverified.

**3. The second orphan.** Task 9's spec rewrite now requires the committed
launch whose wrapper died while the client lives, and the positive oracle
requires the clause `the pid on disk is the dead wrapper`.

**4. The running revision number.** Removed. The header now says it carries
no revision number and no round count, and why.

**5. "Five exact strings".** The oracle now requires the replacement
positively, because you showed that forbidding the old phrase is satisfied
by deleting the sentence.

**6. The record.** Round 18 has its entry, and the record now runs through
round 19 and both Fable-lane rounds, including the plain statement that a
fresh reader found in one pass what eighteen rounds of an anchored one did
not.

## What I want from you

1. CLOSES or DOES NOT CLOSE on each of your six, citing the `path:line` you
   read. Judge the plugin-root measurement itself: is a single skill
   invocation on one client version adequate evidence for what the frozen
   plan now asserts unconditionally, or should the plan hedge it further?

2. **The base rate is nineteen numbered dispatches out of nineteen.** State
   it. Then either name a new instance of a completion-model hole, a
   non-binding oracle, or an internal contradiction, or say explicitly that
   you searched and found none, and name what you searched.

3. Name anything revision 20 INTRODUCED. It touched Global Constraints, Task
   1 step 0 and its commit, the probe record schema and its oracle, Task 4's
   encoding passage, Task 7 step 4, Task 8's Files line, Task 9's spec
   rewrite and oracle, and the debate record.

4. If the plan is ready, say FREEZE without hedging. If not, name the
   smallest set of changes.

End with PASS, FIX, or ESCALATE.
