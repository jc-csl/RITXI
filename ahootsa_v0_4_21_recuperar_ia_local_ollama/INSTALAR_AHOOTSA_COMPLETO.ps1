param(
    [switch]$SkipDesktopCheck,
    [switch]$SkipOfficialAppCheck
)

$ErrorActionPreference = "Continue"

function Header($Text) {
    Write-Host ""
    Write-Host "============================================"
    Write-Host " $Text"
    Write-Host "============================================"
}
function Info($Text) { Write-Host "[INFO] $Text" }
function Warn($Text) { Write-Host "[AVISO] $Text" -ForegroundColor Yellow }
function Fail($Text) { Write-Host "[ERROR] $Text" -ForegroundColor Red; exit 1 }

function Run-PipInstallForced($PythonExe, $Root) {
    Info "Instalando Ahootsa en: $PythonExe"

    & $PythonExe -m pip uninstall -y ahootsa-realtime-ollama-desktop-app 2>$null
    $uninstallExit = $LASTEXITCODE

    # Primero intento normal.
    & $PythonExe -m pip install --no-deps --force-reinstall -e $Root
    $code = $LASTEXITCODE

    if ($code -ne 0) {
        Warn "Instalacion normal fallo en $PythonExe con codigo $code."
        Warn "Reintentando con --break-system-packages..."
        & $PythonExe -m pip install --break-system-packages --no-deps --force-reinstall -e $Root
        $code = $LASTEXITCODE
    }

    if ($code -ne 0) {
        Fail "No se pudo instalar Ahootsa en $PythonExe. Codigo: $code"
    }

    Info "Instalacion OK en $PythonExe"

    & $PythonExe -c "import importlib.metadata as m; print('version=', m.version('ahootsa-realtime-ollama-desktop-app')); print([ep.name for ep in m.entry_points(group='reachy_mini_apps')])"
}

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

Header "Ahootsa Realtime Ollama v0.4.21 - instalacion forzada"

$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$MetaDir = Join-Path $DesktopDir ".app_metadata"
$PythonEmbedded = Join-Path $DesktopDir "cpython-3.12-windows-x86_64-none\python.exe"
$PythonVenv = Join-Path $DesktopDir ".venv\Scripts\python.exe"
$PythonAppsVenv = Join-Path $DesktopDir "apps_venv\Scripts\python.exe"

if (-not $SkipDesktopCheck) {
    if (-not (Test-Path $DesktopDir)) {
        Fail "No existe $DesktopDir. Abre Reachy Mini Desktop App una vez antes de instalar Ahootsa."
    }
    Info "Reachy Mini Desktop encontrado: $DesktopDir"
}

if (-not $SkipOfficialAppCheck) {
    $officialMeta = Join-Path $MetaDir "reachy_mini_conversation_app.json"
    if (-not (Test-Path $officialMeta)) {
        Warn "No se encuentra metadata de la app oficial: $officialMeta"
        Warn "Instala/abre Reachy Mini Conversation App desde Desktop antes de usar Ahootsa."
    } else {
        Info "Metadata app oficial encontrada."
    }
}

Header "Liberar puertos Ahootsa"
$ports = 7860,7861,7862
foreach ($port in $ports) {
    $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    foreach ($conn in $conns) {
        try {
            Info "Cerrando puerto $port PID $($conn.OwningProcess)"
            Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
        } catch {
            Warn "No se pudo cerrar puerto ${port}: $_"
        }
    }
}

Header "Comprobar Ollama y modelo local"
$ollama = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $ollama) {
    Fail "Ollama no esta instalado o no esta en PATH."
}
Info "Ollama encontrado: $($ollama.Source)"

$BaseModel = "hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest"
$AhootsaModel = "ahootsa-local"
$AhootsaModelLatest = "ahootsa-local:latest"
$ModelDir = Join-Path $env:LOCALAPPDATA "Ahootsa\ollama_ahootsa"
New-Item -ItemType Directory -Force -Path $ModelDir | Out-Null
$Modelfile = Join-Path $ModelDir "Modelfile"

Info "Descargando/comprobando modelo base: $BaseModel"
ollama pull $BaseModel
if ($LASTEXITCODE -ne 0) { Fail "ollama pull fallo." }

$modelfileContent = @"
FROM $BaseModel

PARAMETER temperature 0.6
PARAMETER top_p 0.9
PARAMETER num_ctx 2048

