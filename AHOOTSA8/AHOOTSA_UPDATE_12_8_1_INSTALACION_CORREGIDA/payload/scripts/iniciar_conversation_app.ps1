param(
    [switch]$DebugMode
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path $PSScriptRoot -Parent
$AppRoot = Join-Path $ProjectRoot "reachy_mini_conversation_app"
$ServerRoot = Join-Path $ProjectRoot "ahootsa_local_server"
$UtilsPath = Join-Path $PSScriptRoot "ahootsa_process_utils.ps1"
$Activate = Join-Path $AppRoot ".venv\Scripts\Activate.ps1"
$DotEnvPath = Join-Path $AppRoot ".env"
$ActiveSessionFile = Join-Path $ServerRoot "data\active_session.json"
$PythonExe = Join-Path $ServerRoot ".venv\Scripts\python.exe"
$ReportTool = Join-Path $ServerRoot "tools\ahootsa_session_report.py"
$ServerUrl = "http://127.0.0.1:8100"

if (-not (Test-Path $UtilsPath)) {
    throw "No se encuentra la utilidad de procesos: $UtilsPath"
}

. $UtilsPath

if (-not (Test-Path $Activate)) {
    throw "No se encuentra el entorno oficial: $Activate"
}

if (Test-AhootsaPort -Port 7860) {
    Write-Host (
        "La Conversation App ya está activa en el puerto 7860."
    ) -ForegroundColor Yellow

    exit 0
}

$Bootstrap = $null

try {
    $Bootstrap = Invoke-RestMethod `
        -Uri "$ServerUrl/panel/api/bootstrap" `
        -Method Get `
        -TimeoutSec 10
} catch {
    throw "El servidor local no responde en el puerto 8100."
}

$SessionMode = $false
$SessionId = $null
$SessionDirectory = $null
$ProfileName = "ahootsa"
$AnonymousDirectory = Join-Path $ServerRoot "data\anonymous"
$LogFile = Join-Path $AnonymousDirectory "conversation_app.log"

if ($null -ne $Bootstrap.active_session) {
    $SessionMode = $true
    $SessionId = [int]$Bootstrap.active_session.session_id
    $ProfileName = "ahootsa_session"

    if (-not (Test-Path $ActiveSessionFile)) {
        throw "Existe una sesión activa, pero falta active_session.json."
    }

    $SessionData = Get-Content `
        $ActiveSessionFile `
        -Raw `
        -Encoding UTF8 |
        ConvertFrom-Json

    if ([int]$SessionData.session_id -ne $SessionId) {
        throw "La sesión de la base de datos no coincide con active_session.json."
    }

    $SessionDirectory = [string]$SessionData.session_directory
    $LogFile = [string]$SessionData.log_file
} else {
    New-Item `
        -ItemType Directory `
        -Path $AnonymousDirectory `
        -Force |
        Out-Null

    if (Test-Path $LogFile) {
        Remove-Item $LogFile -Force
    }
}

Set-AhootsaDotEnvProfile `
    -DotEnvPath $DotEnvPath `
    -ProfileName $ProfileName

$env:REACHY_MINI_CUSTOM_PROFILE = $ProfileName

$LogDirectory = Split-Path $LogFile -Parent

New-Item `
    -ItemType Directory `
    -Path $LogDirectory `
    -Force |
    Out-Null

Set-Location $AppRoot
& $Activate

Write-Host ""
Write-Host "AHOOTSA CONVERSATION APP" -ForegroundColor Cyan

if ($SessionMode) {
    Write-Host "Modo: SESIÓN IDENTIFICADA" -ForegroundColor Green
    Write-Host "Sesión: $SessionId" -ForegroundColor Gray
    Write-Host "Perfil: ahootsa_session" -ForegroundColor Gray
} else {
    Write-Host "Modo: ANÓNIMO" -ForegroundColor Yellow
    Write-Host "Perfil: ahootsa" -ForegroundColor Gray
    Write-Host "No se genera informe personal." -ForegroundColor Yellow
}

Write-Host "Puerto: 7860" -ForegroundColor Gray
Write-Host "Log: $LogFile" -ForegroundColor Gray
Write-Host ""

Start-Transcript `
    -Path $LogFile `
    -Append |
    Out-Null

try {
    if ($DebugMode) {
        reachy-mini-conversation-app --ui --debug
    } else {
        reachy-mini-conversation-app --ui
    }
} finally {
    try {
        Stop-Transcript | Out-Null
    } catch {}

    if ($SessionMode) {
        $PanelMarker = Join-Path `
            $SessionDirectory `
            "panel_finish_requested.flag"

        $ScriptMarker = Join-Path `
            $SessionDirectory `
            "external_finish_requested.flag"

        $OtherFinalizerOwnsSession = (
            (Test-Path $PanelMarker) -or
            (Test-Path $ScriptMarker)
        )

        if ($OtherFinalizerOwnsSession) {
            Write-Host ""
            Write-Host (
                "Otro finalizador completará la sesión y el informe."
            ) -ForegroundColor Cyan
        } elseif (
            (Test-Path $PythonExe) -and
            (Test-Path $ReportTool)
        ) {
            Write-Host ""
            Write-Host (
                "Procesando la sesión identificada y generando el informe..."
            ) -ForegroundColor Cyan

            & $PythonExe `
                $ReportTool `
                --session-id $SessionId `
                --server-url $ServerUrl `
                --log $LogFile `
                --session-dir $SessionDirectory

            if ($LASTEXITCODE -ne 0) {
                Write-Host (
                    "El informe queda pendiente. Ejecuta " +
                    "FINALIZAR_SESION_AHOOTSA.ps1."
                ) -ForegroundColor Yellow
            }
        }
    } else {
        Write-Host ""
        Write-Host (
            "Conversación anónima finalizada."
        ) -ForegroundColor Yellow
    }

    Set-AhootsaDotEnvProfile `
        -DotEnvPath $DotEnvPath `
        -ProfileName "ahootsa"

    $env:REACHY_MINI_CUSTOM_PROFILE = "ahootsa"
}
