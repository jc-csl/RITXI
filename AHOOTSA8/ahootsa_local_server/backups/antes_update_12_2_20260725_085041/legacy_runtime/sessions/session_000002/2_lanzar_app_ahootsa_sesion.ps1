$ErrorActionPreference = 'Stop'
$projectRoot = 'D:\RITXI\AHOOTSA8'
$appRoot = 'D:\RITXI\AHOOTSA8\reachy_mini_conversation_app'

Set-Location $projectRoot

$env:REALTIME_TRANSCRIPTION_LANGUAGE = 'es'
$env:HF_REALTIME_CONNECTION_MODE = 'deployed'
$env:REACHY_MINI_CUSTOM_PROFILE = 'ahootsa_session_000002'
$env:REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY = 'D:\RITXI\AHOOTSA8\runtime\generated_profiles'
$env:REACHY_MINI_EXTERNAL_TOOLS_DIRECTORY = 'D:\RITXI\AHOOTSA8\reachy_mini_conversation_app\external_content\external_tools'
$env:AUTOLOAD_EXTERNAL_TOOLS = 'false'
$env:AHOOTSA_SESSION_ID = '2'
$env:AHOOTSA_SESSION_CONTEXT_FILE = 'D:\RITXI\AHOOTSA8\runtime\sessions\session_000002\session_context.json'
$env:AHOOTSA_LOCAL_SERVER_URL = 'http://127.0.0.1:8100'

$activate = Join-Path $appRoot '.venv\Scripts\Activate.ps1'
if (-not (Test-Path $activate)) {
    Write-Host 'No se encuentra el entorno virtual de la app oficial:' -ForegroundColor Red
    Write-Host "  $activate"
    exit 1
}

Set-Location $appRoot
& $activate

Write-Host ''
Write-Host 'Iniciando Reachy Mini Conversation App para Ahootsa' -ForegroundColor Cyan
Write-Host 'Sesión: 2' -ForegroundColor Gray
Write-Host 'Perfil: ahootsa_session_000002' -ForegroundColor Gray
Write-Host 'Contexto: D:\RITXI\AHOOTSA8\runtime\sessions\session_000002\session_context.json' -ForegroundColor Gray
Write-Host ''

reachy-mini-conversation-app --ui
# Añadir --debug manualmente cuando sea necesario.
