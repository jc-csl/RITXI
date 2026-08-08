$ErrorActionPreference = "Stop"

$Root = "D:\RITXI\AHOOTSA_LOCAL"
$SpeechDir = Join-Path $Root "speech_engine"
$Handler = Join-Path $SpeechDir "src\speech_to_speech\TTS\kokoro_handler.py"
$Backup = "$Handler.ahootsa_backup"
$Python = Join-Path $SpeechDir ".venv\Scripts\python.exe"

Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " AHOOTSA - RECUPERAR KOKORO Y DIAGNOSTICAR" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $Backup)) {
    throw "No existe el backup esperado: $Backup"
}

if (-not (Test-Path $Python)) {
    throw "No existe Python del venv: $Python"
}

Write-Host "[1/3] Restaurando kokoro_handler.py desde el backup..." -ForegroundColor Yellow
Copy-Item $Backup $Handler -Force
Write-Host "OK - archivo original restaurado." -ForegroundColor Green
Write-Host ""

Write-Host "[2/3] Comprobando sintaxis Python..." -ForegroundColor Yellow
& $Python -m py_compile $Handler
if ($LASTEXITCODE -ne 0) {
    throw "El archivo restaurado sigue teniendo error de sintaxis."
}
Write-Host "OK - kokoro_handler.py compila correctamente." -ForegroundColor Green
Write-Host ""

Write-Host "[3/3] Mostrando zona real de gestion de voz..." -ForegroundColor Yellow
Write-Host ""

$lines = Get-Content $Handler
$start = 235
$end = [Math]::Min(305, $lines.Count)

for ($i = $start; $i -le $end; $i++) {
    $line = $lines[$i - 1]
    Write-Host ("{0,4}: {1}" -f $i, $line)
}

Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " RECUPERACION TERMINADA" -ForegroundColor Green
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "NO arranques SPEECH SERVE todavia." -ForegroundColor Yellow
Write-Host "Copia y pega aqui las lineas mostradas entre 235 y 305."
Write-Host ""
