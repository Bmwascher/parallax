# Mirror link re-link (item 90) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the review mirror without copying through directory links, re-creating each as a junction so the reviewer reads the same bytes and the identity gate still sees every change behind it.

**Architecture:** `tools/new-review-mirror.ps1` already walks the source before the copy; that walk now records each directory link (relative path, resolved absolute target), keeps descending through links so the cycle and overlap refusals still see a link behind a link, and counts nothing beneath a link against the budget. A guard then refuses a mirror or override path that overlaps any link target. `robocopy` runs with `/XJD`, and after the final back-channel sweep the tool creates a junction per recorded link, then re-enumerates back-channels read-only and blocks if any sit under a link. The mirror's own `git status` names each junction as one subject; `Get-ContentManifest` expands a subject by listing its files and then starting a listing at every directory link beneath it, because a recursion from a parent does not pass through a link on either host. The existing source-status and mirror-state digests therefore cover the linked content with no new record fields and no change to `-VerifyIdentity` or `tools/dispatch-round.ps1`.

**Tech Stack:** Windows PowerShell 5.1 and PowerShell 7 (ASCII-only script), robocopy, git, pytest.

**Spec:** `docs/superpowers/specs/2026-09-05-mirror-link-relink-design.md`

## Global Constraints

- Feature branch `mirror-link-relink` off `main`; lowercase imperative commit messages; no AI attribution lines; stage by explicit path (a hook refuses `git add -A`).
- `tools/new-review-mirror.ps1` stays ASCII only and Windows PowerShell 5.1 compatible. Every new failure path exits BLOCKED (1) or ERROR (2) with the reason on stdout; nothing new may read as clean without a measurement.
- Change tests FIRST for every pinned contract (CLAUDE.md, "Skill editing rules"). The `mirror-path-budget` region keeps its id, so `DECLARED_REGIONS` in `evals/multi-model-verify/test_contract_coverage.py` is NOT edited.
- A pin on raw text needs its phrase on ONE physical line in the Markdown; check `_norm` versus raw before reflowing near a pin.
- The build must never delete, write, or commit THROUGH a link. Junctions are created after the last writer into the mirror and after the last back-channel sweep. Two writers run later and are not writes through a link: git's optional index refresh during a status capture writes the repository's own `.git/index`, and the walk refuses a `.git` that is itself a directory link; the override file is written beside the mirror at a path the link-target guard has already checked.
- Run PowerShell-facing test modules under BOTH hosts: once with `$env:PARALLAX_PS_HOST = "powershell"` and once with `"pwsh"`.
- Never run pytest or write files inside a review mirror or inside this repo while a reviewer round is running (CLAUDE.md, "DO NOT TOUCH THE REVIEWED TREE").
- Bump `.claude-plugin/plugin.json` to `0.32.0` only AFTER the diff debate (CLAUDE.md, "BUMP THE VERSION AFTER THE DIFF DEBATE").
- Commit messages must not contain a token that looks like a PowerShell flag such as `-Force` or `-Prepare` (memory: the git guard reads it as a flag). Write "force" or "the force switch" in prose.

---

### Task 1: Branch, retained poll, backlog items 90, 91 and 92

**Files:**
- Create: `docs/superpowers/plans/rounds/2026-09-05-mirror-link-poll/brief.md`
- Create: `docs/superpowers/plans/rounds/2026-09-05-mirror-link-poll/reply.md`
- Modify: `BACKLOG.md` (ranking list under `### Second - taxes every cycle`, and three new items appended after item 89)

**Interfaces:**
- Consumes: nothing.
- Produces: item ids 90, 91, 92 that later commit messages and the record cite.

- [ ] **Step 1: Use the existing branch**

The branch `mirror-link-relink` already exists and carries the design, this plan, and the plan debate's fixes. Check it out and confirm it is ahead of `main`:

```bash
git checkout mirror-link-relink && git log --oneline main..HEAD
```

Expected: at least two commits listed, the first of them `draft the mirror link re-link design and plan for item 90`. If the branch does not exist, stop and report; do not create a new one.

- [ ] **Step 2: Retain the Astra poll**

Copy the two files from the session scratchpad. Their source paths are `C:\Users\Brandon\AppData\Local\Temp\claude\C--Users-Brandon-Documents-parallax\0f17a7a2-52fe-418e-b80e-a4f68e9e3515\scratchpad\astra-poll\brief.md` and `...\astra-poll\reply` (rename the reply to `reply.md`). If the scratchpad is gone, say so in the commit message and create the directory with a `README.md` stating the poll's verdict ("AGREE WITH CHANGES", 2026-09-05, gpt-6-astra at high effort) and that the brief and reply were not recoverable.

```powershell
$src = "C:\Users\Brandon\AppData\Local\Temp\claude\C--Users-Brandon-Documents-parallax\0f17a7a2-52fe-418e-b80e-a4f68e9e3515\scratchpad\astra-poll"
$dst = "docs\superpowers\plans\rounds\2026-09-05-mirror-link-poll"
New-Item -ItemType Directory -Force $dst | Out-Null
Copy-Item "$src\brief.md" "$dst\brief.md"
Copy-Item "$src\reply" "$dst\reply.md"
```

- [ ] **Step 3: Add the ranking lines**

In `BACKLOG.md`, under `### Second - taxes every cycle`, after the line `- 77`, add:

```markdown
- 90
- 91
```

Under `### First - breaks the repo's own review process`, after `- 58`, add:

```markdown
- 92
```

- [ ] **Step 4: Append the three items after item 89's text**

Append at the end of `BACKLOG.md` (item 89 is currently last). The `Verified` digests are filled in Step 5.

```markdown
## 90. The review mirror copies through directory links and doubles its size
Status: OPEN
Cost: every mirror build of a repo that links a reference checkout writes the whole target as ordinary files, measured 2026-09-05 at 14,884 extra files for one 14k-file addon, so each build pays twice the copy it needs
Pairs: 91
Verified: 2026-09-05 PLACEHOLDER

**Filed 2026-09-05 from the user's report** that the mirror of a WoW addon
repo doubles in size because `robocopy /E` follows the `.wow-api-reference`
link onto a shared API reference checkout. Design:
`docs/superpowers/specs/2026-09-05-mirror-link-relink-design.md`. Plan:
`docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md`. Astra was
polled first and agreed with changes; the poll is retained under
`docs/superpowers/plans/rounds/2026-09-05-mirror-link-poll/`.

**The change.** The path-budget walk records each directory link, keeps
descending through it so the cycle and overlap refusals see a link
behind a link, and counts nothing beneath it against the budget; every
link target the walk reaches becomes a protected tree that the mirror
and override paths may not overlap or pass through; the copy runs with
`/XJD`; the manifest starts a listing at every link beneath a subject;
after the final back-channel sweep the tool creates a junction per
recorded link onto the same resolved target and then re-enumerates
back-channels READ-ONLY, blocking if any sit under a link. No new
identity fields: measured 2026-09-05, both hosts hash through a link
when a listing starts at the link, and the mirror's own status names the
junction as one subject, so the existing digests cover the linked bytes.

**Closing this item** means the branch is merged with the re-link case,
the drift-behind-the-link case, the redirected-link case, the rebuild
case and the back-channel-behind-a-link case green on both hosts, the
timing task's before-and-after numbers recorded here, and 0.32.0
installed and content-verified.

## 91. The identity digests hash a linked reference checkout three times per build and six times per round
Status: OPEN
Cost: a build hashes every file behind a linked checkout, its `.git` objects included, three times, and each round's three identity verifies hash it on both sides for six more passes; measured 2026-09-05 at 14,884 files per pass, so the reference is hashed more often than the addon under review
Pairs: 90
Verified: 2026-09-05 PLACEHOLDER

**Filed 2026-09-05 during item 90's design.** Item 90 removes the copy's
read and the pre-copy budget accounting only. `Get-StatusSha256` runs
before and after the copy on the source and once on the mirror, and each
run expands the link's single status entry through `Get-ChildItem
-Recurse`, hashing all 14,884 files of the reference checkout and its
`.git` internals. Every `-VerifyIdentity` call does the same on both
sides, and a round runs three of them: the dispatch tool's own at
prepare time, then the wrapper's before and after the client.
Cross-vendor round 1 of item 90's plan debate corrected the counts this
item first carried.

**A candidate fix, not decided.** A subject whose directory holds its own
`.git` could be bound by that checkout's HEAD plus its own status digest
rather than a byte walk that includes its object store. That changes the
`mirror-identity-gate` contract and needs a debate of its own; it must
not narrow coverage of a plain linked folder, which git already walks
file by file. Closing this item means a measured reduction in build and
verify time on a repo carrying `.wow-api-reference`, with the coverage
argument written into the contract region.

## 92. The back-channel sweep does not enumerate inside a nested repository
Status: OPEN
Cost: an instruction file inside a linked reference checkout reaches the reviewer unenumerated and undeleted, today with the copy and after item 90 with the junction, because `git ls-files --others` stops at a directory that holds its own `.git`
Pairs: none
Verified: 2026-09-05 PLACEHOLDER

**Filed 2026-09-05 during item 90's design, as a PRE-EXISTING gap.**
Measured on a fixture: a junction onto a directory holding `.git` is one
`ls-files` entry, so `*AGENTS.md` beneath it never matches, and the
finished-mirror sweep reports clean. The client context probe is the
only control left for that content. Item 90 deliberately does not delete
through a link, so the remedy is not "descend and delete": it is either a
read-only enumeration of each nested checkout that BLOCKS the build when
a back-channel is present, or a documented statement that linked
checkouts are outside the sweep. Closing this item means one of those
two is shipped and the `enumeration-depth-asymmetry` region says which.
```

