@echo off
REM A .cmd form of the stub app server.
REM
REM This exists because of a REAL failure, not for symmetry. Measured
REM 2026-08-11: `codex` on a machine with the npm install resolves to
REM codex.ps1, codex.cmd AND an extensionless codex, with no codex.exe at
REM all, and Process.Start with UseShellExecute=false can launch none of
REM them directly. The probe's first version special-cased only .ps1 and
REM worked here by luck; another session on the same machine hit the .cmd
REM and the probe failed three times before the cause was found.
REM
REM Driving the probe through THIS file is what proves the .cmd branch
REM launches at all.
powershell.exe -NoProfile -NonInteractive -File "%~dp0stub-appserver.ps1" %*
