$ErrorActionPreference = "Continue"
Set-Location -LiteralPath $PSScriptRoot

$Logs = Join-Path $PSScriptRoot "logs"
New-Item -ItemType Directory -Force -Path $Logs | Out-Null
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LauncherLog = Join-Path $Logs "lanzador_completo_$Stamp.log"

function Log($msg) {
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $msg"
    Write-Host $line
    $line | Add-Content -Path $LauncherLog -Encoding utf8
}

function Test-Port($port) {
    try {
        $client = New-Object Net.Sockets.TcpClient
        $iar = $client.BeginConnect("127.0.0.1", $port, $null, $null)
        $ok = $iar.AsyncWaitHandle.WaitOne(700, $false)
        if (-not $ok) { $client.Close(); return $false }
        $client.EndConnect($iar)
        $client.Close()
        return $true
    } catch { return $false }
}

function Wait-Port($port, $seconds, $name) {
    for ($i=1; $i -le $seconds; $i++) {
        if (Test-Port $port) {
            Log "[OK] $name disponible en 127.0.0.1:$port tras $i s"
            return $true
        }
        if (($i % 5) -eq 0) { Log "esperando $name... $i/$seconds s" }
        Start-Sleep -Seconds 1
    }
    return $false
}

Write-Host "============================================================"
Write-Host " 6 - LANZAR RITXI COMPLETO"
Write-Host "============================================================"
Write-Host "Log: $LauncherLog"
Write-Host ""

foreach ($f in @("1_INSTALAR_RITXI.cmd","2_INICIAR_DAEMON_RITXI.cmd","3_RUN_RITXI.cmd")) {
    if (-not (Test-Path $f)) {
        Log "[ERROR] No encuentro $f"
        Read-Host "Pulsa ENTER para cerrar"
        exit 1
    }
}

Log "[1/3] Instalando / actualizando Ritxi..."
$env:RITXI_NO_PAUSE = "1"
& cmd.exe /c "1_INSTALAR_RITXI.cmd"
$installCode = $LASTEXITCODE
Remove-Item Env:\RITXI_NO_PAUSE -ErrorAction SilentlyContinue

if ($installCode -ne 0) {
    Log "[ERROR] Fallo 1_INSTALAR_RITXI.cmd con código $installCode"
    Read-Host "Pulsa ENTER para cerrar"
    exit $installCode
}

Log "[2/3] Lanzando daemon en otra terminal..."
Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "cd /d `"$PSScriptRoot`" && 2_INICIAR_DAEMON_RITXI.cmd"

Log "Esperando daemon: primero comprobación de puerto 8000 hasta 45 segundos..."
$daemonReady = Wait-Port 8000 45 "daemon Reachy/MuJoCo"

if (-not $daemonReady) {
    Log "[AVISO] No se detecta puerto 8000 tras 45 s. Se lanza 3_RUN_RITXI.cmd igualmente, pero puede avisar si el daemon aún no está listo."
}

Log "[3/3] Lanzando Ritxi/FastAPI en otra terminal..."
Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "cd /d `"$PSScriptRoot`" && 3_RUN_RITXI.cmd"

Log "[OK] Flujo completo lanzado."
Log "Ventanas abiertas: daemon y Ritxi/FastAPI."
Write-Host ""
Write-Host "[OK] Puedes cerrar esta ventana si Ritxi ya ha abierto."
Start-Sleep -Seconds 3
