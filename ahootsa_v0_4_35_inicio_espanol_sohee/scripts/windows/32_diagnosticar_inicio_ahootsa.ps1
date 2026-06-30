# DIAGNOSTICAR_INICIO_AHOOTSA.ps1
$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$ProfileName = "ahootsa_realtime_es"
$paths = @(
    (Join-Path $DesktopDir "user_personalities\$ProfileName"),
    (Join-Path $DesktopDir "profiles\$ProfileName"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\$ProfileName"),
    (Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_talk_data\profiles\$ProfileName")
)
Write-Host "Variables de entorno usuario:"
Write-Host "AHOOTSA_VOICE=" ([Environment]::GetEnvironmentVariable("AHOOTSA_VOICE", "User"))
Write-Host "REACHY_MINI_CUSTOM_PROFILE=" ([Environment]::GetEnvironmentVariable("REACHY_MINI_CUSTOM_PROFILE", "User"))
Write-Host "REALTIME_TRANSCRIPTION_LANGUAGE=" ([Environment]::GetEnvironmentVariable("REALTIME_TRANSCRIPTION_LANGUAGE", "User"))
Write-Host ""
foreach ($p in $paths) {
    Write-Host "Perfil: $p"
    Write-Host " exists=" (Test-Path $p)
    foreach ($f in @("voice.txt", "greeting.txt", "instructions.txt")) {
        $file = Join-Path $p $f
        if (Test-Path $file) {
            $content = Get-Content $file -Raw -Encoding UTF8
            if ($content.Length -gt 180) { $content = $content.Substring(0,180) + "..." }
            Write-Host "  $f -> $content"
        } else {
            Write-Host "  $f -> NO EXISTE"
        }
    }
    Write-Host ""
}
