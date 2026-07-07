# INSTALAR_5_COMPLETO_SOBRE_CONVERSATION_APP.ps1
# Ahootsa 5.0.23 - instalacion completa sobre reachy_mini_conversation_app.
# ask_ollama queda como actividad opcional, no como cerebro principal.

$ErrorActionPreference = "Continue"

function Start-AhootsaLog {
    param([string]$Name)
    $script:LogRoot = "D:\RITXI\logs"
    if (-not (Test-Path -LiteralPath $script:LogRoot)) { New-Item -ItemType Directory -Force -Path $script:LogRoot | Out-Null }
    if (-not $env:AHOOTSA_SESSION_ID) { $env:AHOOTSA_SESSION_ID = Get-Date -Format "yyyyMMdd_HHmmss" }
    $env:AHOOTSA_LOG_DIR = $script:LogRoot
    $script:PsLog = Join-Path $script:LogRoot ("ahootsa_ps_" + $Name + "_" + $env:AHOOTSA_SESSION_ID + ".log")
    $script:JsonLog = Join-Path $script:LogRoot ("ahootsa_ps_events_" + $env:AHOOTSA_SESSION_ID + ".jsonl")
    try { Start-Transcript -LiteralPath $script:PsLog -Append | Out-Null } catch {}
    Write-AhootsaEvent "ps.start" @{script=$Name; pwd=(Get-Location).Path; user=$env:USERNAME}
}
function Write-AhootsaEvent {
    param([string]$Event, [hashtable]$Data=@{})
    if (-not $script:JsonLog) {
        $script:LogRoot="D:\RITXI\logs"; if (-not (Test-Path $script:LogRoot)) { New-Item -ItemType Directory -Force -Path $script:LogRoot | Out-Null }
        if (-not $env:AHOOTSA_SESSION_ID) { $env:AHOOTSA_SESSION_ID = Get-Date -Format "yyyyMMdd_HHmmss" }
        $script:JsonLog=Join-Path $script:LogRoot ("ahootsa_ps_events_" + $env:AHOOTSA_SESSION_ID + ".jsonl")
    }
    $o=[ordered]@{ts=(Get-Date).ToString("o"); event=$Event; session_id=$env:AHOOTSA_SESSION_ID; pid=$PID}
    foreach($k in $Data.Keys){$o[$k]=$Data[$k]}
    try { ($o|ConvertTo-Json -Depth 12 -Compress) | Add-Content -Encoding UTF8 -LiteralPath $script:JsonLog } catch {}
}
function Stop-AhootsaLog {
    param([string]$Name)
    Write-AhootsaEvent "ps.end" @{script=$Name}
    try { Stop-Transcript | Out-Null } catch {}
}

Start-AhootsaLog "INSTALAR_5_COMPLETO_SOBRE_CONVERSATION_APP"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$env:AHOOTSA_LOG_DIR = "D:\RITXI\logs"
$env:AHOOTSA_VOICE = "Sohee"
$env:VOICE = "Sohee"
$env:REACHY_MINI_VOICE = "Sohee"
$env:OPENAI_REALTIME_VOICE = "Sohee"
$env:REALTIME_VOICE = "Sohee"
$env:TTS_VOICE = "Sohee"
$env:AUDIO_VOICE = "Sohee"
# voice.env.forced.510

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProfileName = "ahootsa_realtime_es"
$SourceProfile = Join-Path $Root "src\ahootsa_realtime_ollama_desktop_app\profiles\$ProfileName"
$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$SitePackages = Join-Path $DesktopDir "apps_venv\Lib\site-packages"
$ConversationPkg = Join-Path $SitePackages "reachy_mini_conversation_app"
$TalkDataPkg = Join-Path $SitePackages "reachy_talk_data"
$AhootsaPkg = Join-Path $SitePackages "ahootsa_realtime_ollama_desktop_app"

