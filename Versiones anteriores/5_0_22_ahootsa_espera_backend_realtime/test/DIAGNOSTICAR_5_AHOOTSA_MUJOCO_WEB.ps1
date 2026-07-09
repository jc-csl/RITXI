# DIAGNOSTICAR_5_AHOOTSA_MUJOCO_WEB.ps1
# Diagnóstico del modo Ahootsa 5.0 MuJoCo web sin Desktop.

param(
    [int]$Port = 8000,
    [string]$HostAddress = "127.0.0.1",
    [string]$AppName = "ahootsa_realtime_ollama_app"
)

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

function Test-PortOpen([string]$HostAddress, [int]$Port) {
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $iar = $client.BeginConnect($HostAddress, $Port, $null, $null)
        $ok = $iar.AsyncWaitHandle.WaitOne(500, $false)
        if ($ok -and $client.Connected) {
            $client.EndConnect($iar)
            $client.Close()
            return $true
        }
        $client.Close()
        return $false
    } catch {
        return $false
    }
}

function Invoke-Api($Method, $Path, [int]$TimeoutSec = 6) {
    $url = "http://$HostAddress`:$Port$Path"
    try {
        if ($Method -eq "GET") {
            return Invoke-RestMethod -Uri $url -Method Get -TimeoutSec $TimeoutSec
        } else {
            return Invoke-RestMethod -Uri $url -Method Post -TimeoutSec $TimeoutSec
        }
    } catch {
        return $null
    }
}

Write-Host ""
Write-Host "============================================================"
Write-Host "Diagnóstico Ahootsa 5.0 - MuJoCo web sin Desktop"
Write-Host "============================================================"

$python = Join-Path $env:LOCALAPPDATA "Reachy Mini Control\apps_venv\Scripts\python.exe"
$daemon = Join-Path $env:LOCALAPPDATA "Reachy Mini Control\apps_venv\Scripts\reachy-mini-daemon.exe"

Write-Host "python existe =" (Test-Path -LiteralPath $python)
Write-Host "daemon existe =" (Test-Path -LiteralPath $daemon)

if (Test-Path -LiteralPath $python) {
    $mujoco = & $python -c "import mujoco; print('OK ' + mujoco.__version__)" 2>&1
    Write-Host "mujoco import =" $mujoco
}

Write-Host "puerto $Port abierto =" (Test-PortOpen $HostAddress $Port)

$status = Invoke-Api "GET" "/api/daemon/status"
Write-Host "daemon status responde =" ($null -ne $status)
if ($null -ne $status) {
    Write-Host ($status | ConvertTo-Json -Depth 6)
}

$installed = Invoke-Api "GET" "/api/apps/list-available/installed"
Write-Host "apps instaladas responde =" ($null -ne $installed)
if ($null -ne $installed) {
    $txt = ($installed | ConvertTo-Json -Depth 10)
    Write-Host "app Ahootsa aparece =" ($txt -match [regex]::Escape($AppName))
    Write-Host "conversation app aparece =" ($txt -match "reachy_mini_conversation_app")
}

$current = Invoke-Api "GET" "/api/apps/current-app-status"
Write-Host "current-app-status responde =" ($null -ne $current)
if ($null -ne $current) {
    Write-Host ($current | ConvertTo-Json -Depth 8)
}

Write-Host ""
Write-Host "Esperado:"
Write-Host "- python existe = True"
Write-Host "- daemon existe = True"
Write-Host "- mujoco import = OK ..."
Write-Host "- puerto 8000 abierto = True"
Write-Host "- daemon status responde = True"
Write-Host "- app Ahootsa aparece = True"

Write-Host ""
Write-Host "============================================================"
Write-Host "Perfil Ahootsa instalado en default"
Write-Host "============================================================"
$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$DefaultProfile = Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\default"
$AhootsaProfile = Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\ahootsa_realtime_es"

foreach ($p in @($DefaultProfile, $AhootsaProfile)) {
    Write-Host ""
    Write-Host "Profile path =" $p
    Write-Host "existe =" (Test-Path -LiteralPath $p)

    $tools = Join-Path $p "tools.txt"
    Write-Host "tools.txt =" (Test-Path -LiteralPath $tools)
    if (Test-Path -LiteralPath $tools) {
        $t = Get-Content -Raw -Encoding UTF8 $tools
        Write-Host "  actividades_comunicacion =" ($t -match "actividades_comunicacion")
        Write-Host "  ask_ollama =" ($t -match "ask_ollama")
        Write-Host "  choose_memory_cards =" ($t -match "choose_memory_cards")
    }

    foreach ($f in @("actividades_comunicacion.py", "ask_ollama.py", "communication_activities_catalog.json")) {
        $fp = Join-Path $p $f
        Write-Host "$f =" (Test-Path -LiteralPath $fp)
    }
}

