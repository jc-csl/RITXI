$ErrorActionPreference = "Continue"
Set-Location -LiteralPath $PSScriptRoot

$Logs = Join-Path $PSScriptRoot "logs"
New-Item -ItemType Directory -Force -Path $Logs | Out-Null

$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = Join-Path $Logs "reachy_daemon_$Stamp.log"
$CurrentLog = Join-Path $Logs "reachy_daemon_current.log"

Write-Host "============================================================"
Write-Host " 2 - INICIAR DAEMON RITXI / REACHY MINI"
Write-Host "============================================================"
Write-Host "Esta ventana debe quedar abierta mientras uses Ritxi."
Write-Host "Puerto esperado: 127.0.0.1:8000"
Write-Host "Log de esta sesion: $LogFile"
Write-Host ""

function Write-Log($msg) {
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $msg"
    Write-Host $line
    $line | Add-Content -Path $LogFile -Encoding utf8
}

function Get-PortPids($port) {
    $pids = @()
    try {
        $lines = netstat -ano | Select-String "LISTENING" | Select-String ":$port"
        foreach ($line in $lines) {
            $parts = ($line.ToString() -split "\s+") | Where-Object { $_ -ne "" }
            if ($parts.Count -ge 5) {
                $pidText = $parts[-1]
                $pidValue = 0
                if ([int]::TryParse($pidText, [ref]$pidValue)) {
                    if ($pidValue -gt 0) { $pids += $pidValue }
                }
            }
        }
    } catch {}
    return $pids | Sort-Object -Unique
}

function Test-Port($port) {
    try {
        $client = New-Object Net.Sockets.TcpClient
        $iar = $client.BeginConnect("127.0.0.1", $port, $null, $null)
        $ok = $iar.AsyncWaitHandle.WaitOne(500, $false)
        if (-not $ok) { $client.Close(); return $false }
        $client.EndConnect($iar)
        $client.Close()
        return $true
    } catch { return $false }
}

"[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Preparando daemon desde $PSScriptRoot" | Out-File -FilePath $LogFile -Encoding utf8 -Force

Write-Log "Cerrando posibles daemons antiguos..."

# 1) Kill by process name
try {
    $oldDaemons = Get-Process -Name "reachy-mini-daemon" -ErrorAction SilentlyContinue
    foreach ($p in $oldDaemons) {
        Write-Log "Matando reachy-mini-daemon.exe PID $($p.Id)"
        Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
    }
} catch {}

# 2) Kill anything listening on port 8000
$pids8000 = Get-PortPids 8000
foreach ($pidValue in $pids8000) {
    try {
        $proc = Get-Process -Id $pidValue -ErrorAction SilentlyContinue
        if ($null -ne $proc) {
            Write-Log "Puerto 8000 ocupado por PID $pidValue ($($proc.ProcessName)). Matando proceso..."
            Stop-Process -Id $pidValue -Force -ErrorAction SilentlyContinue
        }
    } catch {}
}

Start-Sleep -Seconds 2

if (Test-Port 8000) {
    Write-Log "[AVISO] El puerto 8000 sigue ocupado despues del kill."
    Write-Log "Puede estar protegido o estar arrancando otro proceso automaticamente."
    Write-Log "Comando manual: netstat -ano | findstr :8000"
    try { Copy-Item -LiteralPath $LogFile -Destination $CurrentLog -Force -ErrorAction SilentlyContinue } catch {}
    Read-Host "Pulsa ENTER para cerrar"
    exit 1
}

if (-not (Test-Path ".venv\Scripts\reachy-mini-daemon.exe")) {
    Write-Log "[ERROR] No existe .venv\Scripts\reachy-mini-daemon.exe"
    Write-Log "Ejecuta primero: 1_INSTALAR_RITXI.cmd"
    try { Copy-Item -LiteralPath $LogFile -Destination $CurrentLog -Force -ErrorAction SilentlyContinue } catch {}
    Read-Host "Pulsa ENTER para cerrar"
    exit 1
}

Write-Log "Arrancando reachy-mini-daemon --sim..."
Write-Host ""

# Importante:
# reachy-mini-daemon escribe algunas lineas por stderr aunque sean INFO.
# Para evitar NativeCommandError de PowerShell, lo ejecutamos a traves de cmd.exe
# y redirigimos stderr dentro de cmd antes de pasarlo a Tee-Object.
$DaemonExe = Join-Path $PSScriptRoot ".venv\Scripts\reachy-mini-daemon.exe"
$cmdLine = "`"$DaemonExe`" --sim 2>&1"
& cmd.exe /c $cmdLine | Tee-Object -FilePath $LogFile -Append

$ExitCode = $LASTEXITCODE
Write-Host ""
Write-Log "[AVISO] El daemon se ha cerrado con codigo: $ExitCode"
try { Copy-Item -LiteralPath $LogFile -Destination $CurrentLog -Force -ErrorAction SilentlyContinue } catch {}
Write-Host "Log: $LogFile"
Read-Host "Pulsa ENTER para cerrar"
exit $ExitCode
