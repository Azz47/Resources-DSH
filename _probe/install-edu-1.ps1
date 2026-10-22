$ErrorActionPreference = 'Continue'

$dshCmd  = "D:\tools\dsh\resources\runtime\cli\bin\dsh.cmd"
$profile = "C:\Users\Administrator\.dsh\profiles\desktop"
$work    = "D:\Resources\DSH\_probe"
$goodDir = Join-Path $work "profile-good"
$logFile = Join-Path $work "install-edu-log.txt"

# Teacher-workflow batch 1: lightweight, no heavy deps.
$packages = @(
  'dsh-animations',
  '@changfenhuang/dsh-genui',
  '@linxin666/dsh-client-ui-skill-explorer',
  'dsh-echocat-skill-panel'
)

function Get-AppAlive { return ((Get-Process -Name 'DeepSeek Harness' -ErrorAction SilentlyContinue) | Measure-Object).Count }
function Write-Log([string]$text) {
  $line = "[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss'), $text
  Write-Output $line
  Add-Content -Path $logFile -Value $line -Encoding utf8
}

Copy-Item (Join-Path $profile 'package.json') (Join-Path $goodDir 'package.json') -Force
Copy-Item (Join-Path $profile 'cordis.patch.yml') (Join-Path $goodDir 'cordis.patch.yml') -Force
foreach ($f in @('cordis.yml','pnpm-workspace.yaml','pnpm-lock.yaml','compatibility.json')) {
  if (Test-Path (Join-Path $profile $f)) { Copy-Item (Join-Path $profile $f) (Join-Path $goodDir $f) -Force }
}

Write-Log "START alive=$(Get-AppAlive)"

foreach ($pkg in $packages) {
  $safe = $pkg -replace '[@/]', '_'
  Write-Log "INSTALL $pkg"
  $raw = & $dshCmd plugin --profile desktop add $pkg 2>&1 | Out-String
  $code = $LASTEXITCODE
  $raw | Set-Content -Path (Join-Path $work "log-edu-$safe.txt") -Encoding utf8
  Start-Sleep -Seconds 8
  $alive = Get-AppAlive

  if ($code -ne 0) {
    Write-Log "FAIL   $pkg exit=$code alive=$alive"
    $tail = ($raw -split "`n" | Where-Object { $_ -match 'dsh:|ERR_PNPM|rejected|incompatible' } | Select-Object -First 4) -join ' | '
    Write-Log "       $tail"
    continue
  }
  if ($alive -lt 4) {
    Write-Log "CRASH  after $pkg - ROLLING BACK"
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
$node = "D:\tools\dsh\resources\runtime\primary-runtime\dependencies\node\bin\node.exe"
Write-Log "dep count: $(& $node -e "const j=require('C:/Users/Administrator/.dsh/profiles/desktop/package.json');console.log(Object.keys(j.dependencies).length)")"
