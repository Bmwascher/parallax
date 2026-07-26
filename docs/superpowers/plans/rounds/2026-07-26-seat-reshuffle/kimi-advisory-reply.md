# Advisory review — 0.14.0 seat-reshuffle design spec

Reviewed `docs/superpowers/specs/2026-07-26-seat-reshuffle-design.md` against the pinned surfaces named in the brief. Findings ranked; every claim cited.

---

## BLOCKING

**B1. The Fable panel lane's transport contract is unspecified where the other two lanes are exact — the plan author must invent the core of panels.md.**
Spec §6 (line 102) pins the Fable lane as "a fresh same-harness fable subagent kept across rounds via resume" — one clause, no command shape, no resume semantics, no per-round evidence rule. Compare the existing lanes: Sol's dispatch/resume commands are pinned verbatim with flags-before-subcommand and per-round header checks (`skills/multi-model-verify/SKILL.md:92-131`); Kimi's dispatch/resume are pinned to the complete command string with the offset-evidence rule (`skills/multi-model-verify/references/backup-lane.md:17-40`, test-locked at `evals/multi-model-verify/test_backup_lane.py:75-96`). For the Fable lane the spec defines only what the evidence is *not* ("no external transport; no route header exists", spec line 104) — never what the driver *checks per round*, nor what a failed check is called. §7 (line 118) then routes a Fable-lane death to "a harness error," which is **not a class in the single failure-class namespace** — fallbacks.md defines every class and the catch-all (`references/fallbacks.md:45-53,139-159`), and backup-lane.md:71-73 states that file defines none of its own. An unnamed class in the namespace file is exactly the drift the namespace exists to prevent. Separately, the repo's own probe gate — "No runtime-behavior claim becomes rule text, skill text, or a test assertion until a dated live probe settles it" (`commands/intake.md:53-56`) — has been applied to every other lane's resume semantics (probed codex resume `SKILL.md:123-131`; probed Kimi resume `backup-lane.md:21`); the spec contains no probe plan for subagent resume (does a resumed subagent keep its `model: fable` pin and tool grant? — the Kimi probe showed resume silently inherits config defaults). panels.md cannot be written to the repo's own standard from this spec. See also UNVERIFIED #2.

## IMPORTANT

**I1. fable-reviewer's read-only containment is prose-over-live-Bash with no evidence check — the control class the 0.13.0 cycle explicitly rejected.**
Spec §3 (lines 37-38) grants `Bash` and contains mutation by "contract text forbids mutation"; §11 (line 219) test-pins only that the read-only *sentence* is present. The 0.13.0 probe record found prose refusal under live write tools was conversation priming, not containment (`references/backup-lane.md:21`), which is why the Kimi lane's five-tool allowlist is "the load-bearing control" with a per-round `Loaded tools:` verification (`backup-lane.md:44-51`), a pre-round-1 write-probe (`backup-lane.md:52-56`), and a post-round clone-delta check (`backup-lane.md:65`). The Flash lane likewise pairs its never-write prose with transcript/tree corroboration (`agents/flash-implementer.md:87-92`). The fable-reviewer gets no isolation statement (real tree? it reads "the frozen plan, the SDD ledger's deferred minors, and a controller-built diff package" — spec line 40-41, presumably the real tree), no mutation-tripwire, and no per-round evidence rule. Either drop Bash (git inspection via the driver's package) or spec an evidence check; pinning prose alone regresses a settled lesson.

**I2. `panel-lane-loss` composition with the existing consent gate and the record fields is unspecified.**
Spec §7 (lines 116-121) says a lost lane "routes through its own existing failure classes first… else it stops at the consent gate," but does not say: (a) when Sol dies mid-panel, the codex classes' consent gate already *offers the backup lane* (`references/fallbacks.md:130-134`) — does a chosen Kimi substitute rejoin the panel, or does the panel collapse to a bilateral substituted debate? (b) what `Verification status` / `Degradation` / `Authorized by` a lane-loss-continued panel records — the structured fields are an enumerated grammar (`references/frozen-plan-format.md:48-50`) with a lane-substitution precedent for FULL-plus-class (`frozen-plan-format.md:79-86`), and the attestation gate mechanically requires `FULL` plus the exact route note `effective route confirmed` (`tools/verify-attestation.ps1:47-49`). The spec's §8 recording paragraph (lines 183-186) covers Participants/Rounds/convergent marking but not the status fields, so the merge-gate consequence of a lane loss is left to the plan author.

**I3. Kimi-in-panel contradicts backup-lane.md's substitution-only framing, and the spec never amends that file.**
backup-lane.md defines the lane as substituting "when the primary reviewer transport is down" and entering "ONLY through the fallbacks.md consent gate" (`references/backup-lane.md:3-6`). Spec §6 uses Kimi as a *parallel* panel lane while Sol is healthy, and §6/§8/§9 name no backup-lane.md edit. The consent-gate text does admit "manual on user request" (`backup-lane.md:5-6`; `fallbacks.md:133-134`), so a user-invoked panel is arguably already covered — but the spec doesn't say so, doesn't state whether panel invocation of Kimi requires the banner, and leaves panels.md to reconcile against a file whose opening paragraph describes a different role. Also unstated: whether the pre-round-1 write-probe (`backup-lane.md:52-54`) runs for a Kimi panel lane (presumably yes under "EXISTING bilateral protocol… unchanged," spec line 99-101 — say it).

