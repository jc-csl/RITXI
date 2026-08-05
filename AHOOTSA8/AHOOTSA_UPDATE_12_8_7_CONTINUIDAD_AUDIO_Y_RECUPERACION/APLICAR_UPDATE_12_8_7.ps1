param(
    [string]$ProjectRoot = "D:\RITXI\AHOOTSA8"
)

$ErrorActionPreference = "Stop"

$SourceRoot = $PSScriptRoot
$PayloadRoot = Join-Path $SourceRoot "payload"
$ServerRoot = Join-Path $ProjectRoot "ahootsa_local_server"
$AppRoot = Join-Path $ProjectRoot "reachy_mini_conversation_app"
$ExternalContentRoot = Join-Path $AppRoot "external_content"
$PanelRoot = Join-Path $ServerRoot "app\static\panel"
$DocumentationRoot = Join-Path $ProjectRoot "documentacion"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupRoot = Join-Path `
    $ServerRoot `
    "backups\antes_update_12_8_7_$Timestamp"
$PythonServer = Join-Path $ServerRoot ".venv\Scripts\python.exe"
$PythonApp = Join-Path $AppRoot ".venv\Scripts\python.exe"
$Cleaner = Join-Path $ProjectRoot "LIMPIAR_PROCESOS_AHOOTSA.ps1"
$ActiveSessionFile = Join-Path $ServerRoot "data\active_session.json"

$AnonymousProfile = Join-Path `
    $ExternalContentRoot `
    "external_profiles\ahootsa"
$SessionProfile = Join-Path `
    $ExternalContentRoot `
    "external_profiles\ahootsa_session"
$SessionTemplate = Join-Path `
    $ExternalContentRoot `
    "profile_defaults\ahootsa_default"
$DanceToolTarget = Join-Path `
    $ExternalContentRoot `
    "external_tools\ahootsa_dances.py"
$SessionServiceTarget = Join-Path `
    $ServerRoot `
    "app\session_preparation_service.py"

$VoiceSource = Join-Path $PayloadRoot "profiles\voice.txt"
$VoiceBlockPath = Join-Path `
    $PayloadRoot `
    "profiles\VOICE_INSTRUCTION_BLOCK.txt"
$DanceBlockPath = Join-Path `
    $PayloadRoot `
    "profiles\DANCE_COMPLETION_BLOCK.txt"
$GreetingBlockPath = Join-Path `
    $PayloadRoot `
    "profiles\SESSION_GREETING_BLOCK.txt"
$ShortTurnsBlockPath = Join-Path `
    $PayloadRoot `
    "profiles\SHORT_TURNS_AUDIO_BLOCK.txt"
$RecoveryScriptSource = Join-Path `
    $SourceRoot `
    "RECUPERAR_AUDIO_SESION.ps1"
$RecoveryScriptTarget = Join-Path `
    $ProjectRoot `
    "RECUPERAR_AUDIO_SESION.ps1"

function Test-PowerShellFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $Tokens = $null
    $Errors = $null

    [System.Management.Automation.Language.Parser]::ParseFile(
        $Path,
        [ref]$Tokens,
        [ref]$Errors
    ) | Out-Null

    if ($Errors.Count -gt 0) {
        Write-Host "ERRORES EN: $Path" -ForegroundColor Red

        foreach ($Item in $Errors) {
            Write-Host $Item.Message -ForegroundColor Yellow
        }

        throw "El script PowerShell no es válido."
    }
}

function Write-Utf8NoBom {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [string]$Text
    )

    [System.IO.File]::WriteAllText(
        $Path,
        $Text,
        (New-Object System.Text.UTF8Encoding($false))
    )
}

