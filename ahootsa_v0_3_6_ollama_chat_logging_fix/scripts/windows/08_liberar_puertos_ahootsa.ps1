$ErrorActionPreference = "Continue"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Ahootsa - liberar puertos locales" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Cierra antes Reachy Mini Desktop App si está abierta." -ForegroundColor Yellow
Write-Host "No se toca Ollama en 11434." -ForegroundColor Yellow
Write-Host ""

$Ports = @(7860, 7861, 7862)
foreach ($Port in $Ports) {
    $Conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if (-not $Conns) {
        Write-Host "Puerto $Port libre." -ForegroundColor Green
        continue
    }
    foreach ($Conn in $Conns) {
        $PidToKill = $Conn.OwningProcess
        if ($PidToKill -and $PidToKill -ne 0) {
            try {
                $Proc = Get-Process -Id $PidToKill -ErrorAction Stop
                Write-Host "Cerrando puerto $Port -> PID $PidToKill ($($Proc.ProcessName))" -ForegroundColor Yellow
                Stop-Process -Id $PidToKill -Force
            } catch {
                Write-Host "No se pudo cerrar PID $PidToKill en puerto ${Port}: $_" -ForegroundColor Red
            }
        }
    }
}

Write-Host ""
Write-Host "Comprobación final:" -ForegroundColor Cyan
Get-NetTCPConnection -LocalPort $Ports -State Listen -ErrorAction SilentlyContinue | Select-Object LocalPort, State, OwningProcess
Write-Host ""
Write-Host "Listo. Ahora abre Reachy Mini Desktop y arranca Ahootsa Ollama Local." -ForegroundColor Green
Write-Host "Panel Ollama Local: http://127.0.0.1:7862" -ForegroundColor Green
