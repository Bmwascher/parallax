# Feasibility record: moving everything to PowerShell 7 (backlog item 48)

Date started: 2026-08-22 (local, CDT).
Repo: branch `item51-inline-brief-transport`, cut from `main` at `a3134dcd76d9253057bf24935f3d7a7eef8eb0e4`.
Hosts under test: Windows PowerShell 5.1.26100.9168 and PowerShell 7.6.5.
Driver: Opus 5, subagent-driven per task.
Header facts captured, not asserted from memory, by running
`git rev-parse --abbrev-ref HEAD`, `git merge-base main HEAD`, and
`$PSVersionTable.PSVersion.ToString()` under each of
`C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe` and
`C:\Program Files\PowerShell\7\pwsh.exe` (task-1-report.md carries the
captured output).

**This is an investigation. Nothing in this cycle is repinned and no 5.1
test is deleted.**

## Verdict

Written last, after `## Residual limits` below was collected (Task 9, Step
2 before Step 4 — an earlier draft got this backwards and the rule meant to
force CONDITIONAL pointed at a list that did not exist yet). Nothing below
re-derives a measurement; every claim cites the section that made it.

### What the test matrix becomes

Item 48's own guess: "probably not 'one host' but 'one host plus a small
number of cases proving the refusal and the re-exec work when started from
5.1'."

**The re-exec half: technique proven, test not yet built.** Measurement 1
(Task 4) found the mechanism a kept test would assert: the ESCAPED
forwarding form (`Esc` + `ProcessStartInfo`), not the native `@args` splat
form, carried all eleven tested hostile shapes through intact under both
hosts as parent. But the harness that proved this — `<REC>/reexec/*.ps1`
and `run.py` — is this investigation's own scratch, explicitly excluded
from Measurement 3's shipped-script table as "not shipped product surface."
So this half of the guess is confirmed in TECHNIQUE, not yet built as a
kept, shipped test.

**Resolving an apparent tension, named in fix round 1.** "The code becomes
UNABLE to run on 5.1" (the migration draft's own hard ordering rule, below)
does not mean a `.ps1` file becomes physically uninvokable by
`powershell.exe` — nothing in this repo can prevent a human or a stale
launcher from typing that. It means every entry point's OWN BEHAVIOUR, when
it finds itself hosted by 5.1, changes from "run the real logic" to
"refuse, or re-exec into 7" — exactly the two retained cases this section
names. A kept re-exec test that starts under a 5.1 PARENT is not a
surviving 5.1 CODE PATH in the sense criterion 4 (below) worries about: it
is the proof that the migration's own refuse-or-re-exec logic — the thing
that makes the code "unable to run on 5.1" in the first place — actually
works when a 5.1 parent is what shows up. The ordering rule and this test
are the same requirement, not two that pull apart.

**The refusal half: not decided by any measurement.** Measurement 4 (Task
7) set out to reproduce "PowerShell 7 absent" and did not — the call
succeeded anyway, because Windows resolves a bare `pwsh` name against the
PARENT process's environment, not the stripped child environment being
passed in. No failure text was produced, so there is nothing to write a
"proves the refusal" assertion against yet. What would decide it is named
in `## Residual limits` below, under Measurement 4: a machine, container, or
CI runner with PowerShell 7 genuinely not installed anywhere.

**Two findings the guess did not anticipate.** Measurement 3 Step 3 (via
Measurement 5 Step 6, verified against source) found two of today's
dual-host tests cannot simply collapse to one host:
`test_measurement_20_ticks_and_date_string_types_diverge_across_hosts`
(`test_lock_protocol_live.py:379`-`:390`) loses its cross-host DIVERGENCE
claim outright — no one-host form exists for "these two things differ" —
though its two pwsh-only type assertions (`:388`,`:390`) survive as a
rewritten regression pin. `TestTheFramesGoOutIntactOnBothHosts`
(`test_codex_tool_surface_probe.py:490`-`:529`) can be rewritten to run
`pwsh` alone, but loses the guarantee that a green run on one host cannot
hide a defect that only shows up on the OTHER — exactly the BOM-on-first-
frame defect it exists to catch, 5.1-only.

**Conclusion.** The shape becomes: most of the 11 dual-host CI modules'
content collapses to `pwsh` alone with no special handling (Measurement 3's
own coverage table); the divergence test is retired outright, accepted as a
cost rather than a reason to keep 5.1 (see criterion 4 below); the frame
test is rewritten to one host, at the cost of the hiding-defect guarantee;
and at least one NEW test is added proving the escaped-form re-exec
technique under a 5.1-starting parent. What the "refusal" case looks like,
and therefore the exact final count of retained cases, is **not decided by
this investigation** — repeating item 48's own guess as a settled
conclusion would be wider than the evidence.

### Questions item 48 asked that this investigation did not answer

1. **Is PowerShell 7 present on the Linux (`ubuntu-latest`) CI runner?**
   (Measurement 2.) Answered by a Linux CI step running `pwsh -Command
   '$PSVersionTable.PSVersion'` and capturing a real version string — no
   such step exists today.
2. **Is PowerShell 7 present on a plugin user's machine?** (Measurement 2.)
   Not reachable from this session at all; answered by a device inventory
   or telemetry report across the actual population of plugin users.
