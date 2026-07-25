$ErrorActionPreference = "Stop"
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$baseUrl = "http://127.0.0.1:8100"

function Invoke-AhootsaJson {
    param(
        [Parameter(Mandatory=$true)][string]$Uri,
        [ValidateSet("GET", "POST")][string]$Method = "GET",
        [object]$Body = $null
    )

    $client = New-Object System.Net.Http.HttpClient
    try {
        if ($Method -eq "POST") {
            $json = if ($null -eq $Body) { "{}" } else { $Body | ConvertTo-Json -Depth 20 }
            $content = New-Object System.Net.Http.StringContent(
                $json,
                [System.Text.Encoding]::UTF8,
                "application/json"
            )
            $response = $client.PostAsync($Uri, $content).GetAwaiter().GetResult()
        } else {
            $response = $client.GetAsync($Uri).GetAwaiter().GetResult()
        }

        $bytes = $response.Content.ReadAsByteArrayAsync().GetAwaiter().GetResult()
        $text = [System.Text.Encoding]::UTF8.GetString($bytes)

        if (-not $response.IsSuccessStatusCode) {
            throw "HTTP $([int]$response.StatusCode): $text"
        }

        return $text | ConvertFrom-Json
    }
    finally {
        $client.Dispose()
    }
}

Write-Host "1. Comprobando versión..." -ForegroundColor Cyan
$health = Invoke-AhootsaJson "$baseUrl/health"
if ($health.version -ne "0.11.0") {
    throw "Versión incorrecta: $($health.version). Debe ser 0.11.0."
}
Write-Host "   Versión 0.11.0 correcta." -ForegroundColor Green

Write-Host "2. Comprobando sesión activa..." -ForegroundColor Cyan
try {
    $sesion = Invoke-AhootsaJson "$baseUrl/sessions/active"
} catch {
    if ($_ -like '*No hay ninguna sesión activa*') {
        Write-Host "   No hay sesión activa." -ForegroundColor Yellow
        Write-Host "   Inicia una sesión y repite la prueba." -ForegroundColor Yellow
        exit 0
    }
    throw
}
Write-Host "   Sesión activa: $($sesion.id)." -ForegroundColor Green

Write-Host "3. Construyendo contexto unificado..." -ForegroundColor Cyan
$contexto = Invoke-AhootsaJson "$baseUrl/context/active"

if ($contexto.session.id -ne $sesion.id) {
    throw "El contexto pertenece a otra sesión."
}
if (-not $contexto.user.external_id) {
    throw "El contexto no contiene el usuario."
}
if ($null -eq $contexto.conversation_state.state) {
    throw "El contexto no contiene el estado conversacional."
}
if ($null -eq $contexto.counters.total_events) {
    throw "El contexto no contiene contadores."
}

Write-Host "   Usuario:   $($contexto.user.preferred_name)" -ForegroundColor Green
Write-Host "   Estado:    $($contexto.conversation_state.state)"
Write-Host "   Actividad: $($contexto.activity.key)"
Write-Host "   Eventos:   $($contexto.counters.total_events)"
Write-Host "   Memorias:  $($contexto.counters.active_memories)"

Write-Host "4. Comprobando UTF-8..." -ForegroundColor Cyan
$catalogo = @(Invoke-AhootsaJson "$baseUrl/activities")
$emociones = $catalogo | Where-Object { $_.key -eq "emotions" }
if ($null -eq $emociones) {
    throw "No se encuentra la actividad emotions."
}
if ($emociones.description -notmatch "alegría") {
    throw "La respuesta no se ha decodificado correctamente como UTF-8: $($emociones.description)"
}
Write-Host "   UTF-8 correcto: $($emociones.description)" -ForegroundColor Green

Write-Host "5. Guardando snapshot..." -ForegroundColor Cyan
$snapshot = Invoke-AhootsaJson `
    -Uri "$baseUrl/context/active/snapshot" `
    -Method POST

if (-not (Test-Path $snapshot.snapshot_file)) {
    throw "No se ha creado el archivo de snapshot: $($snapshot.snapshot_file)"
}
Write-Host "   Snapshot creado:" -ForegroundColor Green
Write-Host "   $($snapshot.snapshot_file)"

Write-Host ""
Write-Host "UPDATE 11 VALIDADO: GESTOR DE CONTEXTO FUNCIONANDO." -ForegroundColor Green
