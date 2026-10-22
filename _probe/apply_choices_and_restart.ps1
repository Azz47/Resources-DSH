param(
  [string]$Profile = 'C:\Users\Administrator\.dsh\profiles\desktop',
  [string]$SafePackage = 'C:\Users\Administrator\.dsh\profiles\desktop\package.json.bak-20261021-231908-maxenable',
  [int]$WaitSeconds = 75
)
$ErrorActionPreference = 'Stop'
$exe = 'D:\tools\dsh\DeepSeek Harness.exe'
$pnpm = 'D:\tools\dsh\resources\runtime\primary-runtime\dependencies\pnpm\bin\pnpm.cjs'
$helper = 'D:\Resources\DSH\_probe\apply_choices.js'
$logDir = 'D:\Resources\DSH\_probe'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$log = Join-Path $logDir "apply_choices_restart_$stamp.log"
$backupDir = Join-Path $logDir "apply_choices_backup_$stamp"

function Log([string]$m) {
  $line = "[$(Get-Date -Format 'HH:mm:ss')] $m"
  Add-Content -LiteralPath $log -Value $line -Encoding UTF8
  Write-Host $line
}

function Stop-Dsh {
  $hosts = Get-CimInstance Win32_Process -Filter "Name='DeepSeek Harness.exe'" |
    Where-Object { $_.CommandLine -match 'desktop-host\\lib\\index.js' }
  $mainIds = @()
  foreach ($h in $hosts) { if ($h.ParentProcessId) { $mainIds += [int]$h.ParentProcessId } }
  $mainIds = $mainIds | Sort-Object -Unique
  foreach ($id in $mainIds) {
    Log "stop main pid $id"
    Stop-Process -Id $id -Force -ErrorAction SilentlyContinue
  }
  Get-Process -Name 'DeepSeek Harness' -ErrorAction SilentlyContinue |
    Stop-Process -Force -ErrorAction SilentlyContinue
  Start-Sleep -Seconds 3
  $left = Get-Process -Name 'DeepSeek Harness' -ErrorAction SilentlyContinue
  if ($left) {
    Log "force leftover app processes: $($left.Id -join ',')"
    $left | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
  }
  Get-CimInstance Win32_Process -Filter "Name='node.exe'" |
    Where-Object { $_.CommandLine -match 'profiles\\desktop\\node_modules\\billion-context' } |
    ForEach-Object {
      Log "stop leftover billion-context node $($_.ProcessId)"
      Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }
}

function Test-Boot([datetime]$start) {
  $deadline = (Get-Date).AddSeconds($WaitSeconds)
  $win = $null
  do {
    Start-Sleep -Seconds 2
    $win = Get-Process -Name 'DeepSeek Harness' -ErrorAction SilentlyContinue |
      Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
  } while (-not $win -and (Get-Date) -lt $deadline)
  if (-not $win) {
    Log "FAIL no main window after $WaitSeconds s"
    return $false
  }
  Log "main window pid $($win.Id)"
  $crashDir = 'C:\Users\Administrator\AppData\Roaming\@deepseek-ai\dsh-desktop\logs'
  $crashes = Get-ChildItem -LiteralPath $crashDir -Filter 'crash-*-web-boot.log' -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -gt $start }
  foreach ($c in $crashes) {
    $txt = Get-Content -LiteralPath $c.FullName -Raw -ErrorAction SilentlyContinue
    if ($txt -match 'invalid locale|Cannot find module|Failed to load plugin|ERR_PNPM') {
      $short = if ($txt.Length -gt 300) { $txt.Substring(0, 300) } else { $txt }
      Log "FAIL crash log $($c.Name): $short"
      return $false
    }
  }
  return $true
}

function Start-Dsh {
  $start = Get-Date
  Log 'start app'
  Start-Process -FilePath $exe -WorkingDirectory 'D:\tools\dsh'
  Start-Sleep -Seconds 3
  return (Test-Boot $start)
}

Log '=== apply plugin choices + restart ==='
Log "profile=$Profile"
if (-not (Test-Path -LiteralPath $SafePackage)) { Log "FAIL safe baseline missing: $SafePackage"; exit 3 }
if (-not (Test-Path -LiteralPath $helper)) { Log "FAIL helper missing: $helper"; exit 3 }
if (-not (Test-Path -LiteralPath $pnpm)) { Log "FAIL pnpm missing: $pnpm"; exit 3 }

New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
foreach ($f in @('package.json', 'pnpm-lock.yaml', 'pnpm-workspace.yaml', 'compatibility.json')) {
  $src = Join-Path $Profile $f
  if (Test-Path -LiteralPath $src) { Copy-Item -LiteralPath $src -Destination (Join-Path $backupDir $f) -Force }
}
Copy-Item -LiteralPath $SafePackage -Destination (Join-Path $backupDir 'safe-package.json') -Force
Log "backup=$backupDir"

Stop-Dsh

