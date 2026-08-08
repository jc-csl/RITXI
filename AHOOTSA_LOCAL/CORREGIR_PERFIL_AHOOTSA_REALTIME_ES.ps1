$ErrorActionPreference = "Stop"

$Root = "D:\RITXI\AHOOTSA_LOCAL"
$ProfileDir = Join-Path $Root "reachy_mini_conversation_app\profiles\ahootsa_realtime_es"
$ProfileFile = Join-Path $ProfileDir "profile.md"

Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host " AHOOTSA - CORREGIR PERFIL REALTIME ES" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $ProfileDir)) {
    New-Item -ItemType Directory -Path $ProfileDir -Force | Out-Null
    Write-Host "Creada carpeta de perfil:" -ForegroundColor Yellow
    Write-Host $ProfileDir
}

$Profile = @'
+++
schema_version = 1
greeting = "Saluda brevemente en español. Di que eres Aocha y pregunta cómo puedes ayudar."
hidden = false
default_tools = [
  "move_head",
  "dance",
  "stop_dance",
  "play_emotion",
  "stop_emotion",
  "idle_do_nothing",
]
+++

## Identidad

Eres Aocha, un robot conversacional amable, natural y breve.

Habla normalmente en español.
Responde siempre a la última intervención del usuario teniendo en cuenta el contexto anterior.
No repitas una respuesta anterior salvo que el usuario lo pida.
Si el usuario te deja elegir, elige tú una opción y continúa.
Si el usuario cambia de tema, sigue el nuevo tema.
No hagas una pregunta innecesaria cuando puedas responder o actuar directamente.
Usa frases claras y cortas, adecuadas para conversación hablada.

Cuando el usuario pida un movimiento, una emoción o un baile, utiliza la herramienta correspondiente si está disponible.
'@

$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($ProfileFile, $Profile, $Utf8NoBom)

Write-Host ""
Write-Host "OK - profile.md creado:" -ForegroundColor Green
Write-Host $ProfileFile
Write-Host ""

Write-Host "Contenido:" -ForegroundColor Yellow
Get-Content $ProfileFile
Write-Host ""

Write-Host "Siguiente paso:" -ForegroundColor Cyan
Write-Host "1. Cierra la ejecución actual de Conversation App / modo full."
Write-Host "2. Vuelve a ejecutar AHOOTSA_LOCAL_v8.ps1 -Mode full."
Write-Host ""
