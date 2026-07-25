$ErrorActionPreference = "Stop"

$mainTest = Join-Path `
    $PSScriptRoot `
    "PROBAR_CONVERSACION_AUTOMATICA_SQLITE_12_4_2_3.ps1"

if (-not (Test-Path $mainTest)) {
    throw "No se encuentra la prueba principal corregida."
}

$sourceText = Get-Content $mainTest -Raw -Encoding UTF8
$start = $sourceText.IndexOf("function Get-AhootsaEventIds")
$end = $sourceText.IndexOf("function Show-Line")

if ($start -lt 0 -or $end -le $start) {
    throw "No se encuentra la funcion Get-AhootsaEventIds."
}

$functionText = $sourceText.Substring($start, $end - $start)
Invoke-Expression $functionText

$event1 = [pscustomobject]@{ id = 70; event_type = "user_response" }
$event2 = [pscustomobject]@{ id = 71; event_type = "robot_message" }

$normal = @($event1, $event2)
$nested = ,$normal
$single = $event1

$normalIds = @(Get-AhootsaEventIds -Response $normal)
$nestedIds = @(Get-AhootsaEventIds -Response $nested)
$singleIds = @(Get-AhootsaEventIds -Response $single)

if (($normalIds -join ",") -ne "70,71") {
    throw "No se normaliza una respuesta array normal."
}
if (($nestedIds -join ",") -ne "70,71") {
    throw "No se normaliza una respuesta Object[] anidada."
}
if (($singleIds -join ",") -ne "70") {
    throw "No se normaliza una respuesta con un unico evento."
}

Write-Host ""
Write-Host (
    "PRUEBA 12.4.2.3 VALIDADA: NORMALIZACION DEL LISTADO API CORRECTA."
) -ForegroundColor Green
