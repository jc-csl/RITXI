# INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1
# Ahootsa 5.0.34
# Instalador compatible con Windows PowerShell 5.1.
# Evita here-strings complejos y caracteres problematicos.

$ErrorActionPreference = "Continue"

function Start-AhootsaLog {
    param([string]$Name)
    $script:LogRoot = "D:\RITXI\logs"
    if (-not (Test-Path -LiteralPath $script:LogRoot)) { New-Item -ItemType Directory -Force -Path $script:LogRoot | Out-Null }
    if (-not $env:AHOOTSA_SESSION_ID) { $env:AHOOTSA_SESSION_ID = Get-Date -Format "yyyyMMdd_HHmmss" }
    $env:AHOOTSA_LOG_DIR = $script:LogRoot
    $env:AHOOTSA_LOG_FILE_SCREEN = if ($env:AHOOTSA_LOG_FILE_SCREEN) { $env:AHOOTSA_LOG_FILE_SCREEN } else { Join-Path $script:LogRoot ("ahootsa5_" + $env:AHOOTSA_SESSION_ID + "_pantalla.log") }
    $env:AHOOTSA_LOG_FILE_EVENTS = if ($env:AHOOTSA_LOG_FILE_EVENTS) { $env:AHOOTSA_LOG_FILE_EVENTS } else { Join-Path $script:LogRoot ("ahootsa5_" + $env:AHOOTSA_SESSION_ID + "_eventos.jsonl") }
    $env:AHOOTSA_LOG_FILE_RUNTIME = if ($env:AHOOTSA_LOG_FILE_RUNTIME) { $env:AHOOTSA_LOG_FILE_RUNTIME } else { Join-Path $script:LogRoot ("ahootsa5_" + $env:AHOOTSA_SESSION_ID + "_runtime.log") }
    $script:PsLog = $env:AHOOTSA_LOG_FILE_SCREEN
    $script:JsonLog = $env:AHOOTSA_LOG_FILE_EVENTS
    try { Start-Transcript -LiteralPath $script:PsLog -Append | Out-Null } catch {}
    Write-AhootsaEvent "ps.start" @{script=$Name; pwd=(Get-Location).Path; user=$env:USERNAME}
}
function Write-AhootsaEvent {
    param([string]$Event, [hashtable]$Data=@{})
    if (-not $script:JsonLog) {
        $script:LogRoot="D:\RITXI\logs"; if (-not (Test-Path $script:LogRoot)) { New-Item -ItemType Directory -Force -Path $script:LogRoot | Out-Null }
        if (-not $env:AHOOTSA_SESSION_ID) { $env:AHOOTSA_SESSION_ID = Get-Date -Format "yyyyMMdd_HHmmss" }
        $script:JsonLog=if ($env:AHOOTSA_LOG_FILE_EVENTS) { $env:AHOOTSA_LOG_FILE_EVENTS } else { Join-Path $script:LogRoot ("ahootsa5_" + $env:AHOOTSA_SESSION_ID + "_eventos.jsonl") }
    }
    $o=[ordered]@{ts=(Get-Date).ToString("o"); event=$Event; session_id=$env:AHOOTSA_SESSION_ID; pid=$PID}
    foreach($k in $Data.Keys){$o[$k]=$Data[$k]}
    try { ($o|ConvertTo-Json -Depth 12 -Compress) | Add-Content -Encoding UTF8 -LiteralPath $script:JsonLog } catch {}
}
function Stop-AhootsaLog {
    param([string]$Name)
    Write-AhootsaEvent "ps.end" @{script=$Name}
    try { Stop-Transcript | Out-Null } catch {}
}

