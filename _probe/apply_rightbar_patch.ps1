<#
  Re-apply the "right-bar default width" patch to the DSH app.asar.

  Why this exists: the DSH desktop update replaces app.asar and silently restores the
  stock 45%-of-viewport right panel. Run this again after every app update.

  Usage (report only):  powershell -ExecutionPolicy Bypass -File _probe\apply_rightbar_patch.ps1
  Usage (write):        powershell -ExecutionPolicy Bypass -File _probe\apply_rightbar_patch.ps1 -Apply

  Flow: extract-and-detect (idempotent) -> backup -> dry-run -> apply -> archive-wide verify.
#>
param(
  [string]$Asar = "D:\tools\dsh\resources\app.asar",
  [string]$InnerPath = "dsh/node_modules/@deepseek-ai/dsh-client-ui-layout/lib/client.js",
  [switch]$Apply
)
$ErrorActionPreference = "Stop"
$probe = $PSScriptRoot
$editsFile = Join-Path $probe "rightbar-default-width.json"
$patchTool = Join-Path $probe "asar_patch.js"
$probeTool = Join-Path $probe "asar_probe.js"
$verifyTool = Join-Path $probe "asar_verify_all.js"
$backupDir = "D:\Resources\DSH\_backup"

foreach ($f in @($Asar, $editsFile, $patchTool, $probeTool, $verifyTool)) {
  if (-not (Test-Path $f)) { throw "missing required path: $f" }
}

# --- 1. is it already patched? (extract the one file and look for the new constant)
$tmp = Join-Path $env:TEMP "dsh-rightbar-check"
if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
& node $probeTool extract $Asar "dsh-client-ui-layout/lib/client.js" $tmp | Out-Null
$innerName = "client.js"
$extracted = Get-ChildItem $tmp -Recurse -File -Filter $innerName | Select-Object -First 1
if (-not $extracted) { throw "extraction produced no $innerName" }
$alreadyPatched = Select-String -Path $extracted.FullName -Pattern "RIGHTBAR_DEFAULT_RATIO = .25" -SimpleMatch -Quiet
$stillStock = Select-String -Path $extracted.FullName -Pattern "RIGHTBAR_DEFAULT_RATIO = .45" -SimpleMatch -Quiet
Write-Output ("already patched : " + $alreadyPatched)
Write-Output ("stock .45 ratio : " + $stillStock)
if ($alreadyPatched -and -not $stillStock) {
  Write-Output "nothing to do - the archive already carries the 25% / 320-360px default."
  exit 0
}

# --- 2. backup
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backup = Join-Path $backupDir ("app.asar.bak-before-rightbar-" + $stamp)
Copy-Item $Asar $backup
Write-Output ("backup          : " + $backup + "  (" + (Get-Item $backup).Length + " bytes)")
Write-Output ("backup sha256   : " + (Get-FileHash $backup -Algorithm SHA256).Hash)

# --- 3. dry run
Write-Output "--- dry run ---"
$dry = & node $patchTool $Asar $InnerPath $editsFile 2>&1
$dry | ForEach-Object { Write-Output $_ }
if ($LASTEXITCODE -ne 0) { throw "dry run failed (exit $LASTEXITCODE) - archive left untouched" }

if (-not $Apply) {
  Write-Output "--- report only: pass -Apply to write ---"
  exit 0
}

# --- 4. apply
Write-Output "--- apply ---"
$applied = & node $patchTool $Asar $InnerPath $editsFile --apply 2>&1
$applied | ForEach-Object { Write-Output $_ }
if ($LASTEXITCODE -ne 0) { throw "apply failed (exit $LASTEXITCODE) - restore from $backup" }

# --- 5. archive-wide verify
Write-Output "--- archive-wide integrity ---"
& node $verifyTool $Asar | ForEach-Object { Write-Output $_ }
if ($LASTEXITCODE -ne 0) { throw "archive verification FAILED - restore from $backup" }
Write-Output "done. Fully quit and relaunch DSH for the new default to take effect."
