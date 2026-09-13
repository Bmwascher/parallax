# Mirror Parent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Review mirrors and clone bridges are built under ONE declared, fixed, short parent, `C:\pxm\<tag>`, instead of the controller host's temp directory or the drive root; every reader of the location (the declaration, its resolver, the attestation emitter's reap guard, the doctor and the skill prose) uses that parent, and the emitter refuses to reap a tree that is not under it.

**Architecture:** The `round-artifact-roots` declaration in `skills/multi-model-verify/references/model-prompting-notes.md` changes its review-mirror row to `C:/pxm/<short-name>/`. `tools/artifact-roots.ps1` stays the ONE reader: it stops substituting `<TEMP>`, gains `-Expect reviewMirror`, and puts the mirror row in its `-Assert` set. `tools/write-attestation.ps1` reads the parent THROUGH that reader (in-process, so the exit code reaches it) and adds one last identity-guard rule to `Resolve-ReapPath`, for the mirror AND the bridge: the tree must sit under the parent. `commands/doctor.md` check 10 inventories the parent as a directory and keeps the `kv*` drive-root sweep as a legacy line. The prose in SKILL.md, preflight-mirror.md and backup-lane.md names the parent. Tests: `test_artifact_roots.py` pins the row, the resolver's answer and a sweep shape for the retired `<TEMP>` form, and binds every `C:\pxm` spelling on the plugin surface to the declaration; `test_mirror_reaper.py` builds every tree a success case names under a per-test directory of the real parent and adds the refusal cases.

**Tech Stack:** PowerShell 5.1 and 7 (ASCII-only tools, LF), Python 3.12 pytest evals, GitHub Actions `powershell-hosts` job.

**Source:** BACKLOG item 107, follow-up 2 only; the handoff `C:\Users\Brandon\Documents\KitnDev\KitnEssentials\dev\docs\handoffs\parallax-mirror-parent-handoff.md`; the reap guard this extends is `docs/superpowers/specs/2026-09-13-mirror-reaper-design.md`, "The identity guard". The parent name `C:\pxm` was chosen by the user (2026-09-13). This plan was NOT debated before the build: the user directed it from the handoff, as with 0.36.0, so the mode-diff debate is the first cross-vendor gate on the work.

## Decisions the handoff left open, settled here

1. **The declared row is drive-rooted and fixed: `C:/pxm/<short-name>/`.** Forward slashes like every other row; the resolver normalizes. It is not derived from `SystemDrive`: the row is a declaration, one edit swaps it, and every reader parses it. Stated limit: a machine whose system drive is not `C:` edits the row.
2. **"Under the parent" means any depth below it, never the parent itself.** The emitter compares `<full>/` against `C:/pxm/` with `OrdinalIgnoreCase` (`StartsWith`, not `Equals`), the same form the overlap comparison at `tools/write-attestation.ps1:123` uses, and the resolver's `-Assert -Expect reviewMirror` answers the same way for the parent itself (outside), a deviation from the other rows corrected 2026-09-13 after the Fable review. A session that groups its trees in a subdirectory of the parent can still reap them; the declaration's SHAPE is one segment, and preflight-mirror.md says so.
3. **The rule covers `-ReapBridge`.** The bridge is built beside the mirror (`C:\pxm\kvs-<tag>`), the doctor counts it in the same inventory, and a bridge left outside the parent is exactly a tree the reaper should not touch by name.
4. **The emitter reads the parent through `tools/artifact-roots.ps1`, never by its own literal.** Item 100 exists because each writer read the location on its own. The resolver runs in-process (`& <tool> -RepoRoot <repo> -Json`), which the tool supports through its documented `$args` fallback, so `exit 2` inside it reaches `$LASTEXITCODE` in the emitter (measured 2026-09-13 on both hosts); any failure to read the parent exits 2 with nothing written. The read happens only when a reap parameter is given, so an emitter run without `-ReapMirror`/`-ReapBridge` never touches the resolver.
5. **The guard is the LAST rule in `Resolve-ReapPath`.** Every existing refusal fires first with its own message, so the existing refusal tests keep their trees in `tmp_path` and still name their reason; the parent guard is proven by trees that pass every earlier rule.
6. **The mirror tool does not enforce the parent.** `tools/new-review-mirror.ps1` takes `-MirrorPath` and does not read the declaration; its callers include every test fixture that builds a mirror in a temporary directory. The check before a build is `tools/artifact-roots.ps1 -Assert <mirror-path> -Expect reviewMirror`, run by the session; the check that matters is the emitter's, because the removal is the dangerous act. A mirror built elsewhere is refused at reap and removed by hand, which the prose says.
7. **`<TEMP>` leaves the resolver entirely**, with its forbidden-character screen and the test that drove it, because no row names it any more; the sweep gains a shape for `<TEMP>` so the form cannot come back.
8. **Item 107 goes PARTIAL**, follow-up 2 closed with the decision and the four edits recorded; follow-ups 1 and 3 stay in a `**What remains.**` paragraph.

## Global Constraints

- Tools under `tools/` are ASCII ONLY, LF, and run under BOTH Windows PowerShell 5.1 and PowerShell 7. Never run a native `git` call under `$ErrorActionPreference = 'Stop'`; read `$LASTEXITCODE` yourself.
- `SKILL.md` is at 6492 of `skill_lint.py`'s 6500-token ceiling (`len(body) // 4` over the frontmatter-stripped body, measured 2026-09-13). Task 3 makes EXACTLY the one edit it quotes in that file (+8 characters). After the edit run `python evals/tools/skill_lint.py skills/multi-model-verify --strict`; an ERROR line means STOP and report, never trim other text.
- Do not reflow any existing paragraph in `skills/`, `agents/` or `commands/`: raw-text pins in `evals/` break on a rewrap. Insert whole new paragraphs or sentences; edit only the text a task quotes. In particular `never inside the reviewed repository` (model-prompting-notes.md) must stay whole on one physical line, and the eight declaration lines are pinned as raw text on eight physical lines.
- Stage by explicit path (`git add <file> <file>`); `git add -A` is refused by the family git guard. Commit messages are lowercase imperative, no AI attribution, and must not contain a token that looks like a PowerShell flag (write "the expect parameter", never `-Expect`; "the reap mirror parameter", never `-ReapMirror`).
- Tests select the host through `PARALLAX_PS_HOST`. Before calling a task done, run its PowerShell-facing module under BOTH hosts, in PowerShell: `$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest <module> -q` and then the same with `"pwsh.exe"`.
- Never touch the eight directories `C:\kv-bl-*` and `C:\kvs-bl-*`, nor the three directories that already sit under `C:\pxm` (`8904109a`, `k10392`, `k92104`; other chats own them). Every test builds its own trees under pytest's `tmp_path` or under a per-test directory `C:\pxm\t-<8 hex>` that the test's fixture creates and removes.
- The worktree is `C:\Users\Brandon\Documents\_worktrees\parallax-mirror-parent` on branch `mirror-parent`; run every command from there. The primary checkout at `C:\Users\Brandon\Documents\parallax` is the session's: never write there.
- Full gate before the Fable review (the session runs it, not a task): the six CI commands in `CLAUDE.md`, under both hosts.

