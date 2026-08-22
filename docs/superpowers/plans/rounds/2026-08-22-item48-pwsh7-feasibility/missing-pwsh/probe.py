#!/usr/bin/env python3
"""What does a caller see when `pwsh` cannot be resolved?

The hook is invoked as a bare `pwsh`, so its failure mode when PowerShell 7
is absent is decided by PATH resolution. This runs the hook's OWN
invocation shape with a PATH stripped of every directory containing pwsh,
and captures what that call produced. Nothing is modified: the real PATH is
untouched outside this child process.

What this captures is what THIS caller saw. Claude Code's hook runner may
present a failure differently, and that presentation was not measured here.
"""
import json
import os
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent


def stripped_path():
    keep = []
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        if not entry:
            continue
        candidate = Path(entry) / "pwsh.exe"
        if candidate.exists():
            continue
        keep.append(entry)
    return os.pathsep.join(keep)


def main():
    env = dict(os.environ)
    env["PATH"] = stripped_path()
    still_there = shutil.which("pwsh", path=env["PATH"])
    result = {
        "pwsh_on_real_path": shutil.which("pwsh"),
        "pwsh_after_stripping": still_there,
    }
    if still_there is not None:
        # STOP HERE. The strip failed, so whatever the invocation below
        # produced would describe a machine that still has PowerShell 7.
        # The task text says to stop and say so; without this the program
        # ran on and could still exit 0, leaving the instruction as the
        # only thing standing between a failed setup and a clean-looking
        # result.
        result["outcome"] = ("the PATH strip did not remove pwsh; nothing "
                             "about a machine without it was measured")
        (HERE / "results.json").write_text(json.dumps(result, indent=1),
                                           encoding="utf-8")
        print(json.dumps(result, indent=1))
        return 1
    # The SHIPPED shape, not a convenient one. hooks/hooks.json:10 invokes
    # `pwsh -NoProfile -NonInteractive -File <script>`; a `-Command
    # Write-Output ok` call would measure a different caller path and then
    # be written up as what the hook shows a user.
    hook_script = str(HERE.parents[5] / "hooks"
                      / "superpowers-review-companion.ps1")
    result["invocation"] = ["pwsh", "-NoProfile", "-NonInteractive",
                            "-File", hook_script]
    # stdin MUST be closed and there MUST be a timeout. The hook's first
    # act is [Console]::In.ReadToEnd() (hooks/superpowers-review-companion.ps1:13).
    # With inherited stdin and no timeout, the SUCCESS path - the one this
    # probe pre-names as a finding - launches the real hook and blocks
    # forever, and no oracle fires. The convenient `-Command Write-Output ok`
    # this replaced could not hang; the faithful shape can.
    try:
        proc = subprocess.run(
            result["invocation"],
            capture_output=True, text=True, env=env, shell=False,
            stdin=subprocess.DEVNULL, timeout=60)
    except subprocess.TimeoutExpired:
        result["outcome"] = "timed out after 60s"
        result["returncode"] = None
        result["stdout"] = ""
        result["stderr"] = ""
        (HERE / "results.json").write_text(json.dumps(result, indent=1),
                                           encoding="utf-8")
        print(json.dumps(result, indent=1))
        # EXIT NONZERO. The task calls a timeout a probe defect that must
        # be fixed; a bare return here would exit 0 over it, which is a
        # command that cannot fail on the one path it was added to catch.
        return 1
    result["returncode"] = proc.returncode
    result["stdout"] = proc.stdout.strip()
    result["stderr"] = proc.stderr.strip()
    (HERE / "results.json").write_text(json.dumps(result, indent=1),
                                       encoding="utf-8")
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
