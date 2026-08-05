param()

$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$Finalizer = Join-Path `
    $ProjectRoot `
    "FINALIZAR_SESION_AHOOTSA.ps1"

if (-not (Test-Path $Finalizer)) {
    throw (
        "No se encuentra FINALIZAR_SESION_AHOOTSA.ps1 en: " +
        $ProjectRoot
    )
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host " AHOOTSA - FINALIZAR SESION Y DETENER TODO" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

& $Finalizer -DetenerTodo

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
