param(
  [string]$Profile = 'C:\Users\Administrator\.dsh\profiles\desktop',
  [string]$SafePackage = 'C:\Users\Administrator\.dsh\profiles\desktop\package.json.bak-20261021-231908-maxenable',
  [int]$WaitSeconds = 60
)
$ErrorActionPreference = 'Stop'
$exe = 'D:\tools\dsh\DeepSeek Harness.exe'
$logDir = 'D:\Resources\DSH\_probe'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$log = Join-Path $logDir "restart_maxenable_$stamp.log"

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
  $patch = Join-Path $Profile 'cordis.patch.yml'
  if (Test-Path -LiteralPath $patch) {
    $pt = Get-Content -LiteralPath $patch -Raw -ErrorAction SilentlyContinue
    if ($pt -match 'dsh-fix') { Log 'WARN cordis.patch.yml still contains dsh-fix' }
  }
  return $true
}

Log '=== restart desktop maxenable ==='
Log "profile=$Profile"
if (-not (Test-Path -LiteralPath $SafePackage)) {
  Log "FAIL safe baseline missing: $SafePackage"
  exit 3
}
Copy-Item -LiteralPath (Join-Path $Profile 'package.json') `
  -Destination (Join-Path $Profile "package.json.bak-$stamp-runtime") -Force
Log "runtime backup package.json.bak-$stamp-runtime"

Stop-Dsh
$start = Get-Date
Log 'start app'
Start-Process -FilePath $exe -WorkingDirectory 'D:\tools\dsh'
Start-Sleep -Seconds 3
$ok = Test-Boot $start
if (-not $ok) {
  Log 'BOOT FAILED -> restore 40-bundle baseline'
  Stop-Dsh
  Copy-Item -LiteralPath $SafePackage -Destination (Join-Path $Profile 'package.json') -Force
  Log "restored $SafePackage"
  $start2 = Get-Date
  Start-Process -FilePath $exe -WorkingDirectory 'D:\tools\dsh'
  Start-Sleep -Seconds 3
  $ok2 = Test-Boot $start2
  if ($ok2) { Log 'ROLLBACK_BOOT_OK' } else { Log 'ROLLBACK_BOOT_FAILED' }
  Log "log=$log"
  exit 2
}
Log 'BOOT_OK'
Log "log=$log"
exit 0
