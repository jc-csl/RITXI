# DIAGNOSTICAR_5_HUGGINGFACE_CONEXION.ps1
# Ahootsa 5.0.23
# Comprueba conectividad minima de Hugging Face/Gradio y estado local.

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$Urls = @(
    "https://huggingface.co/api/whoami-v2",
    "https://api.gradio.app/gradio-messaging/en"
)

foreach ($Url in $Urls) {
    try {
        $Resp = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec 12 -UseBasicParsing
        $Body = [string]$Resp.Content
        if ($Body.Length -gt 300) { $Body = $Body.Substring(0, 300) + "..." }
        Write-Host "[OK] $Url -> $($Resp.StatusCode) $Body"
    } catch {
        Write-Host "[WARN] $Url -> $($_.Exception.Message)"
    }
}

try {
    $Status = Invoke-RestMethod -Uri "http://127.0.0.1:7860/status" -Method Get -TimeoutSec 5
    Write-Host "local /status =" ($Status | ConvertTo-Json -Depth 8 -Compress)
} catch {
    Write-Host "[WARN] local /status no disponible: $($_.Exception.Message)"
}
