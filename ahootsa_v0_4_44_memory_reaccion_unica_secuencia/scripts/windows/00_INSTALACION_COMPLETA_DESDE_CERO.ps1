$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Ahootsa Realtime Ollama v0.4.44 - instalacion completa" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Este script instala Ahootsa desde la carpeta copiada en esta maquina." -ForegroundColor Cyan
Write-Host "No modifica la app oficial. Solo registra Ahootsa y ask_ollama." -ForegroundColor Cyan
Write-Host ""

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$ReachyBase = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$ScriptsDir = Join-Path $ProjectRoot "scripts\windows"

function Stop-WithHelp($Message, $HelpLines=@()) {
    Write-Host "" 
    Write-Host "ERROR: $Message" -ForegroundColor Red
    foreach ($line in $HelpLines) { Write-Host $line -ForegroundColor Yellow }
    Write-Host ""
    exit 1
}

function Run-Step($Title, $ScriptName) {
    Write-Host ""
    Write-Host "------------------------------------------------------------" -ForegroundColor DarkCyan
    Write-Host " $Title" -ForegroundColor Cyan
    Write-Host "------------------------------------------------------------" -ForegroundColor DarkCyan
    $ScriptPath = Join-Path $ScriptsDir $ScriptName
    if (-not (Test-Path $ScriptPath)) {
        Stop-WithHelp "No existe el script $ScriptName" @("Ruta esperada: $ScriptPath")
    }
    & $ScriptPath
}

Write-Host "Carpeta del proyecto:" $ProjectRoot -ForegroundColor Green
Write-Host "Carpeta Reachy Mini Control:" $ReachyBase -ForegroundColor Green

if (-not (Test-Path $ReachyBase)) {
    Stop-WithHelp "No existe la carpeta de Reachy Mini Desktop." @(
        "Instala Reachy Mini Desktop App.",
        "Abrela al menos una vez para que cree: $ReachyBase",
        "Despues cierra Reachy Mini Desktop y vuelve a ejecutar este script."
    )
}

$Pythons = @(
    (Join-Path $ReachyBase "cpython-3.12-windows-x86_64-none\python.exe"),
    (Join-Path $ReachyBase ".venv\Scripts\python.exe"),
    (Join-Path $ReachyBase "apps_venv\Scripts\python.exe")
)
$ExistingPythons = @($Pythons | Where-Object { Test-Path $_ })
if ($ExistingPythons.Count -eq 0) {
    Stop-WithHelp "No encuentro los Python internos de Reachy Mini Desktop." @(
        "Abre Reachy Mini Desktop App una vez.",
        "Instala/abre la app oficial Reachy Mini Conversation App desde Desktop.",
        "Cierra Desktop y vuelve a ejecutar este script."
    )
}

Write-Host "Python internos encontrados:" -ForegroundColor Cyan
foreach ($py in $ExistingPythons) { Write-Host " - $py" -ForegroundColor Green }

# Comprobar que la app oficial esta disponible en algun entorno.
$OfficialFound = $false
foreach ($py in $ExistingPythons) {
    try {
        & $py -c "import reachy_mini_conversation_app; print('OK')" | Out-Null
        $OfficialFound = $true
        break
    } catch {}
}
if (-not $OfficialFound) {
    Stop-WithHelp "No encuentro reachy_mini_conversation_app en los entornos de Desktop." @(
        "Abre Reachy Mini Desktop App.",
        "Instala la app oficial Reachy Mini Conversation App.",
        "Ejecutala una vez si es necesario.",
        "Cierra Desktop y vuelve a ejecutar este instalador."
    )
}

if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Stop-WithHelp "No encuentro Ollama." @(
        "Instala Ollama desde https://ollama.com/download",
        "Abre Ollama una vez.",
        "Despues vuelve a ejecutar este script."
    )
}

try {
    ollama list | Out-Null
} catch {
    Stop-WithHelp "Ollama esta instalado, pero no responde." @(
        "Abre Ollama o reinicia el servicio de Ollama.",
        "Comprueba en PowerShell: ollama list",
        "Despues vuelve a ejecutar este script."
    )
}

Write-Host ""
Write-Host "Recomendacion: Reachy Mini Desktop debe estar cerrado durante la instalacion." -ForegroundColor Yellow
Write-Host "Si estaba abierto, cierralo ahora. Continuando en 4 segundos..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Run-Step "Liberar puertos Ahootsa 7860/7861/7862" "08_liberar_puertos_ahootsa.ps1"
Run-Step "Limpiar variables antiguas de emociones locales" "04_limpiar_variables_emociones_locales.ps1"
Run-Step "Crear/verificar modelo Ollama ahootsa-local" "00_crear_modelo_ollama_ahootsa.ps1"
Run-Step "Instalar paquete Ahootsa en Python internos de Desktop" "01_instalar_ahootsa_realtime_ollama_en_desktop.ps1"
Run-Step "Registrar metadata en Reachy Mini Desktop" "05_instalar_metadata_desktop.ps1"
Run-Step "Comprobar instalacion y modelos" "02_comprobar_ahootsa_realtime_ollama.ps1"
Run-Step "Probar API de Ollama con ahootsa-local" "09_probar_ollama_api_ahootsa.ps1"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host " INSTALACION COMPLETA" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "Ahora:" -ForegroundColor Green
Write-Host "1. Cierra esta PowerShell si quieres." -ForegroundColor Green
Write-Host "2. Abre Reachy Mini Desktop App." -ForegroundColor Green
Write-Host "3. En Applications, busca: Ahootsa Realtime Ollama." -ForegroundColor Green
Write-Host "4. Pulsa Start." -ForegroundColor Green
Write-Host "5. Abre http://127.0.0.1:7860" -ForegroundColor Green
Write-Host ""
Write-Host "Pruebas por voz:" -ForegroundColor Cyan
Write-Host " - baila" -ForegroundColor Cyan
Write-Host " - saluda" -ForegroundColor Cyan
Write-Host " - mira a la izquierda" -ForegroundColor Cyan
Write-Host " - usa la IA local para darme una actividad sencilla" -ForegroundColor Cyan
Write-Host ""
