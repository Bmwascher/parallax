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
- item 35's defect is closed by construction in 0.28.0 and its heading
  still says OPEN;
- five of the eleven stated pairings are written from one side only, one
  names a closed partner (27 with 19), and one pairs items in different
  files (54 with 51);
- three findings from item 74's close have no owning item;
- about a third of the ranking's prose is history of its own renumbering.

Nothing enforces that a session returns to the file when work completes,
and nothing checks the file's shape. The repo has measured three times
(item 59) that a rule enforced only by remembering it is skipped.

## Goals

1. One source of truth per fact. The status view and the ranking are
   derived from the items, never written separately.
2. A session cannot finish work that changes shipped surfaces without
   touching the backlog, and cannot merge to main without it.
3. The file's shape is checked mechanically on every edit, in the gate,
   and at push.
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

```
## Ranking

Ordered. Groups are labels, not tiers; order within and across groups
is the build order. No prose here: the case for a place is the item's
Cost line.

### First - breaks the repo's own review process
- 75
- 49
...
### Last - housekeeping and open questions
- 61
```

Rules: one item id per line, no position numbers, no text after the id.
Group header names are free text. Closing an item deletes its line and
nothing else moves.

### 1c. Items

Every item opens with a fixed header block, then its body.

```
## 75. The review mirror deletes authoritative policy
Status: OPEN
Cost: the reviewer certifies a transcription of a policy, and no gate can see it
Pairs: none
Verified: 2026-09-04
```

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
- `Verified`: an ISO date. The date a person last read the whole item and
  its ranking place against the tree. Required on every item.

Heading form: `## <id>. <title>`. Ids are integers, except item 47,
which becomes two items `47a` (empty-diff half) and `47b` (preamble
half) so that "every open item ranked exactly once" holds with no
exception.

Bodies:

- `OPEN` and `PARTIAL` items keep their full current text, cleaned of
  ranking-history prose and with the header replacing any prose status.
  A `PARTIAL` item's body must contain a paragraph beginning
  `**What remains.**`.
- `DONE` and `GONE` items keep only a resolution block: what shipped, in
  one to five sentences, and a `Record:` line naming the retained record
  path or the merge commit. The full previous text stays in git history
  at the old path's last revision, which the preamble names by commit.

Items condensed in the rewrite are condensed by reading each one, not by
pattern, and each resolution block is written from the item's own
resolution text.

### 1d. Content decisions taken in the rewrite

- 75 stays first, `Pairs: none`. Nothing on the list shares its file or
  its gate.
- 49, 59, 67 and 78 are mutually paired and hold entries 2 to 5; 78 is
  costed as Medium per its own text.
- 35 is re-examined against `tools/dispatch-round.ps1` and SKILL.md's
  step ordering. If the prior-state file is a required input of the
  prepare step that precedes the dispatch, 35 closes as `DONE`,
  `Closed: 0.28.0`, with the resolution saying so.
- 68 moves to the missing-measurement group; 69 moves out of the
  workflow group to sit above 77. 43 moves above 31.
- 73 and 79 are slotted: 73 into the missing-measurement group as its
  cheapest member, 79 last. 71 and 72 are slotted into the last group
  with a Cost line that says the cost is uncosted and why.
- 27 loses its dead pairing with 19. 54 is repaired to pair with 77 and
  76; 31 and 51 pair unconditionally; 40 pairs with 43 and 41; 55 with
  45; 65 with 64. Every pairing is written on both sides.
- Three new items are filed from item 74's close, each `OPEN`, each
  costed and slotted: a retained reviewer reply is not checked to have
  reached its last section; general classifier refusals have no failure
  class in `fallbacks.md`; what the `fable` alias resolves to and what
  effort a seat runs at are unmeasured. A fourth from item 32: resume
  after a killed round is unmeasured.
- All renumbering narrative is deleted. The record of WHY the ranking
  looked as it did lives in git history.

### 1e. The old path

`docs/superpowers/plans/2026-07-27-0150-backlog.md` becomes a three-line
file: a pointer to `BACKLOG.md` and the commit at which the full text was
last present. Handoff files and memories cite the old path, so it must
resolve.

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
7. `Verified` is a valid ISO date not in the future, and is not earlier
   than the date of the last commit that changed that item's span. The
   span is the heading through the line before the next heading; the
   commit date comes from `git log` restricted to that line range. When
   the file is not in a git repository or git is unavailable, this rule
   reports SKIPPED by name and the exit code stays 1, because an unmade
   check is not a clean one.
