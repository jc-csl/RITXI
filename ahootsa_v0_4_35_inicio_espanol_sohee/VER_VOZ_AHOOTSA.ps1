# VER_VOZ_AHOOTSA.ps1
$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$profiles = @(
    (Join-Path $DesktopDir "user_personalities\ahootsa_realtime_es"),
    (Join-Path $DesktopDir "profiles\ahootsa_realtime_es"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\ahootsa_realtime_es"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_talk_data\profiles\ahootsa_realtime_es")
)
foreach ($p in $profiles) {
    $f = Join-Path $p "voice.txt"
    if (Test-Path $f) { Write-Host "$f ->" (Get-Content $f -Raw -Encoding UTF8) }
}
