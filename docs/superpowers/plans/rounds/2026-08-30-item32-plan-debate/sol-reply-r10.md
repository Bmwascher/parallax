## 1. The five required changes

1. The executable order, pinned region, declaration comment, and Task 9 reconciliation now agree: NO RECEIPT → RECEIPT NOT EXPECTED → LAUNCH UNKNOWN. The new nonexistent/uncommitted-directory cases make checking LAUNCH UNKNOWN first observably fail. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:79`, `:127-136`, `:201-231`, `:284-290`, `:762-764` — **CLOSES**

2. The tool contract and named tests correctly make `running` exit 3 and reserve exit 0 for `reply-present`. However, Task 3’s point-of-use text still says “exit 0 covers `running` as well as `reply-present`,” and its per-site test asserts only the command, not the exit guidance. The implementation could be correct while the shipped skill contradicts it. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:57-63`, `:82-83`, `:240-244`, `:355-362`, `:443-447` — **DOES NOT CLOSE**

3. The intended classification is now unambiguous in prose: unreadable receipt content is `no-receipt`/exit 1, while exit 2 is limited to parameter binding or internal execution. But no named case actually supplies an unreadable receipt; the schema test covers malformed content, and the mapping test may construct `no-receipt` using an absent or malformed file. An implementation returning 2 for an unreadable receipt can therefore satisfy every specified case. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:55-63`, `:81-82`, `:129` — **DOES NOT CLOSE**

4. Receipt-path separation now has both a launch-time mechanism and a named test covering equal, one-level-descendant, and two-level-descendant paths before directory creation. The receipt is also still created with create-new semantics. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:50`, `:72`, `:114-123` — **CLOSES**

5. The schema oracle now covers non-object top-level values, every missing field, each empty required string, unparsable ticks, each field holding the wrong type, and unknown fields. That test can fail for every behavior the stated schema distinguishes. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:56`, `:81`, `:129` — **CLOSES**

## 2. Completion-model sweep

I used the requested nine-of-nine base rate; the plan itself still requires treating this class as open. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:21-26`

I searched for:

- a stale receipt, directory, label, commit, PID, exit, or reply crossing acts;
- a live process with a partial reply;
- PID recycling or unreadable process identity;
- a hard kill at every launch-publication boundary;
- malformed, unreadable, or substituted receipt content;
- exit-status-only callers;
- wrapper parse failure, premature wrapper death, and surviving child processes;
- a wrong wrapper or brief reaching a clean evidence binder. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:71-103`, `:116-140`, `:403-418`, `:550-557`

I found no tenth false-completion sequence. The remaining admitted cross-act case requires the caller to supply the earlier receipt, earlier directory, and earlier label together; the plan deliberately classifies that as describing the earlier act rather than silently attributing it to the new one. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:52-53`, `:78-80`, `:235-244`

I did, however, find new internal contradictions and an oracle gap, so the broader base rate becomes ten rounds out of ten even though this round did not expose another artifact-to-result path.

## 3. Prose-only and contradiction sweep

### Rules with mechanisms

The expected-act comparison, path separation, schema, state ordering, PID/start-time identity, and unfinished exit code now have executable steps and named tests. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:72-89`, `:116-140`

The unreadable-receipt distinction remains prose-only because no test creates an unreadable receipt and asserts exit 1. Passing a directory as `-Receipt` would provide a deterministic cross-host unreadable-file case. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:61`, `:81-82`, `:129`

### Contradictions

1. **Point-of-use exit guidance:** the state contract says `running` exits 3 and only `reply-present` exits 0, while Task 3 says exit 0 covers both. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:57-63`, `:240-244`, `:443-447`

2. **Which artifact is last:** the architecture, tool region, and test name call `launch.committed` the last artifact, while the executable sequence writes `launch.committed` and then publishes the receipt “last of all.” `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:7`, `:50`, `:74`, `:121-123`, `:181-185`

   The accurate contract is: PID/start ticks → internal `launch.committed` marker → external receipt as the transaction’s final publication.

3. **Spec reconciliation is incomplete:** the current design still says the session itself runs `Start-Process`, writes the PID, and later polls it. Task 9 updates the state model, regions, quoting, encoding, and reversed tool decision, but does not explicitly replace that mechanism section; its grep does not detect the stale session-owned launch sequence. `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:136-148`, `:264-277`; `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:762-779`

The spec’s current seven-state count and old region inventory are not separate findings because Task 9 explicitly names and gates those replacements. `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:190-207`, `:285-291`; `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:762-779`

## 4. Freeze decision

The plan is not ready to freeze. The smallest sufficient changes are:

1. Replace Task 3’s stale exit sentence with “exit 3 means running; exit 0 means reply-present only,” and make the per-site oracle assert it.
2. Add `test_an_unreadable_receipt_is_no_receipt`, using a directory as the receipt path and requiring state `no-receipt`, exit 1.
3. Replace every “launch-commit artifact last” claim with the actual order—PID/start ticks, internal commit marker, external receipt last—and make the order test assert all three.
4. Make Task 9 explicitly replace the spec’s session-owned `Start-Process` mechanism with the shipped-tool/receipt transaction, and add a positive oracle for the tool path and receipt-based Poll interface.

The fresh-shell and background-Agent facts remain explicitly non-repository-verifiable, while real harness detachment and cross-host non-ASCII transport remain future Task 8 measurements. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:32`, `:717-741`

**FIX**