---

### Task 1: The declaration, the resolver and their tests

**Files:**
- Modify: `skills/multi-model-verify/references/model-prompting-notes.md` (the review-mirror row, and the "Review mirror:" bullet below the region)
- Modify: `tools/artifact-roots.ps1`
- Modify: `evals/multi-model-verify/test_artifact_roots.py`

**Interfaces:**
- Produces: declaration row `Canonical review mirror root: `C:/pxm/<short-name>/``.
- Produces: `tools/artifact-roots.ps1 -RepoRoot <repo> -Json` whose `reviewMirror` is `C:/pxm/<short-name>`; `-Assert <path> -Expect reviewMirror` exit 0 inside `C:/pxm` (any depth below it; the parent itself answers outside, unlike every other row, so the pre-build check agrees with the reap guard — corrected 2026-09-13 after the Fable review), 1 outside, 2 on a fault; the `-Expect` value list is `rounds, frozenPlan, attestation, checkpoint, reviewMirror`; text output `assert: inside review mirror root: <path>`.
- Consumes: nothing new.

- [ ] **Step 1: Write the failing tests**

In `evals/multi-model-verify/test_artifact_roots.py`:

(a) In `test_declaration_region_is_pinned_whole`, replace the line
```python
        "Canonical review mirror root: `<TEMP>/<short-name>/`\n"
```
with
```python
        "Canonical review mirror root: `C:/pxm/<short-name>/`\n"
```

(b) In `test_fixed_rows_state_their_reason_outside_the_region`, after `assert "never inside the reviewed repository" in tail`, add:
```python
    assert "never under the controller host's temp directory" in tail
    assert "-Expect reviewMirror" in tail
```

(c) In `test_resolver_prints_the_default_set`, replace the two mirror-row assertions
```python
    # The mirror row resolves OUTSIDE the repo, under the host temp dir.
    assert norm(got["reviewMirror"]).endswith("/<short-name>")
    assert not norm(got["reviewMirror"]).startswith(norm(repo) + "/")
```
with
```python
    # The mirror row is FIXED and drive-rooted: the declared parent with
    # the per-debate placeholder appended, nowhere near the repo or TEMP.
    assert norm(got["reviewMirror"]) == "c:/pxm/<short-name>"
    assert not norm(got["reviewMirror"]).startswith(norm(repo) + "/")
```

(d) Delete `test_a_forbidden_character_in_temp_is_a_parameter_fault` whole (TEMP is no longer an input of the resolver).

(e) In the `test_expect_parameter_faults_exit_2` parametrize list, the unknown value `"ledger"` stays; add one case after it:
```python
    ("-RepoRoot", "{repo}", "-Assert", "{repo}/x", "-Expect", "review-mirror"),
```
(the hyphenated text-output label is not the key; the keys are the camelCase names).

(f) After `test_assert_follows_the_override`, add:
```python
@needs_host
def test_expect_review_mirror_answers_for_the_declared_parent(tmp_path):
    # The check a session runs BEFORE building a mirror (preflight-mirror.md):
    # the declared parent accepts a direct child and a deeper path, and
    # refuses the two places mirrors used to be built, the host temp
    # directory and the drive root. The paths need not exist.
    repo = make_repo(tmp_path)
    for inside in (r"C:\pxm\kv-t", "C:/pxm/kvs-t", r"C:\pxm\t-1\kv-t"):
        proc = run_resolver("-RepoRoot", str(repo), "-Assert", inside,
                            "-Expect", "reviewMirror")
        assert proc.returncode == 0, inside + ": " + proc.stdout + proc.stderr
        assert "assert: inside review mirror root:" in proc.stdout, proc.stdout
    temp_root = os.environ.get("TEMP") or tmp_path
    for outside in (str(Path(temp_root) / "kv-t"), r"C:\kv-t", r"C:\pxmx\kv-t"):
        proc = run_resolver("-RepoRoot", str(repo), "-Assert", outside,
                            "-Expect", "reviewMirror")
        assert proc.returncode == 1, outside + ": " + proc.stdout + proc.stderr
        assert "outside every retained root" in proc.stdout, proc.stdout
    got = json.loads(run_resolver("-RepoRoot", str(repo), "-Assert", r"C:\pxm\kv-t",
                                  "-Expect", "reviewMirror", "-Json").stdout)
    assert got["assert"] == {"path": "C:/pxm/kv-t", "inside": True,
                             "root": "review mirror root",
                             "expected": "review mirror root"}


@needs_host
def test_a_mirror_path_asserted_for_another_root_is_refused(tmp_path):
    # The mirror row is in the -Assert set, so a rounds retention copy
    # aimed at the mirror parent is refused by name, like one aimed at
    # the frozen plan parent.
    repo = make_repo(tmp_path)
    proc = run_resolver("-RepoRoot", str(repo), "-Assert", r"C:\pxm\kv-t",
                        "-Expect", "rounds")
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "assert: inside review mirror root, expected rounds root" in proc.stdout
```