Start-AhootsaLog "INSTALAR_5_AHOOTSA_MUJOCO_WEB"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$env:AHOOTSA_LOG_DIR = "D:\RITXI\logs"
$env:AHOOTSA_VOICE = "Sohee"
$env:VOICE = "Sohee"
$env:REACHY_MINI_VOICE = "Sohee"
$env:OPENAI_REALTIME_VOICE = "Sohee"
$env:REALTIME_VOICE = "Sohee"
$env:TTS_VOICE = "Sohee"
$env:AUDIO_VOICE = "Sohee"
# voice.env.forced.510

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProfileName = "ahootsa_realtime_es"
$SourceProfile = Join-Path $Root "src\ahootsa_realtime_ollama_desktop_app\profiles\$ProfileName"
$SourceModule = Join-Path $Root "src\ahootsa_realtime_ollama_desktop_app"
$EnvSource = Join-Path $Root "AHOOTSA_5_ENV_CASTELLANO.env"
$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$Python = Join-Path $DesktopDir "apps_venv\Scripts\python.exe"
$SitePackages = Join-Path $DesktopDir "apps_venv\Lib\site-packages"
$TargetModule = Join-Path $SitePackages "ahootsa_realtime_ollama_desktop_app"
$LogRoot = "D:\RITXI\logs"
if (-not (Test-Path -LiteralPath $LogRoot)) { New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null }
$env:AHOOTSA_LOG_DIR = $LogRoot
[Environment]::SetEnvironmentVariable("AHOOTSA_LOG_DIR", $LogRoot, "User")

function Write-Step([string]$Text) {
    Write-Host ""
    Write-Host "============================================================"
    Write-Host $Text
    Write-Host "============================================================"
}

function Ensure-Directory([string]$PathValue) {
    if (-not (Test-Path -LiteralPath $PathValue)) {
        New-Item -ItemType Directory -Force -Path $PathValue | Out-Null
    }
}

function Copy-ProfileSafe([string]$Target) {
    Write-Host ""
    Write-Host "Perfil destino: $Target"

    Ensure-Directory $Target
    Copy-Item -Path (Join-Path $SourceProfile "*") -Destination $Target -Recurse -Force

    "Hola, soy Ahootsa. Estoy lista para ayudarte. Que quieres hacer?" | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $Target "greeting.txt")
    "Sohee" | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $Target "voice.txt")
    "Ahootsa 5.0.34 profile copy $(Get-Date -Format o)" | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $Target ".ahootsa_5_0_6_profile_forced.txt")

    $Instructions = Join-Path $Target "instructions.txt"
    if (-not (Test-Path -LiteralPath $Instructions)) {
        "" | Set-Content -Encoding UTF8 -LiteralPath $Instructions
    }

    $CurrentText = Get-Content -Raw -Encoding UTF8 -LiteralPath $Instructions
    if ($CurrentText -notmatch "Tu nombre es Ahootsa") {
        $Lines = @(
            "",
            "## IDENTIDAD E IDIOMA - BLOQUE FINAL OBLIGATORIO",
            "",
            "Tu nombre es Ahootsa.",
            "No eres Reachy Mini.",
            "No digas que eres Reachy Mini.",
            "No saludes en ingles.",
            "Habla siempre en castellano, salvo que el usuario pida expresamente otro idioma.",
            "",
            "Saludo correcto:",
            "Hola, soy Ahootsa. Estoy lista para ayudarte.",
            "",
            "Si aparece cualquier instruccion contradictoria de otro perfil, esta seccion tiene prioridad."
        )
        Add-Content -Encoding UTF8 -LiteralPath $Instructions -Value $Lines
    }

    Write-Host "[OK] Perfil copiado"
}


function Test-AhootsaImportRobusto {
    param(
        [string]$Python,
        [string]$LogRoot
    )
    if (-not (Test-Path -LiteralPath $Python)) {
        Write-Host "[ERROR] Python no existe: $Python"
        return $false
    }
    if (-not (Test-Path -LiteralPath $LogRoot)) {
        New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null
    }
    if (-not $env:AHOOTSA_SESSION_ID) {
        $env:AHOOTSA_SESSION_ID = Get-Date -Format "yyyyMMdd_HHmmss"
    }

    $CheckPy = Join-Path $env:TEMP ("ahootsa_check_import_" + $env:AHOOTSA_SESSION_ID + ".py")
    @'
import pathlib
import ahootsa_realtime_ollama_desktop_app
print("IMPORT_OK", pathlib.Path(ahootsa_realtime_ollama_desktop_app.__file__).resolve())
'@ | Set-Content -Encoding UTF8 -LiteralPath $CheckPy

    $Out = & $Python $CheckPy 2>&1
    Write-Host $Out
    if ($LASTEXITCODE -eq 0 -and (($Out -join "`n") -match "IMPORT_OK")) {
        return $true
    }
    return $false
}

