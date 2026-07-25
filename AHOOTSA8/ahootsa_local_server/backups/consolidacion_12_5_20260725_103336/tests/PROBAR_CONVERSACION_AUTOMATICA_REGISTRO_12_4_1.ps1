param(
    [string]$BaseUrl = "http://127.0.0.1:8100",
    [int]$PausaMilisegundos = 250
)

$ErrorActionPreference = "Stop"
try {
    [Console]::InputEncoding = New-Object System.Text.UTF8Encoding($false)
    [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
} catch {}

$serverRoot = Split-Path $PSScriptRoot -Parent
$definitionPath = Join-Path `
    $serverRoot `
    "config\tests\conversacion_automatica_preferencias.json"
$lastTestPath = Join-Path `
    $serverRoot `
    "data\last_automatic_conversation_test.json"

function Invoke-AhootsaJson {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Uri,

        [ValidateSet("GET", "POST", "PUT")]
        [string]$Method = "GET",

        [object]$Body = $null
    )

    $request = [System.Net.HttpWebRequest]::Create($Uri)
    $request.Method = $Method
    $request.Accept = "application/json"
    $request.Timeout = 15000
    $request.ReadWriteTimeout = 15000

    if ($Method -ne "GET") {
        $json = if ($null -eq $Body) {
            "{}"
        } else {
            $Body | ConvertTo-Json -Depth 30
        }

        $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
        $request.ContentType = "application/json; charset=utf-8"
        $request.ContentLength = $bytes.Length

        $requestStream = $request.GetRequestStream()
        try {
            $requestStream.Write($bytes, 0, $bytes.Length)
        } finally {
            $requestStream.Close()
        }
    }

    try {
        $response = $request.GetResponse()
    } catch [System.Net.WebException] {
        $message = $_.Exception.Message
        if ($null -ne $_.Exception.Response) {
            $errorStream = $_.Exception.Response.GetResponseStream()
            $errorReader = New-Object System.IO.StreamReader(
                $errorStream,
                [System.Text.Encoding]::UTF8
            )
            try {
                $errorText = $errorReader.ReadToEnd()
                if (-not [string]::IsNullOrWhiteSpace($errorText)) {
                    $message = $message + " | " + $errorText
                }
            } finally {
                $errorReader.Close()
            }
        }
        throw $message
    }

    try {
        $responseStream = $response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader(
            $responseStream,
            [System.Text.Encoding]::UTF8
        )
        try {
            $text = $reader.ReadToEnd()
        } finally {
            $reader.Close()
        }
    } finally {
        $response.Close()
    }

    if ([string]::IsNullOrWhiteSpace($text)) {
        return $null
    }

    return $text | ConvertFrom-Json
}

function Show-Line {
    param(
        [string]$Role,
        [string]$Text
    )

    switch ($Role) {
        "assistant" {
            Write-Host ("Aocha:   {0}" -f $Text) -ForegroundColor Cyan
        }
        "user" {
            Write-Host ("Usuario: {0}" -f $Text) -ForegroundColor Green
        }
        "system" {
            Write-Host ("Sistema: {0}" -f $Text) -ForegroundColor DarkYellow
        }
        default {
            Write-Host ("Evento:  {0}" -f $Text) -ForegroundColor Gray
        }
    }
}

function Assert-Equals {
    param(
        [object]$Actual,
        [object]$Expected,
        [string]$Message
    )

    if ($Actual -ne $Expected) {
        throw ("{0} Esperado={1}; real={2}." -f $Message, $Expected, $Actual)
    }
}

function Assert-EventsById {
    param(
        [object[]]$StoredEvents,
        [System.Collections.Generic.List[int]]$RegisteredIds,
        [object[]]$Definitions
    )

    $eventsById = @{}
    foreach ($storedEvent in $StoredEvents) {
        $eventsById[[string]$storedEvent.id] = $storedEvent
    }

    Assert-Equals `
        $RegisteredIds.Count `
        $Definitions.Count `
        "El numero de identificadores registrados no coincide."

    for ($index = 0; $index -lt $RegisteredIds.Count; $index++) {
        $eventId = [int]$RegisteredIds[$index]
        $key = [string]$eventId

        if (-not $eventsById.ContainsKey($key)) {
            throw ("No se recupera desde SQLite el evento id={0}." -f $eventId)
        }

        $stored = $eventsById[$key]
        $expected = $Definitions[$index]

        Assert-Equals `
            ([string]$stored.event_type) `
            ([string]$expected.event_type) `
            ("Tipo incorrecto para el evento id={0}." -f $eventId)

        Assert-Equals `
            ([string]$stored.value_text) `
            ([string]$expected.value_text) `
            ("Texto incorrecto para el evento id={0}." -f $eventId)

        Assert-Equals `
            ([string]$stored.source) `
            ([string]$expected.source) `
            ("Origen incorrecto para el evento id={0}." -f $eventId)
    }
}

if (-not (Test-Path $definitionPath)) {
    throw "No se encuentra la definicion de la conversacion: $definitionPath"
}

