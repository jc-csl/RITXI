param(
    [string]$AppRoot = "D:\RITXI\5_0_25_ahootsa_logs_simples_actividades_recuperadas"
)

$ErrorActionPreference = "Continue"
$Launch = Join-Path $AppRoot "LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1"
Write-Host "============================================================"
Write-Host "Ahootsa 5.0.32 - diagnostico lanzador"
Write-Host "============================================================"
Write-Host "Launch: $Launch"

if (-not (Test-Path -LiteralPath $Launch)) {
    Write-Host "No existe el lanzador."
    exit 1
}

Write-Host ""
Write-Host "Primeras 80 lineas del lanzador:"
$i = 0
Get-Content -LiteralPath $Launch -TotalCount 80 -ErrorAction SilentlyContinue | ForEach-Object {
    $i += 1
    "{0,4}: {1}" -f $i, $_
}

Write-Host ""
Write-Host "Backups recientes del lanzador:"
Get-ChildItem -LiteralPath $AppRoot -Filter "LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1.bak_*" -File -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 10 Name, LastWriteTime, Length |
    Format-Table -AutoSize
