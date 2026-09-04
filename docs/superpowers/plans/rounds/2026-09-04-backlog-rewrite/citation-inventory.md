# Citations into the old backlog path, inventoried 2026-09-04

Source: `citation-grep.txt` beside this file, the full untruncated output of
`git ls-files | xargs grep -nH '2026-07-27-0150-backlog\.md'` at the
commit that adds this file. Two citation shapes were searched for: the
path followed by `:N` or `:N-M`, and the path named on a line that cites
`:N` later in the same line. A bare mention of the path is not a citation. Raw round records are never edited, so nothing
here is applied to them. A row records the commit at which the cited line
carries the text the citation describes, or `unresolved` when no candidate
does. Nothing is guessed.

Candidates tried per row, in order: the subject revision the record names
in its filename or text; the record's own first commit (`git log
--diff-filter=A --format=%h -- <file>`); that commit's first parent.

| citing file | cited line(s) | candidate revision(s) | text at the cited line matches? | resolving commit |
|---|---|---|---|---|
| `2026-07-28-0160-backlog/fable-review-c6b7c85-efe4fa0.md:30` | 160-162 | c6b7c85; efe4fa0; 7a89084 (own first commit); 7a89084^ (first parent) | no | unresolved |
| `2026-07-28-0160-backlog/kimi-backup-lane-0160-r1-reply.md:9` | 72-75 | 3413c8e (own first commit) | yes | yes 3413c8e |
| `2026-07-28-0160-backlog/kimi-backup-lane-0160-r1-reply.md:25` | 75 | 3413c8e (own first commit) | yes | yes 3413c8e |
| `2026-07-28-0160-backlog/sol-diff-0160-r1-reply.md:65` | 52-58 | 9beb9a2 (own first commit) | yes | yes 9beb9a2 |
| `2026-07-28-0160-backlog/sol-diff-0160-r1-reply.md:66` | 212-224 | 9beb9a2 (own first commit) | yes | yes 9beb9a2 |
| `2026-07-28-0160-backlog/sol-diff-0160-r1-reply.md:67` | 217-219 | 9beb9a2 (own first commit) | yes | yes 9beb9a2 |
| `2026-07-28-0160-backlog/sol-diff-0160-r1-reply.md:80` | 154-164 | 9beb9a2 (own first commit) | yes | yes 9beb9a2 |
| `2026-07-28-0160-backlog/sol-diff-0160-r2-reply.md:1` | 230-250 | 3413c8e (own first commit) | yes | yes 3413c8e |
| `2026-07-28-0160-backlog/sol-diff-0160-r2-reply.md:36` | 52-70 | 3413c8e (own first commit) | yes | yes 3413c8e |
| `2026-07-28-0160-backlog/sol-diff-0160-r2-reply.md:40` | 233-234 | 3413c8e (own first commit) | yes | yes 3413c8e |
| `2026-07-28-0160-backlog/sol-diff-0160-r2-reply.md:41` | 235-240 | 3413c8e (own first commit) | yes | yes 3413c8e |
| `2026-07-28-0160-backlog/sol-diff-0160-r2-reply.md:42` | 245-250 | 3413c8e (own first commit) | yes | yes 3413c8e |
| `2026-07-28-0160-backlog/sol-diff-0160-r2-reply.md:53` | 72-75 | 3413c8e (own first commit) | yes | yes 3413c8e |
| `2026-07-28-0160-backlog/sol-diff-0160-r3-reply.md:37` | 230-255 | 3413c8e (own first commit) | yes | yes 3413c8e |
| `2026-07-28-0160-backlog/sol-diff-0160-r3-reply.md:41` | 222-228 | 3413c8e (own first commit) | yes | yes 3413c8e |
| `2026-07-28-0160-backlog/sol-diff-0160-r3-reply.md:47` | 222-228 | 3413c8e (own first commit) | yes | yes 3413c8e |
| `2026-07-28-0160-backlog/sol-diff-0160-r4-reply.md:31` | 260-280 | 3413c8e (own first commit) | yes | yes 3413c8e |
| `2026-07-28-reviewer-isolation/kimi-panel-r1-reply.md:25` | 343-369 | 42c9421 (own first commit) | yes | yes 42c9421 |
| `2026-07-28-reviewer-isolation/sol-diff-r1-reply.md:84` | 343-349 | d43e547 (own first commit) | yes | yes d43e547 |
| `2026-07-28-reviewer-isolation/sol-plan-r1-reply.md:27` | 14 | fb293d9 (own first commit) | yes | yes fb293d9 |
| `2026-08-03-home-skills-root/kimi-r1-reply.md:10` | 577, 11-14 | e9c0aae (own first commit) | yes | yes e9c0aae |
| `2026-08-03-home-skills-root/kimi-r1-reply.md:71` | 41 | e9c0aae (own first commit) | yes | yes e9c0aae |
| `2026-08-03-home-skills-root/kimi-r1-reply.md:324` | 41 | e9c0aae (own first commit) | yes | yes e9c0aae |
| `2026-08-03-home-skills-root/kimi-r1-reply.md:345` | 41 | e9c0aae (own first commit) | yes | yes e9c0aae |
| `2026-08-03-home-skills-root/sol-plan-r1-brief.md:41` | 577 | e9c0aae (own first commit) | yes | yes e9c0aae |
| `2026-08-04-lane-release-and-round-cap/diff-reply-r1.md:67` | 1810-1837 | 35f66cd (own first commit) | yes | yes 35f66cd |
| `2026-08-04-lane-release-and-round-cap/diff-reply-r1.md:75` | 1672-1680 | 35f66cd (own first commit) | yes | yes 35f66cd |
| `2026-08-04-lane-release-and-round-cap/diff-reply-r1.md:79` | 11-16 | 35f66cd (own first commit) | yes | yes 35f66cd |
| `2026-08-04-lane-release-and-round-cap/diff-reply-r1.md:88` | 1826-1837 | 35f66cd (own first commit) | yes | yes 35f66cd |
| `2026-08-04-lane-release-and-round-cap/diff-reply-r2.md:11` | 1683 | 35f66cd (own first commit) | yes | yes 35f66cd |
| `2026-08-04-lane-release-and-round-cap/diff-reply-r2.md:13` | 1688 | 35f66cd (own first commit) | yes | yes 35f66cd |
| `2026-08-04-lane-release-and-round-cap/diff-reply-r2.md:37` | 1837 | 35f66cd (own first commit) | yes | yes 35f66cd |
| `2026-08-04-lane-release-and-round-cap/diff-reply-r2.md:41` | 11 | 35f66cd (own first commit) | yes | yes 35f66cd |
| `2026-08-04-lane-release-and-round-cap/diff-reply-r2.md:43` | 1688 | 35f66cd (own first commit) | yes | yes 35f66cd |
| `2026-08-04-lane-release-and-round-cap/diff-reply-r3.md:39` | 1837 | 35f66cd (own first commit) | yes | yes 35f66cd |
| `2026-08-04-lane-release-and-round-cap/diff-reply-r3.md:43` | 1681 | 35f66cd (own first commit) | yes | yes 35f66cd |
| `2026-08-04-lane-release-and-round-cap/diff-reply-r4.md:35` | 1837 | 35f66cd (own first commit) | yes | yes 35f66cd |
| `2026-08-04-lane-release-and-round-cap/diff-reply-r4.md:39` | 1575 | 35f66cd (own first commit) | yes | yes 35f66cd |
| `2026-08-04-lane-release-and-round-cap/diff-reply-r5.md:33` | 1837 | 35f66cd (own first commit) | yes | yes 35f66cd |
| `2026-08-04-lane-release-and-round-cap/diff-reply-r6.md:29` | 1837 | 35f66cd (own first commit) | yes | yes 35f66cd |
| `2026-08-04-lane-release-and-round-cap/diff-reply-r6.md:33` | 1575 | 35f66cd (own first commit) | yes | yes 35f66cd |
| `2026-08-04-lane-release-and-round-cap/plan-reply-r1.md:7` | 1606 | 35f66cd (own first commit) | yes | yes 35f66cd |
| `2026-08-04-lane-release-and-round-cap/plan-reply-r1.md:69` | 1573 | 35f66cd (own first commit) | yes | yes 35f66cd |
| `2026-08-04-lane-release-and-round-cap/plan-reply-r1.md:76` | 1481 | 35f66cd (own first commit) | yes | yes 35f66cd |
| `2026-08-04-transport-and-mirror/diff-r1-reply.md:92` | 20 | 4b02cb3 (own first commit) | yes | yes 4b02cb3 |
| `2026-08-04-transport-and-mirror/diff-r1-reply.md:104` | 37-42 | 4b02cb3 (own first commit) | yes | yes 4b02cb3 |
| `2026-08-04-transport-and-mirror/diff-r1-reply.md:106` | 22-35 | 4b02cb3 (own first commit) | yes | yes 4b02cb3 |
| `2026-08-04-transport-and-mirror/diff-r2-reply.md:22` | 28-46 | 4b02cb3 (own first commit) | yes | yes 4b02cb3 |
| `2026-08-04-transport-and-mirror/diff-r2-reply.md:28` | 57-64 | 4b02cb3 (own first commit) | yes | yes 4b02cb3 |
| `2026-08-04-transport-and-mirror/diff-r2-reply.md:34` | 22-26 | 4b02cb3 (own first commit) | yes | yes 4b02cb3 |
| `2026-08-04-transport-and-mirror/diff-r3-reply.md:13` | 48-55 | 4b02cb3 (own first commit) | yes | yes 4b02cb3 |
| `2026-08-04-transport-and-mirror/diff-r3-reply.md:15` | 1110-1116 | 4b02cb3 (own first commit) | yes | yes 4b02cb3 |
| `2026-08-04-transport-and-mirror/diff-r3-reply.md:17` | 22-27 | 4b02cb3 (own first commit) | yes | yes 4b02cb3 |
| `2026-08-04-transport-and-mirror/plan-reply-r1b.md:7` | 1195 | 4b02cb3 (own first commit) | yes | yes 4b02cb3 |
| `2026-08-04-transport-and-mirror/plan-reply-r1b.md:11` | 1280 | 4b02cb3 (own first commit) | yes | yes 4b02cb3 |
| `2026-08-04-transport-and-mirror/plan-reply-r1b.md:37` | 1195 | 4b02cb3 (own first commit) | yes | yes 4b02cb3 |
| `2026-08-04-transport-and-mirror/plan-reply-r1b.md:39` | 1280 | 4b02cb3 (own first commit) | yes | yes 4b02cb3 |
| `2026-08-04-transport-and-mirror/plan-reply-r1b.md:41` | 1346 | 4b02cb3 (own first commit) | yes | yes 4b02cb3 |
| `2026-08-04-transport-and-mirror/plan-reply-r1b.md:43` | 1383 | 4b02cb3 (own first commit) | yes | yes 4b02cb3 |
| `2026-08-04-transport-and-mirror/plan-reply-r2.md:3` | 1213 | 4b02cb3 (own first commit) | yes | yes 4b02cb3 |
| `2026-08-04-transport-and-mirror/plan-reply-r2.md:31` | 1212 | 4b02cb3 (own first commit) | yes | yes 4b02cb3 |
| `2026-08-04-transport-and-mirror/plan-reply-r2.md:33` | 1361 | 4b02cb3 (own first commit) | yes | yes 4b02cb3 |
| `2026-08-04-transport-and-mirror/plan-reply-r2.md:43` | 1191 | 4b02cb3 (own first commit) | yes | yes 4b02cb3 |
| `2026-08-04-transport-and-mirror/plan-reply-r3.md:18` | 1392 | 4b02cb3 (own first commit) | yes | yes 4b02cb3 |
| `2026-08-04-transport-and-mirror/plan-reply-r3.md:22` | 1191 | 4b02cb3 (own first commit) | yes | yes 4b02cb3 |
| `2026-08-04-transport-and-mirror/plan-reply-r3.md:23` | 1225 | 4b02cb3 (own first commit) | yes | yes 4b02cb3 |
| `2026-08-04-transport-and-mirror/plan-reply-r3.md:24` | 1214 | 4b02cb3 (own first commit) | yes | yes 4b02cb3 |
| `2026-08-04-transport-and-mirror/plan-reply-r4.md:19` | 1226 | 4b02cb3 (own first commit) | yes | yes 4b02cb3 |
| `2026-08-04-transport-and-mirror/plan-reply-r6.md:8` | 1668 | 4b02cb3 (own first commit) | yes | yes 4b02cb3 |
| `2026-08-04-transport-and-mirror/plan-reply-r7.md:1` | 1675 | 4b02cb3 (own first commit) | yes | yes 4b02cb3 |
| `2026-08-11-budget-flake-generator/diff-reply-r1.txt:38` | 1187-1229 | 985ff7e (own first commit) | yes | yes 985ff7e |
| `2026-08-11-budget-flake-generator/diff-reply-r1.txt:60` | 1181-1185 | 985ff7e (own first commit) | yes | yes 985ff7e |
| `2026-08-11-budget-flake-generator/diff-reply-r2.txt:19` | 670 | 492bb65 (own first commit) | yes | yes 492bb65 |
| `2026-08-11-budget-flake-generator/diff-reply-r2.txt:24` | 659 | 492bb65 (own first commit) | yes | yes 492bb65 |
| `2026-08-11-budget-flake-generator/diff-reply-r2.txt:28` | 1979 | 492bb65 (own first commit) | yes | yes 492bb65 |
| `2026-08-11-budget-flake-generator/diff-reply-r2.txt:30` | 2013 | 492bb65 (own first commit) | yes | yes 492bb65 |
| `2026-08-11-budget-flake-generator/plan-reply-r1.txt:18` | 1158-1167 | e050b35 (own first commit) | yes | yes e050b35 |
| `2026-08-11-budget-flake-generator/plan-reply-r1.txt:36` | 1169-1184 | e050b35 (own first commit) | yes | yes e050b35 |
| `2026-08-11-budget-flake-generator/plan-reply-r1.txt:63` | 1129-1142 | e050b35 (own first commit) | yes | yes e050b35 |
| `2026-08-11-budget-flake-generator/plan-reply-r1.txt:100` | 624-635 | e050b35 (own first commit) | yes | yes e050b35 |
| `2026-08-11-budget-flake-generator/plan-reply-r1.txt:130` | 1169-1184 | e050b35 (own first commit) | yes | yes e050b35 |
| `2026-08-11-budget-flake-generator/plan-reply-r1.txt:159` | 603-628 | e050b35 (own first commit) | yes | yes e050b35 |
| `2026-08-11-budget-flake-generator/plan-reply-r11.txt:1` | 603-650 | 28bfd07 (own first commit) | yes | yes 28bfd07 |
| `2026-08-11-budget-flake-generator/plan-reply-r12.txt:3` | 603-650 | 28bfd07 (own first commit) | yes | yes 28bfd07 |
| `2026-08-11-budget-flake-generator/plan-reply-r2.txt:114` | 603-628 | e050b35 (own first commit) | yes | yes e050b35 |
| `2026-08-11-budget-flake-generator/plan-reply-r3.txt:23` | 1158-1161 | e050b35 (own first commit) | yes | yes e050b35 |
| `2026-08-11-budget-flake-generator/plan-reply-r3.txt:31` | 1169-1172 | e050b35 (own first commit) | yes | yes e050b35 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r1.txt:13` | 593-600 | ac7dc43 (own first commit) | yes | yes ac7dc43 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r1.txt:36` | 2593-2600 | ac7dc43 (own first commit) | yes | yes ac7dc43 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r1.txt:44` | 957-963 | ac7dc43 (own first commit) | yes | yes ac7dc43 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r1.txt:56` | 2473-2498 | ac7dc43 (own first commit) | yes | yes ac7dc43 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r1.txt:60` | 562-583 | ac7dc43 (own first commit) | yes | yes ac7dc43 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r1.txt:62` | 2602-2617 | ac7dc43 (own first commit) | yes | yes ac7dc43 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r1.txt:68` | 484-490 | ac7dc43 (own first commit) | yes | yes ac7dc43 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r2.txt:9` | 608-617 | 8b46296 (own first commit) | yes | yes 8b46296 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r2.txt:23` | 2651-2656 | 8b46296 (own first commit) | yes | yes 8b46296 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r2.txt:29` | 2619-2649 | 8b46296 (own first commit) | yes | yes 8b46296 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r2.txt:31` | 2658-2689 | 8b46296 (own first commit) | yes | yes 8b46296 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r3.txt:18` | 619-629 | ca93356 (own first commit) | yes | yes ca93356 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r3.txt:22` | 2743-2747 | ca93356 (own first commit) | yes | yes ca93356 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r3.txt:23` | 2707-2723 | ca93356 (own first commit) | yes | yes ca93356 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r4.txt:16` | 2740-2758 | a02618e (own first commit) | yes | yes a02618e |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r4.txt:18` | 2705 | a02618e (own first commit) | yes | yes a02618e |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r4.txt:19` | 2740-2747 | a02618e (own first commit) | yes | yes a02618e |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r4.txt:30` | 2705-2762 | a02618e (own first commit) | yes | yes a02618e |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r5.txt:28` | 2740-2766 | 99d1961 (own first commit) | yes | yes 99d1961 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r5.txt:32` | 2705 | 99d1961 (own first commit) | yes | yes 99d1961 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r5.txt:33` | 2740-2747 | 99d1961 (own first commit) | yes | yes 99d1961 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r6.txt:29` | 2705 | e713081 (own first commit) | yes | yes e713081 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r7.txt:31` | 11-15 | 8c80891 (own first commit) | yes | yes 8c80891 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r7.txt:32` | 2947-2951 | 8c80891 (own first commit) | yes | yes 8c80891 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r7.txt:33` | 3205-3210 | 8c80891 (own first commit) | yes | yes 8c80891 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r7.txt:40` | 2971-2979 | 8c80891 (own first commit) | yes | yes 8c80891 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r7.txt:41` | 1120-1137 | 8c80891 (own first commit) | yes | yes 8c80891 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r8.txt:3` | 1106 | fd87657 (own first commit) | yes | yes fd87657 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r8.txt:7` | 2955-2964 | fd87657 (own first commit) | yes | yes fd87657 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r8.txt:17` | 3233-3240 | fd87657 (own first commit) | yes | yes fd87657 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r8.txt:18` | 3318-3327 | fd87657 (own first commit) | yes | yes fd87657 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r8.txt:19` | 3279-3306 | fd87657 (own first commit) | yes | yes fd87657 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r8.txt:20` | 3285-3289 | fd87657 (own first commit) | yes | yes fd87657 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r8.txt:26` | 3285 | fd87657 (own first commit) | yes | yes fd87657 |
| `2026-08-11-tool-surface-agy-drift/diff-reply-r8.txt:38` | 2955-2964 | fd87657 (own first commit) | yes | yes fd87657 |
| `2026-08-11-tool-surface-agy-drift/fable-review-1-ef428c3-5133f98.md:36` | 526 | 3b2c49d (own first commit) | yes | yes 3b2c49d |
| `2026-08-11-tool-surface-agy-drift/plan-reply-r1.txt:7` | 510-519 | 4be7eee (own first commit) | yes | yes 4be7eee |
| `2026-08-11-tool-surface-agy-drift/plan-reply-r1.txt:13` | 779-785 | 4be7eee (own first commit) | yes | yes 4be7eee |
| `2026-08-11-tool-surface-agy-drift/plan-reply-r2.txt:23` | 787-800 | 5737d4d (own first commit) | yes | yes 5737d4d |
| `2026-08-11-tool-surface-agy-drift/plan-reply-r3.txt:17` | 787-800 | 6f1a93e (own first commit) | yes | yes 6f1a93e |
| `2026-08-11-tool-surface-agy-drift/plan-reply-r4.txt:5` | 787-800 | e876ca8 (own first commit) | yes | yes e876ca8 |
| `2026-08-16-fresh-preamble-gate/diff-debate-r1.md:60` | 3712 | cefa969 (own first commit) | yes | yes cefa969 |
| `2026-08-16-fresh-preamble-gate/diff-debate-r1.md:114` | 3712 | cefa969 (own first commit) | yes | yes cefa969 |
| `2026-08-16-fresh-preamble-gate/diff-debate-r1.md:118` | 3987 | cefa969 (own first commit) | yes | yes cefa969 |
| `2026-08-16-fresh-preamble-gate/diff-debate-r1.md:124` | 3940 | cefa969 (own first commit) | yes | yes cefa969 |
| `2026-08-16-fresh-preamble-gate/diff-debate-r2.md:55` | 4071 | cefa969 (own first commit) | yes | yes cefa969 |
| `2026-08-16-fresh-preamble-gate/diff-debate-r2.md:66` | 4093 | cefa969 (own first commit) | yes | yes cefa969 |
| `2026-08-16-fresh-preamble-gate/diff-debate-r2.md:84` | 4086 | cefa969 (own first commit) | yes | yes cefa969 |
| `2026-08-16-fresh-preamble-gate/diff-debate-r2.md:85` | 4077 | cefa969 (own first commit) | yes | yes cefa969 |
| `2026-08-16-fresh-preamble-gate/diff-debate-r3.md:47` | 4067 | cefa969 (own first commit) | yes | yes cefa969 |
| `2026-08-16-fresh-preamble-gate/diff-debate-r3.md:49` | 4061 | cefa969 (own first commit) | yes | yes cefa969 |
| `2026-08-16-fresh-preamble-gate/diff-debate-r3.md:51` | 4112 | cefa969 (own first commit) | yes | yes cefa969 |
| `2026-08-16-fresh-preamble-gate/diff-debate-r4.md:81` | 4067 | cefa969 (own first commit) | yes | yes cefa969 |
| `2026-08-16-fresh-preamble-gate/diff-debate-r4.md:82` | 4131 | cefa969 (own first commit) | yes | yes cefa969 |
| `2026-08-16-fresh-preamble-gate/diff-debate-r5b.md:58` | 4067 | cefa969 (own first commit) | yes | yes cefa969 |
| `2026-08-16-fresh-preamble-gate/plan-debate-r2.md:40` | 214 | e9c28df (own first commit) | yes | yes e9c28df |
| `2026-08-16-fresh-preamble-gate/plan-debate-r2.md:54` | 195 | e9c28df (own first commit) | yes | yes e9c28df |
| `2026-08-16-fresh-preamble-gate/plan-debate-r2.md:58` | 1172 | e9c28df (own first commit) | yes | yes e9c28df |
| `2026-08-16-fresh-preamble-gate/plan-debate-r3.md:33` | 25 | 99f7bac (own first commit) | yes | yes 99f7bac |
| `2026-08-16-fresh-preamble-gate/plan-debate-r3.md:35` | 49 | 99f7bac (own first commit) | yes | yes 99f7bac |
| `2026-08-16-fresh-preamble-gate/plan-debate-r3.md:37` | 191 | 99f7bac (own first commit) | yes | yes 99f7bac |
| `2026-08-16-fresh-preamble-gate/plan-debate-r3.md:49` | 31 | 99f7bac (own first commit) | yes | yes 99f7bac |
| `2026-08-16-fresh-preamble-gate/plan-debate-r4.md:36` | 62 | 9d15388 (own first commit) | yes | yes 9d15388 |
| `2026-08-16-fresh-preamble-gate/plan-debate-r5.md:37` | 34 | fe3a831 (own first commit) | yes | yes fe3a831 |
| `2026-08-16-fresh-preamble-gate/plan-debate-r5.md:39` | 196 | fe3a831 (own first commit) | yes | yes fe3a831 |
| `2026-08-16-fresh-preamble-gate/plan-debate-r5.md:52` | 4173 | fe3a831 (own first commit) | yes | yes fe3a831 |
| `2026-08-16-fresh-preamble-gate/plan-debate-r5.md:56` | 4149 | fe3a831 (own first commit) | yes | yes fe3a831 |
| `2026-08-16-fresh-preamble-gate/plan-debate-r5.md:58` | 4155 | fe3a831 (own first commit) | yes | yes fe3a831 |
| `2026-08-16-fresh-preamble-gate/plan-debate-r5.md:60` | 4160 | fe3a831 (own first commit) | yes | yes fe3a831 |
| `2026-08-16-fresh-preamble-gate/plan-debate-r5.md:62` | 4168 | fe3a831 (own first commit) | yes | yes fe3a831 |
| `2026-08-16-fresh-preamble-gate/plan-debate-r6.md:48` | 3000 | 03b4eef (own first commit) | yes | yes 03b4eef |
| `2026-08-16-fresh-preamble-gate/plan-debate-r6.md:52` | 4185 | 03b4eef (own first commit) | yes | yes 03b4eef |
| `2026-08-19-resume-not-guaranteed/sol-r1-reply.md:14` | 4596-4608 | 2c3730d (own first commit) | yes | yes 2c3730d |
| `2026-08-19-resume-not-guaranteed/sol-r1-reply.md:15` | 4622-4627 | 2c3730d (own first commit) | yes | yes 2c3730d |
| `2026-08-19-resume-not-guaranteed/sol-r1-reply.md:17` | 4589-4594 | 2c3730d (own first commit) | yes | yes 2c3730d |
| `2026-08-19-resume-not-guaranteed/sol-r1-reply.md:38` | 4589-4620 | 2c3730d (own first commit) | yes | yes 2c3730d |
| `2026-08-19-resume-not-guaranteed/sol-r2-reply.md:23` | 4602-4608 | 2c3730d (own first commit) | yes | yes 2c3730d |
| `2026-08-19-resume-not-guaranteed/sol-r2-reply.md:24` | 4622-4627 | 2c3730d (own first commit) | yes | yes 2c3730d |
| `2026-08-19-resume-not-guaranteed/sol-r2-reply.md:26` | 4589-4594 | 2c3730d (own first commit) | yes | yes 2c3730d |
| `2026-08-19-resume-not-guaranteed/sol-r2-reply.md:34` | 4589-4627 | 2c3730d (own first commit) | yes | yes 2c3730d |
| `2026-08-22-item48-plan-debate/sol-reply-r1.md:27` | 3531-3532 | 69779a2 (own first commit) | yes | yes 69779a2 |
| `2026-08-22-item48-plan-debate/sol-reply-r1.md:64` | 3534-3543 | 69779a2 (own first commit) | yes | yes 69779a2 |
| `2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:289` | 3748 | 39408ac (own first commit) | yes | yes 39408ac |
| `2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:1671` | 3456 | 39408ac (own first commit) | yes | yes 39408ac |
| `2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:1734` | 3485 | 39408ac (own first commit) | yes | yes 39408ac |
| `2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:1767` | 3473 | 39408ac (own first commit) | yes | yes 39408ac |
| `2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:2076` | 3561 | 39408ac (own first commit) | yes | yes 39408ac |
| `2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:2089` | 3380 | 39408ac (own first commit) | yes | yes 39408ac |
| `2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:2100` | 3098 | 39408ac (own first commit) | yes | yes 39408ac |
| `2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:2549` | 3748 | 39408ac (own first commit) | yes | yes 39408ac |
| `2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:2550` | 2510 | 39408ac (own first commit) | yes | yes 39408ac |
| `2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:2640` | 3750 | 39408ac (own first commit) | yes | yes 39408ac |
| `2026-08-30-item32-plan-debate/fable-reply-r1.md:11` | 4496 | 28802bd (own first commit) | yes | yes 28802bd |
| `2026-08-30-item32-plan-debate/fable-reply-r2.md:9` | 4496 | 28802bd (own first commit) | yes | yes 28802bd |
| `2026-08-30-item32-plan-debate/sol-reply-r2.md:94` | 2674-2681 | 28802bd (own first commit) | yes | yes 28802bd |
| `2026-08-30-item32-plan-debate/sol-reply-r5.md:3` | 4430-4455 | 28802bd (own first commit) | yes | yes 28802bd |
| `2026-08-30-item32-plan-debate/sol-reply-r5.md:7` | 4449-4455 | 28802bd (own first commit) | yes | yes 28802bd |
| `2026-08-30-item32-plan-debate/sol-reply-r6.md:48` | 4440-4455 | 28802bd (own first commit) | yes | yes 28802bd |
| `2026-08-30-item32-plan-debate/sol-reply-r6.md:62` | 4427-4438 | 28802bd (own first commit) | yes | yes 28802bd |
| `2026-08-31-completion-coupled-dispatch/fable-whole-branch-review-8af6ae0..3029599.md:38` | 4829-4854 | c0ef41a (own first commit) | yes | yes c0ef41a |
| `2026-08-31-completion-coupled-dispatch/kimi-plan-review-r1.md:19` | 4018-4027 | fbdcd13 (own first commit) | yes | yes fbdcd13 |
| `2026-08-31-completion-coupled-dispatch/sol-diff-debate-r1.md:79` | 4909-4910 | cce350c (own first commit) | yes | yes cce350c |
| `2026-08-31-completion-coupled-dispatch/sol-diff-debate-r2.md:69` | 4909-4910 | cce350c (own first commit) | yes | yes cce350c |
| `2026-09-03-item74-diff-debate/fable-diff-r2-reply.md:28` | 400-401 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/fable-diff-r3-reply.md:39` | 48-50 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/fable-diff-r5-reply.md:33` | 5314-5317 | 233a340 (own first commit) | yes | yes 233a340 |
| `2026-09-03-item74-diff-debate/fable-diff-r9-reply.md:35` | 5557-5569 | 3a0b6b7 (own first commit) | yes | yes 3a0b6b7 |
| `2026-09-03-item74-diff-debate/sol-diff-r1-reply.md:22` | 388 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r1-reply.md:28` | 41 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r1-reply.md:32` | 121 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r1-reply.md:33` | 219 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r1-reply.md:34` | 151 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r1-reply.md:42` | 121 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r2-reply.md:13` | 126 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r2-reply.md:15` | 333 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r2-reply.md:19` | 45 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r2-reply.md:23` | 48 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:13` | 47 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:14` | 420 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:15` | 421 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:16` | 336 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:17` | 52 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:18` | 59 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:24` | 3480 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:25` | 4994 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:26` | 5291 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:27` | 5308 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:28` | 5322 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:32` | 379 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:34` | 43 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:36` | 420 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:38` | 47 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r3-reply.md:42` | 3480 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r4-reply.md:13` | 5542 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r4-reply.md:15` | 5307 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r4-reply.md:17` | 3480 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r4-reply.md:19` | 5558 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r4-reply.md:21` | 5312 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r4-reply.md:23` | 5305 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r4-reply.md:25` | 5536 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r4-reply.md:27` | 5551 | b9c17bc (own first commit) | yes | yes b9c17bc |
| `2026-09-03-item74-diff-debate/sol-diff-r5-reply.md:20` | 5312 | 233a340 (own first commit) | yes | yes 233a340 |
| `2026-09-03-item74-diff-debate/sol-diff-r5-reply.md:22` | 5538 | 233a340 (own first commit) | yes | yes 233a340 |
| `2026-09-03-item74-diff-debate/sol-diff-r5-reply.md:28` | 5541 | 233a340 (own first commit) | yes | yes 233a340 |
| `2026-09-03-item74-diff-debate/sol-diff-r5-reply.md:30` | 5312 | 233a340 (own first commit) | yes | yes 233a340 |
| `2026-09-03-item74-diff-debate/sol-diff-r5-reply.md:32` | 3480 | 233a340 (own first commit) | yes | yes 233a340 |
| `2026-09-03-item74-diff-debate/sol-diff-r7-reply.md:29` | 3480 | fa86675 (own first commit) | yes | yes fa86675 |
| `2026-09-03-item74-diff-debate/sol-diff-r7-reply.md:32` | 379 | fa86675 (own first commit) | yes | yes fa86675 |
| `2026-09-03-item74-diff-debate/sol-diff-r8-reply.md:36` | 3480 | 20d557a (own first commit) | yes | yes 20d557a |
| `2026-09-03-item74-diff-debate/sol-diff-r8-reply.md:39` | 379 | 20d557a (own first commit) | yes | yes 20d557a |
| `2026-09-03-item74-diff-debate/sol-diff-r9-reply.md:18` | 5557 | 3a0b6b7 (own first commit) | yes | yes 3a0b6b7 |
| `2026-09-03-item74-diff-debate/whole-branch-review.md:30` | 983 | e0dbb89 (own first commit) | yes | yes e0dbb89 |
| `2026-09-04-backlog-plan-review/reply-fable-r1.md:58` | 41 | 0ecc7c7 (own first commit) | yes | yes 0ecc7c7 |
| `2026-09-04-backlog-spec-review/brief-sol-r1.md:33` | 169 | ceca5f8 (own first commit) | yes | yes ceca5f8 |
| `2026-09-04-backlog-spec-review/reply-sol-r1.md:1` | 11 | ceca5f8 (own first commit) | yes | yes ceca5f8 |
| `2026-09-04-backlog-spec-review/reply-sol-r1.md:17` | 5379 | ceca5f8 (own first commit) | yes | yes ceca5f8 |
| `2026-09-04-backlog-spec-review/reply-sol-r1.md:21` | 3476 | ceca5f8 (own first commit) | yes | yes ceca5f8 |
| `2026-09-04-backlog-spec-review/reply-sol-r1.md:25` | 548 | ceca5f8 (own first commit) | yes | yes ceca5f8 |
| `2026-09-04-backlog-spec-review/reply-sol-r1.md:29` | 3414 | ceca5f8 (own first commit) | yes | yes ceca5f8 |
| `2026-09-04-backlog-spec-review/reply-sol-r2b.md:27` | 3577 | ceca5f8 (own first commit) | yes | yes ceca5f8 |
| `2026-09-04-backlog-spec-review/reply-sol-r2b.md:29` | 41 | ceca5f8 (own first commit) | yes | yes ceca5f8 |
| `2026-09-04-backlog-spec-review/reply-sol-r3.md:7` | 3577 | ceca5f8 (own first commit) | yes | yes ceca5f8 |
| `2026-09-04-backlog-spec-review/reply-sol-r3.md:9` | 160 | ceca5f8 (own first commit) | yes | yes ceca5f8 |
## Discrepancy with the spec's inventory