$definition = Get-Content `
    $definitionPath `
    -Raw `
    -Encoding UTF8 |
    ConvertFrom-Json

Write-Host "PRUEBA 12.4.1 DE CONVERSACION AUTOMATICA Y REGISTRO" -ForegroundColor Cyan
Write-Host (
    "Simula turnos por API; no usa microfono, ASR, Hugging Face ni MuJoCo."
) -ForegroundColor Gray
Write-Host ""

try {
    $health = Invoke-AhootsaJson -Uri "$BaseUrl/health"
} catch {
    throw (
        "Ahootsa Local Server no responde en el puerto 8100. " +
        "Arrancalo con .\3_lanzar_ahootsa_server.ps1."
    )
}

if ([version]$health.version -lt [version]"0.12.2") {
    throw "Se necesita Ahootsa Local Server 0.12.2 o posterior."
}
Write-Host ("Servidor: {0}" -f $health.version) -ForegroundColor Gray

$bootstrap = Invoke-AhootsaJson -Uri "$BaseUrl/panel/api/bootstrap"

if ($bootstrap.services.conversation_app.running) {
    throw "Cierra la Conversation App para no mezclar conversaciones."
}

if ($null -ne $bootstrap.active_session) {
    $activeExternalId = [string]$bootstrap.active_session.user.external_id

    if ($activeExternalId -eq [string]$definition.user.external_id) {
        Write-Host (
            "Cerrando la sesion tecnica anterior {0}..." -f
            $bootstrap.active_session.session_id
        ) -ForegroundColor Yellow

        Invoke-AhootsaJson `
            -Uri "$BaseUrl/panel/api/session/finish" `
            -Method POST `
            -Body @{
                note = "Sesion tecnica anterior cerrada por la prueba 12.4.1."
                decision = "no_decision"
            } |
            Out-Null
    } else {
        throw (
            "Existe una sesion activa real: " +
            $bootstrap.active_session.session_id +
            ". Finalizala desde el panel."
        )
    }
}

$users = @(Invoke-AhootsaJson -Uri "$BaseUrl/users")
$testUser = $users |
    Where-Object {
        $_.external_id -eq $definition.user.external_id
    } |
    Select-Object -First 1

