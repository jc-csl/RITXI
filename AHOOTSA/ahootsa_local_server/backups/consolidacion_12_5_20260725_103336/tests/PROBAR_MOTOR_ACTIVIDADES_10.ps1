$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$baseUrl = "http://127.0.0.1:8100"

Write-Host "1. Comprobando versión..." -ForegroundColor Cyan
$health = Invoke-RestMethod "$baseUrl/health"
if ($health.version -ne "0.10.0") {
    throw "Versión incorrecta: $($health.version). Debe ser 0.10.0."
}
Write-Host "   Versión 0.10.0 correcta." -ForegroundColor Green

Write-Host "2. Consultando catálogo..." -ForegroundColor Cyan
$catalogo = Invoke-RestMethod "$baseUrl/activities"
$cantidadActividades = ($catalogo | Measure-Object).Count
if ($cantidadActividades -lt 2) {
    throw "El catálogo debe contener al menos dos actividades."
}
$catalogo | Format-Table key, title, version
Write-Host "   Catálogo correcto." -ForegroundColor Green

Write-Host "3. Comprobando sesión activa..." -ForegroundColor Cyan
try {
    $sesion = Invoke-RestMethod "$baseUrl/sessions/active"
} catch {
    if ($_.ErrorDetails.Message -like '*No hay ninguna sesión activa*') {
        Write-Host "   No hay sesión activa." -ForegroundColor Yellow
        Write-Host "   Inicia una sesión y repite esta prueba." -ForegroundColor Yellow
        exit 0
    }
    throw
}
Write-Host "   Sesión activa: $($sesion.id)." -ForegroundColor Green

Write-Host "4. Comprobando si ya hay actividad..." -ForegroundColor Cyan
try {
    $activa = Invoke-RestMethod "$baseUrl/activities/active"
    Write-Host "   Ya existe una actividad activa: $($activa.activity)." -ForegroundColor Yellow
    Write-Host "   Se usará esa actividad para evitar duplicarla." -ForegroundColor Yellow
} catch {
    if ($_.ErrorDetails.Message -like '*No hay ninguna actividad activa*') {
        $body = @{ activity = "emotions" } | ConvertTo-Json
        $activa = Invoke-RestMethod `
            -Uri "$baseUrl/activities/active/start" `
            -Method Post `
            -ContentType "application/json; charset=utf-8" `
            -Body ([System.Text.Encoding]::UTF8.GetBytes($body))
        Write-Host "   Actividad emotions iniciada." -ForegroundColor Green
    } else {
        throw
    }
}

Write-Host ""
Write-Host "ESTADO ACTUAL" -ForegroundColor Cyan
Write-Host "Actividad: $($activa.activity)"
Write-Host "Paso:      $($activa.step)"
Write-Host "Acción:    $($activa.action)"
Write-Host "Texto:     $($activa.text)"

if ($activa.activity -eq "emotions") {
    $respuestas = @{
        1 = "alegre"
        2 = "triste"
        3 = "enfadada"
    }
    $respuesta = $respuestas[[int]$activa.step]

    if ($respuesta) {
        Write-Host "5. Enviando respuesta de prueba: $respuesta" -ForegroundColor Cyan
        $answerBody = @{ answer = $respuesta } | ConvertTo-Json
        $resultado = Invoke-RestMethod `
            -Uri "$baseUrl/activities/active/answer" `
            -Method Post `
            -ContentType "application/json; charset=utf-8" `
            -Body ([System.Text.Encoding]::UTF8.GetBytes($answerBody))

        Write-Host "   Respuesta procesada." -ForegroundColor Green
        Write-Host "   Nueva acción: $($resultado.action)"
        Write-Host "   Nuevo paso:   $($resultado.step)"
        Write-Host "   Texto:        $($resultado.text)"
    }
}

Write-Host ""
Write-Host "UPDATE 10 VALIDADO: MOTOR DE ACTIVIDADES FUNCIONANDO." -ForegroundColor Green