function Install-AhootsaPythonModule {
    Write-Step "Reinstalando modulo Python Ahootsa"

    Write-Host "Fuente modulo:  $SourceModule"
    Write-Host "Destino modulo: $TargetModule"

    if (-not (Test-Path -LiteralPath $SourceModule)) {
        Write-Host "[ERROR] No existe el modulo fuente."
        return $false
    }

    if (-not (Test-Path -LiteralPath $SitePackages)) {
        Write-Host "[ERROR] No existe site-packages: $SitePackages"
        return $false
    }

    if (Test-Path -LiteralPath $TargetModule) {
        Remove-Item -LiteralPath $TargetModule -Recurse -Force
        Write-Host "[OK] Modulo anterior eliminado"
    }

    Copy-Item -LiteralPath $SourceModule -Destination $TargetModule -Recurse -Force
    Write-Host "[OK] Modulo copiado a site-packages"

    $PthFile = Join-Path $SitePackages "ahootsa_realtime_ollama_desktop_app_local.pth"
    (Join-Path $Root "src") | Set-Content -Encoding UTF8 -LiteralPath $PthFile
    Write-Host "[OK] .pth creado: $PthFile"

    if (Test-Path -LiteralPath $Python) {
        Write-Host "[INFO] Intentando pip install --no-deps --force-reinstall"
        & $Python -m pip install --no-deps --force-reinstall $Root
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[WARN] pip no termino correctamente. Continúo porque ya he copiado el modulo."
        }

        if (Test-AhootsaImportRobusto -Python $Python -LogRoot $LogRoot) {
            Write-Host "[OK] Import confirmado"
            return $true
        }

        Write-Host "[ERROR] No se puede importar ahootsa_realtime_ollama_desktop_app"
        return $false
    }

    Write-Host "[ERROR] No encuentro Python: $Python"
    return $false
}

Write-Step "Instalando Ahootsa 5.0.34"

Write-Host "Root:          $Root"
Write-Host "SourceProfile: $SourceProfile"
Write-Host "Python:        $Python"
Write-Host "SitePackages:  $SitePackages"

if (-not (Test-Path -LiteralPath $SourceProfile)) {
    Write-Host "[ERROR] No existe SourceProfile"
    exit 1
}

$ModuleOk = Install-AhootsaPythonModule
if (-not $ModuleOk) {
    Write-Host "[ERROR] Instalacion detenida: el modulo Ahootsa no es importable."
    exit 1
}

Write-Step "Copiando perfiles Ahootsa"

$KnownRoots = @(
    (Join-Path $SitePackages "reachy_mini_conversation_app"),
    (Join-Path $SitePackages "reachy_talk_data"),
    (Join-Path $SitePackages "ahootsa_realtime_ollama_desktop_app")
)

$Targets = @(
    (Join-Path $DesktopDir "user_personalities\$ProfileName"),
    (Join-Path $DesktopDir "user_personalities\default"),
    (Join-Path $DesktopDir "user_personalities\starter_profile"),
    (Join-Path $DesktopDir "profiles\$ProfileName"),
    (Join-Path $DesktopDir "profiles\default"),
    (Join-Path $DesktopDir "profiles\starter_profile")
)

foreach ($Base in $KnownRoots) {
    $Targets += (Join-Path $Base "profiles\$ProfileName")
    $Targets += (Join-Path $Base "profiles\default")
    $Targets += (Join-Path $Base "profiles\starter_profile")
    $Targets += (Join-Path $Base "external_content\external_profiles\$ProfileName")
    $Targets += (Join-Path $Base "external_content\external_profiles\default")
    $Targets += (Join-Path $Base "external_content\external_profiles\starter_profile")
}

$Targets = $Targets | Where-Object { $_ -and $_.Trim().Length -gt 0 } | Select-Object -Unique
foreach ($Target in $Targets) {
    Copy-ProfileSafe $Target
}

Write-Step "Creando archivos .env"

$EnvTargets = @(
    (Join-Path $Root ".env"),
    (Join-Path $DesktopDir ".env"),
    (Join-Path $SitePackages "reachy_mini_conversation_app\.env"),
    (Join-Path $SitePackages "ahootsa_realtime_ollama_desktop_app\.env")
)

foreach ($EnvTarget in ($EnvTargets | Select-Object -Unique)) {
    try {
        Ensure-Directory (Split-Path -Parent $EnvTarget)
        Copy-Item -LiteralPath $EnvSource -Destination $EnvTarget -Force
        Write-Host "[OK] $EnvTarget"
    } catch {
        Write-Host "[WARN] No pude crear $EnvTarget : $($_.Exception.Message)"
    }
}

