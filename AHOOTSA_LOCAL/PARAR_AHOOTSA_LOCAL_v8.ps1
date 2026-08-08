$ErrorActionPreference = "Continue"

$Root = "D:\RITXI\AHOOTSA_LOCAL"
$PidFile = Join-Path $Root ".ahootsa_local_v8_pids.json"

Write-Host ""
Write-Host "AHOOTSA LOCAL v8 - PARADA" -ForegroundColor Cyan

if (Test-Path $PidFile) {
    try {
        $obj = Get-Content $PidFile -Raw | ConvertFrom-Json

        foreach ($name in @("app","mujoco","speech","qwen")) {
            $prop = $obj.PSObject.Properties[$name]
            if ($null -ne $prop) {
                $pidValue = [int]$prop.Value
                Write-Host "Cerrando $name PID $pidValue..." -ForegroundColor Yellow
                cmd.exe /c "taskkill /PID $pidValue /T /F" | Out-Null
            }
        }
    } catch {
        Write-Host "Aviso: $($_.Exception.Message)" -ForegroundColor Yellow
    }

    Remove-Item $PidFile -ErrorAction SilentlyContinue
} else {
    Write-Host "No existe fichero de PIDs de v8." -ForegroundColor Yellow
    Write-Host "Cierra con Ctrl+C cualquier ventana Qwen/speech/Reachy que siga abierta." -ForegroundColor Yellow
}
