# PROBAR_IA_LOCAL_AHOOTSA.ps1
# Comprueba que Ollama y el modelo ahootsa-local funcionan y muestra el log ask_ollama.

$ErrorActionPreference = "Continue"

function Header($Text) {
    Write-Host ""
    Write-Host "============================================"
    Write-Host " $Text"
    Write-Host "============================================"
}
function Info($Text) { Write-Host "[INFO] $Text" }
function Err($Text) { Write-Host "[ERROR] $Text" -ForegroundColor Red }

Header "1. Comprobar Ollama"

$ollama = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $ollama) {
    Err "Ollama no está en PATH."
    exit 1
}
Info "Ollama: $($ollama.Source)"
ollama list

Header "2. Probar ahootsa-local:latest por API"

try {
    $body = @{
        model = "ahootsa-local:latest"
        stream = $false
        messages = @(
            @{ role = "user"; content = "Responde en una frase: la IA local Ahootsa funciona correctamente." }
        )
    } | ConvertTo-Json -Depth 5

    $resp = Invoke-RestMethod `
      -Uri "http://127.0.0.1:11434/api/chat" `
      -Method Post `
      -ContentType "application/json" `
      -Body $body

    Write-Host "Respuesta:"
    Write-Host $resp.message.content
} catch {
    Err "Falló la llamada a Ollama."
    Write-Host $_
}

Header "3. Verificar herramientas del perfil"

$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$toolsFiles = Get-ChildItem $DesktopDir -Recurse -Filter "tools.txt" -ErrorAction SilentlyContinue |
    Where-Object { (Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue) -match "ask_ollama" }

$toolsFiles | Select-Object FullName

Header "4. Últimas llamadas ask_ollama"

$log = Join-Path $DesktopDir "ahootsa_logs\ask_ollama.log"
if (Test-Path $log) {
    Get-Content $log -Encoding UTF8 -Tail 20
} else {
    Write-Host "Todavía no existe ask_ollama.log. Se creará cuando la app use ask_ollama."
}

Header "Frase de prueba en la app"

Write-Host "Di exactamente:"
Write-Host "comprueba la IA local con ask_ollama"
