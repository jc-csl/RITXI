# VER_VOZ_AHOOTSA.ps1
# Muestra voice.txt en todas las rutas conocidas de Ahootsa.

$ProfileName = "ahootsa_realtime_es"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$files = @(
    (Join-Path $Root "src\ahootsa_realtime_ollama_desktop_app\profiles\$ProfileName\voice.txt"),
    (Join-Path $DesktopDir "user_personalities\$ProfileName\voice.txt"),
    (Join-Path $DesktopDir "profiles\$ProfileName\voice.txt"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\$ProfileName\voice.txt"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_talk_data\profiles\$ProfileName\voice.txt")
) | Select-Object -Unique

foreach ($f in $files) {
    if (Test-Path $f) {
        Write-Host "$f -> $(Get-Content $f -Raw -Encoding UTF8)"
    } else {
        Write-Host "$f -> NO EXISTE"
    }
}