- [ ] **Step 5: Fill the Verified digests and lint**

```bash
python evals/tools/backlog_lint.py --digests BACKLOG.md
```

Replace each `PLACEHOLDER` with the digest the lint prints for that item, then run the lint until it exits 0:

```bash
python evals/tools/backlog_lint.py
```

Expected: exit 0, no rule failures.

- [ ] **Step 6: Commit**

```bash
git add BACKLOG.md docs/superpowers/plans/rounds/2026-09-05-mirror-link-poll/brief.md docs/superpowers/plans/rounds/2026-09-05-mirror-link-poll/reply.md
git commit -m "file items 90, 91 and 92 and retain the astra mirror-link poll"
```

If Step 2 took the README fallback, stage that file instead of the two it replaces:

```bash
git add BACKLOG.md docs/superpowers/plans/rounds/2026-09-05-mirror-link-poll/README.md
git commit -m "file items 90, 91 and 92 and record that the astra poll files were not recoverable"
```

The design and plan documents are already committed on this branch (commit `ea41288`), so they are not staged here.

---

### Task 2: The contract region says re-link, test first

**Files:**
- Modify: `evals/multi-model-verify/test_backup_lane.py:1869-1929` (`test_mirror_path_budget_region`)
- Modify: `skills/multi-model-verify/references/backup-lane.md:770-810` (the `mirror-path-budget` region)

**Interfaces:**
- Consumes: nothing.
- Produces: the contract sentence the builder in Task 3 implements. Its wording is fixed here and quoted verbatim in the builder's comments.

- [ ] **Step 1: Change the pin**

In `test_mirror_path_budget_region`, replace the docstring sentence beginning "A directory link is FOLLOWED" through "the one the copy cannot complete." with:

```python
    A directory link is NOT copied through: `/XJD` excludes it and the
    tool re-creates it as a junction after the last sweep, so its
    contents are never destinations. The refusals that survive are the
    cycle case and the overlap case, because the manifest still walks
    through every link.
```

In the same test's asserted string, the literal `"never covers it and it carries its own check. A source "` stays as it is. Replace the adjacent literals that follow it, from the FOLLOWED line through the "stays refused" line:

```python
            "directory reparse point is FOLLOWED, because the copy "
            "follows it: `robocopy /E` with neither /XJ nor /SL writes "
            "the target's contents as an ordinary directory at the "
            "link's relative path, so refusing to measure across one "
            "described a SMALLER universe than the copy produces. What "
            "the copy cannot survive is a cycle, so a link onto one of "
            "its own ancestors is refused, and so is a tree whose links "
            "reach one target twice, which is indistinguishable from a "
            "cycle without walking the whole graph. A repo root that is "
            "itself a reparse point stays refused. "
```

with:

```python
            "directory reparse point is NOT copied through: the copy "
            "runs with `/XJD`, which excludes directory junctions and "
            "directory symbolic links, so the link is one destination "
            "and nothing beneath it is. After the last writer into the "
            "mirror and the last back-channel sweep, the tool re-creates "
            "each recorded link as a JUNCTION at the same relative path "
            "onto the same resolved absolute target, whatever kind of "
            "link the source had, because a junction needs no privilege "
            "and reads identically. It then enumerates back-channels "
            "once more, READ-ONLY, and BLOCKS if any entry sits under a "
            "re-linked path: the build never deletes through a link. "
            "The manifest still walks through every link, so a link onto "
            "one of its own ancestors is refused, and so is a tree whose "
            "links reach one target twice, which is indistinguishable "
            "from a cycle without walking the whole graph. A repo root "
            "that is itself a reparse point stays refused. "
```

- [ ] **Step 2: Run the pin to see it fail**

```bash
python -m pytest evals/multi-model-verify/test_backup_lane.py::test_mirror_path_budget_region -q
```

Expected: FAIL (the Markdown still carries the FOLLOWED clause).

- [ ] **Step 3: Rewrite the region**

In `skills/multi-model-verify/references/backup-lane.md`, inside the `mirror-path-budget` region, replace the sentences from "A source directory reparse point is FOLLOWED" through "A repo root that is itself a reparse point stays refused." with the same words as the new pin, wrapped to the file's indentation. The pin compares through `_norm`, so line breaks are free, but keep every word and every backtick identical:

```markdown
  never covers it and it carries its own check. A source directory
  reparse point is NOT copied through: the copy runs with `/XJD`, which
  excludes directory junctions and directory symbolic links, so the
  link is one destination and nothing beneath it is. After the last
  writer into the mirror and the last back-channel sweep, the tool
  re-creates each recorded link as a JUNCTION at the same relative path
  onto the same resolved absolute target, whatever kind of link the
  source had, because a junction needs no privilege and reads
  identically. It then enumerates back-channels once more, READ-ONLY,
  and BLOCKS if any entry sits under a re-linked path: the build never
  deletes through a link. The manifest still walks through every link,
  so a link onto one of its own ancestors is refused, and so is a tree
  whose links reach one target twice, which is indistinguishable from a
  cycle without walking the whole graph. A repo root that is itself a
  reparse point stays refused. A source path that cannot be enumerated
  BLOCKS the build and is never skipped, the same hole semantics the
```

- [ ] **Step 4: Run the pin, the coverage checker and the lint**

```bash
python -m pytest evals/multi-model-verify/test_backup_lane.py::test_mirror_path_budget_region evals/multi-model-verify/test_contract_coverage.py -q
```

Expected: PASS.

```bash
python evals/tools/skill_lint.py skills/multi-model-verify --strict
```

Expected: exit 0.

- [ ] **Step 5: Commit**

```bash
git add evals/multi-model-verify/test_backup_lane.py skills/multi-model-verify/references/backup-lane.md
git commit -m "state that the mirror re-links directory links instead of copying through them"
```

---

### Task 3: The builder re-links, tests first

**Files:**
- Modify: `evals/multi-model-verify/test_review_mirror.py:1343-1374` (replace `test_a_source_directory_link_is_followed_not_refused`) and append five cases after `test_verify_refuses_a_mirror_at_a_different_path`
- Modify: `tools/new-review-mirror.ps1` (the path-budget walk near lines 923-1052, the robocopy call at line 1100, a new re-link block after the final sweep near line 1338, and the record print near line 1408)

