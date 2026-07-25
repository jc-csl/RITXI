param(
    [string]$BaseUrl = "http://127.0.0.1:8100",
    [int]$PausaMilisegundos = 200
)

$ErrorActionPreference = "Stop"
try {
    [Console]::InputEncoding = New-Object System.Text.UTF8Encoding($false)
    [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
} catch {}

$serverRoot = Split-Path $PSScriptRoot -Parent
$definitionPath = Join-Path $serverRoot "config\tests\conversacion_automatica_12_4_2.json"
$dbPath = Join-Path $serverRoot "data\ahootsa.db"
$pythonExe = Join-Path $serverRoot ".venv\Scripts\python.exe"
$verifierPath = Join-Path $PSScriptRoot "verificar_eventos_sqlite_12_4_2.py"
$lastTestPath = Join-Path $serverRoot "data\last_automatic_conversation_test_12_4_2.json"

function Invoke-AhootsaJson {
    param(
        [Parameter(Mandatory = $true)][string]$Uri,
        [ValidateSet("GET", "POST", "PUT")][string]$Method = "GET",
        [object]$Body = $null
    )
    $request = [System.Net.HttpWebRequest]::Create($Uri)
    $request.Method = $Method
    $request.Accept = "application/json"
    $request.Timeout = 15000
    $request.ReadWriteTimeout = 15000
    if ($Method -ne "GET") {
        $json = if ($null -eq $Body) { "{}" } else { $Body | ConvertTo-Json -Depth 30 }
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
        $request.ContentType = "application/json; charset=utf-8"
        $request.ContentLength = $bytes.Length
        $stream = $request.GetRequestStream()
        try { $stream.Write($bytes, 0, $bytes.Length) } finally { $stream.Close() }
    }
    try { $response = $request.GetResponse() }
    catch [System.Net.WebException] {
        $message = $_.Exception.Message
        if ($null -ne $_.Exception.Response) {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream(), [System.Text.Encoding]::UTF8)
            try { $detail = $reader.ReadToEnd() } finally { $reader.Close() }
            if ($detail) { $message = $message + " | " + $detail }
        }
        throw $message
    }
    try {
        $reader = New-Object System.IO.StreamReader($response.GetResponseStream(), [System.Text.Encoding]::UTF8)
        try { $text = $reader.ReadToEnd() } finally { $reader.Close() }
    } finally { $response.Close() }
    if ([string]::IsNullOrWhiteSpace($text)) { return $null }
    return $text | ConvertFrom-Json
}

function Show-Line {
    param([string]$Role, [string]$Text)
    switch ($Role) {
        "assistant" { Write-Host ("Aocha:   {0}" -f $Text) -ForegroundColor Cyan }
        "user"      { Write-Host ("Usuario: {0}" -f $Text) -ForegroundColor Green }
        "system"    { Write-Host ("Sistema: {0}" -f $Text) -ForegroundColor DarkYellow }
        default      { Write-Host ("Evento:  {0}" -f $Text) -ForegroundColor Gray }
    }
}

function Assert-Equal {
    param([object]$Actual, [object]$Expected, [string]$Message)
    if ($Actual -ne $Expected) { throw ("{0} Esperado={1}; real={2}." -f $Message, $Expected, $Actual) }
}

function Test-SqliteEvents {
    param([int]$SessionId, [System.Collections.Generic.List[int]]$Ids)
    $idText = (@($Ids) -join ",")
    $jsonText = & $pythonExe $verifierPath --db $dbPath --session-id $SessionId --ids $idText
    $exitCode = $LASTEXITCODE
    if ([string]::IsNullOrWhiteSpace($jsonText)) { throw "El verificador SQLite no devolvio datos." }
    $verification = $jsonText | ConvertFrom-Json
    if ($exitCode -ne 0 -or -not $verification.ok) {
        throw ("Fallo SQLite. Ausentes={0}; sesion incorrecta={1}." -f ($verification.missing_ids -join ","), (($verification.wrong_session | ConvertTo-Json -Compress)))
    }
    return $verification
}

if (-not (Test-Path $definitionPath)) { throw "No se encuentra $definitionPath" }
if (-not (Test-Path $pythonExe)) { throw "No se encuentra el Python del servidor: $pythonExe" }
if (-not (Test-Path $verifierPath)) { throw "No se encuentra el verificador: $verifierPath" }

