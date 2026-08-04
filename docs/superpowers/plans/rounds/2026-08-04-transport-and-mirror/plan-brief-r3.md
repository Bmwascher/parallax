<role>Adversarial reviewer, equal weight, in a two-model mode-diff debate. Round 3. Two rounds of fixes have each carried their own defects; assume this round's do too.</role>

<task>Round 2 you returned PASS on claim 6 and FIX on claims 1 to 5. All were applied, two of them narrowed. The repo is at C:/Users/Brandon/Documents/parallax, read-only. The diff under review is c9d9cef75112..aae5be896b97 (base..head). Read whatever you need.</task>

<rules>
Cite file:line for every claim you make or contest; uncited claims will be struck. If a fix stands, say PASS and move on. End each numbered item with PASS, FIX (with the specific fix), or ESCALATE.

Three project invariants bind this branch:
- A claim may never be wider than its evidence.
- An unmade, failed, or unreadable measurement is never a clean one.
- A test is not evidence until it has been watched to FAIL for the reason it claims.

Two of your round-2 sub-claims were checked and did not hold, and the record says so: `bytes`, `prefixSha256` and `sessionId` were NOT permissive, because each was already refused downstream. The shape checks landed on the narrower ground that the refusal named the wrong artifact. Applying the same standard to yourself is in scope.
</rules>

<what-was-applied>

**G1.** The resume prior state now requires a non-empty string `rolloutFile` and `sessionId`, an integral non-negative `bytes`, and a lowercase 64-hex `prefixSha256`. The `rolloutFile` comparison, previously gated on truthiness, now runs unconditionally.

**G2 and G9.** Object-ness of a JSONL line is decided by `Test-JsonObjectLine`: the raw text must begin with `{` AND the parse must yield a `PSCustomObject`. Both the resume first-line check and the SHIPPED slice parser now use it. This replaced `-is [PSCustomObject]` alone, which was measured to be host-dependent: `'[{...}]' | ConvertFrom-Json` returns `System.Object[]` on Windows PowerShell 5.1 and the UNROLLED inner object on PowerShell 7.6.3, so the slice parser's contract-stated non-object refusal was true on 5.1 and false on 7.

**G3.** `references/backup-lane.md` now says the mirror-location rule lives in BOTH it and `SKILL.md` and must be changed in both, instead of claiming one source.

**G4.** The identity region now limits post-construction detection to changes visible in `git status` or in the content of a path status names, and names clean-filter-equivalent raw-byte drift as uncovered. Item 22's closure carries the same limit.

**G5 to G8.** Item 20's closure records the resume half's presence-only history and what remains; its oracle-count sentence says "of the six added by the debate's first round"; the test module dates refusals to "before ITS TARGET CHECK exists"; the empty-inventory positive control authors the inventory before the rollout exists.

Seven new oracles. Both host suites green.

</what-was-applied>

<claims>

1. `Test-JsonObjectLine` is correct and completely applied. Try to find a JSONL line that is not an object and still reaches a property read, on EITHER host; and try to find any other place in this tool that assumes object-ness without going through it.

2. The resume schema check leaves no remaining path where a prior-state field skips the comparison it exists to enable. `rolloutFile` was the reachable one. Look for another, in either parameter set.

3. The narrowed `mirror-identity-gate` and mirror-location text now match the code in both directions: not wider, and not so narrow that a guarantee the code does provide has been given away.

4. The item 20 and item 22 closures are accurate as they now stand. Include the new paragraphs.

5. The seven new oracles are load-bearing. The two array cases were confirmed by mutating the raw-text check out and watching both fail on PowerShell 7 while passing on 5.1. Try to find one of the other five that would still pass with its target check removed.

6. Scope: nothing in this diff is untraceable to G1 through G9.

</claims>

<boundaries>
Already decided and NOT under debate: the four backlog items and their dispositions; the release grouping; the 260-character policy threshold; reading the JSONL rollout rather than the human transcript; and NOT building from an immutable filesystem snapshot in this release.

Out of scope: backlog items 18, 19, 24, 25, 26 and 27. The `SKILL.md` token-budget warning is item 19.
</boundaries>

<final-check>List any claim you could not verify against files you actually read, as UNVERIFIED. If everything stands, say so plainly; a round that finds nothing is a real outcome and this branch has not had one yet.</final-check>
