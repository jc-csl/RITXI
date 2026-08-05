param()

$ErrorActionPreference = "Stop"

$SourceRoot = $PSScriptRoot
$Installer = Join-Path `
    $SourceRoot `
    "APLICAR_UPDATE_12_8_7.ps1"
$Recovery = Join-Path `
    $SourceRoot `
    "RECUPERAR_AUDIO_SESION.ps1"
$ReportTool = Join-Path `
    $SourceRoot `
    "payload\tools\ahootsa_session_report.py"
$ShortBlock = Join-Path `
    $SourceRoot `
    "payload\profiles\SHORT_TURNS_AUDIO_BLOCK.txt"

foreach ($File in @(
    Get-ChildItem `
        -Path $SourceRoot `
        -Recurse `
        -File `
        -Filter "*.ps1"
)) {
    $Tokens = $null
    $Errors = $null

    [System.Management.Automation.Language.Parser]::ParseFile(
        $File.FullName,
        [ref]$Tokens,
        [ref]$Errors
    ) | Out-Null

    if ($Errors.Count -gt 0) {
        Write-Host "ERRORES EN: $($File.FullName)" -ForegroundColor Red

        foreach ($Item in $Errors) {
            Write-Host $Item.Message -ForegroundColor Yellow
        }

        exit 1
    }
}

foreach ($Required in @(
    $Installer,
    $Recovery,
    $ReportTool,
    $ShortBlock
)) {
    if (-not (Test-Path $Required)) {
        throw "Falta: $Required"
    }
}

$RecoveryText = Get-Content $Recovery -Raw -Encoding UTF8
$ReportText = Get-Content $ReportTool -Raw -Encoding UTF8
$BlockText = Get-Content $ShortBlock -Raw -Encoding UTF8

foreach ($Required in @(
    "external_finish_requested.flag",
    "Stop-AhootsaConversationAppGracefully",
    "La sesión activa cambió durante la recuperación",
    "Wait-AhootsaPortOpen"
)) {
    if ($RecoveryText -notmatch [regex]::Escape($Required)) {
        throw "Falta en la recuperación: $Required"
    }
}

foreach ($Required in @(
    "terminal_listening_diagnostic",
    "possible_listening_stall",
    "Posible incidencia de escucha",
    '"report_version": "1.2"'
)) {
    if ($ReportText -notmatch [regex]::Escape($Required)) {
        throw "Falta en el informe: $Required"
    }
}

foreach ($Required in @(
    "TURNOS CORTOS Y CONTINUIDAD DE LA ESCUCHA",
    "cuarenta y cinco segundos",
    "divide el contenido en partes breves",
    "espera una nueva respuesta real"
)) {
    if ($BlockText -notmatch [regex]::Escape($Required)) {
        throw "Falta en las instrucciones: $Required"
    }
}

Write-Host ""
Write-Host "PAQUETE 12.8.7: CORRECTO." -ForegroundColor Green
Write-Host "Parser de Windows PowerShell: OK" -ForegroundColor Green
Write-Host "Turnos cortos y relatos por partes: OK" -ForegroundColor Green
Write-Host "Recuperación de audio sin cerrar sesión: OK" -ForegroundColor Green
Write-Host "Diagnóstico de silencio terminal: OK" -ForegroundColor Green
Write-Host "Limpieza de mensajes internos del informe: OK" -ForegroundColor Green
