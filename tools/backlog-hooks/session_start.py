"""SessionStart hook: record this session's baseline (spec 3a0)."""
import json
import sys

from _common import backlog_sha256, baseline_path, git, read_payload


def main():
    payload = read_payload()
    head = git("rev-parse", "HEAD")
    if head is None:
        head = "unknown"
        print("backlog baseline: git unavailable, head recorded as unknown")
    data = {"head": head.strip(), "backlog_sha256": backlog_sha256(),
            "cwd": payload.get("cwd", "")}
    baseline_path(payload.get("session_id")).write_text(json.dumps(data), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
