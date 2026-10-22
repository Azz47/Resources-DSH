$ErrorActionPreference = 'Continue'

$dshCmd  = "D:\tools\dsh\resources\runtime\cli\bin\dsh.cmd"
$profile = "C:\Users\Administrator\.dsh\profiles\desktop"
$work    = "D:\Resources\DSH\_probe"
$goodDir = Join-Path $work "profile-good"
New-Item -ItemType Directory -Force -Path $goodDir | Out-Null
$logFile = Join-Path $work "install-log.txt"

# Packages still to install (dsh-mindmap already installed as the canary).
$packages = @(
  'dsh-ppt-studio',
  'dsh-craft-your-textbook',
  'dsh-plugin-education',
  '@arcaneorion/dsh-teaching-board',
  'dsh-context',
  'dsh-better-sidebar',
  'dsh-hotspots',
  'dsh-image-generation',
  'dshmarket'
)

function Get-AppAlive {
  return ((Get-Process -Name 'DeepSeek Harness' -ErrorAction SilentlyContinue) | Measure-Object).Count
}

function Write-Log([string]$text) {
  $line = "[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss'), $text
  Write-Output $line
  Add-Content -Path $logFile -Value $line -Encoding utf8
}

# Seed the "known good" snapshot from the current, healthy profile.
Copy-Item (Join-Path $profile 'package.json') (Join-Path $goodDir 'package.json') -Force
Copy-Item (Join-Path $profile 'cordis.patch.yml') (Join-Path $goodDir 'cordis.patch.yml') -Force
if (Test-Path (Join-Path $profile 'pnpm-lock.yaml')) {
  Copy-Item (Join-Path $profile 'pnpm-lock.yaml') (Join-Path $goodDir 'pnpm-lock.yaml') -Force
}

Write-Log "START baseline process count = $(Get-AppAlive)"

foreach ($pkg in $packages) {
  Write-Log "INSTALL $pkg"
  $raw = & $dshCmd plugin --profile desktop add $pkg 2>&1 | Out-String
  $code = $LASTEXITCODE
  $raw | Set-Content -Path (Join-Path $work ("log-" + ($pkg -replace '[@/]', '_') + ".txt")) -Encoding utf8
  Start-Sleep -Seconds 6
  $alive = Get-AppAlive

  if ($code -ne 0) {
    Write-Log "FAIL   $pkg exit=$code alive=$alive  (see log-$($pkg -replace '[@/]','_').txt)"
    $tail = ($raw -split "`n" | Where-Object { $_ -match 'dsh:|ERR_|error|rejected|incompatible' } | Select-Object -First 6) -join ' | '
    Write-Log "       detail: $tail"
    # Profile files were restored by the manager on a failed run; continue to the next package.
    continue
  }

  if ($alive -lt 4) {
    Write-Log "CRASH  app died after $pkg (alive=$alive) - ROLLING BACK to last known good profile"
    Copy-Item (Join-Path $goodDir 'package.json') (Join-Path $profile 'package.json') -Force
    Copy-Item (Join-Path $goodDir 'cordis.patch.yml') (Join-Path $profile 'cordis.patch.yml') -Force
    if (Test-Path (Join-Path $goodDir 'pnpm-lock.yaml')) {
      Copy-Item (Join-Path $goodDir 'pnpm-lock.yaml') (Join-Path $profile 'pnpm-lock.yaml') -Force
    }
    Write-Log "STOP   rolled back; remaining packages not installed"
    break
  }

  $dep = (Get-Content (Join-Path $profile 'package.json') -Raw | ConvertFrom-Json).dependencies.PSObject.Properties.Name -contains $pkg
  $bun = (Get-Content (Join-Path $profile 'package.json') -Raw | ConvertFrom-Json).dsh.profile.bundles -contains $pkg
  Write-Log "OK     $pkg exit=0 alive=$alive dep=$dep bundle=$bun"

  Copy-Item (Join-Path $profile 'package.json') (Join-Path $goodDir 'package.json') -Force
  Copy-Item (Join-Path $profile 'cordis.patch.yml') (Join-Path $goodDir 'cordis.patch.yml') -Force
  if (Test-Path (Join-Path $profile 'pnpm-lock.yaml')) {
    Copy-Item (Join-Path $profile 'pnpm-lock.yaml') (Join-Path $goodDir 'pnpm-lock.yaml') -Force
  }
}

Copy-Item (Join-Path $profile 'package.json') (Join-Path $work 'final-package.json') -Force
Write-Log "DONE final process count = $(Get-AppAlive)"