function Ensure-Dir([string]$P) {
    if (-not (Test-Path -LiteralPath $P)) { New-Item -ItemType Directory -Force -Path $P | Out-Null }
}

function Copy-Profile([string]$Target) {
    Ensure-Dir $Target
    Copy-Item -Path (Join-Path $SourceProfile "*") -Destination $Target -Recurse -Force
    "Hola, soy Ahootsa. Estoy lista para ayudarte. Que quieres hacer?" | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $Target "greeting.txt")
    "Sohee" | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $Target "voice.txt")
    "Ahootsa 5.0.23 full install $(Get-Date -Format o)" | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $Target ".ahootsa_5_0_9_full_install.txt")

    $Instructions = Join-Path $Target "instructions.txt"
    if (-not (Test-Path -LiteralPath $Instructions)) { "" | Set-Content -Encoding UTF8 -LiteralPath $Instructions }
    $Txt = Get-Content -Raw -Encoding UTF8 -LiteralPath $Instructions
    if ($Txt -notmatch "MODO CONVERSACIONAL 5.0.23") {
        Add-Content -Encoding UTF8 -LiteralPath $Instructions -Value @(
            "",
            "## MODO CONVERSACIONAL 5.0.23 - APP OFICIAL COMPLETA",
            "Tu nombre es Ahootsa.",
            "No eres Reachy Mini.",
            "Habla siempre en castellano.",
            "Conversacion normal: responde tu directamente como Ahootsa.",
            "No uses ask_ollama salvo que el usuario pida especificamente IA local u Ollama.",
            "Si no entiendes el audio, pide repetir de forma sencilla.",
            "Si empiezas una actividad, da una instruccion clara y una pregunta final sencilla."
        )
    }
    Write-Host "[OK] perfil -> $Target"
}

Write-Host ""
Write-Host "============================================================"
Write-Host "Ahootsa 5.0.23 - instalacion completa sobre conversation app"
Write-Host "============================================================"

if (-not (Test-Path -LiteralPath $SourceProfile)) {
    Write-Host "[ERROR] No existe SourceProfile: $SourceProfile"
    exit 1
}

$Targets = @(
    (Join-Path $DesktopDir "user_personalities\$ProfileName"),
    (Join-Path $DesktopDir "profiles\$ProfileName"),
    (Join-Path $ConversationPkg "profiles\$ProfileName"),
    (Join-Path $ConversationPkg "profiles\default"),
    (Join-Path $ConversationPkg "profiles\starter_profile"),
    (Join-Path $ConversationPkg "external_content\external_profiles\$ProfileName"),
    (Join-Path $ConversationPkg "external_content\external_profiles\default"),
    (Join-Path $ConversationPkg "external_content\external_profiles\starter_profile"),
    (Join-Path $TalkDataPkg "profiles\$ProfileName"),
    (Join-Path $TalkDataPkg "profiles\default"),
    (Join-Path $TalkDataPkg "profiles\starter_profile"),
    (Join-Path $TalkDataPkg "external_content\external_profiles\$ProfileName"),
    (Join-Path $TalkDataPkg "external_content\external_profiles\default"),
    (Join-Path $TalkDataPkg "external_content\external_profiles\starter_profile")
)

foreach ($T in ($Targets | Select-Object -Unique)) { Copy-Profile $T }

Write-Host ""
Write-Host "Copiando herramientas Python a ubicaciones compartidas..."
$ToolFiles = Get-ChildItem -LiteralPath $SourceProfile -Filter "*.py" -File
$ToolTargets = @(
    (Join-Path $ConversationPkg "tools"),
    (Join-Path $ConversationPkg "external_content\external_tools"),
    (Join-Path $TalkDataPkg "tools"),
    (Join-Path $TalkDataPkg "external_content\external_tools")
)
foreach ($Target in $ToolTargets) {
    Ensure-Dir $Target
    foreach ($Tool in $ToolFiles) { Copy-Item -LiteralPath $Tool.FullName -Destination (Join-Path $Target $Tool.Name) -Force }
    Write-Host "[OK] tools -> $Target"
}

