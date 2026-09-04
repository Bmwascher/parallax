"""Stop hook: a one-shot reminder that governed changes need a re-attested
backlog item (spec 3b). Blocks by exit 2 with the reason on stdout. Honours
stop_hook_active so it cannot loop; passes with a note when the baseline,
git, or the baseline commit is missing so a broken tool cannot wedge a
session.

"What this session changed" is approximated as the diff between the
baseline HEAD and the working tree. A pull, merge or rebase during the
session brings other people's governed changes into that diff, and they
are attributed to this session; the remedy is the same re-attestation,
and the approximation is stated here rather than hidden."""
import json
import sys

from _common import (BACKLOG, REPO_ROOT, backlog_sha256, baseline_path, git,
                     lint_working_tree, load_lint, read_payload)

REFUSAL = ("BACKLOG.md carries no re-attested item this session while governed "
           "surfaces changed; update the item that owns the work and refresh its "
           "Verified field")


def main():
    payload = read_payload()
    if payload.get("stop_hook_active"):
        return 0
    path = baseline_path(payload.get("session_id"))
    if not path.exists():
        print("backlog stop check: no baseline for this session (started before the "
              "hook existed); nothing checked")
        return 0
    baseline = json.loads(path.read_text(encoding="utf-8"))
    if git("rev-parse", "--verify", "--quiet", "HEAD") is None:
        print("backlog stop check: git unavailable; nothing checked")
        return 0
    head = baseline.get("head", "unknown")
    if head == "unknown" or git("cat-file", "-e", head + "^{commit}") is None:
        print("backlog stop check: baseline commit %s not found; nothing checked" % head)
        return 0
    lint = load_lint()
    # --no-renames: a governed file moved to an ungoverned path is otherwise
    # listed only at its destination, and the governed side goes unseen.
    tracked = git("diff", "--no-renames", "--name-only", head) or ""
    already = set(baseline.get("untracked_governed") or [])
    untracked = [p for p in (git("ls-files", "--others", "--exclude-standard")
                             or "").splitlines() if p and p not in already]
    changed = [p for p in tracked.splitlines() if p] + untracked
    governed = sorted({p for p in changed if lint.is_governed(p)})
    backlog_changed = backlog_sha256() != baseline.get("backlog_sha256")
    if governed:
        # Byte reads with strict UTF-8, like the lint's own modes: no
        # newline translation between the file and the parser.
        old_text = lint.read_at_revision(REPO_ROOT, head, lint.BACKLOG_PATH)
        new_text = lint.decode_utf8(BACKLOG.read_bytes()) if BACKLOG.exists() else None
        ids = lint.reattested_items(old_text, new_text)
        if not ids:
            detail = "governed paths changed: " + ", ".join(governed)
            print(REFUSAL)
            print(detail)
            print(REFUSAL, file=sys.stderr)
            print(detail, file=sys.stderr)
            return 2
        print("backlog stop check: governed paths changed; re-attested: " + ", ".join(ids))
    if backlog_changed:
        code, output = lint_working_tree(lint)
        if code != 0:
            print(output)
            print(output, file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
