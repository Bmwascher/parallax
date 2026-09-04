"""SessionStart hook: record this session's baseline (spec 3a0)."""
import json
import sys

from _common import (backlog_sha256, baseline_path, git, load_lint,
                     read_payload, untracked_governed)


def main():
    payload = read_payload()
    lint = load_lint()
    out = git("rev-parse", "HEAD")
    # The oracle rejects anything but exactly one nonempty line; a git that
    # printed two lines, or nothing, is recorded as unknown rather than read.
    head = lint.accept_exactly_one_nonempty_line(out) if out is not None else None
    if head is None:
        head = "unknown"
        print("backlog baseline: git unavailable, head recorded as unknown")
    data = {"head": head, "backlog_sha256": backlog_sha256(),
            "cwd": payload.get("cwd", ""),
            "untracked_governed": untracked_governed(lint)}
    baseline_path(payload.get("session_id")).write_text(json.dumps(data), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
