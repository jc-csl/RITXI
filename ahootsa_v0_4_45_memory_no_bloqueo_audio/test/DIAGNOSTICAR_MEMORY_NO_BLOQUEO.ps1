# DIAGNOSTICAR_MEMORY_NO_BLOQUEO.ps1
# Comprueba que Memory no llama internamente a movimiento/audio.

$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$Profile = Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\ahootsa_realtime_es"
$Choose = Join-Path $Profile "choose_memory_cards.py"
$MainLogDir = Join-Path $DesktopDir "ahootsa_logs"

Write-Host "Variables:"
foreach ($name in @("AHOOTSA_RUNTIME_PROFILE_COPY","AHOOTSA_MEMORY_REACTION_ENABLED","AHOOTSA_IDLE_REMINDER_ENABLED")) {
    Write-Host "$name=" ([Environment]::GetEnvironmentVariable($name, "User"))
}

Write-Host ""
Write-Host "choose_memory_cards.py =" (Test-Path $Choose)
if (Test-Path $Choose) {
    $txt = Get-Content -Raw -Encoding UTF8 $Choose
    Write-Host "sin await emotion =" (-not ($txt -match "await _emotion"))
    Write-Host "sin play_emotion interno =" (-not ($txt -match "PlayEmotion"))
    Write-Host "duplicate_ignored =" ($txt -match "duplicate_ignored")
    Write-Host "visual_only_no_blocking_audio =" ($txt -match "visual_only_no_blocking_audio")
}

Write-Host ""
Write-Host "Puerto 7870:"
try {
    Get-NetTCPConnection -LocalPort 7870 -State Listen -ErrorAction SilentlyContinue |
        Format-Table -AutoSize
} catch {
    Write-Host "No se pudo consultar Get-NetTCPConnection."
}

Write-Host ""
Write-Host "Si sin await emotion=True y sin play_emotion interno=True, Memory no debería bloquear la escucha por audio/movimiento."
