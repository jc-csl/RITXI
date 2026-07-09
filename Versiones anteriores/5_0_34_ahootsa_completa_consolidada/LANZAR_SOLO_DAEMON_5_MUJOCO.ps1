# LANZAR_SOLO_DAEMON_5_MUJOCO.ps1
# Lanza solo el daemon MuJoCo con rutas entrecomilladas correctamente.

param(
    [int]$Port = 8000,
    [string]$HostAddress = "127.0.0.1",
    [switch]$Headless,
    [switch]$NoMedia
)

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$daemon = Join-Path $env:LOCALAPPDATA "Reachy Mini Control\apps_venv\Scripts\reachy-mini-daemon.exe"
$logDir = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "logs"
if (-not (Test-Path -LiteralPath $logDir)) { New-Item -ItemType Directory -Force -Path $logDir | Out-Null }
$logFile = Join-Path $logDir ("ahootsa_5_mujoco_daemon_manual_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".log")

$argsList = @(
    "--sim",
    "--fastapi-host", $HostAddress,
    "--fastapi-port", "$Port",
    "--no-goto-sleep-on-stop",
    "--dataset-update-interval", "0",
    "--no-preload-datasets",
    "--log-file", $logFile
)
if ($Headless) { $argsList += "--headless" }
if ($NoMedia) { $argsList += "--no-media" }

Write-Host "Daemon: $daemon"
Write-Host "Log: $logFile"
Write-Host "No cierres esta ventana mientras uses MuJoCo."
& $daemon @argsList
