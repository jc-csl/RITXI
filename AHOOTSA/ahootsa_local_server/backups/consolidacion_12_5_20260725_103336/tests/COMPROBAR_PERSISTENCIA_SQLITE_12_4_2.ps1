param([string]$BaseUrl = "http://127.0.0.1:8100")
$ErrorActionPreference = "Stop"
$serverRoot = Split-Path $PSScriptRoot -Parent
$lastPath = Join-Path $serverRoot "data\last_automatic_conversation_test_12_4_2.json"
$dbPath = Join-Path $serverRoot "data\ahootsa.db"
$pythonExe = Join-Path $serverRoot ".venv\Scripts\python.exe"
$verifier = Join-Path $PSScriptRoot "verificar_eventos_sqlite_12_4_2.py"
if (-not (Test-Path $lastPath)) { throw "Ejecuta primero PROBAR_CONVERSACION_AUTOMATICA_SQLITE_12_4_2.ps1." }
$last = Get-Content $lastPath -Raw -Encoding UTF8 | ConvertFrom-Json
$idText = (@($last.registered_event_ids) -join ",")
$jsonText = & $pythonExe $verifier --db $dbPath --session-id ([int]$last.session_id) --ids $idText
if ($LASTEXITCODE -ne 0) { throw ("SQLite no conserva todos los eventos: {0}" -f $jsonText) }
$result = $jsonText | ConvertFrom-Json
if (-not $result.ok -or [int]$result.found_count -ne 9) { throw "La persistencia SQLite no es correcta." }
$summary = Invoke-RestMethod -Uri "$BaseUrl/sessions/$($last.session_id)/summary" -Method Get -TimeoutSec 15
if ($summary.status -ne "finished") { throw "La sesion no persiste como finished." }
Write-Host "PRUEBA 12.4.2 PERSISTENCIA SQLITE VALIDADA TRAS REINICIO." -ForegroundColor Green
Write-Host ("Sesion {0}; eventos {1}; respuestas {2}; aciertos {3}." -f $last.session_id, $result.found_count, $summary.user_responses, $summary.correct_responses) -ForegroundColor Gray
