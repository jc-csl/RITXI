$ErrorActionPreference = "Stop"

$Root = "D:\RITXI\AHOOTSA_LOCAL"
$SpeechDir = Join-Path $Root "speech_engine"
$Handler = Join-Path $SpeechDir "src\speech_to_speech\TTS\kokoro_handler.py"
$Backup = "$Handler.ahootsa_backup"
$Python = Join-Path $SpeechDir ".venv\Scripts\python.exe"
$Profile = Join-Path $Root "reachy_mini_conversation_app\profiles\ahootsa_realtime_es\profile.md"

Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " AHOOTSA - COMPATIBILIDAD REACHY <-> KOKORO v3" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $Handler)) {
    throw "No existe: $Handler"
}
if (-not (Test-Path $Backup)) {
    throw "No existe el backup original: $Backup"
}
if (-not (Test-Path $Python)) {
    throw "No existe Python del venv: $Python"
}

Write-Host "[1/4] Leyendo kokoro_handler.py..." -ForegroundColor Yellow
$lines = [System.Collections.Generic.List[string]](Get-Content $Handler)

# Si ya está aplicado, no duplicar.
$alreadyPatched = $false
foreach ($line in $lines) {
    if ($line -match 'AHOOTSA_REACHY_VOICE_COMPAT') {
        $alreadyPatched = $true
        break
    }
}

if ($alreadyPatched) {
    Write-Host "La compatibilidad ya estaba aplicada." -ForegroundColor Green
}
else {
    $targetIndex = -1

    for ($i = 0; $i -lt ($lines.Count - 1); $i++) {
        if (
            $lines[$i] -eq "        if voice:" -and
            $lines[$i + 1] -eq "            self.voice = voice"
        ) {
            $targetIndex = $i
            break
        }
    }

    if ($targetIndex -lt 0) {
        throw "No se han encontrado exactamente las lineas 'if voice:' / 'self.voice = voice'. No se modifica nada."
    }

    Write-Host ("Bloque localizado en lineas {0}-{1}." -f ($targetIndex + 1), ($targetIndex + 2)) -ForegroundColor Green

    # Eliminamos exactamente las dos líneas originales.
    $lines.RemoveAt($targetIndex)
    $lines.RemoveAt($targetIndex)

    $replacement = [string[]]@(
        "        if voice:",
        "            # AHOOTSA_REACHY_VOICE_COMPAT",
        "            # Reachy envia nombres de voz de Qwen3-TTS que no son IDs de Kokoro.",
        "            # Si llega una de esas voces, conservamos la voz Kokoro configurada al arrancar.",
        "            reachy_qwen_voices = {",
        '                "Aiden",',
        '                "Ryan",',
        '                "Dylan",',
        '                "Eric",',
        '                "Ono_Anna",',
        '                "Serena",',
        '                "Sohee",',
        '                "Uncle_Fu",',
        '                "Vivian",',
        "            }",
        "            if voice in reachy_qwen_voices:",
        "                logger.info(",
        '                    "Ignoring Reachy/Qwen voice %r for Kokoro; keeping Kokoro voice %r",',
        "                    voice,",
        "                    self.voice,",
        "                )",
        "            else:",
        "                self.voice = voice"
    )

    for ($j = $replacement.Length - 1; $j -ge 0; $j--) {
        $lines.Insert($targetIndex, $replacement[$j])
    }

    $Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllLines($Handler, $lines, $Utf8NoBom)

    Write-Host "OK - bloque sustituido." -ForegroundColor Green
}

Write-Host ""
Write-Host "[2/4] Comprobando sintaxis Python..." -ForegroundColor Yellow

& $Python -m py_compile $Handler
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR - el parche no compila. Restaurando backup..." -ForegroundColor Red
    Copy-Item $Backup $Handler -Force
    & $Python -m py_compile $Handler
    throw "Parche cancelado. El archivo original ha sido restaurado."
}

Write-Host "OK - sintaxis Python correcta." -ForegroundColor Green

Write-Host ""
Write-Host "[3/4] Dejando una voz valida para la Conversation App..." -ForegroundColor Yellow

if (Test-Path $Profile) {
    $profileText = [System.IO.File]::ReadAllText($Profile)

    if ($profileText -match '(?m)^voice\s*=\s*".*"\s*$') {
        $profileText = [regex]::Replace(
            $profileText,
            '(?m)^voice\s*=\s*".*"\s*$',
            'voice = "Aiden"'
        )
    }
    elseif ($profileText -match '(?m)^schema_version\s*=\s*1\s*$') {
        $profileText = [regex]::Replace(
            $profileText,
            '(?m)^(schema_version\s*=\s*1\s*)$',
            '$1' + "`r`n" + 'voice = "Aiden"',
            1
        )
    }

    $Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($Profile, $profileText, $Utf8NoBom)

    Write-Host 'OK - profile.md: voice = "Aiden" (alias aceptado por Reachy).' -ForegroundColor Green
}
else {
    Write-Host "AVISO - no se encontro profile.md; no se ha modificado." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[4/4] Mostrando el bloque aplicado..." -ForegroundColor Yellow
Write-Host ""

$finalLines = Get-Content $Handler
$marker = Select-String -Path $Handler -Pattern 'AHOOTSA_REACHY_VOICE_COMPAT' | Select-Object -First 1

if (-not $marker) {
    throw "No aparece la marca del parche despues de escribir el archivo."
}

$start = [Math]::Max(1, $marker.LineNumber - 2)
$end = [Math]::Min($finalLines.Count, $marker.LineNumber + 23)

for ($i = $start; $i -le $end; $i++) {
    Write-Host ("{0,4}: {1}" -f $i, $finalLines[$i - 1])
}

Write-Host ""
Write-Host "====================================================" -ForegroundColor Green
Write-Host " VALIDACION OK" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Green
Write-Host ""
Write-Host "NO arranques full." -ForegroundColor Cyan
Write-Host "Ahora arranca solo SPEECH y despues APP."
Write-Host ""
Write-Host "1) powershell -ExecutionPolicy Bypass -File .\AHOOTSA_LOCAL_v8.ps1 -Mode speech"
Write-Host "2) powershell -ExecutionPolicy Bypass -File .\AHOOTSA_LOCAL_v8.ps1 -Mode app"
Write-Host ""
Write-Host "En SPEECH SERVE esperamos ver:" -ForegroundColor Yellow
Write-Host "Ignoring Reachy/Qwen voice 'Aiden' for Kokoro; keeping Kokoro voice 'ef_dora'"
Write-Host ""
Write-Host "Y NO debe volver a aparecer:" -ForegroundColor Yellow
Write-Host "voices/Aiden.pt"
Write-Host ""
