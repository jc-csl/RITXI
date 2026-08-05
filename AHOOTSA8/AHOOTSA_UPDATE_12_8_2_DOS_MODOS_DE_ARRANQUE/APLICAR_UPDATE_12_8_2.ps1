param(
    [string]$ProjectRoot = "D:\RITXI\AHOOTSA8"
)

$ErrorActionPreference = "Stop"

$SourceRoot = $PSScriptRoot
$PayloadRoot = Join-Path $SourceRoot "payload"
$ServerRoot = Join-Path $ProjectRoot "ahootsa_local_server"
$ConfigPath = Join-Path $ServerRoot "config\panel_config.json"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupRoot = Join-Path $ServerRoot "backups\antes_update_12_8_2_$Timestamp"
$ObsoleteBackup = Join-Path $BackupRoot "scripts_sustituidos"
$PythonExe = Join-Path $ServerRoot ".venv\Scripts\python.exe"

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
        Write-Host ""
        Write-Host "ERRORES DE SINTAXIS EN: $Path" -ForegroundColor Red

        foreach ($Item in $Errors) {
            Write-Host $Item.Message -ForegroundColor Yellow
        }

        throw "El paquete contiene un script PowerShell no válido."
    }
}

if (-not (Test-Path $PayloadRoot)) {
    throw "Falta la carpeta interna payload."
}

Write-Host ""
Write-Host "COMPROBANDO EL PAQUETE 12.8.2..." -ForegroundColor Cyan

foreach ($File in @(
    Get-ChildItem `
        -Path $SourceRoot `
        -Recurse `
        -File `
        -Filter "*.ps1"
)) {
    Test-PowerShellFile -Path $File.FullName
}

Write-Host "Sintaxis PowerShell del paquete: OK" -ForegroundColor Green

if (-not (Test-Path (Join-Path $ServerRoot "app\main.py"))) {
    throw "No se encuentra la instalación principal: $ServerRoot"
}

if (-not (Test-Path $ConfigPath)) {
    throw "No se encuentra panel_config.json: $ConfigPath"
}

$PayloadUtils = Join-Path $PayloadRoot "scripts\ahootsa_process_utils.ps1"
. $PayloadUtils

Write-Host "Cerrando servicios anteriores..." -ForegroundColor Cyan

Stop-AhootsaConversationAppGracefully | Out-Null

foreach ($Definition in @(
    @{
        Port = 7860
        Name = "Conversation App"
    },
    @{
        Port = 8100
        Name = "Ahootsa Local Server"
    },
    @{
        Port = 8000
        Name = "Reachy Mini daemon"
    }
)) {
    Stop-AhootsaPortProcess `
        -Port $Definition.Port `
        -ServiceName $Definition.Name |
        Out-Null
}

New-Item -ItemType Directory -Path $BackupRoot -Force | Out-Null
New-Item -ItemType Directory -Path $ObsoleteBackup -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $ProjectRoot "scripts") -Force | Out-Null

$AccidentalBackup = Join-Path $BackupRoot "extraccion_incorrecta"
New-Item -ItemType Directory -Path $AccidentalBackup -Force | Out-Null

$AccidentalPayload = Join-Path $ProjectRoot "payload"
$PayloadMarker = Join-Path $AccidentalPayload "scripts\ahootsa_process_utils.ps1"
$PayloadStartMarker = Join-Path $AccidentalPayload "INICIAR_AHOOTSA.ps1"

if (
    (Test-Path $AccidentalPayload) -and
    (Test-Path $PayloadMarker) -and
    (Test-Path $PayloadStartMarker)
) {
    Write-Host (
        "Archivando la carpeta payload extraída por error en la raíz..."
    ) -ForegroundColor Yellow

    Move-Item `
        $AccidentalPayload `
        (Join-Path $AccidentalBackup "payload") `
        -Force
}

foreach ($AccidentalFile in @(
    "APLICAR_UPDATE_12_8.ps1",
    "COMPROBAR_PAQUETE_12_8.ps1",
    "INSTRUCCIONES_UPDATE_12_8.txt",
    "APLICAR_UPDATE_12_8_1.ps1",
    "COMPROBAR_PAQUETE_12_8_1.ps1",
    "INSTRUCCIONES_UPDATE_12_8_1.txt"
)) {
    $Path = Join-Path $ProjectRoot $AccidentalFile

    if (Test-Path $Path) {
        Move-Item `
            $Path `
            (Join-Path $AccidentalBackup $AccidentalFile) `
            -Force
    }
}
New-Item -ItemType Directory -Path (Join-Path $ServerRoot "tools") -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $ServerRoot "docs") -Force | Out-Null