**I4. §5's escalation report contract contradicts the file it claims to mirror.**
Spec line 72-73: "Report contract otherwise mirrors implementer.md (STATUS / FILES CHANGED / VERIFICATION / DECISIONS / CONCERNS)." `agents/implementer.md:30-36` defines STATUS / FILES CHANGED / VERIFICATION / **DEVIATIONS** ("must be 'none'") — no DECISIONS, no CONCERNS. The parenthetical silently drops DEVIATIONS and adds CONCERNS while claiming to mirror. For a judgment-permitted lane the fate of the DEVIATIONS rule is a real design question (does DECISIONS *replace* it?), and the flash lane's report (`agents/flash-implementer.md:109-120`) adds ROUTE — unspecified whether the escalation lane needs an equivalent. The plan author must guess which sections the §11 "DECISIONS required-section text present" test (line 221-222) coexists with.

## MINOR

**M1.** §4's pinned sentence (line 59) requires "dispositioned findings" in the round-1 brief, but no actor or grammar for the disposition step is defined; "dispositioned" is the application-checkpoint state machine's vocabulary (`SKILL.md:152-157`), where dispositioning is a formal recorded step. Who dispositions the Fable findings, against what evidence, before the cross-vendor lanes see them?

**M2.** The finish-line/attestation grammar is bilateral: the emitter invocation pins singular `-Participants "<session-model> (session) / <reviewer-model> (reviewer)"` and `-Rounds <n>` (`SKILL.md:178`), and §8 records per-lane rounds only in frozen-plan-format. Nothing specifies the attestation/finish-line form for panels — including whether the *required* fable review is named in the mechanical record at all (today the record would bind only the debate; the required step's execution lives in prose).

**M3.** §9 (line 195) names only CLAUDE.md for the public-repo accuracy fix — `CLAUDE.md:39` says "(Bmwascher/parallax, private)" — but `README.md:188` carries the same false claim ("git auth for this private repo"). §10's completeness pass would presumably catch it; the fix as scoped names one of two instances.

**M4.** §13 (line 254-256) budgets the panel smoke "against the Kimi 5-hour window and the codex weekly window (doctor 4b first)" — doctor 4b reads codex quota only (`commands/doctor.md:86-102`); doctor's kimi check covers version/artifacts, no quota surface (`commands/doctor.md:146-159`). The Kimi half of the budget check has no probe.

**M5.** §2's seat table (line 29) labels the transcription implementer "Claude Haiku tier (implementer.md)" — the file's frontmatter is `model: sonnet` with haiku as a per-dispatch override (`agents/implementer.md:4,40-41`). Pre-existing shorthand (`README.md:29`), but the parenthetical points at a file that contradicts the label.

## Sound (checked, no objection)

- §8 heading rename: `## Fable 5 (the session side)` appears only at `references/model-prompting-notes.md:3` and in the spec — no parser or test reads it; parsers match the `Canonical model id:` labels (`evals/multi-model-verify/test_multi_model_verify.py:117,236`; `test_backup_lane.py:46-56`), and the primary-before-backup ordering rule (`model-prompting-notes.md:214-216`) is untouched. PASS.
- §10's amend-pins-with-tests rule (lines 209-212) correctly anticipates the pinned README mermaid edge and table-row prefix (`test_backup_lane.py:139-148`). PASS.
- §11's panel-pointer `count == 2` pin mirrors the backup-lane pointer pin (`test_backup_lane.py:139-141`); panels.md joining REQUIRED_REFERENCE_FILES (`test_multi_model_verify.py:27-34`) also sweeps it into the no-backslash rule (same file, lines 88-94) — compatible. PASS.
- §12's manual eval case satisfies the schema pins (`test_multi_model_verify.py:496-519`) and follows the manual precedent (`evals/multi-model-verify/evals.json:95-99`). PASS.
- §5 route 2's consent-gate reroute matches the Flash lane's own contract (`agents/flash-implementer.md:105-107`). PASS.
- Hook impact: the fable-reviewer dispatch won't match the fingerprint (`hooks/superpowers-review-companion.ps1:27-29`) and the injected reminder stays accurate — no hook change needed. PASS.
- §7's "a lost lane's incomplete round is never adjudicated" matches the stale-reply discard discipline (`references/fallbacks.md:45-50`). PASS.

## UNVERIFIED

1. The "154+1skip baseline" (spec line 235) — I cannot run the suite.
2. Same-harness subagent "resume" mechanics (spec line 102) — no probed evidence exists in this repo; all resume knowledge is codex/Kimi (`SKILL.md:116-131`; `backup-lane.md:19-21`). Feasibility rests on an unprobed harness capability.
3. All three external guide fetches cited in §8 (Opus 5, Fable 5, Kimi best-practices; spec lines 130-179) — no web access; content claims unverifiable from the workspace.
4. "The 0.12.0 precedent" for the single-driver debate record (spec line 263) — not checked against the 0.12.0 record.

## Verdict

**SOUND-WITH-FIXES.** The architecture is coherent with the repo's invariants and most pinned-surface interactions are anticipated; but the Fable panel lane's transport/evidence/failure contract (B1) must be specified — and probed, per the repo's own probe gate — before a plan can be written without guesswork, and I1-I4 are cheap to fix now.

To resume this session: kimi -r 493c77f6-7a26-4139-a369-34a2126c0c04