$definition = Get-Content $definitionPath -Raw -Encoding UTF8 | ConvertFrom-Json
Write-Host "PRUEBA 12.4.2: CONVERSACION AUTOMATICA Y SQLITE" -ForegroundColor Cyan
Write-Host "Usa rutas de sesion explicitas y comprueba directamente SQLite." -ForegroundColor Gray
Write-Host ""

$health = Invoke-AhootsaJson -Uri "$BaseUrl/health"
Write-Host ("Servidor: {0}" -f $health.version) -ForegroundColor Gray
$bootstrap = Invoke-AhootsaJson -Uri "$BaseUrl/panel/api/bootstrap"
if ($bootstrap.services.conversation_app.running) { throw "Cierra la Conversation App antes de esta prueba." }
if ($null -ne $bootstrap.active_session) {
    $activeUser = [string]$bootstrap.active_session.user.external_id
    if ($activeUser -eq [string]$definition.user.external_id) {
        Write-Host ("Cerrando sesion tecnica anterior {0}..." -f $bootstrap.active_session.session_id) -ForegroundColor Yellow
        Invoke-AhootsaJson -Uri "$BaseUrl/panel/api/session/finish" -Method POST -Body @{ note="Sesion tecnica anterior cerrada por 12.4.2."; decision="no_decision" } | Out-Null
    } else {
        throw ("Existe una sesion real activa: {0}. Finalizala desde el panel." -f $bootstrap.active_session.session_id)
    }
}

$users = @(Invoke-AhootsaJson -Uri "$BaseUrl/users")
$user = $users | Where-Object { $_.external_id -eq $definition.user.external_id } | Select-Object -First 1
if ($null -eq $user) {
    Invoke-AhootsaJson -Uri "$BaseUrl/users" -Method POST -Body @{
        external_id=[string]$definition.user.external_id; name=[string]$definition.user.name;
        preferred_name=[string]$definition.user.preferred_name; language=[string]$definition.user.language;
        notes=[string]$definition.user.notes
    } | Out-Null
    Write-Host "Usuario tecnico creado." -ForegroundColor Green
} else { Write-Host "Usuario tecnico reutilizado." -ForegroundColor Green }

Invoke-AhootsaJson -Uri "$BaseUrl/users/$($definition.user.external_id)/profile" -Method PUT -Body @{
    communication_style="simple"; speech_speed="normal"; response_wait_seconds=5.0;
    preferred_interaction_mode="mixed"; preferred_reinforcement="refuerzo verbal positivo";
    interests="musica y baile"; avoid_topics=$null;
    accessibility_notes="Una pregunta por turno y un maximo de dos opciones.";
    max_instructions_per_turn=1
} | Out-Null

