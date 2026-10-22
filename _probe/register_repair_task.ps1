$ErrorActionPreference = 'Stop'
$scriptPath = 'D:\Resources\DSH\_probe\repair_desktop_profile.ps1'
$taskName = 'DSH Desktop Profile Repair'
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument ('-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "{0}"' -f $scriptPath)
$trigger = New-ScheduledTaskTrigger -Once -At ((Get-Date).AddMinutes(2))
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 30)
$userId = (Get-CimInstance Win32_ComputerSystem).UserName
$principal = New-ScheduledTaskPrincipal -UserId $userId -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description 'Repair DSH desktop pnpm lockfile and update dsh-automation + dshmarket' -Force | Out-Null
$task = Get-ScheduledTask -TaskName $taskName
$info = $task | Get-ScheduledTaskInfo
[pscustomobject]@{
    TaskName = $task.TaskName
    State = $task.State
    NextRunTime = $info.NextRunTime
    LastTaskResult = $info.LastTaskResult
    Execute = $action.Execute
    Arguments = $action.Arguments
    UserId = $principal.UserId
    LogonType = $principal.LogonType
} | Format-List
