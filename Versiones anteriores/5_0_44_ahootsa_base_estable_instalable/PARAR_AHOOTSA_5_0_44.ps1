$ErrorActionPreference = "Continue"
try { Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/apps/stop-current-app" -TimeoutSec 5 | Out-Host } catch { Write-Host $_.Exception.Message }
Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match "ahootsa|reachy-mini-daemon|uvicorn" } | Select-Object ProcessId,Name,CommandLine | Format-List
