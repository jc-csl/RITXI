# REINICIAR_5_SESION_CONVERSACION.ps1
# Ahootsa 5.0.23
# Reinicia solo la app Ahootsa/conversacion y espera backend realtime.

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$AppName = "ahootsa_realtime_ollama_app"

Write-Host "Reiniciando sesion de conversacion Ahootsa..."

try {
    Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/apps/stop-current-app" -Method Post -TimeoutSec 10 | Out-Null
    Write-Host "[OK] app actual parada"
} catch {
    Write-Host "[WARN] no pude parar app actual: $($_.Exception.Message)"
}

Start-Sleep -Seconds 4

try {
    Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/apps/start-app/$AppName" -Method Post -TimeoutSec 20 | Out-Null
    Write-Host "[OK] app Ahootsa arrancada"
} catch {
    Write-Host "[ERROR] no pude arrancar app Ahootsa: $($_.Exception.Message)"
    exit 1
}

Start-Sleep -Seconds 8

$VoiceScript = Join-Path $Root "FORZAR_5_VOZ_SOHEE_COMPLETA.ps1"
if (Test-Path -LiteralPath $VoiceScript) {
    powershell -ExecutionPolicy Bypass -File $VoiceScript -WaitSeconds 15
}

$WaitBackendScript = Join-Path $Root "ESPERAR_5_BACKEND_REALTIME_LISTO.ps1"
if (Test-Path -LiteralPath $WaitBackendScript) {
    powershell -ExecutionPolicy Bypass -File $WaitBackendScript -TimeoutSeconds 120 -IntervalSeconds 3
}

Start-Process "http://127.0.0.1:7860"
Write-Host "[OK] sesion reiniciada. Habla solo cuando backend_connected=true."
