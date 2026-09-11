# Fable closing adjudication, 2026-09-11

Seat: `parallax:fable-reviewer` (Claude, in-harness), asked one
question at head `58035af` after six diff-debate exchanges: authorize a
seventh round, merge now, or merge with the residual guard questions
treated as their own subject. The session leaned toward the third. The
reply is retained verbatim; the session verified the one code claim in it
(three call sites at `new-review-mirror.ps1:1429`, `:1856`, `:1900`)
before acting on it.

---

**Recommendation: option 3, with one change to its shape. Merge now. Do not spend round 7 of this debate on the guard, and do not make the guard's next step a read-only reviewer round at all.**

**Is the trend converging?** Split the question. On the branch's subject it converged in round 1: claim 1 survived a full trace (diff-debate.md:44-46) and every later round re-verified prior fixes as holding (129-143, 563-565). On the guard it is not converging, it is diverging in scope: the 8.3 regex was wrong in rounds 3, 4, 5 and 6 (245-250, 333-343, 409-417, 545-552), and round 6 opened a new class (wildcard globbing, 519-527) that no earlier round was looking for. "Every round found something" here means the guard is a spelling-comparison design being fuzzed one alias at a time, and item 99 already states that no spelling rule closes that class (BACKLOG.md:4335-4341). A seventh round would be paid quota to re-prove a written-down theorem.

**Does the months-old defect argue for more rounds?** For fewer on this debate, more on a differently-shaped piece of work. The tool is less sound than assumed, yes, but the sound fix is the design change item 99 names (resolve to identity or restrict), not regex attempt six.

**Is merging unsafe?** No. Every guard change is a tightening plus `-LiteralPath`; main still holds the trailing-dot bypass and the wildcard substitution. Every regex error on this branch failed in the refusing direction (usability), never the accepting direction. The only unreviewed surface is the round-6 fix commits themselves, and this branch's history says this side's fixes are usually wrong somewhere, so state that plainly in the record. One instance I checked: the "ONE HELPER, called by every operand" claim (new-review-mirror.ps1:1302-1309, diff-debate.md:220-224) ships as a subject list plus three separate call sites (1423-1429, 1856, 1900), which is the same shape the comment says is the defect. Not unsafe; a record overclaim of the class rounds 4-6 kept finding.

**Fourth option, and I would take it.** The record shows three reviewers could not run the decisive experiments from a read-only session (345-347, 455-458, BACKLOG.md:4327-4333). Items 98 and 99 both name a measurement nobody has made. So the guard's next spend should be the session running those two experiments (`fsutil setshortname` alias, real removal denial), then a design decision, then a debate on that. A read-only round 7 is the wrong instrument for what remains.

Options 2 and 3 are not exclusive: merge, and write the record exactly as option 2 says it (ended by budget, subject clean five rounds, round-6 fixes unreviewed).

---

**Disposition:** taken as written. The helper comment corrected at
`5a7e1e5`; the closing section of `diff-debate.md` written in option 2's
terms; items 98 and 99 named as where the guards' next spend goes.
