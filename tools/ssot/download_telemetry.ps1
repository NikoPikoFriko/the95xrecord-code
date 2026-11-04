# download_telemetry.ps1 — bind a downloaded file to its JIMS URL, time and hash using Windows evidence
# Usage: pwsh -File download_telemetry.ps1 -Path "C:\Users\NIKO\Downloads\1234567890.pdf" [-Docket 413] [-Case 1RC191003776]
param(
  [Parameter(Mandatory)][string]$Path,
  [string]$Docket = "",
  [string]$Case = "1RC191003776",
  [string]$OutDir = "D:\PROJECT_CENTER\temp\download-telemetry"
)
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
if (-not (Test-Path $Path)) { throw "file not found: $Path" }
$f = Get-Item $Path

# 1) bytes + hashes
$sha = (Get-FileHash $Path -Algorithm SHA256).Hash.ToLower()
$md5 = (Get-FileHash $Path -Algorithm MD5).Hash.ToLower()

# 2) Zone.Identifier ADS (source URL Chrome records)
$zone = $null; $zoneRaw = $null
try {
  $zoneRaw = Get-Content -Path $Path -Stream Zone.Identifier -ErrorAction Stop
  $zone = ($zoneRaw | Where-Object { $_ -match '^ZoneId=|^ReferrerUrl=|^HostUrl=' }) -join '; '
} catch { $zone = 'none' }

# 3) Chrome download history (copy the live DB first — it is locked while Chrome runs)
$chromeRow = $null
$hist = Join-Path $env:LOCALAPPDATA 'Google\Chrome\User Data\Default\History'
if (Test-Path $hist) {
  $tmp = Join-Path $OutDir ("History-" + [guid]::NewGuid().ToString('N') + ".sqlite")
  try {
    Copy-Item $hist $tmp -Force
    $queries = @(
      "select target_path, start_time, url, referrer, received_bytes, state, mime_type from downloads where target_path like '%$($f.Name)%' order by start_time desc limit 1"
    )
    foreach ($q in $queries) {
      $row = & sqlite3 $tmp $q 2>$null
      if ($row) { $chromeRow = $row; break }
    }
  } catch { $chromeRow = "history unreadable: $($_.Exception.Message)" }
  finally { if (Test-Path $tmp) { Remove-Item $tmp -Force } }
}
if (-not $chromeRow) { $chromeRow = 'no matching downloads row (profile other than Default, or history cleared)' }

# 4) USN journal (best effort; needs admin, tolerated failure)
$usn = $null
try {
  $usn = (& fsutil usn readjournal C: 2>$null | Select-String -SimpleMatch $f.Name | Select-Object -First 1)
  if (-not $usn) { $usn = 'no usn match' }
} catch { $usn = 'usn unavailable' }

$rec = [ordered]@{
  recorded_at   = (Get-Date).ToString('o')
  case          = $Case
  docket        = $Docket
  file_name     = $f.Name
  file_path     = $f.FullName
  bytes         = $f.Length
  sha256        = $sha
  md5           = $md5
  created       = $f.CreationTime.ToString('o')
  modified      = $f.LastWriteTime.ToString('o')
  zone_id       = $zone
  zone_raw      = ($zoneRaw -join ' | ')
  chrome_row    = "$chromeRow"
  usn_row       = "$usn"
  source_host   = if ($zone -match 'jimspss1\.courts\.state\.hi\.us') { 'jimspss1.courts.state.hi.us' } else { 'unverified-from-zone' }
}
$line = ($rec | ConvertTo-Json -Compress)
Add-Content -Path (Join-Path $OutDir 'TELEMETRY.jsonl') -Value $line -Encoding UTF8
Write-Output $line