Write-Host ""
Write-Host "Si el log dice 'Loading tools for profile: default', default/tools.txt debe tener actividades_comunicacion=True."

Write-Host ""
Write-Host "============================================================"
Write-Host "Identidad e idioma Ahootsa 5.0.4"
Write-Host "============================================================"

$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$DefaultProfile = Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\default"
$EnvFile = Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\.env"

foreach ($p in @($DefaultProfile)) {
    Write-Host ""
    Write-Host "Perfil default =" $p
    $g = Join-Path $p "greeting.txt"
    $i = Join-Path $p "instructions.txt"
    $t = Join-Path $p "tools.txt"

    Write-Host "greeting existe =" (Test-Path -LiteralPath $g)
    if (Test-Path -LiteralPath $g) { Write-Host "greeting =" (Get-Content -Raw -Encoding UTF8 $g) }

    Write-Host "instructions existe =" (Test-Path -LiteralPath $i)
    if (Test-Path -LiteralPath $i) {
        $it = Get-Content -Raw -Encoding UTF8 $i
        Write-Host "instructions dice Ahootsa =" ($it -match "Tu nombre es Ahootsa")
        Write-Host "instructions no Reachy Mini =" ($it -match "No eres Reachy Mini")
        Write-Host "instructions castellano =" ($it -match "Habla siempre en castellano")
    }

    Write-Host "tools existe =" (Test-Path -LiteralPath $t)
    if (Test-Path -LiteralPath $t) {
        $tt = Get-Content -Raw -Encoding UTF8 $t
        Write-Host "tools ask_ollama =" ($tt -match "ask_ollama")
        Write-Host "tools actividades =" ($tt -match "actividades_comunicacion")
    }
}

Write-Host ""
Write-Host ".env conversation app =" (Test-Path -LiteralPath $EnvFile)
if (Test-Path -LiteralPath $EnvFile) {
    $envtxt = Get-Content -Raw -Encoding UTF8 $EnvFile
    Write-Host ".env AHOOTSA_NAME =" ($envtxt -match "AHOOTSA_NAME=Ahootsa")
    Write-Host ".env LANGUAGE =" ($envtxt -match "LANGUAGE=es")
}

Write-Host ""
Write-Host "============================================================"
Write-Host "Módulo Python Ahootsa y puerto 7860"
Write-Host "============================================================"

$Python = Join-Path $env:LOCALAPPDATA "Reachy Mini Control\apps_venv\Scripts\python.exe"
if (Test-Path -LiteralPath $Python) {
    $imp = & $Python -c "import ahootsa_realtime_ollama_desktop_app, pathlib; print('IMPORT_OK', pathlib.Path(ahootsa_realtime_ollama_desktop_app.__file__).resolve())" 2>&1
    Write-Host "import ahootsa =" $imp
} else {
    Write-Host "python apps_venv no encontrado"
}

function Test-PortQuiet([int]$Port) {
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $iar = $client.BeginConnect("127.0.0.1", $Port, $null, $null)
        $ok = $iar.AsyncWaitHandle.WaitOne(500, $false)
        if ($ok -and $client.Connected) {
            $client.EndConnect($iar)
            $client.Close()
            return $true
        }
        $client.Close()
        return $false
    } catch { return $false }
}

Write-Host "puerto 7860 abierto =" (Test-PortQuiet 7860)
Write-Host "Si import ahootsa NO dice IMPORT_OK, ejecuta INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1."
Write-Host "Si import OK pero 7860 False, la app no ha arrancado o se ha cerrado."

Write-Host ""
Write-Host "============================================================"
Write-Host "Ahootsa 5.0.7 - actividades directas"
Write-Host "============================================================"

$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$ProfileA = Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\ahootsa_realtime_es"
$DirectFiles = @(
    "actividades_comunicacion.py",
    "listar_actividades_comunicacion.py",
    "iniciar_actividad_comunicacion.py",
    "list_communication_activity_levels.py",
    "list_communication_activities.py",
    "start_communication_activity.py"
)

foreach ($Name in $DirectFiles) {
    $Path = Join-Path $ProfileA $Name
    if (Test-Path -LiteralPath $Path) {
        $Txt = Get-Content -Raw -Encoding UTF8 -LiteralPath $Path
        Write-Host "$Name needs_response_false =" ($Txt -match "needs_response\s*=\s*False")
    } else {
        Write-Host "$Name needs_response_false = MISSING"
    }
}

try {
    $Status = Invoke-RestMethod -Uri "http://localhost:7860/status" -Method Get -TimeoutSec 5
    Write-Host "Ahootsa /status responde = True"
} catch {
    Write-Host "Ahootsa /status responde = False"
}
