param(
    [string]$BaseUrl = "http://127.0.0.1:8100",
    [int]$PausaMilisegundos = 250,
    [switch]$SoloComprobarPersistencia
)

$ErrorActionPreference = "Stop"
$serverRoot = Split-Path $PSScriptRoot -Parent
$definitionPath = Join-Path $serverRoot "config\tests\conversacion_automatica_preferencias.json"
$lastTestPath = Join-Path $serverRoot "data\last_automatic_conversation_test.json"

function Invoke-AhootsaRest {
    param(
        [Parameter(Mandatory = $true)][string]$Uri,
        [ValidateSet("GET", "POST", "PUT")][string]$Method = "GET",
        [object]$Body = $null
    )
    $parameters = @{ Uri = $Uri; Method = $Method; TimeoutSec = 15 }
    if ($Method -ne "GET") {
        $json = if ($null -eq $Body) { "{}" } else { $Body | ConvertTo-Json -Depth 30 }
        $parameters.ContentType = "application/json; charset=utf-8"
        $parameters.Body = [System.Text.Encoding]::UTF8.GetBytes($json)
    }
    return Invoke-RestMethod @parameters
}

function Get-MetadataValue {
    param([object]$Event, [string]$Name)
    if ($null -eq $Event.metadata) { return $null }
    $property = $Event.metadata.PSObject.Properties[$Name]
    if ($null -eq $property) { return $null }
    return $property.Value
}

function Show-Line {
    param([string]$Role, [string]$Text)
    switch ($Role) {
        "assistant" { Write-Host ("Aocha:   {0}" -f $Text) -ForegroundColor Cyan }
        "user"      { Write-Host ("Usuario: {0}" -f $Text) -ForegroundColor Green }
        "system"    { Write-Host ("Sistema: {0}" -f $Text) -ForegroundColor DarkYellow }
        default     { Write-Host ("Evento:  {0}" -f $Text) -ForegroundColor Gray }
    }
}

function Assert-Equals {
    param([object]$Actual, [object]$Expected, [string]$Message)
    if ($Actual -ne $Expected) {
        throw ("{0} Esperado={1}; real={2}." -f $Message, $Expected, $Actual)
    }
}

try { $health = Invoke-AhootsaRest "$BaseUrl/health" }
catch { throw "Ahootsa Local Server no responde en el puerto 8100." }

if ([version]$health.version -lt [version]"0.12.2") {
    throw "Se necesita Ahootsa Local Server 0.12.2 o posterior."
}

if ($SoloComprobarPersistencia) {
    Write-Host "COMPROBACION DE PERSISTENCIA" -ForegroundColor Cyan
    if (-not (Test-Path $lastTestPath)) {
        throw "No existe una prueba anterior. Ejecuta primero el script sin parametros."
    }
    $last = Get-Content $lastTestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $sessionId = [int]$last.session_id
    $runId = [string]$last.test_run_id
    $events = @(Invoke-AhootsaRest "$BaseUrl/sessions/$sessionId/events")
    $summary = Invoke-AhootsaRest "$BaseUrl/sessions/$sessionId/summary"
    $testEvents = @($events | Where-Object {
        (Get-MetadataValue $_ "test_run_id") -eq $runId
    } | Sort-Object { [int](Get-MetadataValue $_ "sequence") })
    Assert-Equals $testEvents.Count 9 "Numero de turnos persistentes incorrecto."
    Assert-Equals $summary.status "finished" "Estado persistente incorrecto."
    Assert-Equals ([int]$summary.user_responses) 3 "Respuestas persistentes incorrectas."
    Assert-Equals ([int]$summary.correct_responses) 3 "Aciertos persistentes incorrectos."
    Assert-Equals ([int]$summary.hints_given) 1 "Pistas persistentes incorrectas."
    Assert-Equals ([int]$summary.silences_detected) 1 "Silencios persistentes incorrectos."
    Write-Host ""
    Write-Host "TRANSCRIPCION RECUPERADA DE SQLITE" -ForegroundColor Cyan
    foreach ($event in $testEvents) {
        Show-Line ([string](Get-MetadataValue $event "role")) ([string]$event.value_text)
    }
    if (-not (Test-Path ([string]$last.report_path))) {
        throw "No se conserva el informe JSON de la prueba."
    }
    Write-Host ""
    Write-Host "PRUEBA 12.4 PERSISTENCIA VALIDADA DESPUES DE RELECTURA." -ForegroundColor Green
    exit 0
}

