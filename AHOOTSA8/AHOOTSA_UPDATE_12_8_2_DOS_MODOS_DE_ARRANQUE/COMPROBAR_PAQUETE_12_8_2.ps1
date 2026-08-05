param()

$ErrorActionPreference = "Stop"

$Files = @(
    (Join-Path $PSScriptRoot "APLICAR_UPDATE_12_8_2.ps1")
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

foreach ($Relative in @(
    "payload\INICIAR_AHOOTSA_ANONIMO.ps1",
    "payload\INICIAR_AHOOTSA_SESION.ps1",
    "payload\FINALIZAR_SESION_AHOOTSA.ps1",
    "payload\COMPROBAR_AHOOTSA.ps1",
    "payload\LIMPIAR_PROCESOS_AHOOTSA.ps1",
    "payload\scripts\iniciar_conversation_anonima.ps1",
    "payload\scripts\iniciar_conversation_sesion.ps1"
)) {
    if (-not (Test-Path (Join-Path $PSScriptRoot $Relative))) {
        throw "Falta: $Relative"
    }
}

Write-Host ""
Write-Host "PAQUETE 12.8.2: SINTAXIS POWERSHELL CORRECTA." -ForegroundColor Green
Write-Host "Inicio anónimo independiente: PRESENTE." -ForegroundColor Green
Write-Host "Inicio con sesión local: PRESENTE." -ForegroundColor Green
Write-Host "No ejecutes archivos dentro de payload." -ForegroundColor Yellow