Write-Host ""
Write-Host "Creando .env..."
$EnvLines = @(
    "REACHY_MINI_CUSTOM_PROFILE=ahootsa_realtime_es",
    "REACHY_MINI_PROFILE=ahootsa_realtime_es",
    "REACHY_MINI_PERSONALITY=ahootsa_realtime_es",
    "REACHY_MINI_USER_PERSONALITY=ahootsa_realtime_es",
    "AHOOTSA_FORCE_DEFAULT_PROFILE=1",
    "AHOOTSA_RUNTIME_PROFILE_COPY=1",
        "AHOOTSA_LOG_DIR=D:\RITXI\logs",
    "AHOOTSA_NAME=Ahootsa",
    "ASSISTANT_NAME=Ahootsa",
    "ROBOT_NAME=Ahootsa",
    "PROJECT_NAME=Ahootsa",
    "AHOOTSA_LANGUAGE=es",
    "REACHY_MINI_LANGUAGE=es",
    "APP_LANGUAGE=es",
    "OUTPUT_LANGUAGE=es",
    "SYSTEM_LANGUAGE=es",
    "REALTIME_TRANSCRIPTION_LANGUAGE=es",
    "AHOOTSA_VOICE=Sohee",
    "OPENAI_REALTIME_VOICE=Sohee",
    "REACHY_MINI_VOICE=Sohee",
    "VOICE=Sohee",
    "OLLAMA_BASE_URL=http://127.0.0.1:11434",
    "OLLAMA_MODEL=ahootsa-local:latest",
    "AHOOTSA_OLLAMA_TIMEOUT_SECONDS=45",
    "AHOOTSA_GREETING=Hola, soy Ahootsa. Estoy lista para ayudarte. Que quieres hacer?",
    "SYSTEM_PROMPT_EXTRA=Tu nombre es Ahootsa. No eres Reachy Mini. Habla siempre en castellano. ask_ollama es solo una actividad opcional de IA local."
)

$EnvTargets = @(
    (Join-Path $Root ".env"),
    (Join-Path $DesktopDir ".env"),
    (Join-Path $ConversationPkg ".env"),
    (Join-Path $TalkDataPkg ".env"),
    (Join-Path $AhootsaPkg ".env")
)
foreach ($E in ($EnvTargets | Select-Object -Unique)) {
    Ensure-Dir (Split-Path -Parent $E)
    $EnvLines | Set-Content -Encoding UTF8 -LiteralPath $E
    Write-Host "[OK] env -> $E"
}

Write-Host ""
Write-Host "Limpiando variable de 5.0.8 si existia..."
[Environment]::SetEnvironmentVariable("AHOOTSA_USE_OLLAMA_AS_BRAIN", $null, "User")
Remove-Item -Path "Env:AHOOTSA_USE_OLLAMA_AS_BRAIN" -ErrorAction SilentlyContinue
[Environment]::SetEnvironmentVariable("AHOOTSA_OLLAMA_TIMEOUT_SECONDS", "45", "User")
$env:AHOOTSA_OLLAMA_TIMEOUT_SECONDS = "45"

Write-Host ""
Write-Host "Instalacion completa finalizada."

Stop-AhootsaLog "INSTALAR_5_COMPLETO_SOBRE_CONVERSATION_APP"

Write-Host "Forzando voz Sohee completa..."
powershell -ExecutionPolicy Bypass -File (Join-Path $Root "FORZAR_5_VOZ_SOHEE_COMPLETA.ps1") -NoApi

Write-Host "Limpiando voz Sohee sin BOM..."
powershell -ExecutionPolicy Bypass -File (Join-Path $Root "LIMPIAR_5_VOZ_SOHEE_SIN_BOM.ps1")
