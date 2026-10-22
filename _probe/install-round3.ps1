$ErrorActionPreference = 'Continue'

$dshCmd  = "D:\tools\dsh\resources\runtime\cli\bin\dsh.cmd"
$profile = "C:\Users\Administrator\.dsh\profiles\desktop"
$work    = "D:\Resources\DSH\_probe"
$goodDir = Join-Path $work "profile-good"
$logFile = Join-Path $work "install-log3.txt"

$packages = @(
  'dsh-todo-board',
  'dsh-skill-mcp-manager',
  '@michengai/dsh-archive-manager',
  'dsh-whale-widget',
  '@tt-a1i/archify-dsh'
)

function Get-AppAlive { return ((Get-Process -Name 'DeepSeek Harness' -ErrorAction SilentlyContinue) | Measure-Object).Count }
function Write-Log([string]$text) {
  $line = "[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss'), $text
  Write-Output $line
  Add-Content -Path $logFile -Value $line -Encoding utf8
}

Write-Log "START round-3 alive=$(Get-AppAlive)"

foreach ($pkg in $packages) {
  Write-Log "INSTALL $pkg"
  $raw = & $dshCmd plugin --profile desktop add $pkg 2>&1 | Out-String
  $code = $LASTEXITCODE
  $raw | Set-Content -Path (Join-Path $work ("log3-" + ($pkg -replace '[@/]', '_') + ".txt")) -Encoding utf8
  Start-Sleep -Seconds 8
  $alive = Get-AppAlive

  if ($code -ne 0) {
    Write-Log "FAIL   $pkg exit=$code alive=$alive"
    $tail = ($raw -split "`n" | Where-Object { $_ -match 'dsh:' } | Select-Object -First 4) -join ' | '
    Write-Log "       $tail"
    continue
  }

  if ($alive -lt 4) {
    Write-Log "CRASH  app died after $pkg - ROLLING BACK"
    Copy-Item (Join-Path $goodDir 'package.json') (Join-Path $profile 'package.json') -Force
    Copy-Item (Join-Path $goodDir 'cordis.patch.yml') (Join-Path $profile 'cordis.patch.yml') -Force
    Write-Log "STOP   rolled back; remaining not installed"
    break
  }

  Write-Log "OK     $pkg exit=0 alive=$alive"
  Copy-Item (Join-Path $profile 'package.json') (Join-Path $goodDir 'package.json') -Force
  Copy-Item (Join-Path $profile 'cordis.patch.yml') (Join-Path $goodDir 'cordis.patch.yml') -Force
}

Write-Log "DONE alive=$(Get-AppAlive)"
Write-Log "--- bundles ---"
Write-Log (Get-Content (Join-Path $profile 'package.json') -Raw)
