$ErrorActionPreference = 'Continue'

$dshCmd  = "D:\tools\dsh\resources\runtime\cli\bin\dsh.cmd"
$profile = "C:\Users\Administrator\.dsh\profiles\desktop"
$work    = "D:\Resources\DSH\_probe"
$goodDir = Join-Path $work "profile-good"
$logFile = Join-Path $work "install-log4.txt"

# npm-sourced first, then the GitHub-sourced one (may need a build-script approval).
$packages = @(
  'dsh-whale-widget',
  '@tt-a1i/archify-dsh',
  'github:haoranwang0921/dsh-session-cleaner'
)

function Get-AppAlive { return ((Get-Process -Name 'DeepSeek Harness' -ErrorAction SilentlyContinue) | Measure-Object).Count }
function Write-Log([string]$text) {
  $line = "[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss'), $text
  Write-Output $line
  Add-Content -Path $logFile -Value $line -Encoding utf8
}

# refresh the known-good snapshot from the current healthy profile
Copy-Item (Join-Path $profile 'package.json') (Join-Path $goodDir 'package.json') -Force
Copy-Item (Join-Path $profile 'cordis.patch.yml') (Join-Path $goodDir 'cordis.patch.yml') -Force
if (Test-Path (Join-Path $profile 'pnpm-lock.yaml')) { Copy-Item (Join-Path $profile 'pnpm-lock.yaml') (Join-Path $goodDir 'pnpm-lock.yaml') -Force }

Write-Log "START round-4 alive=$(Get-AppAlive)"

foreach ($pkg in $packages) {
  $safe = $pkg -replace '[@/:]', '_'
  Write-Log "INSTALL $pkg"
  $raw = & $dshCmd plugin --profile desktop add $pkg 2>&1 | Out-String
  $code = $LASTEXITCODE
  $raw | Set-Content -Path (Join-Path $work ("log4-$safe.txt")) -Encoding utf8
  Start-Sleep -Seconds 8
  $alive = Get-AppAlive

  if ($code -ne 0) {
    Write-Log "FAIL   $pkg exit=$code alive=$alive"
    $tail = ($raw -split "`n" | Where-Object { $_ -match 'dsh:|ERR_PNPM|allowBuilds|ignored build' } | Select-Object -First 6) -join ' | '
    Write-Log "       $tail"
    continue
  }

  if ($alive -lt 4) {
    Write-Log "CRASH  app died after $pkg - ROLLING BACK"
    Copy-Item (Join-Path $goodDir 'package.json') (Join-Path $profile 'package.json') -Force
    Copy-Item (Join-Path $goodDir 'cordis.patch.yml') (Join-Path $profile 'cordis.patch.yml') -Force
    Write-Log "STOP   rolled back"
    break
  }

  Write-Log "OK     $pkg exit=0 alive=$alive"
  Copy-Item (Join-Path $profile 'package.json') (Join-Path $goodDir 'package.json') -Force
  Copy-Item (Join-Path $profile 'cordis.patch.yml') (Join-Path $goodDir 'cordis.patch.yml') -Force
}

Write-Log "DONE alive=$(Get-AppAlive)"
Write-Log "--- dependencies ---"
$node = "D:\tools\dsh\resources\runtime\primary-runtime\dependencies\node\bin\node.exe"
Write-Log (& $node -e "const j=require('C:/Users/Administrator/.dsh/profiles/desktop/package.json'); console.log(Object.keys(j.dependencies).join(', '))")
Write-Log "--- bundles ---"
Write-Log (& $node -e "const j=require('C:/Users/Administrator/.dsh/profiles/desktop/package.json'); console.log(j.dsh.profile.bundles.join(', '))")
