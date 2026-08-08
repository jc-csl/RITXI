$ErrorActionPreference = "Stop"

$Root = "D:\RITXI\AHOOTSA_LOCAL"
$SpeechDir = Join-Path $Root "speech_engine"
$Handler = Join-Path $SpeechDir "src\speech_to_speech\TTS\kokoro_handler.py"
$Profile = Join-Path $Root "reachy_mini_conversation_app\profiles\ahootsa_realtime_es\profile.md"

Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " AHOOTSA - COMPATIBILIDAD REACHY <-> KOKORO v2" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $Handler)) {
    throw "No existe: $Handler"
}

# Backup único del original.
$Backup = "$Handler.ahootsa_backup"
if (-not (Test-Path $Backup)) {
    Copy-Item $Handler $Backup -Force
    Write-Host "Backup creado:" -ForegroundColor Yellow
    Write-Host $Backup
} else {
    Write-Host "Backup ya existente:" -ForegroundColor DarkGray
    Write-Host $Backup
}

$content = [System.IO.File]::ReadAllText($Handler)

# Si ya está aplicado, no tocar otra vez.
if ($content -match 'AHOOTSA_REACHY_VOICE_COMPAT') {
    Write-Host ""
    Write-Host "La compatibilidad ya está aplicada." -ForegroundColor Green
}
else {
    # En la versión actual de speech-to-speech el bloque es:
    #
    #   if voice:
    #       self.voice = voice
    #
    # Usamos regex tolerante a CRLF/LF y espacios.
    $pattern = '(?m)^(?<indent>[ \t]*)if voice:\s*\r?\n(?<inner>[ \t]+)self\.voice = voice\s*$'

    $match = [regex]::Match($content, $pattern)

    if (-not $match.Success) {
        Write-Host ""
        Write-Host "No se encontró el bloque automático." -ForegroundColor Red
        Write-Host "Buscando las líneas relacionadas con 'voice' para diagnóstico:" -ForegroundColor Yellow
        Select-String -Path $Handler -Pattern 'if voice|self\.voice = voice|runtime_config|audio_output' |
            ForEach-Object {
                Write-Host ("{0}: {1}" -f $_.LineNumber, $_.Line)
            }
        throw "No se ha modificado kokoro_handler.py."
    }

    $indent = $match.Groups["indent"].Value
    $inner = $match.Groups["inner"].Value
    $inner2 = $inner + "    "
    $inner3 = $inner2 + "    "

    $replacement = @(
        $indent + "if voice:",
        $inner + "# AHOOTSA_REACHY_VOICE_COMPAT",
        $inner + "# Reachy Conversation App envía nombres de voz de Qwen3-TTS.",
        $inner + "# Kokoro usa IDs distintos; ignoramos esas voces y mantenemos",
        $inner + "# la voz Kokoro configurada por CLI (ef_dora).",
        $inner + "reachy_qwen_voices = {",
        $inner2 + '"Aiden",',
        $inner2 + '"Ryan",',
        $inner2 + '"Dylan",',
        $inner2 + '"Eric",',
        $inner2 + '"Ono_Anna",',
        $inner2 + '"Serena",',
        $inner2 + '"Sohee",',
        $inner2 + '"Uncle_Fu",',
        $inner2 + '"Vivian",',
        $inner + "}",
        $inner + "if voice in reachy_qwen_voices:",
        $inner2 + "logger.info(",
        $inner3 + '"Ignoring Reachy/Qwen voice %r for Kokoro; keeping Kokoro voice %r",',
        $inner3 + "voice,",
        $inner3 + "self.voice,",
        $inner2 + ")",
        $inner + "else:",
        $inner2 + "self.voice = voice"
    ) -join "`r`n"

    $newContent = [regex]::Replace($content, $pattern, [System.Text.RegularExpressions.MatchEvaluator]{
        param($m)
        return $replacement
    }, 1)

    $Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Handler, $newContent, $Utf8NoBom)

    Write-Host ""
    Write-Host "OK - compatibilidad aplicada a kokoro_handler.py" -ForegroundColor Green
}

# Mantener en el perfil una voz aceptada por Reachy.
# Para Kokoro actúa solo como voz de protocolo; el patch conserva ef_dora.
if (Test-Path $Profile) {
    $p = [System.IO.File]::ReadAllText($Profile)

    if ($p -match '(?m)^voice\s*=\s*".*"\s*$') {
        $p = [regex]::Replace(
            $p,
            '(?m)^voice\s*=\s*".*"\s*$',
            'voice = "Aiden"'
        )
    }
    elseif ($p -match '(?m)^schema_version\s*=\s*1\s*$') {
        $p = [regex]::Replace(
            $p,
            '(?m)^(schema_version\s*=\s*1\s*)$',
            '$1' + "`r`n" + 'voice = "Aiden"',
            1
        )
    }

    $Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Profile, $p, $Utf8NoBom)

    Write-Host "Perfil Reachy: voice = Aiden (solo nombre de protocolo)." -ForegroundColor Green
}

# Validación del parche.
$check = [System.IO.File]::ReadAllText($Handler)

if ($check -notmatch 'AHOOTSA_REACHY_VOICE_COMPAT') {
    throw "La validación ha fallado: no aparece la marca del parche."
}

Write-Host ""
Write-Host "VALIDACION OK" -ForegroundColor Green
Write-Host ""

Select-String -Path $Handler -Pattern 'AHOOTSA_REACHY_VOICE_COMPAT|Ignoring Reachy/Qwen voice|self\.voice = voice' |
    ForEach-Object {
        Write-Host ("{0}: {1}" -f $_.LineNumber, $_.Line)
    }

Write-Host ""
Write-Host "SIGUIENTE PASO" -ForegroundColor Cyan
Write-Host "1. Cierra SPEECH SERVE y CONVERSATION APP si siguen abiertos."
Write-Host "2. Arranca de nuevo SPEECH SERVE."
Write-Host "3. Arranca de nuevo CONVERSATION APP."
Write-Host ""
Write-Host "Esperado en SPEECH SERVE:" -ForegroundColor Yellow
Write-Host "Ignoring Reachy/Qwen voice 'Aiden' for Kokoro; keeping Kokoro voice 'ef_dora'"
Write-Host ""
Write-Host "NO debe aparecer:" -ForegroundColor Yellow
Write-Host "voices/Aiden.pt -> 404"
Write-Host ""
