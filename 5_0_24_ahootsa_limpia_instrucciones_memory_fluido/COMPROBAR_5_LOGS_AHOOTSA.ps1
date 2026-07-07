# COMPROBAR_5_LOGS_AHOOTSA.ps1
$ErrorActionPreference = "Continue"
$LogRoot = "D:\RITXI\logs"
$env:AHOOTSA_LOG_DIR = $LogRoot
[Environment]::SetEnvironmentVariable("AHOOTSA_LOG_DIR", $LogRoot, "User")
if (-not (Test-Path -LiteralPath $LogRoot)) { New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null }
$TestFile = Join-Path $LogRoot ("ahootsa_log_write_test_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".txt")
"TEST LOG WRITE OK $(Get-Date -Format o)" | Set-Content -Encoding UTF8 -LiteralPath $TestFile
Write-Host "LogRoot = $LogRoot"
Write-Host "TestFile existe =" (Test-Path -LiteralPath $TestFile)
Write-Host "AHOOTSA_LOG_DIR =" $env:AHOOTSA_LOG_DIR
Get-ChildItem -LiteralPath $LogRoot -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 30 FullName,LastWriteTime,Length | Format-Table -AutoSize


Write-Host ""
Write-Host "Comprobacion de snapshots antiguos grandes:"
$LargeSnapshots = Get-ChildItem -LiteralPath $LogRoot -Filter "voice_probe_before_*.json" -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Length -gt 5MB } |
    Sort-Object Length -Descending

if ($LargeSnapshots) {
    Write-Host "[AVISO] Hay voice_probe_before grande de versiones anteriores. Ya no se generaran en 5.0.24."
    $LargeSnapshots | Select-Object FullName, Length, LastWriteTime | Format-Table -AutoSize
    Write-Host "Puedes borrarlos si no los necesitas para diagnostico historico."
} else {
    Write-Host "No hay voice_probe_before grande."
}
