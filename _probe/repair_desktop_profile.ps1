# DSH desktop profile repair: fix broken pnpm lockfile and update two plugins.
# ASCII only. Windows PowerShell 5.1 compatible.

$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'

$script:Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$script:Probe = 'D:\Resources\DSH\_probe'
$script:ProfDir = 'C:\Users\Administrator\.dsh\profiles\desktop'
$script:Runtime = 'D:\tools\dsh\resources\runtime\primary-runtime'
$script:Node = Join-Path $script:Runtime 'dependencies\node\bin\node.exe'
$script:Pnpm = Join-Path $script:Runtime 'dependencies\pnpm\bin\pnpm.cjs'
$script:DshCmd = 'D:\tools\dsh\resources\runtime\cli\bin\dsh.cmd'
$script:AppExe = 'D:\tools\dsh\DeepSeek Harness.exe'
$script:LogPath = Join-Path $script:Probe ('repair_desktop_' + $script:Stamp + '.log')
$script:BackupDir = Join-Path $script:Probe ('backup_desktop_' + $script:Stamp)
$script:Failed = $null
$script:PostAuto = ''
$script:PostMarket = ''

function Write-Log {
    param([string]$Message)
    $line = '[' + (Get-Date -Format 'HH:mm:ss') + '] ' + $Message
    Add-Content -LiteralPath $script:LogPath -Value $line -Encoding ASCII
    Write-Host $line
}

function Run-Cmd {
    param([string]$Exe, [string[]]$Argv, [string]$Label)
    Write-Log ('RUN ' + $Label + ': ' + $Exe + ' ' + ($Argv -join ' '))
    $out = & $Exe @Argv 2>&1
    $code = $LASTEXITCODE
    if ($null -ne $out) {
        foreach ($line in @($out)) { Write-Log ('  ' + [string]$line) }
    }
    Write-Log ('EXIT ' + $Label + ' = ' + $code)
    return $code
}

function Get-PkgVersion {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return 'MISSING' }
    try {
        $obj = Get-Content -Raw -LiteralPath $Path | ConvertFrom-Json
        return [string]$obj.version
    } catch {
        return 'UNREADABLE'
    }
}

function Stop-Dsh {
    Write-Log 'Stopping DSH desktop.'
    $procs = @(Get-Process -Name 'DeepSeek Harness' -ErrorAction SilentlyContinue)
    Write-Log ('DeepSeek Harness processes: ' + $procs.Count)
    foreach ($p in $procs) {
        try { if ($p.MainWindowHandle -ne 0) { [void]$p.CloseMainWindow() } } catch { }
    }
    $deadline = (Get-Date).AddSeconds(60)
    while ((Get-Date) -lt $deadline) {
        $left = @(Get-Process -Name 'DeepSeek Harness' -ErrorAction SilentlyContinue)
        if ($left.Count -eq 0) { break }
        Start-Sleep -Seconds 2
    }
    $left = @(Get-Process -Name 'DeepSeek Harness' -ErrorAction SilentlyContinue)
    if ($left.Count -gt 0) {
        Write-Log 'Graceful close timed out; forcing termination.'
        foreach ($p in $left) {
            try { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue } catch { }
        }
        Start-Sleep -Seconds 4
    }
    $left = @(Get-Process -Name 'DeepSeek Harness' -ErrorAction SilentlyContinue)
    if ($left.Count -gt 0) { throw 'DSH desktop is still running.' }

    $nodes = @(Get-CimInstance Win32_Process -Filter "Name='node.exe'" -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -and $_.CommandLine -match 'billion-context[\\/]dist[\\/]index\.js'
    })
    foreach ($n in $nodes) {
        Write-Log ('Stopping billion-context node PID ' + $n.ProcessId)
        try { Stop-Process -Id $n.ProcessId -Force -ErrorAction SilentlyContinue } catch { }
    }
    Start-Sleep -Seconds 2
    try {
        $conns = @(Get-NetTCPConnection -LocalPort 18787 -State Listen -ErrorAction SilentlyContinue)
        foreach ($c in $conns) {
            Write-Log ('Stopping port 18787 owner PID ' + $c.OwningProcess)
            try { Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue } catch { }
        }
    } catch { }

    $runFile = Join-Path $script:ProfDir '.plugin-manager\run.json'
    if (Test-Path -LiteralPath $runFile) {
        try {
            $rec = Get-Content -Raw -LiteralPath $runFile | ConvertFrom-Json
            $alive = $false
            if ($rec.pid) { $alive = [bool](Get-Process -Id ([int]$rec.pid) -ErrorAction SilentlyContinue) }
            if (-not $alive) {
                Remove-Item -LiteralPath $runFile -Force -ErrorAction SilentlyContinue
                Write-Log 'Removed stale .plugin-manager/run.json'
            }
        } catch {
            Remove-Item -LiteralPath $runFile -Force -ErrorAction SilentlyContinue
        }
    }
    Write-Log 'DSH desktop stopped.'
}

