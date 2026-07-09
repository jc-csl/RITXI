param(
    [int]$DaemonPort = 8000,
    [switch]$KillDaemon
)
$ErrorActionPreference = "Continue"
$daemonUrl = "http://127.0.0.1:$DaemonPort"
Write-Host "[INFO] Intentando parar app Ahootsa por API..."
foreach($path in @('/api/apps/stop-app/ahootsa_realtime_ollama_app','/api/apps/stop/ahootsa_realtime_ollama_app')){
    try { Invoke-RestMethod -Method Post -Uri "$daemonUrl$path" -TimeoutSec 5 | ConvertTo-Json -Depth 5; break } catch { Write-Host "No: $path -> $($_.Exception.Message)" }
}
if ($KillDaemon) {
    Write-Host "[WARN] Cerrando procesos reachy-mini-daemon..."
    Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'reachy-mini-daemon' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
}
