# DIAGNOSTICAR_5_LOGS_Y_VOZ.ps1
$LogRoot="D:\RITXI\logs"
Write-Host "Logs en $LogRoot =" (Test-Path $LogRoot)
if(Test-Path $LogRoot){Get-ChildItem $LogRoot -File|Sort-Object LastWriteTime -Descending|Select-Object -First 20 FullName,LastWriteTime,Length|Format-Table -AutoSize}
$DesktopDir=Join-Path $env:LOCALAPPDATA "Reachy Mini Control"; $SP=Join-Path $DesktopDir "apps_venv\Lib\site-packages"
$Files=@((Join-Path $SP "reachy_mini_conversation_app\profiles\ahootsa_realtime_es\voice.txt"),(Join-Path $SP "reachy_mini_conversation_app\profiles\default\voice.txt"),(Join-Path $SP "reachy_mini_conversation_app\profiles\starter_profile\voice.txt"),(Join-Path $SP "reachy_talk_data\profiles\ahootsa_realtime_es\voice.txt"),(Join-Path $SP "ahootsa_realtime_ollama_desktop_app\profiles\ahootsa_realtime_es\voice.txt"))
foreach($F in $Files){Write-Host ""; Write-Host $F; Write-Host "existe =" (Test-Path $F); if(Test-Path $F){Write-Host "valor =" (Get-Content -Raw -Encoding UTF8 $F)}}
"AHOOTSA_VOICE","VOICE","REACHY_MINI_VOICE","OPENAI_REALTIME_VOICE","REALTIME_VOICE","TTS_VOICE","AUDIO_VOICE"|ForEach-Object{Write-Host "$_ =" ([Environment]::GetEnvironmentVariable($_,"User"))}
try{$C=Invoke-RestMethod -Uri "http://127.0.0.1:7860/voices/current" -Method Get -TimeoutSec 5; Write-Host "API voices/current =" ($C|ConvertTo-Json -Depth 8 -Compress)}catch{Write-Host "API voices/current no responde"}