foreach ($Current in @(
    (Join-Path $ProjectRoot "INICIAR_AHOOTSA.ps1"),
    (Join-Path $ProjectRoot "INICIAR_AHOOTSA_ANONIMO.ps1"),
    (Join-Path $ProjectRoot "INICIAR_AHOOTSA_SESION.ps1"),
    (Join-Path $ProjectRoot "FINALIZAR_SESION_AHOOTSA.ps1"),
    (Join-Path $ProjectRoot "COMPROBAR_AHOOTSA.ps1"),
    (Join-Path $ProjectRoot "LIMPIAR_PROCESOS_AHOOTSA.ps1"),
    (Join-Path $ProjectRoot "scripts\iniciar_conversation_app.ps1"),
    (Join-Path $ProjectRoot "scripts\iniciar_conversation_anonima.ps1"),
    (Join-Path $ProjectRoot "scripts\iniciar_conversation_sesion.ps1"),
    (Join-Path $ProjectRoot "scripts\ahootsa_process_utils.ps1"),
    (Join-Path $ProjectRoot "scripts\iniciar_servidor_local.ps1"),
    (Join-Path $ProjectRoot "scripts\iniciar_daemon_mujoco.ps1"),
    (Join-Path $ServerRoot "app\main.py"),
    (Join-Path $ServerRoot "app\panel_mvp.py"),
    (Join-Path $ServerRoot "tools\ahootsa_session_report.py"),
    $ConfigPath
)) {
    if (Test-Path $Current) {
        Copy-Item `
            $Current `
            (Join-Path $BackupRoot (Split-Path $Current -Leaf)) `
            -Force
    }
}

foreach ($Name in @(
    "INICIAR_AHOOTSA.ps1",
    "0_detener_servicios_ahootsa.ps1",
    "1_lanzar_daemon_mujoco.ps1",
    "2_lanzar_app_ahootsa.ps1",
    "3_abrir_paneles_control.ps1",
    "COMPROBAR_SERVICIOS_AHOOTSA.ps1",
    "PROBAR_AHOOTSA_COMPLETO.ps1"
)) {
    $Path = Join-Path $ProjectRoot $Name

    if (Test-Path $Path) {
        Move-Item `
            $Path `
            (Join-Path $ObsoleteBackup $Name) `
            -Force
    }
}

$OldConversationLauncher = Join-Path `
    $ProjectRoot `
    "scripts\iniciar_conversation_app.ps1"

if (Test-Path $OldConversationLauncher) {
    Move-Item `
        $OldConversationLauncher `
        (Join-Path $ObsoleteBackup "iniciar_conversation_app.ps1") `
        -Force
}

foreach ($Name in @(
    "INICIAR_AHOOTSA_ANONIMO.ps1",
    "INICIAR_AHOOTSA_SESION.ps1",
    "FINALIZAR_SESION_AHOOTSA.ps1",
    "COMPROBAR_AHOOTSA.ps1",
    "LIMPIAR_PROCESOS_AHOOTSA.ps1"
)) {
    Copy-Item `
        (Join-Path $PayloadRoot $Name) `
        (Join-Path $ProjectRoot $Name) `
        -Force
}

