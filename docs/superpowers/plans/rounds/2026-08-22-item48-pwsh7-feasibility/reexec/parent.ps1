$enc = New-Object System.Text.UTF8Encoding($false)
$lines = @()
foreach ($a in $args) {
  $bytes = [System.Text.Encoding]::UTF8.GetBytes([string]$a)
  $lines += (($bytes | ForEach-Object { '{0:x2}' -f $_ }) -join '')
}
[System.IO.File]::WriteAllText($env:PROBE_PARENT_OUT, ($lines -join "`n"), $enc)

function Esc([string]$s) {
  $s = $s -replace '(\\*)"', '$1$1\"'
  $s = $s -replace '(\\+)$', '$1$1'
  return '"' + $s + '"'
}

if ($env:PROBE_FORM -eq 'splat') {
  & $env:PROBE_TARGET_HOST -NoProfile -ExecutionPolicy Bypass -File $env:PROBE_CHILD @args
} else {
  $cmd = '-NoProfile -ExecutionPolicy Bypass -File ' + (Esc $env:PROBE_CHILD)
  foreach ($a in $args) { $cmd = $cmd + ' ' + (Esc ([string]$a)) }
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = $env:PROBE_TARGET_HOST
  $psi.Arguments = $cmd
  $psi.UseShellExecute = $false
  $proc = [System.Diagnostics.Process]::Start($psi)
  $proc.WaitForExit()
}