3. **Do the JSON-depth-truncation trap and the `ConvertFrom-Json`
   nesting-limit trap (item 48's traps 1 and 4) behave correctly under
   `pwsh`?** (Measurement 3 Step 3.) Answered by un-gating
   `evals/tools/drift_statemachine_tests.ps1`'s `agy-allow-depth-over-
   boundary` scenario inside a CI job — today it self-skips when
   `pwsh.exe` is absent, and the harness itself is switched off in both CI
   jobs.
4. **Does the em-dash/`$OutputEncoding` flattening trap (item 48's trap 2)
   need a mitigation under `pwsh`, or does 7's UTF-8 default already avoid
   it?** (Measurement 3 Step 3.) Answered by adding a `pwsh`-driven case to
   `TestBriefEncodingOverStdin`, which today hardcodes `powershell.exe` at
   `test_multi_model_verify.py:2999`.
5. **What does a user actually see when `pwsh` is genuinely absent?**
   (Measurement 4, explicitly UNANSWERED.) Answered by running the probe on
   a machine, container, or CI runner with PowerShell 7 genuinely not
   installed anywhere — no `Program Files\PowerShell\7`, no WindowsApps
   alias, no `App Paths` registry entry.
6. **Do the 3 `migration=unknown` rows (the `TransparentHosts` allowlist at
   `tools/kimi-lane-lock.ps1:887` and its two doc/test siblings) still need
   to recognize `"powershell.exe"`?** (Entry point inventory, `unknown`
   rows.) Answered by deciding whether a leftover 5.1 install can still
   legitimately appear as an ancestor process in a PS7-only deployment — an
   environment question, not one the line itself answers.
7. **What is the NET time saving, once the final retained 5.1-starting test
   set exists?** (Measurement 5, explicitly left undetermined.) Answered by
   re-timing the `powershell-hosts` CI job, or its replacement, once that
   set is actually built (see `### What the test matrix becomes` above).
8. **Has the installed plugin cache, or any already-registered scheduled
   task, drifted from the checkout?** (Entry point inventory, "What this
   method cannot see.") Answered by inspecting the actual cache directory
   content and the real Task Scheduler entry, neither of which the survey
   can see.

### Criterion: "Any entry point that cannot be made to reach 7"

**Decided by TWO sections, not one (corrected in fix round 1).** The
entry-point survey answers whether a fix is NAMED for every classified
line; `## Measurement 2` answers whether the PLACES that code has to run
actually have PowerShell 7 to reach. The pre-fix text cited only the
survey. Both bear, and both leave this criterion open.

**From the entry-point survey (`## Entry point inventory`, Task 3):** 0
unclassified, 0 stale, every `must-change` row names a stated fix (at
least 83 rows, known-deflated per the inventory's own words). On its face
this looks NOT MET.

But 3 rows carry `migration=unknown`, all concerning the same
`$TransparentHosts` allowlist (`pwsh.exe`, `powershell.exe`, `cmd.exe`,
`conhost.exe`) `kimi-lane-lock.ps1`'s ancestry walk uses to decide which
processes are legitimate transparent intermediaries for a credential
operation: `evals/multi-model-verify/test_backup_lane.py:270`,
`skills/multi-model-verify/references/backup-lane.md:111`,
`tools/kimi-lane-lock.ps1:887`. The inventory's own words: whether
`"powershell.exe"` must be removed "depends on whether the ancestry walk
can still legitimately meet that name after a 5.1 drop" — a question about
the *environment* the migrated repo runs in (can a user still legitimately
invoke this repo's tooling from a lingering 5.1 outer shell), not about
what the line itself does.

**Disposition (Rule 3): these 3 rows bear on this criterion.** They are not
about whether this repo's own scripts can be made to invoke `pwsh` — the
survey already answers that. They are about whether an entry point that
already reaches 7 (the credential lock) keeps working correctly for a
legitimate caller who has not migrated their own outer shell, or should be
tightened once 5.1 is dropped inside this repo. That is undecided.

**From `## Measurement 2: is PowerShell 7 present` (Task 5) — a second,
independent reason this criterion is UNKNOWN.** Measurement 2 opens by
declaring itself the answer to this exact criterion, for the four places
this code has to run. It found PowerShell 7 present and proven on two of
them (this developer machine; the Windows CI runner, for the one run
cited) and **unproven** on the other two: the Linux (`ubuntu-latest`) CI
runner ("nothing in the workflow starts a PowerShell host there") and any
plugin user's machine (not measurable from this session at all, and per
Microsoft's own install documentation NOT the default state of a stock
Windows install). "Made to reach 7" presumes 7 is reachable at all; for
half of the four places this record checked, that is not established. This
is a genuinely different reason than the `$TransparentHosts` rows — even if
every line in the inventory were `must-change` with zero `unknown` rows,
this criterion would still be UNKNOWN on Measurement 2's evidence alone.

**Sweep of `## Residual limits` against this criterion (Rule 4).** The
entry-point survey's own named method limits (`## Entry point inventory`,
"What this method cannot see", carried into `## Residual limits`' Task 3
bucket) were walked entry by entry:

- The versioned plugin cache possibly drifting from the checkout, and an
  already-registered scheduled task keeping a stale host — both bear: a
  `must-change` row repinned in the checkout does not certify what is
  actually INSTALLED or already registered is reaching 7. Not separately
  resolvable by more survey work (the survey reads source, not the cache
  or Task Scheduler); folded into condition (1) below rather than given a
  fifth condition of its own.
- Verbally-relayed or memory-carried instructions, and untracked files
  (the `tools/drift-reports/` wrappers) — both bear on how completely "no
  entry point cannot reach 7" can be certified, for the same reason: they
  are, by definition, invisible to a method that reads tracked files. Same
  disposition — folded into condition (1).
- `NOT SCANNED` files — **does not bear on this criterion today, because**
  the survey's own final run reports `0 files not scanned`; there is
  currently no unread file to name.
- A classification that is syntactically valid but semantically wrong —
  bears on whether a `must-change` row's STATED fix is actually the RIGHT
  fix, which this record cannot verify by construction. Folded into
  condition (1): the same "environment and correctness, not just
  presence-of-a-row" gap the `$TransparentHosts` rows already represent.
- The unmatched shape at `README.md:412`, and the deliberately-unmatched
  bare-`git` class — **do not, themselves, bear on this criterion**,
  because both are named instances the record's own text states CAN be
  migrated exactly like their neighbours; they weaken confidence in the
  survey's completeness (more misses may exist), not evidence that
  something cannot reach 7. That completeness concern is already carried
  by the two bullets above, not counted a third time.
- Measurement 3's note that `pwsh` presence on `ubuntu-latest` for Tier 2b
  was not independently re-verified, and that the `hooks/hooks.json`
  citation is scoped to the checkout — **does not add a new bearing
  item**; it is the same Linux-runner and plugin-cache gaps already named
  above under Measurement 2 and the entry-point survey, counted once.
- **Missed in fix round 1, added in fix round 2: "The green Windows CI run
  cited proves PowerShell 7 present on the runner image served for that
  one run on that one date, not that every future `windows-latest` image
  carries it"** (Measurement 2's own bucket) — **bears, and is a
  DIFFERENT KIND of gap than the two above, not folded into condition
  (1).** The Linux-runner and plugin-machine gaps above are "unproven,
  ever." This one is "proven once (run `32391262449`, 2026-08-20),
  durability unproven" — a positive result whose SCOPE is narrower than a
  reader could take "proven" (used two paragraphs above) to mean. Judged
  on its own merits rather than folded for convenience: this is a real,
  separate open question about whether the ONE proven place stays proven,
  not the same question as whether the TWO unproven places ever become
  proven. **Added to the verdict's condition list as condition (5)
  below.**

**Criterion: UNKNOWN, for THREE independent reasons** — the 3
`migration=unknown` rows (`test_backup_lane.py:270`, `backup-lane.md:111`,
`kimi-lane-lock.ps1:887`); PowerShell 7's unproven presence on the Linux CI
runner and on any plugin user's machine (Measurement 2); and the Windows CI
runner's proof being scoped to one run rather than shown durable
(Measurement 2, added in fix round 2). Per Rule 5, a criterion resting on
an unresolved question is UNKNOWN, not NOT MET, and NOT MET would in any
case be too wide a claim while any of the three reasons stands.

### Criterion: "A re-exec that cannot pass arguments through provably intact"

Decided by Measurement 1 (Task 4) — a direct measurement, not reasoning: 8
arms (2 hosts x 2 forwarding forms x 2 argument shapes), 11 hostile payload
shapes. Under the ESCAPED form, every arm survived under both hosts as
parent (stage B exact `true` in all 4 escaped rows). Under the native SPLAT
form, PowerShell 5.1 as parent corrupted both shapes (`ps51/splat/
positional`: 8 of 10 items received; `ps51/splat/named`: embedded quote and
trailing backslash both mangled); PowerShell 7 as parent survived splat
cleanly. Measurement 1's own section, headed "Answer to the NO-criterion,"
states this without hedging.

**Sweep of `## Residual limits` against this criterion (Rule 4),** all from
Measurement 1's own bucket:

- The host's own `-File` parsing was not isolated from the forwarding
  mechanism — **does not bear on this criterion's conclusion, because** it
  only limits how finely a FUTURE corruption could be localized
  (parent-vs-child); it did not weaken or change the positive finding for
  the escaped form, which corrupted nothing in this measurement.
- Untried parameter shapes (arrays, `ValueFromRemainingArguments`,
  self-re-exec) bear on this criterion for those specific shapes only, not
  for the ones measured; not a new condition, since the status below is
  already scoped to what was tested rather than claimed for every
  possible shape.
- One machine, one build of each host bears on generalizing this finding
  elsewhere; already scoped by this record's own header (lines 4-5), so
  does not add a limit specific to re-exec beyond what the whole record
  already carries.
- **Command-line length against the ~32767-character ceiling — bears, and
  is NOT dismissed (corrected in fix round 1).** The pre-fix text admitted
  this bearing ("not dismissed") and then closed the criterion NOT MET as
  if it had been dismissed, which Rule 4 does not permit. Cross-task
  evidence narrows the gap: `docs/superpowers/plans/rounds/
  2026-08-22-item51-inline-brief-probe/probe-record.md` (cited in full
  under `## Residual limits`, Measurement 1 bucket) independently measured
  this SAME escaped mechanism at much larger sizes and found it exact at
  31995 characters, throwing (`The filename or extension is too long`) at
  32967 and 39933 — a LOUD failure, symmetric on both hosts, not silent
  corruption and not a 5.1-specific one. That narrows the gap considerably
  but does not close it: item 51's own scenario
  (`docs/superpowers/plans/2026-07-27-0150-backlog.md:3748`) is exactly "a
  large non-ASCII brief passed as a command-line argument," and the
  untested region — whether a real migration payload could ever approach
  or exceed that ~32000-character ceiling, and if so what transport
  replaces the escaped argument form — is exactly the region a migration
  exists to cover. **Added to the verdict's condition list as condition
  (4) below**, not dismissed here.

**Criterion: NOT MET, scoped explicitly to what was measured** — decided
by Measurement 1 for the argument shapes it tested, via the escaped
forwarding form, extended (not merely asserted) by the item-51 probe up to
31995 characters on both hosts. This status does NOT cover payloads at or
beyond the ~32000-character command-line ceiling, where the escaped form's
behaviour (a loud throw, per the item-51 probe) has not been evaluated
against what item 48's own re-exec requirement needs — that gap is
condition (4) of the verdict, not folded silently into "NOT MET."

### Criterion: "A user-facing failure mode worse than the bugs being removed"

Decided by Measurement 4 (Task 7). The probe stripped every PATH entry
containing `pwsh.exe` from a child environment and ran the hook's exact
shipped invocation shape. The call succeeded anyway (`returncode: 0`,
empty stdout/stderr) — Windows resolved the bare name `pwsh` against the
PARENT process's own environment, not the stripped child environment being
passed in; a `cmd /c where pwsh` check confirmed the strip itself was
genuine.

Measurement 4's own words, verbatim, at its close: "item 48's NO-criterion
'a user-facing failure mode worse than the bugs being removed'... [is]
UNANSWERED, and item 48's own requirement that the failure 'must stop with
a message naming what to install' is UNTESTED by this task — no failure
text was produced to check that requirement against. `## Verdict` may not
treat this criterion as satisfied on the strength of this section."

**Sweep of `## Residual limits` against this criterion (Rule 4),** all
from Measurement 4's own bucket — each already folded into the UNKNOWN
status below rather than adding a new one:

- Only the bare-`pwsh` resolution path was probed; entry points that name
  `powershell.exe` explicitly were not — bears, and is already the reason
  this section's own findings are scoped to one invocation shape; no new
  condition, since the whole section is already the unresolved measurement
  behind condition (2).
- Claude Code's hook-runner presentation of a failure, and its resolution
  METHOD (direct process-creation vs. shell-mediated), were not measured —
  bears, same disposition: already inside the unresolved measurement that
  is condition (2).
- The probe did not reproduce genuine absence, on a machine with two
  resolvable `pwsh.exe` copies — this IS the primary fact behind the
  UNKNOWN status; not a separate item.
- Item 48's own NO-criterion, left UNANSWERED in bold at the section's
  close — this is the criterion itself being named unresolved by its own
  deciding section; already condition (2), not counted again.

**Criterion: UNKNOWN** — Measurement 4 explicitly could not reproduce the
condition it set out to test. Per Rule 2, UNKNOWN, not NOT MET, and it
cannot produce YES on its own strength.

### Criterion: "Any need to keep a 5.1 code path 'just in case', which would mean paying for both hosts and testing one"

**Why "the test set" is the right proxy for "a code path" here (fix round
1, Minor 1).** The criterion is worded about a CODE PATH; this subsection
answers it by talking about a TEST SET, and that substitution needs to be
justified rather than made silently. A retained test cannot exist without
SOME code path for it to exercise: proving "the re-exec work when started
from 5.1" or "the refusal when pwsh is missing" requires that the
corresponding entry point still contains logic that runs while hosted by
5.1 — the escaped-form re-exec, or the refusal check. So the size and
shape of the retained TEST SET is a direct, one-to-one proxy for the size
and shape of the retained 5.1 CODE PATH: every kept test implies exactly
the code path it exercises, and no more. This is why `### What the test
matrix becomes` above is answered first — it IS this criterion's evidence,
not a stand-in for it. What it does not automatically resolve is whether
that code path is the narrow, criterion-2-required kind (detect-and-
refuse-or-re-exec, which item 48 itself requires to exist) or a wider
"just in case" hedge — that distinction is exactly what remains open
below.

Decided jointly by `### What the test matrix becomes` above and
Measurement 5's ledger. What the measurements DO establish: most of today's
dual-host coverage needs no hedge — Measurement 3 found most of the 11
dual-host CI modules have no behaviour that depends on comparing two hosts;
those collapse to `pwsh` alone. That is the opposite of "paying for both
hosts and testing one."

What the measurements do NOT establish: the exact shape and cost of the
"small number of cases" item 48 anticipated keeping. The re-exec case has a
proven technique but no built test. The refusal case cannot be specified at
all, because Measurement 4 never reproduced the condition it would test
against. Measurement 5 states outright: "The retained-case set... is not
yet chosen (Task 9), so its ongoing cost is not priced here either" — and
`### What the test matrix becomes` above confirms that determination stays
open for the refusal half.

**Residual dispositioned (Rule 4):** the two bilateral tests found in
Measurement 5 Step 6 (`test_measurement_20_ticks_and_date_string_types_
diverge_across_hosts`, `TestTheFramesGoOutIntactOnBothHosts`) bear on this
criterion — they are existing cases whose value today depends on running
something under both hosts. This does NOT bear as "evidence 5.1 must be
retained": the record's own reconciliation is that the divergence claim is
lost outright (accepted as a cost, not preserved by a hedge) and the frame
test's assertion form survives a one-host rewrite. Dispositioned as: a real
accepted loss on the cost side, not a reason to keep 5.1.

**Sweep of `## Residual limits` against this criterion (Rule 4),** the
remainder of Measurement 5's bucket:

- **The bilateral-mechanism sweep was run four ways but is not claimed
  exhaustive — bears, and is NOT dismissed.** If a fifth sweep method
  found a third test whose value depends on comparing two hosts, the
  retained-case set's shape (and this criterion's answer) could change
  again. **Folded into condition (3) below** (the open question about
  that set's final shape), rather than given a separate numbered
  condition.
- The four saved-time figures (CI wall-clock, the local pair, item 44's
  gate, the two defects avoided), the 5-run CI sample, and item 44's
  GROSS-only figure — **do not bear on this criterion, because** they
  describe the SIZE of the benefit from dropping 5.1, not whether a 5.1
  code path must be kept; a smaller or larger saving does not change
  whether the "small number of cases" is needed.
- The edit cost's "at least 83 rows, plus 3 further `unknown`" — **does
  not add a new bearing item here**; the 3 `unknown` rows are the same
  `$TransparentHosts` rows already dispositioned under criterion 1, not a
  separate cost-side fact about criterion 4.
- The retained-case set not yet chosen, cost not priced — this is the
  ALREADY-central fact behind this criterion's UNKNOWN status below, not a
  new item.

**Further sweep entries, from Measurement 3's bucket (missed in fix round
1, walked in fix round 2):**

- "This section maps INVOCATION..., not that the invoking module's
  assertions are the RIGHT check, and does not re-derive
  `entry-points.tsv`'s own classifications" — **bears on this criterion.**
  The coverage table's "10 of 16 covered" claim is only as strong as the
  covering modules' assertions actually testing the right behaviour, which
  this record does not verify. A wider retained-case set could be needed
  than the coverage table alone suggests. **Folded into condition (3)**
  ("fixing the final retained test set's shape") — this is a REASON that
  shape is not yet fixed, not a new fact standing outside it.
- "The 6 uncovered scripts are not equally unproven" —
  `superpowers-review-companion.ps1` has a narrower gap (runs under a real
  `pwsh`, just outside the dual-host job) than `.githooks/pre-push` (no
  `runs` row anywhere, on any host) — **bears.** `.githooks/pre-push` is a
  candidate for a THIRD kind of retained case beyond item 48's
  re-exec/refusal pair, since nothing today proves its behaviour under
  EITHER host. **Folded into condition (3)**, same reason as above — this
  widens what "fixing the shape" has to decide, it does not add a new
  question outside that shape.
- "The three extra host-sensitive behaviours found beyond item 48's named
  five are not claimed to be the complete set a wider search would find"
  — **bears, the same way the bilateral-sweep's non-exhaustiveness bears
  above:** an incomplete search for host-sensitive behaviours means the
  retained-case set could be missing a case this record has not yet found.
  **Folded into condition (3)** — the same open question as the
  bilateral-sweep bullet, about the SAME unresolved shape, not a second
  incompleteness question.

**Criterion: UNKNOWN** — the measurements support that broad dual-host
retention is not needed, but do not yet fix the final small retained set
(particularly the refusal case, blocked on Measurement 4; the open
bilateral-sweep completeness; whether coverage-table modules' assertions
are the right check; and whether `.githooks/pre-push` needs its own case),
so this criterion rests on an incomplete measurement rather than a settled
one, per Rule 5.

### Residuals bearing on none of the four criteria, or already fully covered above

Completing the Rule 4 sweep (fix round 1): the remaining `## Residual
limits` entries not walked inside a criterion subsection above.

- **One ANSI code page** (investigation-wide) — does not bear on any of
  the four criteria directly; it bears on the em-dash/`$OutputEncoding`
  trap's generalizability, already carried as an open question in `###
  Questions item 48 asked that this investigation did not answer` (item
  4), not restated as a verdict condition here.
- **One Claude Code version** (investigation-wide) — does not bear on any
  of the four criteria, because none of them concerns the tooling that ran
  this investigation's own measurements; it is a limit on this
  investigation's own reproducibility, not on the repo's behaviour under
  either PowerShell host.
- **One machine, one build of each host** (investigation-wide) — already
  dispositioned specifically where it matters most, under criterion 2
  above; for criteria 1, 3 and 4 it does not name a question beyond what
  Measurement 2's unproven environments (criterion 1) and Measurement 4's
  unreproduced absence (criterion 3) already are.
- **No script was run under a migration it does not yet have**
  (investigation-wide) — bears, diffusely, on all four criteria at once:
  none of them observes the actual migrated code. It is not a sixth,
  separate condition; it is why the five conditions in the verdict line
  below exist in the first place — each one names the specific unmeasured
  piece of "the migrated code's real behaviour" that this bullet describes
  in general terms.

### Applying the rules

1. No criterion is MET — does not force NO by itself.
2. Criteria 1, 3 and 4 are UNKNOWN — forces CONDITIONAL. Criterion 1 is
   UNKNOWN for THREE independent reasons (the 3 `migration=unknown`
   `TransparentHosts` rows; PowerShell 7's unproven presence on the Linux
   CI runner and any plugin user's machine; and the Windows CI runner's
   proof being scoped to one run, added in fix round 2). Criterion 3 is
   UNKNOWN because Measurement 4 never reproduced the condition it set out
   to test. Criterion 4 is UNKNOWN because the final retained 5.1-starting
   test set's shape is not fixed (blocked on criterion 3's own gap, on the
   bilateral-sweep completeness question, and on the two further
   Measurement-3 gaps added in fix round 2).
3. The 3 `migration=unknown` rows bearing on criterion 1 independently
   force CONDITIONAL (listed above by `path:line`).
4. **Checkable Rule 4 sweep (fix round 2 rewrite — fix round 1's version
   of this claim was itself wrong; see below).** `## Residual limits` holds
   34 bulleted entries across 7 buckets, machine-counted by `awk` over the
   section (command and output in the fix-round report; any reader can
   re-run it):

   | Bucket | Entries | Where walked |
   |---|---|---|
   | Entry point inventory (Task 3) | 8 | Criterion 1 sweep |
   | Measurement 1 (Task 4) | 5 | Criterion 2 sweep |
   | Measurement 2 (Task 5) | 3 | Criterion 1 (2 in the main paragraph, 1 — the green-CI-run bullet — in the sweep, fix round 2) |
   | Measurement 3 (Task 6) | 4 | Criterion 1 sweep (1) + Criterion 4 sweep (3, fix round 2) |
   | Measurement 4 (Task 7) | 4 | Criterion 3 sweep |
   | Measurement 5 (Task 8) | 6 | Criterion 4 sweep |
   | Investigation-wide | 4 | `### Residuals bearing on none of the four criteria` |
   | **Total** | **34** | all 34 placed; 0 unplaced |

   Verify by running, from the repo root:
   `awk '/^## Residual limits/{r=1} /^## Draft: the migration item/{r=0} r&&/^### /{if(b!="")print b": "c;b=$0;c=0;next} r&&/^- /{c++} END{if(b!="")print b": "c}' docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/feasibility-record.md`
   and summing the printed counts (the closing-gate subsection prints `0`
   because it is a prose paragraph, not a bulleted residual list, and is
   already self-dispositioned inline — "not claimed to bear on any
   criterion above" — so it is not counted among the 34). Fix round 1's
   prose claim ("every entry... was walked") was checked by sampling and
   found FALSE for 4 of the 34 entries, all inside the Measurement 2 and
   Measurement 3 buckets; fix round 2 walked those 4 (recorded in the
   criterion 1 and criterion 4 sweeps above) and rewrote this item so the
   claim is a count a reader can re-derive rather than a sentence they have
   to trust.
5. YES is unavailable: three of four criteria are UNKNOWN, not NOT MET.

**VERDICT: CONDITIONAL ON** (1) resolving whether the `$TransparentHosts`
allowlist (`tools/kimi-lane-lock.ps1:887`,
`evals/multi-model-verify/test_backup_lane.py:270`,
`skills/multi-model-verify/references/backup-lane.md:111`) still needs to
recognize `"powershell.exe"`, AND proving PowerShell 7 present on the Linux
(`ubuntu-latest`) CI runner and on the machines of plugin users who would
lose the 5.1 fallback (Measurement 2 found both unproven); (2) reproducing
and verifying a genuine pwsh-missing refusal, which Measurement 4 did not;
(3) fixing the final retained 5.1-starting test set's shape and cost —
which cannot be finished until (2) is answered, requires confirming the
bilateral-mechanism sweep (only run four ways so far) has found every test
whose value depends on comparing two hosts, requires deciding whether the
coverage table's covering modules are actually asserting the right thing,
and requires deciding whether `.githooks/pre-push` (proven on NO host
today) needs its own retained case; (4) confirming that the escaped
re-exec form's ~32000-character command-line ceiling — bracketed by this
record's own item-51 probe at 31995 exact / 32967 throws, a loud failure
symmetric on both hosts, not silent corruption — does not bind any real
migration payload, or specifying a fallback transport for a payload that
would exceed it; and (5) confirming that PowerShell 7's proven presence on
the Windows CI runner (Measurement 2, run `32391262449`, 2026-08-20) holds
for the images GitHub actually serves going forward, not just the one run
this record cites (added in fix round 2 — Measurement 2's own text never
claimed more than the one run, but the pre-fix verdict read "proven" as if
it had).

Only ONE of the four criteria is actually NOT MET — criterion 2, re-exec
fidelity, and even that is scoped to what was
measured rather than claimed unconditionally (fix round 1 corrected an
earlier draft that closed it wider than its own admitted residual).
Criterion 1's underlying survey finding also points this record's own way
— every classified line has a stated migration path — but that finding is
not the criterion's final status: three independent gaps (the 3
`$TransparentHosts` rows, PowerShell 7's unproven presence on two of the
four places this code has to run, and the Windows CI runner's proof being
scoped to one run) leave criterion 1 itself UNKNOWN, not NOT MET. Criteria
3 and 4 open onto genuine gaps rather than close ones — the refusal probe
could not reproduce PowerShell 7's absence at all, so item 48's own
failure-mode requirement is untested rather than met, and that same gap,
plus the unresolved allowlist and environment findings, the not-yet-
exhaustive bilateral sweep, and the two further coverage-confidence gaps
Measurement 3 itself names, leaves the final retained test set
undetermined. None of these five conditions is evidence of a NO — nothing
measured here points at an unreachable entry point, a corrupting re-exec,
or a worse failure mode — they are unmeasured or only partially measured,
which Rule 2 and Rule 4 do not permit reading as clean.

## What would make the verdict NO

Copied verbatim from backlog item 48 BEFORE any measurement was made, so
the answer cannot be shaped by the effort already spent:

- Any entry point that cannot be made to reach 7 - most likely a hook or a
  scheduled task registered outside this repo's control.
- A re-exec that cannot pass arguments through provably intact.
- A user-facing failure mode worse than the bugs being removed.
- Any need to keep a 5.1 code path "just in case", which would mean paying
  for both hosts and testing one.

## Method

The entry point inventory is produced by `survey.py` in this directory and
verified by re-running it, not by rereading it. Two earlier hand
inventories of this item were wrong: the first in three of four entries,
the second in four further ways after claiming to fix the first.

The script matches THREE regex families across every tracked file it can
read, and FAILS if any match lacks a written classification. So a DETECTED
entry point cannot be passed over silently.

It does not do more than that, and this record does not claim it does:

- The families are a filter. They were two when first written and have been
  corrected repeatedly, every time because a reviewer produced a live entry
  point in this repo that the filter did not match. The count and the
  enumerated list live in `survey.py`'s FAMILIES comment and nowhere else;
  copy them from there. There is no argument that the current filter is
  enough - only that nobody has produced the next miss yet, which is not
  the same statement.
- A green run says every detected match carries a row. It says nothing
  about whether the row is CORRECT.
- A file the script cannot read is listed as `NOT SCANNED`, by name. An
  unread file is not a clean one.

## Entry point inventory

Produced by classifying every match `survey.py` detects across the three
regex families (`host`, `launch`, `bare`), split by family across three
tasks in that order, each committing its own rows and each judged per line
by reading the line and its surrounding code, never from the path or from
expectation. Two hand inventories of this exact question shipped wrong
before this method existed.

**Final survey run**, verbatim:

```
FAMILY bare: 5491 hits, 0 unclassified
FAMILY host: 1143 hits, 0 unclassified
FAMILY launch: 529 hits, 0 unclassified
SURVEY: 7163 hits, 7163 classified, 0 unclassified, 0 stale, 0 files not scanned
```

Exit code: `0`.

**What this proves, and no more.** This green run proves every detected
match carries a syntactically valid row, and that no row points at a line
that has changed or gone. It does NOT prove any classification is CORRECT,
and it does not prove the three families detect every entry point.

**Why a re-run today prints different numbers — TWO causes, not one
(corrected in the final-review fix; the number below was also stale until
this fix re-ran the command rather than copying an old table).**
Re-running the survey command above after this section existed prints
`7481 hits, 7481 classified, 0 unclassified, 0 stale`, still exit code `0`
— higher than the 7163 captured above, for two DIFFERENT reasons that this
record previously conflated into one:

1. **The hit-count growth** (7163 -> 7476, the `survey.py` run's own
   total). This section's own prose quotes `powershell.exe`, `pwsh.exe` and
   `.ps1` text about the inventory, adding matches inside
   `feasibility-record.md` itself. That file is covered by the `docs/`
   prefix row, so these new matches need no rows and do not turn the
   survey red; the 7163 above is the Step 3 run captured before this
   section was written, not a number this record keeps in sync with
   itself.
2. **The row-count growth in `entry-points.tsv`**, which is the actual
   cause of the classification-counts table below moving. Task 4 (commit
   `43cd165`) added 21 explicit rows for `<REC>/reexec/*.ps1`, and Task 7
   (commit `8b8918c`) added 12 for `<REC>/missing-pwsh/probe.py` — both
   scratch files this investigation itself created, under the `docs/`
   prefix but matched by `EXEMPT_SUFFIXES`, which forces an explicit row
   for any `.py`/`.ps1` file rather than letting the prefix row cover it.
   33 rows (21 + 12) accounts for the table's total moving from 1078 to
   1111; a further 3 rows, added by this final review's own Important 3
   fix to `survey.py`'s own comment prose (the same self-quoting effect
   as cause 1 above, but landing as classified rows because `survey.py`
   itself sits under `EXEMPT_SUFFIXES`, not the `docs/` prefix), move the
   table's actual total to 1114 below. Rows-versus-hits is a separate
   distinction, explained where the table sits, and does not by itself
   explain why the table's OWN total changed.

