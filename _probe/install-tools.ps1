$ErrorActionPreference = 'Continue'
$dl = "D:\tools\_downloads"
New-Item -ItemType Directory -Force -Path $dl | Out-Null

function Log($m) { Write-Output ("[{0}] {1}" -f (Get-Date -Format 'HH:mm:ss'), $m) }

# ---------- git (PortableGit, self-extracting 7z) ----------
$gitDir = "D:\tools\git"
$gitExe = "$gitDir\cmd\git.exe"
if (Test-Path $gitExe) {
  Log "git already present: $(& $gitExe --version)"
} else {
  $url = "https://github.com/git-for-windows/git/releases/download/v2.56.0.windows.2/PortableGit-2.56.0.2-64-bit.7z.exe"
  $sfx = "$dl\PortableGit.7z.exe"
  if (-not (Test-Path $sfx)) {
    Log "downloading git ..."
    Invoke-WebRequest -Uri $url -OutFile $sfx -TimeoutSec 900
  }
  Log ("git sfx: " + [math]::Round((Get-Item $sfx).Length/1MB,1) + " MB")
  New-Item -ItemType Directory -Force -Path $gitDir | Out-Null
  Log "extracting git -> $gitDir"
  & $sfx -o"$gitDir" -y | Out-Null
  Start-Sleep -Seconds 3
  if (Test-Path $gitExe) { Log "git OK: $(& $gitExe --version)" } else { Log "git EXTRACT FAILED" }
}

# ---------- ffmpeg (zip) ----------
$ffDir = "D:\tools\ffmpeg"
$ffExe = "$ffDir\bin\ffmpeg.exe"
if (Test-Path $ffExe) {
  Log "ffmpeg already present"
} else {
  $url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
  $zip = "$dl\ffmpeg.zip"
  if (-not (Test-Path $zip)) {
    Log "downloading ffmpeg ..."
    Invoke-WebRequest -Uri $url -OutFile $zip -TimeoutSec 1800
  }
  Log ("ffmpeg zip: " + [math]::Round((Get-Item $zip).Length/1MB,1) + " MB")
  $tmp = "$dl\ffmpeg-extract"
  if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
  New-Item -ItemType Directory -Force -Path $tmp | Out-Null
  Log "extracting ffmpeg ..."
  & tar -xf $zip -C $tmp
  $inner = Get-ChildItem $tmp -Directory | Select-Object -First 1
  if ($inner) {
    New-Item -ItemType Directory -Force -Path $ffDir | Out-Null
    Copy-Item "$($inner.FullName)\*" $ffDir -Recurse -Force
    Log "ffmpeg -> $ffDir"
  }
  if (Test-Path $ffExe) { Log "ffmpeg OK" } else { Log "ffmpeg EXTRACT FAILED" }
}

# ---------- add to USER PATH for future sessions ----------
$add = @("$gitDir\cmd", "$ffDir\bin") | Where-Object { Test-Path $_ }
$cur = [Environment]::GetEnvironmentVariable('Path','User')
$parts = @()
if ($cur) { $parts = $cur.Split(';') | Where-Object { $_ -ne '' } }
$changed = $false
foreach ($a in $add) {
  if ($parts -notcontains $a) { $parts += $a; $changed = $true }
}
if ($changed) {
  [Environment]::SetEnvironmentVariable('Path', ($parts -join ';'), 'User')
  Log "user PATH updated: $($add -join ' ; ')"
} else { Log "user PATH already contains the tools" }

Log "DONE"
