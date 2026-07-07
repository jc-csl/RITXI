# PARAR_6_FALLBACK_LOCAL.ps1

param(
    [int]$Port = 8090
)

$ErrorActionPreference = "Continue"

Write-Host "Parando Ahootsa 6 en puerto $Port..."

$Candidates = Get-CimInstance Win32_Process |
    Where-Object {
        $_.CommandLine -match "uvicorn" -and
        $_.CommandLine -match "app.main:app" -and
        $_.CommandLine -match ([string]$Port)
    }

foreach ($P in $Candidates) {
    Write-Host "Parando PID $($P.ProcessId)"
    Stop-Process -Id $P.ProcessId -Force
}

Write-Host "Hecho."