8. No line in the file matches the banned-narrative list:
   `renumbered`, `moved up by one`, `moved down by one`, `shifted down`,
   `formerly entry`, `used to hold entry`, `read the numbers as they
   stand`. The list lives in the tool and is extendable; the test pins
   that each phrase fails.
9. A `PARTIAL` body contains `**What remains.**`.
10. A `DONE` or `GONE` body contains a `Record:` line.
11. The old path's pointer file exists and names `BACKLOG.md`.

The checker does NOT: rewrite the file, judge order, or read item
bodies beyond rules 8 to 10.

## Part 3: the hooks

All in a tracked `.claude/settings.json` at the repo root, project scope.
Hook commands are `pwsh` invocations calling Python, matching the host
the plugin's own hooks already require.

### 3a. PostToolUse on Edit and Write

Matcher: tool is Edit or Write. The hook script reads the tool input's
file path; if its basename is `BACKLOG.md`, it runs the lint and returns
the lint output as the hook's message. A failing lint is reported, not
blocked, because the edit has already happened; the session sees it in
the same turn.

### 3b. Stop

On Stop, the hook computes two things against the branch's merge base
with main: whether any tracked change, staged, unstaged or committed
since the base, touches `tools/`, `skills/`, `agents/`, `evals/`,
`commands/`, `hooks/` or `README.md`; and whether `BACKLOG.md` differs
from the base. If the first is true and the second is false, the hook
returns a block decision with the reason
`BACKLOG.md unchanged since branch base while shipped surfaces changed;
update it or record why no item moved`. On main with a clean tree it
returns nothing. It never blocks when git is unavailable; it prints a
note instead, so a broken git cannot wedge a session.

The escape is explicit: a one-line `Verified` date bump on the relevant
item counts as a touch, because rule 7 already forces that bump when the
item's span changed, and a session that read the item and found nothing
to change has done the work the hook exists to force.

### 3c. Pre-push

`.githooks/pre-push` gains a second clause before the attestation clause.
For a push to `refs/heads/main` whose range `remote..local` contains a
merge commit, it refuses (exit 1) unless both hold: `BACKLOG.md` is in
the range's changed paths, and `python evals/tools/backlog_lint.py`
passes on the local sha's tree (checked out to a temporary index, never
the working tree). The message names which of the two failed.

This is the first BLOCKING clause in that hook. The attestation clause
stays non-blocking exactly as written; the hook's header comment is
updated to say which clause blocks and why.

### 3d. Gate and CI

`python evals/tools/backlog_lint.py` is added to CLAUDE.md's
verification list and to the `skill-evals` job as its own tier, so a
hand edit or a merge from another machine is caught in CI.

## Error handling

- Every hook script exits 0 with a printed note when Python or git is
  missing, except pre-push, which refuses, because a push is the one
  place a missing tool must not read as a pass.
- The lint prints every failure, never the first only, per CLAUDE.md's
  rule that the names are what a second run needs.

## Testing

- `test_backlog_lint.py`: one failing fixture per rule, one clean
  fixture, and a run against the real `BACKLOG.md` that must pass.
- Rule 7's git dependency is tested inside a temporary repo the test
  creates and commits to.
- The Stop and PostToolUse hook scripts are tested by invoking them with
  hand-built JSON on stdin inside a temporary repo, under both PowerShell
  hosts per the dual-host rule.
- The pre-push clause is tested by the same method the drift
  state-machine harness uses: a disposable clone with a stub remote,
  pushed with and without a backlog change in a merge range.
- The rewritten `BACKLOG.md` passes the lint before the branch is
  reviewed.

## Process

Feature branch, written plan, subagent-driven build, whole-branch Fable
review, then the cross-vendor diff debate before merge, per this repo's
rules. The rewrite of item bodies is one task of that plan and is
verified by a second reader comparing each resolution block to the
item's own resolution text at the old path. The version bump comes after
the debate. `BACKLOG.md` itself is updated as the last act of the branch,
by the hooks this branch installs.
