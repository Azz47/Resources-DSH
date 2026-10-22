param(
  [string]$OutRoot = "D:\Resources\DSH\_specs\atlas\png",
  [int]$W = 960,
  [int]$H = 540
)
$ErrorActionPreference = "Continue"
New-Item -ItemType Directory -Force -Path $OutRoot | Out-Null

$targets = @()
# 27 style templates: first two slides each
$styleRoot = Join-Path $env:USERPROFILE ".dsh\skills\morph-ppt\reference\styles"
Get-ChildItem $styleRoot -Directory | Sort-Object Name | ForEach-Object {
  $f = Get-ChildItem $_.FullName -Filter *.pptx -File | Select-Object -First 1
  if ($f) { $targets += [pscustomobject]@{ Slug = $_.Name; File = $f.FullName; Pages = @(1, 2) } }
}
# web samples
$web = "D:\Resources\DSH\corpus\_web\gordensun"
foreach ($n in @("data-viz-deck", "report-massive-charts", "red-teaching-framework")) {
  $f = Join-Path $web ($n + ".pptx")
  if (Test-Path $f) { $targets += [pscustomobject]@{ Slug = "web--" + $n; File = $f; Pages = @(1, 2, 3, 5) } }
}
# our decks
$decks = "D:\Resources\DSH\decks"
$v2 = Get-ChildItem $decks -Directory | Where-Object { $_.Name -like "*v2*" } | Select-Object -First 1
if ($v2) {
  $f = Get-ChildItem $v2.FullName -Filter *.pptx -File | Sort-Object Length -Descending | Select-Object -First 1
  if ($f) { $targets += [pscustomobject]@{ Slug = "ours--v2"; File = $f.FullName; Pages = @(1, 8, 13, 22, 36, 44) } }
}
$v1dir = Get-ChildItem $decks -Directory | Where-Object { $_.Name -notlike "*v2*" } | Select-Object -First 1
if ($v1dir) {
  $f = Get-ChildItem $v1dir.FullName -Filter source.pptx -File | Select-Object -First 1
  if (-not $f) { $f = Get-ChildItem $v1dir.FullName -Filter *.pptx -File | Sort-Object Length -Descending | Select-Object -First 1 }
  if ($f) { $targets += [pscustomobject]@{ Slug = "ours--v1"; File = $f.FullName; Pages = @(1, 10, 20, 30) } }
}

Write-Output ("targets: " + $targets.Count)
$ppt = New-Object -ComObject PowerPoint.Application
try { $ppt.Visible = 1 } catch { Write-Output "visible set failed" }
$ok = 0; $fail = 0
foreach ($t in $targets) {
  $dir = Join-Path $OutRoot $t.Slug
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  try {
    $pres = $ppt.Presentations.Open($t.File, $true, $false, $false)
    $count = $pres.Slides.Count
    foreach ($p in $t.Pages) {
      if ($p -gt $count) { continue }
      $out = Join-Path $dir ("p{0:d2}.png" -f $p)
      if (Test-Path $out) { Remove-Item $out -Force }
      $pres.Slides.Item($p).Export($out, "PNG", $W, $H)
      $ok++
    }
    $pres.Close()
    Write-Output ("OK  " + $t.Slug + "  slides=" + $count)
  } catch {
    $fail++
    Write-Output ("ERR " + $t.Slug + "  " + $_.Exception.Message)
    try { $pres.Close() } catch {}
  }
}
try { $ppt.Quit() } catch {}
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($ppt) | Out-Null
Write-Output ("exported=" + $ok + " failed_decks=" + $fail)
