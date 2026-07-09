param([int]$Seconds = 120)
$ErrorActionPreference = "Continue"
$LogDir = "D:\RITXI\logs"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$Out = Join-Path $LogDir "AHOOTSA_TRAZA_VOZ_7_0_21_$Stamp.log"
$Start = Get-Date
$End = $Start.AddSeconds($Seconds)
"TRAZA VOZ AHOOTSA 7.0.21" | Out-File -Encoding UTF8 $Out
"Inicio: $Start" | Out-File -Encoding UTF8 -Append $Out
"Durante la prueba di: lista de bailes / haz baile dos / haz baile tres / haz un saludo / abre juego de parejas" | Out-File -Encoding UTF8 -Append $Out
Write-Host "Grabando trazas durante $Seconds segundos..."
Write-Host "Di ahora: lista de bailes; haz baile dos; haz baile tres; haz un saludo; abre juego de parejas"
while ((Get-Date) -lt $End) {
  Start-Sleep -Seconds 2
}
"`n=== ARCHIVOS MODIFICADOS EN VENTANA ===" | Out-File -Encoding UTF8 -Append $Out
Get-ChildItem $LogDir -File | Where-Object { $_.LastWriteTime -ge $Start.AddMinutes(-1) } | Sort-Object LastWriteTime | ForEach-Object {
  "FILE $($_.Name) $($_.LastWriteTime) size=$($_.Length)" | Out-File -Encoding UTF8 -Append $Out
} 
"`n=== EVENTOS HERRAMIENTAS / BUSQUEDA ===" | Out-File -Encoding UTF8 -Append $Out
$patterns = "tool_start|tool_result|tool_exception|play_panel_dance_activity|list_panel_dances_activities|play_emotion|start_memory_pairs_game|choose_memory_cards|memory_choose|dance1|dance2|dance3|welcoming2|olay|play"
Get-ChildItem $LogDir -File | Where-Object { $_.LastWriteTime -ge $Start.AddMinutes(-1) -and ($_.Name -like "*.log" -or $_.Name -like "*.jsonl" -or $_.Name -like "*.txt") } | ForEach-Object {
  try {
    Select-String -Path $_.FullName -Pattern $patterns -Encoding UTF8 -ErrorAction SilentlyContinue | Select-Object -Last 80 | ForEach-Object { "{0}:{1}: {2}" -f $_.Path,$_.LineNumber,$_.Line } | Out-File -Encoding UTF8 -Append $Out
  } catch {}
}
Write-Host "LOG: $Out"
