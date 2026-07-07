# DIAGNOSTICAR_5_TOOLS_FLUIDEZ.ps1
# Comprueba tools.txt instalados y que la lista es reducida.

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$SP = Join-Path $DesktopDir "apps_venv\Lib\site-packages"
$Files = @(
    (Join-Path $SP "reachy_mini_conversation_app\profiles\ahootsa_realtime_es\tools.txt"),
    (Join-Path $SP "reachy_mini_conversation_app\profiles\default\tools.txt"),
    (Join-Path $SP "reachy_talk_data\profiles\ahootsa_realtime_es\tools.txt"),
    (Join-Path $SP "ahootsa_realtime_ollama_desktop_app\profiles\ahootsa_realtime_es\tools.txt")
)

foreach ($F in $Files) {
    Write-Host ""
    Write-Host $F
    if (Test-Path -LiteralPath $F) {
        $Tools = Get-Content -Encoding UTF8 -LiteralPath $F | Where-Object { $_.Trim() -ne "" -and -not $_.Trim().StartsWith("#") }
        Write-Host "count=$($Tools.Count)"
        $Tools | ForEach-Object { Write-Host " - $_" }
        if ($Tools -contains "ask_ollama") {
            Write-Host "[AVISO] ask_ollama cargado: esto puede reducir fluidez."
        }
    } else {
        Write-Host "[WARN] no existe"
    }
}
