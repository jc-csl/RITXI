param(
    [string]$BaseUrl = "http://127.0.0.1:7860"
)
$ErrorActionPreference = "Continue"
New-Item -ItemType Directory -Force -Path "D:\RITXI\logs" | Out-Null
$Out = "D:\RITXI\logs\AHOOTSA7_MEMORY_CAMARA_DIAGNOSTICO.log"
Start-Transcript -LiteralPath $Out -Force | Out-Null
try {
    Write-Host "============================================================"
    Write-Host "Diagnóstico Memory + Cámara PC Ahootsa 7.0.9"
    Write-Host "============================================================"
    foreach($url in @(
        "$BaseUrl/ahootsa/status",
        "$BaseUrl/memory/games",
        "$BaseUrl/memory/reset?game_id=animales",
        "$BaseUrl/memory/state",
        "$BaseUrl/camera_pc/latest",
        "$BaseUrl/camera_pc/page"
    )) {
        Write-Host "`n--- $url"
        try {
            $r = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 6
            $r | ConvertTo-Json -Depth 8
        } catch {
            Write-Host "ERROR $($_.Exception.Message)"
            try {
                $resp = $_.Exception.Response
                if ($resp) {
                    $reader = New-Object System.IO.StreamReader($resp.GetResponseStream())
                    Write-Host "BODY:" $reader.ReadToEnd()
                }
            } catch {}
        }
    }

    Write-Host "`n--- Prueba de captura PC OpenCV"
    try {
        $body = @{ camera_index = 0; warmup_frames = 2 } | ConvertTo-Json
        $r = Invoke-RestMethod -Uri "$BaseUrl/camera_pc/capture" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 12
        $r | ConvertTo-Json -Depth 8
    } catch {
        Write-Host "ERROR_CAPTURE $($_.Exception.Message)"
        try {
            $resp = $_.Exception.Response
            if ($resp) {
                $reader = New-Object System.IO.StreamReader($resp.GetResponseStream())
                Write-Host "BODY:" $reader.ReadToEnd()
            }
        } catch {}
    }

    Write-Host "`nÚltimas fotos D:\RITXI\fotos"
    if (Test-Path "D:\RITXI\fotos") {
        Get-ChildItem "D:\RITXI\fotos" -File | Sort-Object LastWriteTime | Select-Object -Last 10 | Format-Table LastWriteTime, Length, Name
    }
} finally {
    Stop-Transcript | Out-Null
    Write-Host "Resumen guardado en $Out"
}