foreach ($Name in @(
    "ahootsa_process_utils.ps1",
    "iniciar_servidor_local.ps1",
    "iniciar_daemon_mujoco.ps1",
    "iniciar_conversation_anonima.ps1",
    "iniciar_conversation_sesion.ps1"
)) {
    Copy-Item `
        (Join-Path $PayloadRoot "scripts\$Name") `
        (Join-Path $ProjectRoot "scripts\$Name") `
        -Force
}

Copy-Item `
    (Join-Path $PayloadRoot "tools\ahootsa_session_report.py") `
    (Join-Path $ServerRoot "tools\ahootsa_session_report.py") `
    -Force

Copy-Item `
    (Join-Path $PayloadRoot "app\panel_mvp.py") `
    (Join-Path $ServerRoot "app\panel_mvp.py") `
    -Force

$Config = Get-Content $ConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json
$Config.daemon_script = "../scripts/iniciar_daemon_mujoco.ps1"
$Config.manual_app_script = "../scripts/iniciar_conversation_sesion.ps1"
$ConfigJson = $Config | ConvertTo-Json -Depth 20

[System.IO.File]::WriteAllText(
    $ConfigPath,
    $ConfigJson,
    (New-Object System.Text.UTF8Encoding($false))
)

foreach ($PythonFile in @(
    (Join-Path $ServerRoot "app\main.py"),
    (Join-Path $ServerRoot "app\panel_mvp.py")
)) {
    if (Test-Path $PythonFile) {
        $Text = Get-Content $PythonFile -Raw -Encoding UTF8
        $Text = [regex]::Replace(
            $Text,
            '0\.12\.\d+(?:\.\d+)?',
            '0.12.8.2'
        )

        [System.IO.File]::WriteAllText(
            $PythonFile,
            $Text,
            (New-Object System.Text.UTF8Encoding($false))
        )
    }
}

Copy-Item `
    (Join-Path $SourceRoot "docs\UPDATE_12_8_2.md") `
    (Join-Path $ServerRoot "docs\UPDATE_12_8_2.md") `
    -Force

Copy-Item `
    (Join-Path $SourceRoot "docs\ARQUITECTURA_FUNCIONALIDAD.md") `
    (Join-Path $ServerRoot "docs\ARQUITECTURA_FUNCIONALIDAD.md") `
    -Force

Copy-Item `
    (Join-Path $SourceRoot "INSTRUCCIONES_UPDATE_12_8_2.txt") `
    (Join-Path $ServerRoot "INSTRUCCIONES_UPDATE_12_8_2.txt") `
    -Force

foreach ($Path in @(
    (Join-Path $ProjectRoot "INICIAR_AHOOTSA_ANONIMO.ps1"),
    (Join-Path $ProjectRoot "INICIAR_AHOOTSA_SESION.ps1"),
    (Join-Path $ProjectRoot "FINALIZAR_SESION_AHOOTSA.ps1"),
    (Join-Path $ProjectRoot "COMPROBAR_AHOOTSA.ps1"),
    (Join-Path $ProjectRoot "LIMPIAR_PROCESOS_AHOOTSA.ps1"),
    (Join-Path $ProjectRoot "scripts\ahootsa_process_utils.ps1"),
    (Join-Path $ProjectRoot "scripts\iniciar_servidor_local.ps1"),
    (Join-Path $ProjectRoot "scripts\iniciar_daemon_mujoco.ps1"),
    (Join-Path $ProjectRoot "scripts\iniciar_conversation_anonima.ps1"),
    (Join-Path $ProjectRoot "scripts\iniciar_conversation_sesion.ps1")
)) {
    Test-PowerShellFile -Path $Path
}

if (Test-Path $PythonExe) {
    & $PythonExe `
        -m py_compile `
        (Join-Path $ServerRoot "app\panel_mvp.py") `
        (Join-Path $ServerRoot "tools\ahootsa_session_report.py")

    if ($LASTEXITCODE -ne 0) {
        throw "Los archivos Python no superan py_compile."
    }
}

Write-Host ""
Write-Host "UPDATE 12.8.2 INSTALADO CORRECTAMENTE." -ForegroundColor Green
Write-Host "Versión del servidor: 0.12.8.2" -ForegroundColor Cyan
Write-Host ""
Write-Host "Arranque anónimo:" -ForegroundColor Yellow
Write-Host "  .\INICIAR_AHOOTSA_ANONIMO.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "Arranque con sesión local:" -ForegroundColor Yellow
Write-Host "  .\INICIAR_AHOOTSA_SESION.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "Backup: $BackupRoot" -ForegroundColor Gray
