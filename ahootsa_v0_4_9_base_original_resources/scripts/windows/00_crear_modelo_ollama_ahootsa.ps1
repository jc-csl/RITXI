$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Ahootsa v0.4.0 - crear modelo Ollama local" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$ModelDir = "D:\RITXI\ollama_ahootsa"
$ModelFile = Join-Path $ModelDir "Modelfile"
$BaseModel = "hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest"
$AhootsaModel = "ahootsa-local"

if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "No encuentro el comando 'ollama'. Instala Ollama antes de continuar." -ForegroundColor Red
    exit 1
}

New-Item -ItemType Directory -Force -Path $ModelDir | Out-Null

@"
FROM $BaseModel

SYSTEM """
Eres Ahootsa, un asistente robótico en español.

Hablas siempre en español claro.
Eres amable, paciente, positivo y breve.
Usas frases cortas.
Haces una sola pregunta cada vez.
Estás pensado para apoyar conversaciones con personas con discapacidad intelectual.
No inventes información.
Si no entiendes algo, pide una aclaración sencilla.
"""

PARAMETER temperature 0.4
PARAMETER num_ctx 2048
"@ | Set-Content $ModelFile -Encoding UTF8

Write-Host "Modelfile creado en:" $ModelFile -ForegroundColor Green
Write-Host "Descargando/verificando modelo base:" $BaseModel -ForegroundColor Cyan
ollama pull $BaseModel

Write-Host "Creando modelo local:" $AhootsaModel -ForegroundColor Cyan
ollama create $AhootsaModel -f $ModelFile

Write-Host ""
Write-Host "Modelo creado. Prueba manual:" -ForegroundColor Green
Write-Host "  ollama run ahootsa-local" -ForegroundColor Green
Write-Host ""
