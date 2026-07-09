$LogRoot="D:\RITXI\logs"
$Info=Join-Path $LogRoot "ULTIMA_EJECUCION_AHOOTSA_INFO.txt"
$Out=Join-Path $LogRoot "ULTIMA_EJECUCION_AHOOTSA_5_0_43_RESUMEN.txt"
"Resumen Ahootsa 5.0.43 - generado $(Get-Date -Format o)" | Set-Content -Encoding UTF8 -LiteralPath $Out
if (Test-Path $Info) { Get-Content $Info | Add-Content -Encoding UTF8 -LiteralPath $Out }
$patterns='ERROR','WARN','Traceback','Exception','404','Not Found','timeout','timed out','Ollama','ollama','camera','cámara','pygame','winsound','pyttsx3','SAPI','connected=False','can_proceed=False','/ollama/ask','/ask_ollama'
Get-ChildItem $LogRoot -File | Sort-Object LastWriteTime -Descending | Select-Object -First 10 | ForEach-Object {
 Add-Content -Encoding UTF8 -LiteralPath $Out -Value "`n------------------------------------------------------------`nArchivo: $($_.FullName)`nTamaño: $($_.Length) bytes`n"
 try { $lines=Get-Content -LiteralPath $_.FullName -Tail 400 -ErrorAction Stop; $sel=$lines | Where-Object { $line=$_; $patterns | Where-Object { $line -match [regex]::Escape($_) } }; if($sel){$sel|Select-Object -Last 160|Add-Content -Encoding UTF8 -LiteralPath $Out}else{$lines|Select-Object -Last 80|Add-Content -Encoding UTF8 -LiteralPath $Out} } catch { Add-Content -Encoding UTF8 -LiteralPath $Out -Value $_.Exception.Message }
}
Write-Host "Resumen: $Out"
