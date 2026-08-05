param()

$ErrorActionPreference = "Stop"

$Files = @(
    (Join-Path $PSScriptRoot "APLICAR_UPDATE_12_8.ps1")
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
Write-Host "PAQUETE 12.8: SINTAXIS POWERSHELL CORRECTA." -ForegroundColor Green
Write-Host "Archivos operativos: COMPLETOS." -ForegroundColor Green