**Interfaces:**
- Consumes: the contract wording from Task 2.
- Produces: a `links:` block in the record, each line `  <relative path> -> <absolute target>`, read by `read_block(stdout, "links:")` in the tests. Relative paths use backslashes exactly as the walk produces them.

- [ ] **Step 1: Add a junction helper and replace the follow test**

Add near the other helpers at the top of the test module, after `assert_built`:

```python
import stat


def make_junction(link, target):
    """A junction via mklink /J, or skip. Junctions need no privilege;
    symbolic links do, and this session cannot make one."""
    rc = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)],
                        capture_output=True, text=True)
    if rc.returncode != 0:
        pytest.skip("junction creation unavailable: " + rc.stderr)


def unlink_junction(link):
    """rmdir removes the junction and never its target."""
    subprocess.run(["cmd", "/c", "rmdir", str(link)],
                   capture_output=True, text=True, check=True)


def is_reparse_point(path):
    """Python's is_symlink() is False for a junction, so read the
    attribute bit the filesystem sets for both kinds of link."""
    return bool(os.lstat(str(path)).st_file_attributes
                & stat.FILE_ATTRIBUTE_REPARSE_POINT)
```

Replace `test_a_source_directory_link_is_followed_not_refused` in full with:

```python
def test_a_source_directory_link_is_recreated_as_a_junction(tmp_path):
    """The copy runs with /XJD, so the link's contents are never
    destinations, and the tool re-creates the link as a junction after
    the last sweep. The reviewer reads the same bytes at the same
    relative path, and the manifest expands through it."""
    repo = make_repo(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "x.txt").write_text("linked\n")
    make_junction(repo / "linked", outside)
    mirror = long_mirror(tmp_path)
    proc = run_mirror(repo, mirror)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert SKIP_BLOCK in proc.stdout, proc.stdout
    relinked = mirror / "linked"
    assert is_reparse_point(relinked), proc.stdout
    assert (relinked / "x.txt").read_text() == "linked\n"
    manifest = [l.split(" ")[0] for l in read_block(proc.stdout, "manifest:")]
    assert "linked/x.txt" in manifest, proc.stdout
    links = read_block(proc.stdout, "links:")
    # Case-insensitive: the filesystem is, and a drive letter's case can
    # differ between Python's resolve() and .NET's GetFullPath().
    assert [l.lower() for l in links] == \
        [("linked -> " + str(outside.resolve())).lower()], proc.stdout
```

- [ ] **Step 2: Append the new cases after `test_verify_refuses_a_mirror_at_a_different_path`**

Fifteen cases follow. Each is listed in Step 3's `-k` selection.

