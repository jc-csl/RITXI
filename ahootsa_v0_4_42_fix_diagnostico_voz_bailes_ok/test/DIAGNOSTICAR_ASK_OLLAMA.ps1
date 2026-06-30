# DIAGNOSTICAR_ASK_OLLAMA.ps1
# Ubicación actual: subcarpeta test.
# Ejecutar desde la raíz con: powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_ASK_OLLAMA.ps1

# 10_diagnosticar_ask_ollama.ps1
# Diagnóstico de Ollama y herramienta ask_ollama para Ahootsa.

$ErrorActionPreference = "Continue"

function Header($Text) {
    Write-Host ""
    Write-Host "============================================"
    Write-Host " $Text"
    Write-Host "============================================"
}

function Info($Text) { Write-Host "[INFO] $Text" }
function Warn($Text) { Write-Host "[AVISO] $Text" -ForegroundColor Yellow }

Header "1. Comprobar Ollama"

$ollama = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $ollama) {
    Write-Host "[ERROR] Ollama no está en PATH." -ForegroundColor Red
} else {
    Info "Ollama encontrado: $($ollama.Source)"
    ollama list
}

Header "2. Probar API /api/tags"

try {
    $tags = Invoke-RestMethod http://127.0.0.1:11434/api/tags
    $tags | ConvertTo-Json -Depth 6
} catch {
    Write-Host "[ERROR] No responde http://127.0.0.1:11434/api/tags" -ForegroundColor Red
    Write-Host $_
}

Header "3. Probar API /api/chat con ahootsa-local:latest"

try {
    $body = @{
        model = "ahootsa-local:latest"
        stream = $false
        messages = @(
            @{ role = "user"; content = "Hola Ahootsa. Responde en español con una frase corta." }
        )
    } | ConvertTo-Json -Depth 5

    $resp = Invoke-RestMethod `
      -Uri "http://127.0.0.1:11434/api/chat" `
      -Method Post `
      -ContentType "application/json" `
      -Body $body

    Write-Host "Respuesta:"
    $resp.message.content
} catch {
    Write-Host "[ERROR] Falló /api/chat" -ForegroundColor Red
    Write-Host $_
}

Header "4. Buscar perfil Ahootsa instalado"

$profileRoots = @(
    "$env:LOCALAPPDATA\Reachy Mini Control\user_personalities",
    "$env:LOCALAPPDATA\Reachy Mini Control\profiles",
    "$env:LOCALAPPDATA\Reachy Mini Control"
)

$askFiles = @()
foreach ($root in $profileRoots) {
    if (Test-Path $root) {
        $askFiles += Get-ChildItem $root -Recurse -Filter "ask_ollama.py" -ErrorAction SilentlyContinue
    }
}

if ($askFiles.Count -eq 0) {
    Write-Host "[ERROR] No se ha encontrado ask_ollama.py copiado en perfiles de Desktop." -ForegroundColor Red
    Write-Host "Ejecuta de nuevo:"
    Write-Host ".\scripts\windows\01_instalar_ahootsa_realtime_ollama_en_desktop.ps1"
} else {
    $askFiles | Select-Object FullName
}

Header "5. Comprobar tools.txt"

$toolsFiles = @()
foreach ($root in $profileRoots) {
    if (Test-Path $root) {
        $toolsFiles += Get-ChildItem $root -Recurse -Filter "tools.txt" -ErrorAction SilentlyContinue |
            Where-Object { (Get-Content $_.FullName -Raw) -match "ask_ollama" }
    }
}

if ($toolsFiles.Count -eq 0) {
    Write-Host "[ERROR] No se encontró tools.txt con ask_ollama." -ForegroundColor Red
} else {
    foreach ($f in $toolsFiles) {
        Write-Host "tools.txt con ask_ollama: $($f.FullName)"
        Get-Content $f.FullName
    }
}

Header "6. Mostrar log ask_ollama"

$log = "$env:LOCALAPPDATA\Reachy Mini Control\ahootsa_logs\ask_ollama.log"
if (Test-Path $log) {
    Write-Host "Log: $log"
    Get-Content $log -Tail 40
} else {
    Warn "Todavía no existe log: $log"
    Warn "El log se crea cuando la herramienta ask_ollama llega a ejecutarse."
}

Header "7. Interpretación"

Write-Host "Si /api/chat funciona pero no aparece log ask_ollama:"
Write-Host "  La IA remota NO está llamando a la herramienta."
Write-Host ""
Write-Host "Prueba por voz una orden muy explícita:"
Write-Host '  "usa la herramienta ask_ollama con este prompt: dame una actividad sencilla en español"'
Write-Host ""
Write-Host "Si aparece log con error:"
Write-Host "  Copia aquí las últimas líneas del log."


Header "8. Comprobar perfil en paquete oficial"

$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$pythons = @(
    (Join-Path $DesktopDir "cpython-3.12-windows-x86_64-none\python.exe"),
    (Join-Path $DesktopDir ".venv\Scripts\python.exe"),
    (Join-Path $DesktopDir "apps_venv\Scripts\python.exe")
) | Where-Object { Test-Path $_ }

foreach ($py in $pythons) {
    Write-Host ""
    Write-Host "Python: $py"
    & $py -c "import pathlib, reachy_mini_conversation_app; p=pathlib.Path(reachy_mini_conversation_app.__file__).resolve().parent/'profiles'/'ahootsa_realtime_es'; print('profile=', p); print('exists=', p.exists()); print('ask=', (p/'ask_ollama.py').exists()); print('tools=', (p/'tools.txt').exists())"
}

Write-Host ""
Write-Host "Variable REACHY_MINI_CUSTOM_PROFILE usuario:"
[Environment]::GetEnvironmentVariable("REACHY_MINI_CUSTOM_PROFILE", "User")


Header "9. Comprobar camera_pc"

$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"

Write-Host "camera_pc.py encontrados:"
Get-ChildItem $DesktopDir -Recurse -Filter "camera_pc.py" -ErrorAction SilentlyContinue |
    Select-Object FullName

Write-Host ""
Write-Host "tools.txt con camera_pc:"
Get-ChildItem $DesktopDir -Recurse -Filter "tools.txt" -ErrorAction SilentlyContinue |
    Where-Object { (Get-Content $_.FullName -Raw -ErrorAction SilentlyContinue) -match "camera_pc" } |
    Select-Object FullName

$camLog = "$env:LOCALAPPDATA\Reachy Mini Control\ahootsa_logs\camera_pc.log"
if (Test-Path $camLog) {
    Write-Host ""
    Write-Host "Log camera_pc:"
    Get-Content $camLog -Encoding UTF8 -Tail 20
}
