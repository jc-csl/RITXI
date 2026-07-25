$ErrorActionPreference = "Stop"

try {
    [Console]::InputEncoding = New-Object System.Text.UTF8Encoding($false)
    [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
} catch {
    # La codificación de consola no debe impedir la prueba funcional.
}

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
if ($health.version -ne "0.11.1") {
    throw "Versión incorrecta: $($health.version). Debe ser 0.11.1."
}
Write-Host "   Versión 0.11.1 correcta." -ForegroundColor Green

Write-Host "2. Comprobando sesión activa..." -ForegroundColor Cyan
try {
    $sesion = Invoke-AhootsaRest "$baseUrl/sessions/active"
} catch {
    $detalle = ""
    if ($_.ErrorDetails -and $_.ErrorDetails.Message) {
        $detalle = $_.ErrorDetails.Message
    } else {
        $detalle = $_.Exception.Message
    }

    if ($detalle -like '*No hay ninguna sesión activa*' -or $detalle -like '*404*') {
        Write-Host "   No hay sesión activa." -ForegroundColor Yellow
        Write-Host "   Inicia una sesión y repite esta prueba." -ForegroundColor Yellow
        exit 0
    }
    throw
}
Write-Host "   Sesión activa: $($sesion.id)." -ForegroundColor Green

Write-Host "3. Construyendo contexto unificado..." -ForegroundColor Cyan
$contexto = Invoke-AhootsaRest "$baseUrl/context/active"

if ([int]$contexto.session.id -ne [int]$sesion.id) {
    throw "El contexto pertenece a otra sesión."
}
if ([string]::IsNullOrWhiteSpace([string]$contexto.user.external_id)) {
    throw "El contexto no contiene el usuario."
}
if ([string]::IsNullOrWhiteSpace([string]$contexto.conversation_state.state)) {
    throw "El contexto no contiene el estado conversacional."
}
if ($null -eq $contexto.counters.total_events) {
    throw "El contexto no contiene el contador total_events."
}

Write-Host "   Usuario:   $($contexto.user.preferred_name)" -ForegroundColor Green
Write-Host "   Estado:    $($contexto.conversation_state.state)"
if ($null -ne $contexto.activity) {
    Write-Host "   Actividad: $($contexto.activity.key)"
} else {
    Write-Host "   Actividad: ninguna"
}
Write-Host "   Eventos:   $($contexto.counters.total_events)"
Write-Host "   Memorias:  $($contexto.counters.active_memories)"

Write-Host "4. Comprobando catálogo de actividades..." -ForegroundColor Cyan
$catalogo = Invoke-AhootsaRest "$baseUrl/activities"
$cantidad = ($catalogo | Measure-Object).Count

if ($cantidad -lt 2) {
    throw "El catálogo debe contener al menos dos actividades. Encontradas: $cantidad."
}

$keys = @($catalogo | ForEach-Object { $_.key })
if ($keys -notcontains "emotions") {
    throw "No se encuentra la actividad emotions."
}
if ($keys -notcontains "preferences") {
    throw "No se encuentra la actividad preferences."
}
Write-Host "   Catálogo correcto: $cantidad actividades." -ForegroundColor Green

Write-Host "5. Guardando snapshot..." -ForegroundColor Cyan
$snapshot = Invoke-AhootsaRest `
    -Uri "$baseUrl/context/active/snapshot" `
    -Method POST

if ([string]::IsNullOrWhiteSpace([string]$snapshot.snapshot_file)) {
    throw "La API no ha devuelto la ruta del snapshot."
}
if (-not (Test-Path -LiteralPath $snapshot.snapshot_file)) {
    throw "No se ha creado el snapshot: $($snapshot.snapshot_file)"
}
Write-Host "   Snapshot creado:" -ForegroundColor Green
Write-Host "   $($snapshot.snapshot_file)"

Write-Host "6. Validando el JSON del snapshot..." -ForegroundColor Cyan
$rawSnapshot = Get-Content -LiteralPath $snapshot.snapshot_file -Raw -Encoding UTF8
$snapshotJson = $rawSnapshot | ConvertFrom-Json

if ([int]$snapshotJson.session.id -ne [int]$sesion.id) {
    throw "El snapshot pertenece a otra sesión."
}
if ([string]::IsNullOrWhiteSpace([string]$snapshotJson.context_version)) {
    throw "El snapshot no incluye context_version."
}
Write-Host "   JSON del snapshot correcto." -ForegroundColor Green

Write-Host ""
Write-Host "UPDATE 11.1 VALIDADO: COMPATIBILIDAD POWERSHELL Y CONTEXTO CORRECTOS." -ForegroundColor Green
