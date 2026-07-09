$LogRoot = "D:\RITXI\logs"
$Info = Join-Path $LogRoot "ULTIMA_EJECUCION_AHOOTSA_INFO.txt"
$Out = Join-Path $LogRoot "ULTIMA_EJECUCION_AHOOTSA_5_0_41_RESUMEN.txt"
"Resumen Ahootsa 5.0.41 - generado $(Get-Date -Format o)" | Set-Content -Encoding UTF8 -LiteralPath $Out
if (Test-Path $Info) { Get-Content $Info | Add-Content -Encoding UTF8 -LiteralPath $Out }
$patterns = 'ERROR','WARN','Traceback','Exception','404','Not Found','timeout','timed out','Ollama','camera','cámara','pygame','winsound','pyttsx3','SAPI','connected=False','can_proceed=False'
Get-ChildItem $LogRoot -File | Sort-Object LastWriteTime -Descending | Select-Object -First 8 | ForEach-Object {
    Add-Content -Encoding UTF8 -LiteralPath $Out -Value "`n------------------------------------------------------------`nArchivo: $($_.FullName)`nTamaño: $($_.Length) bytes`n"
    try {
        $lines = Get-Content -LiteralPath $_.FullName -Tail 300 -ErrorAction Stop
        $sel = $lines | Where-Object { $line=$_; $patterns | Where-Object { $line -match [regex]::Escape($_) } }
        if ($sel) { $sel | Select-Object -Last 120 | Add-Content -Encoding UTF8 -LiteralPath $Out }
        else { $lines | Select-Object -Last 60 | Add-Content -Encoding UTF8 -LiteralPath $Out }
    } catch { Add-Content -Encoding UTF8 -LiteralPath $Out -Value $_.Exception.Message }
}
Write-Host "Resumen: $Out"
