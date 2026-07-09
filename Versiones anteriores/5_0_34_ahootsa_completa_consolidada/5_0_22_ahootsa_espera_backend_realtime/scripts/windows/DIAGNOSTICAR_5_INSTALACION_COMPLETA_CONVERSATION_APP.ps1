# DIAGNOSTICAR_5_INSTALACION_COMPLETA_CONVERSATION_APP.ps1

$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$SitePackages = Join-Path $DesktopDir "apps_venv\Lib\site-packages"
$ConversationPkg = Join-Path $SitePackages "reachy_mini_conversation_app"
$Profile = Join-Path $ConversationPkg "profiles\ahootsa_realtime_es"
$DefaultProfile = Join-Path $ConversationPkg "profiles\default"

foreach ($P in @($Profile, $DefaultProfile)) {
    Write-Host ""
    Write-Host "Perfil =" $P
    Write-Host "existe =" (Test-Path -LiteralPath $P)

    $Tools = Join-Path $P "tools.txt"
    $Instructions = Join-Path $P "instructions.txt"
    $Ask = Join-Path $P "ask_ollama.py"
    $Act = Join-Path $P "start_communication_activity.py"

    if (Test-Path -LiteralPath $Tools) {
        $TT = Get-Content -Raw -Encoding UTF8 -LiteralPath $Tools
        Write-Host "tools actividades =" ($TT -match "actividades_comunicacion")
        Write-Host "tools ask_ollama =" ($TT -match "ask_ollama")
    }
    if (Test-Path -LiteralPath $Instructions) {
        $IT = Get-Content -Raw -Encoding UTF8 -LiteralPath $Instructions
        Write-Host "instructions modo 5.0.9 =" ($IT -match "MODO CONVERSACIONAL 5.0.9")
        Write-Host "instructions no Reachy =" ($IT -match "No eres Reachy Mini")
        Write-Host "ask_ollama opcional en instrucciones =" ($IT -match "No uses ask_ollama salvo")
    }
    if (Test-Path -LiteralPath $Ask) {
        $AT = Get-Content -Raw -Encoding UTF8 -LiteralPath $Ask
        Write-Host "ask_ollama actividad opcional =" ($AT -match "actividad opcional")
        Write-Host "ask_ollama no cerebro =" ($AT -match "No es el cerebro principal|no como cerebro principal")
    }
    if (Test-Path -LiteralPath $Act) {
        $AC = Get-Content -Raw -Encoding UTF8 -LiteralPath $Act
        Write-Host "actividad directa =" ($AC -match "needs_response\s*=\s*False")
    }
}

Write-Host ""
Write-Host "AHOOTSA_USE_OLLAMA_AS_BRAIN =" $env:AHOOTSA_USE_OLLAMA_AS_BRAIN
Write-Host "Esperado: vacio"