function Backup-Profile {
    New-Item -ItemType Directory -Path $script:BackupDir -Force | Out-Null
    $files = @('package.json', 'pnpm-lock.yaml', 'pnpm-workspace.yaml', 'compatibility.json', 'node_modules\.modules.yaml')
    foreach ($f in $files) {
        $src = Join-Path $script:ProfDir $f
        if (Test-Path -LiteralPath $src) {
            $dst = Join-Path $script:BackupDir ($f -replace '\\', '__')
            Copy-Item -LiteralPath $src -Destination $dst -Force
            if (-not (Test-Path -LiteralPath $dst)) { throw ('backup failed: ' + $f) }
            Write-Log ('Backed up ' + $f)
        } else {
            Write-Log ('Skip missing backup file ' + $f)
        }
    }
}

function Restore-Profile {
    Write-Log 'Rollback: restoring manifest backups.'
    foreach ($f in @('package.json', 'pnpm-workspace.yaml', 'compatibility.json')) {
        $src = Join-Path $script:BackupDir $f
        if (Test-Path -LiteralPath $src) {
            Copy-Item -LiteralPath $src -Destination (Join-Path $script:ProfDir $f) -Force
        }
    }
    $code = Run-Cmd $script:Node @($script:Pnpm, 'install', '--fix-lockfile', '--ignore-scripts') 'rollback-pnpm-install'
    if ($code -ne 0) {
        Write-Log 'Rollback install failed; restoring original lockfile bytes.'
        $src = Join-Path $script:BackupDir 'pnpm-lock.yaml'
        if (Test-Path -LiteralPath $src) {
            Copy-Item -LiteralPath $src -Destination (Join-Path $script:ProfDir 'pnpm-lock.yaml') -Force
        }
    }
    $code2 = Run-Cmd $script:Node @($script:Pnpm, 'install', '--frozen-lockfile', '--ignore-scripts') 'rollback-frozen-check'
    Write-Log ('Rollback frozen check exit = ' + $code2)
}

function Start-Dsh {
    Write-Log 'Starting DSH desktop.'
    Start-Process -FilePath $script:AppExe -WorkingDirectory 'D:\tools\dsh' | Out-Null
    Start-Sleep -Seconds 12
    $procs = @(Get-Process -Name 'DeepSeek Harness' -ErrorAction SilentlyContinue)
    Write-Log ('DeepSeek Harness processes after launch: ' + $procs.Count)
    return ($procs.Count -gt 0)
}

Set-Location $script:ProfDir
Write-Log '=== DSH desktop profile repair start ==='
Write-Log ('Stamp: ' + $script:Stamp)
Write-Log ('Profile: ' + $script:ProfDir)
Write-Log ('Log: ' + $script:LogPath)

$preAuto = Get-PkgVersion (Join-Path $script:ProfDir 'node_modules\@michengai\dsh-automation\package.json')
$preMarket = Get-PkgVersion (Join-Path $script:ProfDir 'node_modules\dshmarket\package.json')
Write-Log ('Versions before repair: automation=' + $preAuto + ' dshmarket=' + $preMarket)

try { Stop-Dsh } catch { $script:Failed = 'stop: ' + $_.Exception.Message }

$canRestore = Test-Path -LiteralPath (Join-Path $script:BackupDir 'package.json')
if ($script:Failed) {
    Write-Log ('Abort before changes: ' + $script:Failed)
} else {
    try { Backup-Profile } catch { $script:Failed = 'backup: ' + $_.Exception.Message }
    $canRestore = Test-Path -LiteralPath (Join-Path $script:BackupDir 'package.json')
}

