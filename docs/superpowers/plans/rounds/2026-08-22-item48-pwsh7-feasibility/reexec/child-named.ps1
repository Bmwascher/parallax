param(
  [switch]$Register,
  [string]$RouteNote,
  [string]$Path
)
$enc = New-Object System.Text.UTF8Encoding($false)
$obj = @{
  register  = [bool]$Register
  routeNote = $RouteNote
  path      = $Path
}
[System.IO.File]::WriteAllText($env:PROBE_CHILD_OUT,
  ($obj | ConvertTo-Json -Compress -Depth 3), $enc)
