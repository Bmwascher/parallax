AGREE WITH CHANGES

**A.** Avoiding repeated reference copies is reasonable, but make this an explicit external-reference feature, not a blanket `/XJ` change. Bind the mirror-relative link path, resolved target, reference HEAD, and content-sensitive fingerprint. Capture these during construction and pass the frozen expectations into the shared pre/post verification arguments in [dispatch-round.ps1:274](/C:/Users/Brandon/Documents/parallax/tools/dispatch-round.ps1:274). Revalidate the link itself: hashing the original target would miss a mirror junction redirected elsewhere.

**B. The proposal misses several material details:**

- **Git distinguishes junctions from symlinks.** Git for Windows classifies directory junctions as directories and actual symbolic links as links. `core.symlinks=false` controls checkout representation—tracked symlinks become small text files; it does not make junctions opaque. Establish the actual link type and Git enumeration before claiming savings. [Git implementation](https://raw.githubusercontent.com/git-for-windows/git/main/compat/mingw.c), [configuration documentation](https://git-scm.com/docs/git-config#Documentation/git-config.txt-coresymlinks).

- **The secondary performance claim identifies the wrong helper.** `ls-files --cached --others` belongs to back-channel discovery, not `Get-StatusSha256`. Each identity verification runs `status --porcelain --ignored -uall -z` and hashes the resulting manifest. Excluding a link from robocopy changes neither source-side operation. A recreated junction can also retain mirror-side traversal costs.

- **Existing coverage is content-sensitive but conditional.** [Get-ContentManifest:470](/C:/Users/Brandon/Documents/parallax/tools/new-review-mirror.ps1:470) recursively expands directory subjects and hashes file bytes. Materialized reference files named by the parent status therefore receive coverage, including a nested checkout reported as a directory. After relinking, coverage depends on Git’s emitted subjects and PowerShell traversal; it cannot simply be presumed absent or preserved. A clean tracked symlink may expose no target content to the fingerprint. Measure both hosts.

- **“Status hash” must include content.** Hashing porcelain text alone misses edits to already-dirty, ignored, or untracked files. Reuse the content-sensitive algorithm or a stronger explicit manifest. HEAD plus that algorithm still inherits the documented clean-filter blind spot at lines 599–614. Neither the existing gate nor the proposal detects changes reverted before the post-check; dispatch explicitly acknowledges this.

- **Remediation can write through the link.** [Line 1194](/C:/Users/Brandon/Documents/parallax/tools/new-review-mirror.ps1:1194) deletes discovered back-channels. Recreating a junction beforehand could delete reference-checkout `AGENTS.md` files; adding it afterward could bypass sanitization. External references need their own validated instruction-channel policy, and cleanup must safely unlink them.

- **Read-only is not confinement to cwd.** Ordinary Codex read-only execution can read external targets subject to filesystem permissions and effective read restrictions. A junction supplies a convenient path, not additional permission. Probe an actual reference read under the deployed reviewer configuration. [OpenAI permissions](https://learn.chatgpt.com/docs/permissions).

- **Keep cycle safeguards.** The current walk rejects ancestor links and repeated targets conservatively, resolves relative targets against the link’s parent, and rejects a reparse-point repo root. Skipping copy traversal does not remove cycles from hashing or reviewer traversal. Match the path-budget universe to the revised copy operation.

**C.** A safer option is a reusable, sanitized reference snapshot keyed by content identity, with each mirror linking to that snapshot. This amortizes copying without exposing the mutable checkout to remediation. Retain source-reference verification if upstream drift must invalidate rounds.

For genuinely small, known input sets, existing `-ExtraInput` is cheaper: it copies **files only**, flattens names, rejects collisions, and covers copied bytes. It neither accepts a reference directory nor rechecks the external originals afterward.

**D.** [test_a_source_directory_link_is_followed_not_refused](/C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_review_mirror.py:1343) intends to pin materialization. However, its `is_symlink()` assertion can miss Windows junctions, so recreation may stay green. Updating the declared contract would make [test_mirror_path_budget_region](/C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_backup_lane.py:1869) red until updated. Ancestor-cycle and repeated-target tests also pin existing refusals.

Read-only review; no files changed or tests run.