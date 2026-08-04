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
  accepted fix in the debate record — an accepted FIX is agreement, not a
  dispute for the user to settle. (This matters whenever a FIX lands in the
  last round before the cap.) THIS IS AGREEMENT, NOT TERMINATION. The
  amendments still have to be APPLIED, and the debate still ends the way
  the termination rule below says it ends: on an adjudicated dry round. A
  round that produces accepted fixes is a round that produced new
  substantive findings, so it is not that round.
- Round cap: **4 CONSECUTIVE CONTESTED exchanges** by default (caller may
  raise or lower it). A round is CONTESTED while any contested point is
  OUTSTANDING, whether it was raised in that round or an earlier one — an
  argument evidence has not settled is still the argument this counter
  exists to count, and a round that merely accepts other findings does not
  settle it. A contested round increments the counter; a round that leaves
  NO contested point outstanding RESETS it to zero.
  Hitting the cap is not failure — it is the signal to stop spending tokens
  on an argument evidence hasn't settled, and that argument is the only
  thing this counter measures.
- **A fix-verify loop is not an argument, and the cap above does not bound
  it.** A round that finds something new, has it verified, accepts it and
  moves on is progress. Two measured runs overran a flat cap of 4: a field
  report ran 8 rounds with zero refutations, zero escalations and zero
  repeat findings, where stopping at 4 would have shipped its defects 5 and
  6; and this repo's own 0.21.1 debate ran 7 rounds in which rounds 5 and 6
  each returned ESCALATE on real defects and only round 7 was terminal. Its
  twelve round records are retained under
  `docs/superpowers/plans/rounds/2026-08-04-transport-and-mirror/`; they
  record verdicts PER CLAIM rather than a contested-point tally, so "no
  contested point" there is a reconstruction from the claims and not a
  reading off the records.
- **A separate TOTAL FIX-VERIFY BUDGET bounds that loop**, caller-set and
  declared before round 1. ONE UNIT IS ONE DISPATCHED EXCHANGE — every
  round sent to a reviewer, whatever it returns, including a round that
  returns nothing usable. Counting only productive rounds would let the
  unproductive ones run free, which is the shape being bounded. Exhausting
  it PAUSES the debate for the user's authorization to continue — it NEVER
  certifies and never converts into a verdict. The session both adjudicates whether a finding is accepted AND
  decides when to stop, which is one actor holding both roles; a budget the
  USER controls is the bound a session cannot grant itself.
- Termination: the debate ends only on an **adjudicated dry round** — one
  that produced no new substantive finding AND left no outstanding
  contested point. "Ends when a round produces no new accepted finding" is
  NOT the rule: that also ends a round whose only new finding is CONTESTED,
  which is the exact case the cap exists to escalate.
- At the cap, at budget exhaustion, or on ESCALATE, for points that remain
  genuinely contested: stop, present BOTH positions to the user with their
  evidence, and let the user decide. Never silently pick a side.
- Questions only runtime testing can answer always escalate — neither model
  can run the live application (in WoW projects, /reload + BugSack is always
  the user's step).

## Scope: pre-existing defects a review walks past

A diff review reads adjacent code and finds defects that PREDATE the range.
Both answers are defensible — surgical-changes discipline says leave them,
and certifying a module you know is broken says fix them — so the rule is
written down here rather than improvised per debate, because an attestation
that means something different run to run means nothing.

**The rule.** FIX a pre-existing defect when it is of the SAME CLASS as
what the branch already fixes AND it lives on the verification surface this
debate will exercise. RECORD anything else as a named follow-up. Do NOT
certify a module whose follow-up has not landed.

Both halves are judgement calls unless they are defined, and two reviewers
who define them differently produce two different attestations. So:

- **SAME CLASS** means a violation of the SAME NAMED invariant, contract
  clause, or frozen postcondition — cited by name. It does not mean similar
  symptoms, the same file, or the same subsystem. "Both are null-handling
  bugs" is not a class; "both violate the postcondition that an unmade
  measurement never reads as a clean one" is.
- **VERIFICATION SURFACE** means the exact files, symbols, runtime paths
  and gates ENUMERATED BEFORE the finding is raised. Enumerated after, it
  is a surface drawn around the answer someone already wanted.
- **The certification unit** is the module or contract region the
  attestation names, and it is named before the debate ends, not inferred
  from what was touched.

**An exercised surface with an outstanding follow-up cannot be attested.**
The debate ends FIX or ESCALATE, or it attests an EXPLICITLY NARROWED claim
that names what is excluded. Silence about a known defect inside a
certified unit is the one outcome this rule exists to prevent.

## Final adjudication (the session's last step)

The chain never ends on the external reviewer's verdict. After the
reviewer's final round — including a re-review of fixes — the SESSION
performs one closing step before anything merges or freezes:

1. Verify each finding from that final round against the live repo (read
   the cited lines; run the gates if implicated) — a final-round finding is
   itself an unverified claim until checked.
2. Accept with evidence, refute with evidence, or ESCALATE to the user.
   Nothing is adopted or dismissed on authority.
3. Emit the terminal verdict. A reviewer PASS/FIX is input to this step,
   never the decision itself.
4. If that verdict requires changes this session will apply itself, the
   chain is NOT over: the application checkpoint
   (references/application-checkpoint.md) precedes the FIRST file edit —
   the checkpoint, not the verdict, is what authorizes touching files.
   After applying, execute the checkpoint's verification plan and
   re-review the fixed range; only the post-re-review terminal PASS
   closes the chain.
5. Close with the finish line (mode diff: first record the closing
   verdict mechanically via the attestation emitter — see SKILL.md's
   finish-line section; when a checkpoint governed the fixes, bind it
   with `-CheckpointFile`). The attestation always records the FINAL
   adjudicated range — never a verdict whose fixes are still unapplied.

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