if (-not $script:Failed) {
    $code = Run-Cmd $script:Node @($script:Pnpm, 'install', '--fix-lockfile') 'pnpm-install-fix'
    if ($code -ne 0) { $script:Failed = 'pnpm-install-fix exit ' + $code }
}
if (-not $script:Failed) {
    $code = Run-Cmd $script:DshCmd @('plugin', '--profile', 'desktop', 'add', '@michengai/dsh-automation@1.0.4') 'add-automation'
    if ($code -ne 0) { $script:Failed = 'add-automation exit ' + $code }
}
if (-not $script:Failed) {
    $code = Run-Cmd $script:DshCmd @('plugin', '--profile', 'desktop', 'add', 'dshmarket@1.66.42') 'add-dshmarket'
    if ($code -ne 0) { $script:Failed = 'add-dshmarket exit ' + $code }
}

if (-not $script:Failed) {
    $script:PostAuto = Get-PkgVersion (Join-Path $script:ProfDir 'node_modules\@michengai\dsh-automation\package.json')
    $script:PostMarket = Get-PkgVersion (Join-Path $script:ProfDir 'node_modules\dshmarket\package.json')
    Write-Log ('Versions after repair: automation=' + $script:PostAuto + ' dshmarket=' + $script:PostMarket)
    try {
        $pkg = Get-Content -Raw -LiteralPath (Join-Path $script:ProfDir 'package.json') | ConvertFrom-Json
        $pa = $pkg.dependencies.PSObject.Properties['@michengai/dsh-automation']
        $pm = $pkg.dependencies.PSObject.Properties['dshmarket']
        if ($null -ne $pa) { Write-Log ('package.json automation spec: ' + [string]$pa.Value) }
        if ($null -ne $pm) { Write-Log ('package.json dshmarket spec: ' + [string]$pm.Value) }
    } catch { Write-Log ('package.json read failed: ' + $_.Exception.Message) }
    if ($script:PostAuto -ne '1.0.4') { $script:Failed = 'automation installed version is ' + $script:PostAuto }
    elseif ($script:PostMarket -ne '1.66.42') { $script:Failed = 'dshmarket installed version is ' + $script:PostMarket }
}

if (-not $script:Failed) {
    $code = Run-Cmd $script:Node @('D:\Resources\DSH\_probe\profile_integrity.js') 'integrity'
    if ($code -ne 0) { $script:Failed = 'integrity exit ' + $code }
}
if (-not $script:Failed) {
    $code = Run-Cmd $script:Node @($script:Pnpm, 'install', '--frozen-lockfile', '--ignore-scripts') 'frozen-check'
    if ($code -ne 0) { $script:Failed = 'frozen-check exit ' + $code }
}

if ($script:Failed) {
    Write-Log ('REPAIR FAILED: ' + $script:Failed)
    if ($canRestore -and -not $script:Failed.StartsWith('stop:')) {
        try { Restore-Profile } catch { Write-Log ('Rollback error: ' + $_.Exception.Message) }
    } else {
        Write-Log 'No rollback performed.'
    }
} else {
    Write-Log 'All repair checks passed.'
}

$appRunning = $false
if ($script:Failed -and $script:Failed.StartsWith('stop:')) {
    Write-Log 'App is still running; not launching another instance.'
} else {
    try { $appRunning = Start-Dsh } catch { Write-Log ('App start failed: ' + $_.Exception.Message) }
}

$resultPath = Join-Path $script:Probe ('repair_desktop_' + $script:Stamp + '.json')
$result = [ordered]@{
    stamp = $script:Stamp
    failed = [string]$script:Failed
    automation_version = $script:PostAuto
    dshmarket_version = $script:PostMarket
    app_running = $appRunning
    log = $script:LogPath
} | ConvertTo-Json
try { Set-Content -LiteralPath $resultPath -Value $result -Encoding ASCII } catch { }

if ($script:Failed -and -not $appRunning) {
    Write-Log ('REPAIR_RESULT=FAILED reason=' + $script:Failed)
    exit 1
}
if ($script:Failed) {
    Write-Log ('REPAIR_RESULT=ROLLED_BACK_OR_ABORTED reason=' + $script:Failed)
    exit 2
}
if (-not $appRunning) {
    Write-Log 'REPAIR_RESULT=FAILED reason=app-not-running'
    exit 1
}
Write-Log 'REPAIR_RESULT=SUCCESS'
exit 0
