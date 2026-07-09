param(
    [string]$BaseUrl = "http://127.0.0.1:7860",
    [string]$Level = "facil",
    [string]$Activity = "1"
)
$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$LogRoot = "D:\RITXI\logs"
New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$Out = Join-Path $LogRoot "AHOOTSA_COMUNICACION_DIAGNOSTICO_7_0_20_$Stamp.log"
function Add-Line([string]$Text = "") { Add-Content -LiteralPath $Out -Encoding UTF8 -Value $Text }
function Test-Endpoint([string]$Name, [string]$Url) {
    Add-Line ""
    Add-Line "===== $Name ====="
    Add-Line "URL: $Url"
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        $res = Invoke-RestMethod -Uri $Url -Method Get -TimeoutSec 20
        $sw.Stop()
        Add-Line "OK: True"
        Add-Line "Elapsed_ms_client: $($sw.ElapsedMilliseconds)"
        $json = $res | ConvertTo-Json -Depth 12
        Add-Line $json
        return @{ ok=$true; elapsed_ms=$sw.ElapsedMilliseconds; response=$res }
    } catch {
        $sw.Stop()
        Add-Line "OK: False"
        Add-Line "Elapsed_ms_client: $($sw.ElapsedMilliseconds)"
        Add-Line "ERROR: $($_.Exception.GetType().FullName): $($_.Exception.Message)"
        return @{ ok=$false; elapsed_ms=$sw.ElapsedMilliseconds; error=$_.Exception.Message }
    }
}
Add-Line "Ahootsa diagnostico comunicacion 7.0.20"
Add-Line "Fecha: $(Get-Date -Format o)"
Add-Line "BaseUrl: $BaseUrl"
Add-Line "Level: $Level"
Add-Line "Activity: $Activity"
Add-Line "Nota: estas pruebas NO llaman a Ollama. Si son rapidas y la voz tarda, el retraso esta en la cadena voz/HF."
Test-Endpoint "Estado Ahootsa" "$BaseUrl/ahootsa/status" | Out-Null
Test-Endpoint "Niveles comunicacion" "$BaseUrl/communication/levels" | Out-Null
Test-Endpoint "Listar actividades" "$BaseUrl/communication/activities?level=$([uri]::EscapeDataString($Level))&limit=6" | Out-Null
Test-Endpoint "Iniciar actividad" "$BaseUrl/communication/start?level=$([uri]::EscapeDataString($Level))&activity=$([uri]::EscapeDataString($Activity))" | Out-Null
Test-Endpoint "Diagnostico completo comunicacion" "$BaseUrl/communication/diagnose?level=$([uri]::EscapeDataString($Level))&activity=$([uri]::EscapeDataString($Activity))" | Out-Null
Add-Line ""
Add-Line "Interpretacion:"
Add-Line "- Si Elapsed_ms_client y duration_ms son bajos, la herramienta local no es el cuello de botella."
Add-Line "- Si por voz tarda cerca de un minuto pero estos endpoints son rapidos, mirar HF Realtime: escucha, transcripcion, seleccion de herramienta o TTS."
Add-Line "- ask_ollama no debe aparecer en esta prueba."
Write-Host "Diagnostico comunicacion guardado en $Out"
