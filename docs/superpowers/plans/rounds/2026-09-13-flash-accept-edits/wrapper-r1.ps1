$code = 1
$priorOutputEncoding = $OutputEncoding
try {
$OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$brief = [System.IO.File]::ReadAllText("C:\Temp\parallax-scratch\2026-09-13-flash-accept-edits\brief-astra-r1.md", (New-Object System.Text.UTF8Encoding($false, $true)))
$bytes = [System.IO.File]::ReadAllBytes("C:\Temp\parallax-scratch\2026-09-13-flash-accept-edits\override-r1.toml")
$seen = ([System.BitConverter]::ToString(([System.Security.Cryptography.SHA256]::Create()).ComputeHash($bytes)) -replace '-', '').ToLower()
if ($seen -cne "84d160071238a9f8a0ec350f9f2b938d8ba3bf0b3e7cfd20eb17cde827579bb1") { throw "the override file changed after the probe verified it" }
$override = (New-Object System.Text.UTF8Encoding($false, $true)).GetString($bytes)
$brief | codex exec --sandbox read-only --disable plugins --disable apps --disable memories -c mcp_servers.node_repl.enabled=false -c $override -m gpt-6-astra -c model_reasoning_effort=high --output-last-message $PSScriptRoot/reply - > $PSScriptRoot/transcript 2>&1
$code = $LASTEXITCODE
} catch { $code = 1 } finally { $OutputEncoding = $priorOutputEncoding }
[System.IO.File]::WriteAllText("$PSScriptRoot/exit", "$code")
exit $code