```python
def test_verify_detects_an_edit_behind_the_mirror_link(tmp_path):
    """The junction's target is a review input. Editing it after
    construction must block the next verify: the source fingerprint
    sees it through the source link, the mirror fingerprint through the
    junction, and either message ends the round."""
    repo = make_repo(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "x.txt").write_text("linked\n")
    make_junction(repo / "linked", outside)
    mirror = tmp_path / "mirror"
    _, ident = build_and_read(repo, mirror)
    (outside / "x.txt").write_text("edited behind the link\n")
    proc = run_verify(repo, mirror, ident)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "changed since construction" in proc.stdout, proc.stdout


def test_verify_detects_a_redirected_mirror_link(tmp_path):
    """A junction re-pointed at different content moves the mirror-state
    digest, because the manifest hashes what the link resolves to, not
    the link's name."""
    repo = make_repo(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "x.txt").write_text("linked\n")
    make_junction(repo / "linked", outside)
    mirror = tmp_path / "mirror"
    _, ident = build_and_read(repo, mirror)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    (elsewhere / "x.txt").write_text("different bytes\n")
    unlink_junction(mirror / "linked")
    make_junction(mirror / "linked", elsewhere)
    proc = run_verify(repo, mirror, ident)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "the mirror's contents changed" in proc.stdout, proc.stdout


def test_a_forced_rebuild_does_not_reach_through_the_mirror_link(tmp_path):
    """The force switch deletes the old mirror recursively. Measured
    2026-09-05 on both hosts that the delete stops at a junction; this
    case keeps that measured."""
    repo = make_repo(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "x.txt").write_text("linked\n")
    make_junction(repo / "linked", outside)
    mirror = tmp_path / "mirror"
    assert_built(run_mirror(repo, mirror))
    assert is_reparse_point(mirror / "linked")
    assert_built(run_mirror(repo, mirror, "-Force"))
    assert (outside / "x.txt").read_text() == "linked\n"
    assert is_reparse_point(mirror / "linked")


def test_a_back_channel_behind_a_link_blocks_and_is_not_deleted(tmp_path):
    """The sweep after re-linking is READ-ONLY. A back-channel reachable
    through a junction blocks the build with its path named, and the
    file behind the link is untouched."""
    repo = make_repo(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "AGENTS.md").write_text("instructions behind the link\n")
    make_junction(repo / "linked", outside)
    mirror = tmp_path / "mirror"
    proc = run_mirror(repo, mirror)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "under a re-linked path" in proc.stdout, proc.stdout
    assert "linked/AGENTS.md" in proc.stdout, proc.stdout
    assert (outside / "AGENTS.md").read_text() == "instructions behind the link\n"


def test_a_link_target_that_vanishes_before_relink_blocks(tmp_path):
    """The walk resolved a target; the copy did not need it; the re-link
    does. A target gone by then is a block, never a mirror missing a
    review input that reads as complete."""
    repo = make_repo(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "x.txt").write_text("linked\n")
    make_junction(repo / "linked", outside)
    mirror = tmp_path / "mirror"
    # -ExtraInput runs between the copy and the re-link, and is the only
    # shipped seam there, so a missing target is simulated by pointing
    # the source link at a directory that is removed before the build.
    unlink_junction(repo / "linked")
    gone = tmp_path / "gone"
    gone.mkdir()
    make_junction(repo / "linked", gone)
    gone.rmdir()
    proc = run_mirror(repo, mirror)
    # Which guard fires first is not the property under test: the source
    # status capture may already stop on a dangling subject before the
    # re-link step does. The property is that a vanished target never
    # yields a mirror that reports itself built.
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert SKIP_BLOCK not in proc.stdout, proc.stdout
    assert not (mirror / "linked").exists() or is_reparse_point(mirror / "linked")


def test_a_cycle_behind_a_link_is_still_refused(tmp_path):
    """Cross-vendor round 1: a walk that stops at the outer link never
    sees an inner cycle. The walk keeps descending through links for
    validation while counting nothing beneath them against the budget.
    `outside/self` points at `outside`, which `linked` already reached,
    so the overlap refusal fires; the ancestor refusal would also be a
    correct answer, so either message passes."""
    repo = make_repo(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "x.txt").write_text("linked\n")
    make_junction(outside / "self", outside)
    make_junction(repo / "linked", outside)
    mirror = tmp_path / "mirror"
    proc = run_mirror(repo, mirror)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    low = proc.stdout.lower()
    assert "links overlap" in low or "never terminate" in low, proc.stdout
    assert not mirror.exists()


def _make_checkout(path):
    """A directory that is its own git repository, the shape of the
    user's reference checkout. git lists a junction onto it as ONE
    status entry and never descends (measured 2026-09-05)."""
    path.mkdir()
    git(path.parent, "init", "-q", str(path))
    (path / "x.txt").write_text("reference\n")
    git(path, "add", "x.txt")
    commit(path, "reference base")


def test_a_junction_onto_a_nested_checkout_is_one_subject_and_fully_hashed(tmp_path):
    """The central case. The status names the junction once, with a
    trailing slash, and the manifest expands through it to every file,
    the checkout's own .git included."""
    repo = make_repo(tmp_path)
    outside = tmp_path / "outside"
    _make_checkout(outside)
    make_junction(repo / "linked", outside)
    mirror = tmp_path / "mirror"
    proc = run_mirror(repo, mirror)
    assert_built(proc)
    baseline = read_block(proc.stdout, "baseline:")
    assert [b for b in baseline if "linked" in b] == ["?? linked/"], baseline
    manifest = [l.split(" ")[0] for l in read_block(proc.stdout, "manifest:")]
    assert "linked/x.txt" in manifest, proc.stdout
    assert "linked/.git/HEAD" in manifest, proc.stdout
    assert is_reparse_point(mirror / "linked")


def test_verify_detects_drift_behind_a_nested_checkout_junction(tmp_path):
    repo = make_repo(tmp_path)
    outside = tmp_path / "outside"
    _make_checkout(outside)
    make_junction(repo / "linked", outside)
    mirror = tmp_path / "mirror"
    _, ident = build_and_read(repo, mirror)
    (outside / "x.txt").write_text("reference edited\n")
    proc = run_verify(repo, mirror, ident)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "changed since construction" in proc.stdout, proc.stdout


def test_verify_detects_a_redirected_nested_checkout_junction(tmp_path):
    """Mirror-only change: the source still points at the original
    checkout, so only the mirror-state digest can see this."""
    repo = make_repo(tmp_path)
    outside = tmp_path / "outside"
    _make_checkout(outside)
    make_junction(repo / "linked", outside)
    mirror = tmp_path / "mirror"
    _, ident = build_and_read(repo, mirror)
    elsewhere = tmp_path / "elsewhere"
    _make_checkout(elsewhere)
    (elsewhere / "x.txt").write_text("a different checkout\n")
    unlink_junction(mirror / "linked")
    make_junction(mirror / "linked", elsewhere)
    proc = run_verify(repo, mirror, ident)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "the mirror's contents changed" in proc.stdout, proc.stdout


def test_a_link_behind_a_nested_checkout_junction_is_hashed(tmp_path):
    """Measured 2026-09-05 on both hosts: Get-ChildItem -Recurse from a
    parent lists a junction and does not pass through it. A nested
    checkout is ONE status subject (cross-vendor round 2 showed an
    ignored plain directory is not: -uall lists its files one by one),
    so a link inside the checkout was reached by no recursion at all.
    The manifest now starts a listing at every link beneath a subject.
    The baseline assertion is what proves the subject shape."""
    repo = make_repo(tmp_path)
    outside = tmp_path / "outside"
    _make_checkout(outside)
    deeper = tmp_path / "deeper"
    deeper.mkdir()
    (deeper / "deep.txt").write_text("behind a nested link\n")
    make_junction(outside / "inner", deeper)
    make_junction(repo / "linked", outside)
    mirror = tmp_path / "mirror"
    proc = run_mirror(repo, mirror)
    assert_built(proc)
    baseline = read_block(proc.stdout, "baseline:")
    assert [b for b in baseline if "linked" in b] == ["?? linked/"], baseline
    manifest = [l.split(" ")[0] for l in read_block(proc.stdout, "manifest:")]
    assert "linked/inner/deep.txt" in manifest, proc.stdout
    _, ident = build_and_read(repo, tmp_path / "mirror2")
    (deeper / "deep.txt").write_text("edited behind a nested link\n")
    proc = run_verify(repo, tmp_path / "mirror2", ident)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "changed since construction" in proc.stdout, proc.stdout


def test_verify_refuses_a_cycle_behind_a_link_in_the_manifest(tmp_path):
    """The construction walk does not rerun at verify time, so the
    manifest's own visited set is the only cycle guard there. A junction
    planted inside the target after the build, pointing back at the
    target, is a repeat of a target the expansion already entered."""
    repo = make_repo(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "x.txt").write_text("linked\n")
    make_junction(repo / "linked", outside)
    mirror = tmp_path / "mirror"
    _, ident = build_and_read(repo, mirror)
    make_junction(outside / "self", outside)
    proc = run_verify(repo, mirror, ident)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "repeats or cycles" in proc.stdout, proc.stdout


def test_an_inner_link_target_is_protected(tmp_path):
    """Cross-vendor round 2: with repo/outer -> A and A/inner -> B, a
    guard over recorded (outer) links alone protects A and lets a mirror
    path at B with the force switch delete B. Every target the walk
    reaches is protected."""
    repo = make_repo(tmp_path)
    a = tmp_path / "a"
    a.mkdir()
    b = tmp_path / "b"
    b.mkdir()
    (b / "keep.txt").write_text("inner target\n")
    make_junction(a / "inner", b)
    make_junction(repo / "outer", a)
    proc = run_mirror(repo, b, "-Force")
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "overlaps the target of a source link" in proc.stdout, proc.stdout
    assert (b / "keep.txt").read_text() == "inner target\n"


def test_a_mirror_path_through_a_link_is_refused(tmp_path):
    """Cross-vendor round 2: a text comparison cannot see that a mirror
    path spelled through some other junction lands inside a protected
    target. Any mirror or override path with a reparse point among its
    existing ancestors is refused outright."""
    repo = make_repo(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "x.txt").write_text("linked\n")
    make_junction(repo / "linked", outside)
    alias = tmp_path / "alias"
    make_junction(alias, outside)
    proc = run_mirror(repo, alias / "mirror")
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "passes through a directory link" in proc.stdout, proc.stdout
    assert not (alias / "mirror").exists()
    assert (outside / "x.txt").read_text() == "linked\n"
    proc = run_mirror(repo, tmp_path / "mirror", "-OverrideOut", str(alias / "o.txt"))
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "passes through a directory link" in proc.stdout, proc.stdout
    assert not (outside / "o.txt").exists()


def test_a_dot_git_that_is_a_link_is_refused(tmp_path):
    """git's optional index refresh writes the repository's own
    .git/index. That is not a write through a link only while .git is
    not a link, so the walk refuses one."""
    repo = make_repo(tmp_path)
    real_git = tmp_path / "real-git"
    shutil.move(str(repo / ".git"), str(real_git))
    make_junction(repo / ".git", real_git)
    proc = run_mirror(repo, tmp_path / "mirror")
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert ".git is a directory link" in proc.stdout, proc.stdout


def test_a_mirror_path_at_a_link_target_is_refused(tmp_path):
    """Cross-vendor round 1: the overlap guard compared only against the
    source root, so a mirror path at the reference checkout with the
    force switch would have deleted the checkout."""
    repo = make_repo(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "x.txt").write_text("linked\n")
    make_junction(repo / "linked", outside)
    proc = run_mirror(repo, outside, "-Force")
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "overlaps the target of a source link" in proc.stdout, proc.stdout
    assert (outside / "x.txt").read_text() == "linked\n"
    inside = outside / "sub"
    proc = run_mirror(repo, inside)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "overlaps the target of a source link" in proc.stdout, proc.stdout
    assert not inside.exists()


def test_an_override_path_at_a_link_target_is_refused(tmp_path):
    repo = make_repo(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "x.txt").write_text("linked\n")
    make_junction(repo / "linked", outside)
    mirror = tmp_path / "mirror"
    proc = run_mirror(repo, mirror, "-OverrideOut", str(outside / "override.txt"))
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "overlaps the target of a source link" in proc.stdout, proc.stdout
    assert not (outside / "override.txt").exists()
    assert not mirror.exists()
```

- [ ] **Step 3: Run the new and changed cases to see them fail**

```bash
python -m pytest evals/multi-model-verify/test_review_mirror.py -q -k "junction or behind or redirected or forced_rebuild or vanishes or nested or link_target or inner_link or through_a_link or dot_git or cycle"
```

