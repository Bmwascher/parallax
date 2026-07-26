Blocking finding: the amended Task 6 still instructs the executor to consume the installed `0.12.0` cache and describes only a pre-`0.12.0` cache as stale (`docs/superpowers/plans/2026-07-25-flash-implementer.md:647-653`). The amended agent exists only in plugin `0.12.1` (`.claude-plugin/plugin.json:3`), and resolved row 25 explicitly makes that bump part of the amendment (`plan:777`). D-a proves this distinction is load-bearing: the `0.12.0` cache served the old contract and invalidated the run, whereas the restarted `0.12.1` run exercised the closing line (`.superpowers/sdd/2026-07-25-flash-implementer/progress.md:44-45`).

Prior F1: **PASS.** The exact closing line is brief-borne at `agents/flash-implementer.md:67-76`, pinned at `test_flash_implementer.py:51-56`, synchronized into the spec at `design.md:203-211`, and Task 6 now forbids controller supplementation at `plan:665-671`. The embedded test block is line-identical and the agent block word-identical.

D-a: **PASS, non-blocking.** It was correctly invalidated before being used as evidence (`checkpoint:64-67`); the valid post-restart run is separately recorded at `checkpoint:59-61`.

D-b: **PASS, non-blocking for this head.** The variance occurred under the old cached agent (`checkpoint:67-71`). The amended agent retains the soft-deny blocking rule (`agents/flash-implementer.md:97-107`), the valid amended run produced no soft-deny, and the amended sentinel path blocked correctly (`progress.md:45-46`). There is no evidence that the installed `0.12.1` agent violated its current contract.

Suites: **UNVERIFIED independently.** Their post-wave results are recorded at `checkpoint:57-58`, but Python remains unavailable in this sandbox. This is not folded into the verdict.

Specific fix: change Task 6’s interface to “installed `0.12.1` cache” and Step 1 to “cached pre-`0.12.1` set”; also attribute the committed bump to row 25 rather than only Task 5. No agent, test, version, or agy rerun is required.

**VERDICT: FIX — stale, load-bearing Task 6 cache-version instructions; Fable 5 / GPT-5.6 Sol, 2 mode-diff rounds, not converged, verification FULL.**