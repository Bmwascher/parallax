The core fresh/resume split is sound, but the fresh validator interface still cannot instantiate that design without inventing missing inputs and directory-selection rules. One structural repair remains.

1. The identity model is directionally correct:

- Exactly-one-new-session fails closed for zero-session and concurrent-session outcomes ([plan:698](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:698), [plan:752](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:752)).
- Cross-checking the discovered directory name against the reported session ID is independent evidence ([plan:752](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:752)).
- Skipping offsets and prefix hashes for a newly established fresh directory is correct; there is no pre-call file prefix to authenticate ([plan:757](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:757)).
- Always emitting a resume-shaped state gives later calls a uniform continuity chain ([plan:767](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:767)).

But the interface does not supply what rule 2 needs. The declared command still requires `-SessionDir` unconditionally and omits `-SessionIdFromStdout` ([plan:656](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:656)). The fresh branch is supposed to discover the session directory itself and requires the omitted stdout parameter ([plan:663](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:663), [plan:752](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:752)). Task 11 likewise supplies the stdout ID but never explains what fresh callers pass as the still-required `-SessionDir` ([plan:972](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:972), [plan:973](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:973)).

Nor can the validator locate the inventory root from the fresh state: that state carries only `kind` and possibly an empty `knownSessionDirs` list ([plan:660](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:660)), while rule 2 refers to `<debate-home>/sessions` without receiving the debate home or sessions root ([plan:752](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:752)).

The inventory member definition is also material. Measured storage is nested as `<home>/sessions/wd_<workspace>/<session-id>/` ([probe-record.md:166](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-07-31-kimi-code-swap/probe-record.md:166)). A generic recursive directory inventory on a clean home can see both a newly created `wd_<workspace>` container and its session child, producing two “new directories” and rejecting a clean call. The rule must define inventory members as session-leaf directories, not every directory below `sessions`.

Two smaller inconsistencies remain:

- No rule explicitly requires `PriorState.kind == -Kind`; rule 1 validates shape and rule 3 discusses fields, but neither states that equality ([plan:750](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:750), [plan:754](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:754)).
- The clean-case list still says a fresh call has “correct offsets,” contradicting the fresh shape and rule 6 ([plan:660](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:660), [plan:685](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:685)).

**FIX — Give the validator explicit Fresh and Resume parameter sets. Fresh must receive a validated `sessionsRoot` and mandatory `SessionIdFromStdout`, must not receive `SessionDir`, and must inventory only defined session-leaf directories. Resume must require `SessionDir` and forbid the fresh-only arguments. Require state kind to equal invocation kind and remove the stale fresh-offset case.**

2. The redesign removes the original catastrophic targets: fake `USERPROFILE`, disposable backing storage, scratch `.git`, and `finally` cleanup are the right isolation strategy ([plan:474](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:474), [plan:479](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:479)).

It is not yet fail-closed:

- `X:` is hard-coded without requiring that the letter be unused or that `subst` succeeded before planting the sentinel and invoking removal ([plan:476](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:476)). If `X:` already names a real or network drive and setup fails unnoticed, the test can fall through onto that real drive—the defect this redesign is meant to eliminate.
- The teardown command is incomplete: deletion requires the selected drive argument, e.g. `subst X: /d`, not merely `subst /d` ([plan:476](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:476)).
- Production refuses `$env:USERPROFILE` “or above it” ([plan:450](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:450)), but the redesigned test exercises only equality with the temporary profile ([plan:475](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:475)). The ancestor branch remains unexercised.

**FIX — Select and verify an unused drive letter, require successful mapping to the intended temporary directory before planting anything, unmap with `subst <drive>: /d` in `finally`, and add a disposable ancestor-of-fake-USERPROFILE case.**

3. The earlier narrowed claims are now correct in their principal and downstream locations:

- Resume conclusions remain limited to four tested flags ([plan:47](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:47), [plan:807](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:807), [plan:992](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:992)).
- The self-review now says three of four measured flags rather than every flag ([plan:1015](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:1015)).
- Fresh and resume boundary names are consistently `metadata` and `turn.prompt` in the measurement, validator, and contract instruction ([plan:49](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:49), [plan:761](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:761), [plan:814](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:814)).

One evidence overclaim remains. Task 9 says kimi-code “discovers agents” and skills from the reviewed tree ([plan:895](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:895)). The original probe explicitly left project agent/skill pickup unverified ([probe-record.md:244](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-07-31-kimi-code-swap/probe-record.md:244)), while the plan’s settled evidence says skills loaded nothing and that the canary files were merely readable as ordinary workspace content ([plan:828](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:828), [plan:829](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:829)). The preflight sweep is still justified, but by readable instruction-file exposure, not measured discovery.

There is also stale operational wording telling the contract to run the validator “with the captured offsets” for every kind, despite fresh calls having no offsets ([plan:814](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:814), [plan:816](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:816)).

**FIX — Rewrite Task 9’s test comment around measured ordinary-file readability, and replace “with the captured offsets” with the kind-specific prior state.**

4. The remaining blocker is structural. The validator is responsible for discovering the fresh session but has neither a sessions-root input nor a usable fresh `SessionDir`; its published signature instead requires the very directory it is meant to establish ([plan:656](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:656), [plan:752](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:752)). Additionally, without defining the inventory as the nested session leaves, the measured `wd_<workspace>/<session-id>` topology can make a clean first call look like two concurrent sessions ([probe-record.md:166](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-07-31-kimi-code-swap/probe-record.md:166)).

That is not a request for a longer test list. It is an undefined and internally contradictory interface at the point where fresh identity is established. Once Fresh/Resume parameter sets, the sessions root, and the inventory-member definition are fixed, the remaining destructive-test and wording defects are addressable implementation details.

**FIX — Do not freeze until the fresh validator can locate and identify its session using only inputs that actually exist at invocation time.**

UNVERIFIED

- The exact parsing and uniqueness of the `To resume this session:` stdout marker was not established by the files read; the retained probe confirms that the CLI prints a resume alias but does not document this extraction contract ([probe-record.md:126](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-07-31-kimi-code-swap/probe-record.md:126)).
- The cp1252 and per-session rotation probes remain future Task 4 work ([plan:491](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:491), [plan:502](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:502)).
- ACL enforcement, transactional cleanup, and removal-guard behavior remain future live checks ([plan:464](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-31-kimi-code-swap.md:464)).