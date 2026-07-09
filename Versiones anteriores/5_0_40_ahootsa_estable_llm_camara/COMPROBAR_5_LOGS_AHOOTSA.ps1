# COMPROBAR_5_LOGS_AHOOTSA.ps1
# Ahootsa 5.0.34: muestra solo logs simples útiles.

$LogRoot = "D:\RITXI\logs"
$env:AHOOTSA_LOG_DIR = $LogRoot
if (-not (Test-Path -LiteralPath $LogRoot)) {
    Write-Host "[ERROR] No existe $LogRoot"
    exit 1
}

Write-Host "LogRoot = $LogRoot"
Write-Host ""
Write-Host "Últimas ejecuciones Ahootsa 5:"
Get-ChildItem -LiteralPath $LogRoot -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match "^ahootsa5_.*_(pantalla\.log|eventos\.jsonl|runtime\.log)$" } |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 15 FullName, LastWriteTime, Length |
    Format-Table -AutoSize

Write-Host ""
Write-Host "Consejo: por ejecución deberían interesar solo 2 o 3 archivos:"
Write-Host " - ahootsa5_<sesion>_pantalla.log"
Write-Host " - ahootsa5_<sesion>_eventos.jsonl"
Write-Host " - ahootsa5_<sesion>_runtime.log"
