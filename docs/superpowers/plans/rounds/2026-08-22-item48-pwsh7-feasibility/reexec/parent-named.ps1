param(
  [switch]$Register,
  [string]$RouteNote,
  [string]$Path
)
$enc = New-Object System.Text.UTF8Encoding($false)
$mine = @{
  register  = [bool]$Register
  routeNote = $RouteNote
  path      = $Path
}
[System.IO.File]::WriteAllText($env:PROBE_PARENT_OUT,
  ($mine | ConvertTo-Json -Compress -Depth 3), $enc)

$forward = @()
if ($Register) { $forward += '-Register' }
$forward += '-RouteNote'; $forward += $RouteNote
$forward += '-Path';      $forward += $Path

function Esc([string]$s) {
  $s = $s -replace '(\\*)"', '$1$1\"'
  $s = $s -replace '(\\+)$', '$1$1'
  return '"' + $s + '"'
}

if ($env:PROBE_FORM -eq 'splat') {
  & $env:PROBE_TARGET_HOST -NoProfile -ExecutionPolicy Bypass -File $env:PROBE_CHILD @forward
} else {
  $cmd = '-NoProfile -ExecutionPolicy Bypass -File ' + (Esc $env:PROBE_CHILD)
  foreach ($a in $forward) { $cmd = $cmd + ' ' + (Esc ([string]$a)) }
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = $env:PROBE_TARGET_HOST
  $psi.Arguments = $cmd
  $psi.UseShellExecute = $false
  $proc = [System.Diagnostics.Process]::Start($psi)
  $proc.WaitForExit()
}
