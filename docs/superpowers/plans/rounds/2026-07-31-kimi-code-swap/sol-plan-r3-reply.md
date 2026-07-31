Revision 3 correctly adopts the measured cardinalities, but the evidence rule still has gaps. Claim 3 passes; the other five need fixes.

1. Two-class evidence is complete and excludes prior-round records

The class split matches the probe: two `config.update`, one active-tools/snapshot/permission record at creation; one prompt and variable requests per call (`probe-record-2.md:23-64`; plan `:40-42,603-605`).

The checks are incomplete:

- The second `config.update` carries `modelAlias` and `thinkingEffort`, but validator rule 6 never compares those fields (`probe-record-2.md:52-56`; plan `:603`).
- `permission.set_mode` is counted but its required `mode=auto` value is never checked (`plan:603`).
- Every request is checked for route fields, but not for nonempty and identical `toolsHash`/`systemPromptHash`. One request in a tool loop could use a different surface while the validator emits hashes from another (`plan:604-606,657`).
- The validator does not require record ordering. A stale wire offset positioned after a prior round’s `turn.prompt` but before its `llm.request` records can produce a slice containing old requests plus the current prompt and current requests. It still has exactly one prompt and one-or-more canonical requests, so it can pass. Only offset zero is tested (`plan:563-564,603-605`).
- The supplied offset and prefix hash are not bound to the immediately preceding validator result. A valid older offset/hash pair can therefore be replayed.

Verdict: **FIX — validate both `config.update` payloads and permission mode, require every request’s hashes to be present and identical, enforce current-turn ordering/association, and bind each invocation to the previous validator’s returned state.**

2. Prefix hashing closes the identity objection

It closes replacement-and-regrowth only for the wire transcript. The interface has one `PrefixSha256`, and rule 4 hashes only the first `WireOffset` lines (`plan:541-542,567,601`). The log still has length-only protection, despite the outstanding rotation question specifically concerning the per-session log (`probe-record-2.md:151-158`).

The wire hash is also underspecified: “SHA-256 of the existing lines” does not define encoding, newline framing, or whether raw file bytes or `Get-Content`-normalized strings are hashed (`plan:601,653`). Two implementations can produce incompatible hashes for the same file.

Verdict: **FIX — carry independent wire-prefix and log-prefix hashes, hash exact raw bytes through byte offsets or define deterministic line framing/encoding, and test replacement-and-regrowth for both files.**

3. `--skills-dir` is correctly classified as a mitigation

Confirmed. The measured runs cannot credit `--skills-dir` with suppressing anything, while the reviewer could still read both planted skill files as ordinary workspace content (`probe-record-2.md:75-105`). The plan accurately separates:

- Allowlist containment against invoking the `Skill` tool.
- Preflight remediation against ordinary `Read` access to hostile project files.
- `--skills-dir` as a cost-free, uncredited mitigation (`plan:667-668`).

Making remediation primary for reviewed-tree `.kimi-code/` content is appropriate, not over-reliance: removal is the only named control that prevents the reviewer from reading those files as ordinary subject material (`plan:733-753`).

Verdict: **PASS**

4. Thirty-one cases are sufficient

Uncovered failure modes remain:

- Wrong `modelAlias` or `thinkingEffort` in the second `config.update`.
- Wrong `permission.set_mode.mode`, missing permission record, duplicate permission record.
- Duplicate `config.update` or two copies of the first shape with the second shape absent.
- Resume slices containing forbidden session-scoped records—the core resume branch has no explicit negative test (`plan:556-587,603`).
- Missing, null, or divergent request hashes inside a multi-request tool loop.
- Wrong provider/model/effort in the log line; the listed inequality case covers requests but not the log (`plan:584-587,604`).
- Log prefix replacement-and-regrowth.
- A stale offset beginning midway through the previous call rather than at zero.
- Invalid or inconsistent `Kind`, offsets, and prefix state.
- A malformed JSON line before the supplied offset paired with a replayed older state.

One listed test is not implementable through the declared interface: after a successful fresh dispatch, the session directory necessarily exists. The validator receives no pre-call “directory existed” measurement, so it cannot distinguish a newly created directory from a pre-existing directory with zero offsets (`plan:541-542,568,598-606`).

