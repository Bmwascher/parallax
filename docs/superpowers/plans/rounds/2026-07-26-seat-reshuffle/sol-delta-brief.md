Delta-confirmation. Evidence rules and verdict grammar as before. Your
confirmation-round items were folded at commit dca790c; verify each in
the re-committed spec docs/superpowers/specs/2026-07-26-seat-reshuffle-design.md:
BLOCKING (plan-mode subject revision) -> section 6 now splits by mode:
diff pins base..head SHAs; plan pins the SHA-256 of the current round
claims bytes with the frozen-plan blob hash taking over only at freeze.
Important-1 (envelope propagation) -> section 5 adds the ENVELOPE
PROPAGATION block (frozen-plan-format carve-out + SKILL mode-diff
clause, both test-pinned in section 11) and the consented reroute
envelope is recorded durably in the SDD ledger. Important-2
(Fable-only remainder) -> section 7 splits remainder status by
surviving-lane vendor: surviving Sol/Kimi clean may record FULL;
surviving Fable-only records DEGRADED under the existing single-vendor
contract with the poisoning rule applying; Participants lists terminal
lanes, the lost lane lives in failure prose. Important-3 (one-round
smoke cannot test resume) -> section 13 makes the smoke two rounds
(fresh dispatch + one resumed rebuttal per lane). Important-4 (probe
record contract) -> the full record (Claude Code 2.1.220, exact
mechanics, verbatim replies, residual limits) is committed at
docs/superpowers/plans/rounds/2026-07-26-seat-reshuffle/subagent-resume-probe.md,
section 15 cites it, and the build adds the dated
model-prompting-notes.md bullet. Minor (vocabulary) -> section 4 now
uses accept / refute / ESCALATE. Also folded from the other lane
convergently: durable raw-reply retention (same rounds dir). Confirm
each delta and end with one verdict on the spec at dca790c: SOUND /
SOUND-WITH-FIXES / RETHINK.
