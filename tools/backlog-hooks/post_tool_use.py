"""PostToolUse hook on Edit and Write: lint BACKLOG.md after a direct edit
(spec 3a). Reported, never blocked: the edit has already happened. With
git unavailable it reports a note instead of a lint whose rule 10 would
call every commit-bound Record unresolved (spec, Error handling)."""
import json
import os
import sys

from _common import git, load_lint, lint_working_tree, read_payload


def report(message):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                             "additionalContext": message}}))


def main():
    payload = read_payload()
    path = (payload.get("tool_input") or {}).get("file_path", "")
    if os.path.basename(path) != "BACKLOG.md":
        return 0
    if git("rev-parse", "--verify", "--quiet", "HEAD") is None:
        report("backlog lint after edit: git unavailable; nothing checked")
        return 0
    lint = load_lint()
    code, output = lint_working_tree(lint)
    report("backlog lint after edit (exit %d):\n%s" % (code, output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
