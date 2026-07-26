# 0.13.0 design — Kimi backup reviewer lane (codification)

Date: 2026-07-25. Status: APPROVED (user), dual advisory findings folded
(section 14). Builds on the lane's live field run: it conducted the real
0.12.0 plan debate (2 rounds, session resume, read-only agent-file
containment held, throwaway clone stayed clean) before it had a design
cycle of its own.

## 1. Purpose and scope

Codify the Kimi K3 backup reviewer lane into the plugin: when the
primary reviewer transport (codex) is down, the debate substitutes a
SECOND cross-vendor reviewer instead of falling to the single-vendor
DEGRADED skeptic. Backup reviewer lane ONLY this cycle — multi-reviewer
panels, hub-and-spoke mediation machinery, and the seat reshuffle are
0.14.0 scope (user ruling).

## 2. User decisions (not under debate)

- Backup model: `kimi-code/k3-256k`, thinking on, effort high (pinned
  via `~/.kimi/config.toml` `.overrides`, applied 2026-07-25).
- Triggers: `quota-exhausted` and transport-broken classes AUTO-QUALIFY
  the backup option at the consent gate; manual invocation anytime; the
  governing consent rule is never bypassed — the user picks the lane.
- Approach B: dedicated `references/backup-lane.md` owns lane mechanics.
- Hub-and-spoke: reviewers never talk directly; the session mediates and
  verifies before relaying (0.14.0 builds the panel form; the invariant
  binds now).
- Standing process rulings apply: Sol plan check-off before
  implementation, mode-diff debate gates merge, attestation on final tip.

## 3. Lane semantics and recording

Inside a debate the backup lane is a full peer: same debate protocol
(strike rule, verdict grammar, 4-round cap, session adjudication), same
XML-tag brief conventions, same anti-sycophancy rules.

Recording (codifies the 0.12.0 precedent, resolving the format gap both
advisors examined): a backup-lane debate is **Verification status:
FULL** — cross-vendor independence is preserved (Moonshot is not
Anthropic). `frozen-plan-format.md` gains a pinned **lane-substitution
combination**: `Verification status: FULL` MAY carry `Degradation:
<primary-lane failure class>` + `Authorized by: user at round N` when a
backup cross-vendor lane substituted for the primary; the Participants
line names the actual backup participant with its transport and session
id (a kimi-shaped example joins the codex-shaped template). The
Degraded-mode note stays bound to DEGRADED status; lane substitution is
NOT degradation. The single-vendor skeptic remains the only true
DEGRADED mode. This retroactively legitimizes the 0.12.0 record's
field-state combination.

Route-note grammar stays normalized and lane-agnostic (advisory
finding): the attestation verifier requires the exact string `effective
route confirmed` (tools/verify-attestation.ps1) and the behavioral
contract expects that wording. "Confirmed" for a given lane means every
round's route evidence matched THAT lane's canonical declarations per
its reference; backup-lane.md defines what confirmation means for kimi
(client-side, attributed — section 6). The evidence class is recorded in
the debate record prose, never by mutating the attestation grammar.

## 4. Transport contract and single-source discipline

Probed facts (2026-07-25, kimi-cli 1.49.0; re-probed where section 12
requires): headless dispatch `kimi --quiet --thinking -m <backup-id>
--agent-file <yaml> -w <clone> -p <brief pointer>`; resume
`kimi -r <uuid>` (session id printed every run); route line `Using LLM
model: provider='managed:kimi-code' model='k3-256k'` appended to
`~/.kimi/logs/kimi.log`; bad model fails loud ("LLM not set"); print
mode auto-approves ALL tools and `--plan` does not block writes (the
reason containment is structural); effort has NO CLI flag — pinned via
config `.overrides`, evidence class = config validation (the log carries
no effort field); inline `--config` replaces the whole config and is
unusable for dispatch-time pinning.

Single-source (both advisors, convergent): the backup model id literal
gets EXACTLY ONE authority — a new, distinctly-labeled declaration block
in `model-prompting-notes.md` (the file already declared THE reviewer
transport single source). Everything else uses placeholders:
backup-lane.md's pinned command carries `<canonical-backup-model-id>`
resolved by reading the notes file at dispatch (mirroring SKILL.md's
`<canonical-model-id>` pattern), the doctor row and drift script carry
no literal (agy precedent), and the consistency sweep's allowed homes
are the notes declaration, the eval test file that pins it, and nothing
else.

Label no-collision constraint (both advisors): the primary parse
surfaces are `re.search(r"Canonical model id: \x60([^\x60]+)\x60")` in
run_behavioral_evals.py (case-sensitive) and a case-INSENSITIVE
PowerShell `-match` in check-drift.ps1. The backup labels (`Canonical
backup reviewer model id:` / `Canonical backup thinking flag:`) must
never contain the substring `Canonical model id:` under case-insensitive
comparison, and the primary declarations must PRECEDE the backup block
in the file. A regression test pins: both runtime surfaces still resolve
the PRIMARY id from the amended file; the backup label matches neither
primary regex case-insensitively; ordering holds.

