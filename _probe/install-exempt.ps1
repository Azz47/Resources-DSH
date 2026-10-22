$ErrorActionPreference = 'Continue'

$dshCmd  = "D:\tools\dsh\resources\runtime\cli\bin\dsh.cmd"
$profile = "C:\Users\Administrator\.dsh\profiles\desktop"
$work    = "D:\Resources\DSH\_probe"
$goodDir = Join-Path $work "profile-good"
$logFile = Join-Path $work "install-log2.txt"

function Get-AppAlive { return ((Get-Process -Name 'DeepSeek Harness' -ErrorAction SilentlyContinue) | Measure-Object).Count }
function Write-Log([string]$text) {
  $line = "[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss'), $text
  Write-Output $line
  Add-Content -Path $logFile -Value $line -Encoding utf8
}

# name@version -> runtime the exemption is granted for
$plan = @(
  @{ pkg = '@arcaneorion/dsh-teaching-board'; version = '0.6.0' },
  @{ pkg = 'dsh-plugin-education';            version = '0.3.2' }
)

Write-Log "START alive=$(Get-AppAlive)  exemptions granted for dsh 0.2.0-rc.2"

foreach ($item in $plan) {
  $pkg = $item.pkg; $ver = $item.version

  Write-Log "EXEMPT $pkg@$ver"
  $ex = & $dshCmd plugin --profile desktop allow-version "$pkg@$ver" --dsh-version 0.2.0-rc.2 --accept-risk 2>&1 | Out-String
  Write-Log "       $(($ex -split "`n" | Where-Object { $_ -match 'dsh:' }) -join ' | ')"

  Write-Log "INSTALL $pkg"
  $raw = & $dshCmd plugin --profile desktop add $pkg 2>&1 | Out-String
  $code = $LASTEXITCODE
  $raw | Set-Content -Path (Join-Path $work ("log2-" + ($pkg -replace '[@/]', '_') + ".txt")) -Encoding utf8
  Start-Sleep -Seconds 8
  $alive = Get-AppAlive

  if ($code -ne 0) {
    Write-Log "FAIL   $pkg exit=$code alive=$alive"
    $tail = ($raw -split "`n" | Where-Object { $_ -match 'dsh:' } | Select-Object -First 4) -join ' | '
    Write-Log "       $tail"
    continue
  }

  if ($alive -lt 4) {
    Write-Log "CRASH  app died after $pkg - rolling back package.json/bundles and revoking exemption"
    Copy-Item (Join-Path $goodDir 'package.json') (Join-Path $profile 'package.json') -Force
    Copy-Item (Join-Path $goodDir 'cordis.patch.yml') (Join-Path $profile 'cordis.patch.yml') -Force
    & $dshCmd plugin --profile desktop revoke-version "$pkg@$ver" --dsh-version 0.2.0-rc.2 2>&1 | Out-Null
    Write-Log "STOP   rolled back"
    break
  }

  Write-Log "OK     $pkg exit=0 alive=$alive"
  Copy-Item (Join-Path $profile 'package.json') (Join-Path $goodDir 'package.json') -Force
  Copy-Item (Join-Path $profile 'cordis.patch.yml') (Join-Path $goodDir 'cordis.patch.yml') -Force
}

Write-Log "DONE alive=$(Get-AppAlive)"
Write-Log "--- compatibility.json ---"
if (Test-Path (Join-Path $profile 'compatibility.json')) { Get-Content (Join-Path $profile 'compatibility.json') -Raw | Add-Content -Path $logFile -Encoding utf8 }
Write-Log "--- final bundles ---"
$pj = Get-Content (Join-Path $profile 'package.json') -Raw
Write-Log $pj
