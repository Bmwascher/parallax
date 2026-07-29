Panel round 2 (your round 10). Subject revision unchanged and FINAL:
base `e2e9242c6153d69e9a4f0c49055e7bf8c81a1dd0`,
head `50c82029f178c747467e5a597b281731f70e4188`.

Another lane raised two findings against the head you just passed. You do
not learn which lane. Both are relayed with their evidence. I verified
both against the repo myself before relaying; my verification notes are
marked DRIVER.

Your round-9 reply said "No false-clean measurement path found." Finding
A is a claimed counterexample to exactly that. Attack it properly: your
job is to REFUTE it if it is wrong, and to say plainly that you missed it
if it is right.

## Finding A — the second pass discards its own ProjectDoc measurement

Claim: `Test-PromptShape` computes an instruction report and returns it
(`tools/codex-context-probe.ps1:461`, `:485`). The `ProjectDoc` fact is
acted on for pass 1 only (`:619-622`). The pass-2 call voids the return
value: `[void](Test-PromptShape $text2 $Json)` at `:667`.

The function's own comment at `:457-460` states the rule it is meant to
enforce: every shape rule applies to BOTH renders, because "a block
appearing only under the generated override ... passed silently."
ProjectDoc is such a rule, and it is not applied to pass 2.

Consequence claimed: a `--- project-doc ---` delimiter present only in
the suppression-pass render reaches `status: clean`, exit 0, while
SKILL.md's clean-probe contract (`skills/multi-model-verify/SKILL.md:150-152`)
says clean means "no instruction source sits inside the reviewed tree."

Trigger claimed to be narrow: both renders come from the same workdir
seconds apart, so a reviewed-tree `AGENTS.md` would have to appear
between the two codex calls. The repo-scoped-skills analogue is closed
structurally, because pass 2 requires the skills block ABSENT (`:673-677`).

DRIVER: I read `:619-622`, `:667`, and `:456-486`. The code is as
described. `$instructions` at `:619` is bound from the pass-1 call, and
nothing rebinds it after `:667`.

Questions for you:
1. Is the consequence real, or is there a path I have not read that
   blocks a pass-2-only project doc anyway?
2. Is the narrow trigger the only trigger? Consider a first pass whose
   project-doc block is absent for a reason OTHER than the file being
   absent, and consider whether the generated override itself can change
   what the second render reports.
3. Is the proposed minimal fix correct and sufficient: capture pass 2's
   report and block on `ProjectDoc`, mirroring `:619-622`? State any
   ordering or message consequence.
4. Should the check instead move INSIDE `Test-PromptShape` so it cannot
   be forgotten again? Say what that would change about pass-1 block
   ORDERING and whether any pinned test depends on that order.

## Finding B — git path quoting defeats remediation and the manifest

Claim: neither the back-channel enumeration
(`tools/new-review-mirror.ps1:39`, `git ls-files --cached --others`) nor
the baseline capture (`:62`, `git status --porcelain --ignored -uall`)
sets `core.quotepath=false`. Git's default quotes non-ASCII paths with
C-style octal escapes.

Consequence claimed: a back-channel or baseline entry with a non-ASCII
path arrives quoted. `Join-Path` / `Test-Path` at `:237-238` then miss
the real file, the entry survives remediation, and the run BLOCKS at
`:279-283` with "back-channel(s) survived remediation" — or the manifest
blocks at `:123`. Direction is fail-closed, so this is a legitimate-run
rejection with a misleading message, not a safety defect.

The other lane marked the git-quoting premise INFERRED because it could
not run git.

DRIVER: I ran it. In a scratch repo containing `café/AGENTS.md`:
- `git ls-files --cached --others '*AGENTS.md'` printed
  `"caf\303\251/AGENTS.md"`
- the same command with `-c core.quotepath=false` printed
  `café/AGENTS.md`
- `git status --porcelain --ignored -uall` printed
  `?? "caf\303\251/AGENTS.md"`
The premise is CONFIRMED, not inferred.

Questions for you:
5. Is the fail-closed direction claim correct at every affected site, or
   is there any site where a quoted path silently passes instead of
   blocking? Check the baseline, the manifest, the tracked/untracked
   branch at `:236`, and the directory pruning at `:243-249`.
6. `-c core.quotepath=false` makes git emit raw UTF-8 bytes. This repo
   runs BOTH PowerShell hosts (`PARALLAX_PS_HOST`), and I found no
   `[Console]::OutputEncoding` handling anywhere in
   `tools/new-review-mirror.ps1`. Does the flag alone fix this on
   Windows PowerShell 5.1, or does it trade an octal-escape bug for a
   mojibake bug? Name the change that is correct on both hosts.
7. Is there a fix that avoids the encoding question entirely?

## Reply format

Per finding: CONFIRMED or REFUTED, with `path:line` evidence, then the
minimal correct fix. Then answer the numbered questions. Then restate
your terminal verdict against the head above: PASS, FIX, or ESCALATE.
Anything you did not check goes under `## Unverified`.
