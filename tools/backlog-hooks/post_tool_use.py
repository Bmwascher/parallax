"""PostToolUse hook on Edit and Write: lint BACKLOG.md after a direct edit
(spec 3a). Reported, never blocked: the edit has already happened."""
import json
import os
import sys

from _common import load_lint, lint_working_tree, read_payload


def main():
    payload = read_payload()
    path = (payload.get("tool_input") or {}).get("file_path", "")
    if os.path.basename(path) != "BACKLOG.md":
        return 0
    lint = load_lint()
    code, output = lint_working_tree(lint)
    message = "backlog lint after edit (exit %d):\n%s" % (code, output)
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                             "additionalContext": message}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
