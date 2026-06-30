# DIAGNOSTICAR_VOZ_SOHEE_TOTAL.ps1
$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$ProfileName = "ahootsa_realtime_es"
Write-Host "Variables de voz:"
foreach ($name in @("AHOOTSA_VOICE","OPENAI_REALTIME_VOICE","REACHY_MINI_VOICE","VOICE","REALTIME_VOICE","TTS_VOICE","AUDIO_VOICE")) { Write-Host "$name=" ([Environment]::GetEnvironmentVariable($name, "User")) }
Write-Host ""; Write-Host "voice.txt:"
$profiles = @(
    (Join-Path $DesktopDir "user_personalities\$ProfileName"),
    (Join-Path $DesktopDir "profiles\$ProfileName"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages
eachy_mini_conversation_app\profiles\$ProfileName"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages
eachy_talk_data\profiles\$ProfileName"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages
eachy_mini_conversation_app\profiles\default"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages
eachy_talk_data\profiles\default")
)
foreach ($p in $profiles) { $v = Join-Path $p "voice.txt"; if (Test-Path $v) { Write-Host "$v ->" (Get-Content $v -Raw -Encoding UTF8) } else { Write-Host "$v -> NO EXISTE" } }
Write-Host ""; Write-Host "Archivos que todavía contienen Aiden:"
Get-ChildItem -Path $DesktopDir -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.Extension -match "\.(json|toml|yaml|yml|ini|cfg|txt|env)$" } | Select-String -Pattern "Aiden|aiden" -CaseSensitive:$false | Select-Object -First 30 | ForEach-Object { Write-Host $_.Path ":" $_.Line.Trim() }
