param(
    [string]$BaseUrl = "http://127.0.0.1:8100"
)

$ErrorActionPreference = "Stop"
try {
    [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
} catch {}

$serverRoot = Split-Path $PSScriptRoot -Parent
$lastTestPath = Join-Path `
    $serverRoot `
    "data\last_automatic_conversation_test.json"

function Invoke-AhootsaJson {
    param([Parameter(Mandatory = $true)][string]$Uri)

    $request = [System.Net.HttpWebRequest]::Create($Uri)
    $request.Method = "GET"
    $request.Accept = "application/json"
    $request.Timeout = 15000

    $response = $request.GetResponse()
    try {
        $stream = $response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader(
            $stream,
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

    return $text | ConvertFrom-Json
}

if (-not (Test-Path $lastTestPath)) {
    throw (
        "No existe una prueba anterior. Ejecuta primero " +
        "PROBAR_CONVERSACION_AUTOMATICA_REGISTRO_12_4_1.ps1."
    )
}

$last = Get-Content `
    $lastTestPath `
    -Raw `
    -Encoding UTF8 |
    ConvertFrom-Json

$sessionId = [int]$last.session_id
$registeredIds = @($last.registered_event_ids | ForEach-Object { [int]$_ })

$events = @(
    Invoke-AhootsaJson `
        -Uri "$BaseUrl/sessions/$sessionId/events"
)
$summary = Invoke-AhootsaJson `
    -Uri "$BaseUrl/sessions/$sessionId/summary"

$eventsById = @{}
foreach ($event in $events) {
    $eventsById[[string]$event.id] = $event
}

foreach ($eventId in $registeredIds) {
    if (-not $eventsById.ContainsKey([string]$eventId)) {
        throw ("No persiste el evento id={0}." -f $eventId)
    }
}

if ($summary.status -ne "finished") {
    throw "La sesion persistente no esta finalizada."
}
if ([int]$summary.user_responses -ne 3) {
    throw "No persisten las tres respuestas."
}
if ([int]$summary.correct_responses -ne 3) {
    throw "No persisten los tres aciertos."
}
if ([int]$summary.hints_given -ne 1) {
    throw "No persiste la pista."
}
if ([int]$summary.silences_detected -ne 1) {
    throw "No persiste el silencio."
}
if (-not (Test-Path ([string]$last.report_path))) {
    throw "No persiste el informe JSON."
}

Write-Host "TRANSCRIPCION RECUPERADA DE SQLITE" -ForegroundColor Cyan

foreach ($eventId in $registeredIds) {
    $event = $eventsById[[string]$eventId]
    switch ([string]$event.event_type) {
        "user_response" {
            Write-Host (
                "Usuario: {0}" -f $event.value_text
            ) -ForegroundColor Green
        }
        "robot_message" {
            Write-Host (
                "Aocha:   {0}" -f $event.value_text
            ) -ForegroundColor Cyan
        }
        "silence_detected" {
            Write-Host (
                "Sistema: {0}" -f $event.value_text
            ) -ForegroundColor DarkYellow
        }
        "hint_given" {
            Write-Host (
                "Aocha:   {0}" -f $event.value_text
            ) -ForegroundColor Cyan
        }
        default {
            Write-Host (
                "Evento:  {0}" -f $event.value_text
            ) -ForegroundColor Gray
        }
    }
}

Write-Host ""
Write-Host (
    "PRUEBA 12.4.1 PERSISTENCIA VALIDADA DESPUES DE RELECTURA."
) -ForegroundColor Green
Write-Host (
    "Sesion {0}; eventos recuperados {1}." -f
    $sessionId,
    $registeredIds.Count
) -ForegroundColor Gray
