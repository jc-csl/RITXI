param(
    [string]$ProjectRoot = "D:\RITXI\AHOOTSA8"
)

$ErrorActionPreference = "Stop"

$ServerRoot = Join-Path $ProjectRoot "ahootsa_local_server"
$ServerUrl = "http://127.0.0.1:8100"
$ActiveSessionFile = Join-Path $ServerRoot "data\active_session.json"
$PythonExe = Join-Path $ServerRoot ".venv\Scripts\python.exe"
$ReportTool = Join-Path $ServerRoot "tools\ahootsa_session_report.py"

function Test-LocalPort {
    param([int]$Port)

    $Client = New-Object System.Net.Sockets.TcpClient
    try {
        $Async = $Client.BeginConnect("127.0.0.1", $Port, $null, $null)
        if (-not $Async.AsyncWaitHandle.WaitOne(400)) {
            return $false
        }
        $Client.EndConnect($Async)
        return $true
    } catch {
        return $false
    } finally {
        $Client.Close()
    }
}

if (-not (Test-Path $ActiveSessionFile)) {
    Write-Host (
        "No hay una sesion identificada pendiente de finalizar."
    ) -ForegroundColor Yellow
    exit 0
}

$SessionData = Get-Content `
    $ActiveSessionFile `
    -Raw `
    -Encoding UTF8 |
    ConvertFrom-Json

$SessionId = [int]$SessionData.session_id
$SessionDirectory = [string]$SessionData.session_directory
$LogFile = [string]$SessionData.log_file

if (Test-LocalPort -Port 7860) {
    Write-Host "Cerrando la Conversation App..." -ForegroundColor Cyan

    try {
        Invoke-RestMethod `
            -Uri "http://127.0.0.1:8000/api/apps/stop-current-app" `
            -Method Post `
            -ContentType "application/json" `
            -Body "{}" `
            -TimeoutSec 10 |
            Out-Null
    } catch {
        $Utils = Join-Path $ProjectRoot "scripts\ahootsa_process_utils.ps1"

        if (Test-Path $Utils) {
            . $Utils
            Stop-AhootsaPortProcess `
                -Port 7860 `
                -ServiceName "Reachy Mini Conversation App" |
                Out-Null
        }
    }

    $Deadline = (Get-Date).AddSeconds(20)
    while ((Get-Date) -lt $Deadline -and (Test-LocalPort -Port 7860)) {
        Start-Sleep -Milliseconds 500
    }
}

if (-not (Test-Path $PythonExe)) {
    throw "No se encuentra el Python del servidor: $PythonExe"
}

if (-not (Test-Path $ReportTool)) {
    throw "No se encuentra el generador de informes: $ReportTool"
}

& $PythonExe `
    $ReportTool `
    --session-id $SessionId `
    --server-url $ServerUrl `
    --log $LogFile `
    --session-dir $SessionDirectory

exit $LASTEXITCODE
