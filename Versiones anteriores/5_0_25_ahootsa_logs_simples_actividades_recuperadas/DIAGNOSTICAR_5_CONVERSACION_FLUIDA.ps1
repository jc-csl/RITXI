# DIAGNOSTICAR_5_CONVERSACION_FLUIDA.ps1
# Ahootsa 5.0.25
# Diagnostica escucha/habla. La clave es backend_connected en /status.

param([int]$TailLines = 80)

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$LogRoot = "D:\RITXI\logs"
if (-not (Test-Path -LiteralPath $LogRoot)) { New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null }

Write-Host "============================================================"
Write-Host "Diagnostico conversacion fluida"
Write-Host "============================================================"

function Get-Endpoint {
    param([string]$Url)
    try {
        $Resp = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec 6 -UseBasicParsing
        $Body = [string]$Resp.Content
        if ($Body.Length -gt 800) { $Body = $Body.Substring(0, 800) + "..." }
        Write-Host "[OK] $Url -> $($Resp.StatusCode) $Body"
        return $Resp.Content
    } catch {
        Write-Host "[WARN] $Url -> $($_.Exception.Message)"
        return $null
    }
}

$DaemonBody = Get-Endpoint "http://127.0.0.1:8000/api/daemon/status"
$StatusBody = Get-Endpoint "http://127.0.0.1:7860/status"
$MicBody = Get-Endpoint "http://127.0.0.1:7860/mic"
$EventsBody = Get-Endpoint "http://127.0.0.1:7860/conversation_events"
$VoiceBody = Get-Endpoint "http://127.0.0.1:7860/voices/current"

Write-Host ""
Write-Host "============================================================"
Write-Host "Conclusion"
Write-Host "============================================================"

try {
    $Status = $StatusBody | ConvertFrom-Json
    $Mic = $MicBody | ConvertFrom-Json

    Write-Host "backend_provider =" $Status.backend_provider
    Write-Host "backend_connected =" $Status.backend_connected
    Write-Host "backend_connection_state =" $Status.backend_connection_state
    Write-Host "backend_error =" $Status.backend_error
    Write-Host "mic_muted =" $Mic.muted

    if ($Status.backend_connected -ne $true) {
        Write-Host ""
        Write-Host "[CAUSA PROBABLE] El micro no esta silenciado, pero el backend realtime NO esta conectado."
        Write-Host "Mientras backend_connected=false y state=connecting, no escuchara/respondera de forma real."
        Write-Host ""
        Write-Host "Prueba:"
        Write-Host "powershell -ExecutionPolicy Bypass -File .\ESPERAR_5_BACKEND_REALTIME_LISTO.ps1"
        Write-Host "powershell -ExecutionPolicy Bypass -File .\DIAGNOSTICAR_5_HUGGINGFACE_CONEXION.ps1"
        Write-Host "powershell -ExecutionPolicy Bypass -File .\REINICIAR_5_SESION_CONVERSACION.ps1"
    } else {
        Write-Host "[OK] Backend realtime conectado. Si aun no responde, revisar eventos/log de conversacion."
    }
} catch {
    Write-Host "[WARN] No pude interpretar JSON de /status o /mic."
}

Write-Host ""
Write-Host "Ultimos logs relevantes:"
$Files = Get-ChildItem -LiteralPath $LogRoot -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match "ahootsa_realtime|wait_backend|voice|daemon|LANZAR|events" } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 12

$Files | Select-Object FullName, LastWriteTime, Length | Format-Table -AutoSize

Write-Host ""
Write-Host "Busqueda de errores/realtime:"
$Patterns = @("ERROR","WARNING","backend","connection","disconnect","realtime","microphone","transcription","timeout","Hugging Face","websocket")
foreach ($Pattern in $Patterns) {
    Write-Host ""
    Write-Host "----- $Pattern -----"
    foreach ($F in $Files) {
        try {
            Select-String -LiteralPath $F.FullName -Pattern $Pattern -SimpleMatch -ErrorAction SilentlyContinue |
                Select-Object -Last 8 |
                ForEach-Object { Write-Host "$($F.Name):$($_.LineNumber): $($_.Line)" }
        } catch {}
    }
}