The spec's own inventory said the frozen plan `docs/superpowers/plans/2026-08-03-home-skills-root-probe.md`
carried two citations into the old backlog path (lines 78 and 975). The
plan review found a third shape at line 158, where the path is named once
and two line references (`:577` and `:11-14`) follow later on the same
line rather than immediately after the path. This is a finding to record,
not to hide: the spec's count of two was wrong by one, in the shape a
`:[0-9]`-only grep pattern cannot see. The untruncated grep confirmed no
other tracked document outside `docs/superpowers/plans/rounds/` carries a
line citation in either shape; every non-rounds hit besides the three
frozen-plan lines is a bare path mention.

## Frozen-plan rewrites (Steps 2 and 3)

All three of the frozen plan's citations resolve to the same commit,
`4448291`:

- Line 78, `docs/superpowers/plans/2026-07-27-0150-backlog.md:41` (the
  27-skill-directory measurement), rewritten to
  `docs/superpowers/plans/2026-07-27-0150-backlog.md@4448291:41`. Line 41
  at `4448291` reads "**Evidence, measured 2026-07-31.** The root holds
  27 skill directories" — the newest, and only, commit in the file's
  history whose line 41 states the 27-directory measurement (every other
  commit's line 41 is an unrelated "Open." list that happens to contain
  the digits 27).
- Line 158, item 10's heading (`:577`) and status block (`:11-14`),
  rewritten to
  `docs/superpowers/plans/2026-07-27-0150-backlog.md@4448291` with the
  `:577` and `:11-14` citations kept as written after it. Line 577 at
  `4448291` reads "## 10. CI does not exercise the probe or the mirror at
  all — FIX DECIDED, not implemented" and lines 11-14 are the file's
  status block naming item 10 as Open — the only commit in the file's
  history whose line 577 is item 10's heading.
- Line 975, the same `:41` citation restated in the plan's own review
  table, rewritten the same way as line 78.

Lines 288, 856 and 892 name the path with no line citation and were left
unchanged, as the brief requires.