$prepared = $null
$finishedOk = $false
$ids = New-Object System.Collections.Generic.List[int]
$runId = [guid]::NewGuid().ToString()
try {
    $prepared = Invoke-AhootsaJson -Uri "$BaseUrl/panel/api/session/prepare" -Method POST -Body @{
        user_external_id=[string]$definition.user.external_id; activity=[string]$definition.session.activity;
        level=[string]$definition.session.level; started_by="Prueba automatica 12.4.2"
    }
    $sessionId = [int]$prepared.session_id
    Write-Host ("Sesion {0} preparada en {1}." -f $sessionId, $prepared.profile_name) -ForegroundColor Green
    Write-Host ""
    Show-Line -Role "assistant" -Text ([string]$prepared.greeting)

    foreach ($item in @($definition.events)) {
        $metadata = @{}
        foreach ($property in $item.metadata.PSObject.Properties) { $metadata[$property.Name] = $property.Value }
        $metadata["test_run_id"] = $runId
        $metadata["test_name"] = "conversacion_automatica_12_4_2"
        $created = Invoke-AhootsaJson -Uri "$BaseUrl/sessions/$sessionId/events" -Method POST -Body @{
            event_type=[string]$item.event_type; source=[string]$item.source; activity=[string]$item.activity;
            value_text=[string]$item.value_text; success=$item.success; metadata=$metadata
        }
        Assert-Equal ([int]$created.session_id) $sessionId "La API registro el evento en otra sesion."
        if ([int]$created.id -le 0) { throw "La API no devolvio un id de evento valido." }
        $ids.Add([int]$created.id)
        Show-Line -Role ([string]$metadata["role"]) -Text ([string]$item.value_text)
        if ($PausaMilisegundos -gt 0) { Start-Sleep -Milliseconds $PausaMilisegundos }
    }

    Write-Host ""
    Write-Host "Comprobando directamente la base SQLite..." -ForegroundColor Cyan
    $sqliteBefore = Test-SqliteEvents -SessionId $sessionId -Ids $ids
    Assert-Equal ([int]$sqliteBefore.found_count) 9 "SQLite no contiene los nueve eventos."
    Write-Host ("SQLite contiene los 9 eventos en la sesion {0}." -f $sessionId) -ForegroundColor Green

    $activeSummary = Invoke-AhootsaJson -Uri "$BaseUrl/sessions/active/summary"
    Assert-Equal ([int]$activeSummary.user_responses) 3 "Respuestas incorrectas."
    Assert-Equal ([int]$activeSummary.correct_responses) 3 "Aciertos incorrectos."
    Assert-Equal ([int]$activeSummary.hints_given) 1 "Pistas incorrectas."
    Assert-Equal ([int]$activeSummary.silences_detected) 1 "Silencios incorrectos."

    $apiEvents = @(Invoke-AhootsaJson -Uri "$BaseUrl/sessions/$sessionId/events")
    $apiIds = @($apiEvents | ForEach-Object { [int]$_.id })
    $missingApi = @($ids | Where-Object { $apiIds -notcontains [int]$_ })
    if ($missingApi.Count -gt 0) {
        Write-Host ("AVISO: la lista API no muestra los ids: {0}" -f ($missingApi -join ",")) -ForegroundColor Yellow
    } else {
        Write-Host "La lista API tambien devuelve los nueve eventos." -ForegroundColor Green
    }

    $finished = Invoke-AhootsaJson -Uri "$BaseUrl/panel/api/session/finish" -Method POST -Body @{
        note=("Prueba automatica 12.4.2 completada. Test run: {0}" -f $runId); decision="no_decision"
    }
    $finishedOk = $true
    Assert-Equal ([string]$finished.status) "finished" "La sesion no se finalizo."

    Write-Host "Comprobando SQLite despues del cierre..." -ForegroundColor Cyan
    $sqliteAfter = Test-SqliteEvents -SessionId $sessionId -Ids $ids
    Assert-Equal ([int]$sqliteAfter.found_count) 9 "Los eventos no persistieron tras el cierre."
    $storedSummary = Invoke-AhootsaJson -Uri "$BaseUrl/sessions/$sessionId/summary"
    Assert-Equal ([string]$storedSummary.status) "finished" "El resumen no esta finalizado."
    Assert-Equal ([int]$storedSummary.activities_completed) 1 "La actividad no consta como completada."

    $sessionDirectory = [string]$prepared.session_directory
    $reportPath = Join-Path $sessionDirectory "automatic_conversation_verification_12_4_2.json"
    @{
        test_name="conversacion_automatica_12_4_2"; test_run_id=$runId; verified_at=(Get-Date).ToUniversalTime().ToString("o");
        server_version=[string]$health.version; session_id=$sessionId; session_directory=$sessionDirectory;
        registered_event_ids=@($ids); sqlite_before=$sqliteBefore; sqlite_after=$sqliteAfter;
        api_listing_missing_ids=$missingApi; summary=$storedSummary
    } | ConvertTo-Json -Depth 30 | Set-Content $reportPath -Encoding UTF8
    @{
        session_id=$sessionId; registered_event_ids=@($ids); report_path=$reportPath;
        completed_at=(Get-Date).ToUniversalTime().ToString("o")
    } | ConvertTo-Json -Depth 20 | Set-Content $lastTestPath -Encoding UTF8

    Write-Host ""
    Write-Host "PRUEBA 12.4.2 VALIDADA: EVENTOS REGISTRADOS DIRECTAMENTE EN SQLITE." -ForegroundColor Green
    Write-Host ("Sesion {0}; ids {1}." -f $sessionId, ($ids -join ",")) -ForegroundColor Gray
    if ($missingApi.Count -gt 0) { Write-Host "Queda pendiente corregir la ruta API de listado, pero SQLite y el resumen son correctos." -ForegroundColor Yellow }
} catch {
    if ($null -ne $prepared -and -not $finishedOk) {
        try { Invoke-AhootsaJson -Uri "$BaseUrl/panel/api/session/finish" -Method POST -Body @{ note=("Prueba 12.4.2 abortada: {0}" -f $_.Exception.Message); decision="no_decision" } | Out-Null } catch {}
    }
    throw
}