if (-not (Test-Path $definitionPath)) {
    throw "No se encuentra la definicion de la conversacion: $definitionPath"
}
$definition = Get-Content $definitionPath -Raw -Encoding UTF8 | ConvertFrom-Json

Write-Host "PRUEBA DE CONVERSACION AUTOMATICA Y REGISTRO" -ForegroundColor Cyan
Write-Host "Simula turnos por API; no usa microfono, ASR, Hugging Face ni MuJoCo." -ForegroundColor Gray
Write-Host ("Servidor: {0}" -f $health.version) -ForegroundColor Gray
Write-Host ""

$bootstrap = Invoke-AhootsaRest "$BaseUrl/panel/api/bootstrap"
if ($bootstrap.services.conversation_app.running) {
    throw "Cierra la Conversation App para no mezclar conversaciones."
}
if ($null -ne $bootstrap.active_session) {
    throw ("Finaliza antes la sesion activa {0}." -f $bootstrap.active_session.session_id)
}

$users = @(Invoke-AhootsaRest "$BaseUrl/users")
$testUser = $users | Where-Object { $_.external_id -eq $definition.user.external_id } | Select-Object -First 1
if ($null -eq $testUser) {
    $testUser = Invoke-AhootsaRest -Uri "$BaseUrl/users" -Method POST -Body @{
        external_id = [string]$definition.user.external_id
        name = [string]$definition.user.name
        preferred_name = [string]$definition.user.preferred_name
        language = [string]$definition.user.language
        notes = [string]$definition.user.notes
    }
    Write-Host "Usuario tecnico creado." -ForegroundColor Green
} else {
    Write-Host "Usuario tecnico reutilizado." -ForegroundColor Green
}

Invoke-AhootsaRest -Uri "$BaseUrl/users/$($definition.user.external_id)/profile" -Method PUT -Body @{
    communication_style = "simple"
    speech_speed = "normal"
    response_wait_seconds = 5.0
    preferred_interaction_mode = "mixed"
    preferred_reinforcement = "refuerzo verbal positivo"
    interests = "musica y baile"
    avoid_topics = $null
    accessibility_notes = "Una pregunta por turno y un maximo de dos opciones."
    max_instructions_per_turn = 1
} | Out-Null

$prepared = $null
$finishedOk = $false
$runId = [guid]::NewGuid().ToString()
$eventIds = New-Object System.Collections.Generic.List[int]

