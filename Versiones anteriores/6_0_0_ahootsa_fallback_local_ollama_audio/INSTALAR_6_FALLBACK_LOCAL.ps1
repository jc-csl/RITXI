# INSTALAR_6_FALLBACK_LOCAL.ps1
# Ahootsa 6.0.0 fallback local

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Venv = Join-Path $Root ".venv"
$PythonExe = Join-Path $Venv "Scripts\python.exe"

Write-Host "============================================================"
Write-Host "Instalando Ahootsa 6.0.0 fallback local"
Write-Host "============================================================"
Write-Host "Root: $Root"

if (-not (Test-Path $Venv)) {
    $Py = $null
    try { $Py = (Get-Command py -ErrorAction Stop).Source } catch {}
    if ($Py) {
        & py -3 -m venv $Venv
    } else {
        & python -m venv $Venv
    }
}

& $PythonExe -m pip install --upgrade pip
& $PythonExe -m pip install -r (Join-Path $Root "requirements.txt")

$LogRoot = "D:\RITXI\logs"
if (-not (Test-Path $LogRoot)) { New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null }
[Environment]::SetEnvironmentVariable("AHOOTSA_LOG_DIR", $LogRoot, "User")
[Environment]::SetEnvironmentVariable("OLLAMA_MODEL", "ahootsa-local:latest", "User")
[Environment]::SetEnvironmentVariable("OLLAMA_BASE_URL", "http://127.0.0.1:11434", "User")

Write-Host ""
Write-Host "Comprobando Ollama..."
try {
    $Tags = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -Method Get -TimeoutSec 5
    $Names = @($Tags.models | ForEach-Object { $_.name })
    Write-Host "[OK] Ollama responde."
    if ($Names -contains "ahootsa-local:latest") {
        Write-Host "[OK] Modelo ahootsa-local:latest encontrado."
    } else {
        Write-Host "[WARN] Modelo ahootsa-local:latest no encontrado."
        Write-Host "Modelos disponibles:"
        $Names | ForEach-Object { Write-Host " - $_" }
        Write-Host ""
        Write-Host "Si tienes llama3.2:3b, puedes crear el modelo:"
        Write-Host "ollama create ahootsa-local -f .\Modelfile.ahootsa-local.example"
    }
} catch {
    Write-Host "[WARN] Ollama no responde en http://127.0.0.1:11434"
    Write-Host "Abre Ollama antes de lanzar Ahootsa 6."
}

Write-Host ""
Write-Host "Instalacion terminada."
Write-Host "Lanza con:"
Write-Host "powershell -ExecutionPolicy Bypass -File .\LANZAR_6_FALLBACK_LOCAL.ps1"