(g) In `FORBIDDEN_SHAPES`, append one entry after the `<git-common-dir>` shape:
```python
    ("the retired temp-directory mirror root",
     re.compile(r"<TEMP>")),
```
and at the end of `test_sweep_can_fail` add:
```python
    # The eighth shape: the mirror row's form until 2026-09-13, when the
    # parent became C:/pxm (backlog item 107); the resolver no longer
    # substitutes it, so a row or a sentence that brings it back names a
    # root nothing resolves.
    hits = [label for label, rx in FORBIDDEN_SHAPES
            if rx.search("Canonical review mirror root: `<TEMP>/<short-name>/`")]
    assert hits == ["the retired temp-directory mirror root"]
    hits = [label for label, rx in FORBIDDEN_SHAPES
            if rx.search(r"$v = $v.Replace(" + '"<TEMP>"' + ", $tempRoot)")]
    assert hits == ["the retired temp-directory mirror root"]
    assert not [label for label, rx in FORBIDDEN_SHAPES
                if rx.search("Canonical review mirror root: `C:/pxm/<short-name>/`")]
```

(h) After `test_declaration_exemption_covers_only_the_marked_region`, add:
```python
MIRROR_ROW = re.compile(r"^Canonical review mirror root: `([^`<]+)<short-name>/`$", re.M)
PARENT_SPELLING = re.compile(r"[A-Za-z]:[/\\]pxm(?![A-Za-z0-9_-])", re.I)


def declared_mirror_parent():
    """The parent the declaration names, normalized: `C:/pxm/<short-name>/`
    gives `c:/pxm`."""
    m = MIRROR_ROW.search(read(NOTES))
    assert m, "the review mirror row is not in the declared shape"
    return norm(m.group(1))


def test_every_parent_spelling_on_the_surface_is_the_declared_one():
    # Prose and the doctor NAME the parent as an example (`C:\pxm\kv-<tag>`).
    # An example is not a second declaration only while it agrees with
    # the row: every drive-rooted `pxm` spelling on the plugin surface is
    # the declared parent, so a renamed row turns each stale example red.
    parent = declared_mirror_parent()
    assert parent == "c:/pxm", parent
    seen = 0
    for pattern in PLUGIN_SURFACE:
        for f in sorted(REPO.glob(pattern)):
            if not f.is_file():
                continue
            for lineno, line in enumerate(read(f).splitlines(), 1):
                for m in PARENT_SPELLING.finditer(line):
                    seen += 1
                    assert norm(m.group(0)) == parent, (
                        f"{f.relative_to(REPO).as_posix()}:{lineno} names "
                        f"{m.group(0)}, not the declared parent")
    assert seen >= 3, "the prose examples and the doctor should name the parent"


def test_parent_spelling_regex_can_fail():
    assert PARENT_SPELLING.search(r"build at C:\pxm\kv-<tag>")
    assert PARENT_SPELLING.search("C:/pxm/<short-name>/")
    assert not PARENT_SPELLING.search(r"C:\pxmx\kv-t")
    assert not PARENT_SPELLING.search("the pxm parent")
    assert norm(PARENT_SPELLING.search(r"D:\PXM\x").group(0)) == "d:/pxm"
```

Run: `python -m pytest evals/multi-model-verify/test_artifact_roots.py -q`. Expected: the pin, the default-set, the two new `-Expect` tests, the sweep-can-fail addition and the parent-spelling test FAIL; everything else passes.

- [ ] **Step 2: The declaration**

In `skills/multi-model-verify/references/model-prompting-notes.md`, inside the region, replace the line
```
Canonical review mirror root: `<TEMP>/<short-name>/`
```
with
```
Canonical review mirror root: `C:/pxm/<short-name>/`
```
Below the region, replace the bullet
```
- Review mirror: never inside the reviewed repository.
  `tools/new-review-mirror.ps1` refuses a path equal to, inside, or
  containing the repo; `<TEMP>` is the controller host's temp
  directory, and references/preflight-mirror.md owns the short-name
  and path-budget rules.
```
with
```
- Review mirror: never inside the reviewed repository, and since
  2026-09-13 never under the controller host's temp directory either.
  `C:/pxm` is a FIXED parent, seven characters with its separator: the
  KitnEssentials review packets put their deepest file 243 characters
  below the repo root, so a mirror root has 15 characters at most, and
  the 36-character temp directory this row named before could never
  hold one, which is how 78 mirror directories came to sit at the
  drive root (backlog item 107). The row is a declaration, not a
  derivation: a machine whose system drive is not `C:` edits it. The
  guard accepts any depth below the parent and never the parent
  itself; the declared SHAPE is one segment, so build `C:\pxm\<tag>`.
  `tools/new-review-mirror.ps1` still refuses a path equal to, inside,
  or containing the repo and does not read this row; run
  `tools/artifact-roots.ps1 -RepoRoot <repo> -Assert <mirror-path> -Expect reviewMirror`
  before the build, and `tools/write-attestation.ps1` refuses to reap a
  tree that is not under the parent (references/preflight-mirror.md,
  End of life). references/preflight-mirror.md owns the short-name and
  path-budget rules.
```
[Corrected 2026-09-13 after the Fable whole-branch review: the command as first written omitted `-RepoRoot <repo>`, which the tool requires; the branch carries the corrected line and a pin on it.]

Then in the operating-rule list, replace the sentence
```
  ledger and mirror rows are not in the assert set, because the session
  never copies into them.
```
with
```
  ledger row is not in the assert set, because the session never copies
  into it; the mirror row is, so `-Expect reviewMirror` answers for a
  mirror path before the build and a copy aimed at the parent is refused.
```

- [ ] **Step 3: The resolver**

In `tools/artifact-roots.ps1`:

(a) In the header comment, change `a forbidden character in -DocsRoot, -Assert or the TEMP variable` to `a forbidden character in -DocsRoot or -Assert`.

(b) In `$expectMap`, add a fifth entry after `checkpoint`:
```powershell
    @{ Key = "reviewMirror"; Name = "review mirror root" }
```
and change the error text `-Expect must be one of rounds, frozenPlan, attestation, checkpoint: ` to `-Expect must be one of rounds, frozenPlan, attestation, checkpoint, reviewMirror: `.

(c) Delete the whole TEMP block, from the line `$tempRoot = $env:TEMP` through `$tempRoot = Resolve-Absolute $tempRoot` (nine lines including its comment), and in `Resolve-Row` delete the line `    $v = $v.Replace("<TEMP>", $tempRoot)`. The mirror row is now a rooted path, so `IsPathRooted` is true and `Resolve-Absolute` canonicalizes it like any other rooted value; no code path in `Resolve-Row` changes.

(d) In the `-Assert` block, replace the comment and list
```powershell
    # Rounds before the plan parent: the rounds root sits under it and
    # the more specific name is the useful answer.
    $retained = @(
        @{ Name = "rounds root";        Root = Strip-Placeholder $resolved.rounds },
        @{ Name = "frozen plan parent"; Root = Strip-Placeholder $resolved.frozenPlan },
        @{ Name = "attestation root";   Root = Strip-Placeholder $resolved.attestation },
        @{ Name = "checkpoint root";    Root = Strip-Placeholder $resolved.checkpoint }
    )
```
with
```powershell
    # Rounds before the plan parent: the rounds root sits under it and
    # the more specific name is the useful answer. The review mirror
    # parent is last: it is outside the repository, and it is in the set
    # so that -Expect reviewMirror answers for a mirror path before the
    # build (backlog item 107) and a retention copy aimed at it is
    # refused by name. The SDD ledger row stays out: nothing copies
    # into it.
    $retained = @(
        @{ Name = "rounds root";         Root = Strip-Placeholder $resolved.rounds },
        @{ Name = "frozen plan parent";  Root = Strip-Placeholder $resolved.frozenPlan },
        @{ Name = "attestation root";    Root = Strip-Placeholder $resolved.attestation },
        @{ Name = "checkpoint root";     Root = Strip-Placeholder $resolved.checkpoint },
        @{ Name = "review mirror root";  Root = Strip-Placeholder $resolved.reviewMirror }
    )
```

- [ ] **Step 4: Run the module under both hosts**

```powershell
$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals/multi-model-verify/test_artifact_roots.py -q
$env:PARALLAX_PS_HOST = "pwsh.exe"; python -m pytest evals/multi-model-verify/test_artifact_roots.py -q
python evals/tools/check_exact_line_oracles.py
python -m pytest evals/multi-model-verify/test_contract_coverage.py -q
```
Expected: all pass on both hosts (the writers group builds real mirrors and takes a minute); the coverage checker still finds the region whole inside its one pin. Also confirm `python -c "open('tools/artifact-roots.ps1','rb').read().decode('ascii')"` prints nothing and the file has no CRLF (`python -c "import sys; sys.exit(b'\r' in open('tools/artifact-roots.ps1','rb').read())"` exits 0).

- [ ] **Step 5: Commit**

```
git add skills/multi-model-verify/references/model-prompting-notes.md tools/artifact-roots.ps1 evals/multi-model-verify/test_artifact_roots.py
git commit -m "declare the review mirror parent as a fixed drive-rooted directory and let the roots tool answer for it"
```

---

### Task 2: The emitter's parent guard and the reaper tests

**Files:**
- Modify: `tools/write-attestation.ps1`
- Modify: `evals/multi-model-verify/test_mirror_reaper.py`

**Interfaces:**
- Produces: `Resolve-MirrorParent($repoRoot)` in `tools/write-attestation.ps1`, returning the declared parent as a forward-slash path with no trailing separator (`C:/pxm`) or printing `ERROR: the declared review mirror parent could not be read ...` and exiting 2. `Resolve-ReapPath` gains a seventh, LAST parameter `$mirrorParent`; a tree not under it is refused with `ERROR: <label> is not under the declared review mirror parent <parent> (<full>)`, exit 2, nothing written. Both `-ReapMirror` and `-ReapBridge` pass through it.
- Consumes: Task 1's `tools/artifact-roots.ps1 -RepoRoot <repo> -Json` (`reviewMirror` field).

- [ ] **Step 1: Write the failing tests**

In `evals/multi-model-verify/test_mirror_reaper.py`:

(a) Add `import stat` and `import uuid` to the imports. After the `read` helper, add:
```python
# The DECLARED review mirror parent (model-prompting-notes.md,
# round-artifact-roots, `Canonical review mirror root`). The emitter reaps
# nothing outside it, so every tree a success case names is built under
# a per-test directory here and removed afterwards. The literal is a pin:
# test_artifact_roots.py binds the resolver's answer to the row.
PARENT = Path(r"C:\pxm")


def _clear_readonly_and_retry(func, path, exc):
    os.chmod(path, stat.S_IWRITE)
    func(path)


@pytest.fixture
def pxm():
    """A fresh `C:\\pxm\\t-<8 hex>` for one test, removed on the way out
    whatever the test left behind (a held-handle case leaves its trees).
    Git's read-only object files are made writable as they are hit.
    Nothing else under the parent is ever touched."""
    d = PARENT / ("t-" + uuid.uuid4().hex[:8])
    d.mkdir(parents=True)
    yield d
    if d.exists():
        shutil.rmtree(d, onexc=_clear_readonly_and_retry)
```

(b) Move every tree a SUCCESS or EXIT-3 case names from `tmp_path` to the fixture, keeping the names. The tests, with their new signature and the changed lines only:

- `test_reaps_mirror_bridge_and_sidecar_after_writing(tmp_path, pxm)`: `bridge = make_bridge(repo, pxm / "kvs-t")`, `mirror = make_mirror(bridge, pxm / "kv-t")`, `sidecar = pxm / "kv-t.source-manifest"`; the junction target `target = tmp_path / "reference"` stays in `tmp_path`.
- `test_a_remediation_commit_above_the_head_is_still_the_mirror(tmp_path, pxm)`: `mirror = make_mirror(repo, pxm / "kv-t")` and `mirror2 = make_mirror(repo, pxm / "kv-u")`.
- `test_a_held_handle_leaves_the_attestation_and_exits_three(tmp_path, pxm)`: `mirror = make_mirror(repo, pxm / "kv-t")`, `bridge = make_bridge(repo, pxm / "kvs-t")`.
- `test_a_failed_record_write_reaps_nothing(tmp_path, pxm)`: `mirror = make_mirror(repo, pxm / "kv-t")`.
- `test_overlapping_mirror_and_bridge_are_refused(tmp_path, shape, pxm)`: `one = make_bridge(repo, pxm / "kvs-t")` and `mirror = make_mirror(repo, pxm / "kv-t")` (the nested bridge stays `mirror / "kvs-inner"`, which is under the parent too, so the overlap rule is what fires).
- `test_a_sidecar_failure_names_the_unattempted_bridge(tmp_path, pxm)`: `mirror`, `bridge` and `sidecar` under `pxm`.
- `test_the_record_lands_in_the_bracketed_repo_and_the_sibling_is_untouched(tmp_path, pxm)`: `mirror = make_mirror(repo, pxm / "kv-t")`; `sib` stays in `tmp_path`.
- `test_sidecar_success_is_read_back(tmp_path, pxm)`: `mirror` and `sidecar` under `pxm`.

`test_without_the_parameters_the_emitter_removes_nothing` keeps its `tmp_path` mirror: nothing is named, so nothing is checked. Every refusal test keeps its `tmp_path` tree: an earlier rule fires first and its message is what the test asserts, which is also what proves the parent guard runs LAST.

(c) In `test_every_wrong_tree_is_refused_before_the_record_is_written`, add `"outside-parent"` to the `shape` list and this branch before the `else`:
```python
    elif shape == "outside-parent":
        # Passes every earlier rule (a real mirror at the attested head)
        # and sits where the 78 directories of 2026-09-13 sat.
        path = make_mirror(repo, tmp_path / "kv-t")
```

(d) After `test_a_relative_reap_path_is_refused`, add a group:
```python
# ---------------------------------------------------------------------
# Group 7: the declared mirror parent (item 107, follow-up 2)
# ---------------------------------------------------------------------
def test_a_tree_outside_the_declared_parent_is_refused_for_mirror_and_bridge(tmp_path):
    # The LAST rule of the identity guard: a mirror and a bridge that
    # pass every other rule, built under the host temp directory as every
    # tree was until 2026-09-13, are refused by name with the record
    # unwritten. The message names the declared parent.
    repo, base, head = make_repo(tmp_path)
    mirror = make_mirror(repo, tmp_path / "kv-t")
    bridge = make_bridge(repo, tmp_path / "kvs-t")
    for kwargs, label in (({"mirror": mirror}, "the reap mirror"),
                          ({"bridge": bridge}, "the reap bridge")):
        proc = attest(repo, base, head, **kwargs)
        assert proc.returncode == 2, label + ": " + proc.stdout + proc.stderr
        assert ("ERROR: " + label + " is not under the declared review mirror parent C:/pxm (") in proc.stdout, proc.stdout
        assert not att_file(repo, head).exists()
    assert mirror.exists() and bridge.exists()


def test_the_parent_itself_is_never_a_reap_path():
    # Source pin: the comparison is StartsWith on the parent WITH its
    # separator, never Equals, so `C:\pxm` can never be named as a tree.
    body = read(WRITE)
    guard = body[body.index("function Resolve-ReapPath"):body.index("function Invoke-Reap")]
    assert '$parentSlash = $mirrorParent.TrimEnd("/") + "/"' in guard
    assert "$p.StartsWith($parentSlash, $cmp)" in guard
    assert "$p.Equals($parentSlash, $cmp)" in guard
    # And it is the LAST rule: the head comparison precedes it.
    assert guard.index("not the attested head") < guard.index("not under the declared review mirror parent")


def test_an_unreadable_parent_refuses_every_reap(tmp_path, pxm):
    # The emitter reads the parent through artifact-roots.ps1, the one
    # reader of the declaration. A copy of the three tools beside a
    # doctored notes file whose mirror row has no placeholder cannot
    # resolve a parent, and a parent that cannot be read accepts
    # NOTHING: exit 2, record unwritten, tree untouched - even for a tree
    # that sits under the real parent.
    fake = tmp_path / "plugin"
    (fake / "tools").mkdir(parents=True)
    notes_dir = fake / "skills" / "multi-model-verify" / "references"
    notes_dir.mkdir(parents=True)
    for name in ("write-attestation.ps1", "artifact-roots.ps1", "review-tree-removal.ps1"):
        shutil.copy(REPO / "tools" / name, fake / "tools" / name)
    notes = REPO / "skills" / "multi-model-verify" / "references" / "model-prompting-notes.md"
    doctored = read(notes).replace(
        "Canonical review mirror root: `C:/pxm/<short-name>/`\n",
        "Canonical review mirror root: `C:/pxm/`\n")
    assert doctored != read(notes)
    (notes_dir / "model-prompting-notes.md").write_text(doctored, encoding="utf-8")
    repo, base, head = make_repo(tmp_path)
    mirror = make_mirror(repo, pxm / "kv-t")
    proc = run_ps(fake / "tools" / "write-attestation.ps1",
                  "-RepoRoot", str(repo), "-BaseSha", base, "-HeadSha", head,
                  "-Verdict", "PASS", "-VerificationStatus", "FULL",
                  "-RouteNote", "effective route confirmed", "-Rounds", "1",
                  "-Participants", "session/reviewer", "-ReapMirror", str(mirror))
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "ERROR: the declared review mirror parent could not be read" in proc.stdout, proc.stdout
    assert not att_file(repo, head).exists()
    assert mirror.exists()
    # Without a reap parameter the same doctored copy never reads the
    # parent and writes the record as before.
    proc = run_ps(fake / "tools" / "write-attestation.ps1",
                  "-RepoRoot", str(repo), "-BaseSha", base, "-HeadSha", head,
                  "-Verdict", "PASS", "-VerificationStatus", "FULL",
                  "-RouteNote", "effective route confirmed", "-Rounds", "1",
                  "-Participants", "session/reviewer")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert att_file(repo, head).is_file()
```

Run: `python -m pytest evals/multi-model-verify/test_mirror_reaper.py -q`. Expected: the moved success cases still pass (nothing yet refuses a `pxm` tree), the `outside-parent` shape, the Group 7 refusal test, the source pin and the unreadable-parent test FAIL.

- [ ] **Step 2: The emitter**

In `tools/write-attestation.ps1`:

(a) In the header comment, after the sentence ending `shared with the mirror tool.`, add on new lines:
```
#
# PARENT (0.37.0, backlog item 107): both trees must also sit under the
# review mirror parent the round-artifact-roots declaration names,
# read here through tools/artifact-roots.ps1 rather than by a literal
# of this file's own, so that one edit to the row moves every reader.
# The rule is the LAST one in Resolve-ReapPath: every other refusal
# keeps its own message.
```

(b) After `Resolve-FullSha`, before `Resolve-ReapPath`, add:
```powershell
function Resolve-MirrorParent($repoRoot) {
    # The declared review mirror parent, read through the ONE reader of
    # the round-artifact-roots declaration, tools/artifact-roots.ps1,
    # invoked in-process so its exit reaches $LASTEXITCODE here (the
    # tool's documented $args fallback; measured 2026-09-13 on both
    # hosts). Every failure exits 2 with nothing written: a parent that
    # could not be read is never a parent that accepts everything.
    $tool = Join-Path $PSScriptRoot "artifact-roots.ps1"
    if (-not (Test-Path -LiteralPath $tool -PathType Leaf)) {
        Write-Output "ERROR: the declared review mirror parent could not be read: $tool is missing"
        exit 2
    }
    $lines = @()
    $why = ""
    try {
        $lines = @(& $tool -RepoRoot $repoRoot -Json 2>&1)
    } catch {
        $why = $_.Exception.Message
    }
    $toolExit = $LASTEXITCODE
    $text = (@($lines | ForEach-Object { [string]$_ }) -join "`n")
    if ($why) {
        Write-Output ("ERROR: the declared review mirror parent could not be read: " + $why)
        exit 2
    }
    if ($toolExit -ne 0) {
        Write-Output ("ERROR: the declared review mirror parent could not be read: artifact-roots.ps1 exited " + $toolExit + ": " + $text)
        exit 2
    }
    $row = ""
    try {
        $parsed = ConvertFrom-Json $text
        $row = [string]$parsed.reviewMirror
    } catch {
        $row = ""
    }
    if (-not $row) {
        Write-Output ("ERROR: the declared review mirror parent could not be read: no reviewMirror row in the tool's answer: " + $text)
        exit 2
    }
    $i = $row.IndexOf("<")
    if ($i -le 0) {
        Write-Output ("ERROR: the declared review mirror parent could not be read: the row has no per-debate placeholder (" + $row + ")")
        exit 2
    }
    $parent = $row.Substring(0, $i).Replace("\", "/").TrimEnd("/")
    if ((-not $parent) -or (-not [System.IO.Path]::IsPathRooted($parent))) {
        Write-Output ("ERROR: the declared review mirror parent could not be read: the row is not rooted (" + $row + ")")
        exit 2
    }
    return $parent
}
```

(c) Change the signature to
```powershell
function Resolve-ReapPath($label, $raw, $repoTop, $commonFull, $headFull, $allowRemediation, $mirrorParent) {
```
extend its opening comment's rule list: after `commit the mirror tool makes over a tracked back-channel.` add ` Last of all, under the declared review mirror parent (any depth, never the parent itself), for the mirror and the bridge alike.`

(d) Replace the tail of the function, from `    if ($treeHead -eq $headFull) {` to the closing `exit 2` of the "not the attested head" message, with:
```powershell
    $identityOk = ($treeHead -eq $headFull)
    if ((-not $identityOk) -and $allowRemediation) {
        $author = (& git --git-dir "$dotGit" log -1 --format=%ae HEAD 2>$null | Out-String).Trim()
        $authorExit = $LASTEXITCODE
        $parents = @(((& git --git-dir "$dotGit" rev-list --parents -n 1 HEAD 2>$null | Out-String).Trim()) -split "\s+")
        if (($authorExit -eq 0) -and ($LASTEXITCODE -eq 0) -and ($author -eq "parallax@local") -and
            ($parents.Count -eq 2) -and ($parents[1] -eq $headFull)) {
            $identityOk = $true
        }
    }
    if (-not $identityOk) {
        Write-Output ("ERROR: $label is at $treeHead, not the attested head $headFull" +
            " - it is not the tree this verdict was issued on ($full)")
        exit 2
    }
    # LAST: the declared parent. StartsWith on the parent WITH its
    # separator, so a sibling whose name merely begins with the parent's
    # (C:/pxmx) is outside, and never Equals, so the parent itself is
    # never a tree. $p already carries the trailing separator.
    $parentSlash = $mirrorParent.TrimEnd("/") + "/"
    if ($p.Equals($parentSlash, $cmp) -or -not $p.StartsWith($parentSlash, $cmp)) {
        Write-Output ("ERROR: $label is not under the declared review mirror parent " + $mirrorParent + " ($full)")
        exit 2
    }
    return $full
```
(`$p` and `$cmp` are the variables the overlap block above already defines.)

(e) In the REAP VALIDATION block, replace
```powershell
$reapMirrorFull = $null
$reapBridgeFull = $null
if ($ReapMirror) {
    $reapMirrorFull = Resolve-ReapPath "the reap mirror" $ReapMirror $toplevel $commonFull $headFull $true
}
if ($ReapBridge) {
    $reapBridgeFull = Resolve-ReapPath "the reap bridge" $ReapBridge $toplevel $commonFull $headFull $false
}
```
with
```powershell
$reapMirrorFull = $null
$reapBridgeFull = $null
$mirrorParent = $null
if ($ReapMirror -or $ReapBridge) {
    # Read once, and only when a tree is named: an emitter run without a
    # reap parameter never touches the declaration.
    $mirrorParent = Resolve-MirrorParent $RepoRoot
}
if ($ReapMirror) {
    $reapMirrorFull = Resolve-ReapPath "the reap mirror" $ReapMirror $toplevel $commonFull $headFull $true $mirrorParent
}
if ($ReapBridge) {
    $reapBridgeFull = Resolve-ReapPath "the reap bridge" $ReapBridge $toplevel $commonFull $headFull $false $mirrorParent
}
```

- [ ] **Step 3: Run the module under both hosts**

```powershell
$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals/multi-model-verify/test_mirror_reaper.py evals/multi-model-verify/test_attestation.py evals/multi-model-verify/test_artifact_roots.py -q
$env:PARALLAX_PS_HOST = "pwsh.exe"; python -m pytest evals/multi-model-verify/test_mirror_reaper.py evals/multi-model-verify/test_attestation.py evals/multi-model-verify/test_artifact_roots.py -q
```
Expected: all pass on both hosts. Then `Get-ChildItem C:\pxm` lists only `8904109a`, `k10392`, `k92104` (every `t-*` directory the fixture made is gone). ASCII and LF checks on `tools/write-attestation.ps1` as in Task 1 Step 4.

- [ ] **Step 4: Commit**

```
git add tools/write-attestation.ps1 evals/multi-model-verify/test_mirror_reaper.py
git commit -m "refuse to reap a review tree that is not under the declared mirror parent, read through the roots tool"
```

---

### Task 3: The doctor, the prose, and item 107

**Files:**
- Modify: `commands/doctor.md` (check 10)
- Modify: `skills/multi-model-verify/SKILL.md` (one sentence at preflight step 3)
- Modify: `skills/multi-model-verify/references/preflight-mirror.md` (the build location, End of life)
- Modify: `skills/multi-model-verify/references/backup-lane.md` (the workspace-isolation bullet)
- Modify: `evals/multi-model-verify/test_mirror_reaper.py` (Group 3 prose anchors)
- Modify: `BACKLOG.md` (item 107)

**Interfaces:**
- Consumes: Task 1's `-Expect reviewMirror`; Task 2's guard.

- [ ] **Step 1: Write the failing prose tests**

In `evals/multi-model-verify/test_mirror_reaper.py`, Group 3:

(a) In `test_preflight_mirror_reference_states_the_end_of_life_rule`, add to the anchor tuple after `"kv-<tag>-2"`:
```python
        "declared review mirror parent",
        "-Expect reviewMirror",
```
and add after the loop:
```python
    assert "directly under the temp directory" not in body
    assert r"C:\pxm\kv-<tag>" in body
```

(b) In `test_doctor_inventories_the_mirrors_and_never_deletes`, add to the anchor tuple after `"backlog item 106"`:
```python
        "artifact-roots.ps1",
        "reviewMirror",
        "legacy",
        "backlog item 107",
```
and after `assert "Remove-Item" not in section` add:
```python
    # The declared parent is the inventory; the drive-root name sweep is
    # the legacy line, and the text says which is which.
    assert section.index("reviewMirror") < section.index("legacy")
```

(c) After that test add:
```python
def test_skill_and_backup_lane_name_the_parent_not_the_temp_directory():
    for path in (SKILL, REPO / "skills" / "multi-model-verify" / "references" / "backup-lane.md"):
        body = read(path)
        assert "directly under the temp directory" not in body, path
        assert "declared review mirror parent" in body, path
```

Run: `python -m pytest evals/multi-model-verify/test_mirror_reaper.py -q -k "prose or preflight or doctor or skill_and"`. Expected: the three FAIL.

- [ ] **Step 2: The doctor**

In `commands/doctor.md`, replace the whole `## 10. Review mirror inventory` section (up to but not including any following `## ` heading or end of file) with:

```markdown
## 10. Review mirror inventory

Observation only: this check reports and never deletes, whatever it
finds. The place every review mirror and clone bridge is built is the
`Canonical review mirror root` row of model-prompting-notes.md's
round-artifact-roots declaration, read through its one reader: run
`<installPath>\tools\artifact-roots.ps1 -RepoRoot . -Json` from a git
working tree (the row is fixed, so any working tree serves; when the
current directory is not one, pass the checkout from check 1) and take
the `reviewMirror` value up to its `<short-name>` placeholder - today
that is `C:\pxm`. List every DIRECTORY directly under that parent.
Measure the count, the total size in GB (sum of file lengths, reparse
points NOT followed), and the oldest `LastWriteTime` among them. A
directory that cannot be measured is named as unmeasured and counted;
it never reads as empty. A parent that does not exist is OK with
`no review mirrors present`; a resolver that exits non-zero is BROKEN
with its `ERROR:` line, never an empty inventory.

- Nothing found: OK, `no review mirrors present`.
- Found, total under 5 GB AND oldest under 3 days: OK, reported as a
  NOTE with the three numbers.
- Total 5 GB or more, OR oldest 3 days or more: STALE, with the three
  numbers and this fix: a finished debate's mirror is removed by the
  attestation emitter, `write-attestation.ps1 -ReapMirror <mirror>
  [-ReapBridge <bridge>]`, which accepts only a tree under the declared
  parent, and one whose debate is over without an attestation is
  removed by hand; the rule and its measurement are backlog item 106,
  the parent is backlog item 107. Never name a directory as safe to
  delete: the doctor cannot tell which of them a live chat can still
  resume, and a `resume` against a deleted mirror is a transport
  failure.

The thresholds are the ones the 2026-09-13 measurement would have
tripped on day two: 13.4 GB across 78 directories accumulated in four
review days, about 3 GB per active day.

A second, legacy line, reported as a NOTE that never changes the
verdict: list every DIRECTORY whose name matches `kv*` sitting directly
under `$env:SystemDrive\` and directly under `$env:TEMP`, with the same
three numbers. Those are the two places mirrors were built before the
parent was declared (the temp directory was the canonical root, and a
session whose packets blew the path budget built at the drive root
instead). Eight `C:\kv-bl-*` and `C:\kvs-bl-*` directories other chats
own were still present on 2026-09-13; once this line finds nothing,
remove it from this check.
```
[Corrected 2026-09-13: the citation as first written lacked the `model-prompting-notes.md's` prefix that `evals/multi-model-verify/test_contract_coverage.py` requires for a region id on the command surface; the implementer added it and the ledger records the ruling.]

- [ ] **Step 3: The skill prose**

(a) `skills/multi-model-verify/SKILL.md`, preflight step 3: replace the one line
```
   at a SHORT `<scratch>` directly under the temp directory, never inside
```
with
```
   at a SHORT `<scratch>` directly under the declared review mirror parent, never inside
```
Then run `python evals/tools/skill_lint.py skills/multi-model-verify --strict` and confirm no ERROR line (the token line stays at or under 6500).

(b) `skills/multi-model-verify/references/preflight-mirror.md`: replace
```
Build at a SHORT `<scratch>` directly under the temp directory, such
as a `kv-<tag>` folder, never inside the session scratchpad: the
mirror re-roots every path, and the tool refuses before creating
anything when the budget is blown. That location is the
`Canonical review mirror root` row of references/model-prompting-notes.md's
round-artifact-roots declaration, fixed there because the tool refuses a
mirror inside the reviewed repository.
```
with
```
Build at a SHORT `<scratch>` directly under the declared review mirror parent,
such as `C:\pxm\kv-<tag>`, never under the temp directory and never
inside the session scratchpad: the mirror re-roots every path, and the
tool refuses before creating anything when the budget is blown. That
location is the `Canonical review mirror root` row of
references/model-prompting-notes.md's round-artifact-roots declaration,
fixed there because the tool refuses a mirror inside the reviewed
repository and because the KitnEssentials packets leave a mirror root
15 characters at most, which the temp directory could never hold. The
mirror tool does not read the row, so run
`tools/artifact-roots.ps1 -RepoRoot <repo> -Assert <scratch> -Expect reviewMirror`
first; exit 0 is the only clean answer, and a mirror built anywhere
else is refused at the reap and removed by hand.
```
In the End of life section, replace
```
A path is accepted only when it
exists as a directory not reached through a link, does not overlap the
reviewed repository or its git common dir, holds a `.git` DIRECTORY
(a `.git` FILE marks a linked worktree, never a mirror or a bridge), and
its HEAD is the attested head.
```
with
```
A path is accepted only when it
exists as a directory not reached through a link, does not overlap the
reviewed repository or its git common dir, holds a `.git` DIRECTORY
(a `.git` FILE marks a linked worktree, never a mirror or a bridge),
its HEAD is the attested head, and, last of all, it sits under the
declared review mirror parent, mirror and bridge alike, at any depth
below it and never the parent itself.
```
and replace
```
An existing `-MirrorPath` without `-Force` is refused with the reap
route named. Build `kv-<tag>-2` beside a finished debate's mirror and
```
with
```
An existing `-MirrorPath` without `-Force` is refused with the reap
route named. Build `C:\pxm\kv-<tag>-2` beside a finished debate's mirror and
```

(c) `skills/multi-model-verify/references/backup-lane.md`: replace
```
- Reviews run in a THROWAWAY REVIEW MIRROR — never the real tree. Build
  it at a SHORT path directly under the temp directory (the
  `Canonical review mirror root` row of model-prompting-notes.md's
  round-artifact-roots declaration), such as a
  `kv-<tag>` folder, and never inside the session scratchpad, whose own
  path is long enough to consume most of the budget before the copy
  starts.
```
with
```
- Reviews run in a THROWAWAY REVIEW MIRROR — never the real tree. Build
  it at a SHORT path directly under the declared review mirror parent (the
  `Canonical review mirror root` row of model-prompting-notes.md's
  round-artifact-roots declaration), such as
  `C:\pxm\kv-<tag>`, never under the temp directory and never inside
  the session scratchpad, whose own
  path is long enough to consume most of the budget before the copy
  starts.
```
(the sentences after `starts.` in that bullet are untouched).

- [ ] **Step 4: Item 107**

In `BACKLOG.md`, item 107:

(a) Change `Status: OPEN` to `Status: PARTIAL`.

(b) Replace follow-up 2's paragraph (from `2. The location.` through `the user picks the name.`) with:
```
2. The location. DECIDED 2026-09-13, shipped by the mirror-parent
   branch: the canonical review mirror root is `C:/pxm/<short-name>/`,
   a fixed drive-rooted parent the user chose, seven characters with
   its separator, so a mirror root fits the 15 characters the DT
   review packets leave. The four edits: the round-artifact-roots row
   and its pin; `tools/artifact-roots.ps1`, which no longer substitutes
   the temp directory and answers `-Assert <path> -Expect reviewMirror`;
   `tools/write-attestation.ps1`, whose `Resolve-ReapPath` refuses, as
   its LAST rule and for the bridge as well as the mirror, a tree that
   is not under the parent, reading the parent through the roots tool
   rather than a literal of its own; and doctor check 10, which
   inventories the parent as a directory and keeps the `kv*` drive-root
   sweep as a legacy line until the eight `C:\kv-bl-*` and `kvs-bl-*`
   directories are gone. The mirror tool itself does not enforce the
   parent; the session's `-Expect reviewMirror` check before the build
   and the emitter's guard at the reap are the two checks. The
   KitnEssentials memory that names `C:\kv-<tag>` is the consumer side
   and is updated after the release.
```

(c) Replace the closing paragraph
```
**What closing it means.** The bridge origin rule shipped with a test
that drives a foreign clone at the attested head and sees it refused,
and a decision recorded on the mirror parent, either a new declared
root with the four edits above or a stated reason to keep the drive
root.
```
with
```
**What remains.** Follow-up 1, the bridge origin rule, shipped with a
test that drives a foreign clone at the attested head and sees it
refused; and follow-up 3, a driving test for the two post-delete
sidecar read-back branches, or a recorded reason none can be built
without administrator rights. Follow-up 2 is closed above.
```

(d) Recompute the digest: `python evals/tools/backlog_lint.py --digests BACKLOG.md` prints one line per item; put item 107's new digest on its `Verified:` line as `Verified: 2026-09-13 <digest>`. Then `python evals/tools/backlog_lint.py` must exit 0.

- [ ] **Step 5: Run the checks**

```powershell
python evals/tools/skill_lint.py skills/multi-model-verify --strict
python evals/tools/skill_scanner.py skills
python evals/tools/backlog_lint.py
$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals/multi-model-verify/test_mirror_reaper.py evals/multi-model-verify/test_artifact_roots.py evals/multi-model-verify/test_contract_coverage.py -q
$env:PARALLAX_PS_HOST = "pwsh.exe"; python -m pytest evals/multi-model-verify/test_mirror_reaper.py -q
```
Expected: every command exits 0; no `ERROR` line from the skill lint; `test_every_parent_spelling_on_the_surface_is_the_declared_one` now sees at least three spellings and passes.

- [ ] **Step 6: Commit**

```
git add commands/doctor.md skills/multi-model-verify/SKILL.md skills/multi-model-verify/references/preflight-mirror.md skills/multi-model-verify/references/backup-lane.md evals/multi-model-verify/test_mirror_reaper.py BACKLOG.md
git commit -m "name the declared mirror parent in the doctor inventory and the skill prose, and record the item 107 decision"
```

---

## Not in this plan

- The version bump to 0.37.0 and the `CHANGELOG.md` section: they follow the diff debate, per `CLAUDE.md`'s dev loop.
- Follow-ups 1 and 3 of item 107, the plan-mode terminal event, and the KitnEssentials memory edit (consumer side, after the release).
- Deleting the eight `C:\kv-bl-*` / `kvs-bl-*` directories and the three pre-existing directories under `C:\pxm`.
- Making `tools/new-review-mirror.ps1` refuse a path outside the parent (decision 6).
