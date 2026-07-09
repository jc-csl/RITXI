# DIAGNOSTICAR_5_VOZ_SIN_BOM.ps1
# Comprueba que voice.txt contiene exactamente Sohee sin BOM.

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$SP = Join-Path $DesktopDir "apps_venv\Lib\site-packages"
$Files = @(
    (Join-Path $SP "reachy_mini_conversation_app\profiles\ahootsa_realtime_es\voice.txt"),
    (Join-Path $SP "reachy_mini_conversation_app\profiles\default\voice.txt"),
    (Join-Path $SP "reachy_mini_conversation_app\profiles\starter_profile\voice.txt"),
    (Join-Path $SP "reachy_talk_data\profiles\ahootsa_realtime_es\voice.txt"),
    (Join-Path $SP "reachy_talk_data\profiles\default\voice.txt"),
    (Join-Path $SP "ahootsa_realtime_ollama_desktop_app\profiles\ahootsa_realtime_es\voice.txt"),
    (Join-Path $SP "ahootsa_realtime_ollama_desktop_app\profiles\default\voice.txt")
)

foreach ($F in $Files) {
    $Exists = Test-Path -LiteralPath $F
    $HasBom = $false
    $Value = ""
    $Len = 0
    if ($Exists) {
        $Bytes = [System.IO.File]::ReadAllBytes($F)
        $Len = $Bytes.Length
        $HasBom = ($Bytes.Length -ge 3 -and $Bytes[0] -eq 239 -and $Bytes[1] -eq 187 -and $Bytes[2] -eq 191)
        $Value = [System.IO.File]::ReadAllText($F)
    }
    Write-Host "$F"
    Write-Host "  existe=$Exists length=$Len has_bom=$HasBom value=[$Value]"
}

try {
    $Current = Invoke-WebRequest -Uri "http://127.0.0.1:7860/voices/current" -Method Get -TimeoutSec 5 -UseBasicParsing
    Write-Host "API voices/current =" $Current.Content
    if ($Current.Content -match "ï»¿|\\ufeff") {
        Write-Host "[AVISO] /voices/current contiene BOM. Ejecuta LIMPIAR_5_VOZ_SOHEE_SIN_BOM.ps1 y reinicia app."
    }
} catch {
    Write-Host "API voices/current no disponible: $($_.Exception.Message)"
}
