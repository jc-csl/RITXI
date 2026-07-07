# DIAGNOSTICAR_6_BOTONES_SDK.ps1
# Comprueba que el backend de Ahootsa 6.1.1 expone endpoints de UI y robot.

param(
    [int]$Port = 8090
)

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "============================================================"
Write-Host "Diagnostico botones SDK Ahootsa 6.1.1"
Write-Host "============================================================"

$base = "http://127.0.0.1:$Port"

Write-Host ""
Write-Host "UI version:"
try {
    Invoke-RestMethod "$base/api/ui/version" -TimeoutSec 5 | ConvertTo-Json -Depth 8
} catch {
    Write-Host "[ERROR] No responde /api/ui/version"
    Write-Host $_.Exception.Message
}

Write-Host ""
Write-Host "Robot status:"
try {
    Invoke-RestMethod "$base/api/robot/status" -TimeoutSec 5 | ConvertTo-Json -Depth 12
} catch {
    Write-Host "[ERROR] No responde /api/robot/status"
    Write-Host $_.Exception.Message
}

Write-Host ""
Write-Host "Robot probe:"
try {
    Invoke-RestMethod -Method Post "$base/api/robot/probe" -TimeoutSec 40 | ConvertTo-Json -Depth 12
} catch {
    Write-Host "[ERROR] Falla /api/robot/probe"
    Write-Host $_.Exception.Message
}

Write-Host ""
Write-Host "Robot accion saludo:"
try {
    Invoke-RestMethod -Method Post "$base/api/robot/action/saludo" -TimeoutSec 40 | ConvertTo-Json -Depth 12
} catch {
    Write-Host "[ERROR] Falla /api/robot/action/saludo"
    Write-Host $_.Exception.Message
}
