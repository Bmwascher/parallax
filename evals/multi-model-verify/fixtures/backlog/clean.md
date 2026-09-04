# BACKLOG

Headers are the source of truth. The ranking is an ordered list and
nothing else. Closing an item means editing its header and deleting
its ranking line. `evals/tools/backlog_lint.py` enforces all of it.

## Ranking

### First - breaks the review process
- 1
- 3

### Last - housekeeping

## 1. First open item
Status: OPEN
Cost: one line of cost
Pairs: 3
Verified: 2026-09-04 012fe7f56152

Body of item one.

## 2. A closed item
Status: DONE
Closed: 0.29.0
Verified: 2026-09-04 4bf273440723

Shipped in one sentence.
Record: docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md

## 3. A partial item
Status: PARTIAL
Cost: the remainder costs this
Pairs: 1
Verified: 2026-09-04 376989925a26

**What remains.** The mechanical half was never designed and this
paragraph carries at least twenty words so that the shape rule nine
is satisfied by the fixture itself here.

## 4. A gone item
Status: GONE
Closed: superseded
Verified: 2026-09-04 5dce3a58691f

Superseded by item 2.
Record: docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md
