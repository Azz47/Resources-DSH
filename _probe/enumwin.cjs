const { execSync } = require("child_process");
const ps = `
Add-Type @"
using System;
using System.Text;
using System.Runtime.InteropServices;
public class W {
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern int GetWindowTextLength(IntPtr h);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
}
"@
$sb = New-Object System.Text.StringBuilder 512
$cls = New-Object System.Text.StringBuilder 256
$cb = [W+EnumProc]{
  param($h, $l)
  $pid2 = 0
  [void][W]::GetWindowThreadProcessId($h, [ref]$pid2)
  $p = Get-Process -Id $pid2 -ErrorAction SilentlyContinue
  if ($p -and $p.ProcessName -eq 'DeepSeek Harness') {
    [void][W]::GetWindowText($h, $sb, 512)
    [void][W]::GetClassName($h, $cls, 256)
    "{0}|{1}|{2}|{3}|{4}" -f $pid2, [W]::IsWindowVisible($h), $cls.ToString(), $sb.ToString(), [int64]$h
  }
  return $true
}
[void][W]::EnumWindows($cb, [IntPtr]::Zero)
`;
const out = execSync("powershell -NoProfile -Command " + JSON.stringify(ps), { encoding: "utf8", maxBuffer: 1e7 });
console.log("=== DeepSeek Harness 的顶层窗口 ===");
console.log(out.trim() || "(一个窗口都没有)");
