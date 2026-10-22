# Bisect desktop profile bundles by launching the app and checking for a visible window.
# Pure ASCII on purpose: Windows PowerShell 5.1 mis-decodes UTF-8 comments.
param(
  [string]$Label,
  [string]$DropCsv
)

$ErrorActionPreference = "Continue"
$P   = "C:\Users\Administrator\.dsh\profiles\desktop"
$BAK = "$P\package.json.bak-bisect"
$PY  = "C:\Users\Administrator\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe"
if (-not (Test-Path $PY)) { $PY = "python" }
$LG  = "$env:APPDATA\@deepseek-ai\dsh-desktop\logs"

$dropJson = ConvertTo-Json -CompileToJson -ErrorAction SilentlyContinue
$dropArr = @()
if ($DropCsv -ne "") { $dropArr = $DropCsv.Split(",") | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" } }
$dropJson = ConvertTo-Json $dropArr -Compress

$script = @"
import io, json, sys
sys.stdout.reconfigure(encoding='utf-8')
p   = r'$P\package.json'
bak = r'$BAK'
d   = json.load(io.open(p, encoding='utf-8'))
old = json.load(io.open(bak, encoding='utf-8'))
drop = set(json.loads(r'''$dropJson'''))
d['dsh']['profile']['bundles'] = [x for x in old['dsh']['profile']['bundles'] if x not in drop]
io.open(p, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=2))
print('bundles=%d' % len(d['dsh']['profile']['bundles']))
"@
$script | & $PY -

$t0 = Get-Date
Get-Process -Name "DeepSeek Harness" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3
$out = "D:\Resources\DSH\_probe\_bt_$Label.txt"
Remove-Item $out -Force -ErrorAction SilentlyContinue
Start-Process "D:\tools\dsh\DeepSeek Harness.exe" -RedirectStandardOutput $out -PassThru | Out-Null

$w = 0
for ($i = 1; $i -le 6; $i++) {
  Start-Sleep -Seconds 8
  $w = @(Get-Process -Name "DeepSeek Harness" -ErrorAction SilentlyContinue |
         Where-Object { $_.MainWindowHandle -ne 0 }).Count
  if ($w -gt 0) { break }
}

$crash = Get-ChildItem $LG -Filter "*main.log" -ErrorAction SilentlyContinue |
         Where-Object { $_.LastWriteTime -gt $t0 } | Select-Object -First 1

if ($w -gt 0) {
  Write-Output ("[$Label]  WINDOW OK")
} elseif ($crash) {
  $err = (Get-Content $crash.FullName -Encoding UTF8 | Select-String '^Error:') | Select-Object -First 1
  Write-Output ("[$Label]  LOCALE ERROR -> " + $err.Line.Trim())
} else {
  Write-Output ("[$Label]  BOOT HANG (no ready, no crash log)")
}
