# RECREAR_MODELO_OLLAMA_AHOOTSA.ps1
# Corrige el Modelfile y recrea el modelo ahootsa-local:latest.

$ErrorActionPreference = "Stop"

function Header($Text) {
    Write-Host ""
    Write-Host "============================================"
    Write-Host " $Text"
    Write-Host "============================================"
}
function Info($Text) { Write-Host "[INFO] $Text" }
function Fail($Text) { Write-Host "[ERROR] $Text" -ForegroundColor Red; exit 1 }

Header "Recrear modelo Ollama Ahootsa"

$BaseModel = "hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest"
$AhootsaModel = "ahootsa-local"
$AhootsaModelLatest = "ahootsa-local:latest"
$ModelDir = Join-Path $env:LOCALAPPDATA "Ahootsa\ollama_ahootsa"
New-Item -ItemType Directory -Force -Path $ModelDir | Out-Null
$Modelfile = Join-Path $ModelDir "Modelfile"

$ollama = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $ollama) {
    Fail "Ollama no está instalado o no está en PATH."
}

Info "Descargando/comprobando modelo base: $BaseModel"
ollama pull $BaseModel
if ($LASTEXITCODE -ne 0) { Fail "ollama pull falló." }

$modelfileContent = @"
FROM $BaseModel

PARAMETER temperature 0.6
PARAMETER top_p 0.9
PARAMETER num_ctx 2048

SYSTEM """
Eres Ahootsa, un asistente educativo amable, claro y paciente.
Respondes siempre en español.
Usas frases cortas.
Das instrucciones sencillas.
Eres positivo y animas al usuario.
No dices que eres ChatGPT.
No controlas directamente el robot.
Si te consultan desde Reachy Mini, ayudas con explicaciones, ideas, actividades y reformulaciones sencillas.
"""
"@

$modelfileContent | Set-Content -Encoding UTF8 $Modelfile

Info "Modelfile escrito en: $Modelfile"
Get-Content $Modelfile

Info "Creando modelo: $AhootsaModelLatest"
ollama create $AhootsaModel -f $Modelfile
if ($LASTEXITCODE -ne 0) { Fail "ollama create falló." }

Info "Comprobando modelos:"
ollama list

Header "Probar API /api/chat"

$body = @{
    model = $AhootsaModelLatest
    stream = $false
    messages = @(
        @{
            role = "user"
            content = "Hola Ahootsa, responde en español con una frase corta."
        }
    )
} | ConvertTo-Json -Depth 5

$resp = Invoke-RestMethod `
  -Uri "http://127.0.0.1:11434/api/chat" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body

Write-Host "Respuesta:"
Write-Host $resp.message.content
