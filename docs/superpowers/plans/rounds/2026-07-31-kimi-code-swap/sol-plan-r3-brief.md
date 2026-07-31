<task>Round 3. Your round-2 challenge to the record cardinality was correct, so we
stopped arguing and measured. Six model calls against a tool-using review.
The plan was rewritten whole against the results. Read
docs/superpowers/plans/2026-07-31-kimi-code-swap.md and the new
docs/superpowers/plans/rounds/2026-07-31-kimi-code-swap/probe-record-2.md.
Evidence rules, verdict grammar and boundaries as before.</task>

<measured-results>
Your cardinality objection was right and the truth was worse than either of us
supposed. Measured, sliced at the pre-call offset:

  record                    fresh (tool-using)   resumed (tool-using)
  config.update                    2                    0
  tools.set_active_tools           1                    0
  llm.tools_snapshot               1                    0
  permission.set_mode              1                    0
  turn.prompt                      1                    1
  llm.request                      4                    2

So revision 2's "exactly one of each in the slice" failed a CLEAN round 1
twice over and every resumed round three times over. Records split into
session-scoped (written once at session creation) and per-call. The plan now
states both classes and checks each where it appears, and requires the
session-scoped records to be ABSENT from a resume slice - which recovers the
old lane's session-kind check.

Other measurements that settled open points:

- systemPromptChars equals the agent body length EXACTLY (431 everywhere).
  Now an evidence check in its own right.
- --skills-dir changes NOTHING measurable. With canary skills planted at both
  documented project roots, runs with and without it were identical, and the
  reviewer asked to list its skills answered NONE. It is a mitigation, not a
  control. The controls are the allowlist excluding Skill, and preflight-3
  remediation. The plan now says exactly that, and Task 9 is re-scoped from
  "defence in depth" to PRIMARY control.
- Thinking-enabled has NO observable signal: enabled=false produced output
  identical to enabled=true. Config-asserted only; the plan no longer claims
  it is verified.
- Effort IS pinnable: default_effort="low" produced thinkingEffort=low.
- Resume ACCEPTS -m, --skills-dir and --add-dir; it rejects only --agent-file,
  with the message "the agent is bound at session creation". Tested free
  against a bogus session id. So the plan re-pins everything re-pinnable,
  which is your round-2 point about defence in depth, taken.
- subagents: [] resolves to an empty array.
</measured-results>

<what-else-changed>
All fourteen round-2 defects are fixed. The ones worth naming: the TryParse
branch is now reachable because $kimiVersion takes the raw value; the state
machine stub moves to the absolute path under the fake profile, advertises
--session, and gains a below-floor mode; removal is a -Remove switch guarded
by a sentinel file rather than an unreachable function; the git check fails
closed on $LASTEXITCODE; the build is transactional so a failure cannot strand
a credential; the validator takes -ExpectedBriefSha256 and -Provider; the
freshness boundary now hashes the pre-call PREFIX, which is your
replaced-and-regrown objection; the tool test asserts set equality against a
frozen inventory rather than a count; Task 8 filters on full path instead of
-Exclude; Task 11 captures offsets BEFORE dispatch; declarations moved to
Task 2 so nothing forward-references them; Task 6 captures its own fixtures so
nothing depends on a deleted probe home.

Task 6's test list is now thirty-one enumerated cases in five groups.

Still declined, with reasons in the plan: binding toolsHash to a client
version, and a sacrificial resume write-probe every debate.
</what-else-changed>

<claims>
1. The two-class evidence rule is correct and complete against the measured
   record behaviour, and nothing in it can be satisfied by a prior round's
   records.

2. The freshness boundary, now including the prefix hash, closes your round-2
   identity objection.

3. Naming --skills-dir a mitigation and moving the load to the allowlist and
   preflight-3 is the right response to it controlling nothing measurable.
   Consider whether the plan now over-relies on remediation.

4. Task 6's thirty-one cases are sufficient. Name any failure mode of the
   evidence rule that no listed case would catch.

5. The revision introduced no new defect. Attack the new material: the
   two-class rule's resume branch, the prefix-hash logic, the sentinel-guarded
   removal, the transactional build, the reachable TryParse, and the frozen
   KNOWN_TOOLS constant.

6. The plan is now executable by an engineer with no repository context.
</claims>

<final-check>
List anything you could not verify against files you read this session, as
UNVERIFIED.
</final-check>