Expected: the re-link, redirected, back-channel, forced-rebuild, nested-checkout, link-behind-checkout, manifest-cycle, inner-target, through-a-link, dot-git and link-target cases FAIL (no `links:` block, the mirror's `linked` is a plain directory, no overlap or pass-through refusal exists, the manifest has no visited set). The vanishing-target case may already pass because the walk refuses an unresolvable target, and the cycle-behind-a-link construction case already passes because today's walk descends; both stay in the run so Step 8 proves they still pass. Record which cases were red at this step in the commit message of Step 9, because a case that was never red proves nothing about the code it names.

- [ ] **Step 4: Record links in the walk, keep descending for validation, stop counting beneath them**

In `tools/new-review-mirror.ps1`, replace the two lines

```powershell
$pending = New-Object System.Collections.Stack
$pending.Push($srcRoot)
```

with:

```powershell
# Every directory link the walk meets that is NOT itself behind another
# link: its relative path under the source root and its resolved
# absolute target. The copy runs with /XJD and creates nothing beneath a
# link, so a link is ONE destination and the entries beneath it are not
# measured against the budget. The walk still DESCENDS through it,
# because the cycle refusal and the overlap refusal apply to every link
# the manifest can reach, and a link behind a link is reachable; a walk
# that stopped at the outer link never saw an inner cycle (cross-vendor
# round 1, 2026-09-05). A link behind a link is not recorded: it exists
# in the target and is reached through the outer junction.
$sourceLinks = New-Object System.Collections.ArrayList

$pending = New-Object System.Collections.Stack
$pending.Push(@{ Path = $srcRoot; UnderLink = $false })
```

Replace `$dir = $pending.Pop()` with:

```powershell
    $item = $pending.Pop()
    $dir = $item.Path
    $underLink = $item.UnderLink
```

Inside the `foreach ($entry in $entries)` loop, replace the comment block that begins `# Source reparse points are FOLLOWED, because the copy follows` through `# guarded below, and it still refuses.` with:

```powershell
        # A source directory reparse point is NOT copied through: the
        # copy runs with /XJD, which excludes directory junctions and
        # directory symbolic links, so the link is one destination and
        # nothing beneath it is. The re-link step after the final sweep
        # re-creates it as a junction. The walk still enters it, for the
        # two refusals below only: measured 2026-09-05, the manifest
        # expansion starts a listing at every link it finds, so a link
        # onto one of its own ancestors or a tree whose links reach one
        # target twice must be refused wherever it sits.
        $isDirLink = $false
```

Set the flag at the top of the existing `if (($attr -band $reparseAttr) -ne 0 -and ($attr -band $dirAttr) -ne 0) {` block, as its first statement, and refuse a `.git` that is a link:

```powershell
            $isDirLink = $true
            # git's optional index refresh writes the repository's own
            # .git/index during every status capture. That is a write
            # into the repository and never through a link only while
            # .git is not itself a link, so one is refused here rather
            # than assumed away (cross-vendor round 2, 2026-09-05).
            if ([System.IO.Path]::GetFileName($entry) -ieq ".git") {
                Write-Output ("ERROR: $entry - .git is a directory link, and" +
                    " the status captures write the repository's own index," +
                    " so this tree cannot be measured without writing" +
                    " through a link")
                exit 2
            }
```

After the existing overlap refusal (`if (-not $followedTargets.Add($targetFull)) { ... exit 2 }`), still inside the reparse block, add:

```powershell
            if (-not $underLink) {
                [void]$sourceLinks.Add(@{ Rel = $entry.Substring($srcPrefix.Length)
                                          Target = $targetFull })
            }
```

Replace the deepest-path accounting and the final push, which currently read

```powershell
        $rel = $entry.Substring($srcPrefix.Length)
        if ($rel.Length -gt $deepestLen) {
            $deepestLen = $rel.Length
            $deepestRel = $rel
        }
        if (($attr -band $dirAttr) -ne 0) { $pending.Push($entry) }
```

with:

```powershell
        # Only a destination counts. The link itself is one; nothing
        # beneath any link is created by the copy.
        if (-not $underLink) {
            $rel = $entry.Substring($srcPrefix.Length)
            if ($rel.Length -gt $deepestLen) {
                $deepestLen = $rel.Length
                $deepestRel = $rel
            }
        }
        if (($attr -band $dirAttr) -ne 0) {
            $pending.Push(@{ Path = $entry; UnderLink = ($underLink -or $isDirLink) })
        }
```

- [ ] **Step 4b: Refuse a mirror or override path that overlaps any link target or passes through a link**

Immediately after the walk's budget refusal (the `if ($deepestLen -ge 0) { ... }` block) and BEFORE `if (Test-Path $MirrorPath) {`, add. `$mp`, `$op` and `$cmp` are the normalised values the overlap guard above already computed, and `$followedTargets` is the walk's set of EVERY resolved link target, inner links included:

```powershell
# LINK TARGETS ARE PROTECTED TREES. The overlap guard above compares the
# mirror and override paths against the source root only, and a link
# target lives outside it. Cross-vendor round 1 (2026-09-05) named the
# case: -MirrorPath at a link's target with -Force would delete the
# user's reference checkout, and -OverrideOut inside it would write
# there. Round 2 added two more: an INNER link's target is reached by
# the manifest just the same, so every target the walk followed is
# protected, not only the recorded outer links; and a path spelled
# THROUGH some other link can land inside a protected target without
# matching its spelling, so a mirror or override path with a reparse
# point among its existing ancestors is refused outright rather than
# compared. This runs before anything is created or deleted.
foreach ($pair in @(@("mirror path", $MirrorPath), @("override path", $OverrideOut))) {
    $label = $pair[0]
    $probe = $pair[1].TrimEnd("\", "/")
    while ($probe -and -not [string]::IsNullOrEmpty([System.IO.Path]::GetFileName($probe))) {
        if (Test-Path -LiteralPath $probe) {
            $pa = 0
            try {
                $pa = [int][System.IO.File]::GetAttributes($probe)
            } catch {
                Write-Output ("ERROR: " + $probe + " could not be read while" +
                    " checking whether the " + $label + " passes through a" +
                    " link: " + $_.Exception.Message)
                exit 2
            }
            if (($pa -band $reparseAttr) -ne 0) {
                Write-Output ("ERROR: the " + $label + " passes through a" +
                    " directory link at " + $probe + " - a path reached" +
                    " through a link can alias a tree the mirror only links" +
                    " to, so the mirror refuses it")
                exit 2
            }
        }
        $probe = [System.IO.Path]::GetDirectoryName($probe)
    }
}
foreach ($target in @($followedTargets)) {
    $tp = ([string]$target).Replace("\", "/").TrimEnd("/") + "/"
    foreach ($pair in @(@("mirror path", $mp), @("override path", ($op + "/")))) {
        $label = $pair[0]
        $cand = $pair[1]
        if ($cand.Equals($tp, $cmp) -or $cand.StartsWith($tp, $cmp) -or
            $tp.StartsWith($cand, $cmp)) {
            Write-Output ("ERROR: the " + $label + " overlaps the target of a" +
                " source link (" + $target + ") - building there would write" +
                " into, or delete, a tree the mirror only links to")
            exit 2
        }
    }
}
```

- [ ] **Step 4c: Expand nested links in the manifest**

Add this function immediately BEFORE `function Get-ContentManifest($repo, $paths) {`:

```powershell
function Get-FilesBeneath($start, $visited, $depth) {
    # Every file beneath $start, INCLUDING files behind every directory
    # link found under it, as full paths. Measured 2026-09-05 on both
    # hosts: Get-ChildItem -Recurse enters a link only when the link IS
    # the start path; from a parent it lists the link and does not pass
    # through it. So each link beneath a subject gets a listing of its
    # own, started at the link. $visited holds every resolved link
    # target this expansion has entered, seeded by the caller with the
    # repository root; a repeat is a refusal. Cross-vendor round 2
    # (2026-09-05) showed the visited set alone is not a cycle guard: a
    # RELATIVE symbolic-link target resolved against the link's spelled
    # parent yields a new string on every level of a cycle reached
    # through an outer junction. $depth is the bound that closes that:
    # a link nested more than 16 links deep is refused. Returns
    # @{Paths=..} or @{Error=..}.
    if ($depth -gt 16) {
        return @{ Error = ("'" + $start + "' sits more than 16 directory" +
            " links deep; the manifest refuses a link graph that deep" +
            " because a relative-link cycle presents exactly like it") }
    }
    $out = New-Object System.Collections.ArrayList
    $startAttr = 0
    try {
        $startAttr = [int][System.IO.File]::GetAttributes($start)
    } catch {
        return @{ Error = ("'" + $start + "' could not be read: " +
                           $_.Exception.Message) }
    }
    if (($startAttr -band [int][System.IO.FileAttributes]::ReparsePoint) -ne 0) {
        $target = $null
        try {
            $target = (Get-Item -LiteralPath $start -Force -ErrorAction Stop).Target
            if ($null -ne $target -and $target -isnot [string]) {
                foreach ($candidate in $target) { $target = $candidate; break }
            }
        } catch { $target = $null }
        if ([string]::IsNullOrEmpty($target)) {
            return @{ Error = ("'" + $start + "' is a directory link whose" +
                               " target could not be read") }
        }
        $targetFull = ""
        if ([System.IO.Path]::IsPathRooted($target)) {
            $targetFull = [System.IO.Path]::GetFullPath($target)
        } else {
            $targetFull = [System.IO.Path]::GetFullPath(
                [System.IO.Path]::Combine(
                    [System.IO.Path]::GetDirectoryName(
                        [System.IO.Path]::GetFullPath($start)), $target))
        }
        if (-not $visited.Add($targetFull.TrimEnd("\"))) {
            return @{ Error = ("'" + $start + "' reaches " + $targetFull +
                " which this expansion already entered; the manifest refuses" +
                " a link graph that repeats or cycles") }
        }
    }
    $found = $null
    try {
        $found = Get-ChildItem -LiteralPath $start -Recurse -File -Force `
            -ErrorAction Stop
    } catch {
        return @{ Error = ("'" + $start + "' could not be enumerated: " +
                           $_.Exception.Message) }
    }
    foreach ($f in $found) { [void]$out.Add($f.FullName) }
    $links = $null
    try {
        $links = @(Get-ChildItem -LiteralPath $start -Recurse -Directory -Force `
            -ErrorAction Stop | Where-Object {
                ($_.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0 })
    } catch {
        return @{ Error = ("'" + $start + "' could not be enumerated for" +
                           " links: " + $_.Exception.Message) }
    }
    foreach ($l in $links) {
        $inner = Get-FilesBeneath $l.FullName $visited ($depth + 1)
        if ($inner.ContainsKey("Error")) { return $inner }
        foreach ($p in @($inner.Paths)) { [void]$out.Add($p) }
    }
    return @{ Paths = @($out) }
}
```

In `Get-ContentManifest`, replace the directory branch's body, which currently reads

```powershell
            $found = $null
            try {
                $found = Get-ChildItem -LiteralPath $full -Recurse -File `
                    -Force -ErrorAction Stop
            } catch {
                return @{ Error = ("'" + $p + "' could not be enumerated: " +
                                   $_.Exception.Message) }
            }
            foreach ($f in $found) {
                $rel = $f.FullName.Substring($repo.Length + 1)
                [void]$files.Add($rel.Replace("\", "/"))
            }
```

with:

```powershell
            # Seeded with the repository root: a link back onto the root
            # is a cycle on its first step, not its second.
            $visited = New-Object "System.Collections.Generic.HashSet[string]" (
                [System.StringComparer]::OrdinalIgnoreCase)
            [void]$visited.Add([System.IO.Path]::GetFullPath($repo).TrimEnd("\"))
            $beneath = Get-FilesBeneath $full $visited 0
            if ($beneath.ContainsKey("Error")) {
                return @{ Error = ("'" + $p + "': " + $beneath.Error) }
            }
            foreach ($fullName in @($beneath.Paths)) {
                $rel = $fullName.Substring($repo.Length + 1)
                [void]$files.Add($rel.Replace("\", "/"))
            }
```

Update the function's leading comment to add, after `identifies nothing.`:

```powershell
    # A directory link beneath a subject is expanded by a listing started
    # at the link (Get-FilesBeneath), because a recursion from the parent
    # does not pass through it on either host.
```

- [ ] **Step 5: Exclude directory links from the copy**

Replace the robocopy line:

```powershell
& robocopy $RepoRoot $MirrorPath /E /COPY:DAT /R:1 /W:1 /NFL /NDL /NJH /NJS /NP | Out-Null
```

with:

```powershell
# /XJD: directory junctions and directory symbolic links are not copied
# through. Measured 2026-09-05: the link is absent from the destination
# and every ordinary file copies. File links are NOT excluded, so a file
# symbolic link still lands as its target's bytes, exactly as before.
& robocopy $RepoRoot $MirrorPath /E /XJD /COPY:DAT /R:1 /W:1 /NFL /NDL /NJH /NJS /NP | Out-Null
```

- [ ] **Step 6: Re-link after the final sweep, then check read-only**

Immediately after the final sweep's block (the one that ends `" an -ExtraInput may not name an instruction channel.")` / `exit 1` / `}`), and BEFORE `$head = (& git -C $MirrorPath rev-parse HEAD ...`, add:

```powershell
# RE-LINK, after the last writer and the last sweep. Remediation deletes
# what it finds with Remove-Item, and after this step that path would
# reach THROUGH a junction into the user's real reference checkout. So
# the junctions are created here, once nothing above can delete again,
# and the check that follows is READ-ONLY.
#
# Always a JUNCTION, whatever the source had. Measured 2026-09-05: a
# symbolic link needs a privilege this tool cannot assume and mklink /D
# refused it; New-Item -ItemType Junction succeeded on both hosts with
# none. The reviewer reads a junction as a directory.
foreach ($lnk in @($sourceLinks)) {
    $dest = Join-Path $MirrorPath $lnk.Rel
    if (Test-Path -LiteralPath $dest) {
        Write-Output ("BLOCKED: the copy created '" + $lnk.Rel + "' although" +
            " /XJD excludes directory links, so the mirror already holds" +
            " something at a path that must be a junction")
        exit 1
    }
    if (-not (Test-Path -LiteralPath $lnk.Target -PathType Container)) {
        Write-Output ("ERROR: the link target " + $lnk.Target + " for '" +
            $lnk.Rel + "' could not be read at re-link time, so the mirror" +
            " would be missing a review input that reads as complete")
        exit 2
    }
    $parent = Split-Path $dest -Parent
    if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
        Write-Output ("BLOCKED: the parent directory of '" + $lnk.Rel + "'" +
            " is missing from the mirror, so the copy did not produce the" +
            " tree the walk measured")
        exit 1
    }
    try {
        New-Item -ItemType Junction -Path $dest -Target $lnk.Target `
            -ErrorAction Stop | Out-Null
    } catch {
        Write-Output ("BLOCKED: could not re-create '" + $lnk.Rel + "' as a" +
            " junction onto " + $lnk.Target + ": " + $_.Exception.Message)
        exit 1
    }
    # Read the junction back. A link that does not resolve to the
    # recorded target is a mirror pointing somewhere the record does not
    # say, which is the case the whole identity gate exists to refuse.
    $made = $null
    try {
        $made = (Get-Item -LiteralPath $dest -Force -ErrorAction Stop).Target
        if ($null -ne $made -and $made -isnot [string]) {
            foreach ($candidate in $made) { $made = $candidate; break }
        }
    } catch { $made = $null }
    if ([string]::IsNullOrEmpty($made)) {
        Write-Output ("BLOCKED: the junction at '" + $lnk.Rel + "' was" +
            " created but its target could not be read back")
        exit 1
    }
    $madeFull = [System.IO.Path]::GetFullPath($made).TrimEnd("\")
    if (-not $madeFull.Equals($lnk.Target.TrimEnd("\"), "OrdinalIgnoreCase")) {
        Write-Output ("BLOCKED: the junction at '" + $lnk.Rel + "' resolves" +
            " to " + $madeFull + " rather than the recorded " + $lnk.Target)
        exit 1
    }
}

# THE LINK SWEEP, read-only by construction. git walks a junction onto a
# plain folder file by file, so a back-channel behind a link is now
# enumerable, and deleting it would delete from the user's real tree.
# Any such entry is a BLOCK with its path named; nothing here removes
# anything. A link onto a directory holding its own .git is ONE entry to
# git and is not descended; that blind spot is backlog item 92, and it
# is the same blind spot the copy had.
if (@($sourceLinks).Count -gt 0) {
    $linkSweep = Get-BackChannelEntry $MirrorPath
    if (-not $linkSweep.Ok) {
        Write-Output ("ERROR: could not enumerate back-channels behind the" +
            " re-linked paths: " + $linkSweep.Reason)
        exit 2
    }
    $behind = New-Object System.Collections.ArrayList
    foreach ($e in @($linkSweep.Entries)) {
        $eNorm = ([string]$e).Replace("\", "/")
        foreach ($lnk in @($sourceLinks)) {
            $prefix = ([string]$lnk.Rel).Replace("\", "/").TrimEnd("/") + "/"
            if ($eNorm.StartsWith($prefix, "OrdinalIgnoreCase")) {
                [void]$behind.Add($eNorm)
                break
            }
        }
    }
    if ($behind.Count -gt 0) {
        Write-Output ("BLOCKED: back-channel(s) under a re-linked path: " +
            ($behind -join "; ") + ". The build never deletes through a" +
            " link; remove the file from the link's target and rebuild.")
        exit 1
    }
}
```

- [ ] **Step 7: Print the links block in the record**

After the `manifest:` block print (`foreach ($m in $manifest) { Write-Output ("  " + $m) }`) and before `Write-Output ("probe: " + $probeLine)`, add:

```powershell
Write-Output "links:"
foreach ($lnk in @($sourceLinks)) {
    Write-Output ("  " + $lnk.Rel + " -> " + $lnk.Target)
}
```

- [ ] **Step 8: Run the whole mirror module under both hosts**

```powershell
$env:PARALLAX_PS_HOST = "powershell"; python -m pytest evals/multi-model-verify/test_review_mirror.py -q
```

```powershell
$env:PARALLAX_PS_HOST = "pwsh"; python -m pytest evals/multi-model-verify/test_review_mirror.py -q
```

Expected: PASS on both. The existing cycle and overlap cases (`test_a_link_pointing_at_its_own_ancestor_is_refused`, `test_two_links_onto_one_target_are_refused`, `test_a_relative_symlink_cycle_is_refused`, `test_a_repo_root_that_is_itself_a_reparse_point_is_refused`) must still pass unchanged.

- [ ] **Step 9: Commit**

```bash
git add tools/new-review-mirror.ps1 evals/multi-model-verify/test_review_mirror.py
git commit -m "re-link directory links as junctions in the mirror instead of copying through them"
```

---

### Task 4: Header comment and skill prose that still say "follows"

**Files:**
- Modify: `tools/new-review-mirror.ps1:1-45` (header comment)
- Modify: any file under `skills/`, `commands/`, `agents/`, `docs/superpowers/specs/2026-09-05-mirror-link-relink-design.md` excluded, that says the mirror copy follows a link

**Interfaces:**
- Consumes: Task 3's behaviour.
- Produces: nothing new; removes stale statements.

- [ ] **Step 1: Sweep for stale statements**

```bash
grep -rn -i "follows it\|FOLLOWED\|/XJ\|neither /XJ" tools/new-review-mirror.ps1 skills commands agents README.md
```

Expected hits after Task 3: only the new comments and the new region. Any other hit that says the copy follows a link is stale and must be rewritten to say the link is re-created as a junction. Report the list of files touched in the commit message.

- [ ] **Step 2: Add one paragraph to the header comment**

After the header paragraph ending `every route and containment check stayed green.` add:

```powershell
#
# Directory links are NOT copied through. robocopy runs with /XJD and the
# tool re-creates each link as a junction after the last sweep, so the
# reviewer reads the target through the same relative path while the
# mirror carries none of its bytes. Measured 2026-09-05: one addon's
# reference link held 14,884 files, doubling every mirror. The identity
# digests still cover that content, because the manifest expands a
# directory subject through a link on both hosts.
```

- [ ] **Step 3: Run tiers 1, 1b, 2 and 2b as named background tasks**

CLAUDE.md requires full gates in the background from the first attempt. Dispatch each as a harness background task under the name shown and read the exit code from its notification.

Task name `Gate: skill lint and scanner`:

```bash
python evals/tools/skill_lint.py skills/multi-model-verify --strict && python evals/tools/skill_scanner.py skills && python evals/tools/run_trigger_evals.py
```

Task name `Gate: pytest 7`:

```powershell
$env:PARALLAX_PS_HOST = "pwsh"; python -m pytest evals -q
```

Expected: both exit 0.

- [ ] **Step 4: Commit**

```bash
git add tools/new-review-mirror.ps1
git commit -m "say in the mirror tool header that directory links are re-linked, not copied"
```

If Step 1 touched other files, add them by explicit path to the same commit.

---

### Task 5: Measure the gain on the real addon repo

**Files:**
- Modify: `docs/superpowers/specs/2026-09-05-mirror-link-relink-design.md` (append a `## Measured after the change` section)
- Modify: `BACKLOG.md` (item 90's body gains the numbers; refresh its `Verified` digest)

**Interfaces:**
- Consumes: the merged-into-branch tool from Task 3, plus `main`'s copy of the tool for the "before" number.
- Produces: the before-and-after numbers item 90's close requires.

- [ ] **Step 1: Extract the old tool**

```bash
git show main:tools/new-review-mirror.ps1 > "C:/Users/Brandon/Documents/KitnDev/_mirror-timing-old.ps1"
```

- [ ] **Step 2: Time both builds, same repo, same host**

Run under PowerShell 7 from a directory OUTSIDE every repo. The mirror paths are short on purpose (the path budget is 260 characters). `-SkipProbe` exits 1 with the skip block; that is the successful-build outcome, and the script requires that exact line before it records a row. `GIT_OPTIONAL_LOCKS=0` stops `git status` from refreshing the addon's index during the source captures, so the task writes nothing into the user's repo (cross-vendor round 1). Save the script to the scratchpad and run it by file; do not paste it inline.

```powershell
$env:GIT_OPTIONAL_LOCKS = "0"
$repo = "C:\Users\Brandon\Documents\KitnDev\KitnEssentials"
$old = "C:\Users\Brandon\Documents\KitnDev\_mirror-timing-old.ps1"
$new = "C:\Users\Brandon\Documents\parallax\tools\new-review-mirror.ps1"
$skip = "BLOCKED: no client measurement was made (-SkipProbe)"
foreach ($pair in @(@("old", $old), @("new", $new))) {
    $label = $pair[0]; $tool = $pair[1]
    $mirror = "C:\Users\Brandon\Documents\KitnDev\_mirror-timing-$label"
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $out = @(& pwsh -NoProfile -NonInteractive -File $tool -RepoRoot $repo -MirrorPath $mirror -SkipProbe 2>&1 | ForEach-Object { [string]$_ })
    $sw.Stop()
    $built = ($out | Where-Object { $_.StartsWith($skip) }).Count -eq 1
    Write-Output ("$label build: " + [int]$sw.Elapsed.TotalSeconds + " s, exit " + $LASTEXITCODE + ", built=" + $built)
    Write-Output ($out | Where-Object { $_ -match "^(BLOCKED|ERROR)" })
    # The links block, in full, with its indented entries.
    $i = [Array]::IndexOf($out, "links:")
    if ($i -ge 0) {
        $j = $i + 1
        while ($j -lt $out.Count -and $out[$j].StartsWith("  ")) { Write-Output $out[$j]; $j++ }
        # The oracle for "the junction resolves to the same files": every
        # relative name and byte hash beneath the mirror's link equals the
        # target's. A file count from the mirror root is NOT that oracle:
        # a recursion from a parent does not pass through a junction.
        for ($k = $i + 1; $k -lt $j; $k++) {
            $parts = $out[$k].Trim() -split " -> ", 2
            $linkPath = Join-Path $mirror $parts[0]
            $target = $parts[1]
            # Errors TERMINATE (cross-vendor round 2: a non-terminating
            # error plus two empty lists compared as equal). A link
            # nested beneath either side is refused, because a listing
            # started at the link does not pass through a nested one,
            # so two equal partial listings would prove nothing.
            $ErrorActionPreference = "Stop"
            $nested = @(Get-ChildItem -LiteralPath $linkPath -Recurse -Directory -Force | Where-Object { ($_.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0 })
            if ($nested.Count -gt 0) { throw ("link " + $parts[0] + " holds nested links; this comparison cannot cover them: " + ($nested.FullName -join "; ")) }
            $a = @(Get-ChildItem -LiteralPath $linkPath -Recurse -File -Force | ForEach-Object { $_.FullName.Substring($linkPath.Length) + " " + (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash } | Sort-Object)
            $b = @(Get-ChildItem -LiteralPath $target -Recurse -File -Force | ForEach-Object { $_.FullName.Substring($target.TrimEnd("\").Length) + " " + (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash } | Sort-Object)
            if ($a.Count -eq 0 -or $b.Count -eq 0) { throw ("link " + $parts[0] + ": an empty listing is not a measurement (" + $a.Count + " through the mirror, " + $b.Count + " in the target)") }
            $same = ($a.Count -eq $b.Count) -and (@(Compare-Object -ReferenceObject $a -DifferenceObject $b).Count -eq 0)
            Write-Output ("$label link " + $parts[0] + ": " + $a.Count + " files through the mirror, " + $b.Count + " in the target, identical names and hashes: " + $same)
            if (-not $same) { throw ("link " + $parts[0] + ": the mirror's link and its target differ; the timing row is not recordable") }
        }
    } elseif ($label -eq "new") {
        throw "the new build printed no links block; the timing row is not recordable"
    }
}
```

The old build prints no `links:` block, so its row records only the time and the built flag. If a row's `built` is false, or the script throws, the build did not complete or the link check failed; record the BLOCKED, ERROR or thrown line instead of a timing row and stop. Every `true` in the report template below must be a value the script printed, never a value typed in.

If either build is refused with `links overlap`, that is the pre-existing two-links-one-target refusal firing on a second `.wow-api-reference` under `.superpowers/worktrees/`. Do NOT delete anything in the user's repo. Record the refusal verbatim in the design doc, then rerun both builds against `KitnUI` instead, which carries one link.

- [ ] **Step 3: Record and clean up**

Append to the design doc:

```markdown
## Measured after the change

Date: <date>. Repo: <repo>. Host: PowerShell 7.

| build | wall time | built (skip line present) |
|-------|-----------|---------------------------|
| old (`main`) | <n> s | true |
| new (branch) | <n> s | true |

Link check on the new build, per link: `<relative path> -> <target>`,
<n> files through the mirror, <n> in the target, identical names and
hashes: true.
```

Then remove the two timing mirrors and the extracted old tool:

```powershell
foreach ($p in @("C:\Users\Brandon\Documents\KitnDev\_mirror-timing-old", "C:\Users\Brandon\Documents\KitnDev\_mirror-timing-new", "C:\Users\Brandon\Documents\KitnDev\_mirror-timing-old.ps1")) {
    if (Test-Path -LiteralPath $p) { Remove-Item -LiteralPath $p -Recurse -Force }
}
```

Confirm afterwards that `C:\Users\Brandon\Documents\WoW-Dev\wow-api-reference` still holds 14,884 files:

```powershell
(Get-ChildItem -LiteralPath "C:\Users\Brandon\Documents\WoW-Dev\wow-api-reference" -Recurse -File -Force | Measure-Object).Count
```

- [ ] **Step 4: Put the numbers into item 90 and refresh its digest**

In item 90's body add one sentence after "Astra was polled first..." naming the two wall times and the repo. Then:

```bash
python evals/tools/backlog_lint.py --digests BACKLOG.md
```

Replace item 90's `Verified` line with today's date and the printed digest, and run `python evals/tools/backlog_lint.py` until exit 0.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/specs/2026-09-05-mirror-link-relink-design.md BACKLOG.md
git commit -m "record the measured mirror build times before and after re-linking"
```

---

### Task 6: Whole-branch review, diff debate, version, install, merge

**Files:**
- Modify: `.claude-plugin/plugin.json` (version `0.32.0`, AFTER the debate)
- Create: `docs/superpowers/plans/rounds/2026-09-05-mirror-link-relink-diff/` (briefs and replies, per CLAUDE.md "WRITE EVERY BRIEF TO DISK")

**Interfaces:**
- Consumes: every commit above.
- Produces: the attested merge.

- [ ] **Step 1: Run every gate, both hosts, as named background tasks**

CLAUDE.md requires full gates to run in the background, named by kind. Dispatch each of the three commands below as a harness background task under the name shown, and read each task's exit code from its notification.

Task name `Gate: tiers 1 to 2c`:

```bash
python evals/tools/skill_lint.py skills/multi-model-verify --strict && python evals/tools/skill_scanner.py skills && python evals/tools/check_exact_line_oracles.py && python evals/tools/run_trigger_evals.py && python evals/tools/backlog_lint.py
```

Task name `Gate: pytest 5.1`:

```powershell
$env:PARALLAX_PS_HOST = "powershell"; python -m pytest evals -q
```

Task name `Gate: pytest 7`:

```powershell
$env:PARALLAX_PS_HOST = "pwsh"; python -m pytest evals -q
```

Expected: every task exits 0.

- [ ] **Step 1b: Run the behavioural suite for the changed contract prose**

The branch edits a contract region under `skills/`, which CLAUDE.md names as the trigger for the local-only behavioural suite. Dispatch as a background task named `Gate: behavioural --head --changed`:

```bash
python evals/tools/run_behavioral_evals.py --head --changed
```

Expected: exit 0, with every skipped case printed by name. If the run selects zero cases because the changed surface intersects none, record that line in the debate record; it is a measurement of the suite's coverage, not a pass.

- [ ] **Step 2: Whole-branch review and the diff debate**

Follow `skills/multi-model-verify/SKILL.md` for a mode-diff debate on `main..HEAD`: dispatch the `parallax:fable-reviewer` agent with this plan's path and a controller-built diff package first, then the cross-vendor rounds through `tools/dispatch-round.ps1 -Prepare`, each round backgrounded and named `Astra R<n> debate round`. Ask the reviewer explicitly for INSTANCES OF THE CLASS "a path the build writes to, deletes from, or commits that could resolve through a link", or an explicit none. Queue every edit until each wrapper exits. Retain every brief and reply under the rounds directory above.

- [ ] **Step 3: Bump the version after the debate closes**

Edit `.claude-plugin/plugin.json`: `"version": "0.32.0"`.

```bash
git add .claude-plugin/plugin.json
git commit -m "bump plugin version to 0.32.0 after the mirror link re-link diff debate"
```

- [ ] **Step 4: Attest, merge, install, verify by content**

Follow `superpowers:finishing-a-development-branch` and the repo's attestation tools (`tools/write-attestation.ps1`, `tools/verify-attestation.ps1`), merge into `main` with a merge commit whose message names item 90 and 0.32.0, then:

```bash
claude plugin marketplace update parallax
```

```bash
claude plugin update parallax@parallax
```

Verify the install by content: `gitCommitSha` in `~/.claude/plugins/installed_plugins.json` must equal the merge commit, and hash `tools/new-review-mirror.ps1` in the cache against the checkout with CRLF normalized. Then push `main`.

The branch changed a file under `skills/`, so the installed copy is not live until the session restarts. Tell the user that a restart is required and that the next mirror build will use the new tool only after it.
