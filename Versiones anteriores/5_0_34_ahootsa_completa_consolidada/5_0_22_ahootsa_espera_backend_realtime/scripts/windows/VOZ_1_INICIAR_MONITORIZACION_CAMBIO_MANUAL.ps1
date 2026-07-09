# VOZ_1_INICIAR_MONITORIZACION_CAMBIO_MANUAL.ps1
# Ahootsa 5.0.22
# Crea SOLO un marcador pequeño. No genera snapshot completo del arbol de archivos.
# Uso: ejecuta esto, cambia manualmente la voz a Sohee, y luego ejecuta VOZ_2_ANALIZAR_CAMBIOS_MANUALES.ps1

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$LogRoot = "D:\RITXI\logs"
if (-not (Test-Path -LiteralPath $LogRoot)) {
    New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null
}

$Session = Get-Date -Format "yyyyMMdd_HHmmss"
$Marker = Join-Path $LogRoot ("voice_probe_marker_light_" + $Session + ".json")
$StartUtc = (Get-Date).ToUniversalTime()

$Data = [ordered]@{
    session = $Session
    marker_time_utc = $StartUtc.ToString("o")
    marker_time_local = (Get-Date).ToString("o")
    mode = "light_no_snapshot"
    note = "No se ha generado snapshot grande. VOZ_2 buscara solo archivos modificados despues de este instante y candidatos de voz/configuracion."
    expected_next_step = "Cambia manualmente la voz a Sohee y ejecuta VOZ_2_ANALIZAR_CAMBIOS_MANUALES.ps1"
}

$Data | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 -LiteralPath $Marker

Write-Host ""
Write-Host "============================================================"
Write-Host "Monitorizacion ligera iniciada"
Write-Host "============================================================"
Write-Host "Marker: $Marker"
Write-Host ""
Write-Host "No se ha generado voice_probe_before grande."
Write-Host "Ahora cambia manualmente la voz a Sohee en la interfaz."
Write-Host "Luego ejecuta:"
Write-Host "powershell -ExecutionPolicy Bypass -File .\VOZ_2_ANALIZAR_CAMBIOS_MANUALES.ps1"