function Backup-File {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path $Path)) {
        return
    }

    $SafeName = $Path -replace ':', ''
    $SafeName = $SafeName -replace '\\', '__'
    $Destination = Join-Path $BackupRoot $SafeName
    $DestinationParent = Split-Path $Destination -Parent

    New-Item `
        -ItemType Directory `
        -Path $DestinationParent `
        -Force |
        Out-Null

    Copy-Item $Path $Destination -Force
}

function Update-MarkedInstructionBlock {
    param(
        [Parameter(Mandatory = $true)]
        [string]$InstructionsPath,

        [Parameter(Mandatory = $true)]
        [string]$StartMarker,

        [Parameter(Mandatory = $true)]
        [string]$EndMarker,

        [Parameter(Mandatory = $true)]
        [string]$BlockText
    )

    if (-not (Test-Path $InstructionsPath)) {
        throw "No se encuentra: $InstructionsPath"
    }

    $Text = Get-Content $InstructionsPath -Raw -Encoding UTF8
    $Pattern = (
        '(?s)\s*' +
        [regex]::Escape($StartMarker) +
        '.*?' +
        [regex]::Escape($EndMarker) +
        '\s*'
    )
    $Text = [regex]::Replace($Text, $Pattern, '')
    $Updated = $BlockText.Trim() + "`r`n`r`n" + $Text.TrimStart()

    Write-Utf8NoBom `
        -Path $InstructionsPath `
        -Text $Updated
}

function Copy-CompleteProfile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Source,

        [Parameter(Mandatory = $true)]
        [string]$Destination
    )

    foreach ($Name in @(
        "instructions.txt",
        "greeting.txt",
        "tools.txt",
        "voice.txt"
    )) {
        $SourceFile = Join-Path $Source $Name

        if (-not (Test-Path $SourceFile)) {
            throw "Falta en la plantilla: $SourceFile"
        }
    }

    if (Test-Path $Destination) {
        Remove-Item $Destination -Recurse -Force
    }

    New-Item `
        -ItemType Directory `
        -Path $Destination `
        -Force |
        Out-Null

    foreach ($Name in @(
        "instructions.txt",
        "greeting.txt",
        "tools.txt",
        "voice.txt"
    )) {
        Copy-Item `
            (Join-Path $Source $Name) `
            (Join-Path $Destination $Name) `
            -Force
    }
}

foreach ($File in @(
    Get-ChildItem `
        -Path $SourceRoot `
        -Recurse `
        -File `
        -Filter "*.ps1"
)) {
    Test-PowerShellFile -Path $File.FullName
}

foreach ($RequiredPath in @(
    (Join-Path $ServerRoot "app\main.py"),
    $SessionServiceTarget,
    $DanceToolTarget,
    $AnonymousProfile,
    $SessionProfile,
    $SessionTemplate,
    $VoiceSource,
    $VoiceBlockPath,
    $DanceBlockPath,
    $GreetingBlockPath,
    $ShortTurnsBlockPath,
    $RecoveryScriptSource
)) {
    if (-not (Test-Path $RequiredPath)) {
        throw "No se encuentra el componente requerido: $RequiredPath"
    }
}

if (Test-Path $ActiveSessionFile) {
    throw (
        "Existe una sesión preparada o activa. Finalízala antes de " +
        "instalar: $ActiveSessionFile"
    )
}

if (Test-Path $Cleaner) {
    Write-Host "Deteniendo los servicios Ahootsa..." -ForegroundColor Cyan
    & $Cleaner

    if ($LASTEXITCODE -ne 0) {
        throw "No se pudieron detener todos los servicios."
    }
}

New-Item -ItemType Directory -Path $BackupRoot -Force | Out-Null
New-Item -ItemType Directory -Path $PanelRoot -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $ServerRoot "tools") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $ServerRoot "docs") -Force | Out-Null

foreach ($Current in @(
    (Join-Path $ServerRoot "app\panel_mvp.py"),
    $SessionServiceTarget,
    (Join-Path $ServerRoot "tools\ahootsa_session_report.py"),
    (Join-Path $PanelRoot "panel_inline_12_8_5.html"),
    $DanceToolTarget,
    (Join-Path $ProjectRoot "INICIAR_AHOOTSA_SESION.ps1"),
    (Join-Path $ProjectRoot "scripts\iniciar_servidor_local.ps1"),
    $RecoveryScriptTarget,
    (Join-Path $DocumentationRoot "02_CONFIGURACION_AHOOTSA.md"),
    (Join-Path $DocumentationRoot "10_CAMBIOS_12_8_6_BAILES_Y_SALUDOS.md"),
    (Join-Path $DocumentationRoot "MANUAL_COMPLETO_AHOOTSA8.docx")
)) {
    Backup-File -Path $Current
}

foreach ($ProfilePath in @(
    $AnonymousProfile,
    $SessionProfile,
    $SessionTemplate
)) {
    foreach ($Name in @(
        "instructions.txt",
        "greeting.txt",
        "tools.txt",
        "voice.txt"
    )) {
        Backup-File -Path (Join-Path $ProfilePath $Name)
    }
}

Copy-Item `
    (Join-Path $PayloadRoot "app\panel_mvp.py") `
    (Join-Path $ServerRoot "app\panel_mvp.py") `
    -Force

Copy-Item `
    (Join-Path $PayloadRoot "app\session_preparation_service.py") `
    $SessionServiceTarget `
    -Force

Copy-Item `
    (Join-Path $PayloadRoot "tools\ahootsa_session_report.py") `
    (Join-Path $ServerRoot "tools\ahootsa_session_report.py") `
    -Force

Copy-Item `
    (Join-Path $PayloadRoot "app\static\panel\panel_inline_12_8_5.html") `
    (Join-Path $PanelRoot "panel_inline_12_8_5.html") `
    -Force

Copy-Item `
    (Join-Path $PayloadRoot "external_tools\ahootsa_dances.py") `
    $DanceToolTarget `
    -Force

Copy-Item `
    (Join-Path $PayloadRoot "INICIAR_AHOOTSA_SESION.ps1") `
    (Join-Path $ProjectRoot "INICIAR_AHOOTSA_SESION.ps1") `
    -Force

Copy-Item `
    (Join-Path $PayloadRoot "iniciar_servidor_local.ps1") `
    (Join-Path $ProjectRoot "scripts\iniciar_servidor_local.ps1") `
    -Force

Copy-Item `
    $RecoveryScriptSource `
    $RecoveryScriptTarget `
    -Force

$VoiceBlock = Get-Content $VoiceBlockPath -Raw -Encoding UTF8
$DanceBlock = Get-Content $DanceBlockPath -Raw -Encoding UTF8
$GreetingBlock = Get-Content $GreetingBlockPath -Raw -Encoding UTF8
$ShortTurnsBlock = Get-Content `
    $ShortTurnsBlockPath `
    -Raw `
    -Encoding UTF8

foreach ($ProfilePath in @(
    $AnonymousProfile,
    $SessionTemplate
)) {
    Copy-Item `
        $VoiceSource `
        (Join-Path $ProfilePath "voice.txt") `
        -Force

    Update-MarkedInstructionBlock `
        -InstructionsPath (Join-Path $ProfilePath "instructions.txt") `
        -StartMarker "INICIO_AHOOTSA_VOZ_SOHEE_12_8_5" `
        -EndMarker "FIN_AHOOTSA_VOZ_SOHEE_12_8_5" `
        -BlockText $VoiceBlock

    Update-MarkedInstructionBlock `
        -InstructionsPath (Join-Path $ProfilePath "instructions.txt") `
        -StartMarker "INICIO_AHOOTSA_BAILE_CONTINUA_12_8_6" `
        -EndMarker "FIN_AHOOTSA_BAILE_CONTINUA_12_8_6" `
        -BlockText $DanceBlock

    Update-MarkedInstructionBlock `
        -InstructionsPath (Join-Path $ProfilePath "instructions.txt") `
        -StartMarker "INICIO_AHOOTSA_CONTINUIDAD_AUDIO_12_8_7" `
        -EndMarker "FIN_AHOOTSA_CONTINUIDAD_AUDIO_12_8_7" `
        -BlockText $ShortTurnsBlock
}

Update-MarkedInstructionBlock `
    -InstructionsPath (Join-Path $SessionTemplate "instructions.txt") `
    -StartMarker "INICIO_AHOOTSA_SALUDO_SESION_12_8_6" `
    -EndMarker "FIN_AHOOTSA_SALUDO_SESION_12_8_6" `
    -BlockText $GreetingBlock

# No hay una sesión activa: se deja ahootsa_session limpio y exactamente
# reconstruido desde la plantilla permanente actualizada.
Copy-CompleteProfile `
    -Source $SessionTemplate `
    -Destination $SessionProfile

foreach ($PythonFile in @(
    (Join-Path $ServerRoot "app\main.py"),
    (Join-Path $ServerRoot "app\panel_mvp.py")
)) {
    if (Test-Path $PythonFile) {
        $Text = Get-Content $PythonFile -Raw -Encoding UTF8
        $Text = [regex]::Replace(
            $Text,
            '0\.12\.\d+(?:\.\d+)?',
            '0.12.8.7'
        )

        Write-Utf8NoBom -Path $PythonFile -Text $Text
    }
}

Copy-Item `
    (Join-Path $SourceRoot "docs\UPDATE_12_8_6.md") `
    (Join-Path $ServerRoot "docs\UPDATE_12_8_6.md") `
    -Force

Copy-Item `
    (Join-Path $SourceRoot "docs\ARQUITECTURA_FUNCIONALIDAD.md") `
    (Join-Path $ServerRoot "docs\ARQUITECTURA_FUNCIONALIDAD.md") `
    -Force

Copy-Item `
    (Join-Path $SourceRoot "docs\UPDATE_12_8_7.md") `
    (Join-Path $ServerRoot "docs\UPDATE_12_8_7.md") `
    -Force

if (Test-Path $DocumentationRoot) {
    Copy-Item `
        (Join-Path $SourceRoot "docs\02_CONFIGURACION_AHOOTSA.md") `
        (Join-Path $DocumentationRoot "02_CONFIGURACION_AHOOTSA.md") `
        -Force

    Copy-Item `
        (Join-Path $SourceRoot "docs\10_CAMBIOS_12_8_6_BAILES_Y_SALUDOS.md") `
        (Join-Path $DocumentationRoot "10_CAMBIOS_12_8_6_BAILES_Y_SALUDOS.md") `
        -Force

    Copy-Item `
        (Join-Path $SourceRoot "docs\MANUAL_COMPLETO_AHOOTSA8.docx") `
        (Join-Path $DocumentationRoot "MANUAL_COMPLETO_AHOOTSA8.docx") `
        -Force
}

Get-ChildItem `
    (Join-Path $ServerRoot "app") `
    -Directory `
    -Recurse `
    -Force `
    -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -eq "__pycache__" } |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

Get-ChildItem `
    (Join-Path $ExternalContentRoot "external_tools") `
    -Directory `
    -Recurse `
    -Force `
    -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -eq "__pycache__" } |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

if (Test-Path $PythonServer) {
    & $PythonServer `
        -m py_compile `
        (Join-Path $ServerRoot "app\panel_mvp.py") `
        $SessionServiceTarget `
        (Join-Path $ServerRoot "tools\ahootsa_session_report.py")

    if ($LASTEXITCODE -ne 0) {
        throw "Los archivos Python del servidor no superan py_compile."
    }
}

if (Test-Path $PythonApp) {
    & $PythonApp -m py_compile $DanceToolTarget

    if ($LASTEXITCODE -ne 0) {
        throw "La herramienta de baile no supera py_compile."
    }
}

foreach ($ProfilePath in @(
    $AnonymousProfile,
    $SessionProfile,
    $SessionTemplate
)) {
    $Voice = (
        Get-Content `
            (Join-Path $ProfilePath "voice.txt") `
            -Raw `
            -Encoding UTF8
    ).Trim()

    if ($Voice -ne "Sohee") {
        throw "La voz no quedó configurada como Sohee: $ProfilePath"
    }

    $Instructions = Get-Content `
        (Join-Path $ProfilePath "instructions.txt") `
        -Raw `
        -Encoding UTF8

    if ($Instructions -notmatch "INICIO_AHOOTSA_BAILE_CONTINUA_12_8_6") {
        throw "Faltan instrucciones de finalización de baile: $ProfilePath"
    }

    if ($Instructions -notmatch "INICIO_AHOOTSA_CONTINUIDAD_AUDIO_12_8_7") {
        throw "Faltan instrucciones de turnos cortos: $ProfilePath"
    }
}

$TemplateInstructions = Get-Content `
    (Join-Path $SessionTemplate "instructions.txt") `
    -Raw `
    -Encoding UTF8

if ($TemplateInstructions -notmatch "INICIO_AHOOTSA_SALUDO_SESION_12_8_6") {
    throw "Faltan instrucciones permanentes del saludo de sesión."
}

$DanceText = Get-Content $DanceToolTarget -Raw -Encoding UTF8
$ServiceText = Get-Content $SessionServiceTarget -Raw -Encoding UTF8

if ($DanceText -notmatch 'AHOOTSA_DANCES_VERSION = "1.4"') {
    throw "No quedó instalada la herramienta de baile 1.4."
}

if ($DanceText -notmatch 'needs_response = True') {
    throw "El baile no quedó configurado para continuar la conversación."
}

if ($ServiceText -notmatch '_build_session_greeting') {
    throw "No quedó instalado el saludo personalizado."
}

if ($ServiceText -notmatch 'greeting_uses_interests') {
    throw "No quedó instalado el uso de intereses en el saludo."
}

Write-Host ""
Write-Host "UPDATE 12.8.7 INSTALADO CORRECTAMENTE." -ForegroundColor Green
Write-Host "Voz Sohee: MANTENIDA." -ForegroundColor Cyan
Write-Host "Edición estable del panel: INCLUIDA." -ForegroundColor Cyan
Write-Host "Informes de sesión: CORREGIDOS." -ForegroundColor Cyan
Write-Host "Saludo literal con nombre: INSTALADO." -ForegroundColor Cyan
Write-Host "Saludo con intereses registrados: INSTALADO." -ForegroundColor Cyan
Write-Host "Finalización automática de bailes: INSTALADA." -ForegroundColor Cyan
Write-Host "Continuación hablada tras el baile: INSTALADA." -ForegroundColor Cyan
Write-Host "Turnos y relatos breves: INSTALADOS." -ForegroundColor Cyan
Write-Host "Recuperación de audio sin cerrar sesión: INSTALADA." -ForegroundColor Cyan
Write-Host "Detección de posible bloqueo en informes: INSTALADA." -ForegroundColor Cyan
Write-Host "Versión del servidor: 0.12.8.7" -ForegroundColor Cyan
Write-Host "Backup: $BackupRoot" -ForegroundColor Gray
Write-Host ""
Write-Host "Arranque:" -ForegroundColor Yellow
Write-Host "  cd $ProjectRoot" -ForegroundColor Gray
Write-Host "  .\INICIAR_AHOOTSA_SESION.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "Panel:" -ForegroundColor Yellow
Write-Host "  http://127.0.0.1:8100/panel-12-8-5" -ForegroundColor Gray
