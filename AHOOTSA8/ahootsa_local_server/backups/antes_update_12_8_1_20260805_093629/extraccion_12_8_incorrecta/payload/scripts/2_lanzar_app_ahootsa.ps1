param(
    [switch]$DebugMode
)

$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$AppRoot = Join-Path $ProjectRoot "reachy_mini_conversation_app"
$ServerRoot = Join-Path $ProjectRoot "ahootsa_local_server"
$ServerUrl = "http://127.0.0.1:8100"
$ActiveSessionFile = Join-Path $ServerRoot "data\active_session.json"
$DotEnvPath = Join-Path $AppRoot ".env"
$PythonExe = Join-Path $ServerRoot ".venv\Scripts\python.exe"
$ReportTool = Join-Path $ServerRoot "tools\ahootsa_session_report.py"

function Set-DotEnvValue {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [string]$Name,

        [Parameter(Mandatory = $true)]
        [string]$Value
    )

    $Lines = @()
    if (Test-Path $Path) {
        $Lines = @(Get-Content $Path -Encoding UTF8)
    }

    $Pattern = "^\s*#?\s*" + [regex]::Escape($Name) + "\s*="
    $Replacement = "$Name=$Value"
    $Found = $false
    $Result = New-Object System.Collections.Generic.List[string]

    foreach ($Line in $Lines) {
        if ($Line -match $Pattern) {
            if (-not $Found) {
                $Result.Add($Replacement)
                $Found = $true
            }
        } else {
            $Result.Add($Line)
        }
    }

    if (-not $Found) {
        $Result.Add($Replacement)
    }

    [System.IO.File]::WriteAllLines(
        $Path,
        $Result.ToArray(),
        (New-Object System.Text.UTF8Encoding($false))
    )
}

function Get-ServerBootstrap {
    try {
        return Invoke-RestMethod `
            -Uri "$ServerUrl/panel/api/bootstrap" `
            -Method Get `
            -TimeoutSec 5
    } catch {
        return $null
    }
}

if (-not (Test-Path (Join-Path $AppRoot ".venv\Scripts\Activate.ps1"))) {
    throw "No se encuentra el entorno oficial: $AppRoot\.venv"
}

$Bootstrap = Get-ServerBootstrap
$ActiveSession = $null

if ($null -ne $Bootstrap) {
    $ActiveSession = $Bootstrap.active_session
}

$SessionMode = $false
$SessionId = $null
$SessionDirectory = $null
$ProfileName = "ahootsa"
$AnonymousDirectory = Join-Path $ServerRoot "data\anonymous"
$LogFile = Join-Path $AnonymousDirectory "conversation_app.log"

if ($null -ne $ActiveSession) {
    $SessionMode = $true
    $SessionId = [int]$ActiveSession.session_id
    $ProfileName = "ahootsa_session"

    if (-not (Test-Path $ActiveSessionFile)) {
        throw (
            "Existe una sesion activa, pero falta active_session.json. " +
            "Vuelve a preparar la sesion desde el panel."
        )
    }

    $SessionData = Get-Content `
        $ActiveSessionFile `
        -Raw `
        -Encoding UTF8 |
        ConvertFrom-Json

    if ([int]$SessionData.session_id -ne $SessionId) {
        throw (
            "La sesion activa del servidor no coincide con active_session.json."
        )
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

    if (Test-Path $ActiveSessionFile) {
        Remove-Item $ActiveSessionFile -Force
    }
}

Set-DotEnvValue `
    -Path $DotEnvPath `
    -Name "REACHY_MINI_CUSTOM_PROFILE" `
    -Value $ProfileName

$env:REACHY_MINI_CUSTOM_PROFILE = $ProfileName

$LogDirectory = Split-Path $LogFile -Parent
New-Item -ItemType Directory -Path $LogDirectory -Force | Out-Null

Set-Location $AppRoot
& ".\.venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "AHOOTSA - INICIO DE CONVERSACION" -ForegroundColor Cyan

if ($SessionMode) {
    Write-Host "Modo: SESION IDENTIFICADA" -ForegroundColor Green
    Write-Host "Sesion: $SessionId" -ForegroundColor Gray
    Write-Host "Perfil: ahootsa_session" -ForegroundColor Gray
    Write-Host "Al cerrar se generara el informe de sesion." -ForegroundColor Green
} else {
    Write-Host "Modo: ANONIMO" -ForegroundColor Yellow
    Write-Host "Perfil: ahootsa" -ForegroundColor Gray
    Write-Host (
        "No se identifica a la persona y no se genera informe de sesion."
    ) -ForegroundColor Yellow
}

Write-Host "Log: $LogFile" -ForegroundColor Gray
Write-Host ""

Start-Transcript -Path $LogFile -Append | Out-Null

try {
    if ($DebugMode) {
        reachy-mini-conversation-app --ui --debug
    } else {
        reachy-mini-conversation-app --ui
    }
}
finally {
    try {
        Stop-Transcript | Out-Null
    } catch {}

    if ($SessionMode) {
        $PanelFinishMarker = Join-Path `
            $SessionDirectory `
            "panel_finish_requested.flag"

        if (Test-Path $PanelFinishMarker) {
            Write-Host ""
            Write-Host (
                "El panel profesional completara la sesion y generara "
                + "el informe."
            ) -ForegroundColor Cyan
        } else {
            Write-Host ""
            Write-Host "Procesando la sesion identificada..." -ForegroundColor Cyan

            if (-not (Test-Path $PythonExe)) {
                Write-Host (
                    "No se encuentra el Python del servidor. " +
                    "El informe queda pendiente."
                ) -ForegroundColor Red
            } elseif (-not (Test-Path $ReportTool)) {
                Write-Host (
                    "No se encuentra ahootsa_session_report.py. " +
                    "El informe queda pendiente."
                ) -ForegroundColor Red
            } else {
                & $PythonExe `
                    $ReportTool `
                    --session-id $SessionId `
                    --server-url $ServerUrl `
                    --log $LogFile `
                    --session-dir $SessionDirectory

                if ($LASTEXITCODE -ne 0) {
                    Write-Host (
                        "No se pudo completar el informe. " +
                        "Ejecuta FINALIZAR_SESION_AHOOTSA.ps1."
                    ) -ForegroundColor Yellow
                }
            }
        }
    } else {
        Write-Host ""
        Write-Host (
            "Conversacion anonima finalizada. No se ha creado una sesion."
        ) -ForegroundColor Yellow
    }

    Set-DotEnvValue `
        -Path $DotEnvPath `
        -Name "REACHY_MINI_CUSTOM_PROFILE" `
        -Value "ahootsa"

    $env:REACHY_MINI_CUSTOM_PROFILE = "ahootsa"
}
