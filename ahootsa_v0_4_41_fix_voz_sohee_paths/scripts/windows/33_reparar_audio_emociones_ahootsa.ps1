# REPARAR_AUDIO_EMOCIONES_AHOOTSA.ps1
# Repara audio asociado a emociones en Ahootsa.
# Debe ejecutarse con Reachy Mini Desktop cerrado.

$ErrorActionPreference = "Continue"

function Header($Text) {
    Write-Host ""
    Write-Host "============================================"
    Write-Host " $Text"
    Write-Host "============================================"
}
function Info($Text) { Write-Host "[INFO] $Text" }
function Warn($Text) { Write-Host "[AVISO] $Text" -ForegroundColor Yellow }
function Fail($Text) { Write-Host "[ERROR] $Text" -ForegroundColor Red; exit 1 }

Header "Reparar audio de emociones Ahootsa"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$SourceProfile = Join-Path $Root "src\ahootsa_realtime_ollama_desktop_app\profiles\ahootsa_realtime_es"

if (-not (Test-Path $SourceProfile)) {
    Fail "No encuentro perfil fuente: $SourceProfile"
}

Header "Instalar/verificar pygame"
powershell -ExecutionPolicy Bypass -File (Join-Path $Root "INSTALAR_AUDIO_EMOCIONES_PYGAME.ps1")

Header "Configurar variables de audio"
[Environment]::SetEnvironmentVariable("AHOOTSA_EMOTION_AUDIO_BACKEND", "pygame", "User")
[Environment]::SetEnvironmentVariable("AHOOTSA_PYGAME_AUDIO_DRIVERS", "directsound,wasapi,winmm,default", "User")
[Environment]::SetEnvironmentVariable("AHOOTSA_EMOTION_AUDIO_VOLUME", "1.0", "User")
Info "Backend configurado a pygame."

Header "Copiar herramienta de emociones reforzada"

$Targets = @(
    (Join-Path $DesktopDir "user_personalities\ahootsa_realtime_es"),
    (Join-Path $DesktopDir "profiles\ahootsa_realtime_es"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\ahootsa_realtime_es"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_talk_data\profiles\ahootsa_realtime_es")
)

$Files = @(
    "play_emotion.py",
    "play_emotion_with_audio.py",
    "tools.txt",
    "instructions.txt"
)

foreach ($t in $Targets) {
    if (Test-Path $t) {
        foreach ($f in $Files) {
            $src = Join-Path $SourceProfile $f
            if (Test-Path $src) {
                Copy-Item -Force $src (Join-Path $t $f)
            }
        }
        $tools = Join-Path $t "tools.txt"
        if (Test-Path $tools) {
            $raw = Get-Content $tools -Raw -Encoding UTF8
            if ($raw -notmatch "play_emotion_with_audio") {
                Add-Content -Path $tools -Encoding UTF8 -Value "`nplay_emotion_with_audio"
            }
        }
        Info "Reparado: $t"
    }
}

Header "Probar audio directo"
powershell -ExecutionPolicy Bypass -File (Join-Path $Root "test\PROBAR_AUDIO_EMOCION_HERRAMIENTA.ps1")

Header "Final"
Write-Host "Si se ha escuchado audio, cierra y vuelve a abrir Reachy Mini Desktop."
Write-Host "Prueba por voz: saluda con emoción"
Write-Host "Log: $DesktopDir\ahootsa_logs\play_emotion_audio.log"
