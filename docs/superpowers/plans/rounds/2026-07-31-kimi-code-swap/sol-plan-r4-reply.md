Revision 4 is substantially tighter, and I withdraw the demand that the plan prescribe the parsing algorithm. The test specification still has several missing observable cases, however.

1. Every round-3 defect is fixed without introducing another

Several new mechanisms now stand:

- Absolute `.cmd` resolution is executable and remains confined to the fixed Kimi bin directory (`2026-07-31-kimi-code-swap.md:142-166,214-224`).
- Parameter sets correctly separate Build and Remove (`:312-317,338-346`).
- Independent byte offsets and prefix hashes close the prior framing/asymmetry defects (`:625-634,699-711`).
- The second config update, permission mode, request hashes, slice boundary, and continuity are now explicit checks (`:682-687,705-710`).
- `KNOWN_TOOLS` is genuinely independent (`:515-532,561-569`).

New defects remain:

- If `--help` fails or is empty, the script records the measurement failure but still executes the flag loop against missing/error output, generating five additional findings that describe nothing (`:187-197`). The loop needs an `else`.
- A thrown `--help` invocation is not caught, so it can abort the drift run before producing the intended finding (`:187-190`).
- The “frozen inventory” comment says the floor forces re-probing on upgrade, but a lower bound accepts every newer version and contains no version-transition stop (`:565-567,180-208`).
- The root-guard test checks only generic text and `$env:USERPROFILE`; the live cases likewise omit a correctly formed sentinel at a drive root or in a tree containing `.git` (`:386-392,448-458`). Those are explicit removal requirements at `:434` but are not executable acceptance cases.
- `-PriorState` does not bind the resolved session directory or session id. Prefix hashes usually make cross-session reuse fail, but the state object does not directly enforce the claimed session ownership (`:625-634,699-711`).

Verdict: **FIX — stop after failed help measurement, catch help invocation failures, test every destructive root guard, bind state to the session identity, and remove the false upgrade-reprobe claim.**

2. The contested position is correct

I withdraw the standalone objection that the plan must prescribe the parser algorithm. The plan now defines:

- Inputs and outputs.
- Raw-byte offset/hash semantics.
- Rule ordering.
- Record cardinalities and field equalities.
- Named failure reasons.
- Clean and negative fixtures written before implementation (`:615-644,646-711`).

For this program, an independently written test suite covering every externally observable invariant is a better specification than duplicating implementation pseudocode in the plan. My remaining objections are missing cases, not the absence of an algorithm description.

Verdict: **PASS**

3. The case list sufficiently constrains a correct implementation

Missing observable cases remain:

- A valid-JSON relevant record with structurally invalid fields—such as non-array `input`, missing `text`, or a non-string hash—must return failed JSON rather than throw or silently coerce. Only syntactically non-JSON input is covered (`:664-688`).
- `-PriorState` fields with wrong types, negative offsets, offsets larger than the PowerShell integer range, malformed hash lengths, or `sessionDirExisted` as a string are not covered (`:661-662,699`).
- `-Kind resume` with `sessionDirExisted:false`, and `-Kind fresh` with nonzero offsets or continuity hashes, are internally inconsistent states without cases (`:627,660-662,699-700`).
- Missing, unreadable, or malformed `-AgentFile` is not covered, despite the validator parsing its frontmatter and exact body (`:625,676-680,706`).
- An invalid `-ExpectedBriefSha256` is not covered (`:625,688,710`).
- Two copies of the second `config.update` shape with the first absent is the untested symmetric counterpart to the listed “two first shapes” case (`:670-672,706`).
- `llm.tools_snapshot.hash` missing or differing from the `toolsHash` carried by every request is untested and not required. Consistent request hashes should still fail if they contradict the snapshot that supposedly describes the sent schemas (`:677,685-686,706,708-709`).
- A prior state belonging to another session directory has no explicit negative case because session identity is absent from the state schema (`:627,661-662`).

These are testable behavioral cases; none requires prescribing the implementation.

Verdict: **FIX — add cases for malformed typed inputs, inconsistent state, agent/expected-hash failures, both config-shape substitutions, snapshot/request hash disagreement, and cross-session state reuse.**

4. Executable by an engineer without repository context

Most earlier blockers are gone, but correctness remains underdetermined in three places:

- The state-machine implementation is executable, but the plan does not specify that the flag loop must be skipped after a failed help measurement; an engineer following the supplied code exactly ships false secondary findings (`:187-197`).
- The validator’s state schema lacks session identity while claiming that one state is bound to the previous invocation (`:627-634`).
- Destructive guard acceptance does not exercise the `.git` and drive-root branches it requires (`:434,448-458`).

There are also two smaller execution defects:

- Task 11 numbers two consecutive steps as “6” (`:919-921`).
- The fault-injection step does not explicitly clear `PARALLAX_LANE_HOME_FAULT` afterward, so subsequent builds in the same shell can continue failing (`:438,456`).

Verdict: **FIX — close the remaining code-path ambiguity, complete destructive live tests, include session identity in state, clear the fault seam, and correct the handoff sequence.**

5. Nothing claims more than measurement supports

Three overclaims remain:

- “The floor check … forces a re-probe at upgrade” is false. It rejects versions below 0.31.1 and accepts newer ones (`:565-567,180-208`).
- “Resume accepts every flag but `--agent-file`” exceeds the measurement. The probe tested `-m`, `--skills-dir`, `--add-dir`, and `--agent-file`; it did not test every CLI flag (`:45,751,931-936`; `probe-record-2.md:131-149`). Say “of the four tested flags.”
- The plan requires the fresh slice’s first record to be a session-creation record, but the retained probe record establishes counts, not first-record ordering (`plan:705,758`; `probe-record-2.md:23-64`). The forthcoming clean fixture can establish that order, but it is not currently a measured fact.

The plan’s narrower claims about skills, effort, thinking, subagents, and cardinality match the recorded evidence (`probe-record-2.md:23-129`; plan `:41-51,760-773`).

Verdict: **FIX — narrow the resume wording, stop claiming the floor forces re-probing, and mark fresh-record ordering as fixture-gated until Task 6 measures it.**

UNVERIFIED:

- cp1252 output behavior and per-session rotation beyond the proposed 16 MB probe depth (`plan:469-492`).
- Fresh-slice first-record ordering; the current probe record gives cardinalities but not order.
- Whether real Windows Kimi distributions may ship as `.cmd`; the current measured installation is an `.exe`.
- Effective ACL, fault cleanup, parameter-set behavior, and destructive guards on both PowerShell hosts; the builder is not implemented yet.
- User-global `~/.agents/skills/` behavior; the retained canary probe covered the two project roots.
- Resume behavior for untested flags and releases after 0.31.1.