# CREAR_6_MODELO_AHOOTSA_LOCAL.ps1
# Crea ahootsa-local:latest si existe llama3.2:3b.

$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

try {
    $Tags = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 5
    $Names = @($Tags.models | ForEach-Object { $_.name })
    if ($Names -contains "ahootsa-local:latest") {
        Write-Host "[OK] ahootsa-local:latest ya existe."
        exit 0
    }
    if (-not ($Names -contains "llama3.2:3b")) {
        Write-Host "[WARN] No existe llama3.2:3b."
        Write-Host "Puedes descargarlo con:"
        Write-Host "ollama pull llama3.2:3b"
        exit 1
    }
    ollama create ahootsa-local -f (Join-Path $Root "Modelfile.ahootsa-local.example")
    Write-Host "[OK] Modelo creado."
} catch {
    Write-Host "[ERROR] Ollama no responde o no se pudo crear modelo."
    Write-Host $_.Exception.Message
    exit 1
}
