$ErrorActionPreference = "Stop"
try {
    [Console]::InputEncoding = New-Object System.Text.UTF8Encoding($false)
    [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
} catch {}

$baseUrl = "http://127.0.0.1:8100"

function Invoke-AhootsaRest {
    param(
        [Parameter(Mandatory=$true)][string]$Uri,
        [ValidateSet("GET", "POST")][string]$Method = "GET",
        [object]$Body = $null
    )

    if ($Method -eq "POST") {
        $json = if ($null -eq $Body) { "{}" } else { $Body | ConvertTo-Json -Depth 20 }
        return Invoke-RestMethod `
            -Uri $Uri `
            -Method Post `
            -ContentType "application/json; charset=utf-8" `
            -Body ([System.Text.Encoding]::UTF8.GetBytes($json))
    }
    return Invoke-RestMethod -Uri $Uri -Method Get
}

Write-Host "1. Comprobando versión..." -ForegroundColor Cyan
$health = Invoke-AhootsaRest "$baseUrl/health"
if ($health.version -ne "0.12.0") {
    throw "Versión incorrecta: $($health.version). Debe ser 0.12.0."
}
Write-Host "   Versión 0.12.0 correcta." -ForegroundColor Green

Write-Host "2. Comprobando el panel HTML..." -ForegroundColor Cyan
$panel = Invoke-WebRequest -Uri "$baseUrl/panel" -UseBasicParsing
if ($panel.StatusCode -ne 200 -or $panel.Content -notmatch "Panel profesional") {
    throw "El panel no responde correctamente."
}
Write-Host "   Panel disponible." -ForegroundColor Green

Write-Host "3. Comprobando configuración y estructura..." -ForegroundColor Cyan
$config = Invoke-AhootsaRest "$baseUrl/panel/api/config/check"
if (-not $config.ok) {
    $fallos = @($config.checks.PSObject.Properties | Where-Object { -not $_.Value } | ForEach-Object { $_.Name })
    throw "Configuración incompleta: $($fallos -join ', ')"
}
Write-Host "   Rutas, scripts, perfil y runtime correctos." -ForegroundColor Green

Write-Host "4. Comprobando catálogo y usuarios..." -ForegroundColor Cyan
$bootstrap = Invoke-AhootsaRest "$baseUrl/panel/api/bootstrap"
$actividades = @($bootstrap.activities)
if (($actividades | Measure-Object).Count -lt 1) {
    throw "No hay actividades configuradas."
}
$preferencias = $actividades | Where-Object { $_.key -eq "express_preferences" }
if ($null -eq $preferencias) {
    throw "No existe la actividad express_preferences."
}

$usuarios = @($bootstrap.users)
if (($usuarios | Measure-Object).Count -eq 0) {
    Write-Host "   No hay usuarios. Creando Álex de ejemplo..." -ForegroundColor Yellow
    $ejemplo = Invoke-AhootsaRest `
        -Uri "$baseUrl/panel/api/example-user" `
        -Method POST `
        -Body @{}
    $usuarioId = $ejemplo.external_id
} else {
    $usuarioId = $usuarios[0].external_id
}
Write-Host "   Usuario para la prueba: $usuarioId" -ForegroundColor Green

$bootstrap = Invoke-AhootsaRest "$baseUrl/panel/api/bootstrap"
if ($null -ne $bootstrap.active_session) {
    Write-Host "5. Ya existe una sesión activa: $($bootstrap.active_session.session_id)." -ForegroundColor Yellow
    Write-Host "   Se valida el panel sin alterar esa sesión." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "UPDATE 12 VALIDADO: PANEL MVP DISPONIBLE; SESIÓN EXISTENTE CONSERVADA." -ForegroundColor Green
    exit 0
}

Write-Host "5. Preparando una sesión de prueba sin lanzar Reachy..." -ForegroundColor Cyan
$preparada = Invoke-AhootsaRest `
    -Uri "$baseUrl/panel/api/session/prepare" `
    -Method POST `
    -Body @{
        user_external_id = $usuarioId
        activity = "express_preferences"
        level = "initial"
        started_by = "Prueba Update 12"
    }

if (-not (Test-Path -LiteralPath $preparada.context_file)) {
    throw "No se ha creado session_context.json."
}
if (-not (Test-Path -LiteralPath $preparada.launcher_script)) {
    throw "No se ha creado el lanzador de sesión."
}
if (-not (Test-Path -LiteralPath $preparada.profile_directory)) {
    throw "No se ha creado el perfil temporal."
}
Write-Host "   Contexto, perfil y lanzador creados." -ForegroundColor Green

Write-Host "6. Registrando marcas profesionales de prueba..." -ForegroundColor Cyan
foreach ($accion in @("adequate", "partial", "hint", "repeat")) {
    Invoke-AhootsaRest `
        -Uri "$baseUrl/panel/api/session/event" `
        -Method POST `
        -Body @{ action = $accion; note = "Prueba automática" } | Out-Null
}
$resumen = Invoke-AhootsaRest "$baseUrl/panel/api/session/summary"
if ($resumen.counts.adequate -ne 1 -or $resumen.counts.partial -ne 1) {
    throw "Los contadores del panel no son correctos."
}
Write-Host "   Registro rápido correcto." -ForegroundColor Green

Write-Host "7. Finalizando la sesión de prueba..." -ForegroundColor Cyan
$final = Invoke-AhootsaRest `
    -Uri "$baseUrl/panel/api/session/finish" `
    -Method POST `
    -Body @{
        note = "Sesión técnica de validación del Update 12."
        decision = "no_decision"
    }
if ($final.status -ne "finished") {
    throw "La sesión no se ha finalizado correctamente."
}
Write-Host "   Sesión finalizada y guardada." -ForegroundColor Green

Write-Host ""
Write-Host "UPDATE 12 VALIDADO: PANEL MVP, PERFIL TEMPORAL Y SEGUIMIENTO FUNCIONANDO." -ForegroundColor Green
Write-Host "No se ha lanzado el daemon ni la Conversation App durante esta prueba." -ForegroundColor Gray
