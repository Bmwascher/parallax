# Citation inventory: docs/superpowers/plans/2026-07-27-0150-backlog.md

Every `2026-07-27-0150-backlog.md:N` (or `:N-M`) citation found by
`citation-grep.txt`, one row per individual citation (a single grep line
can carry more than one citation; each is its own row here). The full
mechanical check that produced the "matches?" column, including its
candidate resolution and the exact comparison for every row, is retained
untruncated in `citation-inventory-check.txt` beside this file.

**Candidate order:** an `@sha` explicitly named in the citing text, then
the citing record's own first commit, then that commit's first parent.
A row reads `yes <sha>` only when the check found the citing text's own
words verbatim, at that exact cited range, at that revision. Anything
short of that is `unresolved` — no row is guessed.

| # | citing record | cites | resolution | matches? |
|---|---|---|---|---|
| 1 | 2026-07-28-0160-backlog/fable-review-c6b7c85-efe4fa0.md:30 | 160-162 | unresolved | insufficient overlap (hits=['recorded']) |
| 2 | 2026-07-28-0160-backlog/kimi-backup-lane-0160-r1-reply.md:9 | 72-75 | yes 3413c8e | distinctive-word overlap (7): blocked-crash, no-verdict, scenarios, scenario, failure, proves |
| 3 | 2026-07-28-0160-backlog/kimi-backup-lane-0160-r1-reply.md:9 | 69-70 | unresolved | insufficient overlap (hits=['scenario']) |
| 4 | 2026-07-28-0160-backlog/kimi-backup-lane-0160-r1-reply.md:25 | 75 | unresolved | no distinctive terms matched at any candidate |
| 5 | 2026-07-28-0160-backlog/sol-diff-0160-r1-reply.md:65 | 52-58 | unresolved | insufficient overlap (hits=['blocked']) |
| 6 | 2026-07-28-0160-backlog/sol-diff-0160-r1-reply.md:66 | 212-224 | yes 7a89084 | distinctive-word overlap (5): kimi-lane-lock, minutes, crashed, driver, stalls |
| 7 | 2026-07-28-0160-backlog/sol-diff-0160-r1-reply.md:67 | 217-219 | yes 7a89084 | quote match: "14 tests" |
| 8 | 2026-07-28-0160-backlog/sol-diff-0160-r1-reply.md:80 | 154-164 | unresolved | insufficient overlap (hits=['backup-lane']) |
| 9 | 2026-07-28-0160-backlog/sol-diff-0160-r1-reply.md:80 | 205-210 | yes 7a89084 | distinctive-word overlap (3): concurrent, startup, window |
| 10 | 2026-07-28-0160-backlog/sol-diff-0160-r2-reply.md:1 | 230-250 | unresolved | insufficient overlap (hits=['ownership', 'staleness']) |
| 11 | 2026-07-28-0160-backlog/sol-diff-0160-r2-reply.md:36 | 52-70 | unresolved | insufficient overlap (hits=['blocked', 'defect']) |
| 12 | 2026-07-28-0160-backlog/sol-diff-0160-r2-reply.md:40 | 233-234 | unresolved | no distinctive terms matched at any candidate |
| 13 | 2026-07-28-0160-backlog/sol-diff-0160-r2-reply.md:41 | 235-240 | unresolved | no distinctive terms matched at any candidate |
| 14 | 2026-07-28-0160-backlog/sol-diff-0160-r2-reply.md:42 | 245-250 | unresolved | no distinctive terms matched at any candidate |
| 15 | 2026-07-28-0160-backlog/sol-diff-0160-r2-reply.md:53 | 72-75 | unresolved | insufficient overlap (hits=['verdict']) |
| 16 | 2026-07-28-0160-backlog/sol-diff-0160-r2-reply.md:53 | 215-228 | unresolved | insufficient overlap (hits=['reported']) |
| 17 | 2026-07-28-0160-backlog/sol-diff-0160-r3-reply.md:37 | 230-255 | yes 3413c8e | distinctive-word overlap (3): case-sensitive, ownership, string |
| 18 | 2026-07-28-0160-backlog/sol-diff-0160-r3-reply.md:41 | 222-228 | unresolved | insufficient overlap (hits=['kimi-lane-lock', 'cannot']) |
| 19 | 2026-07-28-0160-backlog/sol-diff-0160-r3-reply.md:47 | 222-228 | unresolved | no distinctive terms matched at any candidate |
| 20 | 2026-07-28-0160-backlog/sol-diff-0160-r4-reply.md:31 | 260-280 | unresolved | insufficient overlap (hits=['non-string', 'current']) |
| 21 | 2026-07-28-reviewer-isolation/kimi-panel-r1-reply.md:25 | 343-369 | unresolved | no distinctive terms matched at any candidate |
| 22 | 2026-07-28-reviewer-isolation/sol-diff-r1-reply.md:84 | 343-349 | unresolved | no distinctive terms matched at any candidate |
| 23 | 2026-07-28-reviewer-isolation/sol-plan-r1-reply.md:27 | 14 | unresolved | no distinctive terms matched at any candidate |
| 24 | 2026-08-03-home-skills-root/kimi-r1-reply.md:71 | 41 | yes e9c0aae | quote match: "27 skill" |
| 25 | 2026-08-03-home-skills-root/kimi-r1-reply.md:324 | 41 | unresolved | insufficient overlap (hits=['directories', 'measured']) |
| 26 | 2026-08-03-home-skills-root/kimi-r1-reply.md:345 | 41 | unresolved | insufficient overlap (hits=['evidence']) |
| 27 | 2026-08-03-home-skills-root/sol-plan-r1-brief.md:41 | 577 | unresolved | insufficient overlap (hits=['mirror']) |
| 28 | 2026-08-04-lane-release-and-round-cap/diff-reply-r1.md:67 | 1810-1837 | unresolved | insufficient overlap (hits=['ordering']) |
| 29 | 2026-08-04-lane-release-and-round-cap/diff-reply-r1.md:75 | 1672-1680 | unresolved | insufficient overlap (hits=['single']) |
| 30 | 2026-08-04-lane-release-and-round-cap/diff-reply-r1.md:79 | 11-16 | unresolved | insufficient overlap (hits=['status']) |
| 31 | 2026-08-04-lane-release-and-round-cap/diff-reply-r1.md:79 | 1471-1472 | unresolved | no distinctive terms matched at any candidate |
| 32 | 2026-08-04-lane-release-and-round-cap/diff-reply-r1.md:79 | 1522-1523 | unresolved | no distinctive terms matched at any candidate |
| 33 | 2026-08-04-lane-release-and-round-cap/diff-reply-r1.md:79 | 1566-1567 | unresolved | no distinctive terms matched at any candidate |
| 34 | 2026-08-04-lane-release-and-round-cap/diff-reply-r1.md:79 | 1810-1812 | unresolved | no distinctive terms matched at any candidate |
| 35 | 2026-08-04-lane-release-and-round-cap/diff-reply-r1.md:88 | 1826-1837 | unresolved | insufficient overlap (hits=['ordering']) |
| 36 | 2026-08-04-lane-release-and-round-cap/diff-reply-r2.md:11 | 1683 | unresolved | no distinctive terms matched at any candidate |
| 37 | 2026-08-04-lane-release-and-round-cap/diff-reply-r2.md:11 | 1691 | unresolved | no distinctive terms matched at any candidate |
| 38 | 2026-08-04-lane-release-and-round-cap/diff-reply-r2.md:13 | 1688 | unresolved | no distinctive terms matched at any candidate |
| 39 | 2026-08-04-lane-release-and-round-cap/diff-reply-r2.md:37 | 1837 | unresolved | no distinctive terms matched at any candidate |
| 40 | 2026-08-04-lane-release-and-round-cap/diff-reply-r2.md:37 | 1853 | unresolved | no distinctive terms matched at any candidate |
| 41 | 2026-08-04-lane-release-and-round-cap/diff-reply-r2.md:37 | 1858 | unresolved | no distinctive terms matched at any candidate |
| 42 | 2026-08-04-lane-release-and-round-cap/diff-reply-r2.md:41 | 11 | unresolved | no distinctive terms matched at any candidate |
| 43 | 2026-08-04-lane-release-and-round-cap/diff-reply-r2.md:41 | 25 | unresolved | no distinctive terms matched at any candidate |
| 44 | 2026-08-04-lane-release-and-round-cap/diff-reply-r2.md:41 | 1575 | unresolved | insufficient overlap (hits=['partially', 'closed']) |
| 45 | 2026-08-04-lane-release-and-round-cap/diff-reply-r2.md:41 | 1681 | unresolved | insufficient overlap (hits=['partially', 'closed']) |
| 46 | 2026-08-04-lane-release-and-round-cap/diff-reply-r2.md:41 | 1703 | unresolved | insufficient overlap (hits=['unmeasurable']) |
| 47 | 2026-08-04-lane-release-and-round-cap/diff-reply-r2.md:41 | 1707 | unresolved | no distinctive terms matched at any candidate |
| 48 | 2026-08-04-lane-release-and-round-cap/diff-reply-r2.md:43 | 1688 | unresolved | no distinctive terms matched at any candidate |
| 49 | 2026-08-04-lane-release-and-round-cap/diff-reply-r3.md:39 | 1837 | unresolved | no distinctive terms matched at any candidate |
| 50 | 2026-08-04-lane-release-and-round-cap/diff-reply-r3.md:39 | 1853 | unresolved | no distinctive terms matched at any candidate |
| 51 | 2026-08-04-lane-release-and-round-cap/diff-reply-r3.md:43 | 1681 | unresolved | insufficient overlap (hits=['partially', 'closed']) |
| 52 | 2026-08-04-lane-release-and-round-cap/diff-reply-r3.md:43 | 1693 | unresolved | insufficient overlap (hits=['wrapper']) |
| 53 | 2026-08-04-lane-release-and-round-cap/diff-reply-r4.md:35 | 1837 | unresolved | insufficient overlap (hits=['ancestry']) |
| 54 | 2026-08-04-lane-release-and-round-cap/diff-reply-r4.md:39 | 1575 | unresolved | insufficient overlap (hits=['partially', 'closed']) |
| 55 | 2026-08-04-lane-release-and-round-cap/diff-reply-r4.md:39 | 1681 | unresolved | insufficient overlap (hits=['partially', 'closed']) |
| 56 | 2026-08-04-lane-release-and-round-cap/diff-reply-r5.md:33 | 1837 | unresolved | no distinctive terms matched at any candidate |
| 57 | 2026-08-04-lane-release-and-round-cap/diff-reply-r6.md:29 | 1837 | unresolved | insufficient overlap (hits=['ancestry']) |
| 58 | 2026-08-04-lane-release-and-round-cap/diff-reply-r6.md:33 | 1575 | unresolved | insufficient overlap (hits=['partially', 'closed']) |
| 59 | 2026-08-04-lane-release-and-round-cap/diff-reply-r6.md:33 | 1681 | unresolved | insufficient overlap (hits=['partially', 'closed']) |
| 60 | 2026-08-04-lane-release-and-round-cap/plan-reply-r1.md:7 | 1606 | unresolved | no distinctive terms matched at any candidate |
| 61 | 2026-08-04-lane-release-and-round-cap/plan-reply-r1.md:69 | 1573 | unresolved | no distinctive terms matched at any candidate |
| 62 | 2026-08-04-lane-release-and-round-cap/plan-reply-r1.md:76 | 1481 | unresolved | no distinctive terms matched at any candidate |
| 63 | 2026-08-04-transport-and-mirror/diff-r1-reply.md:92 | 20 | unresolved | insufficient overlap (hits=['shipped']) |
| 64 | 2026-08-04-transport-and-mirror/diff-r1-reply.md:104 | 37-42 | unresolved | insufficient overlap (hits=['skills']) |
| 65 | 2026-08-04-transport-and-mirror/diff-r1-reply.md:106 | 22-35 | unresolved | insufficient overlap (hits=['suppressed', 'measured']) |
| 66 | 2026-08-04-transport-and-mirror/diff-r2-reply.md:22 | 28-46 | yes 4b02cb3 | distinctive-word overlap (3): home-skills-root, invocation, verdict |
| 67 | 2026-08-04-transport-and-mirror/diff-r2-reply.md:22 | 1094-1118 | unresolved | no distinctive terms matched at any candidate |
| 68 | 2026-08-04-transport-and-mirror/diff-r2-reply.md:28 | 57-64 | unresolved | insufficient overlap (hits=['falsified']) |
| 69 | 2026-08-04-transport-and-mirror/diff-r2-reply.md:34 | 22-26 | unresolved | no distinctive terms matched at any candidate |
| 70 | 2026-08-04-transport-and-mirror/diff-r3-reply.md:13 | 48-55 | unresolved | no distinctive terms matched at any candidate |
| 71 | 2026-08-04-transport-and-mirror/diff-r3-reply.md:15 | 1110-1116 | unresolved | no distinctive terms matched at any candidate |
| 72 | 2026-08-04-transport-and-mirror/diff-r3-reply.md:17 | 22-27 | unresolved | no distinctive terms matched at any candidate |
| 73 | 2026-08-04-transport-and-mirror/plan-reply-r1b.md:7 | 1195 | unresolved | no distinctive terms matched at any candidate |
| 74 | 2026-08-04-transport-and-mirror/plan-reply-r1b.md:7 | 1195 | unresolved | no distinctive terms matched at any candidate |
| 75 | 2026-08-04-transport-and-mirror/plan-reply-r1b.md:11 | 1280 | unresolved | no distinctive terms matched at any candidate |
| 76 | 2026-08-04-transport-and-mirror/plan-reply-r1b.md:11 | 1280 | unresolved | no distinctive terms matched at any candidate |
| 77 | 2026-08-04-transport-and-mirror/plan-reply-r1b.md:37 | 1195 | unresolved | no distinctive terms matched at any candidate |
| 78 | 2026-08-04-transport-and-mirror/plan-reply-r1b.md:37 | 1195 | unresolved | no distinctive terms matched at any candidate |
| 79 | 2026-08-04-transport-and-mirror/plan-reply-r1b.md:39 | 1280 | unresolved | no distinctive terms matched at any candidate |
| 80 | 2026-08-04-transport-and-mirror/plan-reply-r1b.md:39 | 1280 | unresolved | no distinctive terms matched at any candidate |
| 81 | 2026-08-04-transport-and-mirror/plan-reply-r1b.md:41 | 1346 | unresolved | no distinctive terms matched at any candidate |
| 82 | 2026-08-04-transport-and-mirror/plan-reply-r1b.md:41 | 1346 | unresolved | no distinctive terms matched at any candidate |
| 83 | 2026-08-04-transport-and-mirror/plan-reply-r1b.md:43 | 1383 | unresolved | no distinctive terms matched at any candidate |
| 84 | 2026-08-04-transport-and-mirror/plan-reply-r1b.md:43 | 1383 | unresolved | no distinctive terms matched at any candidate |
| 85 | 2026-08-04-transport-and-mirror/plan-reply-r2.md:3 | 1213 | unresolved | insufficient overlap (hits=['remains']) |
| 86 | 2026-08-04-transport-and-mirror/plan-reply-r2.md:3 | 1213 | unresolved | insufficient overlap (hits=['remains']) |
| 87 | 2026-08-04-transport-and-mirror/plan-reply-r2.md:31 | 1212 | unresolved | insufficient overlap (hits=['resume']) |
| 88 | 2026-08-04-transport-and-mirror/plan-reply-r2.md:31 | 1212 | unresolved | insufficient overlap (hits=['resume']) |
| 89 | 2026-08-04-transport-and-mirror/plan-reply-r2.md:31 | 1191 | unresolved | insufficient overlap (hits=['oracles']) |
| 90 | 2026-08-04-transport-and-mirror/plan-reply-r2.md:31 | 1191 | unresolved | insufficient overlap (hits=['oracles']) |
| 91 | 2026-08-04-transport-and-mirror/plan-reply-r2.md:33 | 1361 | unresolved | no distinctive terms matched at any candidate |
| 92 | 2026-08-04-transport-and-mirror/plan-reply-r2.md:33 | 1361 | unresolved | no distinctive terms matched at any candidate |
| 93 | 2026-08-04-transport-and-mirror/plan-reply-r2.md:33 | 1369 | unresolved | no distinctive terms matched at any candidate |
| 94 | 2026-08-04-transport-and-mirror/plan-reply-r2.md:33 | 1369 | unresolved | no distinctive terms matched at any candidate |
| 95 | 2026-08-04-transport-and-mirror/plan-reply-r2.md:43 | 1191 | unresolved | insufficient overlap (hits=['oracles']) |
| 96 | 2026-08-04-transport-and-mirror/plan-reply-r2.md:43 | 1191 | unresolved | insufficient overlap (hits=['oracles']) |
| 97 | 2026-08-04-transport-and-mirror/plan-reply-r3.md:18 | 1392 | unresolved | no distinctive terms matched at any candidate |
| 98 | 2026-08-04-transport-and-mirror/plan-reply-r3.md:18 | 1392 | unresolved | no distinctive terms matched at any candidate |
| 99 | 2026-08-04-transport-and-mirror/plan-reply-r3.md:22 | 1191 | unresolved | insufficient overlap (hits=['oracles']) |
| 100 | 2026-08-04-transport-and-mirror/plan-reply-r3.md:22 | 1191 | unresolved | insufficient overlap (hits=['oracles']) |
| 101 | 2026-08-04-transport-and-mirror/plan-reply-r3.md:23 | 1225 | unresolved | insufficient overlap (hits=['checks']) |
| 102 | 2026-08-04-transport-and-mirror/plan-reply-r3.md:23 | 1225 | unresolved | insufficient overlap (hits=['checks']) |
| 103 | 2026-08-04-transport-and-mirror/plan-reply-r3.md:24 | 1214 | unresolved | insufficient overlap (hits=['validates']) |
| 104 | 2026-08-04-transport-and-mirror/plan-reply-r3.md:24 | 1214 | unresolved | insufficient overlap (hits=['validates']) |
| 105 | 2026-08-04-transport-and-mirror/plan-reply-r4.md:19 | 1226 | unresolved | no distinctive terms matched at any candidate |
| 106 | 2026-08-04-transport-and-mirror/plan-reply-r4.md:19 | 1226 | unresolved | no distinctive terms matched at any candidate |
| 107 | 2026-08-04-transport-and-mirror/plan-reply-r6.md:8 | 1668 | unresolved | no distinctive terms matched at any candidate |
| 108 | 2026-08-04-transport-and-mirror/plan-reply-r6.md:8 | 1668 | unresolved | no distinctive terms matched at any candidate |
| 109 | 2026-08-04-transport-and-mirror/plan-reply-r6.md:8 | 1683 | yes 4b02cb3 | quote match: "leading `+` in an exponent" |
| 110 | 2026-08-04-transport-and-mirror/plan-reply-r6.md:8 | 1683 | yes 4b02cb3 | quote match: "leading `+` in an exponent" |
| 111 | 2026-08-04-transport-and-mirror/plan-reply-r6.md:8 | 1695 | unresolved | no distinctive terms matched at any candidate |
| 112 | 2026-08-04-transport-and-mirror/plan-reply-r6.md:8 | 1695 | unresolved | no distinctive terms matched at any candidate |
| 113 | 2026-08-04-transport-and-mirror/plan-reply-r7.md:1 | 1675 | unresolved | no distinctive terms matched at any candidate |
| 114 | 2026-08-04-transport-and-mirror/plan-reply-r7.md:1 | 1675 | unresolved | no distinctive terms matched at any candidate |
| 115 | 2026-08-04-transport-and-mirror/plan-reply-r7.md:1 | 1679 | unresolved | no distinctive terms matched at any candidate |
| 116 | 2026-08-04-transport-and-mirror/plan-reply-r7.md:1 | 1679 | unresolved | no distinctive terms matched at any candidate |
| 117 | 2026-08-11-budget-flake-generator/diff-reply-r1.txt:38 | 1187-1229 | unresolved | no distinctive terms matched at any candidate |
| 118 | 2026-08-11-budget-flake-generator/diff-reply-r1.txt:38 | 1187 | unresolved | no distinctive terms matched at any candidate |
| 119 | 2026-08-11-budget-flake-generator/diff-reply-r1.txt:60 | 1181-1185 | unresolved | insufficient overlap (hits=['pending']) |
| 120 | 2026-08-11-budget-flake-generator/diff-reply-r1.txt:60 | 1181 | unresolved | no distinctive terms matched at any candidate |
| 121 | 2026-08-11-budget-flake-generator/diff-reply-r2.txt:19 | 670 | unresolved | no distinctive terms matched at any candidate |
| 122 | 2026-08-11-budget-flake-generator/diff-reply-r2.txt:24 | 659 | unresolved | no distinctive terms matched at any candidate |
| 123 | 2026-08-11-budget-flake-generator/diff-reply-r2.txt:28 | 1979 | unresolved | insufficient overlap (hits=['spelling']) |
| 124 | 2026-08-11-budget-flake-generator/diff-reply-r2.txt:30 | 2013 | unresolved | no distinctive terms matched at any candidate |
| 125 | 2026-08-11-budget-flake-generator/plan-reply-r1.txt:18 | 1158-1167 | yes e050b35 | distinctive-word overlap (4): correction, shrunk, across, cycles |
| 126 | 2026-08-11-budget-flake-generator/plan-reply-r1.txt:36 | 1169-1184 | unresolved | insufficient overlap (hits=['warning']) |
| 127 | 2026-08-11-budget-flake-generator/plan-reply-r1.txt:63 | 1129-1142 | yes e050b35 | distinctive-word overlap (5): expectation, re-measure, unchanged, branch, repair |
| 128 | 2026-08-11-budget-flake-generator/plan-reply-r1.txt:100 | 624-635 | unresolved | insufficient overlap (hits=['generated']) |
| 129 | 2026-08-11-budget-flake-generator/plan-reply-r1.txt:130 | 1169-1184 | unresolved | insufficient overlap (hits=['warning']) |
| 130 | 2026-08-11-budget-flake-generator/plan-reply-r1.txt:159 | 603-628 | yes e050b35 | distinctive-word overlap (5): powershell, evidence, problem, written, defect |
| 131 | 2026-08-11-budget-flake-generator/plan-reply-r11.txt:1 | 603-650 | unresolved | insufficient overlap (hits=['correctly', 'parsers']) |
| 132 | 2026-08-11-budget-flake-generator/plan-reply-r12.txt:3 | 603-650 | unresolved | insufficient overlap (hits=['correct']) |
| 133 | 2026-08-11-budget-flake-generator/plan-reply-r2.txt:114 | 603-628 | yes e050b35 | distinctive-word overlap (4): powershell, evidence, problem, design |
| 134 | 2026-08-11-budget-flake-generator/plan-reply-r3.txt:23 | 1158-1161 | unresolved | insufficient overlap (hits=['failure', 'warning']) |
| 135 | 2026-08-11-budget-flake-generator/plan-reply-r3.txt:31 | 1169-1172 | unresolved | insufficient overlap (hits=['load-bearing']) |
| 136 | 2026-08-11-tool-surface-agy-drift/diff-reply-r1.txt:13 | 593-600 | unresolved | no distinctive terms matched at any candidate |
| 137 | 2026-08-11-tool-surface-agy-drift/diff-reply-r1.txt:13 | 2567-2588 | yes ac7dc43 | distinctive-word overlap (5): model-prompting-notes, multi-model-verify, references, prompting, skills |
| 138 | 2026-08-11-tool-surface-agy-drift/diff-reply-r1.txt:36 | 2593-2600 | yes 835226b | distinctive-word overlap (6): debate-protocol, verification, references, section, surface, outside |
| 139 | 2026-08-11-tool-surface-agy-drift/diff-reply-r1.txt:44 | 957-963 | yes 835226b | distinctive-word overlap (5): breakage, boundary, observed, baseline, measured |
| 140 | 2026-08-11-tool-surface-agy-drift/diff-reply-r1.txt:44 | 964-966 | yes 835226b | distinctive-word overlap (3): pre-dispatch, transcript, exists |
| 141 | 2026-08-11-tool-surface-agy-drift/diff-reply-r1.txt:44 | 968-973 | yes ac7dc43 | distinctive-word overlap (4): allownonworkspaceaccess, flash-implementer, implementer, agents |
| 142 | 2026-08-11-tool-surface-agy-drift/diff-reply-r1.txt:56 | 2473-2498 | yes ac7dc43 | distinctive-word overlap (3): unmeasured, written, itself |
| 143 | 2026-08-11-tool-surface-agy-drift/diff-reply-r1.txt:56 | 2509-2531 | yes 835226b | distinctive-word overlap (3): promotion, required, written |
| 144 | 2026-08-11-tool-surface-agy-drift/diff-reply-r1.txt:56 | 2541-2557 | yes ac7dc43 | distinctive-word overlap (3): promotion, required, written |
| 145 | 2026-08-11-tool-surface-agy-drift/diff-reply-r1.txt:56 | 2567-2588 | unresolved | insufficient overlap (hits=['reachability', 'unmeasured']) |
| 146 | 2026-08-11-tool-surface-agy-drift/diff-reply-r1.txt:60 | 562-583 | yes ac7dc43 | distinctive-word overlap (7): unreported, candidate, node_repl, disabling, removes, launch |
| 147 | 2026-08-11-tool-surface-agy-drift/diff-reply-r1.txt:62 | 2602-2617 | yes 835226b | distinctive-word overlap (4): accepted, version, failed, defect |
| 148 | 2026-08-11-tool-surface-agy-drift/diff-reply-r1.txt:62 | 2625-2627 | yes 835226b | distinctive-word overlap (3): version, watcher, cannot |
| 149 | 2026-08-11-tool-surface-agy-drift/diff-reply-r1.txt:68 | 484-490 | unresolved | insufficient overlap (hits=['memories', 'feature']) |
| 150 | 2026-08-11-tool-surface-agy-drift/diff-reply-r2.txt:9 | 608-617 | yes 8b46296 | distinctive-word overlap (7): enablement, resolved, dispatch, memories, control, feature |
| 151 | 2026-08-11-tool-surface-agy-drift/diff-reply-r2.txt:23 | 2651-2656 | unresolved | no distinctive terms matched at any candidate |
| 152 | 2026-08-11-tool-surface-agy-drift/diff-reply-r2.txt:29 | 2619-2649 | yes ac7dc43 | distinctive-word overlap (9): debate-protocol, state-machine, verification, pre-existing, references, surface |
| 153 | 2026-08-11-tool-surface-agy-drift/diff-reply-r2.txt:31 | 2658-2689 | yes ac7dc43 | distinctive-word overlap (7): drift_statemachine_tests, powershell, unmeasured, hardcoded, records, harness |
| 154 | 2026-08-11-tool-surface-agy-drift/diff-reply-r3.txt:18 | 619-629 | unresolved | insufficient overlap (hits=['feature', 'surface']) |
| 155 | 2026-08-11-tool-surface-agy-drift/diff-reply-r3.txt:22 | 2743-2747 | unresolved | insufficient overlap (hits=['measured', 'resume']) |
| 156 | 2026-08-11-tool-surface-agy-drift/diff-reply-r3.txt:23 | 2707-2723 | yes ca93356 | distinctive-word overlap (3): read-codex-round-evidence, identity, resumed |
| 157 | 2026-08-11-tool-surface-agy-drift/diff-reply-r3.txt:23 | 2740-2741 | yes 8b46296 | quote match: "Every debate that spans midnight" |
| 158 | 2026-08-11-tool-surface-agy-drift/diff-reply-r4.txt:16 | 2740-2758 | yes a02618e | distinctive-word overlap (4): correction, checkpoint, same-day, records |
| 159 | 2026-08-11-tool-surface-agy-drift/diff-reply-r4.txt:18 | 2705 | unresolved | insufficient overlap (hits=['resume', 'cannot']) |
| 160 | 2026-08-11-tool-surface-agy-drift/diff-reply-r4.txt:19 | 2740-2747 | yes a02618e | distinctive-word overlap (4): unmeasured, midnight, refresh, trigger |
| 161 | 2026-08-11-tool-surface-agy-drift/diff-reply-r4.txt:19 | 2760-2762 | yes ca93356 | quote match: "only while a debate stays inside one day," |
| 162 | 2026-08-11-tool-surface-agy-drift/diff-reply-r4.txt:30 | 2705-2762 | unresolved | insufficient overlap (hits=['evidence']) |
| 163 | 2026-08-11-tool-surface-agy-drift/diff-reply-r5.txt:28 | 2740-2766 | yes 99d1961 | distinctive-word overlap (9): non-identical, workaround, guaranteed, condition, refreshed, preamble |
| 164 | 2026-08-11-tool-surface-agy-drift/diff-reply-r5.txt:32 | 2705 | yes 99d1961 | quote match: "non-identical" |
| 165 | 2026-08-11-tool-surface-agy-drift/diff-reply-r5.txt:32 | 2740-2747 | yes 99d1961 | quote match: "non-identical" |
| 166 | 2026-08-11-tool-surface-agy-drift/diff-reply-r5.txt:33 | 2740-2747 | yes 99d1961 | distinctive-word overlap (3): condition, boundary, observed |
| 167 | 2026-08-11-tool-surface-agy-drift/diff-reply-r6.txt:29 | 2705 | unresolved | insufficient overlap (hits=['non-identical', 'refreshed']) |
| 168 | 2026-08-11-tool-surface-agy-drift/diff-reply-r6.txt:29 | 2740-2747 | yes 99d1961 | distinctive-word overlap (3): non-identical, condition, refreshed |
| 169 | 2026-08-11-tool-surface-agy-drift/diff-reply-r7.txt:31 | 11-15 | yes 8c80891 | distinctive-word overlap (3): headings, source, status |
| 170 | 2026-08-11-tool-surface-agy-drift/diff-reply-r7.txt:31 | 26-27 | unresolved | no distinctive terms matched at any candidate |
| 171 | 2026-08-11-tool-surface-agy-drift/diff-reply-r7.txt:31 | 1098 | unresolved | no distinctive terms matched at any candidate |
| 172 | 2026-08-11-tool-surface-agy-drift/diff-reply-r7.txt:31 | 1185 | unresolved | no distinctive terms matched at any candidate |
| 173 | 2026-08-11-tool-surface-agy-drift/diff-reply-r7.txt:31 | 2196 | unresolved | no distinctive terms matched at any candidate |
| 174 | 2026-08-11-tool-surface-agy-drift/diff-reply-r7.txt:31 | 2225 | unresolved | no distinctive terms matched at any candidate |
| 175 | 2026-08-11-tool-surface-agy-drift/diff-reply-r7.txt:32 | 2947-2951 | unresolved | insufficient overlap (hits=['separate']) |
| 176 | 2026-08-11-tool-surface-agy-drift/diff-reply-r7.txt:33 | 3205-3210 | yes e713081 | distinctive-word overlap (3): drift_statemachine_tests, new-kimi-lane-login, powershell |
| 177 | 2026-08-11-tool-surface-agy-drift/diff-reply-r7.txt:33 | 3249-3251 | yes e713081 | distinctive-word overlap (4): drift_statemachine_tests, invoke-drift, powershell, hardcodes |
| 178 | 2026-08-11-tool-surface-agy-drift/diff-reply-r7.txt:40 | 2971-2979 | unresolved | insufficient overlap (hits=['fable-advisor']) |
| 179 | 2026-08-11-tool-surface-agy-drift/diff-reply-r7.txt:40 | 3151-3159 | unresolved | insufficient overlap (hits=['fable-advisor', 'changes']) |
| 180 | 2026-08-11-tool-surface-agy-drift/diff-reply-r7.txt:41 | 1120-1137 | yes 8c80891 | distinctive-word overlap (3): service_tier, screenshot, itself |
| 181 | 2026-08-11-tool-surface-agy-drift/diff-reply-r8.txt:3 | 1106 | unresolved | no distinctive terms matched at any candidate |
| 182 | 2026-08-11-tool-surface-agy-drift/diff-reply-r8.txt:3 | 1193 | unresolved | no distinctive terms matched at any candidate |
| 183 | 2026-08-11-tool-surface-agy-drift/diff-reply-r8.txt:3 | 2204 | unresolved | no distinctive terms matched at any candidate |
| 184 | 2026-08-11-tool-surface-agy-drift/diff-reply-r8.txt:3 | 2233 | unresolved | no distinctive terms matched at any candidate |
| 185 | 2026-08-11-tool-surface-agy-drift/diff-reply-r8.txt:3 | 25 | unresolved | no distinctive terms matched at any candidate |
| 186 | 2026-08-11-tool-surface-agy-drift/diff-reply-r8.txt:3 | 31 | unresolved | insufficient overlap (hits=['closed']) |
| 187 | 2026-08-11-tool-surface-agy-drift/diff-reply-r8.txt:3 | 33 | unresolved | no distinctive terms matched at any candidate |
| 188 | 2026-08-11-tool-surface-agy-drift/diff-reply-r8.txt:3 | 34 | unresolved | no distinctive terms matched at any candidate |
| 189 | 2026-08-11-tool-surface-agy-drift/diff-reply-r8.txt:3 | 17-23 | unresolved | insufficient overlap (hits=['headings', 'status']) |
| 190 | 2026-08-11-tool-surface-agy-drift/diff-reply-r8.txt:7 | 2955-2964 | yes 8c80891 | quote match: "the gate run that preceded the round-6 fixes" |
| 191 | 2026-08-11-tool-surface-agy-drift/diff-reply-r8.txt:17 | 3233-3240 | yes 8c80891 | distinctive-word overlap (7): scheduled-task, check-drift, powershell, migration, identity, watcher |
| 192 | 2026-08-11-tool-surface-agy-drift/diff-reply-r8.txt:18 | 3318-3327 | yes 8c80891 | distinctive-word overlap (6): new-kimi-lane-login, arguments, argument, re-exec, working, itself |
| 193 | 2026-08-11-tool-surface-agy-drift/diff-reply-r8.txt:19 | 3279-3306 | yes fd87657 | distinctive-word overlap (10): test_multi_model_verify, multi-model-verify, new-review-mirror, brief-encoding, independently, powershell |
| 194 | 2026-08-11-tool-surface-agy-drift/diff-reply-r8.txt:20 | 3285-3289 | yes fd87657 | distinctive-word overlap (6): hookspath, installed, pre-push, checkout, sample, active |
| 195 | 2026-08-11-tool-surface-agy-drift/diff-reply-r8.txt:26 | 3285 | unresolved | no distinctive terms matched at any candidate |
| 196 | 2026-08-11-tool-surface-agy-drift/diff-reply-r8.txt:38 | 2955-2964 | unresolved | no distinctive terms matched at any candidate |
| 197 | 2026-08-11-tool-surface-agy-drift/fable-review-1-ef428c3-5133f98.md:36 | 526 | unresolved | insufficient overlap (hits=['failure']) |
| 198 | 2026-08-11-tool-surface-agy-drift/plan-reply-r1.txt:7 | 510-519 | unresolved | insufficient overlap (hits=['parsing', 'levers']) |
| 199 | 2026-08-11-tool-surface-agy-drift/plan-reply-r1.txt:13 | 779-785 | yes 4be7eee | distinctive-word overlap (5): drift-snapshot, contracts, snapshot, version, records |
| 200 | 2026-08-11-tool-surface-agy-drift/plan-reply-r2.txt:23 | 787-800 | yes 5737d4d | distinctive-word overlap (9): flash-implementer, approval-bypass, persisted, security, evidence, property |
| 201 | 2026-08-11-tool-surface-agy-drift/plan-reply-r3.txt:17 | 787-800 | unresolved | insufficient overlap (hits=['reachability', 'doctor']) |
| 202 | 2026-08-11-tool-surface-agy-drift/plan-reply-r4.txt:5 | 787-800 | yes e876ca8 | distinctive-word overlap (7): flash-implementer, reachability, commands, security, property, doctor |
| 203 | 2026-08-16-fresh-preamble-gate/diff-debate-r1.md:60 | 3712 | unresolved | no distinctive terms matched at any candidate |
| 204 | 2026-08-16-fresh-preamble-gate/diff-debate-r1.md:114 | 3712 | unresolved | no distinctive terms matched at any candidate |
| 205 | 2026-08-16-fresh-preamble-gate/diff-debate-r1.md:114 | 4052 | unresolved | no distinctive terms matched at any candidate |
| 206 | 2026-08-16-fresh-preamble-gate/diff-debate-r1.md:118 | 3987 | unresolved | no distinctive terms matched at any candidate |
| 207 | 2026-08-16-fresh-preamble-gate/diff-debate-r1.md:124 | 3940 | unresolved | no distinctive terms matched at any candidate |
| 208 | 2026-08-16-fresh-preamble-gate/diff-debate-r2.md:55 | 4071 | unresolved | no distinctive terms matched at any candidate |
| 209 | 2026-08-16-fresh-preamble-gate/diff-debate-r2.md:66 | 4093 | unresolved | no distinctive terms matched at any candidate |
| 210 | 2026-08-16-fresh-preamble-gate/diff-debate-r2.md:84 | 4086 | unresolved | insufficient overlap (hits=['filter']) |
| 211 | 2026-08-16-fresh-preamble-gate/diff-debate-r2.md:85 | 4077 | unresolved | no distinctive terms matched at any candidate |
| 212 | 2026-08-16-fresh-preamble-gate/diff-debate-r2.md:85 | 202 | unresolved | no distinctive terms matched at any candidate |
| 213 | 2026-08-16-fresh-preamble-gate/diff-debate-r3.md:47 | 4067 | unresolved | insufficient overlap (hits=['read-codex-round-evidence', 'test-recordisusermessage']) |
| 214 | 2026-08-16-fresh-preamble-gate/diff-debate-r3.md:49 | 4061 | unresolved | no distinctive terms matched at any candidate |
| 215 | 2026-08-16-fresh-preamble-gate/diff-debate-r3.md:49 | 4104 | unresolved | insufficient overlap (hits=['records']) |
| 216 | 2026-08-16-fresh-preamble-gate/diff-debate-r3.md:49 | 31 | unresolved | no distinctive terms matched at any candidate |
| 217 | 2026-08-16-fresh-preamble-gate/diff-debate-r3.md:51 | 4112 | unresolved | no distinctive terms matched at any candidate |
| 218 | 2026-08-16-fresh-preamble-gate/diff-debate-r4.md:81 | 4067 | yes cefa969 | distinctive-word overlap (3): read-codex-round-evidence, test-recordisusermessage, round- |
| 219 | 2026-08-16-fresh-preamble-gate/diff-debate-r4.md:82 | 4131 | unresolved | no distinctive terms matched at any candidate |
| 220 | 2026-08-16-fresh-preamble-gate/diff-debate-r5b.md:58 | 4067 | unresolved | insufficient overlap (hits=['read-codex-round-evidence']) |
| 221 | 2026-08-16-fresh-preamble-gate/plan-debate-r2.md:40 | 214 | unresolved | no distinctive terms matched at any candidate |
| 222 | 2026-08-16-fresh-preamble-gate/plan-debate-r2.md:40 | 2128 | unresolved | insufficient overlap (hits=['closed']) |
| 223 | 2026-08-16-fresh-preamble-gate/plan-debate-r2.md:40 | 4081 | unresolved | no distinctive terms matched at any candidate |
| 224 | 2026-08-16-fresh-preamble-gate/plan-debate-r2.md:54 | 195 | unresolved | no distinctive terms matched at any candidate |
| 225 | 2026-08-16-fresh-preamble-gate/plan-debate-r2.md:58 | 1172 | unresolved | no distinctive terms matched at any candidate |
| 226 | 2026-08-16-fresh-preamble-gate/plan-debate-r2.md:58 | 1639 | unresolved | no distinctive terms matched at any candidate |
| 227 | 2026-08-16-fresh-preamble-gate/plan-debate-r2.md:58 | 2160 | unresolved | no distinctive terms matched at any candidate |
| 228 | 2026-08-16-fresh-preamble-gate/plan-debate-r2.md:58 | 3461 | unresolved | no distinctive terms matched at any candidate |
| 229 | 2026-08-16-fresh-preamble-gate/plan-debate-r3.md:33 | 25 | unresolved | no distinctive terms matched at any candidate |
| 230 | 2026-08-16-fresh-preamble-gate/plan-debate-r3.md:33 | 31 | unresolved | no distinctive terms matched at any candidate |
| 231 | 2026-08-16-fresh-preamble-gate/plan-debate-r3.md:33 | 33 | unresolved | no distinctive terms matched at any candidate |
| 232 | 2026-08-16-fresh-preamble-gate/plan-debate-r3.md:33 | 34 | unresolved | no distinctive terms matched at any candidate |
| 233 | 2026-08-16-fresh-preamble-gate/plan-debate-r3.md:35 | 49 | unresolved | no distinctive terms matched at any candidate |
| 234 | 2026-08-16-fresh-preamble-gate/plan-debate-r3.md:35 | 214 | unresolved | no distinctive terms matched at any candidate |
| 235 | 2026-08-16-fresh-preamble-gate/plan-debate-r3.md:37 | 191 | unresolved | no distinctive terms matched at any candidate |
| 236 | 2026-08-16-fresh-preamble-gate/plan-debate-r3.md:49 | 31 | unresolved | insufficient overlap (hits=['partially', 'closed']) |
| 237 | 2026-08-16-fresh-preamble-gate/plan-debate-r3.md:49 | 34 | unresolved | no distinctive terms matched at any candidate |
| 238 | 2026-08-16-fresh-preamble-gate/plan-debate-r3.md:49 | 96 | unresolved | no distinctive terms matched at any candidate |
| 239 | 2026-08-16-fresh-preamble-gate/plan-debate-r3.md:49 | 100 | unresolved | no distinctive terms matched at any candidate |
| 240 | 2026-08-16-fresh-preamble-gate/plan-debate-r3.md:49 | 195 | unresolved | insufficient overlap (hits=['closed']) |
| 241 | 2026-08-16-fresh-preamble-gate/plan-debate-r4.md:36 | 62 | unresolved | no distinctive terms matched at any candidate |
| 242 | 2026-08-16-fresh-preamble-gate/plan-debate-r4.md:36 | 109 | unresolved | insufficient overlap (hits=['second']) |
| 243 | 2026-08-16-fresh-preamble-gate/plan-debate-r4.md:36 | 124 | unresolved | no distinctive terms matched at any candidate |
| 244 | 2026-08-16-fresh-preamble-gate/plan-debate-r4.md:36 | 163 | unresolved | insufficient overlap (hits=['fourth']) |
| 245 | 2026-08-16-fresh-preamble-gate/plan-debate-r4.md:36 | 185 | unresolved | no distinctive terms matched at any candidate |
| 246 | 2026-08-16-fresh-preamble-gate/plan-debate-r4.md:36 | 194 | unresolved | no distinctive terms matched at any candidate |
| 247 | 2026-08-16-fresh-preamble-gate/plan-debate-r5.md:37 | 34 | unresolved | no distinctive terms matched at any candidate |
| 248 | 2026-08-16-fresh-preamble-gate/plan-debate-r5.md:37 | 3696 | unresolved | no distinctive terms matched at any candidate |
| 249 | 2026-08-16-fresh-preamble-gate/plan-debate-r5.md:37 | 3938 | unresolved | no distinctive terms matched at any candidate |
| 250 | 2026-08-16-fresh-preamble-gate/plan-debate-r5.md:37 | 3985 | unresolved | insufficient overlap (hits=['partially', 'closed']) |
| 251 | 2026-08-16-fresh-preamble-gate/plan-debate-r5.md:39 | 196 | unresolved | no distinctive terms matched at any candidate |
| 252 | 2026-08-16-fresh-preamble-gate/plan-debate-r5.md:39 | 211 | unresolved | no distinctive terms matched at any candidate |
| 253 | 2026-08-16-fresh-preamble-gate/plan-debate-r5.md:52 | 4173 | unresolved | insufficient overlap (hits=['negative', 'lexical']) |
| 254 | 2026-08-16-fresh-preamble-gate/plan-debate-r5.md:56 | 4149 | unresolved | insufficient overlap (hits=['skill-evals']) |
| 255 | 2026-08-16-fresh-preamble-gate/plan-debate-r5.md:58 | 4155 | unresolved | no distinctive terms matched at any candidate |
| 256 | 2026-08-16-fresh-preamble-gate/plan-debate-r5.md:60 | 4160 | unresolved | no distinctive terms matched at any candidate |
| 257 | 2026-08-16-fresh-preamble-gate/plan-debate-r5.md:62 | 4168 | unresolved | insufficient overlap (hits=['test_multi_model_verify', 'schema']) |
| 258 | 2026-08-16-fresh-preamble-gate/plan-debate-r6.md:48 | 3000 | unresolved | no distinctive terms matched at any candidate |
| 259 | 2026-08-16-fresh-preamble-gate/plan-debate-r6.md:48 | 3006 | unresolved | no distinctive terms matched at any candidate |
| 260 | 2026-08-16-fresh-preamble-gate/plan-debate-r6.md:52 | 4185 | yes fe3a831 | quote match: "four wrong citations" |
| 261 | 2026-08-19-resume-not-guaranteed/sol-r1-reply.md:14 | 4596-4608 | yes 63a9b3a | distinctive-word overlap (4): continuity, condition, answer, panels |
| 262 | 2026-08-19-resume-not-guaranteed/sol-r1-reply.md:14 | 4596 | unresolved | insufficient overlap (hits=['continuity', 'panels']) |
| 263 | 2026-08-19-resume-not-guaranteed/sol-r1-reply.md:15 | 4622-4627 | yes 63a9b3a | distinctive-word overlap (7): frozen-plan-format, re-dispatched, fallbacks, consented, verdict, format |
| 264 | 2026-08-19-resume-not-guaranteed/sol-r1-reply.md:15 | 4622 | unresolved | insufficient overlap (hits=['frozen-plan-format', 'format']) |
| 265 | 2026-08-19-resume-not-guaranteed/sol-r1-reply.md:17 | 4589-4594 | yes 63a9b3a | distinctive-word overlap (6): deliberately, follow-up, accepted, contract, surface, closing |
| 266 | 2026-08-19-resume-not-guaranteed/sol-r1-reply.md:17 | 4589 | unresolved | no distinctive terms matched at any candidate |
| 267 | 2026-08-19-resume-not-guaranteed/sol-r1-reply.md:38 | 4589-4620 | yes 63a9b3a | distinctive-word overlap (4): frozen-plan, follow-up, accepted, contract |
| 268 | 2026-08-19-resume-not-guaranteed/sol-r1-reply.md:38 | 4589 | unresolved | no distinctive terms matched at any candidate |
| 269 | 2026-08-19-resume-not-guaranteed/sol-r2-reply.md:23 | 4602-4608 | yes 63a9b3a | distinctive-word overlap (3): recall, answer, panels |
| 270 | 2026-08-19-resume-not-guaranteed/sol-r2-reply.md:23 | 4602 | unresolved | no distinctive terms matched at any candidate |
| 271 | 2026-08-19-resume-not-guaranteed/sol-r2-reply.md:24 | 4622-4627 | yes 63a9b3a | distinctive-word overlap (3): fallbacks, format, cannot |
| 272 | 2026-08-19-resume-not-guaranteed/sol-r2-reply.md:24 | 4622 | unresolved | insufficient overlap (hits=['format']) |
| 273 | 2026-08-19-resume-not-guaranteed/sol-r2-reply.md:26 | 4589-4594 | unresolved | insufficient overlap (hits=['follow-up', 'accepted']) |
| 274 | 2026-08-19-resume-not-guaranteed/sol-r2-reply.md:26 | 4589 | unresolved | no distinctive terms matched at any candidate |
| 275 | 2026-08-19-resume-not-guaranteed/sol-r2-reply.md:34 | 4589-4627 | unresolved | insufficient overlap (hits=['instance']) |
| 276 | 2026-08-19-resume-not-guaranteed/sol-r2-reply.md:34 | 4589 | unresolved | no distinctive terms matched at any candidate |
| 277 | 2026-08-22-item48-plan-debate/sol-reply-r1.md:27 | 3531-3532 | yes 69779a2 | quote match: "Anything a subagent or skill instructs to be run" |
| 278 | 2026-08-22-item48-plan-debate/sol-reply-r1.md:64 | 3534-3543 | yes 69779a2 | quote match: "Does 7 exist everywhere this must run?" |
| 279 | 2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:289 | 3748 | unresolved | no distinctive terms matched at any candidate |
| 280 | 2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:1671 | 3456 | unresolved | no distinctive terms matched at any candidate |
| 281 | 2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:1734 | 3485 | unresolved | no distinctive terms matched at any candidate |
| 282 | 2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:1767 | 3473 | unresolved | no distinctive terms matched at any candidate |
| 283 | 2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:2076 | 3561 | yes 39408ac | quote match: "what does the test matrix become" |
| 284 | 2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:2089 | 3380 | unresolved | no distinctive terms matched at any candidate |
| 285 | 2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:2100 | 3098 | unresolved | no distinctive terms matched at any candidate |
| 286 | 2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:2549 | 3748 | unresolved | insufficient overlap (hits=['mangled', 'inline']) |
| 287 | 2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:2550 | 2510 | unresolved | no distinctive terms matched at any candidate |
| 288 | 2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:2640 | 3750 | unresolved | no distinctive terms matched at any candidate |
| 289 | 2026-08-30-item32-plan-debate/fable-reply-r1.md:11 | 4496 | yes 28802bd | quote match: "Shape of a fix, none decided" |
| 290 | 2026-08-30-item32-plan-debate/fable-reply-r2.md:9 | 4496 | yes 28802bd | quote match: "none decided" |
| 291 | 2026-08-30-item32-plan-debate/sol-reply-r2.md:94 | 2674-2681 | unresolved | insufficient overlap (hits=['whether']) |
| 292 | 2026-08-30-item32-plan-debate/sol-reply-r5.md:3 | 4430-4455 | unresolved | insufficient overlap (hits=['reviewed', 'records']) |
| 293 | 2026-08-30-item32-plan-debate/sol-reply-r5.md:3 | 4457-4460 | unresolved | insufficient overlap (hits=['plugin']) |
| 294 | 2026-08-30-item32-plan-debate/sol-reply-r5.md:3 | 4475-4485 | yes 28802bd | distinctive-word overlap (4): claude_plugin_root, mechanism, resolve, plugin |
| 295 | 2026-08-30-item32-plan-debate/sol-reply-r5.md:7 | 4449-4455 | unresolved | no distinctive terms matched at any candidate |
| 296 | 2026-08-30-item32-plan-debate/sol-reply-r5.md:7 | 4487-4488 | unresolved | no distinctive terms matched at any candidate |
| 297 | 2026-08-30-item32-plan-debate/sol-reply-r6.md:48 | 4440-4455 | unresolved | no distinctive terms matched at any candidate |
| 298 | 2026-08-30-item32-plan-debate/sol-reply-r6.md:48 | 4457-4480 | yes 28802bd | distinctive-word overlap (5): claude_plugin_root, repository, mechanism, reviewed, resolve |
| 299 | 2026-08-30-item32-plan-debate/sol-reply-r6.md:62 | 4427-4438 | unresolved | insufficient overlap (hits=['exists']) |
| 300 | 2026-08-31-completion-coupled-dispatch/fable-whole-branch-review-8af6ae0..3029599.md:38 | 4829-4854 | yes c0ef41a | distinctive-word overlap (4): executor, harness, branch, cannot |
| 301 | 2026-08-31-completion-coupled-dispatch/kimi-plan-review-r1.md:19 | 4018-4027 | yes fbdcd13 | quote match: "three recorded values BEFORE EVERY fresh and resumed dispatch" |
| 302 | 2026-08-31-completion-coupled-dispatch/sol-diff-debate-r1.md:79 | 4909-4910 | unresolved | insufficient overlap (hits=['round-dispatch-operation', 'model-prompting-notes']) |
| 303 | 2026-08-31-completion-coupled-dispatch/sol-diff-debate-r2.md:69 | 4909-4910 | unresolved | no distinctive terms matched at any candidate |
| 304 | 2026-09-03-item74-diff-debate/fable-diff-r2-reply.md:28 | 400-401 | unresolved | insufficient overlap (hits=['bullet', 'effort']) |
| 305 | 2026-09-03-item74-diff-debate/fable-diff-r3-reply.md:39 | 48-50 | yes b9c17bc | quote match: "never added to the ranking. They ARE in the Open list above" |
| 306 | 2026-09-03-item74-diff-debate/fable-diff-r5-reply.md:33 | 5314-5317 | yes 233a340 | quote match: "pushed the bullet below its old range" |
| 307 | 2026-09-03-item74-diff-debate/fable-diff-r9-reply.md:35 | 5557-5569 | yes 20d557a | distinctive-word overlap (4): instance, narrowed, records, account |
| 308 | 2026-09-03-item74-diff-debate/sol-diff-r1-reply.md:22 | 388 | unresolved | no distinctive terms matched at any candidate |
| 309 | 2026-09-03-item74-diff-debate/sol-diff-r1-reply.md:28 | 41 | unresolved | no distinctive terms matched at any candidate |
| 310 | 2026-09-03-item74-diff-debate/sol-diff-r1-reply.md:28 | 145 | unresolved | no distinctive terms matched at any candidate |
| 311 | 2026-09-03-item74-diff-debate/sol-diff-r1-reply.md:28 | 211 | unresolved | no distinctive terms matched at any candidate |
| 312 | 2026-09-03-item74-diff-debate/sol-diff-r1-reply.md:28 | 286 | unresolved | no distinctive terms matched at any candidate |
| 313 | 2026-09-03-item74-diff-debate/sol-diff-r1-reply.md:28 | 363 | unresolved | no distinctive terms matched at any candidate |
| 314 | 2026-09-03-item74-diff-debate/sol-diff-r1-reply.md:28 | 506 | unresolved | no distinctive terms matched at any candidate |
| 315 | 2026-09-03-item74-diff-debate/sol-diff-r1-reply.md:28 | 615 | unresolved | no distinctive terms matched at any candidate |
| 316 | 2026-09-03-item74-diff-debate/sol-diff-r1-reply.md:28 | 716 | unresolved | no distinctive terms matched at any candidate |
| 317 | 2026-09-03-item74-diff-debate/sol-diff-r1-reply.md:32 | 121 | unresolved | no distinctive terms matched at any candidate |
| 318 | 2026-09-03-item74-diff-debate/sol-diff-r1-reply.md:32 | 157 | unresolved | no distinctive terms matched at any candidate |
| 319 | 2026-09-03-item74-diff-debate/sol-diff-r1-reply.md:33 | 219 | unresolved | no distinctive terms matched at any candidate |
| 320 | 2026-09-03-item74-diff-debate/sol-diff-r1-reply.md:33 | 226 | unresolved | no distinctive terms matched at any candidate |
| 321 | 2026-09-03-item74-diff-debate/sol-diff-r1-reply.md:34 | 151 | unresolved | no distinctive terms matched at any candidate |
| 322 | 2026-09-03-item74-diff-debate/sol-diff-r1-reply.md:34 | 506 | unresolved | no distinctive terms matched at any candidate |
| 323 | 2026-09-03-item74-diff-debate/sol-diff-r1-reply.md:34 | 526 | unresolved | no distinctive terms matched at any candidate |
| 324 | 2026-09-03-item74-diff-debate/sol-diff-r1-reply.md:34 | 543 | unresolved | no distinctive terms matched at any candidate |
| 325 | 2026-09-03-item74-diff-debate/sol-diff-r1-reply.md:42 | 121 | unresolved | no distinctive terms matched at any candidate |
| 326 | 2026-09-03-item74-diff-debate/sol-diff-r2-reply.md:13 | 126 | unresolved | no distinctive terms matched at any candidate |
| 327 | 2026-09-03-item74-diff-debate/sol-diff-r2-reply.md:13 | 161 | unresolved | no distinctive terms matched at any candidate |
| 328 | 2026-09-03-item74-diff-debate/sol-diff-r2-reply.md:13 | 191 | unresolved | no distinctive terms matched at any candidate |
| 329 | 2026-09-03-item74-diff-debate/sol-diff-r2-reply.md:13 | 231 | unresolved | no distinctive terms matched at any candidate |
| 330 | 2026-09-03-item74-diff-debate/sol-diff-r2-reply.md:13 | 565 | unresolved | no distinctive terms matched at any candidate |
| 331 | 2026-09-03-item74-diff-debate/sol-diff-r2-reply.md:13 | 43 | unresolved | no distinctive terms matched at any candidate |
| 332 | 2026-09-03-item74-diff-debate/sol-diff-r2-reply.md:13 | 47 | unresolved | insufficient overlap (hits=['ranking']) |
| 333 | 2026-09-03-item74-diff-debate/sol-diff-r2-reply.md:15 | 333 | unresolved | no distinctive terms matched at any candidate |
| 334 | 2026-09-03-item74-diff-debate/sol-diff-r2-reply.md:15 | 334 | unresolved | no distinctive terms matched at any candidate |
| 335 | 2026-09-03-item74-diff-debate/sol-diff-r2-reply.md:15 | 5579 | unresolved | no distinctive terms matched at any candidate |
| 336 | 2026-09-03-item74-diff-debate/sol-diff-r2-reply.md:15 | 5606 | unresolved | no distinctive terms matched at any candidate |
| 337 | 2026-09-03-item74-diff-debate/sol-diff-r2-reply.md:15 | 5644 | unresolved | insufficient overlap (hits=['ranking']) |
| 338 | 2026-09-03-item74-diff-debate/sol-diff-r2-reply.md:15 | 155 | unresolved | no distinctive terms matched at any candidate |
| 339 | 2026-09-03-item74-diff-debate/sol-diff-r2-reply.md:15 | 370 | unresolved | no distinctive terms matched at any candidate |
| 340 | 2026-09-03-item74-diff-debate/sol-diff-r2-reply.md:19 | 45 | unresolved | no distinctive terms matched at any candidate |
| 341 | 2026-09-03-item74-diff-debate/sol-diff-r2-reply.md:19 | 51 | unresolved | no distinctive terms matched at any candidate |
| 342 | 2026-09-03-item74-diff-debate/sol-diff-r2-reply.md:19 | 333 | unresolved | no distinctive terms matched at any candidate |
| 343 | 2026-09-03-item74-diff-debate/sol-diff-r2-reply.md:23 | 48 | unresolved | no distinctive terms matched at any candidate |
| 344 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:13 | 47 | unresolved | insufficient overlap (hits=['ranking']) |
| 345 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:13 | 49 | unresolved | insufficient overlap (hits=['ranking']) |
| 346 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:14 | 420 | unresolved | insufficient overlap (hits=['general']) |
| 347 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:15 | 421 | unresolved | no distinctive terms matched at any candidate |
| 348 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:16 | 336 | unresolved | no distinctive terms matched at any candidate |
| 349 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:16 | 339 | unresolved | no distinctive terms matched at any candidate |
| 350 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:17 | 52 | unresolved | no distinctive terms matched at any candidate |
| 351 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:17 | 57 | unresolved | no distinctive terms matched at any candidate |
| 352 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:18 | 59 | unresolved | no distinctive terms matched at any candidate |
| 353 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:18 | 3239 | unresolved | no distinctive terms matched at any candidate |
| 354 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:24 | 3480 | yes b9c17bc | distinctive-word overlap (4): model-prompting-notes, multi-model-verify, references, skills |
| 355 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:25 | 4994 | yes b9c17bc | distinctive-word overlap (3): codex-tool-surface-probe, model-prompting-notes, references |
| 356 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:26 | 5291 | yes b9c17bc | distinctive-word overlap (4): model-prompting-notes, multi-model-verify, references, skills |
| 357 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:27 | 5308 | unresolved | insufficient overlap (hits=['model-prompting-notes']) |
| 358 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:28 | 5322 | unresolved | no distinctive terms matched at any candidate |
| 359 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:32 | 379 | unresolved | no distinctive terms matched at any candidate |
| 360 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:32 | 389 | unresolved | no distinctive terms matched at any candidate |
| 361 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:32 | 404 | unresolved | no distinctive terms matched at any candidate |
| 362 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:32 | 422 | unresolved | insufficient overlap (hits=['reasoning_extraction']) |
| 363 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:32 | 462 | unresolved | insufficient overlap (hits=['resume']) |
| 364 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:34 | 43 | unresolved | no distinctive terms matched at any candidate |
| 365 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:34 | 158 | unresolved | no distinctive terms matched at any candidate |
| 366 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:34 | 226 | unresolved | no distinctive terms matched at any candidate |
| 367 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:34 | 379 | unresolved | no distinctive terms matched at any candidate |
| 368 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:34 | 523 | unresolved | no distinctive terms matched at any candidate |
| 369 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:34 | 633 | unresolved | no distinctive terms matched at any candidate |
| 370 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:34 | 734 | unresolved | no distinctive terms matched at any candidate |
| 371 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:34 | 45 | unresolved | insufficient overlap (hits=['stated']) |
| 372 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:34 | 63 | yes b9c17bc | distinctive-word overlap (3): partially, ranked, closed |
| 373 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:34 | 67 | unresolved | insufficient overlap (hits=['stated']) |
| 374 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:36 | 420 | unresolved | insufficient overlap (hits=['general']) |
| 375 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:38 | 47 | unresolved | no distinctive terms matched at any candidate |
| 376 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:42 | 3480 | unresolved | insufficient overlap (hits=['model-prompting-notes', 'references']) |
| 377 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:42 | 4994 | unresolved | insufficient overlap (hits=['model-prompting-notes', 'references']) |
| 378 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:42 | 5291 | unresolved | insufficient overlap (hits=['model-prompting-notes', 'references']) |
| 379 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:42 | 5308 | unresolved | insufficient overlap (hits=['model-prompting-notes']) |
| 380 | 2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:42 | 5322 | unresolved | no distinctive terms matched at any candidate |
| 381 | 2026-09-03-item74-diff-debate/sol-diff-r4-reply.md:13 | 5542 | unresolved | insufficient overlap (hits=['model-prompting-notes']) |
| 382 | 2026-09-03-item74-diff-debate/sol-diff-r4-reply.md:13 | 5544 | unresolved | no distinctive terms matched at any candidate |
| 383 | 2026-09-03-item74-diff-debate/sol-diff-r4-reply.md:13 | 5546 | unresolved | no distinctive terms matched at any candidate |
| 384 | 2026-09-03-item74-diff-debate/sol-diff-r4-reply.md:13 | 5312 | unresolved | insufficient overlap (hits=['model-prompting-notes']) |
| 385 | 2026-09-03-item74-diff-debate/sol-diff-r4-reply.md:15 | 5307 | unresolved | insufficient overlap (hits=['resume', 'bullet']) |
| 386 | 2026-09-03-item74-diff-debate/sol-diff-r4-reply.md:17 | 3480 | unresolved | insufficient overlap (hits=['references']) |
| 387 | 2026-09-03-item74-diff-debate/sol-diff-r4-reply.md:17 | 4994 | unresolved | insufficient overlap (hits=['references']) |
| 388 | 2026-09-03-item74-diff-debate/sol-diff-r4-reply.md:17 | 5291 | unresolved | insufficient overlap (hits=['references']) |
| 389 | 2026-09-03-item74-diff-debate/sol-diff-r4-reply.md:17 | 5329 | unresolved | no distinctive terms matched at any candidate |
| 390 | 2026-09-03-item74-diff-debate/sol-diff-r4-reply.md:17 | 5536 | unresolved | no distinctive terms matched at any candidate |
| 391 | 2026-09-03-item74-diff-debate/sol-diff-r4-reply.md:17 | 5558 | unresolved | insufficient overlap (hits=['checker']) |
| 392 | 2026-09-03-item74-diff-debate/sol-diff-r4-reply.md:19 | 5558 | unresolved | insufficient overlap (hits=['branch']) |
| 393 | 2026-09-03-item74-diff-debate/sol-diff-r4-reply.md:19 | 5551 | unresolved | no distinctive terms matched at any candidate |
| 394 | 2026-09-03-item74-diff-debate/sol-diff-r4-reply.md:21 | 5312 | unresolved | insufficient overlap (hits=['model-prompting-notes']) |
| 395 | 2026-09-03-item74-diff-debate/sol-diff-r4-reply.md:21 | 5539 | unresolved | no distinctive terms matched at any candidate |
| 396 | 2026-09-03-item74-diff-debate/sol-diff-r4-reply.md:21 | 5542 | unresolved | insufficient overlap (hits=['model-prompting-notes']) |
| 397 | 2026-09-03-item74-diff-debate/sol-diff-r4-reply.md:23 | 5305 | unresolved | no distinctive terms matched at any candidate |
| 398 | 2026-09-03-item74-diff-debate/sol-diff-r4-reply.md:23 | 5536 | unresolved | no distinctive terms matched at any candidate |
| 399 | 2026-09-03-item74-diff-debate/sol-diff-r4-reply.md:25 | 5536 | unresolved | no distinctive terms matched at any candidate |
| 400 | 2026-09-03-item74-diff-debate/sol-diff-r4-reply.md:27 | 5551 | unresolved | no distinctive terms matched at any candidate |
| 401 | 2026-09-03-item74-diff-debate/sol-diff-r5-reply.md:20 | 5312 | unresolved | no distinctive terms matched at any candidate |
| 402 | 2026-09-03-item74-diff-debate/sol-diff-r5-reply.md:20 | 5312 | unresolved | no distinctive terms matched at any candidate |
| 403 | 2026-09-03-item74-diff-debate/sol-diff-r5-reply.md:22 | 5538 | unresolved | insufficient overlap (hits=['instances']) |
| 404 | 2026-09-03-item74-diff-debate/sol-diff-r5-reply.md:28 | 5541 | unresolved | insufficient overlap (hits=['retained']) |
| 405 | 2026-09-03-item74-diff-debate/sol-diff-r5-reply.md:30 | 5312 | unresolved | no distinctive terms matched at any candidate |
| 406 | 2026-09-03-item74-diff-debate/sol-diff-r5-reply.md:32 | 3480 | unresolved | insufficient overlap (hits=['references']) |
| 407 | 2026-09-03-item74-diff-debate/sol-diff-r5-reply.md:32 | 4994 | unresolved | insufficient overlap (hits=['references']) |
| 408 | 2026-09-03-item74-diff-debate/sol-diff-r5-reply.md:32 | 5291 | unresolved | insufficient overlap (hits=['references']) |
| 409 | 2026-09-03-item74-diff-debate/sol-diff-r5-reply.md:32 | 5332 | unresolved | no distinctive terms matched at any candidate |
| 410 | 2026-09-03-item74-diff-debate/sol-diff-r7-reply.md:29 | 3480 | unresolved | no distinctive terms matched at any candidate |
| 411 | 2026-09-03-item74-diff-debate/sol-diff-r7-reply.md:29 | 4994 | unresolved | no distinctive terms matched at any candidate |
| 412 | 2026-09-03-item74-diff-debate/sol-diff-r7-reply.md:29 | 5291 | unresolved | no distinctive terms matched at any candidate |
| 413 | 2026-09-03-item74-diff-debate/sol-diff-r7-reply.md:29 | 5332 | unresolved | no distinctive terms matched at any candidate |
| 414 | 2026-09-03-item74-diff-debate/sol-diff-r7-reply.md:32 | 379 | unresolved | no distinctive terms matched at any candidate |
| 415 | 2026-09-03-item74-diff-debate/sol-diff-r7-reply.md:32 | 385 | unresolved | insufficient overlap (hits=['problem']) |
| 416 | 2026-09-03-item74-diff-debate/sol-diff-r8-reply.md:36 | 3480 | unresolved | no distinctive terms matched at any candidate |
| 417 | 2026-09-03-item74-diff-debate/sol-diff-r8-reply.md:36 | 4994 | unresolved | no distinctive terms matched at any candidate |
| 418 | 2026-09-03-item74-diff-debate/sol-diff-r8-reply.md:36 | 5291 | unresolved | no distinctive terms matched at any candidate |
| 419 | 2026-09-03-item74-diff-debate/sol-diff-r8-reply.md:36 | 5332 | unresolved | no distinctive terms matched at any candidate |
| 420 | 2026-09-03-item74-diff-debate/sol-diff-r8-reply.md:39 | 379 | unresolved | no distinctive terms matched at any candidate |
| 421 | 2026-09-03-item74-diff-debate/sol-diff-r8-reply.md:39 | 385 | unresolved | insufficient overlap (hits=['problem']) |
| 422 | 2026-09-03-item74-diff-debate/sol-diff-r9-reply.md:18 | 5557 | unresolved | insufficient overlap (hits=['ownership']) |
| 423 | 2026-09-03-item74-diff-debate/whole-branch-review.md:30 | 983 | unresolved | no distinctive terms matched at any candidate |
| 424 | 2026-09-04-backlog-plan-review/reply-fable-r1.md:58 | 41 | unresolved | no distinctive terms matched at any candidate |
| 425 | 2026-09-04-backlog-spec-review/brief-sol-r1.md:33 | 169 | unresolved | no distinctive terms matched at any candidate |
| 426 | 2026-09-04-backlog-spec-review/reply-sol-r1.md:1 | 11 | unresolved | insufficient overlap (hits=['status']) |
| 427 | 2026-09-04-backlog-spec-review/reply-sol-r1.md:1 | 46 | unresolved | insufficient overlap (hits=['ranking']) |
| 428 | 2026-09-04-backlog-spec-review/reply-sol-r1.md:1 | 167 | unresolved | no distinctive terms matched at any candidate |
| 429 | 2026-09-04-backlog-spec-review/reply-sol-r1.md:17 | 5379 | unresolved | insufficient overlap (hits=['partially', 'closed']) |
| 430 | 2026-09-04-backlog-spec-review/reply-sol-r1.md:17 | 5425 | unresolved | insufficient overlap (hits=['partially', 'closed']) |
| 431 | 2026-09-04-backlog-spec-review/reply-sol-r1.md:21 | 3476 | unresolved | insufficient overlap (hits=['multi-model-verify', 'skills']) |
| 432 | 2026-09-04-backlog-spec-review/reply-sol-r1.md:25 | 548 | unresolved | insufficient overlap (hits=['construction', 'mirror']) |
| 433 | 2026-09-04-backlog-spec-review/reply-sol-r1.md:25 | 622 | unresolved | no distinctive terms matched at any candidate |
| 434 | 2026-09-04-backlog-spec-review/reply-sol-r1.md:25 | 670 | unresolved | no distinctive terms matched at any candidate |
| 435 | 2026-09-04-backlog-spec-review/reply-sol-r1.md:25 | 719 | unresolved | no distinctive terms matched at any candidate |
| 436 | 2026-09-04-backlog-spec-review/reply-sol-r1.md:29 | 3414 | unresolved | insufficient overlap (hits=['truncated', 'captures']) |
| 437 | 2026-09-04-backlog-spec-review/reply-sol-r1.md:29 | 3438 | unresolved | no distinctive terms matched at any candidate |
| 438 | 2026-09-04-backlog-spec-review/reply-sol-r1.md:29 | 3453 | unresolved | insufficient overlap (hits=['truncated']) |
| 439 | 2026-09-04-backlog-spec-review/reply-sol-r2b.md:27 | 3577 | unresolved | insufficient overlap (hits=['synthesized', 'readme']) |
| 440 | 2026-09-04-backlog-spec-review/reply-sol-r2b.md:29 | 41 | unresolved | no distinctive terms matched at any candidate |
| 441 | 2026-09-04-backlog-spec-review/reply-sol-r3.md:7 | 3577 | yes ceca5f8 | distinctive-word overlap (3): synthesized, editing, readme |
| 442 | 2026-09-04-backlog-spec-review/reply-sol-r3.md:9 (@7a89084) | 160 | unresolved | no distinctive terms matched at any candidate |
| 443 | 2026-09-04-backlog-spec-review/reply-sol-r3.md:9 (@efe4fa0) | 160 | unresolved | insufficient overlap (hits=['observation']) |
| 444 | 2026-08-03-home-skills-root/kimi-r1-reply.md:10 | 577 | unresolved | no distinctive terms matched at any candidate |
| 445 | 2026-08-03-home-skills-root/kimi-r1-reply.md:10 | 11-14 | unresolved | insufficient overlap (hits=['status']) |
| 446 | 2026-08-03-home-skills-root/kimi-r1-reply.md:10 | 16-19 | unresolved | no distinctive terms matched at any candidate |