### Classification counts

Produced by, re-run for this fix rather than copied from an earlier table:
`awk -F'\t' '!/^#/ && NF==6 {print $5}' docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/entry-points.tsv | sort | uniq -c | sort -rn`

| count | classification |
|---|---|
| 609 | not-a-launch |
| 227 | test-harness |
| 106 | doc-instruction |
| 54 | launch-nonhost |
| 46 | host-pin-nonexec |
| 31 | fixture |
| 15 | launch-explicit |
| 13 | ci |
| 7 | launch-inherit |
| 5 | host-pin-exec |
| 1 | record |

One row of the 7481 hits is a prefix row (`docs/	*	*	-	record	no-change`);
the count above is the per-row classification, not per-hit, so the table's
total (1114) is the hand-written row count, not the hit count (7481) the
prefix row also covers.

### `must-change` rows, whole file

Every row whose `migration` value is `must-change`, one line each. Rows
from the `host` and `launch` family tasks are described from reading the
same lines during this pass, not re-classified; only the `bare` rows below
were classified by this task.

- `.githooks/pre-push:24` (host-pin-exec / launch-explicit) — hardcodes
  `powershell.exe` as the attestation verifier's interpreter; must invoke
  `pwsh.exe` (or resolve dynamically) once 5.1 is gone.
- `.github/workflows/skill-evals.yml:74` — the `run:` step body of the
  "PowerShell-facing tests under Windows PowerShell 5.1" job step; the
  whole step must be removed or repurposed with 5.1 dropped.
- `.github/workflows/skill-evals.yml:95` — `PARALLAX_PS_HOST:
  powershell.exe`, the 5.1 job step's env line; the whole step (this line,
  and `:96`/`:97` below) must go with it. (`:112`, the PAIRED `pwsh.exe`
  env line for the step that SURVIVES, is `no-change` — see the
  correction note at the end of this list.)
- `.github/workflows/skill-evals.yml:96`, `:97` (bare) — `run: >` and
  `python -m pytest ...`, the body of that same 5.1 job step. Read on
  their own these lines are host-neutral text; they are `must-change`
  because deleting the step they belong to (per `:95` above) deletes them
  with it — the step and its env line, run header, and command body stand
  or fall together, and the `host` family's `:95` row already reads
  `must-change`.
- `evals/multi-model-verify/test_attestation.py:10` — docstring stating
  the module "runs wherever a PowerShell host exists: Windows
  powershell.exe or pwsh"; the 5.1 half of that sentence must go.
- `evals/multi-model-verify/test_attestation.py:30`, `:36` — the
  `POWERSHELL` host-selector's comment and its
  `shutil.which("powershell")` fallback; the fallback must be dropped.
- `evals/multi-model-verify/test_backup_lane.py:1322,1328,1334,1338,1340,
  1354,1360,1373,1374,1376,1378,1388,1395,1401,1408,1413` —
  `test_check_workflow_paths_flags_host_parity_gap` and its neighbours
  build synthetic workflow text asserting BOTH a `powershell.exe` step and
  a `pwsh.exe` step exist with parity; dropping 5.1 removes the thing
  these tests enforce, so they must be rewritten or removed.
- `evals/multi-model-verify/test_backup_lane.py:1741` — a separate test,
  roughly 330 lines later in the same file (not one of the
  `test_check_workflow_paths_flags_host_parity_gap` neighbours above): it
  reads the real `skill-evals.yml` and asserts a `PARALLAX_PS_HOST:` marker
  exists for BOTH `"powershell.exe"` and `"pwsh.exe"`; the 5.1 half of that
  assertion must go with the step it checks for.
- `evals/multi-model-verify/test_codex_context_probe.py:52` — comment
  stating `powershell-hosts` runs the module "under BOTH powershell.exe
  and pwsh.exe"; the 5.1 half must go.
- `evals/multi-model-verify/test_codex_context_probe.py:58` — the
  `POWERSHELL` selector's `shutil.which("powershell")` fallback; drop it.
- `evals/multi-model-verify/test_codex_round_evidence.py:58` — same
  `POWERSHELL` selector pattern; drop the `powershell` fallback.
- `evals/multi-model-verify/test_codex_tool_surface_probe.py:40`, `:515` —
  the selector fallback, and a test that explicitly resolves both
  `shutil.which("powershell")` and `shutil.which("pwsh")` to drive every
  present host; both must lose their 5.1 half.
- `evals/multi-model-verify/test_home_skill_canary.py:62` — same selector
  fallback pattern; drop it.
- `evals/multi-model-verify/test_kimi_credential_state.py:70` — same
  selector fallback pattern; drop it.
- `evals/multi-model-verify/test_kimi_lane_home.py:61` — same selector
  fallback pattern; drop it.
- `evals/multi-model-verify/test_kimi_lane_home.py:238` — docstring on
  `_clean_env` explaining why `PSModulePath` is scrubbed: a PS7-flavoured
  `PSModulePath` shadows "the 5.1 copy of Microsoft.PowerShell.Security"
  inside a `powershell.exe` child; the whole rationale disappears with 5.1.
- `evals/multi-model-verify/test_kimi_lane_lock.py:30` — same selector
  fallback pattern; drop it.
- `evals/multi-model-verify/test_kimi_lane_lock.py:225` — docstring noting
  the `powershell` fallback "resolves under System32 with no spaces"
  unlike the `pwsh` fallback under Program Files; the 5.1 half of that
  comparison disappears with 5.1.
- `evals/multi-model-verify/test_kimi_lane_login.py:47` — same selector
  fallback pattern; drop it.
- `evals/multi-model-verify/test_kimi_lane_login.py:234` — same
  PSModulePath/`Get-Acl`-shadowing rationale as
  `test_kimi_lane_home.py:238`; the rationale disappears with 5.1.
- `evals/multi-model-verify/test_kimi_round_evidence.py:89` — same
  selector fallback pattern; drop it.
- `evals/multi-model-verify/test_lane_credential_live.py:60` — same
  selector fallback pattern; drop it.
- `evals/multi-model-verify/test_lock_protocol_live.py:21` — docstring
  explaining "Measurement 20's divergence test... needs BOTH
  powershell.exe and pwsh.exe to have actually run"; the whole rationale,
  and the test it describes, must go with 5.1.
- `evals/multi-model-verify/test_lock_protocol_live.py:55` — the
  `POWERSHELL` selector's `shutil.which("powershell")` fallback; drop it.
- `evals/multi-model-verify/test_lock_protocol_live.py:71` — inside
  `ps_host()` (not `required_hosts()`, which starts lower at `:77`), the
  `pytest.fail` text "and neither powershell nor pwsh is on PATH"; the 5.1
  half of that message must go.
- `evals/multi-model-verify/test_lock_protocol_live.py:83` — inside
  `required_hosts()`, the literal `for name in ("powershell.exe",
  "pwsh.exe")` loop that demands BOTH hosts be on PATH; must be rewritten
  to require only `pwsh.exe`.
- `evals/multi-model-verify/test_lock_protocol_live.py:78` — docstring on
  `ps_host()` stating "the plan's own verification runs this module
  twice, once per host"; false once there is one host.
- `evals/multi-model-verify/test_lock_protocol_live.py:381`, `:382`,
  `:400` — `test_measurement_20_ticks_and_date_string_types_diverge_
  across_hosts`, which asserts `powershell.exe` and `pwsh.exe` return
  DIFFERENT `ConvertFrom-Json` types for the same value; the test's whole
  premise is the divergence between two hosts, so it must be removed with
  5.1.
- `evals/multi-model-verify/test_multi_model_verify.py:2954`, `:2961`,
  `:2999` — `os.name != "nt"` skip-reason strings and comments naming
  "drives powershell.exe"; the module they gate hardcodes `powershell.exe`
  (see the next bullet, `:2960`/`:2962`/`:2998`/`:3000`) and must change
  with it.
- `evals/multi-model-verify/test_multi_model_verify.py:2960`, `:2962`,
  `:2998`, `:3000` — the two `subprocess.run(["powershell.exe", ...])`
  calls (`test_run_state_machine` and `TestBriefEncodingOverStdin._run`)
  and their `"-File", str(...)` argument-list halves; both hardcode
  `powershell.exe` as the literal interpreter and must be changed to
  `pwsh.exe`.
- `evals/multi-model-verify/test_review_mirror.py:38` — comment stating
  the `powershell-hosts` job "runs this module under BOTH powershell.exe
  and pwsh.exe"; the 5.1 half must go.
- `evals/multi-model-verify/test_review_mirror.py:42` — same selector
  fallback pattern; drop it.
- `evals/multi-model-verify/test_skill_report_shapes.py:17` — docstring
  stating "CI already runs this directory under both Windows PowerShell
  and pwsh"; false once there is one host.
- `evals/multi-model-verify/test_skill_report_shapes.py:45` — same
  selector fallback pattern; drop it.
- `evals/tools/check_workflow_paths.py:41,42,43` — docstring/comment
  defining the required host MULTISET as "exactly one `powershell.exe`
  and one `pwsh.exe`"; the checker's whole contract changes with 5.1 gone.
- `evals/tools/check_workflow_paths.py:85` — `REQUIRED_HOST_NAMES =
  {"powershell.exe", "pwsh.exe"}`; must drop `"powershell.exe"`.
- `evals/tools/check_workflow_paths.py:153` — comment restating the
  multiset requirement; same change as above.
