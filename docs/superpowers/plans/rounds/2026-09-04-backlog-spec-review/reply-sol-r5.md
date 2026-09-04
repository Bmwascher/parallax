1. Control widths are mostly corrected, but Part 3 still calls both pre-push and CI “hard controls” that “do not depend…on the local hook being installed.” Pre-push inherently depends on installation, as the later section correctly admits when it calls the per-clone hook the only refusal before a ruleset exists (`docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md:311`, `docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md:437`). Impact: medium; the preamble overstates enforcement on hookless clones.

**FIX — State that pre-push is a hard refusal only on hooked clones, while CI independently detects arrivals without relying on local installation.**

2. The digest is still internally ambiguous. Removing the exact `### ` prefix from `###   Name  ` leaves two leading spaces; the algorithm strips only trailing spaces and tabs, but its fixture requires the result to be `Name` (`docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md:124`, `docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md:128`). Two conforming implementers could hash different group components.

**FIX — Specify stripping ASCII space and tab from both ends of the post-prefix group text, or change the fixture to require the two leading spaces; pin the chosen bytes explicitly.**

3. The spec is not yet sound to hand off because the plan writer would have to resolve the pre-push dependency contradiction and choose group-header canonicalization, both design decisions rather than implementation details (`docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md:311`, `docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md:124`).

**FIX — Apply claims 1 and 2 before invoking writing-plans.**

### Final check

UNVERIFIED: none.