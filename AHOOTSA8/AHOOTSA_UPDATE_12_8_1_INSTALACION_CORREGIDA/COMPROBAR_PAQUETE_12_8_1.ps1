param()

$ErrorActionPreference = "Stop"

$Files = @(
    (Join-Path $PSScriptRoot "APLICAR_UPDATE_12_8_1.ps1")
)

$Files += @(
    Get-ChildItem `
        -Path (Join-Path $PSScriptRoot "payload") `
        -Recurse `
        -File `
        -Filter "*.ps1"
).FullName

foreach ($File in $Files) {
    $Tokens = $null
    $Errors = $null

    [System.Management.Automation.Language.Parser]::ParseFile(
        $File,
        [ref]$Tokens,
        [ref]$Errors
    ) | Out-Null

    if ($Errors.Count -gt 0) {
        Write-Host ""
        Write-Host "ERRORES EN: $File" -ForegroundColor Red

        foreach ($Item in $Errors) {
            Write-Host $Item.Message -ForegroundColor Yellow
        }

        exit 1
    }

    $Text = Get-Content $File -Raw -Encoding UTF8

    $InvalidVariablePattern = '\$ServiceName' + ':'

    if ($Text -match $InvalidVariablePattern) {
        throw "Referencia inválida encontrada en: $File"
    }
}

$Required = @(
    "payload\INICIAR_AHOOTSA.ps1",
    "payload\FINALIZAR_SESION_AHOOTSA.ps1",
    "payload\COMPROBAR_AHOOTSA.ps1",
    "payload\LIMPIAR_PROCESOS_AHOOTSA.ps1",
    "payload\scripts\ahootsa_process_utils.ps1",
    "payload\scripts\iniciar_servidor_local.ps1",
    "payload\scripts\iniciar_daemon_mujoco.ps1",
    "payload\scripts\iniciar_conversation_app.ps1",
    "payload\tools\ahootsa_session_report.py",
    "payload\app\panel_mvp.py"
)

foreach ($Relative in $Required) {
    $Path = Join-Path $PSScriptRoot $Relative

    if (-not (Test-Path $Path)) {
        throw "Falta: $Relative"
    }
}

Write-Host ""
Write-Host "PAQUETE 12.8.1: SINTAXIS POWERSHELL CORRECTA." -ForegroundColor Green
Write-Host "Referencia de variables con dos puntos: CORREGIDA." -ForegroundColor Green
Write-Host "Estructura del paquete: CORRECTA." -ForegroundColor Green
Write-Host "No ejecutes ningún archivo dentro de payload." -ForegroundColor Yellow
