# LANZAR_6_FALLBACK_LOCAL.ps1
# Ahootsa 6.0.0 fallback local

param(
    [int]$Port = 8090,
    [switch]$NoOpenBrowser
)

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonExe = Join-Path $Root ".venv\Scripts\python.exe"
$LogRoot = "D:\RITXI\logs"
if (-not (Test-Path $LogRoot)) { New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null }

$env:AHOOTSA_LOG_DIR = $LogRoot
$env:OLLAMA_MODEL = if ($env:OLLAMA_MODEL) { $env:OLLAMA_MODEL } else { "ahootsa-local:latest" }
$env:OLLAMA_BASE_URL = if ($env:OLLAMA_BASE_URL) { $env:OLLAMA_BASE_URL } else { "http://127.0.0.1:11434" }
$env:PYTHONPATH = $Root

if (-not (Test-Path $PythonExe)) {
    Write-Host "[ERROR] No existe .venv. Ejecuta primero INSTALAR_6_FALLBACK_LOCAL.ps1"
    exit 1
}

Write-Host "============================================================"
Write-Host "Ahootsa 6.0.0 - fallback local Ollama + audio navegador"
Write-Host "============================================================"
Write-Host "Root:   $Root"
Write-Host "Port:   $Port"
Write-Host "Ollama: $env:OLLAMA_BASE_URL"
Write-Host "Model:  $env:OLLAMA_MODEL"
Write-Host "Logs:   $LogRoot"

# Si hay una instancia previa de este mismo servidor, no la matamos por fuerza.
try {
    $Probe = Invoke-WebRequest -Uri "http://127.0.0.1:$Port/api/status" -TimeoutSec 2 -UseBasicParsing
    Write-Host "[OK] Ahootsa 6 ya esta respondiendo en http://127.0.0.1:$Port"
    if (-not $NoOpenBrowser) { Start-Process "http://127.0.0.1:$Port" }
    exit 0
} catch {}

$ArgsList = @("-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", [string]$Port)
$Log = Join-Path $LogRoot ("ahootsa6_server_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".log")

$Proc = Start-Process -FilePath $PythonExe -ArgumentList $ArgsList -WorkingDirectory $Root -PassThru -NoNewWindow `
    -RedirectStandardOutput $Log -RedirectStandardError ($Log + ".stderr.log")

Write-Host "Proceso servidor PID: $($Proc.Id)"
Write-Host "Log: $Log"

for ($i=1; $i -le 30; $i++) {
    Start-Sleep -Seconds 1
    try {
        $Status = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/api/status" -TimeoutSec 2
        Write-Host "[OK] Servidor listo: http://127.0.0.1:$Port"
        Write-Host "Ollama OK: $($Status.ollama.ok)"
        Write-Host "Modelo disponible: $($Status.ollama.model_available)"
        if (-not $NoOpenBrowser) { Start-Process "http://127.0.0.1:$Port" }
        exit 0
    } catch {
        Write-Host "Esperando servidor... $i"
    }
}

Write-Host "[ERROR] El servidor no ha respondido."
Write-Host "Revisa: $Log"
exit 1