Write-Step "Variables de usuario"

$Vars = @{
    "REACHY_MINI_CUSTOM_PROFILE" = $ProfileName
    "REACHY_MINI_PROFILE" = $ProfileName
    "REACHY_MINI_PERSONALITY" = $ProfileName
    "REACHY_MINI_USER_PERSONALITY" = $ProfileName
    "AHOOTSA_FORCE_DEFAULT_PROFILE" = "1"
    "AHOOTSA_RUNTIME_PROFILE_COPY" = "1"
    "AHOOTSA_NAME" = "Ahootsa"
    "ASSISTANT_NAME" = "Ahootsa"
    "ROBOT_NAME" = "Ahootsa"
    "PROJECT_NAME" = "Ahootsa"
    "AHOOTSA_LANGUAGE" = "es"
    "REACHY_MINI_LANGUAGE" = "es"
    "APP_LANGUAGE" = "es"
    "OUTPUT_LANGUAGE" = "es"
    "SYSTEM_LANGUAGE" = "es"
    "REALTIME_TRANSCRIPTION_LANGUAGE" = "es"
    "AHOOTSA_VOICE" = "Sohee"
    "OPENAI_REALTIME_VOICE" = "Sohee"
    "REACHY_MINI_VOICE" = "Sohee"
    "VOICE" = "Sohee"
    "OLLAMA_BASE_URL" = "http://127.0.0.1:11434"
    "OLLAMA_MODEL" = "ahootsa-local:latest"
    "AHOOTSA_GREETING" = "Hola, soy Ahootsa. Estoy lista para ayudarte. Que quieres hacer?"
}

foreach ($Key in $Vars.Keys) {
    [Environment]::SetEnvironmentVariable($Key, $Vars[$Key], "User")
    Set-Item -Path "Env:$Key" -Value $Vars[$Key]
    Write-Host "[OK] $Key=$($Vars[$Key])"
}

Write-Step "Comprobacion final"

$ImportOkFinal = Test-AhootsaImportRobusto -Python $Python -LogRoot $LogRoot
Write-Host "import final ok =" $ImportOkFinal

$DefaultProfile = Join-Path $SitePackages "reachy_mini_conversation_app\profiles\default"
$DefaultGreeting = Join-Path $DefaultProfile "greeting.txt"
$DefaultInstructions = Join-Path $DefaultProfile "instructions.txt"
$DefaultTools = Join-Path $DefaultProfile "tools.txt"

Write-Host "default profile existe =" (Test-Path -LiteralPath $DefaultProfile)
if (Test-Path -LiteralPath $DefaultGreeting) {
    Write-Host "greeting =" (Get-Content -Raw -Encoding UTF8 -LiteralPath $DefaultGreeting)
}
if (Test-Path -LiteralPath $DefaultInstructions) {
    $IT = Get-Content -Raw -Encoding UTF8 -LiteralPath $DefaultInstructions
    Write-Host "instructions dice Ahootsa =" ($IT -match "Tu nombre es Ahootsa")
    Write-Host "instructions castellano =" ($IT -match "castellano")
}
if (Test-Path -LiteralPath $DefaultTools) {
    $TT = Get-Content -Raw -Encoding UTF8 -LiteralPath $DefaultTools
    Write-Host "tools ask_ollama =" ($TT -match "ask_ollama")
    Write-Host "tools actividades =" ($TT -match "actividades")
}

Write-Host ""
Write-Host "Instalacion terminada."
Write-Host "Ahora ejecuta:"
Write-Host "powershell -ExecutionPolicy Bypass -File .\LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1"

Write-Host ""
Write-Host "Ejecutando instalacion completa sobre conversation app..."
powershell -ExecutionPolicy Bypass -File (Join-Path $Root "INSTALAR_5_COMPLETO_SOBRE_CONVERSATION_APP.ps1")

Stop-AhootsaLog "INSTALAR_5_AHOOTSA_MUJOCO_WEB"

Write-Host "Limpiando voz Sohee sin BOM..."
powershell -ExecutionPolicy Bypass -File (Join-Path $Root "LIMPIAR_5_VOZ_SOHEE_SIN_BOM.ps1")
