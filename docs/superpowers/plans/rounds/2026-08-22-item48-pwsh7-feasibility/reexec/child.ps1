$enc = New-Object System.Text.UTF8Encoding($false)
$lines = @()
foreach ($a in $args) {
  $bytes = [System.Text.Encoding]::UTF8.GetBytes([string]$a)
  $lines += (($bytes | ForEach-Object { '{0:x2}' -f $_ }) -join '')
}
[System.IO.File]::WriteAllText($env:PROBE_CHILD_OUT, ($lines -join "`n"), $enc)
