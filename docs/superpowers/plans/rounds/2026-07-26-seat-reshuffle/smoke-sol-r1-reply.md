> QUARANTINED (driver marker, 2026-07-26): this round ran while an untracked AGENTS.md (the user's Codex-app "Import agent setup" output) sat at the repo root — an instruction back-channel codex ingests. Under the narrow FULL ruling (mode-diff debate, 0.14.0) this round's evidence does not count toward the panel record; it is retained verbatim below as incident evidence, and its findings entered the record only as driver-verified amendments. Clean replacement lane: smoke-sol2-r1 / smoke-sol2-r2.

1. **FIX.** ROUTE, FILES CHANGED, and VERIFICATION have direct evidence requirements (`agents/flash-implementer.md:83-95`, `agents/flash-implementer.md:114-118`). DEVIATIONS, however, is only required to say `none`; no wrapper-side conformance check proves that assertion, and the contract says plan drift is checked afterward (`agents/flash-implementer.md:22-26`, `agents/flash-implementer.md:119-120`). Consequently, an unconditional `STATUS: done` also cannot establish exact task fidelity from those artifacts alone. **Specific fix:** narrow the claim to direct observability of route metadata, git-visible changes, and verification output; characterize `DEVIATIONS: none` and `done` as wrapper adjudications still subject to the later diff-versus-plan check.

2. **FIX.** The clean-tree preflight provides a recoverable baseline (`agents/flash-implementer.md:60-61`), and blocked reports preserve paths currently reported by `git status` (`agents/flash-implementer.md:114-116`). But “always” and “every path Flash already touched” are stronger than the supporting rules: authorship corroboration is only one-way—every path reported changed by Git must appear in the transcript—not a guarantee that every transcript write remains represented by Git status (`agents/flash-implementer.md:87-92`). **Specific fix:** state that the report supports recovery of every remaining, git-visible partial change from the clean baseline.

3. **PASS.** `INPUT GAP` is a separate STATUS value (`agents/flash-implementer.md:111`), and the corresponding rule requires stopping, reporting the missing input, and never inventing or guessing it (`agents/flash-implementer.md:27-30`).

4. **PASS.** Deviations are defects under the lane contract (`agents/flash-implementer.md:24-26`); the report permits only `none`, with any other content explaining why execution stopped rather than recording an accepted deviation (`agents/flash-implementer.md:119-120`).

**UNVERIFIED:** none.

**OVERALL: FIX — subject revision `c95f18e1ec2cb6a5d7de586557e072e638583e9f`, blob `69dbdb0f77d6606e5729ffe5414bc131aa4922e8`; claims 1 and 2 overstate the guarantees established by `agents/flash-implementer.md:83-120`.**

