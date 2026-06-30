$ErrorActionPreference = "Continue"
$ports = 7860,7861,7862
foreach ($Port in $ports) {
    $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    foreach ($conn in $conns) {
        $PidToKill = $conn.OwningProcess
        if ($PidToKill -and $PidToKill -ne 0) {
            try {
                Write-Host "Cerrando puerto ${Port}, PID $PidToKill" -ForegroundColor Yellow
                Stop-Process -Id $PidToKill -Force
            } catch {
                Write-Host "No se pudo cerrar PID $PidToKill en puerto ${Port}: $_" -ForegroundColor Red
            }
        }
    }
}
Write-Host "Puertos Ahootsa revisados. No se ha tocado el puerto 11434 de Ollama." -ForegroundColor Green
