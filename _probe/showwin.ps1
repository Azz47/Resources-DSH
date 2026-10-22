# Force-show the hidden DeepSeek Harness main window.
# Pure ASCII on purpose: Windows PowerShell 5.1 mis-decodes UTF-8 comments.
Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public class WinShow {
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
}
"@

$SW_SHOW = 5
$SW_RESTORE = 9

$targets = @{}
Get-Process -Name "DeepSeek Harness" -ErrorAction SilentlyContinue | ForEach-Object { $targets[$_.Id] = $true }

$sb = New-Object System.Text.StringBuilder 512
$cls = New-Object System.Text.StringBuilder 256
$main = [IntPtr]::Zero

$cb = [WinShow+EnumProc]{
  param($h, $l)
  $ownerPid = 0
  [void][WinShow]::GetWindowThreadProcessId($h, [ref]$ownerPid)
  if ($targets.ContainsKey([int]$ownerPid)) {
    [void][WinShow]::GetClassName($h, $cls, 256)
    if ($cls.ToString() -eq 'Chrome_WidgetWin_1') {
      [void][WinShow]::GetWindowText($h, $sb, 512)
      if ($sb.ToString() -eq 'DeepSeek Harness') { $script:main = $h }
    }
  }
  return $true
}
[void][WinShow]::EnumWindows($cb, [IntPtr]::Zero)

if ($main -eq [IntPtr]::Zero) {
  Write-Output "main window not found"
  exit 1
}

Write-Output ("main window hwnd = 0x{0:X}" -f [int64]$main)
Write-Output ("visible before : " + [WinShow]::IsWindowVisible($main))
Write-Output ("minimized before: " + [WinShow]::IsIconic($main))

if ([WinShow]::IsIconic($main)) { [void][WinShow]::ShowWindow($main, $SW_RESTORE) }
else { [void][WinShow]::ShowWindow($main, $SW_SHOW) }
Start-Sleep -Milliseconds 600
[void][WinShow]::SetForegroundWindow($main)
Start-Sleep -Milliseconds 600

Write-Output ("visible after  : " + [WinShow]::IsWindowVisible($main))
Write-Output ("minimized after : " + [WinShow]::IsIconic($main))