$applyOk = $true
try {
  & node $helper $Profile 2>&1 | ForEach-Object { Log "helper: $_" }
  if ($LASTEXITCODE -ne 0) { $applyOk = $false }
} catch {
  Log "helper exception: $($_.Exception.Message)"
  $applyOk = $false
}
if (-not $applyOk) {
  Log 'APPLY FAILED (helper) -> restore and start safe baseline'
  Copy-Item -LiteralPath $SafePackage -Destination (Join-Path $Profile 'package.json') -Force
  Copy-Item -LiteralPath (Join-Path $backupDir 'pnpm-lock.yaml') -Destination (Join-Path $Profile 'pnpm-lock.yaml') -Force
  Copy-Item -LiteralPath (Join-Path $backupDir 'pnpm-workspace.yaml') -Destination (Join-Path $Profile 'pnpm-workspace.yaml') -Force
  Copy-Item -LiteralPath (Join-Path $backupDir 'compatibility.json') -Destination (Join-Path $Profile 'compatibility.json') -Force
  Push-Location $Profile
  & node $pnpm install --fix-lockfile --ignore-scripts 2>&1 | ForEach-Object { Log "restore pnpm: $_" }
  Log "restore pnpm exit=$LASTEXITCODE"
  Pop-Location
  Start-Dsh | Out-Null
  Log "log=$log"
  exit 2
}

Push-Location $Profile
& node $pnpm remove dsh-free-search '@michengai/dsh-skills-manager' dsh-run2skill 2>&1 | ForEach-Object { Log "pnpm: $_" }
$removeExit = $LASTEXITCODE
Pop-Location
Log "pnpm remove exit=$removeExit"
if ($removeExit -ne 0) {
  Log 'APPLY FAILED (pnpm remove) -> restore and start safe baseline'
  Copy-Item -LiteralPath $SafePackage -Destination (Join-Path $Profile 'package.json') -Force
  Copy-Item -LiteralPath (Join-Path $backupDir 'pnpm-lock.yaml') -Destination (Join-Path $Profile 'pnpm-lock.yaml') -Force
  Copy-Item -LiteralPath (Join-Path $backupDir 'pnpm-workspace.yaml') -Destination (Join-Path $Profile 'pnpm-workspace.yaml') -Force
  Copy-Item -LiteralPath (Join-Path $backupDir 'compatibility.json') -Destination (Join-Path $Profile 'compatibility.json') -Force
  Push-Location $Profile
  & node $pnpm install --fix-lockfile --ignore-scripts 2>&1 | ForEach-Object { Log "restore pnpm: $_" }
  Log "restore pnpm exit=$LASTEXITCODE"
  Pop-Location
  Start-Dsh | Out-Null
  Log "log=$log"
  exit 2
}

$pkg = [IO.File]::ReadAllText((Join-Path $Profile 'package.json'), [Text.Encoding]::UTF8) | ConvertFrom-Json
$compat = [IO.File]::ReadAllText((Join-Path $Profile 'compatibility.json'), [Text.Encoding]::UTF8) | ConvertFrom-Json
Log "bundles=$($pkg.dsh.profile.bundles.Count) run2skill=$($pkg.dsh.profile.bundles -contains 'dsh-run2skill') free-search=$($null -ne $pkg.dependencies.'dsh-free-search') skills-manager=$($null -ne $pkg.dependencies.'@michengai/dsh-skills-manager')"
Log "teaching-exempt=$($compat.'@arcaneorion/dsh-teaching-board@0.6.0' -join ',')"

$ok = Start-Dsh
if (-not $ok) {
  Log 'BOOT FAILED -> restore pre-apply lockfile and 40-bundle safe baseline'
  Stop-Dsh
  Copy-Item -LiteralPath $SafePackage -Destination (Join-Path $Profile 'package.json') -Force
  Copy-Item -LiteralPath (Join-Path $backupDir 'pnpm-lock.yaml') -Destination (Join-Path $Profile 'pnpm-lock.yaml') -Force
  Copy-Item -LiteralPath (Join-Path $backupDir 'pnpm-workspace.yaml') -Destination (Join-Path $Profile 'pnpm-workspace.yaml') -Force
  Copy-Item -LiteralPath (Join-Path $backupDir 'compatibility.json') -Destination (Join-Path $Profile 'compatibility.json') -Force
  Push-Location $Profile
  & node $pnpm install --fix-lockfile --ignore-scripts 2>&1 | ForEach-Object { Log "rollback pnpm: $_" }
  Log "rollback pnpm exit=$LASTEXITCODE"
  Pop-Location
  $ok2 = Start-Dsh
  if ($ok2) { Log 'ROLLBACK_BOOT_OK' } else { Log 'ROLLBACK_BOOT_FAILED' }
  Log "log=$log"
  exit 2
}
Log 'APPLY_AND_BOOT_OK'
Log "log=$log"
exit 0