## 5. Containment

Committed artifacts (inventory, complete): 
- `references/kimi-reviewer-agent.yaml` — tools allowlist exactly
  SetTodoList, ReadFile, ReadMediaFile, Glob, Grep (no write, shell, or
  web tool entries).
- `references/kimi-reviewer-system.md` — SELF-AUTHORED system prompt
  (no copy of kimi-cli's internal file; no drift coupling). Plan-time
  probe 12.1 confirms the self-authored variant behaves; failure branch:
  fall back to the probed copy-at-invocation form, and if that also
  fails the lane is BROKEN and this design returns for revision.

Write-probe (falsifiable oracle, advisory finding): before round 1 of
every backup-lane debate, in a FRESH disposable session with the exact
debate configuration (same agent-file, model, flags, workspace), ask the
contained agent to create a named marker file. PASS requires ALL of:
explicit refusal in the reply, marker absent on disk, clone status delta
empty. Anything else = lane BROKEN (integrity class, section 7) — never
dispatch a review over it.

Clone isolation: reviews run in a throwaway clone of the repo (never the
real tree), brief delivered as the untracked `KIMI-REVIEW-BRIEF.md`.
Post-round check (fixing the internal contradiction the advisory
caught): `git status --porcelain` must list EXACTLY the brief file and
nothing else; any other delta quarantines that round's reply (integrity
class). The brief is retained as evidence per the raw-rounds convention.

## 6. Route evidence and per-round attribution

`~/.kimi/logs/kimi.log` is a shared, user-global append stream — a bare
"the line appears in the log" check cannot attribute the line to a
specific dispatch (both advisors, convergent). The lane's rule:

- Before EVERY dispatch (fresh or resumed): capture the log's current
  length (byte offset).
- After the call: exactly ONE new `Using LLM model:` line carrying the
  canonical backup id must appear past the captured offset. Zero
  matching new lines, more than one, or a wrong id = route-attribution
  failure — the reply is DISCARDED unread (same rule as codex
  route-mismatch), fail closed.
- This check runs on EVERY round, resumes included.

Resume: the codified resume form re-pins the load-bearing flags
defensively (`kimi -r <uuid> --agent-file <yaml> ...` — exact form
settled by probe 12.2, which tests whether resume inherits or drops
`--agent-file`, `-m`, and `--thinking`; the codex lane's costliest probe
lesson — sandbox non-continuity — applied to this transport). If probe
12.2 shows resume cannot be made containment-safe, resumed rounds are
replaced by fresh-per-round dispatches with the full brief (the
continuity cost recorded in the debate record), and backup-lane.md says
so explicitly.

## 7. Failure classes and the consent gate

fallbacks.md remains the failure-class namespace (single home —
advisory finding); backup-lane.md points at it and defines nothing
class-shaped of its own. New content in fallbacks.md:

