# Debate protocol

Both advisors are equal weight. Neither model's claim outranks the other's;
only evidence does.

## Evidence grounding (the strike rule)

- **Every externally checkable claim must carry a citation to a source the
  other side can read**: a file:line in the repo or reference material the
  citing side actually read (the session: read this session; the reviewer:
  read inside its sandboxed run — its quoted excerpt counts as reading),
  authoritative local docs, or a fetched URL.
- Source-specific examples: reference-port claims cite
  `References/<name>/<file>:<line>`; WoW 12.0 API claims cite
  `.wow-api-reference/` or a dated in-game probe result; library or platform
  claims cite the vendored source or official docs.
- **Anchor every file the first time you cite it** — full repo-relative path
  with line, `References/DemoWidget/DemoWidget.toc:1`, not `DemoWidget.toc:1`.
  This holds for EVERY file, including one-line manifests and secondary
  files, not just the main source. Once a file is anchored, shorthand
  (`Core.lua:19`) is fine for later citations of that same file. A bare
  filename does not locate anything for the other side: the project has its
  own `DemoAddon.toc` and the reference has `DemoWidget.toc`, and an
  unanchored `.toc:1` could be either.
- A claim with no citation is **struck, not debated**. Note it as struck and
  move on — arguing against an ungrounded claim launders it into the record.
- Reports are claims requiring evidence. "The reference handles this" without
  the file:line is an assertion, not a finding.

## Round structure

Each exchange (one session position or rebuttal + one reviewer reply) is a round.

1. From round 2 on, state position changes since last round: which of the
   other side's points are **accepted** (absorbed into the plan), which are
   **refuted** (with the evidence that refutes them), which are **struck**
   (no citation).
2. Raise new risks only with evidence attached.
3. End with a verdict on the current plan/diff:
   - **PASS** — no remaining substantive objections.
   - **FIX** — named change required, with the specific fix and its evidence.
   - **ESCALATE** — a disagreement evidence cannot settle (taste, missing
     in-game data, ambiguous reference intent).

## Convergence and the round cap

- Converged: both sides verdict PASS in the same round.
- **Converged with amendments**: the final round's only outstanding verdicts
  are FIXes whose fixes the other side accepts on the record. Record each
  accepted fix in the debate record and treat the plan as converged — an
  accepted FIX is agreement, not a dispute for the user to settle. (This
  matters whenever a FIX lands in the last round before the cap.)
- Round cap: **4 exchanges** by default (caller may raise or lower it).
  Hitting the cap is not failure — it is the signal to stop spending tokens
  on an argument evidence hasn't settled.
- At the cap or on ESCALATE, for points that remain genuinely contested:
  stop, present BOTH positions to the user with their evidence, and let the
  user decide. Never silently pick a side.
- Questions only runtime testing can answer always escalate — neither model
  can run the live application (in WoW projects, /reload + BugSack is always
  the user's step).

## Final adjudication (the session's last step)

The chain never ends on the external reviewer's verdict. After the
reviewer's final round — including a re-review of fixes — the SESSION
performs one closing step before anything merges or freezes:

1. Verify each finding from that final round against the live repo (read
   the cited lines; run the gates if implicated) — a final-round finding is
   itself an unverified claim until checked.
2. Accept with evidence, refute with evidence, or ESCALATE to the user.
   Nothing is adopted or dismissed on authority.
3. Emit the terminal verdict and the finish line (mode diff: then record
   the verdict mechanically via the attestation emitter — see SKILL.md's
   finish-line section). A reviewer PASS/FIX is input to this step, never
   the decision itself.

Equal weight governs claims during the debate; adjudication is procedural,
not a rank: the session is the accountable party with live-repo access, so
the session always has the final say — and a genuine deadlock still goes to
the user, never to whoever spoke last (user directive, 2026-07-12).

## Anti-sycophancy, anti-theater

Debates fail two ways: rubber-stamping and manufactured conflict. Both are
defects.

- **A sound plan gets one line.** "Plan is sound; the one thing to watch is
  X." Converging in round 1 is the system working.
- **Do not manufacture objections** to justify the round. If you would not
  push back in a real review, do not push back here.
- Do not restate the other side's point in different words as a "new" risk.
- Do not concede a point you can refute just to converge faster —
  unresolved disagreement has an honest exit (ESCALATE).

## Why the structure carries the trust

The current reviewer lane has a documented (METR, vendor system card — see
model-prompting-notes.md) tendency to fabricate
results under evaluation pressure. The mitigation is this protocol — every
claim must survive citation and refutation by an independent model — not
down-weighting the reviewer's verdicts. The same rules bind the session
model equally: fabricated
detail is a known failure mode of every frontier model, and this project's
history (see memory: no-fabrication feedback) treats invented API behavior as
the cardinal sin.