Verdict: **FIX — add the cases above and pass an authenticated/pre-call state object containing prior existence, both offsets, and both prefix hashes.**

5. No new defect was introduced

New defects remain in the attacked material.

High — drift harness:

The plan still does not provide an executable absolute-path stub. It correctly says a `.cmd` renamed `.exe` will not execute, but then proposes creating a `.cmd` and somehow making the production `.exe` path find it (`plan:176-185`). The production code performs an exact `Test-Path` and invocation of `.kimi-code/bin/kimi.exe` (`plan:123-133`). This needs a real executable stub or an explicit injected test seam.

High — version probe:

A present binary whose `--version` invocation fails or returns empty still reaches the “binary absent” note because neither `$LASTEXITCODE` nor the empty-result distinction is checked (`plan:123-133,150-170`). `--help` exit status is also unchecked (`plan:150-157`).

High — frozen inventory:

`KNOWN_TOOLS` is defined as the union of the lists being tested, then the test compares that same union back to `KNOWN_TOOLS`. It is tautological and detects neither swapped names nor omissions (`plan:438-448,477-485`). It must be an independent explicit frozen set.

High — removal interface:

The interface promises `-Path <dir> -Remove` without `-Model`, while the mandated test requires `$Model` to be globally mandatory (`plan:275,296-301,325-331`). Proper PowerShell parameter sets are required, and the test must recognize that form.

Medium — sentinel and transaction:

A filename-only sentinel can be planted in any directory and then authorizes recursive deletion. It should contain builder-specific magic plus the resolved path, and removal must still reject roots, the user profile, and repository roots (`plan:363-370`). Transaction cleanup is specified as an unconditional recursive delete; it should run only after this invocation successfully created and marked the directory. The static test does not inject a post-credential failure to prove cleanup (`plan:334-337,367-369`).

High — new evidence fields:

The new two-class implementation omits validation of the second config payload, permission mode, and per-request hashes, as described under claim 1 (`plan:603-606`).

Verdict: **FIX — replace the impossible stub instructions, fail closed on command exit/empty output, make the inventory independent, use parameter sets, harden sentinel deletion, fault-test transaction cleanup, and complete the two-class comparisons.**

6. Executable without repository context

There are still concrete execution blockers:

- The `-Remove`/mandatory-model parameter contradiction leaves the builder’s command surface undefined (`plan:275,296-301,325-331`).
- The absolute-path drift stub instructions do not identify a runnable implementation (`plan:176-185`).
- The validator cannot execute the “session directory did not exist before dispatch” test from its declared inputs (`plan:541-542,568`).
- The rotation probe says to exceed “any plausible rotation threshold,” which gives an engineer no finite success criterion (`plan:407-411`).
- The validator does not define how to parse the two distinct `config.update` shapes, which request supplies emitted hashes, or how prefix-line hashing is encoded (`plan:601-606`).
- The contract says recording hashes prevents silent rebaselining, but comparison remains caller-performed rather than part of the executable validator (`plan:606,657`).
- Task 11 uses returned offsets but does not mention persisting or passing the returned prefix hash, which is required by the validator interface (`plan:541-542,811-814`).

Verdict: **FIX — resolve the builder parameter sets and harness stub, make the complete pre-call state an explicit validator input/output object, define exact parsing and hashing algorithms, and give every probe a finite success criterion.**

UNVERIFIED:

- The cp1252 output behavior and per-session rotation behavior remain explicitly unmeasured (`probe-record-2.md:151-158`).
- Cardinality and ordering for substantially larger tool loops remain unmeasured (`probe-record-2.md:159-161`).
- Whether user-global `~/.agents/skills/` behaves like the two measured project roots; the probe covered only project roots (`probe-record-2.md:14-18,75-98`).
- Effective ACLs, transactional cleanup, and sentinel removal on both PowerShell hosts; the builder does not yet exist.
- Resume inheritance on releases after 0.31.1; all measurements are version-specific (`probe-record-2.md:3,131-149`).