param(
    [string]$Raiz = "D:\RITXI\AHOOTSA8"
)

$ErrorActionPreference = "Stop"
$origen = Join-Path $PSScriptRoot "documentacion"

$documentacion = Join-Path $Raiz "documentacion"
$serverDocs = Join-Path $Raiz "ahootsa_local_server\docs"

$carpetas = @(
    $documentacion,
    $serverDocs,
    (Join-Path $Raiz "logs\conversation_app"),
    (Join-Path $Raiz "runtime\sessions"),
    (Join-Path $Raiz "runtime\generated_profiles"),
    (Join-Path $Raiz "runtime\imports"),
    (Join-Path $Raiz "runtime\exports")
)

foreach ($carpeta in $carpetas) {
    New-Item -ItemType Directory -Path $carpeta -Force | Out-Null
}

Copy-Item `
    (Join-Path $origen "ANALISIS_ACTIVIDADES_POR_NIVELES_Y_PANEL_PROFESIONAL.md") `
    $documentacion `
    -Force

Copy-Item `
    (Join-Path $origen "ESTADO_ACTUAL_AHOOTSA8.md") `
    $documentacion `
    -Force

Copy-Item `
    (Join-Path $origen "panel_de_control_profesional_ahootsa.png") `
    $documentacion `
    -Force

Copy-Item `
    (Join-Path $origen "ANALISIS_ACTIVIDADES_POR_NIVELES_Y_PANEL_PROFESIONAL.md") `
    (Join-Path $serverDocs "ARQUITECTURA_PANEL_Y_SEGUIMIENTO.md") `
    -Force

Write-Host ""
Write-Host "Estructura documental preparada." -ForegroundColor Green
Write-Host "No se ha modificado código, .env, SQLite ni external_content." -ForegroundColor Cyan
Write-Host ""
Write-Host "Documento principal:"
Write-Host "  $(Join-Path $documentacion 'ANALISIS_ACTIVIDADES_POR_NIVELES_Y_PANEL_PROFESIONAL.md')"
