$ErrorActionPreference = "Stop"

$serverRoot = Split-Path $PSScriptRoot -Parent
$pythonExe = Join-Path $serverRoot ".venv\Scripts\python.exe"
$verifier = Join-Path $PSScriptRoot "verificar_eventos_sqlite_12_4_2.py"
$selfTest = Join-Path $PSScriptRoot "probar_verificador_sqlite_12_4_2_1.py"

if (-not (Test-Path $pythonExe)) {
    throw "No se encuentra el Python del servidor: $pythonExe"
}
if (-not (Test-Path $verifier)) {
    throw "No se encuentra el verificador corregido: $verifier"
}
if (-not (Test-Path $selfTest)) {
    throw "No se encuentra la prueba del verificador: $selfTest"
}

Write-Host "1. Comprobando sintaxis Python..." -ForegroundColor Cyan
& $pythonExe -m py_compile $verifier $selfTest

if ($LASTEXITCODE -ne 0) {
    throw "La comprobacion de sintaxis Python ha fallado."
}

Write-Host "   Sintaxis correcta." -ForegroundColor Green
Write-Host "2. Ejecutando una base SQLite temporal..." -ForegroundColor Cyan

$resultText = & $pythonExe $selfTest
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0) {
    throw "La prueba funcional del verificador SQLite ha fallado."
}

if ([string]::IsNullOrWhiteSpace($resultText)) {
    throw "La prueba funcional no devolvio resultado."
}

$result = $resultText | ConvertFrom-Json

if (-not $result.ok -or [int]$result.found_count -ne 2) {
    throw "El resultado funcional del verificador no es correcto."
}

Write-Host "   El verificador encontro los eventos 70 y 71." -ForegroundColor Green
Write-Host ""
Write-Host (
    "PRUEBA 12.4.2.1 VALIDADA: VERIFICADOR SQLITE CORREGIDO."
) -ForegroundColor Green