- The consent-gate banner gains the backup-lane option: `[run backup
  lane (cross-vendor preserved)]` — offered automatically when the
  failing class is `quota-exhausted` or any transport-broken class;
  available on request otherwise. When offered, the banner's `What it
  would NOT verify:` line names the backup lane's known evidence gap:
  reviewer reasoning effort (config-validation only — no per-call
  evidence).
- `transport-broken` mapping (advisory finding — operational, not
  vibes): the classes that auto-qualify the backup option are
  codex-missing, model-rejected, auth-expired, and a route-mismatch or
  missing-rollout that survives its gate. `quota-exhausted` qualifies by
  the user's standing ruling.
- Backup-lane failure table (detection → retry → disposition):
  kimi-missing (`kimi --version` fails; no retry; gate), kimi-bad-model
  ("LLM not set", loud; no retry; gate), route-attribution failure
  (section 6; no retry — nothing transient; reply discarded; gate),
  resume failure (one retry, then gate with the fresh-per-round option),
  integrity failure (write-probe fail or clone delta beyond the brief;
  no retry; reply quarantined; gate), catch-all (one same-parameters
  retry, then gate — mirrors the primary catch-all). Both lanes down =
  the honest choices: wait for reset, single-vendor DEGRADED skeptic, or
  abort — never a silent third vendor.

## 8. SKILL.md and README wiring

SKILL.md (advisory finding — the lane must be ROUTED, not just
documented): the Overview names the backup lane's existence; a
lane-selection paragraph states the primary is default, the backup
enters only through the fallbacks.md consent gate (auto-qualified or
manual), and backup-lane.md is REQUIRED READING before a backup round;
mode plan/diff dispatch steps gain a one-line pointer ("backup lane:
transport per references/backup-lane.md, same protocol"); the finish
line's route-note grammar is explicitly lane-agnostic (section 3).
README: the consent-gate flowchart gains the backup-lane option beside
the three existing exits, plus a one-sentence lane description in the
What's-in-the-box list.

## 9. Doctor and drift

Doctor: new check row for the backup transport — `kimi --version`, the
notes-file backup declaration parse, and presence of the two committed
containment artifacts. Non-billable only; exact probe shape from probed
commands (no speculative flags).

Drift (advisory finding — a version snapshot alone is toothless for a
reviewer transport): kimi version snapshot field in carry-forward style
(agy precedent) PLUS a non-billable flag-surface probe — `kimi --help`
grepped for the six load-bearing flags (`--quiet`, `--thinking`, `-m`,
`--agent-file`, `-w`, `-p`) and `-r` — run alongside the codex flag
probe. A containment-vocabulary probe (the yaml's tool module paths
still importable in the installed kimi-cli) is settled by plan-time
probe 12.3; if no clean non-billable form exists, the vocabulary check
lands in the doctor row instead, and drift covers flags only.

## 10. Testing

Offline pins (CI, no CLI calls): agent.yaml allowlist exact-match plus
absence of any write/shell/web tool entry; backup-lane.md exact-sentence
pins (route-attribution rule, exactly-the-brief clone rule, write-probe
oracle, resume form); fallbacks banner option + transport-broken mapping
pins; frozen-plan-format lane-substitution pin; the notes parser
regression test (section 4); kimi-literal single-source sweep; the new
reference files join the structural pins (REQUIRED_REFERENCE_FILES,
no-backslash rule — pinned paths are forward-slash).

Behavioral (local, opt-in): one new evals.json case declaring surface
`fallbacks.md` + `backup-lane.md` — consented backup selection routes to
the kimi transport contract (graded like existing cases). Drift-script
changes carry the standing requirement: the offline state-machine suite
runs with kimi-probe scenarios added to its stub CLIs.

## 11. Live verification (attended task; 0.12.0's lesson applied)

Through the CODIFIED machinery at head — the installed skill text, the
committed yaml + system prompt, the placeholder-resolved command — not
from memory: fresh throwaway clone; write-probe with the section-5
oracle; one real review round on a scratch brief with offset-attributed
route evidence; one resumed (or fresh-per-round, per probe 12.2)
continuation exchange; post-round exactly-the-brief check. Evidence in
the SDD ledger; the diff-debate brief cites it.

## 12. Plan-time probes (each with a failure branch)

1. Self-authored system prompt behaves under --agent-file (else:
   copy-at-invocation; else lane BROKEN, design revisits).
2. Resume flag inheritance: does `kimi -r` retain --agent-file / -m /
   --thinking? Probe with a disposable session + write-probe on the
   RESUMED round (else: fresh-per-round dispatches, recorded).
3. Containment-vocabulary probe feasibility (else: doctor-only check).
4. Notes-file parser regression harness: amended notes text against both
   runtime parsers before the text ships (grader + drift).
5. "LLM not set" also covers the missing/broken managed-config case
   (auth-shaped failures) — confirm the loud-fail signature class.

## 13. Trimmed and out of scope

- `kimi export`: NOT part of any workflow step (advisory scope
  challenge). backup-lane.md keeps one caution sentence — export writes
  a session zip into CWD, so never run it inside a repo — because the
  operator-error class is real; nothing depends on export.
- Panels, Opus driver switch, fable-reviewer, escalation implementer:
  0.14.0.
- No new implementer machinery: this cycle touches the REVIEWER side
  only.

## 14. Review provenance

Dual cross-vendor advisory pass on the design draft (2026-07-25,
pre-spec; hub-and-spoke, blind — neither advisor saw the other's
review):
- Kimi K3 (`kimi-code/k3-256k`, kimi-cli 1.49.0, contained read-only
  agent against a throwaway clone at main/498d72f, session
  849d24f7-e171-43b6-bda4-5027488ddd2e, route line verified): FIX, 10
  findings — incl. the resume flag-inheritance probe, the
  Degradation-on-FULL format gap, label no-collision precision, and a
  firsthand corroboration of the containment allowlist from inside the
  contained session.
- GPT-5.6 Sol (codex exec read-only, session
  019f9c5f-a234-72c0-a1fe-cd29e6d9065d, effective route confirmed):
  FIX, 11 findings — incl. SKILL.md routing, the attestation
  route-note grammar constraint, the clone-clean/brief contradiction,
  the write-probe oracle, and the export scope trim.
- Convergent findings (single-source, log attribution, SKILL wiring,
  failure-class home, drift depth) adopted in their strongest form; the
  one direct disagreement (format gap: flag vs precedent) dissolved —
  both true, resolved by pinning the combination (section 3). All
  session-verified against the repo before folding; raw replies retained
  under the plans rounds dir at plan freeze.
- NOT part of the cross-vendor gate: the Sol plan check-off and the
  mode-diff debate remain ahead per standing rulings.

## 15. Risks and residuals

- Server-side model substitution is undetectable for kimi exactly as for
  codex and agy — the route evidence is client-side; language discipline
  applies (named residual, accepted).
- Reviewer effort has NO per-call evidence (config-validation only) —
  named in the consent banner (section 7).
- kimi-cli is pip-installed and updates under its own schedule; drift
  coverage (section 9) is the watch, and the plan re-probes before
  shipping (section 12).
- The backup lane shares the user's Kimi account quota; no headroom
  probe exists this cycle (0.12.0-style quota probing for kimi is
  future work if the lane sees regular use).