**Totals.** 446 individual citations checked (up from the 250 rows in the first pass, once a corrected extraction captured every citation packed onto a shared grep line instead of only the first). 74 resolve to `yes <sha>` under the mechanical bar above; 372 are `unresolved`. The mechanical bar is deliberately strict — it requires the citing text's own distinctive words to reappear verbatim at the exact cited range, and does not credit a paraphrase — so `unresolved` means exactly that the check could not confirm the row without guessing; it is not a measurement of how many rows a human reading would accept, and this record makes no claim about that. Full detail for every row is in `citation-inventory-check.txt`.

**The frozen plan's own citations** (plan Task 9 Steps 2 and 3). `docs/superpowers/plans/2026-08-03-home-skills-root-probe.md` named the old backlog path on six lines; three carried line citations and were rewritten commit-bound, the other three (288, 856, 892) name the path without a line and were left unchanged. Line 78 cites `:41` and now reads `docs/superpowers/plans/2026-07-27-0150-backlog.md@4448291:41`; line 975 cites the same `:41` and was rewritten the same way; line 158 cites `:577` and `:11-14` and now reads `docs/superpowers/plans/2026-07-27-0150-backlog.md@4448291`. `4448291` is the commit whose layout those numbers were read against (the old file's revision when the probe plan was written), and all three ranges resolve there: `:41` is the 27-directory count, `:577` is item 10's heading, `:11-14` is its status block.