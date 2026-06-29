$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Ahootsa v0.3.6 - metadata Desktop" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

$MetaDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control\.app_metadata"
New-Item -ItemType Directory -Force -Path $MetaDir | Out-Null

function Write-AppMetadata($FileName, $AppId, $Title, $Emoji, $Description, $ColorFrom, $ColorTo, $HostUrl) {
    $Path = Join-Path $MetaDir $FileName
    $j = [ordered]@{
        _id = "local-$AppId"
        id = "local-user/$AppId"
        sdk = "static"
        likes = 0
        tags = @("static", "reachy_mini", "reachy_mini_python_app", "local")
        private = $false
        author = "Centro San Luis"
        sha = "local-v0.3.6"
        lastModified = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ss.000Z")
        cardData = [ordered]@{
            title = $Title
            emoji = $Emoji
            colorFrom = $ColorFrom
            colorTo = $ColorTo
            sdk = "static"
            pinned = $false
            short_description = $Description
            suggested_storage = "small"
            tags = @("reachy_mini", "reachy_mini_python_app", "local")
        }
        subdomain = "local-$AppId"
        gated = $false
        disabled = $false
        host = $HostUrl
        models = @("ahootsa-local", "hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest")
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
}

Write-AppMetadata `
    -FileName "ahootsa_ollama_local_app.json" `
    -AppId "ahootsa_ollama_local_app" `
    -Title "Ahootsa Ollama Local" `
    -Emoji "🧠" `
    -Description "IA local por texto con Ollama" `
    -ColorFrom "green" `
    -ColorTo "blue" `
    -HostUrl "http://127.0.0.1:7862"

Write-AppMetadata `
    -FileName "ahootsa_reachy_mini_conversation_app.json" `
    -AppId "ahootsa_reachy_mini_conversation_app" `
    -Title "Ahootsa!" `
    -Emoji "🤖" `
    -Description "Conversación en español para Reachy Mini" `
    -ColorFrom "green" `
    -ColorTo "blue" `
    -HostUrl "http://127.0.0.1:7860"

Write-Host ""
Write-Host "Cierra y abre Reachy Mini Desktop App para recargar Applications." -ForegroundColor Green
