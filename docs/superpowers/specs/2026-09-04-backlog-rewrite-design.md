# Backlog rewrite and maintenance enforcement - design

Date: 2026-09-04. Decided in conversation with the user; every choice
below is the user's or was presented and approved.

## Problem

`docs/superpowers/plans/2026-07-27-0150-backlog.md` is 5,905 lines and
holds three hand-written views of the same facts: each item's heading, a
status block, and a ranked build order. Every close edits one view and
forgets the others. Measured on 2026-09-04 by a full read of the file:

- entry 1 of the ranking says "Ranked second";
- entries 2 to 4 argue from evidence their own items superseded on
  2026-09-03 and 04;
- half of item 35's defect is closed by construction in 0.28.0 and its
  text does not say which half;
- five of the eleven stated pairings are written from one side only, one
  names a closed partner (27 with 19), and one pairs items in different
  files (54 with 51);
- two findings from item 74's close have no owning item, and a third
  belongs to item 34 without item 34 saying so;
- about a third of the ranking's prose is history of its own renumbering.

Nothing enforces that a session returns to the file when work completes,
and nothing checks the file's shape. The repo has measured three times
(item 59) that a rule enforced only by remembering it is skipped.

## Goals

1. One source of truth per fact. The status view and the ranking are
   derived from the items, never written separately. The checker proves
   the ranking cannot omit an open item, list one twice, or carry prose
   that goes stale; whether an item's POSITION agrees with its Cost line
   stays a human judgement, reviewed by a person and never by the tool.
2. A session that changes governed surfaces is stopped ONCE with a
   reminder to re-attest the owning backlog item. A push to main from a
   clone with the hook installed is refused without such a
   re-attestation in the same range. A push from a clone without the
   hook, or a merge made in the GitHub interface, is DETECTED by CI on
   arrival and fails the job; it is not prevented, because prevention
   needs a repository ruleset that is not in this tree (see 3d).
3. The file's shape is checked mechanically after every direct edit,
   before the session stops, in the gate, and at push.
4. Open work is what a reader lands on; closed history is short and
   points at the retained records.

## Non-goals

- Judging whether a ranking is RIGHT. The checker proves the ranking is
  complete, consistent and current; the order itself is a human call.
- Changing the shipped plugin. Every hook here is repo-maintenance
  tooling in project scope, not in `hooks/hooks.json`.
- Editing retained round records under `docs/superpowers/plans/rounds/`.

## Part 1: the file

`BACKLOG.md` at the repository root. Three sections in this order.

### 1a. Preamble

