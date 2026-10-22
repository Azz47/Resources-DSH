<#
  sparse_fetch_skill.ps1 —— 只取 GitHub 仓库里的技能目录（blobless + sparse），不搬整仓。

  为什么：技能本体常常只有整仓的 1/40。实测 iOfficeAI/OfficeCLI ——
    整仓 ZIP 78,714,337 B；只取 skills\ 只要 121 文件 / 1,703,082 B（1.62 MiB）。

  用法：
    pwsh -File _probe\sparse_fetch_skill.ps1 -Repo iOfficeAI/OfficeCLI `
         -Path skills -Dest D:\Resources\DSH\_skillinstall_sparse\OfficeCLI `
         -ExtraFiles SKILL.md,install.ps1,SHA256SUMS

    pwsh -File _probe\sparse_fetch_skill.ps1 -Repo hugohe3/ppt-master `
         -Path skills/ppt-master -Dest D:\Resources\DSH\_skillinstall_sparse\ppt-master `
         -ExtraFiles requirements.txt

  参数：
    -Path       sparse-checkout cone 目录（相对仓库根，正斜杠）；取整仓别用本脚本。
    -ExtraFiles 仓库根散件，用 `git show HEAD:<f>` 单独取出（不动 checkout 的稀疏设定）。
    -Branch     默认分支为空即可；要锁分支就传 main / master。

  断线（promisor remote / schannel server closed abruptly）是瞬断：重跑同一命令，
  或进目标目录再跑一次 git checkout，缺的对象会自动补齐。

  取到目录后装进技能根，用插件自己的导入语义（有 dry-run、有冲突跳过）：
    node D:\Resources\DSH\_probe\import_skills.mjs --dirs <目录>
#>
param(
  [Parameter(Mandatory = $true)][string]$Repo,
  [Parameter(Mandatory = $true)][string]$Path,
  [Parameter(Mandatory = $true)][string]$Dest,
  [string[]]$ExtraFiles = @(),
  [string]$Branch = '',
  [string]$Git = 'D:\tools\git\bin\git.exe'
)
$ErrorActionPreference = 'Stop'
if (Test-Path $Dest) { throw "目标已存在，拒绝覆盖：$Dest" }
if (-not (Test-Path $Git)) { throw "找不到 git：$Git" }

$cloneArgs = @('clone', '--filter=blob:none', '--no-checkout', '--depth', '1')
if ($Branch) { $cloneArgs += @('--branch', $Branch) }
$cloneArgs += @("https://github.com/$Repo.git", $Dest)
Write-Host "[1/4] blobless clone  $Repo"
& $Git @cloneArgs
if ($LASTEXITCODE -ne 0) { throw "clone 失败（瞬断可直接重跑）" }

Push-Location $Dest
try {
  Write-Host "[2/4] sparse-checkout init --cone"
  & $Git sparse-checkout init --cone
  Write-Host "[3/4] sparse-checkout set $Path"
  & $Git sparse-checkout set $Path
  Write-Host "[4/4] checkout（只拉取选中目录的 blob）"
  & $Git checkout
  if ($LASTEXITCODE -ne 0) { throw "checkout 失败（瞬断可直接重跑）" }

  foreach ($f in $ExtraFiles) {
    $out = Join-Path $Dest $f
    $parent = Split-Path $out -Parent
    if ($parent -and -not (Test-Path $parent)) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
    $lines = & $Git show "HEAD:$f" 2>$null
    if ($LASTEXITCODE -ne 0) { Write-Warning "取不到 $f（跳过）"; continue }
    [System.IO.File]::WriteAllText($out, (($lines -join "`n") + "`n"), (New-Object System.Text.UTF8Encoding($false)))
    Write-Host ("  + {0} ({1} B)" -f $f, (Get-Item $out).Length)
  }
}
finally { Pop-Location }

$sel = Join-Path $Dest ($Path -replace '/', '\')
if (Test-Path $sel) {
  $m = Get-ChildItem -Recurse -File $sel | Measure-Object -Property Length -Sum
  Write-Host ("== {0}: {1} 个文件 / {2:N0} B ({3:N2} MiB) ==" -f $Path, $m.Count, $m.Sum, ($m.Sum / 1MB))
} else { Write-Warning "稀疏目录不存在：$sel" }
$all = Get-ChildItem -Recurse -File $Dest |
  Where-Object { $_.FullName -notlike '*\.git\*' } |
  Measure-Object -Property Length -Sum
Write-Host ("== 目标目录合计（不含 .git）：{0} 个文件 / {1:N0} B ==" -f $all.Count, $all.Sum)
