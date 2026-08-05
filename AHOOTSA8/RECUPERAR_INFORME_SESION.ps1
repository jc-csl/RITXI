param(
    [Parameter(Mandatory = $true)]
    [int]$SessionId,

    [string]$ProjectRoot = "D:\RITXI\AHOOTSA8"
)

$ErrorActionPreference = "Stop"

$ServerRoot = Join-Path $ProjectRoot "ahootsa_local_server"
$SessionDirectory = Join-Path `
    $ServerRoot `
    ("data\sessions\session_{0:D6}" -f $SessionId)
$LogFile = Join-Path $SessionDirectory "conversation_app.log"
$PythonExe = Join-Path $ServerRoot ".venv\Scripts\python.exe"
$ReportTool = Join-Path $ServerRoot "tools\ahootsa_session_report.py"
$ServerLauncher = Join-Path `
    $ProjectRoot `
    "scripts\iniciar_servidor_local.ps1"
$PendingFile = Join-Path `
    $SessionDirectory `
    "informe_sesion_pendiente.json"

function Test-Port {
    param([int]$Port)

    try {
        $Client = New-Object System.Net.Sockets.TcpClient
        $Result = $Client.BeginConnect(
            "127.0.0.1",
            $Port,
            $null,
            $null
        )
        $Connected = $Result.AsyncWaitHandle.WaitOne(500, $false)

        if ($Connected) {
            $Client.EndConnect($Result)
        }

        $Client.Close()
        return $Connected
    } catch {
        return $false
    }
}

if (-not (Test-Path $SessionDirectory)) {
    throw "No existe la carpeta de la sesión: $SessionDirectory"
}

if (-not (Test-Path $LogFile)) {
    throw "No existe el log de la sesión: $LogFile"
}

if (-not (Test-Path $PythonExe)) {
    throw "No existe el Python del servidor: $PythonExe"
}

if (-not (Test-Path $ReportTool)) {
    throw "No existe el generador de informes: $ReportTool"
}

if (-not (Test-Port -Port 8100)) {
    if (-not (Test-Path $ServerLauncher)) {
        throw "El servidor está detenido y falta: $ServerLauncher"
    }

    Write-Host "Arrancando temporalmente el servidor local..." -ForegroundColor Cyan

    Start-Process `
        powershell.exe `
        -WorkingDirectory $ProjectRoot `
        -ArgumentList @(
            "-NoExit",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            $ServerLauncher
        )

    $Deadline = (Get-Date).AddSeconds(60)

    while (
        (Get-Date) -lt $Deadline -and
        -not (Test-Port -Port 8100)
    ) {
        Start-Sleep -Milliseconds 500
    }

    if (-not (Test-Port -Port 8100)) {
        throw "El servidor local no responde en el puerto 8100."
    }
}

Write-Host ""
Write-Host "REGENERANDO INFORME DE LA SESIÓN $SessionId" -ForegroundColor Cyan
Write-Host "Carpeta: $SessionDirectory" -ForegroundColor Gray
Write-Host ""

& $PythonExe `
    $ReportTool `
    --session-id $SessionId `
    --server-url "http://127.0.0.1:8100" `
    --log $LogFile `
    --session-dir $SessionDirectory

if ($LASTEXITCODE -ne 0) {
    throw "No se pudo regenerar el informe de la sesión $SessionId."
}

Remove-Item `
    $PendingFile `
    -Force `
    -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "INFORME RECUPERADO CORRECTAMENTE." -ForegroundColor Green

Get-ChildItem `
    $SessionDirectory `
    -File |
    Where-Object {
        $_.Name -in @(
            "informe_sesion.pdf",
            "informe_sesion.html",
            "informe_sesion.json",
            "transcripcion_sesion.txt"
        )
    } |
    Format-Table Name,Length,LastWriteTime -AutoSize