SYSTEM """
Eres Ahootsa, un asistente educativo amable, claro y paciente.
Respondes siempre en español.
Usas frases cortas.
Das instrucciones sencillas.
Eres positivo y animas al usuario.
No dices que eres ChatGPT.
No controlas directamente el robot.
Si te consultan desde Reachy Mini, ayudas con explicaciones, ideas, actividades y reformulaciones sencillas.
"""
"@
$modelfileContent | Set-Content -Encoding UTF8 $Modelfile

Info "Creando modelo: $AhootsaModelLatest"
ollama create $AhootsaModel -f $Modelfile
if ($LASTEXITCODE -ne 0) { Fail "ollama create fallo." }

Info "Modelos instalados:"
ollama list

Header "Probar API Ollama"
try {
    $body = @{
        model = $AhootsaModelLatest
        stream = $false
        messages = @(@{ role = "user"; content = "Hola Ahootsa, responde en español con una frase corta." })
    } | ConvertTo-Json -Depth 5

    $resp = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/chat" -Method Post -ContentType "application/json" -Body $body
    Info "Respuesta de Ollama: $($resp.message.content)"
} catch {
    Warn "No se pudo probar la API de Ollama."
    Warn "$_"
}

Header "Limpiar variables antiguas"
[Environment]::SetEnvironmentVariable("AHOOTSA_EMOTIONS_LIBRARY_DIR", $null, "User")
[Environment]::SetEnvironmentVariable("REACHY_MINI_EMOTIONS_LIBRARY_DIR", $null, "User")
[Environment]::SetEnvironmentVariable("AHOOTSA_LOCAL_EMOTIONS_LIBRARY", $null, "User")

Header "Instalar Ahootsa en TODOS los Python internos"

$pythons = @($PythonEmbedded, $PythonVenv, $PythonAppsVenv) | Where-Object { Test-Path $_ }

if ($pythons.Count -eq 0) {
    Fail "No se encontró ningún Python interno de Reachy Mini Desktop."
}

foreach ($py in $pythons) {
    Run-PipInstallForced -PythonExe $py -Root $Root
}

Header "Crear metadata para Reachy Mini Desktop"

New-Item -ItemType Directory -Force -Path $MetaDir | Out-Null
$metadataPath = Join-Path $MetaDir "ahootsa_realtime_ollama_app.json"

$metadata = @{
    _id = "local-ahootsa-realtime-ollama-app"
    id = "local-user/ahootsa_realtime_ollama_app"
    sdk = "static"
    author = "Centro San Luis"
    cardData = @{
        title = "Ahootsa Realtime Ollama"
        emoji = "🤖"
        short_description = "Conversacion en espanol con herramientas originales y consulta Ollama local"
        tags = @("reachy_mini", "reachy_mini_python_app", "ollama", "ahootsa")
    }
    host = "http://localhost:7860"
    isPythonApp = $true
} | ConvertTo-Json -Depth 10

$metadata | Set-Content -Encoding UTF8 $metadataPath
Info "Metadata creada: $metadataPath"


Header "Instalar soporte cámara PC para modo SIM"
powershell -ExecutionPolicy Bypass -File (Join-Path $Root "INSTALAR_CAMARA_PC.ps1")
if ($LASTEXITCODE -ne 0) {
    Warn "No se pudo instalar/verificar OpenCV para camera_pc. La app seguirá funcionando, pero camera_pc puede fallar."
}

Header "Reparar perfil ask_ollama"

powershell -ExecutionPolicy Bypass -File (Join-Path $Root "REPARAR_PERFIL_ASK_OLLAMA.ps1")
if ($LASTEXITCODE -ne 0) { Fail "REPARAR_PERFIL_ASK_OLLAMA.ps1 fallo." }


Header "Aplicar voz Coral por defecto"
powershell -ExecutionPolicy Bypass -File (Join-Path $Root "CAMBIAR_VOZ_AHOOTSA.ps1") -Voice Coral

Header "Diagnostico final"

powershell -ExecutionPolicy Bypass -File (Join-Path $Root "DIAGNOSTICAR_ASK_OLLAMA.ps1")

Header "Instalacion completada"

Write-Host ""
Write-Host "Siguientes pasos:"
Write-Host "1. Cierra completamente Reachy Mini Desktop."
Write-Host "2. Abre Reachy Mini Desktop App."
Write-Host "3. Arranca Ahootsa Realtime Ollama."
Write-Host "4. Prueba: usa la herramienta ask_ollama con este prompt: dame una actividad sencilla en español"
