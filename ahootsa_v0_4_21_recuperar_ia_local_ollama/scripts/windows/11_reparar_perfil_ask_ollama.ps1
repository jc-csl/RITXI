# REPARAR_PERFIL_ASK_OLLAMA.ps1
# v0.4.14: copia el perfil Ahootsa a rutas de perfil reconocidas y fuerza el nombre de perfil.
# Ejecutar con Reachy Mini Desktop cerrado.

$ErrorActionPreference = "Stop"

function Header($Text) {
    Write-Host ""
    Write-Host "============================================"
    Write-Host " $Text"
    Write-Host "============================================"
}
function Info($Text) { Write-Host "[INFO] $Text" }
function Warn($Text) { Write-Host "[AVISO] $Text" -ForegroundColor Yellow }
function Fail($Text) { Write-Host "[ERROR] $Text" -ForegroundColor Red; exit 1 }

function Get-ReachyPythonPaths {
    $DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
    @(
        (Join-Path $DesktopDir "cpython-3.12-windows-x86_64-none\python.exe"),
        (Join-Path $DesktopDir ".venv\Scripts\python.exe"),
        (Join-Path $DesktopDir "apps_venv\Scripts\python.exe")
    ) | Where-Object { Test-Path $_ } | Select-Object -Unique
}

function Copy-Profile($Src, $Dst) {
    New-Item -ItemType Directory -Force -Path $Dst | Out-Null
    Copy-Item (Join-Path $Src "*") $Dst -Recurse -Force

    $tools = Join-Path $Dst "tools.txt"
    $ask = Join-Path $Dst "ask_ollama.py"

    if (-not (Test-Path $ask)) {
        Fail "No se ha copiado ask_ollama.py en $Dst"
    }

    $camPc = Join-Path $Dst "camera_pc.py"
    if (-not (Test-Path $camPc)) {
        Fail "No se ha copiado camera_pc.py en $Dst"
    }
    if (-not (Test-Path $tools)) {
        Fail "No se ha copiado tools.txt en $Dst"
    }

    $raw = Get-Content $tools -Raw -Encoding UTF8
    if ($raw -notmatch "ask_ollama") {
        Add-Content -Encoding UTF8 -Path $tools -Value "`nask_ollama"
    }
    $raw = Get-Content $tools -Raw -Encoding UTF8
    if ($raw -notmatch "camera_pc") {
        Add-Content -Encoding UTF8 -Path $tools -Value "`ncamera_pc"
    }

    Info "Perfil copiado: $Dst"
}

Header "Reparar perfil Ahootsa ask_ollama v0.4.14"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProfileName = "ahootsa_realtime_es"
$SrcProfile = Join-Path $Root "src\ahootsa_realtime_ollama_desktop_app\profiles\$ProfileName"
$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"

if (-not (Test-Path $SrcProfile)) { Fail "No existe perfil origen: $SrcProfile" }
if (-not (Test-Path $DesktopDir)) { Fail "No existe Reachy Mini Control. Abre Desktop una vez." }

# 1. Rutas de usuario / instancia.
$destinations = New-Object System.Collections.Generic.List[string]
$destinations.Add((Join-Path $DesktopDir "user_personalities\$ProfileName"))
$destinations.Add((Join-Path $DesktopDir "profiles\$ProfileName"))

Get-ChildItem $DesktopDir -Directory -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -in @("user_personalities", "profiles") } |
    ForEach-Object {
        $destinations.Add((Join-Path $_.FullName $ProfileName))
    }

# 2. Rutas reales del paquete oficial en cada Python.
$pythons = @(Get-ReachyPythonPaths)
foreach ($py in $pythons) {
    try {
        $pkgDir = & $py -c "import pathlib, reachy_mini_conversation_app; print(pathlib.Path(reachy_mini_conversation_app.__file__).resolve().parent)"
        if ($pkgDir -and (Test-Path $pkgDir)) {
            $destinations.Add((Join-Path $pkgDir "profiles\$ProfileName"))
        }
    } catch {
        Warn "No se pudo localizar paquete oficial en $py"
    }
}

$unique = $destinations | Sort-Object -Unique

Write-Host "Origen:"
Write-Host "  $SrcProfile"
Write-Host ""
Write-Host "Destinos:"
foreach ($d in $unique) { Write-Host "  $d" }

foreach ($d in $unique) {
    Copy-Profile -Src $SrcProfile -Dst $d
}

# 3. Variable de usuario como apoyo; la app Ahootsa también la fuerza en proceso.
[Environment]::SetEnvironmentVariable("REACHY_MINI_CUSTOM_PROFILE", $ProfileName, "User")
Info "Variable de usuario REACHY_MINI_CUSTOM_PROFILE=$ProfileName"

Header "Comprobación"

Write-Host "ask_ollama.py encontrados:"
Get-ChildItem $DesktopDir -Recurse -Filter "ask_ollama.py" -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -match $ProfileName } |
    Select-Object FullName

foreach ($py in $pythons) {
    Write-Host ""
    Write-Host "Paquete oficial en $py"
    & $py -c "import pathlib, reachy_mini_conversation_app; p=pathlib.Path(reachy_mini_conversation_app.__file__).resolve().parent/'profiles'/'ahootsa_realtime_es'; print(p); print('EXISTE=', p.exists()); print('ASK=', (p/'ask_ollama.py').exists()); print('TOOLS=', (p/'tools.txt').exists())"
}

Header "Final"
Write-Host "Cierra completamente Reachy Mini Desktop."
Write-Host "Abre Desktop y arranca Ahootsa Realtime Ollama."
Write-Host "IMPORTANTE: las herramientas se cargan al arranque, no basta con Apply dentro de Personality."
