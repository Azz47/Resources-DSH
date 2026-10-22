param(
  [string]$Profile = 'C:\Users\Administrator\.dsh\profiles\desktop',
  [string]$Package = '@nanmicoder/dsh-agent-teams',
  [string]$Version = '0.1.26',
  [int]$WaitSeconds = 75
)
$ErrorActionPreference = 'Stop'
$exe = 'D:\tools\dsh\DeepSeek Harness.exe'
$pnpm = 'D:\tools\dsh\resources\runtime\primary-runtime\dependencies\pnpm\bin\pnpm.cjs'
$logDir = 'D:\Resources\DSH\_probe'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$log = Join-Path $logDir "reinstall_agent_teams_$stamp.log"
$backupDir = Join-Path $logDir "reinstall_agent_teams_backup_$stamp"
$spec = "$Package@$Version"
$totalSteps = 8

function Log([string]$m) {
  $line = "[$(Get-Date -Format 'HH:mm:ss')] $m"
  Add-Content -LiteralPath $log -Value $line -Encoding UTF8
  Write-Host $line
}

function Read-Json([string]$path) {
  return ([IO.File]::ReadAllText($path, [Text.Encoding]::UTF8) | ConvertFrom-Json)
}

function Get-Bundles([string]$path) {
  $o = Read-Json $path
  return @($o.dsh.profile.bundles)
}

function Get-InstalledVersion([string]$name) {
  $p = Join-Path (Join-Path (Join-Path $Profile 'node_modules') $name) 'package.json'
  if (-not (Test-Path -LiteralPath $p)) { return $null }
  try { return (Read-Json $p).version } catch { return 'UNREADABLE' }
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
  $crashes = Get-ChildItem -LiteralPath $crashDir -Filter 'crash-*-*.log' -ErrorAction SilentlyContinue |
    Where-Object { $_.LastWriteTime -gt $start }
  foreach ($c in $crashes) {
    $txt = Get-Content -LiteralPath $c.FullName -Raw -ErrorAction SilentlyContinue
    if ($txt -match 'invalid locale|Cannot find module|Failed to load plugin|ERR_PNPM|agent-teams') {
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

Log '=== 1/8 reinstall @nanmicoder/dsh-agent-teams + restart ==='
Log "profile=$Profile spec=$spec"
Log "log=$log backupDir=$backupDir"
if (-not (Test-Path -LiteralPath $pnpm)) { Log 'FAIL pnpm missing'; exit 3 }
if (-not (Test-Path -LiteralPath (Join-Path $Profile 'package.json'))) { Log 'FAIL package.json missing'; exit 3 }

Log '=== 2/8 backup profile files + current bundle list ==='
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
foreach ($f in @('package.json', 'pnpm-lock.yaml', 'pnpm-workspace.yaml', 'compatibility.json')) {
  $src = Join-Path $Profile $f
  if (Test-Path -LiteralPath $src) { Copy-Item -LiteralPath $src -Destination (Join-Path $backupDir $f) -Force }
}
$bundlesBefore = Get-Bundles (Join-Path $profile 'package.json')
$bundlesBefore | Set-Content -LiteralPath (Join-Path $backupDir 'bundles-before.txt') -Encoding UTF8
Log "bundles before = $($bundlesBefore.Count); agent-teams in bundles = $($bundlesBefore -contains $Package)"
Log "installed before = $(Get-InstalledVersion $Package)"

Log '=== 3/8 stop running desktop app (holds the profile lock) ==='
Stop-Dsh

Log '=== 4/8 reinstall plugin via app CLI (version-matched, preflights peer compatibility) ==='
$cli = 'D:\tools\dsh\resources\runtime\cli\bin\dsh.cmd'
Push-Location $Profile
$out = & $cli plugin --profile desktop add $spec 2>&1
$addExit = $LASTEXITCODE
Pop-Location
$out | ForEach-Object { Log "add: $_" }
Log "add exit=$addExit"
if ($addExit -ne 0) {
  Log 'FAIL add failed -> restore backup and start app'
  foreach ($f in @('package.json', 'pnpm-lock.yaml', 'pnpm-workspace.yaml', 'compatibility.json')) {
    $b = Join-Path $backupDir $f
    if (Test-Path -LiteralPath $b) { Copy-Item -LiteralPath $b -Destination (Join-Path $Profile $f) -Force }
  }
  Start-Dsh | Out-Null
  Log 'REINSTALL_ABORTED'
  exit 2
}

Log '=== 5/8 verify install: dependency, bundle, files ==='
$pkgNow = Read-Json (Join-Path $Profile 'package.json')
$depSpec = $null
if ($pkgNow.dependencies.PSObject.Properties.Name -contains $Package) { $depSpec = $pkgNow.dependencies.$Package }
$bundlesAfter = @($pkgNow.dsh.profile.bundles)
$instAfter = Get-InstalledVersion $Package
$mainEntry = Join-Path (Join-Path (Join-Path $Profile 'node_modules') $Package) 'package.json'
Log "dep spec = $depSpec"
Log "bundles after = $($bundlesAfter.Count); agent-teams in bundles = $($bundlesAfter -contains $Package)"
Log "installed after = $instAfter"
Log "package.json present = $(Test-Path -LiteralPath $mainEntry)"

$installOk = ($depSpec -ne $null) -and ($bundlesAfter -contains $Package) -and ($instAfter -eq $Version)
if (-not $installOk) {
  Log 'FAIL verification: dependency/bundle/version mismatch -> restore backup and start app'
  foreach ($f in @('package.json', 'pnpm-lock.yaml', 'pnpm-workspace.yaml', 'compatibility.json')) {
    $b = Join-Path $backupDir $f
    if (Test-Path -LiteralPath $b) { Copy-Item -LiteralPath $b -Destination (Join-Path $Profile $f) -Force }
  }
  Push-Location $Profile
  & node $pnpm install --fix-lockfile --ignore-scripts 2>&1 | ForEach-Object { Log "restore pnpm: $_" }
  Log "restore pnpm exit=$LASTEXITCODE"
  Pop-Location
  Start-Dsh | Out-Null
  Log 'VERIFY_FAILED_RESTORED'
  exit 2
}
Log 'install verification OK'

Log '=== 6/8 start app and check boot ==='
$ok = Start-Dsh
if (-not $ok) {
  Log '=== 7/8 BOOT FAILED -> roll back to backup and start again ==='
  Stop-Dsh
  foreach ($f in @('package.json', 'pnpm-lock.yaml', 'pnpm-workspace.yaml', 'compatibility.json')) {
    $b = Join-Path $backupDir $f
    if (Test-Path -LiteralPath $b) { Copy-Item -LiteralPath $b -Destination (Join-Path $Profile $f) -Force }
  }
  Push-Location $Profile
  & node $pnpm install --fix-lockfile --ignore-scripts 2>&1 | ForEach-Object { Log "rollback pnpm: $_" }
  Log "rollback pnpm exit=$LASTEXITCODE"
  Pop-Location
  $ok2 = Start-Dsh
  if ($ok2) { Log 'ROLLBACK_BOOT_OK' } else { Log 'ROLLBACK_BOOT_FAILED' }
  Log "log=$log"
  exit 2
}

Log '=== 8/8 final state ==='
$finalPkg = Read-Json (Join-Path $Profile 'package.json')
$finalBundles = @($finalPkg.dsh.profile.bundles)
Log "final bundles = $($finalBundles.Count) (before $($bundlesBefore.Count))"
Log "final installed = $(Get-InstalledVersion $Package)"
Log 'REINSTALL_AND_BOOT_OK'
Log "log=$log"
exit 0
