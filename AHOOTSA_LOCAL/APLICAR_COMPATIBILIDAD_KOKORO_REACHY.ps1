$ErrorActionPreference = "Stop"

$Root = "D:\RITXI\AHOOTSA_LOCAL"
$SpeechDir = Join-Path $Root "speech_engine"
$Handler = Join-Path $SpeechDir "src\speech_to_speech\TTS\kokoro_handler.py"
$Profile = Join-Path $Root "reachy_mini_conversation_app\profiles\ahootsa_realtime_es\profile.md"

Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " AHOOTSA - COMPATIBILIDAD REACHY <-> KOKORO" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $Handler)) {
    throw "No existe: $Handler"
}

# Copia de seguridad solo la primera vez.
$Backup = "$Handler.ahootsa_backup"
if (-not (Test-Path $Backup)) {
    Copy-Item $Handler $Backup
    Write-Host "Backup creado:" -ForegroundColor Yellow
    Write-Host $Backup
}

$content = [System.IO.File]::ReadAllText($Handler)

$old = @'
        if voice:
            self.voice = voice
'@

$new = @'
        if voice:
            # AHOOTSA LOCAL compatibility:
            # Reachy Mini Conversation App sends one of its Qwen3-TTS voice names
            # (Aiden, Serena, Sohee, ...). Those names are not Kokoro voice IDs.
            # Keep the Kokoro CLI/default voice instead of replacing it with an
            # incompatible Reachy voice. Valid Kokoro voice IDs can still be sent.
            reachy_qwen_voices = {
                "Aiden",
                "Ryan",
                "Dylan",
                "Eric",
                "Ono_Anna",
                "Serena",
                "Sohee",
                "Uncle_Fu",
                "Vivian",
            }
            if voice in reachy_qwen_voices:
                logger.info(
                    "Ignoring Reachy/Qwen voice %r for Kokoro; keeping Kokoro voice %r",
                    voice,
                    self.voice,
                )
            else:
                self.voice = voice
'@

if ($content.Contains($new)) {
    Write-Host "La compatibilidad ya estaba aplicada." -ForegroundColor Green
}
elseif ($content.Contains($old)) {
    $content = $content.Replace($old, $new)
    $Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Handler, $content, $Utf8NoBom)
    Write-Host "OK - Kokoro ya ignora las voces Qwen enviadas por Reachy." -ForegroundColor Green
}
else {
    throw "No se ha encontrado el bloque esperado en kokoro_handler.py. No se modifica el archivo."
}

# El perfil debe usar una voz que la Conversation App considere válida.
# Aiden se usa solo como nombre de protocolo; Kokoro mantendrá ef_dora.
if (Test-Path $Profile) {
    $p = [System.IO.File]::ReadAllText($Profile)
    if ($p -match '(?m)^voice\s*=\s*".*"\s*$') {
        $p = [regex]::Replace($p, '(?m)^voice\s*=\s*".*"\s*$', 'voice = "Aiden"')
    }
    $Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Profile, $p, $Utf8NoBom)
    Write-Host "Perfil Reachy dejado en voice = Aiden (alias de protocolo)." -ForegroundColor Green
}

Write-Host ""
Write-Host "IMPORTANTE:" -ForegroundColor Cyan
Write-Host "El servidor speech-to-speech debe reiniciarse para cargar el cambio."
Write-Host ""
Write-Host "Resultado esperado en SPEECH SERVE:" -ForegroundColor Yellow
Write-Host "Ignoring Reachy/Qwen voice 'Aiden' for Kokoro; keeping Kokoro voice 'ef_dora'"
Write-Host ""
Write-Host "Y NO debe volver a aparecer:" -ForegroundColor Yellow
Write-Host "voices/Aiden.pt -> 404"
Write-Host ""