Under fifteen lines. States that headers are the source of truth, that
the ranking is an ordered list and nothing else, that closing an item
means editing its header and deleting its ranking line, and that
`evals/tools/backlog_lint.py` enforces all of it. It names no counts and
no dates about the file itself (item 70's convention).

### 1b. Ranking

The preamble, not this section, states that the ranking is ordered,
that groups are labels rather than tiers, that order within and across
groups is the build order, and that the case for a place is the item's
Cost line. The section itself holds nothing but group headers and ids:

```
## Ranking

### First - breaks the repo's own review process
- 75
- 49
...
### Last - housekeeping and open questions
- 61
```

Rules: one item id per line, no position numbers, no text after the id,
no text between a header and its ids. A group header is `### ` followed
by at most eight words. Closing an item deletes its line and nothing
else moves.

### 1c. Items

Every item opens with a fixed header block, then its body.

```
## 75. The review mirror deletes authoritative policy
Status: OPEN
Cost: the reviewer certifies a transcription of a policy, and no gate can see it
Pairs: none
Verified: 2026-09-04 3f1c9a0b7e2d
```

The digest shown is illustrative; the tool prints the real one.

Field contract:

- `Status`: exactly one of `OPEN`, `PARTIAL`, `DONE`, `GONE`. Nothing
  else, no suffixes.
- `Closed`: present if and only if Status is `DONE` or `GONE`. A version
  string such as `0.29.0`, or `record` for an investigation closed on a
  record rather than a release, or `superseded` for GONE.
- `Cost`: one line, required for `OPEN` and `PARTIAL`, absent otherwise.
  What it costs NOW, not why it is interesting.
- `Pairs`: `none`, or a comma-separated list of item ids. Required for
  `OPEN` and `PARTIAL`. Every named item must name this one back.
- `Verified`: an ISO date, a space, and the first 12 hex characters of
  the SHA-256 of the item's canonical content. Canonical content is
  built byte-exactly as follows, so the working tree and a git object
  digest the same: decode as UTF-8; fold CRLF to LF; take the heading
  line, every header line except the `Verified` line, and every body
  line up to the line before the next `## ` heading; strip trailing
  ASCII space (U+0020) and tab (U+0009) from each line and nothing
  else; drop trailing blank lines; join with a single LF; append LF,
  then `group:`, then the group header text AFTER the `### ` prefix
  with its own trailing spaces and tabs stripped, then LF; encode as
  UTF-8 and hash. Fixtures pin each decision: a line ending in a
  non-breaking space (U+00A0) must digest differently from one that
  does not, a header written `###   Name  ` must digest as `Name`, and
  the same item from a CRLF working copy and from `--revision` must
  digest equal. Required on every
  item. The tool prints the expected value on a mismatch so the field
  is refreshed by an explicit act per item rather than by a date that
  happens to be today. It is an ATTESTATION that someone re-issued the
  field after the item last changed; it is not proof the item was read,
  and nothing mechanical can be.

Heading form: `## <id>. <title>`. Ids are integers, except item 47,
which becomes two items `47a` (empty-diff half) and `47b` (preamble
half) so that "every open item ranked exactly once" holds with no
exception.

Bodies:

- `OPEN` and `PARTIAL` items keep their full current text, cleaned of
  ranking-history prose and with the header replacing any prose status.
  A `PARTIAL` item's body must contain a paragraph beginning
  `**What remains.**` followed by at least twenty words on the same
  paragraph.
- `DONE` and `GONE` items keep only a resolution block: what shipped, in
  one to five sentences, and a `Record:` line naming a retained record
  path that exists in the tree, or a commit that `git cat-file -e`
  resolves. The full previous text stays in git history
  at the old path's last revision, which the preamble names by commit.

Items condensed in the rewrite are condensed by reading each one, not by
pattern, and each resolution block is written from the item's own
resolution text.

### 1d. Content decisions taken in the rewrite

- 75 stays first, `Pairs: none`. The reason is that its fix is undecided
  and uncosted (its own "Shape of a fix" says none of its candidates is
  costed), so no partner can be named until it is designed; it is NOT
  that nothing shares its surface, since item 76 touches the same mirror
  and sweep machinery and has chosen item 38 as its partner.
- 49, 59, 67 and 78 are mutually paired and hold entries 2 to 5; 78 is
  costed as Medium per its own text.
- 35 stays `OPEN`, narrowed. `-Prepare` takes `-PriorStateFile` as a
  plain string parameter and hashes whatever readable bytes it names;
  it checks neither the file's schema nor when it was captured, and
  SKILL.md still states the capture rule after the dispatch block (the
  command at its line 208, the rule at its line 254 at commit
  `1973843`). So the "no file at all" half is closed by the parameter
  and the "captured too late" half is not. Its Cost line says so.
- 68 moves to the missing-measurement group; 69 moves out of the
  workflow group to sit above 77. 43 moves above 31.
- 73 and 79 are slotted: 73 into the missing-measurement group as its
  cheapest member, 79 last. 71 and 72 are slotted into the last group
  with a Cost line that says the cost is uncosted and why.
- 27 loses its dead pairing with 19. 54 is repaired to pair with 77 and
  76; 31 and 51 pair unconditionally; 40 pairs with 43 and 41; 55 with
  45; 65 with 64. Every pairing is written on both sides.
- Item 34 (truncated captures on the reply side) is AMENDED and
  re-costed to carry the Fable raw-reply case from item 74's close: a
  retained reviewer reply is not checked to have reached its last
  section. It is the same failure class on a second lane, and a second
  item would split one class in two.
- Two new items are filed from item 74's close, each `OPEN`, each costed
  and slotted: general classifier refusals have no failure class in
  `fallbacks.md`; what the `fable` alias resolves to and what effort a
  seat runs at are unmeasured. A third from item 32: resume after a
  killed round is unmeasured.
- All renumbering narrative is deleted. The record of WHY the ranking
  looked as it did lives in git history.

### 1e. The old path

`docs/superpowers/plans/2026-07-27-0150-backlog.md` becomes a three-line
file: a pointer to `BACKLOG.md` and the commit at which the full text was
last present. Handoff files and memories cite the old path, so it must
resolve. Line citations into the old path exist in 83 retained round
records under `docs/superpowers/plans/rounds/` and in two lines of one
frozen plan, `docs/superpowers/plans/2026-08-03-home-skills-root-probe.md`
(its lines 78 and 975 at `0a41110`). An earlier version of this section
said no tracked document outside the round records carried one; that
inventory was wrong because the grep behind it was piped through `head`
and the two tracked hits were cut off, which is the trap CLAUDE.md's
long-running-commands rule names.

Raw round records are never edited, so their citations are NOT
rewritten. They also cannot be resolved at the last full-text commit:
the file was edited many times after most of them were written, and a
line number bound to one layout lands on unrelated text in another (the
probe plan's cite of line 41 was written for a 27-directory measurement;
at `0a41110` line 41 says item 16 is gone). Nor does the citing document's own commit always recover the layout:
`rounds/2026-07-28-0160-backlog/fable-review-c6b7c85-efe4fa0.md` cites
backlog lines 160 to 162, and at the commit that added that artifact
those lines hold different text from what it quotes, because the
backlog moved inside the branch between commits and the review read an
intermediate tree. So the pointer file names NO resolver at all. It
says that a line citation into this path is bound to the layout the
citing document read, that the branch inventory below records the
resolving commit for each citation where one exists, and that a
citation the inventory marks unresolved has none.

The branch inventories every raw citation into the old path: for each,
the citing file, the cited line, the subject revision the record names
(in its filename or text) or its own commit, and whether the cited line
at that revision carries the text the citation describes. Where it
does, the resolving commit is recorded; where it does not, the row is
marked unresolved and nothing is guessed. The inventory is retained
under the branch's round directory, never applied to the records.

The two citations in the frozen plan are rewritten in that plan to the
commit-bound form `path@<sha>:41`, where `<sha>` is the commit at which
line 41 carried the measurement. A frozen plan is a synthesized document
and not a raw round artifact, so correcting it is permitted under the
same rule that forbids editing the records. The branch grep that proves
no other tracked document carries such a citation is run WITHOUT any
output truncation and its full output is retained in the branch record.

## Part 2: the checker

`evals/tools/backlog_lint.py`, tested by
`evals/multi-model-verify/test_backlog_lint.py`. Runs on the file path
given, default `BACKLOG.md` at the repo root. Exit 0 on clean, 1 on any
failure, 2 on a file it cannot read or parse. Every failure names the
item id and the rule.

Rules, each a named check with at least one failing fixture:

1. Every `## <id>. <title>` heading is followed immediately by a header
   block with exactly the fields the status requires, in the fixed
   order, and no unknown fields.
2. Every id is unique. Ids are integers or `47a`/`47b`.
3. The `## Ranking` section contains only group headers and lines of the
   form `- <id>`.
4. The set of ranked ids equals the set of `OPEN` and `PARTIAL` ids, and
   each appears exactly once.
5. A `DONE` or `GONE` id never appears in the ranking.
6. `Pairs` is symmetric: if A names B, B names A. A pairing may not name
   a `DONE` or `GONE` item, or the item itself.
7. `Verified` carries a valid ISO date not in the future and a 12-hex
   digest equal to the digest of the item's current canonical content
   as defined in 1c. A mismatch names the item and prints the expected
   digest. This rule reads only the file, never git, so it behaves the
   same on the first commit, in a temporary checkout, and under the
   pre-push revision mode in Part 3. Required fixtures: the initial
   file; an item edited without refreshing the field; an item moved to
   another ranking group; a heading renamed; the same item edited twice
   in one day with the field refreshed once.
8. No ranking group header and no `OPEN` or `PARTIAL` body matches the
   banned-narrative list: `renumbered`, `moved up by one`, `moved down
   by one`, `shifted down`, `formerly entry`, `used to hold entry`,
   `read the numbers as they stand`. The list lives in the tool and is
   extendable; the test pins that each phrase fails. This rule is a
   HEURISTIC for the migration and is labelled one in the tool: it can
   be evaded by rewording anywhere it applies. Rules 3, 4 and 12 LIMIT
   narrative in the ranking to whatever fits an eight-word header; they
   do not make it impossible, since a short renumbering story fits. In
   item bodies nothing limits it, and the spec claims nothing more.
9. A `PARTIAL` body contains `**What remains.**` followed by at least
   twenty words in the same paragraph.
10. A `DONE` or `GONE` body contains a `Record:` line whose value is a
    path that exists in the tree (in `--revision` mode, in that
    revision's tree) or a commit that `git cat-file -e` resolves.
11. The old path's pointer file exists, names `BACKLOG.md`, and carries
    the resolution rule from 1e.
12. Every `### ` header inside `## Ranking` is at most eight words, and
    no non-header, non-id line appears in that section.

Rules 9 and 10 are SHAPE checks and are labelled so in the tool: twenty
filler words satisfy 9, and any existing path satisfies 10. Whether the
remainder text is real and the record is the right one is judged by the
second reader named under Process, never by the lint.

The checker does NOT: rewrite the file, judge order, or read item
bodies beyond rules 7 to 10.

It accepts `--revision <sha>`, under which it reads `BACKLOG.md` and the
old-path pointer from git objects (`git show <sha>:<path>`) instead of the
working tree, so a hook can lint a pushed commit without touching the
checkout.

## Part 3: the hooks

**What each hook IS, stated before any of them is described.** The Stop
hook is a REMINDER-class control: it fires once, a second stop attempt
carries `stop_hook_active` and passes, and it exits 0 when its baseline
or git is missing, so a session CAN finish without updating the backlog
by stopping twice or by running where the hook cannot see. The hard
controls are the pre-push clause and the CI range check in 3d, which
apply the SAME governed-range and re-attestation test and do not depend
on the session cooperating or on the local hook being installed. The
spec does not promise that a session "cannot finish" without the
backlog. It promises that a hooked push is refused and that any other
arrival on main is detected by CI; turning detection into prevention is
a repository setting outside this tree, stated in 3d.

**What "touched the backlog" means for the hooks.** A changed byte is
not enough: changing an unrelated item's date, or a preamble character,
would satisfy a bytes test and review nothing. The Stop and pre-push
hooks therefore require that the backlog diff (against the baseline for
Stop, across the range for pre-push) changes the `Verified` line of at
least one `OPEN` or `PARTIAL` item, and the hook names that item id in
its output. That is the same explicit per-item act rule 7 already
forces after a content change. The hooks prove exactly that someone
changed an eligible item's attestation line in the range, and nothing
more. Two residuals are irreducible and both are stated: a session can
re-attest the WRONG item, because no mechanical rule can tell which
item owns a piece of work; and a session can re-attest the right item
WITHOUT READING it, because the `Verified` line is outside its own
digest and a date change alone satisfies the predicate. Rule 7 forces
a per-item act after content changes; it does not force reading.

All in a tracked `.claude/settings.json` at the repo root, project scope.
Hook commands are `pwsh` invocations calling Python, matching the host
the plugin's own hooks already require. `.gitignore` currently ignores
`.claude/` wholesale (its line 3 at `1973843`), so the branch changes
that entry to `.claude/*` and adds `!.claude/settings.json`; a test
asserts the settings file is tracked.

Hook shapes, from the Claude Code hooks documentation read 2026-09-04
(code.claude.com/docs/en/hooks-guide): a Stop hook blocks by EXIT CODE
2 with its reason on stdout, not by a JSON decision; its stdin carries
`stop_hook_active`, which the hook must honour by exiting 0 when true so
it cannot loop; and a SessionStart hook receives `session_id` and `cwd`
on stdin. Each shape is proven by a checked-in fixture that feeds the
documented stdin to the script and asserts the exit code, before any
hook is wired.

### 3a0. SessionStart

Writes a per-session baseline under the session's scratch area, keyed by
`session_id`: the current HEAD, and the SHA-256 of `BACKLOG.md`'s bytes
(or `absent`). The Stop hook compares against this, so the check is
scoped to what THIS session did and not to the branch's whole history.

### 3a. PostToolUse on Edit and Write

Matcher: tool is Edit or Write. The hook script reads the tool input's
file path; if its basename is `BACKLOG.md`, it runs the lint and returns
the lint output as the hook's message. A failing lint is reported, not
blocked, because the edit has already happened; the session sees it in
the same turn. An edit made through a shell command is not seen here;
it is caught at Stop, in the gate, and at push.

### 3b. Stop

On Stop, after honouring `stop_hook_active`, the hook reads this
session's baseline and computes: whether any change since the baseline
HEAD, staged, unstaged or committed, touches a GOVERNED path; and
whether `BACKLOG.md`'s current bytes differ from the baseline hash. The
governed paths are `tools/`, `skills/`, `agents/`, `evals/`, `commands/`,
`hooks/`, `.claude-plugin/`, `.githooks/`, `.github/`, `README.md` and
`CLAUDE.md`. If governed paths changed and no `OPEN` or `PARTIAL`
item's `Verified` line changed, it exits 2 with `BACKLOG.md carries no
re-attested item this session while governed surfaces changed; update
the item that owns the work and refresh its Verified field`. Whenever the backlog DID change, it runs the lint and exits 2
on failure with the lint's output, so an edit made through a shell
command that PostToolUse never saw is still checked before the session
ends. With no baseline file (a session started before the hook existed)
it prints a note and exits 0. When git is unavailable it prints a note
and exits 0, so a broken git cannot wedge a session. A detached HEAD is
handled the same as a branch: the baseline records a commit, not a ref.

The escape is explicit: refreshing the `Verified` field of the item that
owns the work counts as a touch, because rule 7 already forces that
refresh when the item's content changed, and a session that read the
item and found nothing else to change has done the work the hook exists
to force.

### 3c. Pre-push

`.githooks/pre-push` gains a second clause before the attestation clause.
For a push to `refs/heads/main`, it lists the paths changed in
`remote..local` (on a new remote branch, in `local` alone). If any
governed path from 3b is in that list and the range's diff of
`BACKLOG.md` changes no `OPEN` or `PARTIAL` item's `Verified` line, it
refuses with exit 1. If `BACKLOG.md` is in the list, it runs
`python evals/tools/backlog_lint.py --revision <local sha>` and refuses
on failure. Merge topology is not consulted: a squash, a fast-forward
and a merge commit are all judged by the paths they carry, so a push
that touches no governed path is never blocked and a governed change
never escapes by being squashed. `README.md` and `CLAUDE.md` ARE
governed, so a push that changes only one of them is blocked without a
re-attested item; that is deliberate, because both are surfaces every
session reads first, and it is stated here so the hook's own header
does not promise otherwise. Every pushed range stands alone: a backlog edit pushed
earlier does not cover governed changes pushed later, because later
work either changes an item (rule 7 forces a refresh) or is a new item.

This is the first BLOCKING clause in that hook. The attestation clause
stays non-blocking exactly as written; the hook's header comment is
updated to say which clause blocks and why. Its "docs/chore pushes stay
friction-free" sentence is rewritten to "pushes touching no governed
path stay friction-free", with the governed list named beside it.

### 3d. Gate and CI

`python evals/tools/backlog_lint.py` is added to CLAUDE.md's
verification list and to the `skill-evals` job as its own tier, so a
hand edit or a merge from another machine is caught in CI.

CI also runs the SAME governed-range and re-attestation test as the
pre-push clause, because a local hook can be uninstalled or bypassed.
The lint gains `--range <base>..<head>` which performs exactly the 3c
test from git objects: on a push to main the base is the event's
`before` sha, on a pull request it is the pull request's base sha, and
on a new branch with no before sha the range is the head alone. The
workflow step fails the job when the range carries a governed change
and no re-attested `OPEN` or `PARTIAL` item. The pre-push clause is
rewritten to call this same mode, so the two cannot drift apart, and
the disposable-clone test drives the mode directly as well as through
the hook.

**What CI can and cannot do here.** A `push` workflow runs AFTER the
ref has moved, so on a direct push from a hookless clone the job fails
with main already changed; that is detection. The same job on a
`pull_request` event runs BEFORE the merge, but GitHub only refuses the
merge if the job is a required status check, and that is a repository
ruleset, not a file in this tree. The design therefore records ONE
decision for the user, not made here: enable a ruleset on `main` that
forbids direct pushes and requires the `skill-evals` job, which turns
the CI check into prevention for every path. Until that is enabled,
every sentence in this spec about CI means detection on arrival, and
the pre-push hook on each clone is the only refusal.

## Error handling

- Every hook script exits 0 with a printed note when Python or git is
  missing, except pre-push, which refuses, because a push is the one
  place a missing tool must not read as a pass.
- The lint prints every failure, never the first only, per CLAUDE.md's
  rule that the names are what a second run needs.

## Testing

- `test_backlog_lint.py`: one failing fixture per rule, the five rule-7
  fixtures named above, one clean fixture, a `--revision` run against a
  temporary repo's committed file, and a run against the real
  `BACKLOG.md` that must pass.
- The SessionStart, Stop and PostToolUse hook scripts are tested by
  invoking them with the documented stdin JSON inside a temporary repo,
  under both PowerShell hosts per the dual-host rule, including
  `stop_hook_active: true`, a missing baseline, a governed change with
  and without a backlog touch, and a backlog edit that fails the lint.
- The pre-push clause is tested by the same method the drift
  state-machine harness uses: a disposable clone with a stub remote,
  pushed as a merge, a squash and a fast-forward, each with and without
  a re-attested item alongside a governed change; a push changing only
  `docs/**` that must pass; pushes changing only `README.md` and only
  `CLAUDE.md` that must block; and a push whose only backlog change is
  an unrelated byte, which must block.
- The rewritten `BACKLOG.md` passes the lint before the branch is
  reviewed.

## Process

Feature branch, written plan, subagent-driven build, whole-branch Fable
review, then the cross-vendor diff debate before merge, per this repo's
rules. The rewrite of item bodies is one task of that plan and is
verified by a second reader comparing each resolution block to the
item's own resolution text at the old path, each `Record:` value to the
record that item's own text names, and each `PARTIAL` remainder
paragraph to what the item's own text says remains. The version bump comes after
the debate. `BACKLOG.md` itself is updated as the last act of the branch,
by the hooks this branch installs.