- `evals/tools/drift_statemachine_tests.ps1:542` — `if (-not $psHost) {
  $psHost = "powershell.exe" }`, the harness's default host; must default
  to `pwsh.exe` (or the harness's whole dual-host framing must go).
- `evals/tools/lane_credential_live_support.py:84` — `resolve_ps_host()`
  docstring; drop the `powershell` half of the fallback description.
- `evals/tools/lane_credential_live_support.py:89` — the
  `shutil.which("powershell")` fallback inside `resolve_ps_host()`; drop
  it.
- `evals/tools/lane_credential_live_support.py:98` — `clean_env()`
  docstring citing the same PS7-shadows-5.1 `PSModulePath`/`Get-Acl`
  rationale; disappears with 5.1.
- `README.md:312` — "`pwsh` (PowerShell 7) for the hook; Windows
  PowerShell 5.1 for the drift watch scheduled task"; the 5.1 half of the
  Requirements line must go.
- `tools/check-drift.ps1:68` — `$appId =
  '{...}\WindowsPowerShell\v1.0\powershell.exe'`, the toast notifier's
  hardcoded AppID path; must point at the PS7 identity once 5.1 is gone.
- `tools/check-drift.ps1:96` (host and launch rows, both `must-change`) —
  `$action = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File
  ..."`, the scheduled task's registered action; must register `pwsh.exe`
  instead.
- `tools/check-drift.ps1:21` — comment: "Written for Windows PowerShell
  5.1 (what schtasks runs): no &&, no ternary, ASCII ONLY"; the whole
  premise (a script written for 5.1's syntax limits) goes away once 5.1
  is dropped.
- `tools/check-drift.ps1:405` — comment: "an over-boundary scenario
  naming pwsh.exe proves a value past the ceiling is reported"; the
  surrounding paragraph's premise — that 5.1 is the default and pwsh.exe
  is named as the one exception (`:406`-`:407`) — goes away with 5.1.
- `README.md:413`, `:414` (bare) — `powershell tools/check-drift.ps1
  -Register` / `-TestNotify`; both name the literal 5.1 launcher
  (`powershell`, not `pwsh`) and must change to `pwsh` once 5.1 is
  dropped.
- `commands/doctor.md:340` (launch and bare rows, both `must-change`) —
  `powershell -NoProfile -File <installPath>\tools\codex-context-probe.ps1
  ...`; same literal-launcher problem as above, must change to `pwsh`.
- `skills/multi-model-verify/SKILL.md:326` (launch and bare rows, both
  `must-change`) — `powershell -NoProfile -File
  <plugin-root>/tools/write-attestation.ps1 ...`; same literal-launcher
  problem, must change to `pwsh`.
- `evals/multi-model-verify/fixtures/stub-appserver/stub-appserver.cmd:14`
  (host and launch families, both rows) — `powershell.exe -NoProfile
  -NonInteractive -File "%~dp0stub-appserver.ps1" %*`. This is live
  executable code, not description: the file's own comment at `:12`-`:13`
  states that driving the probe through THIS file is what proves the
  `.cmd` branch launches at all, and the line it drives through hardcodes
  `powershell.exe`. Settled to `must-change` on both rows (the `host`
  family's row previously read `unknown`; see the correction note below):
  once 5.1 is gone, `powershell.exe` either does not exist or is no
  longer the intended target, so the line must change to `pwsh.exe` for
  the stub to keep proving what it exists to prove.

### `unknown` rows, whole file

Every row whose `migration` value is `unknown`, with why it could not be
determined from the line. `migration` is a property of the LINE, not of
the family row — one line has one answer, and where the `host` and
`launch` rows for the same line disagreed (`stub-appserver.cmd:14`,
below), that has been settled to a single value rather than left as two
answers; the settlement is recorded in the `must-change` list above, not
here.

- `evals/multi-model-verify/test_backup_lane.py:270` — an `assert` string
  checking that `backup-lane.md` documents `-ResolveOwner`'s four-name
  "TRANSPORTS" allowlist, `pwsh.exe`, `powershell.exe`, `cmd.exe`,
  `conhost.exe`. Whether dropping 5.1 requires removing `powershell.exe`
  from that allowlist depends on whether any process could still present
  as `powershell.exe` in a PS7-only world (e.g. a leftover 5.1 install on
  a user machine) — a question about the *environment* the code runs in,
  not about the line itself.
- `skills/multi-model-verify/references/backup-lane.md:111` — the prose
  documenting that same four-name transparent-hosts list. Same
  undeterminable-from-the-line reason as above.
- `tools/kimi-lane-lock.ps1:887` — `$script:TransparentHosts =
  @("pwsh.exe", "powershell.exe", "cmd.exe", "conhost.exe")`, the actual
  list. Same reason: whether `"powershell.exe"` must be removed depends on
  whether the ancestry walk can still legitimately meet that name after a
  5.1 drop, which this line does not answer.

### What this method cannot see

- **The versioned plugin cache copy of `hooks/hooks.json`.** That copy,
  not the checkout, is what actually runs, and it only changes on a
  version bump plus `plugin update`. The survey reads tracked checkout
  files; it cannot see whether the installed cache has drifted from them.
- **An already-registered scheduled task.** `tools/check-drift.ps1
  -Register` writes the host into the task's action string at
  registration time; a task registered before a code change keeps running
  the OLD action until someone re-registers it. The survey reads source,
  not the Windows Task Scheduler.
- **Any instruction a human or agent follows that is not written in a
  tracked file.** A verbally-relayed or memory-carried instruction to run
  something under a specific host leaves no line for the survey to match.
- **Any file listed as `NOT SCANNED` by the survey, by name.** This run
  reports `0 files not scanned`, so there is currently none to name; a
  future run that cannot read or decode a tracked file would list it here
  instead of counting it clean.
- **A classification that is syntactically valid and semantically
  wrong.** The survey enforces that every match has a row and that the
  row's digest matches the current line; it has no way to check that the
  chosen classification is the CORRECT one for what the line does.
- **Anything UNTRACKED.** `git ls-files` lists tracked files only, so a
  generated or `.gitignore`d file is invisible to the scan. The
  auto-triage wrapper scripts under `tools/drift-reports/` are the live
  example: they invoke a client and are not in the index, so no run of
  this survey will ever see them.
- **A shape the filter does not match at all, so no row exists and this
  record cannot list it as `must-change`.** `--emit` only ever offers a
  row for a DETECTED match; a shape none of the three families' regexes
  catch leaves nothing to classify and nothing to sweep for. Named
  instance: `README.md:412`,
  `powershell tools/check-drift.ps1            # one-shot` — the first
  line of the SAME fenced block whose next two lines, `:413` and `:414`,
  ARE in the inventory as `must-change` (they end in a flag, which the
  `bare` family's `.ps1` alternative requires; `:412` ends in a `#`
  comment instead, so no alternative matches it). It invokes 5.1 by name
  and a migration would have to edit it exactly like its two neighbours.
  `survey.py` was NOT widened to catch this shape: every count in this
  task was measured against the filter as it stands, and widening it now
  would invalidate all 1114 hand-written rows and this whole inventory.
  The plan's own remedy for a known miss is to NAME it, as this bullet
  and the bare-`git` bullet below both do, not to chase it into the
  filter. Consequence stated plainly: the `must-change` count above (83)
  is therefore known to be deflated by at least this one instance.
- **A bare `git` invocation, deliberately.** Matching bare `git` was
  measured to cost 179 further hits, almost all prose and shell plumbing,
  against a class that never starts a PowerShell host — a measured trade,
  not an empty set. Its instance is named in `survey.py`'s own comment:
  `tools/check-drift.ps1:987`.

This list is not itself provably complete, and a blind-spot list that
reads as complete is the same defect one level up. The count is not
restated here from memory or from this instruction; it is copied from the
single place that carries it, `survey.py`'s own FAMILIES comment:

> THE CORRECTIONS, enumerated. Across FIVE review rounds a reviewer
> produced a live entry point this filter did not match NINE times:
>   1-2. two classes prompted the third family at all;
>   3-4. two more widened it (call operator through a variable; flagless
>        instruction invocations);
>   5.   Start-Job joined the launch family;
>   6.   the line-wrapped backtick form;
>   7-8. the generic call operator with a literal command, and bare
>        `python`;
>   9.   bare `agy`, the Flash implementer's client - live at
>        agents/flash-implementer.md:47 and :78, and used across six
>        non-docs files.
>
> Nobody has produced a tenth. That is the only honest statement available,
> and it is not the same as saying there is none.
>
> ONE KNOWN MISS IS LEFT IN DELIBERATELY, with its instance named. Bare
> `git` invocations - tools/check-drift.ps1:987, `git -C $worktree commit`
> - are NOT matched. Matching bare `git` costs 179 further hits, almost all
> of them prose and shell plumbing, against a class that never starts a
> PowerShell host. That is a measured trade and not an empty set: the
> instance above is real and is not in the inventory.

## Measurement 1: re-exec fidelity

Measured by `<REC>/reexec/run.py`, which drives a PARENT script under one
host, has it forward its own arguments to a CHILD script under a NAMED
target host, and compares what each side actually received (as UTF-8 hex
dumps for the positional arm, as parsed JSON for the named arm) against
what was sent. Two stages: Stage A is what the PARENT received (the
control - if this is wrong, the probe measured nothing about forwarding).
Stage B is what the CHILD received after the parent forwarded (the
question). Two forwarding forms: `splat` (native `@args`/`@forward` through
the PowerShell call operator `&`) and `escaped` (the parent hand-builds a
quoted command-line string via an `Esc` function and starts the child
through `System.Diagnostics.ProcessStartInfo`). Two argument shapes:
positional (`$args`, ten hostile strings) and named (three parameters,
one holding an embedded quote and an em dash, another holding spaces and
a trailing backslash). Eight arms in total. Full output verbatim in
`<REC>/reexec/results.json`.

**Stage A never failed.** Every one of the 8 arms shows
`stage_a_parent_exact: true` - the parent always received exactly what
`run.py` sent it, so every stage B result below is measuring forwarding,
not a broken control. (If the parent did not receive what was sent,
nothing downstream is measurable, so this means the task does not stop
early; had any Stage A been false the task would have reported BLOCKED
instead of writing this section.)

`first difference` for the named shape names the first PARAMETER NAME, in
ALPHABETICAL order over the union of expected and received keys
(`run.py:164-166`), that differs - not send order. `routeNote` was sent
first and also differed for `ps51/splat/named`; `path` sorts first
alphabetically, which is why it is the name shown.

| host | form | shape | return code | child ran | stage A exact | stage B exact | first difference |
|---|---|---|---|---|---|---|---|
| ps51 | splat | positional | 0 | yes | true | **false** | index 2 (`has"quote`) |
| ps51 | splat | named | 0 | yes | true | **false** | `path` |
| ps51 | escaped | positional | 0 | yes | true | true | none |
| ps51 | escaped | named | 0 | yes | true | true | none |
| pwsh7 | splat | positional | 0 | yes | true | true | none |
| pwsh7 | splat | named | 0 | yes | true | true | none |
| pwsh7 | escaped | positional | 0 | yes | true | true | none |
| pwsh7 | escaped | named | 0 | yes | true | true | none |

"child ran" is `stage_b_child_count is not None` for every arm - every
child wrote its output file, including the two corrupted arms. That
matters because it means the two `false` rows are a CORRUPTION finding,
not a never-started child: `ps51/splat/positional`'s child received only 8
of the 10 sent items (`stage_b_child_count: 8` against `sent_count: 10`),
and `ps51/splat/named`'s child bound all three parameters but with wrong
values - `routeNote` lost its embedded quotes (`a "quoted" note — here`
arrived as `a quoted note — here`) and `path`'s trailing backslash is
gone, with a quote standing in its place (`C:\dir with space\` arrived as
`C:\dir with space"`). What produced that substitution is not recorded by
this run - `results.json` holds the observation, not a cause, and no
mechanism is asserted here.

**Positional payload, verbatim (`PAYLOAD` in run.py):**

```
"plain"
"has space"
'has"quote'
'odd"quote"count"'
"em\u2014dash"
""
"trailing\\"
"semi;colon &amp"
"$var and `backtick`"
"-looks-like-a-flag"
```

**Named payload, verbatim (`NAMED` sent / `NAMED_EXPECTED` bound, in run.py):**

```
NAMED = ["-Register", "-RouteNote", 'a "quoted" note \u2014 here',
         "-Path", "C:\\dir with space\\"]
NAMED_EXPECTED = {"register": True,
                  "routeNote": 'a "quoted" note \u2014 here',
                  "path": "C:\\dir with space\\"}
```

**Answer to the NO-criterion.** A 5.1 script CAN re-exec into PowerShell 7
with these argument shapes intact - but only under the ESCAPED forwarding
form (a hand-built, hand-quoted command-line string passed through
`ProcessStartInfo`), never under the native `@args`/`@forward` SPLAT form.
Under Windows PowerShell 5.1, splat corrupted both the positional payload
(the child received 8 of 10 items and the first index that differs is 2;
which two items were dropped is not recorded by this run - the positional
arm keeps no per-item child data on the success path, by design, per
`run.py:201-204`) and the named payload (an embedded quote and a trailing
backslash both mangled). The escaped form survived every payload shape
under BOTH parent hosts, and PowerShell 7 as the PARENT host survived
every payload shape under BOTH forwarding forms. The CHILD host was
PowerShell 7 in every one of the eight arms - `run.py:63` and `run.py:112`
pin `PROBE_TARGET_HOST` to `PWSH` unconditionally - so no arm measured
PowerShell 5.1 as a target; the corruption is specific to 5.1 acting as
the SPLAT-forwarding parent, not to PowerShell 7 as a target, and not to
escaping as a technique.

**Width of the evidence.** This measured ten positional payload shapes and
one named-parameter set (three parameters, one holding an embedded quote
and an em dash, another holding spaces and a trailing backslash) - not
arbitrary arguments. Item 48's NO-criterion asks about arguments passing through
"provably intact"; what is proved here is that these eleven shapes survive
under the escaped form and that the same eleven shapes do NOT all survive
under 5.1's native splat form. It does not establish that EVERY possible
argument string survives the escaped form, only that this hostile set -
spaces, quotes, an odd quote count, an em dash, an empty string, a
trailing backslash, a semicolon and ampersand, a dollar sign and
backtick, and a leading-dash flag-like token - does.

**Residual limits, named:**

- **Command-line length.** Not measured against the ~32767-character
  Windows command-line ceiling; every payload item here is short. A
  migration relying on the escaped form for a very large brief (the kind
  `multi-model-verify` sends) is not covered by this measurement.
- **The host's own `-File` parsing.** This measured the escaped form and
  the splat form end-to-end - through the target host's own `-File`
  argument parsing, not isolated from it - so a stage-A pass and a
  stage-B fail together localize the corruption to what happens BETWEEN
  the parent's command-line construction and the CHILD host's own
  argument binding; this measurement cannot further separate "the parent
  built a bad command line" from "the child host's `-File` parsing
  mangled a well-formed one" beyond what `parent_bound`/`child_bound` in
  `results.json` show for the named arm.
- **Parameter shapes not tried.** Arrays, `ValueFromRemainingArguments`,
  and a script that re-execs ITSELF (rather than a sibling script) were
  not measured.
- **One machine, one build of each host.** All eight arms ran on this one
  machine against exactly one installed build of each host: Windows
  PowerShell `5.1.26100.9168` and PowerShell `7.6.5`, captured by running
  `$PSVersionTable.PSVersion.ToString()` under each of the two absolute
  paths `run.py:22-23` pins. Neither host's build is recorded inside
  `results.json` itself. These match the two versions captured
  independently by Task 1 for the record's own header (line 5), so the
  two measurements agree rather than diverge. This measurement says
  nothing about a different build of either host, or a second machine.

## Measurement 2: is PowerShell 7 present

Answers the blunt question under one of the four pre-committed NO-criteria
("any entry point that cannot be made to reach 7") for the four places this
code has to run: the Windows CI runner, the Linux CI runner, a developer
machine, and a plugin user's machine. Only the developer machine (this one)
is directly observable; the other three are evidenced differently, and each
subsection below says which.

**What the workflow file declares (`.github/workflows/skill-evals.yml`),
working tree read via
`grep -n "runs-on\|shell:\|pwsh\|powershell" .github/workflows/skill-evals.yml`:**
`:17` `runs-on: ubuntu-latest`; `:53`, `:55` comment prose mentioning
`pwsh`/`powershell.exe`; `:59` `powershell-hosts:`; `:60`
`runs-on: windows-latest`; `:74`, `:75`, `:78`, `:80`, `:87`, `:91` more
comment prose; `:95` `PARALLAX_PS_HOST: powershell.exe`; `:112`
`PARALLAX_PS_HOST: pwsh.exe`. No `shell:` key appears anywhere in the file
(the grep for it produced zero hits).

### Windows CI runner

Evidence, not declaration: `gh run list --workflow skill-evals.yml --limit 5
--json databaseId,headSha,status,conclusion,createdAt` (run 2026-08-22)
returned the most recent successful run as `databaseId 32391262449`,
`headSha a3134dcd76d9253057bf24935f3d7a7eef8eb0e4`, `conclusion: success`,
`createdAt: 2026-08-20T16:18:35Z` — that SHA is the same commit this
record's own header (line 4) names as the branch cut point.
`gh run view 32391262449 --json jobs --jq '.jobs[] | {name, conclusion,
startedAt, completedAt, runnerName}'` returned the `powershell-hosts` job
with `conclusion: success`, `startedAt: 2026-08-20T16:19:31Z`,
`completedAt: 2026-08-20T17:05:16Z`. (`runnerName` came back `null` for
both jobs — GitHub-hosted runners do not report a runner name through this
field; that is a property of the API, not evidence of anything about the
runner.)

A green `powershell-hosts` job, `runs-on: windows-latest`, whose two steps
(`skill-evals.yml:93-108` and `:110-125`) set `PARALLAX_PS_HOST:
powershell.exe` and `PARALLAX_PS_HOST: pwsh.exe` respectively and then run
`python -m pytest` against the same eleven `evals/multi-model-verify/`
modules, is direct evidence that a `pwsh.exe` host existed and worked on
`windows-latest` for run `32391262449` on 2026-08-20 — not merely a green
job that a self-skipping module could have produced the same way with no
host at all: one of those eleven modules, `test_lock_protocol_live.py`,
calls `required_hosts()`, which `## Measurement 3` (`:1463`-`:1471`
below) documents as the only host-selector in this repo that FAILS rather
than skips when a host is missing, making a pass of that module the
strongest host-presence evidence this record has, not just a green
conclusion taken at face value. This proves PowerShell 7 was present and
functional on that one runner image on
that one date; it does not prove every future `windows-latest` image
carries it, only that the image GitHub served for this run did.

**Revision binding.** `gh run view 32391262449 --json headSha --jq
'.headSha'` returned `a3134dcd76d9253057bf24935f3d7a7eef8eb0e4`. That SHA
exists locally (`git cat-file -e` succeeded), so `git show
a3134dcd76d9253057bf24935f3d7a7eef8eb0e4:.github/workflows/skill-evals.yml
| grep -n "runs-on\|shell:\|pwsh\|powershell"` was run directly (not the
working tree read as a stand-in) and returned the identical line numbers
and text as the working-tree read above — no drift. This is not a
coincidence to be glossed over: the working tree happens to sit at that
same commit right now, but the comparison was still made against the
commit's own blob via `git show`, not assumed from the tree matching by
name.

### Linux CI runner

`awk '/^  skill-evals:/{f=1} f&&/^  [a-z-]+:/&&!/^  skill-evals:/{exit}
f{print NR": "$0}' .github/workflows/skill-evals.yml | grep
"pwsh\|powershell\|shell:\|run:"` was run over the WHOLE `skill-evals:`
job (`skill-evals.yml:16-47`), not just the lines after `runs-on`. It
returned five `run:` step headers (`:28`, `:36`, `:39`, `:42`, `:45`), none
of which contain `pwsh` or `powershell`, plus two more hits at `:53` and
`:55`. Both of those are comment lines (`#  lock that read every lock as
unusable on pwsh...` and `#  powershell.exe when both are installed...`),
part of the prose block at `:49-58` that explains why the `powershell-hosts`
job below exists — not invocations. So: **zero steps in the `ubuntu-latest`
job invoke `pwsh` or `powershell`.**

PowerShell 7's presence on the `ubuntu-latest` Linux runner is **unproven by
this repo's own evidence.** Nothing in this workflow starts a PowerShell
host on Linux, so there is no green job to point at the way there is for
Windows. What would prove it: a Linux CI step that runs `pwsh -Command
'$PSVersionTable.PSVersion'` (or equivalent) and captures a real version
string, the way `powershell-hosts` does for Windows.

### Developer machine (this one)

Measured directly. `where.exe pwsh` returned two paths: `C:\Program
Files\PowerShell\7\pwsh.exe` and
`C:\Users\Brandon\AppData\Local\Microsoft\WindowsApps\pwsh.exe`. Then
`"C:\Program Files\PowerShell\7\pwsh.exe" -NoProfile -Command
"$PSVersionTable.PSVersion.ToString()"` returned `7.6.5` — matching the
`7.6.5` already captured in this record's header (line 5) and re-captured
independently by Task 4. PowerShell 7 is present and working on this
machine, absolute path confirmed.

### Plugin user's machine

Not measurable at all from here — no telemetry, no fleet, no way to run a
command on a machine this session cannot reach.

**The half-requirement that already exists regardless of any migration:**
`hooks/hooks.json:10` and `:22` (both rows present in
`entry-points.tsv:159-160` (`host` family) and `:424-425` (`launch`
family), classified `host-pin-exec` / `launch-explicit`, `no-change`) each
invoke `"command": "pwsh -NoProfile -NonInteractive -File
\"${CLAUDE_PLUGIN_ROOT}/hooks/superpowers-review-companion.ps1\""`. Any
plugin user who has the hook installed and enabled already needs `pwsh` on
PATH today, before any 5.1-removal work — this is a fact about the repo as
it stands, not a claim about any user's machine.

**The preinstall claim**, in the cited form the brief requires (background
knowledge is not an acceptable substitute for a claim this specific):
Microsoft's own installation documentation, `Install PowerShell 7 on
Windows`, https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell-on-windows
(read 2026-08-22), states: "PowerShell 7 doesn't replace Windows PowerShell
5.1. It installs to a new directory and runs side-by-side with Windows
PowerShell 5.1," and, describing the Start Menu entries left after
installing PowerShell 7: "The first and last entries shown are for Windows
PowerShell 5.1, which are installed by default on Windows." Read together,
Windows PowerShell 5.1 ships by default and PowerShell 7 is a separate,
opt-in install (WinGet, MSI, MSIX, ZIP, or `dotnet tool`) that a user or an
administrator has to add. So a plugin user's machine having `pwsh` present
is **unproven** for any given machine, and per this citation is **not the
default state** of a stock Windows install; it is present only where
someone installed it. What would additionally prove it for a *specific*
fleet: a device inventory or telemetry report showing `pwsh.exe` present
across the actual population of plugin users, which this measurement does
not have access to.

## Measurement 3: behaviour under 7

Answers which host-sensitive behaviours already shipped in this repo are
KNOWN to work under PowerShell 7, versus which are only declared to. Item
48's own warning is precise about the shortcut this measurement must not
take: "Not 'does it start'. 0.16.0's lock STARTED fine on 7 and did not
lock." So this section maps COVERAGE - which modules actually invoke which
script as a process, and whether that invocation sits inside a run that is
known to have passed under `pwsh.exe` - and does not re-run the suite
itself.

### Step 1: the dual-host CI job's module list

`.github/workflows/skill-evals.yml:59` opens job `powershell-hosts`,
`runs-on: windows-latest`. Two steps run the SAME eleven-module list, once
per host: `:93` "PowerShell-facing tests under Windows PowerShell 5.1"
(`:95` `PARALLAX_PS_HOST: powershell.exe`, modules at `:98`-`:108`), then
`:110` "PowerShell-facing tests under PowerShell 7" (`:112`
`PARALLAX_PS_HOST: pwsh.exe`, modules at `:115`-`:125`). Both step bodies
list the identical eleven modules, verbatim:
`test_attestation.py`, `test_codex_context_probe.py`,
`test_codex_tool_surface_probe.py`, `test_review_mirror.py`,
`test_kimi_round_evidence.py`, `test_kimi_lane_lock.py`,
`test_lock_protocol_live.py`, `test_kimi_credential_state.py`,
`test_kimi_lane_login.py`, `test_kimi_lane_home.py`,
`test_lane_credential_live_support.py`. Selection is a hand-written list
in the workflow file, not a glob - the job's own comment at `:73`-`:92`
states the intent ("EVERY dual-host module, not just the lock") but
nothing enforces the list is exhaustive.

**Revision binding.** Task 5 bound its cited green run
(`32391262449`/job `96497936725`, `conclusion: success`) to
`headSha a3134dcd76d9253057bf24935f3d7a7eef8eb0e4`, which this record's own
header (line 4) names as this branch's cut point.
`git show a3134dcd76d9253057bf24935f3d7a7eef8eb0e4:.github/workflows/skill-evals.yml`
read directly (not the working tree as a stand-in) and re-filtered the same
way as above returned line-for-line identical step names and module lists
to the working-tree read. So the module list above is the one that SHA's
run actually exercised, not a working-tree list paired with a run from
elsewhere. Re-pulling the job's own log directly
(`gh run view --job 96497936725 --log`, run just now, not copied from the
dispatch note) confirms real execution rather than a skip: `773 passed in
1363.25s` under `PARALLAX_PS_HOST: powershell.exe`, then `773 passed in
1356.53s` under `PARALLAX_PS_HOST: pwsh.exe`, both steps' shell reported as
`C:\Program Files\PowerShell\7\pwsh.EXE` (the Actions runner's own shell,
not the env var the tests select internally). Both lines are BARE `773
passed` - no `skipped` or `deselected` count on either side, which pytest
prints whenever either is nonzero - so a wholesale skip on one host cannot
have produced this output; both invocations actually ran and passed the
identical 773 items.

**Module-level revision binding.** `git diff --name-only
a3134dcd76d9253057bf24935f3d7a7eef8eb0e4..HEAD -- evals/ tools/ hooks/
.githooks/` returns EMPTY output. So every `path:line` citation in the
rest of this section against those four directories - not only the
workflow file checked above - is safe to read against today's working
tree: nothing under any of them has changed since the cited run's commit.

### Step 2: shipped scripts and which are covered

**Pattern used**, run exactly:
`git ls-files 'tools/*.ps1' '.githooks/*' 'evals/tools/*.ps1' 'hooks/*.ps1'`.
This returns **16** files (counted from the command's own output, not
assumed). `hooks/*.ps1` is in the glob deliberately - it is what catches
`hooks/superpowers-review-companion.ps1`, missing from an earlier draft's
hand-written glob, and the checkout's `hooks/hooks.json:10`/`:22` invoke it
as bare `pwsh`.

**Exclusions, named.** A repo-wide `git ls-files '*.ps1'` returns 21
files. Of the 16 entries the four-glob command above returns, only 15
carry a `.ps1` extension - the 16th, `.githooks/pre-push`, has none - so
the excluded `.ps1` set is 21 minus 15, **6 files**, not 5 (an earlier
draft of this section subtracted 5, treating `.githooks/pre-push` as if
it were one of the 21):
- `docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/reexec/{child,child-named,parent,parent-named}.ps1`
  (4 files) - this investigation's OWN measurement harness, built by an
  earlier task in this same plan to produce Measurement 1. Scratch for the
  feasibility record, not shipped product surface a user, hook, or CI job
  invokes.
- `evals/multi-model-verify/fixtures/stub-appserver/stub-appserver.ps1` -
  a test double standing in for an external app server INSIDE the test
  suite, not a script the product ships to run in production. (Its sibling
  `stub-appserver.cmd` already has its own `must-change` row in
  `entry-points.tsv:70`/`:220` for hardcoding `powershell.exe`, so this
  exclusion is not hiding that finding, only scoping THIS table to scripts
  under the four brief-named directories.)
- `evals/multi-model-verify/fixtures/stub-codex/stub-codex.ps1` - the same
  kind of test double, standing in for the codex CLI inside the test
  suite rather than a script the product ships to run in production. It
  DOES appear in the repo-wide `*.ps1` listing (an earlier draft of this
  section said it did not, which was wrong - it is line 6 of that
  listing); it is excluded for the same reason as `stub-appserver.ps1`,
  not because it is absent.

**Coverage table.** For each script, the covering module with the
STRONGEST evidence found (a `runs` row inside a dual-host-job module, where
one exists); citations are `path:line`. "In dual-host job" means the
covering module is one of the eleven from Step 1.

| script | covering module | classification (cite) | in dual-host job |
|---|---|---|---|
| `tools/codex-context-probe.ps1` | `test_codex_context_probe.py` | runs (`:24` `PROBE`, invoked at `:375` via `ps_host()`) | yes |
| `tools/codex-tool-surface-probe.ps1` | `test_codex_tool_surface_probe.py` | runs (`:36` `PROBE`, invoked at `:137`) | yes |
| `tools/kimi-lane-lock.ps1` | `test_kimi_lane_lock.py`, `test_kimi_lane_home.py`, `test_kimi_lane_login.py`, `test_lock_protocol_live.py`, `test_lane_credential_live_support.py` | runs (`test_kimi_lane_lock.py:83,91,599`; `test_kimi_lane_home.py:347,356,369`; `test_kimi_lane_login.py:259`; `test_lock_protocol_live.py:103`; `test_lane_credential_live_support.py:129` calling `evals/tools/lane_credential_live_support.py:163-165 resolve_owner`) | yes (all five) |
| `tools/new-kimi-lane-home.ps1` | `test_kimi_lane_home.py` | runs (`:30` `BUILDER`, copied then invoked at `:702`,`:710`) | yes |
| `tools/new-kimi-lane-login.ps1` | `test_kimi_lane_login.py` | runs (`:31` `SCRIPT`, copied then invoked at `:356`,`:364`) | yes |
| `tools/new-review-mirror.ps1` | `test_review_mirror.py` | runs (`:20` `MIRROR`, invoked at `:118` via `ps_host()`) | yes |
| `tools/read-kimi-credential-state.ps1` | `test_kimi_credential_state.py` | runs (`:56` `VALIDATOR`, invoked at `:104` via `ps_host()`) | yes |
| `tools/read-kimi-round-evidence.ps1` | `test_kimi_round_evidence.py` | runs (`:55` `SCRIPT`, invoked at `:241`,`:257`) | yes |
| `tools/verify-attestation.ps1` | `test_attestation.py` | runs (`:26` `VERIFY`, invoked at `:91` via `run_ps`) | yes |
| `tools/write-attestation.ps1` | `test_attestation.py` | runs (`:25` `WRITE`, invoked at `:81`) | yes |
| `hooks/superpowers-review-companion.ps1` | `test_multi_model_verify.py` | runs (`:22` `HOOK_SCRIPT`, invoked at `:2269` - hardcoded `shutil.which("pwsh")`, always host 7, never selector-driven) | **no** - this module is not one of the eleven; it runs only inside Tier 2b (`skill-evals.yml:44`-`:47`, `ubuntu-latest`), gated by a skip if `pwsh` is absent there, which this task did not check |
| `tools/read-codex-round-evidence.ps1` | `test_codex_round_evidence.py` | runs (`:55` `SCRIPT`, invoked at `:245`,`:254`) | **no** - module not in the eleven |
| `tools/plant-home-skill-canary.ps1` | `test_home_skill_canary.py` | runs (`:48` `TOOL`, invoked at `:93` via `ps_host()`) | **no** - module not in the eleven |
| `tools/check-drift.ps1` | `test_backup_lane.py` (`reads` only - `:1181` `DRIFT`, text asserted at `:1187`,`:1205`,`:1216`,`:1237`, never executed; NOT a dual-host module - `grep -c "test_backup_lane" .github/workflows/skill-evals.yml` returns `0`); `evals/tools/drift_statemachine_tests.ps1` (`runs` - `:120`-`:121` `Copy-Item`/`$DriftScript`, but this IS the local-only harness itself) | reads (non-dual-host module) / runs (non-CI harness) | **no**, and stronger than merely gated off: `test_multi_model_verify.py:2957`-`:2959` gates the harness invocation behind `PARALLAX_STATEMACHINE` (unset in both CI jobs), and the invocation itself (`:2961`) hardcodes `"powershell.exe"`. `tools/check-drift.ps1:406`-`:408` states outright "the rest of the harness still drives 5.1 only (backlog item 41); that one scenario names its host rather than the harness changing hosts" - and that one PS7-naming scenario, `agy-allow-depth-over-boundary` (`drift_statemachine_tests.ps1:1283`), SKIPS ITSELF when `pwsh.exe` is absent (`:1275`). `check-drift.ps1` has no PowerShell 7 execution path at all, in CI or locally, except one opt-in scenario that can skip itself. |
| `evals/tools/drift_statemachine_tests.ps1` | `test_multi_model_verify.py` | runs (`:2903` builds the path, executed under the `PARALLAX_STATEMACHINE`-gated test at `:2957`-`:2959`) | **no** - gated off in both CI jobs; local-only per this repo's own README/CLAUDE.md, opt-in |
| `.githooks/pre-push` | `test_attestation.py` | mentions only (`:5`,`:29` - docstring/comment naming what the hook calls; no module anywhere invokes `.githooks/pre-push` itself as a process) | **no** - no `runs` row exists for this script in the whole repo, on any host |

**Count: 10 of 16 shipped scripts have a `runs` row inside a module that
is one of the eleven the dual-host CI job runs; 6 do not** (one of the 6,
`check-drift.ps1`, has a `runs` row, but only inside a harness the CI jobs
never turn on). Per the width-of-evidence rule this record uses throughout
(Measurement 1, Measurement 2): a `runs` row says the module invokes the
script, not that the invocation passed. What the green run cited above
(`32391262449`/`96497936725`, headSha bound above) adds is the passing
half, for the ten scripts whose covering module is in that job's list -
`773 passed` under `pwsh.exe` covers all eleven modules' test functions
together, not scored per script.

### Step 3: the five named traps, coverage under 7

Backlog item 48's own list, `docs/superpowers/plans/2026-07-27-0150-backlog.md:3456`-`:3470`,
copied here as the fixed set to check, each against whether a test
exercises the SAME behaviour under 7:

1. **`ConvertTo-Json` truncates silently at the default depth; 7 warns
   (0.24.0).** Mitigated in shipped code by hardcoding `-Depth 100` /
   `-Depth 3` (`tools/check-drift.ps1:205,765,1242`), with the rationale at
   `:376`-`:407` ("measured on both hosts rather than argued... an
   over-boundary scenario naming pwsh.exe"). But `:406`-`:408` of that same
   comment says plainly "the rest of the harness still drives 5.1 only
   (backlog item 41)": the only harness that drives this scenario live is
   `evals/tools/drift_statemachine_tests.ps1`, gated behind
   `PARALLAX_STATEMACHINE` (`test_multi_model_verify.py:2957`-`:2959`,
   whose invocation is itself hardcoded to `"powershell.exe"` at `:2961`),
   unset in both CI jobs - and even inside that opt-in harness, the one
   scenario that names `pwsh.exe`, `agy-allow-depth-over-boundary`
   (`drift_statemachine_tests.ps1:1283`), SKIPS ITSELF when `pwsh.exe` is
   absent (`:1275`). **No coverage under 7** in any run this task can point
   to; the comment's "measured on both hosts" describes a past manual/local
   measurement, not a CI-repeatable one.
2. **A no-BOM file reads with the ANSI code page and `$OutputEncoding`
   defaults to us-ascii, flattening an em dash (0.23.0).** Tested by
   `TestBriefEncodingOverStdin` in `test_multi_model_verify.py` (four
   `@pytest.mark.skipif(os.name != "nt", ...)` cases at `:3029`,`:3042`,
   `:3060`,`:3093`), whose `_run` helper (`:2986`-`:3000`) hardcodes
   `"powershell.exe"` at `:2999` as the literal interpreter - never
   selector-driven, never `pwsh`. **No coverage under 7**: every assertion
   about this behaviour is made against 5.1 only. Whether PowerShell 7 (which
   defaults `$OutputEncoding` to UTF-8, per this repo's own CLAUDE.md prose)
   needs or already avoids the same mitigation is asserted in comments and
   documentation, not exercised by a test against `pwsh` here.
3. **Native argument splatting strips embedded double quotes without
   changing the argument count (0.21.0, item 20).** Covered: `##
   Measurement 1: re-exec fidelity` in THIS record, produced by Task 4, ran
   this exact class of corruption under both hosts as PARENT. The
   `pwsh7/splat/positional` and `pwsh7/splat/named` rows both show
   `stage B exact: true` - PowerShell 7 as the splatting parent forwarded
   every hostile shape (embedded quotes, trailing backslash, em dash,
   semicolon/ampersand) intact. This is a direct measurement in this same
   investigation, not a shipped pytest module.
4. **`ConvertFrom-Json` throws at about 100 nested levels; 7 accepts far
   more (0.24.0).** Same gating as trap 1: the only live scenario is inside
   `evals/tools/drift_statemachine_tests.ps1`, behind
   `PARALLAX_STATEMACHINE`, never set in CI. `tools/check-drift.ps1:387`-
   `:407`'s comment states an "over-boundary scenario naming pwsh.exe"
   exists in that harness - the `agy-allow-depth-over-boundary` scenario at
   `drift_statemachine_tests.ps1:1283` - but that scenario SKIPS ITSELF
   when `pwsh.exe` is absent (`:1275`), and the harness does not run in
   either CI job regardless. **No coverage under 7** evidenced by a run
   this task can cite.
5. **The tool-surface probe built the process's stdin from
   `Console.InputEncoding` and put a byte-order mark on the first JSON-RPC
   frame, rejected by the app server - broken on 5.1 only.** Covered:
   `test_codex_tool_surface_probe.py:514`
   `test_the_first_frame_reaches_the_server_with_no_byte_order_mark`, whose
   class docstring (`:510`) states "it drives EVERY host present" - line
   `:515` builds the host list from `shutil.which("powershell")` AND
   `shutil.which("pwsh")` and asserts a clean run for each host found. This
   module IS one of the eleven dual-host-job modules, so the green run
   cited above covers this behaviour under `pwsh.exe` directly.

**Beyond item 48's five: other host-sensitive behaviours found while
reading these scripts.** Item 48's own list is not presented as
exhaustive - `docs/superpowers/plans/2026-07-27-0150-backlog.md:3485`-
`:3490` treats its own entry-point count as "a claim, not a fact" and
records rounds that kept finding more. Reading the 16 shipped scripts for
Steps 1-2 surfaced three more host-sensitive behaviours; recording them
here rather than silently narrowing the search to the five names already
given:

a. **Native stderr promoted to a terminating error.**
   `tools/new-kimi-lane-home.ps1:671`-`:679`: "Windows PowerShell 5.1 turns
   ANY native-command stderr line into a terminating `NativeCommandError`
   under `$ErrorActionPreference = "Stop"`, even when that stderr is being
   captured rather than displayed - so the preference is relaxed for just
   this call and restored immediately after" - a shipped save/restore
   workaround (`:678`-`:679`,`:695`,`:699`). CLAUDE.md carries the same
   rule for the codex-dispatch scripts, so this is a recurring class, not
   a one-off. Its covering module, `test_kimi_lane_home.py`, IS one of the
   eleven and this code path runs on every home build the tests do under
   `pwsh` in the cited green run - but no assertion in that module measures
   whether PowerShell 7 exhibits the same stderr-promotion behaviour.
   Verdict: **exercised, divergence not measured**.
b. **Reparse-point traversal during a recursive directory walk.**
   `tools/plant-home-skill-canary.ps1:70`-`:73`: "Walk MANUALLY and never
   step through a reparse point. `Get-ChildItem -Recurse` follows junctions
   on some hosts, which would take this scan into whatever the junction
   aims at." Its only covering module, `test_home_skill_canary.py:93`, is
   outside the eleven (see this script's own row in Step 2's table).
   Verdict: **no coverage under 7** - neither the divergence itself nor the
   manual-walk mitigation is exercised by anything the dual-host job runs.
c. **`ConvertFrom-Json` returns `String` on 5.1 and `DateTime` on 7 for the
   same ISO-8601 timestamp.** `test_lock_protocol_live.py:379`-`:390`
   `test_measurement_20_ticks_and_date_string_types_diverge_across_hosts`
   measures this directly - the exact coercion behind the 0.16.0 lane lock
   that "did not lock" (`skill-evals.yml:50`-`:53`,
   `2026-07-27-0150-backlog.md:3473`-`:3477`). Its `required_hosts()`
   helper (`:77`-`:91`) is the only host-selection function found anywhere
   in this repo's test suite that FAILS rather than skips when a host is
   missing (`:83`-`:89`: "an unavailable host fails it rather than reading
   as a skip"), which makes a pass of this test the strongest single piece
   of host-presence evidence this record has found. Its module IS one of
   the eleven, so the cited green run covers it. Verdict: **covered under
   7** - and the coverage is BILATERAL: `required_hosts()` demands both
   `powershell.exe` and `pwsh.exe` by literal name, so this exact test
   cannot survive a 5.1 drop unmodified. That is not a coverage caveat, it
   is an asset a 5.1 drop destroys - flagged forward to `## Measurement 5:
   what is saved`, not resolved here.

These three are counted separately below, not folded into item 48's own
"2 of 5" tally, so the scope decision stays visible rather than being
silently absorbed either way.

**2 of item 48's 5 named traps (native-splat corruption, tool-surface-probe
stdin BOM) have real coverage of the same behaviour under PowerShell 7. 3
of 5 (JSON-depth truncation, em-dash/`$OutputEncoding` flattening, the
`ConvertFrom-Json` nesting-limit throw) have no coverage under 7 evidenced
by this task** - two because the only harness that exercises them is
gated off in both CI jobs (and, for the one scenario inside it that DOES
name `pwsh.exe`, self-skipping whenever `pwsh.exe` is absent), one because
the shipped test that guards the fix is written to run 5.1 only, by
design, and nothing here tests the pwsh side of that same claim. Counting
the three additional behaviours above alongside the five named traps: 3 of
8 host-sensitive behaviours this task identified are covered under 7
(traps 3 and 5, plus the Measurement-20 divergence); 5 of 8 are not (traps
1, 2 and 4, plus the reparse-point walk, plus the stderr-promotion
behaviour - the last one "exercised but not measured" rather than
untouched entirely).

### Summary

Of the 16 shipped PowerShell-facing scripts (derived mechanically from
`git ls-files 'tools/*.ps1' '.githooks/*' 'evals/tools/*.ps1' 'hooks/*.ps1'`,
6 further tracked `.ps1` files excluded and named above), 10 have a `runs`
row inside a module the dual-host CI job actually runs, and that job's most
recent green run at this branch's cut commit
(`32391262449`/`96497936725`, headSha `a3134dcd76d9253057bf24935f3d7a7eef8eb0e4`,
re-verified directly against the job log: `773 passed` under both
`powershell.exe` and `pwsh.exe`) is real evidence those ten scripts'
exercised behaviour passed under PowerShell 7, not merely a declaration.
The other 6 scripts have no `runs` row inside a dual-host-job module: three
(`hooks/superpowers-review-companion.ps1`, `read-codex-round-evidence.ps1`,
`plant-home-skill-canary.ps1`) run only in modules outside that job (one
gated by a `pwsh`-presence skip on `ubuntu-latest`, two invoked through
`ps_host()`/a raw host string this task did not resolve against either CI
job); two more
(`check-drift.ps1`, `drift_statemachine_tests.ps1`) are exercised only by a
harness both CI jobs leave switched off; and `.githooks/pre-push` has no
`runs` row anywhere in this repo, on either host. Of backlog item 48's five
named 5.1-specific traps, only 2 have coverage of the same behaviour class
actually exercised under 7 by a real, evidenced run; the other 3 are
"declared, not proven" under 7 - written up, reasoned about in comments,
in one case measured under this record's own Measurement 1, but not
covered by anything the dual-host CI job runs today. Three more
host-sensitive behaviours turned up beyond item 48's named five (native
stderr promotion, reparse-point traversal, and the Measurement-20
`ConvertFrom-Json` type divergence); one of those three is itself the
strongest single piece of coverage evidence in this whole record, and is
also the one asset a 5.1 drop would destroy outright - see Step 3 above
and the forward pointer to Measurement 5. No percentage is given for any
of these counts: the tables above are the width of what this task
measured, and a single number would claim more precision than 10-of-16
scripts, 2-of-5 named traps, or 3-of-8 total behaviours supports.

**Residual limits, named.**
- This section maps INVOCATION, per the interfaces the brief sets: a
  `runs` row is not a claim that the invoking module's assertions are
  correct, only that the script was actually started as a process by test
  code. Whether each assertion inside those ten modules is the RIGHT check
  is outside this task's scope, as it was outside Measurement 2's. Nor
  does this section claim the passing run's assertions match every
  classification in `entry-points.tsv` - that inventory classifies LINES,
  not test coverage, and this section does not re-derive it.
- The 6 uncovered scripts are not all equally unproven: `run_hook` in
  `test_multi_model_verify.py:2269` DOES invoke
  `superpowers-review-companion.ps1` under a real `pwsh`, just outside the
  dual-host job and gated by a presence skip this task did not resolve
  either way on `ubuntu-latest`. That is a narrower gap than
  `.githooks/pre-push`, which no test anywhere invokes.
- The three behaviours found beyond item 48's named five (Step 3, above)
  are not claimed to be the complete set of what a wider search would
  find; they are what this task's reading of the 16 shipped scripts
  surfaced, disclosed rather than dropped for not matching the five given
  names.
- This section did not independently re-verify whether `pwsh` is present
  on the `ubuntu-latest` runner that executes Tier 2b
  (`skill-evals.yml:44`-`:47`) or the module that hook test runs inside
  when it does. Measurement 2 already recorded that PowerShell 7's presence
  on the Linux runner is unproven by this repo's own evidence; this section
  does not contradict that, and does not attempt to resolve it.
- This section's `hooks/hooks.json:10`/`:22` citation (Step 2, `runs`
  classification for `hooks/superpowers-review-companion.ps1`) is scoped to
  the CHECKOUT, matching Measurement 2's own scoping. The versioned plugin
  cache copy actually installed was not inspected by this task either;
  Measurement 2 already names that gap in its own "half-requirement"
  paragraph, and this section does not re-measure or contradict it.

## Measurement 4: refusal when pwsh is missing

Attempted by `<REC>/missing-pwsh/probe.py`, which strips every `PATH` entry
containing `pwsh.exe` from a CHILD environment dict only (the real PATH,
this process's own `os.environ`, and the real `pwsh.exe` binary are never
touched - see `hooks/hooks.json:10` for the invocation shape reproduced,
already recorded in Measurement 2 as `no-change`) and then runs the hook's
own shipped shape - `pwsh -NoProfile -NonInteractive -File
hooks/superpowers-review-companion.ps1` - through that stripped
environment, with `stdin=subprocess.DEVNULL` and a 60-second timeout.

Outcome, named explicitly: the second of the three the task pre-named -
the call succeeded anyway. **Absence of PowerShell 7 was NOT reproduced by
this probe, and item 48's NO-criterion this measurement exists to answer
remains untested by it - see the closing note at the end of this
section.** Verbatim captured output
(`<REC>/missing-pwsh/results.json`, also printed to stdout by the run):

```
{
 "pwsh_on_real_path": "C:\\Program Files\\PowerShell\\7\\pwsh.EXE",
 "pwsh_after_stripping": null,
 "invocation": [
  "pwsh",
  "-NoProfile",
  "-NonInteractive",
  "-File",
  "C:\\Users\\Brandon\\Documents\\parallax\\hooks\\superpowers-review-companion.ps1"
 ],
 "returncode": 0,
 "stdout": "",
 "stderr": ""
}
```

`pwsh_after_stripping` came back `null` - `shutil.which("pwsh",
path=env["PATH"])`, resolving directly against the stripped PATH string
inside THIS process, found nothing, so the strip itself was not the
failure. But the actual `subprocess.run(["pwsh", ...], env=env)` call still
started `pwsh` and it exited `0`. This was checked further, not just
accepted: a `cmd /c "echo %PATH% & where pwsh"` launched through the same
stripped `env` dict shows the CHILD's own `%PATH%` correctly excludes both
`C:\Program Files\PowerShell\7` and
`C:\Users\Brandon\AppData\Local\Microsoft\WindowsApps`, and that child's
own `where pwsh`, searching ITS OWN received environment, genuinely fails
(`INFO: Could not find files for the given pattern(s)`, returncode 1).

The command run (a Python one-liner reusing `probe.py`'s own
`stripped_path()`) and its full verbatim captured output, not merely a
characterisation of it:

```
env = dict(os.environ); env["PATH"] = stripped_path()
proc = subprocess.run(["cmd", "/c", "echo %PATH% & where pwsh"],
                      capture_output=True, text=True, env=env)
```

```
RETURNCODE: 1
---STDOUT---
C:\Users\Brandon\bin;C:\Program Files\Git\mingw64\bin;C:\Program Files\Git\usr\local\bin;C:\Program Files\Git\usr\bin;C:\Program Files\Git\usr\bin;C:\Program Files\Git\mingw64\bin;C:\Program Files\Git\usr\bin;C:\Users\Brandon\bin;C:\Users\Brandon\AppData\Roaming\Code\User\globalStorage\github.copilot-chat\debugCommand;C:\Users\Brandon\AppData\Roaming\Code\User\globalStorage\github.copilot-chat\copilotCli;C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;C:\WINDOWS\System32\WindowsPowerShell\v1.0;C:\WINDOWS\System32\OpenSSH;C:\Program Files\NVIDIA Corporation\NVIDIA App\NvDLISR;C:\Program Files (x86)\NVIDIA Corporation\PhysX\Common;C:\Program Files\Git\cmd;C:\Program Files\nodejs;C:\Users\Brandon\.kimi-code\bin;C:\Users\Brandon\AppData\Local\agy\bin;C:\Users\Brandon\Documents\WoW-Dev\lua51\bin;C:\Users\Brandon\AppData\Local\Microsoft\dotnet;C:\Users\Brandon\AppData\Roaming\luarocks\bin;C:\Users\Brandon\scoop\apps\mingw\current\bin;C:\Users\Brandon\scoop\persist\luarocks\rocks\bin;C:\Users\Brandon\scoop\shims;C:\Users\Brandon\AppData\Local\Programs\Python\Python312\Scripts;C:\Users\Brandon\AppData\Local\Programs\Python\Python312;C:\Users\Brandon\AppData\Local\Programs\Python\Launcher;C:\Users\Brandon\AppData\Local\Programs\Microsoft VS Code\bin;C:\Users\Brandon\AppData\Roaming\npm;C:\Users\Brandon\AppData\Local\Programs\luacheck;C:\Users\Brandon\.local\bin;C:\Users\Brandon\AppData\Local\Microsoft\WinGet\Packages\ajeetdsouza.zoxide_Microsoft.Winget.Source_8wekyb3d8bbwe;C:\Users\Brandon\.bun\bin;C:\Users\Brandon\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin;C:\Users\Brandon\AppData\Local\npm-global;C:\Users\Brandon\AppData\Local\Microsoft\WinGet\Packages\GitHub.cli_Microsoft.Winget.Source_8wekyb3d8bbwe\bin;C:\Users\Brandon\.dotnet\tools;C:\Users\Brandon\AppData\Local\Programs\Orca\resources\bin;C:\Program Files\Git\usr\bin\vendor_perl;C:\Program Files\Git\usr\bin\core_perl;C:\Users\Brandon\.claude\plugins\cache\claude-plugins-official\claude-md-management\1.0.0\bin;C:\Users\Brandon\.claude\plugins\cache\claude-plugins-official\security-guidance\2.0.7\bin;C:\Users\Brandon\.claude\plugins\cache\claude-plugins-official\superpowers\6.3.0\bin;C:\Users\Brandon\.claude\plugins\cache\claude-plugins-official\claude-code-setup\1.0.0\bin;C:\Users\Brandon\.claude\plugins\cache\openai-codex\codex\1.0.6\bin;C:\Users\Brandon\Documents\parallax\bin;C:\Users\Brandon\.claude\plugins\cache\claude-plugins-official\frontend-design\unknown\bin;C:\Users\Brandon\.claude\plugins\cache\i-have-adhd\i-have-adhd\0.2.0\bin;C:\Users\Brandon\.claude\plugins\cache\claude-plugins-official\code-simplifier\1.0.0\bin
---STDERR---
INFO: Could not find files for the given pattern(s).
```

Neither `PowerShell\7` nor `WindowsApps` appears anywhere in that printed
`%PATH%` line - confirmed by reading it, not merely asserted - which is
what makes the `where pwsh` failure on the next line direct rather than
coincidental. So the stripped environment IS what the new process receives
once it exists. What differs is resolving the bare executable NAME
`"pwsh"` to start that process in the first place: Windows resolves a bare
command name using the PARENT process's own environment for that search,
not the `env` dict handed to the child being created - exactly the outcome
the brief pre-named ("the process-creation call resolves it using the
PARENT process's environment, not the child environment being passed in").
This account is specific to the PATH search step of that resolution -
`CreateProcess` also checks the calling process's own directory, the
current directory, `System32`, and the Windows directory before it
consults PATH, and none of those were independently tried. They are ruled
out here only because both known copies of `pwsh.exe` on this machine
live exclusively in PATH-listed directories (`C:\Program
Files\PowerShell\7\` and the WindowsApps alias directory), neither of
which is the probe's own working/calling directory or a system directory
- that placement is the load-bearing elimination, not a direct test of
each of those other locations.

1. **Which outcome:** the call succeeded anyway (outcome 2 of 3). Not a
   failure and not a timeout.
2. **No failure text exists to report.** `returncode` is `0` and both
   `stdout` and `stderr` are empty. Absence of PowerShell 7 was **not
   reproduced** by this probe on this machine, so there is nothing to
   quote as "what a user would see," and no failure text is substituted
   here from a guess about what one would probably look like. Per the
   pre-named handling for this outcome: this is not read as evidence that
   the failure mode is benign, and the strip is not judged to have "failed"
   either - `pwsh_after_stripping: null` and the `cmd`/`where` check above
   both show the stripped environment was genuinely PATH-less for `pwsh`
   from the child's own point of view. What defeated the probe is a
   property of how the parent process asks Windows to CREATE the child
   when given a bare name, not a leak in the environment dict itself.
3. **Named residual limits:**
   - Only the bare-`pwsh` resolution path (as this repo's hook already
     invokes it, `hooks/hooks.json:10`/`:22`) was measured. Entry points
     that today name `powershell.exe` explicitly (the `must-change` rows
     in this record's inventory) were not probed here, since nothing about
     them changes until a migration edits them.
   - The harness's own presentation of a hook failure - what Claude Code's
     hook runner shows a user when a `PostToolUse`/`PostToolUseFailure`
     command hook errors - was not measured by this probe. This probe only
     captures what the OS-level child process produced. Nor was the
     runner's METHOD of resolving the bare name `pwsh` measured, and that
     is a separate thing from its presentation: this probe's own outcome
     was decided by Python's `subprocess.run` resolving a bare executable
     name against the PARENT's environment rather than the child's. If
     Claude Code's hook runner instead starts the command through a shell
     (rather than the same direct bare-name process-creation path Python
     used here), a shell-mediated resolution would consult the CHILD's own
     PATH - and the `cmd`/`where` cross-check above is direct evidence that
     resolution behaves differently in that case (it correctly failed
     against the same stripped environment). Which mechanism the real
     runner uses is not asserted here in either direction; this bullet
     names it as unmeasured rather than leaving the gap implicit.
   - **What this probe actually measured, and what it did not.** It proved
     that stripping `PATH` of every directory holding `pwsh.exe` does not,
     by itself, reproduce "PowerShell 7 is absent" on this machine when the
     caller names the executable barely (as the shipped hook does) via
     Python's `subprocess.run`. It did not measure the refusal message a
     user sees when `pwsh` is genuinely absent, because genuine absence was
     not achieved. What would prove it: a machine, container, or CI runner
     with PowerShell 7 genuinely not installed anywhere on it (no
     `Program Files\PowerShell\7`, no WindowsApps alias, no `App Paths`
     registry entry) - not a PATH-stripped child of a machine that has it.
   - This machine has two resolvable copies of `pwsh.exe`
     (`C:\Program Files\PowerShell\7\pwsh.exe` and
     `C:\Users\Brandon\AppData\Local\Microsoft\WindowsApps\pwsh.exe`, per
     Measurement 2's own `where.exe pwsh` output); both directories were
     confirmed stripped from the child's `PATH` string, and the outcome
     above still occurred, so a wider PATH search was not the gap here.

**Item 48's NO-criterion, left open.** This measurement therefore leaves
item 48's NO-criterion "a user-facing failure mode worse than the bugs
being removed" (see `## What would make the verdict NO` above) UNANSWERED,
and item 48's own requirement that the failure "must stop with a message
naming what to install" is UNTESTED by this task - no failure text was
produced to check that requirement against. `## Verdict` may not treat
this criterion as satisfied on the strength of this section; what would
answer it is named above (a machine, container, or CI runner with
PowerShell 7 genuinely not installed anywhere on it).

## Measurement 5: what is saved

Answers the brief's own question - what the change actually saves - against
the cost the earlier measurements have already surfaced. A section that
lists only savings is not a ledger; both sides are recorded here.

### Step 1: CI wall-clock, STEP timings not job timings

`gh run list --workflow skill-evals.yml --limit 10 --json
databaseId,conclusion,headSha,createdAt --jq '.[] | select(.conclusion==
"success")'` returned seven successful runs; the first five, newest first:
`32391262449` (2026-08-20), `32085653133` (2026-08-18), `32082761519`
(2026-08-18), `32078875878` (2026-08-17), `31956013509` (2026-08-16). These
differ from Measurement 2's cited run only by including four MORE runs
after it in the same list - `32391262449` is the same run Measurement 2
cites (`headSha a3134dcd...`), so the two sections do not disagree, they
just cover different windows of the same run history.

For each id, `gh run view <ID> --json jobs --jq '.jobs[] | select(.name==
"powershell-hosts") | {job: .name, jobStart: .startedAt, jobEnd:
.completedAt, steps: [.steps[] | select(.name | test("PowerShell-facing
tests under")) | {name, startedAt, completedAt}]}'` returned real
`startedAt`/`completedAt` timestamps for both named steps AND the job
itself, for all five runs - no run needed to be marked unmeasured. Per the
brief's own warning, the job total is shown ONLY as context (it also pays
for checkout, Python setup and pytest install, none of which a migration
removes); the two step columns are the load-bearing numbers.

| run id | date | `powershell-hosts` job | `...5.1` step | `...7` step |
|---|---|---|---|---|
| 32391262449 | 2026-08-20 | 45m45s | 22m44s | 22m37s |
| 32085653133 | 2026-08-18 | 46m05s | 22m56s | 22m39s |
| 32082761519 | 2026-08-18 | 43m29s | 20m58s | 21m40s |
| 32078875878 | 2026-08-17 | 46m41s | 23m25s | 22m56s |
| 31956013509 | 2026-08-16 | 45m07s | 22m46s | 22m01s |

**GROSS saving, as a range across these five runs, not one number:** the
5.1 step alone ran between **20m58s and 23m25s** (1258s-1405s) across the
five. That range - not a single averaged figure - is what dropping the 5.1
step removes from the `powershell-hosts` job on each of these five
occasions. It is a GROSS figure: it is what disappears from the job if the
5.1 step is deleted outright, not what disappears from a migration that
keeps some 5.1-starting cases.

**The NET saving is not determined by this task.** Item 48's own answer to
"what does the test matrix become" (`docs/superpowers/plans/2026-07-27-0150-backlog.md:3561`-
`:3563`) is "probably not 'one host' but 'one host plus a small number of
cases proving the refusal and the re-exec work when started from 5.1'."
Which cases those are, and how long they cost to keep running, is Task 9's
decision, not this one's. So: **the net saving is bounded above by the
gross range above (20m58s-23m25s per run of this job) and is not stated as
a number here.** Any sentence claiming a net figure at this point would
state as known something Task 9 has not yet decided.

### Step 2: the already-recorded local pair (cited, not re-measured)

Backlog item 48 itself records local timing evidence, gathered during the
0.27.0 gate, same tree and head, back to back:
`docs/superpowers/plans/2026-07-27-0150-backlog.md:3380`-`:3386` - `2558
passed, 14 skipped` in **32m23s** under Windows PowerShell 5.1 against
**18m33s** under `pwsh.exe`, and a second pair the same night, **20m22s**
against **18m50s**. Counts identical on both hosts both times. Item 48's
own caveat, carried forward rather than dropped: "the runs were not
isolated from other load, and the 5.1 spread (32m to 20m) is wider than the
gap itself" - so this pair is indicative, not a benchmark, and is cited
here rather than re-measured.

### Step 3: item 44's 57 minutes, GROSS upper bound only

Item 44 (`docs/superpowers/plans/2026-07-27-0150-backlog.md:3098`-`:3126`)
measured the gate's three serial passes - full pytest, then the
PowerShell-facing modules under 5.1, then the same modules under 7 - at
**1187s / 1153s / 1092s**, about **57 minutes** total, on the tree
committed as `99d1961`. The GROSS upper bound this change could remove from
that 57 minutes is the 5.1 pass's own duration: **1153s, about 19m13s**.
That is not a net figure: Task 9 has not yet decided which 5.1-starting
cases a migration keeps, and item 44's own "about 20 minutes instead" figure
(`:3105`-`:3108`) is about PARALLELIZING the three passes, a different
change from dropping one of them, so it is not substituted here either.

### Step 4: defects avoided (cited, not re-derived)

`docs/superpowers/plans/rounds/2026-08-22-item51-inline-brief-probe/probe-record.md`
measured two independent corruption defects in the Kimi lane's inline
brief transport, BOTH 5.1-only: Defect 1, the READ (`Get-Content -Raw`
decoding a no-BOM UTF-8 file with the ANSI code page, mangling non-ASCII
text) at `probe-record.md:75`-`:89`; Defect 2, the ARGUMENT (5.1 not
escaping embedded double quotes in a native argument, silently dropping
them when the count is balanced and SHATTERING the brief across multiple
argv elements when the count is odd) at `probe-record.md:91`-`:110`. Its
own summary table (`probe-record.md:67`-`:73`) shows every PowerShell-7
row exact and every corrupted row under 5.1. Dropping 5.1 removes both
defect classes outright, since PowerShell 7 was never the host on which
either fired. This is a real saving and it is already measured elsewhere;
it is cited here, not re-derived.

### Step 5: the edit cost (cited, not recounted)

The other side of "maintenance" - what this change costs to MAKE, as
opposed to what running two hosts costs going forward - is the entry point
inventory's own count, already recorded above (`## Entry point inventory`).
That section's own text, not restated from memory here: **"at least 83"**,
not a flat 83 - `feasibility-record.md:369`-`:370` states the count "is
therefore known to be deflated by at least this one instance" (the
`README.md:412` miss, named there), and `:377`-`:378` adds "this list is
not itself provably complete, and a blind-spot list that reads as complete
is the same defect one level up." So the figure carried into this ledger is
**at least 83 `must-change` rows, plus 3 further rows left `unknown`,
known-deflated and not provably complete** - the same discipline Step 2
above already applied to item 48's own timing caveat, applied here to the
edit-cost side.

### Step 6: the cost side - the bilateral test, verified against source

Measurement 3 flagged `evals/multi-model-verify/test_lock_protocol_live.py:379`-
`:390` forward to this section rather than resolving it itself. Verified
directly against the source, not taken from the forward pointer's
characterization.

**Correction to an earlier draft of this section, recorded rather than
silently fixed.** An earlier draft claimed this file's own `ps_host()`
"tolerates a missing host by skipping" and that `required_hosts()` "is the
only one in this repo that FAILS instead", then attributed a "single
strongest piece of host-presence evidence" superlative to the module
docstring. Both claims were checked against the source during this
fix-round and both are wrong:

- `ps_host()` itself (`:63`-`:74`) calls `pytest.fail` (`:69`-`:73`), not
  `pytest.skip`. Its own docstring says so directly: "A host that fails to
  resolve is a setup failure, not a reason to skip" (`:67`-`:68`).
- `test_lane_credential_live.py`'s `host()` fixture (`:54`-`:62`) also
  calls `pytest.fail` (`:57`-`:61`), under its own banner: "Every failure
  here is `pytest.fail`, never `pytest.skip`" (`:51`-`:52`).
- The "single strongest piece of host-presence evidence" line was this
  task's own judgment, presented as though the module docstring (`:14`-
  `:23`) said it. It does not; that docstring's own words are quoted above
  and say only that a resolvable-but-missing host is a FAILED measurement
  here, never a skipped one. Dropped rather than re-attributed, since it
  added a claim of comparative strength this task cannot actually rank
  against every other measurement in the record.

**The narrow claim that IS true, verified directly:** `required_hosts()`
(`:77`-`:91`) loops over the literal tuple `("powershell.exe", "pwsh.exe")`
(`:83`) and fails if EITHER is missing. `ps_host()` and `host()` above both
fail-hard too, but only when NO host resolves at all - either one of the
two suffices to satisfy them. `required_hosts()` is the only resolver
found in this repo that is not satisfied by a machine holding just one of
the two hosts; a machine with only `pwsh` on PATH, which is exactly what a
5.1 drop aims for, fails this specific gate by design.

- `test_measurement_20_ticks_and_date_string_types_diverge_across_hosts`
  (`:379`-`:390`) calls `required_hosts()` (`:380`), then runs the SAME
  script under `hosts["powershell.exe"]` and `hosts["pwsh.exe"]`
  (`:381`-`:382`) and asserts FOUR things: both hosts report `Int64` for
  the same tick value (`:387`-`:388`), and the two hosts report DIFFERENT
  `ConvertFrom-Json` types for the same date string - `String` on 5.1
  (`:389`), `DateTime` on 7 (`:390`).

**What a 5.1 drop actually destroys here, stated precisely rather than as
a blanket "destroyed."** Two of those four assertions are single-host
facts about PowerShell 7 that need nothing from 5.1 to keep asserting:
`assert pwsh_report["ticksType"] == "Int64"` (`:388`) and `assert
pwsh_report["whenType"] == "DateTime"` (`:390`). The fail-closed harness
that produces `pwsh_report` - `measure_type_report` (`:353`-`:377`) and
`TYPE_REPORT_SCRIPT` (`:344`-`:351`) - survives unchanged. A rewrite that
drops the `ps1_report` half keeps a genuine regression pin on the exact
`ConvertFrom-Json` coercion the lock code compensates for on the one host
that would remain. **What is actually destroyed, and cannot be edited
around, is narrower: the CROSS-HOST DIVERGENCE claim itself** - the
demonstration that the two hosts disagree, which by definition needs both
hosts to exist at once. That is still a real, uneditable loss; it is just
smaller than "the test's entire value."

**Is it the only one?** Searched four ways this round, not just re-read
the forward pointer - the fourth added after the first fix-round's sweep
was shown to miss a live instance:

1. `grep -rn "required_hosts\|diverge" evals/multi-model-verify/*.py
   evals/tools/*.py` - the only other hit inside this file is
   `test_measurement_20_a_failed_host_invocation_never_reads_as_divergence`
   (`test_lock_protocol_live.py:393`-`:400`), which ALSO calls
   `required_hosts()` and so is ALSO destroyed by a 5.1 drop as written -
   but its own assertion does not compare the two hosts' behaviour against
   each other: it forces `hosts["powershell.exe"]` to exit nonzero and
   checks that the measurement helper fails closed rather than reading an
   empty result as "the type differs" (`:398`-`:400`). Unlike the
   divergence test above, this one COULD be rewritten to exercise
   `pwsh.exe` instead without losing what it tests - its value comes from
   testing the fail-closed helper, not from comparing two hosts. So it
   shares the same fatal gate today but is not, itself, a bilateral asset.
2. The original co-occurrence script (function/class bodies containing
   BOTH literal `"powershell.exe"` and `"pwsh.exe"`) found: `check_host_parity`
   in `evals/tools/check_workflow_paths.py` (`REQUIRED_HOST_NAMES` at
   `:85`) and its unit tests `test_check_workflow_paths_flags_host_parity_gap`
   / `test_check_workflow_paths_refuses_a_duplicate_host_step`
   (`test_backup_lane.py`, already itemized in this record's own
   `must-change` list), plus `test_no_module_claims_ci_skips_the_windows_suites`
   (`test_backup_lane.py:1707`-`:1747`). All three require BOTH host NAMES
   to appear as declared steps in the CI workflow TEXT - a parity/coverage
   check on the YAML, not a live measurement of either host's runtime
   behaviour. These get REWRITTEN to require `pwsh.exe` alone, a cost
   already counted once in the edit-cost figure above, not a second,
   separate asset destroyed.
3. **Corrected sweep, this round.** The original script keyed only on the
   `"powershell.exe"` / `"pwsh.exe"` literal spellings. `gh`-independent
   re-run with the bare-name spelling too -
   `grep -rn 'which("powershell"\|which("pwsh"' evals/multi-model-verify/*.py
   evals/tools/*.py`, plus a repeat of the same function/class-body script
   checking `which("powershell")` and `which("pwsh")` co-occurrence - found
   one function this task had not previously flagged as bilateral:
   `TestTheFramesGoOutIntactOnBothHosts.test_the_first_frame_reaches_the_server_with_no_byte_order_mark`
   (`test_codex_tool_surface_probe.py:490`-`:529`). Its docstring
   (`:509`-`:511`) states its purpose outright: "This case is the one that
   does not depend on which host the suite happened to pick: it drives
   EVERY host present... a green suite on one host proves one
   interpreter." At `:515`-`:516` it builds `hosts = [h for h in
   (shutil.which("powershell"), shutil.which("pwsh")) if h]` and at
   `:521`-`:529` asserts the SAME clean verdict under each host present.
   Everything else the corrected sweep turned up under the bare spelling
   was the single-host `PARALLAX_PS_HOST or shutil.which("powershell") or
   shutil.which("pwsh")` OR-fallback selector, already named per-file in
   the `must-change` list - a preference chain that resolves to ONE host,
   not a comparison between two, so those are not added here.
4. No other `subprocess.run` call anywhere in the two directories was
   found comparing a result from one host against a result from the other
   within the same assertion, under either spelling.

**`TestTheFramesGoOutIntactOnBothHosts`, added to the cost side, and why
its shape differs from the divergence test.** Under the brief's own
definition - anything that asserts two hosts behave the same or
differently - this SAMENESS-form loop is bilateral too, even though it
never compares the two hosts' results TO EACH OTHER (each host's result is
checked against a fixed expectation, independently, inside the `for`
loop). Its host-resolution line (`:515`) is already one of the 83
`must-change` rows (Step 5's inventory: "`:40`, `:515` - the selector
fallback, and a test that explicitly resolves both `shutil.which
("powershell")` and `shutil.which("pwsh")` to drive every present host;
both must lose their 5.1 half"), so editing it is already priced once.
What is NOT already priced, and belongs here: unlike the parity checks in
item 2 above, editing this test to a single host does not just trim
prose - per its own docstring, its entire reason to exist is proving that
a green run on ONE host does not hide a defect that only shows up on the
OTHER (the BOM-on-first-frame defect at `:494`-`:507` is the exact case in
point: 5.1-only, and twenty single-host-green cases missed it). With one
host, the class of defect this test exists to catch - one worked, one
didn't, and the suite stayed green anyway - can never again be
demonstrated caught, because there is no longer a second host for the
defect to hide on. The assertion form survives an edit; the guarantee it
was built to provide does not.

**Reconciling the destroyed-asset bullet against the 83, so the two do not
silently overlap.** The `must-change` inventory already lists eight lines
inside `test_lock_protocol_live.py` as `must-change`: `:21`, `:55`, `:71`,
`:78`, `:83`, `:381`, `:382`, `:400` - all already inside the "at least 83"
counted in Step 5. Putting "one test destroyed outright" on the cost side
as a SEPARATE line item from the 83 would double-bill the same lines. It
is not separate. What Step 6 adds beyond the 83's flat edit count is a
CLASSIFICATION of what kind of edit those specific lines require: most of
the eight (`:21`, `:55`, `:71`, `:78`, `:83`, and the host-resolution calls
at `:381`-`:382`) are edited the same way every other selector-fallback
line in the inventory is - drop the 5.1 half, keep going. But `:381`-`:382`
feed the divergence assertion (`:389`-`:390` compared against `:387`-`:388`)
that this step already narrowed above: THAT comparison, specifically,
cannot survive any edit, no matter how the surrounding lines are rewritten
- because "these two things differ" has no one-host form. So this is not a
second destroyed asset on top of the 83; it is one finding, already
counted once by row, about what the edit at those particular rows costs
beyond a find-and-replace.

**Conclusion.** Two bilateral mechanisms were found and verified against
source this round, both already inside the 83 `must-change` rows by line
count, both adding something the flat row count does not itself say:
`test_measurement_20_ticks_and_date_string_types_diverge_across_hosts`
(`:379`-`:390`) loses its cross-host divergence claim outright while its
two pwsh-only assertions survive a rewrite; `TestTheFramesGoOutIntactOnBothHosts`
(`test_codex_tool_surface_probe.py:490`-`:529`) loses the guarantee that a
single-host-green suite cannot hide a host-specific defect, while its
assertion FORM survives a rewrite to one host. Everything else found
either (a) shares a fail-hard host-resolution gate without itself being a
cross-host comparison (item 1 above - destroyed as written, but rewritable
to test the same thing on one host), or (b) requires both host NAMES in
declared CI text, which the must-change list already prices as an edit,
not a destroyed asset (item 2 above).

### Ledger

**Saved.** These four figures measure overlapping wall-clock (a GitHub CI
job, a local full-suite pair, and a local three-pass gate all cover
substantially the same PowerShell-facing test runs from different angles)
and are deliberately never summed anywhere in this record. **They are not
additive** - adding, say, the 23m25s CI figure to the 19m13s item-44 figure
would double-count the same underlying test execution measured twice, on
two different machines, by two different methods:
- CI wall-clock: gross 20m58s-23m25s per run of the `powershell-hosts` job
  (Step 1), net not yet determined (bounded above by that range).
- The already-recorded local pair, 32m23s/18m33s and 20m22s/18m50s, cited
  with its own wider-spread caveat (Step 2).
- Item 44's structural 57-minute gate cost: a GROSS upper bound of about
  19m13s removable, not a net figure (Step 3).
- Two independent 5.1-only corruption defects in the Kimi lane's inline
  brief transport, removed outright (Step 4).

**Costs:**
- At least 83 `must-change` edit rows (plus 3 `unknown`), known-deflated
  and not provably complete per the inventory's own words, already counted
  once in `## Entry point inventory` (Step 5).
- Inside those rows, two bilateral mechanisms verified against source and
  classified rather than counted a second time (Step 6):
  `test_measurement_20_ticks_and_date_string_types_diverge_across_hosts`
  (`test_lock_protocol_live.py:379`-`:390`, rows `:21`,`:55`,`:71`,`:78`,
  `:83`,`:381`,`:382`,`:400` of the 83) loses its cross-host DIVERGENCE
  claim outright - no edit preserves "these two things differ" on one
  host - while its two pwsh-only type assertions (`:388`,`:390`) survive a
  rewrite as a regression pin. `TestTheFramesGoOutIntactOnBothHosts`
  (`test_codex_tool_surface_probe.py:490`-`:529`, row `:515` of the 83)
  loses the guarantee that a single-host-green suite cannot hide a
  host-specific defect (the exact BOM defect it was built to catch,
  `:494`-`:507`), while its assertion form survives a rewrite to one host.
- Measurement 4's NO-criterion - "a user-facing failure mode worse than the
  bugs being removed" - is UNANSWERED by this record (`## Measurement 4:
  refusal when pwsh is missing`, closing note), not merely uncosted; a
  verdict reader should weigh this ledger against an open question, not a
  cleared one.
- The retained-case set from item 48's own "one host plus a small number of
  cases" answer is not yet chosen (Task 9), so its ongoing cost is not
  priced here either.

## Residual limits

Every residual limit named by Tasks 3 through 8, gathered here BEFORE any
criterion in `## Verdict` above was adjudicated (Task 9 Step 2, ahead of
Step 4) — an earlier draft of this plan collected these after the verdict
was written, so the rule meant to force CONDITIONAL pointed at a list that
did not exist yet. Each item names the section it came from; nothing here
is re-derived.

### From `## Entry point inventory` (Task 3) — "What this method cannot see"

- The versioned plugin cache copy of `hooks/hooks.json`, not the checkout,
  is what actually runs; the survey cannot see whether the installed cache
  has drifted from it.
- An already-registered scheduled task keeps the host written into its
  action at registration time; the survey reads source, not Task
  Scheduler.
- Any instruction relayed verbally or from memory, never written to a
  tracked file, leaves no line for the survey to match.
- Any file the survey cannot read is listed `NOT SCANNED` by name (0
  today).
- A classification can be syntactically valid and semantically wrong; the
  survey checks that a row exists and its digest matches the current line,
  not that the chosen classification is correct.
- Anything untracked is invisible to `git ls-files` (named instance: the
  `tools/drift-reports/` auto-triage wrapper scripts).
- A shape none of the three regex families matches leaves no row at all
  (named instance: `README.md:412`), which is why the `must-change` count
  is "known to be deflated by at least this one instance."
- Bare `git` invocations are deliberately unmatched — a measured trade
  (179 further hits, almost all prose/plumbing), named instance
  `tools/check-drift.ps1:987`.

### From `## Measurement 1: re-exec fidelity` (Task 4)

- Command-line length was not measured against the ~32767-character
  Windows command-line ceiling; every tested payload item was short. A
  migration relying on the escaped form for a very large brief (the kind
  multi-model-verify sends) is not covered.
- The measurement ran end-to-end through the target host's own `-File`
  parsing, not isolated from it, so a stage-B corruption cannot be
  localized further than "between parent construction and child binding."
- Arrays, `ValueFromRemainingArguments`, and a script re-execing ITSELF
  (rather than a sibling script) were not tried.
- All eight arms ran on one machine, one build of each host (Windows
  PowerShell `5.1.26100.9168`, PowerShell `7.6.5`); a different build or a
  second machine is not covered.
- **Cross-task evidence narrows the command-line-length gap above, but
  does not close it (added in fix round 1).**
  `docs/superpowers/plans/rounds/2026-08-22-item51-inline-brief-probe/probe-record.md:139`-`:161`
  independently measured this SAME escaped/`Esc()` forwarding mechanism at
  much larger sizes, on both hosts: exact at 31995 characters, **throws**
  (`The filename or extension is too long`) at 32967 and 39933 —
  bracketing the Windows command-line ceiling at ~32767 characters. The
  failure is LOUD on both hosts identically, not silent corruption and not
  5.1-specific. That probe's own child was also a stub — a Python process
  recording `GetCommandLineW`, not the real `kimi.exe` — so, per its own
  residual list, "an intact command line is necessary, not proven
  sufficient." This is the same stub-child family of limit as this
  measurement's own harness (`<REC>/reexec/child.ps1` records what it
  received, not what any real downstream consumer would do with it).
  Named once here; `## Verdict`'s criterion 2 subsection and `## Draft:
  the migration item` step 6 both cite this bullet rather than
  re-deriving it.

### From `## Measurement 2: is PowerShell 7 present` (Task 5)

- PowerShell 7's presence on the Linux (`ubuntu-latest`) CI runner is
  unproven by this repo's own evidence — nothing in the workflow starts a
  PowerShell host there.
- PowerShell 7's presence on any plugin user's machine is not measurable
  at all from this session, and per Microsoft's own install documentation
  is NOT the default state of a stock Windows install.
- The green Windows CI run cited proves PowerShell 7 present on the runner
  image served for that one run on that one date, not that every future
  `windows-latest` image carries it.

### From `## Measurement 3: behaviour under 7` (Task 6)

- This section maps INVOCATION (a script was started as a process), not
  that the invoking module's assertions are the RIGHT check, and does not
  re-derive `entry-points.tsv`'s own classifications.
- The 6 uncovered scripts are not equally unproven:
  `superpowers-review-companion.ps1` runs under a real `pwsh` just outside
  the dual-host job (gated by an unresolved presence-skip on
  `ubuntu-latest`); `.githooks/pre-push` has no `runs` row anywhere, on
  any host.
- The three extra host-sensitive behaviours found beyond item 48's named
  five are not claimed to be the complete set a wider search would find.
- `pwsh` presence on `ubuntu-latest` for Tier 2b was not independently
  re-verified here (Measurement 2 already records it unproven); the
  `hooks/hooks.json` citation is scoped to the checkout — the installed
  plugin cache was not inspected.

### From `## Measurement 4: refusal when pwsh is missing` (Task 7)

- Only the bare-`pwsh` resolution path (as `hooks/hooks.json` already
  invokes it) was measured; entry points that today name `powershell.exe`
  explicitly were not probed.
- Claude Code's own hook-runner presentation of a failure, and its METHOD
  of resolving a bare name (direct process-creation vs. shell-mediated),
  were not measured.
- The probe did not reproduce genuine absence of PowerShell 7 on this
  machine (two resolvable copies exist); what would prove it is a machine,
  container, or CI runner with PowerShell 7 genuinely not installed
  anywhere.
- **Item 48's NO-criterion "a user-facing failure mode worse than the bugs
  being removed" is UNANSWERED by this record** — stated in bold at the
  section's own close, and carried forward here as an open question rather
  than a cleared one.

### From `## Measurement 5: what is saved` (Task 8)

- The four saved-time figures (CI wall-clock, the local pair, item 44's
  57-minute gate, the two corruption defects) are deliberately never
  summed; they measure overlapping wall-clock by different methods.
- CI wall-clock is a 5-run sample, not isolated from other load; the local
  pair carries the same caveat, wider than the gap itself.
- Item 44's ~19m13s figure is a GROSS upper bound only; the NET saving is
  not determined by Measurement 5 and is explicitly left to this task's
  decision on the retained test set.
- The edit cost is "at least 83" `must-change` rows plus 3 further
  `unknown` rows, known-deflated and not provably complete, not a flat
  count.
- The bilateral-mechanism sweep (tests comparing both hosts) was run four
  ways this round but is not claimed exhaustive.
- The retained 5.1-starting case set (item 48's "one host plus a small
  number of cases" guess) was not yet chosen when Measurement 5 was
  written, so its ongoing cost was not priced there — `## Verdict`'s
  `### What the test matrix becomes` above is where that gets decided as
  far as the evidence allows.

### Of the investigation as a whole

- One machine throughout (this developer machine), one build of each host
  (Windows PowerShell `5.1.26100.9168`, PowerShell `7.6.5`).
- One ANSI code page (this machine's own) for every code-page-sensitive
  measurement — the em-dash/`$OutputEncoding` trap is untested against
  `pwsh` at all (Measurement 3 Step 3, trap 2), and no other code page was
  tried anywhere in this record.
- One Claude Code version (this session's), not varied against any floor
  this repo's CLAUDE.md names for other lanes.
- No script in this repo was run under a migration it does not yet have —
  every measurement above ran against the CURRENT, unmigrated code.
  Nothing in this record observes the actual edited entry points behaving
  post-migration.

### This task's own closing gate (Step 6), for the record

Not new evidence about any of item 48's four criteria — the full `evals`
suite, re-run once per host after this record was otherwise finished, to
confirm nothing above broke what already passed. Windows PowerShell 5.1:
`2558 passed, 14 skipped, 5 warnings in 1153.61s (0:19:13)`. PowerShell 7:
`2558 passed, 14 skipped in 1115.16s (0:18:35)`. Identical pass and skip
counts on both hosts; zero `FAILED` lines in either log. The 5.1 run's 5
warnings are `PytestWarning: (rm_rf) unknown function <built-in function
scandir>` / `PermissionError: [WinError 5]` teardown noise from
`test_an_unreadable_source_path0`, a test that deliberately makes a path
unreadable; the pwsh7 run reports none. That is a real, if immaterial, host
difference in teardown noise — recorded here rather than dropped, not
claimed to bear on any criterion above.

## Draft: the migration item

Drafted because `## Verdict` above is CONDITIONAL, per Task 9 Step 5. This
is a DRAFT only — it is not added to
`docs/superpowers/plans/2026-07-27-0150-backlog.md` by this task; that edit
happens at merge, not here.

**Problem.** This repo runs its PowerShell-facing code and tests on two
hosts, Windows PowerShell 5.1 and PowerShell 7, even though 5.1 is where
every measured PowerShell-hosting defect in this repo's history has fired
(`## Measurement 5: what is saved`, Step 4: two independent corruption
defects in the Kimi lane's inline brief transport, both 5.1-only). This
record's own entry-point survey found at least 83 rows that pin, invoke,
or document 5.1 specifically and would need to change to drop it
(`## Entry point inventory`). Backlog items 51 (`docs/superpowers/plans/
2026-07-27-0150-backlog.md:3748`, the Kimi lane's inline brief mangled by
5.1) and 31 (`docs/superpowers/plans/2026-07-27-0150-backlog.md:2510`, the
drift autofix dispatch's `Get-Content -Raw | codex exec` degrading on 5.1's
ANSI code page) are both instances of this same 5.1-only defect class and
are absorbed by this item rather than fixed independently.

**What would close it.** This record's verdict is CONDITIONAL, not YES: the
five open conditions named in `## Verdict` above (the `$TransparentHosts`
allowlist rows and the unproven pwsh-presence environments; the
unreproduced pwsh-missing refusal; the final retained test set, including
the not-yet-exhaustive bilateral sweep and the two further coverage-
confidence gaps added in fix round 2; the escaped-form command-line
ceiling; and the Windows CI runner's proof being scoped to one run, also
added in fix round 2) must be resolved before or as part of this work, not
skipped. As a
hard ordering rule, taken from item 48 itself: **the code becomes UNABLE to
run on 5.1 BEFORE any 5.1 test is deleted.** Pinning the tests without
pinning the code first is the one outcome this item may not produce (the
same lesson 0.16.0's own history already argues for — a suite green on one
interpreter proves one interpreter, not both).

**Ordered work**, consistent with `### What the test matrix becomes` above
without restating it:

1. Resolve the five open verdict conditions first, since later steps
   depend on their answers: decide the `$TransparentHosts` allowlist rows
   (`tools/kimi-lane-lock.ps1:887` and its two doc/test siblings); prove
   PowerShell 7 present on the Linux (`ubuntu-latest`) CI runner and
   establish what fraction of plugin users actually have it (Measurement 2
   found both unproven); confirm PowerShell 7's presence on the Windows CI
   runner holds durably rather than on the one run and date this record
   actually observed (`32391262449`, 2026-08-20) — a repeated check across
   several `windows-latest` runs over time, not a single cited run, is what
   would settle condition (5); measure a genuine pwsh-missing refusal on a
   machine, container, or CI runner that truly lacks PowerShell 7, and
   confirm it stops with a message naming what to install (item 48's own
   requirement); use that failure text to write the retained "refusal"
   test case Measurement 4 could not specify.
2. Build the retained "re-exec" test case from the technique Measurement 1
   already proved — the escaped forwarding form, not native splat — as a
   shipped, kept test (not scratch), asserting fidelity for a 5.1-starting
   parent. Size it against the ~32000-character command-line ceiling this
   record's own item-51 probe bracketed (`## Verdict`, criterion 2): if the
   real payload a migrated re-exec would carry can approach that ceiling,
   this step must also decide the fallback transport, not just the
   in-bounds case.
3. Re-point every `must-change` row in the entry-point inventory at
   `pwsh`, in the order the inventory already groups them (host pins,
   launch pins, bare invocations, docs), re-running `survey.py` after each
   group to confirm no row is missed and none goes stale.
4. Before this step, close condition (3)'s three sub-parts, not only the
   bilateral sweep (the same gap fix round 3 found and fixed for condition
   (5) in step 1, above): re-run the bilateral-mechanism sweep that
   `## Measurement 5` Step 6 ran four ways (not claimed exhaustive) at
   least once more, with a fifth method, to close the open question
   whether `test_measurement_20_ticks_and_date_string_types_diverge_
   across_hosts` and `TestTheFramesGoOutIntactOnBothHosts` are the
   COMPLETE bilateral set; audit whether the coverage table's ten covering
   modules (`## Measurement 3` Step 2) actually assert the RIGHT behaviour
   rather than merely invoking the script, widening the retained set for
   any that do not; and decide whether `.githooks/pre-push` — proven on NO
   host today, on either side of a migration — needs its own retained case
   alongside the re-exec and refusal ones from step 1. Only once steps 1-3
   leave the code UNABLE to
   run on 5.1 (every `must-change` row repinned, the refusal and re-exec
   cases proven under the new shape) AND the bilateral sweep above is
   settled: retire `test_measurement_20_ticks_and_date_string_
   types_diverge_across_hosts`'s cross-host divergence assertion (its two
   pwsh-only type assertions survive as a rewritten regression pin, per
   `## Measurement 5`, Step 6), rewrite `TestTheFramesGoOutIntactOnBothHosts`
   to run `pwsh` alone (accepting the loss of its one-host-hides-a-defect
   guarantee), and remove the `powershell-hosts` CI job's 5.1 step
   (`.github/workflows/skill-evals.yml:93`-`:108`) and every other 5.1-only
   test named `must-change` in the inventory. No 5.1 test is deleted before
   step 4, and no test is deleted at all until the code it exercises is
   already unable to run on 5.1.
5. Re-time the CI job (or its replacement) once the final retained set from
   steps 1-2 exists, to answer the NET saving `## Measurement 5`
   deliberately left undetermined.
6. **Item 31 and item 51 close differently — corrected in fix round 1.**
   Item 31 is closed by construction once step 3 is complete:
   `tools/check-drift.ps1` inherits its host from whatever launches it
   (the scheduled task's registered action, `tools/check-drift.ps1:96`
   above), so once every entry point capable of starting it is repinned to
   `pwsh`, its `Get-Content -Raw` read at `:1060` decodes on pwsh's UTF-8
   default rather than the ANSI code page, and the defect no longer fires.
   Item 51 is NOT closed by construction the same way. The Kimi lane's
   inline brief transport WAS independently measured this cycle
   (`docs/superpowers/plans/rounds/2026-08-22-item51-inline-brief-probe/probe-record.md`
   — measured, not merely reported, despite the stale "REPORTED, NOT
   MEASURED HERE" heading still standing at
   `docs/superpowers/plans/2026-07-27-0150-backlog.md:3750`, which this
   task does not edit), and that probe found the fix is the escaped
   `Esc()` forwarding form — exactly the technique step 2 above already
   builds into the retained re-exec test, not merely "stop running on
   5.1." That same probe measured a further limit, the same stub-child
   family as `## Verdict` criterion 2's residual above: its child was a
   Python stub, not the real `kimi.exe`, so an intact command line there
   is proven necessary, not proven sufficient. Closing item 51 requires
   confirming the real client too, which neither this record nor "no
   longer runs under 5.1" alone establishes.

**Priority.** Medium-high, unchanged from item 48's own assessment: it
gates a large cleanup, retires the single largest source of measured
defects in this repo, and makes item 44 smaller — but it is CONDITIONAL,
not ready to execute as scoped, until the five open conditions in
`## Verdict` above are resolved.
