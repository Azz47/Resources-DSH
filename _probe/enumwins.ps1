# Enumerate every top-level window owned by DeepSeek Harness processes.
# Pure ASCII on purpose: Windows PowerShell 5.1 mis-decodes UTF-8 comments.
Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public class WinEnum {
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
}
"@

$targets = @{}
Get-Process -Name "DeepSeek Harness" -ErrorAction SilentlyContinue | ForEach-Object { $targets[$_.Id] = $true }
Write-Output ("target pids: " + (($targets.Keys | Sort-Object) -join ", "))

$rows = New-Object System.Collections.ArrayList
$sb = New-Object System.Text.StringBuilder 512
$cls = New-Object System.Text.StringBuilder 256

$cb = [WinEnum+EnumProc]{
  param($h, $l)
  $ownerPid = 0
  [void][WinEnum]::GetWindowThreadProcessId($h, [ref]$ownerPid)
  if ($targets.ContainsKey([int]$ownerPid)) {
    [void][WinEnum]::GetWindowText($h, $sb, 512)
    [void][WinEnum]::GetClassName($h, $cls, 256)
    $null = $rows.Add([pscustomobject]@{
      Pid     = $ownerPid
      Visible = [WinEnum]::IsWindowVisible($h)
      Min     = [WinEnum]::IsIconic($h)
      Class   = $cls.ToString()
      Title   = $sb.ToString()
      Hwnd    = ('0x{0:X}' -f [int64]$h)
    })
  }
  return $true
}
[void][WinEnum]::EnumWindows($cb, [IntPtr]::Zero)

if ($rows.Count -eq 0) {
  Write-Output "NO TOP-LEVEL WINDOW AT ALL (not even a hidden one)"
} else {
  Write-Output ("total windows: " + $rows.Count)
  $rows | Format-Table -AutoSize | Out-String -Width 140
}