try {
    $prepared = Invoke-AhootsaRest -Uri "$BaseUrl/panel/api/session/prepare" -Method POST -Body @{
        user_external_id = [string]$definition.user.external_id
        activity = [string]$definition.session.activity
        level = [string]$definition.session.level
        started_by = [string]$definition.session.started_by
    }
    Write-Host ("Sesion {0} preparada en {1}." -f $prepared.session_id, $prepared.profile_name) -ForegroundColor Green
    Write-Host ""
    Show-Line "assistant" ([string]$prepared.greeting)

    foreach ($item in @($definition.events)) {
        $metadata = @{}
        foreach ($property in $item.metadata.PSObject.Properties) {
            $metadata[$property.Name] = $property.Value
        }
        $metadata["test_run_id"] = $runId
        $metadata["test_name"] = [string]$definition.test_name
        $created = Invoke-AhootsaRest -Uri "$BaseUrl/sessions/active/events" -Method POST -Body @{
            event_type = [string]$item.event_type
            source = [string]$item.source
            activity = [string]$item.activity
            value_text = [string]$item.value_text
            success = $item.success
            metadata = $metadata
        }
        $eventIds.Add([int]$created.id)
        Show-Line ([string]$metadata["role"]) ([string]$item.value_text)
        if ($PausaMilisegundos -gt 0) { Start-Sleep -Milliseconds $PausaMilisegundos }
    }

    $beforeEvents = @(Invoke-AhootsaRest "$BaseUrl/sessions/$($prepared.session_id)/events")
    $testEvents = @($beforeEvents | Where-Object {
        (Get-MetadataValue $_ "test_run_id") -eq $runId
    })
    $activeSummary = Invoke-AhootsaRest "$BaseUrl/sessions/active/summary"
    Assert-Equals $testEvents.Count ([int]$definition.expected.scripted_events) "Eventos previos al cierre incorrectos."
    Assert-Equals ([int]$activeSummary.user_responses) ([int]$definition.expected.user_responses) "Respuestas incorrectas."
    Assert-Equals ([int]$activeSummary.correct_responses) ([int]$definition.expected.correct_responses) "Aciertos incorrectos."
    Assert-Equals ([int]$activeSummary.hints_given) ([int]$definition.expected.hints_given) "Pistas incorrectas."
    Assert-Equals ([int]$activeSummary.silences_detected) ([int]$definition.expected.silences_detected) "Silencios incorrectos."

    $finished = Invoke-AhootsaRest -Uri "$BaseUrl/panel/api/session/finish" -Method POST -Body @{
        note = "Prueba automatica de registro completada. Test run: $runId"
        decision = "no_decision"
    }
    $finishedOk = $true
    Assert-Equals $finished.status "finished" "La sesion no se finalizo."

    $storedEvents = @(Invoke-AhootsaRest "$BaseUrl/sessions/$($prepared.session_id)/events")
    $storedTestEvents = @($storedEvents | Where-Object {
        (Get-MetadataValue $_ "test_run_id") -eq $runId
    })
    $storedSummary = Invoke-AhootsaRest "$BaseUrl/sessions/$($prepared.session_id)/summary"
    Assert-Equals $storedTestEvents.Count 9 "Los turnos no se conservaron."
    Assert-Equals $storedSummary.status "finished" "El resumen final no quedo almacenado."
    Assert-Equals ([int]$storedSummary.activities_completed) 1 "La actividad no consta como completada."

    $sessionDirectory = [string]$prepared.session_directory
    $reportPath = Join-Path $sessionDirectory "automatic_conversation_verification.json"
    $statusPath = Join-Path $sessionDirectory "session_status.json"
    $summaryPath = Join-Path $sessionDirectory "summary.json"
    if (-not (Test-Path $statusPath)) { throw "Falta session_status.json." }
    if (-not (Test-Path $summaryPath)) { throw "Falta summary.json." }

    @{
        test_name = [string]$definition.test_name
        test_run_id = $runId
        verified_at = (Get-Date).ToUniversalTime().ToString("o")
        server_version = [string]$health.version
        session_id = [int]$prepared.session_id
        session_directory = $sessionDirectory
        profile_name = [string]$prepared.profile_name
        scripted_event_count = [int]$storedTestEvents.Count
        registered_event_ids = @($eventIds)
        total_session_events = [int]$storedEvents.Count
        expected = $definition.expected
        summary = $storedSummary
    } | ConvertTo-Json -Depth 30 | Set-Content $reportPath -Encoding UTF8

    @{
        test_run_id = $runId
        session_id = [int]$prepared.session_id
        report_path = $reportPath
        session_directory = $sessionDirectory
        completed_at = (Get-Date).ToUniversalTime().ToString("o")
    } | ConvertTo-Json -Depth 10 | Set-Content $lastTestPath -Encoding UTF8

    Write-Host ""
    Write-Host "PRUEBA 12.4 VALIDADA: CONVERSACION AUTOMATICA REGISTRADA Y PERSISTENTE." -ForegroundColor Green
    Write-Host ("Sesion {0}; eventos del guion {1}; eventos totales {2}." -f $prepared.session_id, $storedTestEvents.Count, $storedEvents.Count) -ForegroundColor Gray
    Write-Host ("Informe: {0}" -f $reportPath) -ForegroundColor Gray
}
catch {
    if ($null -ne $prepared -and -not $finishedOk) {
        try {
            Invoke-AhootsaRest -Uri "$BaseUrl/panel/api/session/finish" -Method POST -Body @{
                note = "Prueba automatica abortada por error."
                decision = "no_decision"
            } | Out-Null
        } catch {}
    }
    throw
}
