$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Ahootsa Realtime Ollama v0.4.9 - metadata" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

$MetaDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control\.app_metadata"
New-Item -ItemType Directory -Force -Path $MetaDir | Out-Null

$AppId = "ahootsa_realtime_ollama_app"
$Path = Join-Path $MetaDir "$AppId.json"
$j = [ordered]@{
    _id = "local-$AppId"
    id = "local-user/$AppId"
    sdk = "static"
    likes = 0
    tags = @("static", "reachy_mini", "reachy_mini_python_app", "ollama", "local")
    private = $false
    author = "Centro San Luis"
    sha = "local-v0.4.9"
    lastModified = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.000Z")
    cardData = [ordered]@{
        title = "Ahootsa Realtime Ollama"
        emoji = "🤖"
        colorFrom = "green"
        colorTo = "blue"
        sdk = "static"
        pinned = $false
        short_description = "Base estable: voz realtime, herramientas originales intactas y ask_ollama explícito"
        suggested_storage = "small"
        tags = @("reachy_mini", "reachy_mini_python_app", "ollama", "local")
    }
    subdomain = "local-$AppId"
    gated = $false
    disabled = $false
    host = "http://127.0.0.1:7860"
    models = @("ahootsa-local:latest", "hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest")
    datasets = @("pollen-robotics/reachy-mini-emotions-library")
    runtime = [ordered]@{
        stage = "LOCAL"
        hardware = [ordered]@{ current = $null; requested = $null }
        replicas = [ordered]@{ requested = 1; current = 1 }
    }
    siblings = @()
    createdAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.000Z")
    usedStorage = 0
    downloads = 0
    isPythonApp = $true
}
$j | ConvertTo-Json -Depth 100 | Set-Content $Path -Encoding UTF8
Write-Host "Metadata creado:" $Path -ForegroundColor Green
Write-Host "Cierra y abre Reachy Mini Desktop App para recargar Applications." -ForegroundColor Green
