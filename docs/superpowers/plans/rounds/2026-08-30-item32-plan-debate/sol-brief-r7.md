# Round 7 - revision 6 answers round 6

You are the cross-vendor reviewer on backlog item 32 (detached dispatch) and
item 33 (automatic review mirror). This is round 7 of the plan debate. Your
round 6 reply is above in this session; every FIX in it is answered below.

The mirror you are reading is a fresh copy of the repository at commit
`c8d6b6c` on branch `item32-detached-dispatch`. The plan is
`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md`. The spec is
`docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md`.

Ground every claim in a `path:line` you actually opened in this mirror.

## What changed since round 6

**1. Launch token (your sweep (a), the fifth false-completion path).**
`-Launch` now mints a GUID token, writes it INSIDE `launch.committed`, and
returns it. `-Poll` requires `-Token <token>`. A commit artifact that does
not carry the supplied token is `launch-not-ours` and stops the poll before
any other artifact is read. Plan `:49`, `:51`, and the ordered checks. The
regression test you asked for is
`test_a_refused_launch_cannot_poll_the_old_rounds_reply`: run a stub launch
to real success, launch again on the same path, take the refusal, then poll.
The documented poll command now carries the token at `:376`, and the
launch block above it states that the token must be kept.

**2. Host boundary (your sweep (b)).** Every documented call is now
`& (Get-Process -Id $PID).Path -NoProfile -File ...`, not a bare
`powershell`. The test strings changed with them, and a new test,
`test_the_documented_outer_command_works_on_this_host`, runs the exact
documented outer command rather than the script.

**3. Per-site codex oracles (your sweeps (c) and finding 4).** The global
`>= 2` count is gone. `CODEX_CALLS = ("codex-fresh", "codex-resume")` is
parametrized exactly like the Kimi one, splitting on
`<!-- call:codex-fresh -->` and `<!-- call:codex-resume -->`, and asserting
a launch, a poll and a client invocation inside each section. The
`Start-Process` absence assertion survives as
`test_no_codex_lane_writes_its_own_launch`, whose docstring states in terms
that it is a centralization guard and cannot show that every site reaches
the tool.

**4. Pid validation and fixture provenance (your sweep (d)).** The state
list is now ten: `launch-unknown`, `launch-not-ours`, `pid-unreadable`,
`running`, `no-exit-file`, `exit-unreadable`, `exit-nonzero`, `no-reply`,
`reply-empty`, `reply-present`. Terminal-state fixtures must be built by
running a stub launch to a real success and then altering ONLY the artifact
that case is about. `test_a_hard_kill_between_start_and_publication_is_never_success`
kills the TOOL in that window rather than injecting a handled failure.

**5. Injectable document paths (your finding 5, first half).** Task 2 gains
a step making `collect_regions` and the two coverage tests accept an
optional `doc_paths` argument, because `DOC_PATHS` is a module constant at
`evals/multi-model-verify/test_contract_coverage.py:611` read directly at
`:737` and `:749`, so the negative oracle could not be run at all.

**6. The convergence grep (your finding 5, second half).** It now searches
for `encoding preamble moves INSIDE the wrapper`, `every wrapper`,
`eight states`, `nine states`, and `powershell -NoProfile -File`, and the
step states the exact replacement wording for the encoding claim.

**7. Ceiling ordering (your finding 7).** The measurement command now
exists in Task 2's preamble, and the measure-and-maybe-raise step moved to
Task 3, immediately before that task's lint oracle, because strict lint
gates Task 3's own commit. Task 9 step 1 only records what Task 3 decided.

## What I did NOT change, and why

- I did not add a mechanism that makes polling impossible before a
  successful launch. The token is carried by the caller. If you think a
  caller that ignores the token is still a reachable false completion, say
  so and name the mechanism that would close it.
- Your three UNVERIFIED items stand as stated. I did not claim
  `${CLAUDE_PLUGIN_ROOT}` substitution is verified by an existing test.

## What I want from you

1. For each of your round 6 FIXes above, say CLOSES or DOES NOT CLOSE, with
   the `path:line` you read. Do not accept my summary; read the plan.

2. **Sweep the class again, and state the base rate when you answer.** Six
   rounds have each found at least one completion-model hole or an oracle
   that binds nothing. Round 6 found the fifth completion hole. Either name
   a SIXTH instance with its input, its sequence and the artifact it would
   be read from, or say explicitly that you searched and found none, and
   name the shapes you searched for.

3. Specifically: the token is a caller-carried secret. What ELSE could take
   the shape of "an artifact from a different act being read as this act's
   result"? Name the shapes, not only the instances.

4. Is the plan now executable by an implementer who sees ONE task and the
   Global Constraints, with no other context? Name any task whose steps
   cannot be carried out from its own text.

End with PASS, FIX, or ESCALATE.
