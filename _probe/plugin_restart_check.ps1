<#
  Is the running DSH app older than the plugins on disk?

  The desktop build never restarts itself when a plugin changes
  (dshmarket's client reports allowRestart: false and only shows a
  "N 项变更需重启 DeepSeek Harness 后生效" banner), so an updated plugin can
  sit on disk while the renderer keeps the previous bundle in memory.
  That mismatch is what breaks the page.

  Usage: powershell -ExecutionPolicy Bypass -File _probe\plugin_restart_check.ps1
  Exit 0 = running build is current, 2 = restart needed.
#>
param(
  [string]$Profile = "C:\Users\Administrator\.dsh\profiles\desktop",
  [string]$ProcessName = "DeepSeek Harness"
)
$ErrorActionPreference = "Stop"

$nm = Join-Path $Profile "node_modules"
$modules = Join-Path $nm ".modules.yaml"

$procs = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue | Sort-Object StartTime
if (-not $procs) { Write-Output "no '$ProcessName' process found - nothing to compare"; exit 0 }
$appStart = ($procs | Select-Object -First 1).StartTime
Write-Output ("app started      : " + $appStart)
Write-Output ("processes        : " + $procs.Count + "  (oldest listed above = main)")

$installTime = $null
if (Test-Path $modules) { $installTime = (Get-Item $modules).LastWriteTime; Write-Output ("last pnpm install: " + $installTime) }

$changed = @()
$deps = @()
$pkg = Get-Content (Join-Path $Profile "package.json") -Raw | ConvertFrom-Json
$deps = $pkg.dependencies.PSObject.Properties.Name
foreach ($d in $deps) {
  $pj = Join-Path (Join-Path $nm $d) "package.json"
  if (Test-Path $pj) {
    $t = (Get-Item $pj).LastWriteTime
    if ($t -gt $appStart) { $changed += [pscustomobject]@{ Pkg = $d; Changed = $t } }
  }
}

Write-Output ("deps checked     : " + $deps.Count)
if ($changed.Count -eq 0) {
  Write-Output "verdict          : OK - every plugin on disk predates the running app."
  exit 0
}

Write-Output ("plugins newer than the running app: " + $changed.Count)
$changed | Sort-Object Changed -Descending | ForEach-Object { Write-Output ("   " + $_.Changed + "  " + $_.Pkg) }
Write-Output "verdict          : RESTART NEEDED - fully quit and relaunch DSH, or the page can crash/white-screen."
exit 2