if ($null -eq $testUser) {
    Invoke-AhootsaJson `
        -Uri "$BaseUrl/users" `
        -Method POST `
        -Body @{
            external_id = [string]$definition.user.external_id
            name = [string]$definition.user.name
            preferred_name = [string]$definition.user.preferred_name
            language = [string]$definition.user.language
            notes = [string]$definition.user.notes
        } |
        Out-Null

    Write-Host "Usuario tecnico creado." -ForegroundColor Green
} else {
    Write-Host "Usuario tecnico reutilizado." -ForegroundColor Green
}

Invoke-AhootsaJson `
    -Uri "$BaseUrl/users/$($definition.user.external_id)/profile" `
    -Method PUT `
    -Body @{
        communication_style = "simple"
        speech_speed = "normal"
        response_wait_seconds = 5.0
        preferred_interaction_mode = "mixed"
        preferred_reinforcement = "refuerzo verbal positivo"
        interests = "musica y baile"
        avoid_topics = $null
        accessibility_notes = (
            "Una pregunta por turno y un maximo de dos opciones."
        )
        max_instructions_per_turn = 1
    } |
    Out-Null

$prepared = $null
$finishedOk = $false
$runId = [guid]::NewGuid().ToString()
$eventIds = New-Object System.Collections.Generic.List[int]
$definitions = @($definition.events)

try {
    $prepared = Invoke-AhootsaJson `
        -Uri "$BaseUrl/panel/api/session/prepare" `
        -Method POST `
        -Body @{
            user_external_id = [string]$definition.user.external_id
            activity = [string]$definition.session.activity
            level = [string]$definition.session.level
            started_by = "Prueba automatica 12.4.1"
        }

    Write-Host (
        "Sesion {0} preparada en {1}." -f
        $prepared.session_id,
        $prepared.profile_name
    ) -ForegroundColor Green
    Write-Host ""

    Show-Line -Role "assistant" -Text ([string]$prepared.greeting)

    foreach ($item in $definitions) {
        $metadata = @{}
        foreach ($property in $item.metadata.PSObject.Properties) {
            $metadata[$property.Name] = $property.Value
        }
        $metadata["test_run_id"] = $runId
        $metadata["test_name"] = "conversacion_automatica_12_4_1"

        $created = Invoke-AhootsaJson `
            -Uri "$BaseUrl/sessions/active/events" `
            -Method POST `
            -Body @{
                event_type = [string]$item.event_type
                source = [string]$item.source
                activity = [string]$item.activity
                value_text = [string]$item.value_text
                success = $item.success
                metadata = $metadata
            }

        $eventIds.Add([int]$created.id)

        Show-Line `
            -Role ([string]$metadata["role"]) `
            -Text ([string]$item.value_text)

        if ($PausaMilisegundos -gt 0) {
            Start-Sleep -Milliseconds $PausaMilisegundos
        }
    }

    Write-Host ""
    Write-Host "Verificando los identificadores antes del cierre..." -ForegroundColor Cyan

    $beforeEvents = @(
        Invoke-AhootsaJson `
            -Uri "$BaseUrl/sessions/$($prepared.session_id)/events"
    )

    Assert-EventsById `
        -StoredEvents $beforeEvents `
        -RegisteredIds $eventIds `
        -Definitions $definitions

    $activeSummary = Invoke-AhootsaJson `
        -Uri "$BaseUrl/sessions/active/summary"

    Assert-Equals `
        ([int]$activeSummary.user_responses) `
        ([int]$definition.expected.user_responses) `
        "Respuestas incorrectas."

    Assert-Equals `
        ([int]$activeSummary.correct_responses) `
        ([int]$definition.expected.correct_responses) `
        "Aciertos incorrectos."

    Assert-Equals `
        ([int]$activeSummary.hints_given) `
        ([int]$definition.expected.hints_given) `
        "Pistas incorrectas."

    Assert-Equals `
        ([int]$activeSummary.silences_detected) `
        ([int]$definition.expected.silences_detected) `
        "Silencios incorrectos."

    Write-Host (
        "Los {0} eventos se recuperan por su id." -f $eventIds.Count
    ) -ForegroundColor Green

    $finished = Invoke-AhootsaJson `
        -Uri "$BaseUrl/panel/api/session/finish" `
        -Method POST `
        -Body @{
            note = (
                "Prueba automatica 12.4.1 completada. " +
                "Test run: $runId"
            )
            decision = "no_decision"
        }

    $finishedOk = $true
    Assert-Equals $finished.status "finished" "La sesion no se finalizo."

    Write-Host "Verificando la persistencia despues del cierre..." -ForegroundColor Cyan

    $storedEvents = @(
        Invoke-AhootsaJson `
            -Uri "$BaseUrl/sessions/$($prepared.session_id)/events"
    )

    Assert-EventsById `
        -StoredEvents $storedEvents `
        -RegisteredIds $eventIds `
        -Definitions $definitions

    $storedSummary = Invoke-AhootsaJson `
        -Uri "$BaseUrl/sessions/$($prepared.session_id)/summary"

    Assert-Equals `
        $storedSummary.status `
        "finished" `
        "El resumen final no quedo almacenado."

    Assert-Equals `
        ([int]$storedSummary.activities_completed) `
        1 `
        "La actividad no consta como completada."

    Assert-Equals `
        ([int]$storedSummary.user_responses) `
        3 `
        "No se conservan las tres respuestas."

    $sessionDirectory = [string]$prepared.session_directory
    $reportPath = Join-Path `
        $sessionDirectory `
        "automatic_conversation_verification_12_4_1.json"

    $statusPath = Join-Path $sessionDirectory "session_status.json"
    $summaryPath = Join-Path $sessionDirectory "summary.json"

    if (-not (Test-Path $statusPath)) {
        throw "Falta session_status.json."
    }
    if (-not (Test-Path $summaryPath)) {
        throw "Falta summary.json."
    }

    @{
        test_name = "conversacion_automatica_12_4_1"
        test_run_id = $runId
        verified_at = (Get-Date).ToUniversalTime().ToString("o")
        server_version = [string]$health.version
        session_id = [int]$prepared.session_id
        session_directory = $sessionDirectory
        profile_name = [string]$prepared.profile_name
        registered_event_ids = @($eventIds)
        expected_events = $definitions
        total_session_events = [int]$storedEvents.Count
        summary = $storedSummary
        validation = @{
            events_recovered_by_id = $true
            summary_finished = ($storedSummary.status -eq "finished")
            files_exist = (
                (Test-Path $statusPath) -and
                (Test-Path $summaryPath)
            )
        }
    } |
        ConvertTo-Json -Depth 30 |
        Set-Content $reportPath -Encoding UTF8

    @{
        test_run_id = $runId
        session_id = [int]$prepared.session_id
        report_path = $reportPath
        session_directory = $sessionDirectory
        registered_event_ids = @($eventIds)
        completed_at = (Get-Date).ToUniversalTime().ToString("o")
    } |
        ConvertTo-Json -Depth 20 |
        Set-Content $lastTestPath -Encoding UTF8

    Write-Host ""
    Write-Host (
        "PRUEBA 12.4.1 VALIDADA: CONVERSACION REGISTRADA Y PERSISTENTE."
    ) -ForegroundColor Green
    Write-Host (
        "Sesion {0}; eventos del guion {1}; eventos totales {2}." -f
        $prepared.session_id,
        $eventIds.Count,
        $storedEvents.Count
    ) -ForegroundColor Gray
    Write-Host ("Informe: {0}" -f $reportPath) -ForegroundColor Gray
}
catch {
    if ($null -ne $prepared -and -not $finishedOk) {
        try {
            Invoke-AhootsaJson `
                -Uri "$BaseUrl/panel/api/session/finish" `
                -Method POST `
                -Body @{
                    note = (
                        "Prueba automatica 12.4.1 abortada: " +
                        $_.Exception.Message
                    )
                    decision = "no_decision"
                } |
                Out-Null
        } catch {}
    }
    throw
}
