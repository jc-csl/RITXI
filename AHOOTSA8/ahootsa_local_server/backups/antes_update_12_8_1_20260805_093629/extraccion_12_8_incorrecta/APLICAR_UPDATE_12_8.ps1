param(
    [string]$ProjectRoot = "D:\RITXI\AHOOTSA8"
)

$ErrorActionPreference = "Stop"

$SourceRoot = $PSScriptRoot
$PayloadRoot = Join-Path $SourceRoot "payload"
$ServerRoot = Join-Path $ProjectRoot "ahootsa_local_server"
$ConfigPath = Join-Path $ServerRoot "config\panel_config.json"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupRoot = Join-Path `
    $ServerRoot `
    "backups\antes_update_12_8_$Timestamp"
$ObsoleteBackup = Join-Path `
    $BackupRoot `
    "scripts_obsoletos"
$PythonExe = Join-Path `
    $ServerRoot `
    ".venv\Scripts\python.exe"

if (-not (Test-Path (Join-Path $ServerRoot "app\main.py"))) {
    throw "No se encuentra la instalación principal: $ServerRoot"
}

if (-not (Test-Path $ConfigPath)) {
    throw "No se encuentra panel_config.json: $ConfigPath"
}

$PayloadUtils = Join-Path `
    $PayloadRoot `
    "scripts\ahootsa_process_utils.ps1"

if (-not (Test-Path $PayloadUtils)) {
    throw "Falta la utilidad de procesos del paquete."
}

. $PayloadUtils

Write-Host ""
Write-Host "INSTALANDO AHOOTSA 12.8" -ForegroundColor Cyan
Write-Host ""

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

New-Item `
    -ItemType Directory `
    -Path $BackupRoot `
    -Force |
    Out-Null

New-Item `
    -ItemType Directory `
    -Path $ObsoleteBackup `
    -Force |
    Out-Null

New-Item `
    -ItemType Directory `
    -Path (Join-Path $ProjectRoot "scripts") `
    -Force |
    Out-Null

New-Item `
    -ItemType Directory `
    -Path (Join-Path $ServerRoot "tools") `
    -Force |
    Out-Null

New-Item `
    -ItemType Directory `
    -Path (Join-Path $ServerRoot "docs") `
    -Force |
    Out-Null

foreach ($Current in @(
    (Join-Path $ProjectRoot "INICIAR_AHOOTSA.ps1"),
    (Join-Path $ProjectRoot "FINALIZAR_SESION_AHOOTSA.ps1"),
    (Join-Path $ProjectRoot "COMPROBAR_AHOOTSA.ps1"),
    (Join-Path $ProjectRoot "LIMPIAR_PROCESOS_AHOOTSA.ps1"),
    (Join-Path $ProjectRoot "scripts\ahootsa_process_utils.ps1"),
    (Join-Path $ProjectRoot "scripts\iniciar_servidor_local.ps1"),
    (Join-Path $ProjectRoot "scripts\iniciar_daemon_mujoco.ps1"),
    (Join-Path $ProjectRoot "scripts\iniciar_conversation_app.ps1"),
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

$ObsoleteRootScripts = @(
    "0_detener_servicios_ahootsa.ps1",
    "1_lanzar_daemon_mujoco.ps1",
    "2_lanzar_app_ahootsa.ps1",
    "3_abrir_paneles_control.ps1",
    "COMPROBAR_SERVICIOS_AHOOTSA.ps1",
    "PROBAR_AHOOTSA_COMPLETO.ps1",
    "LIMPIAR_AHOOTSA8.ps1",
    "FINALIZAR_LIMPIEZA_AHOOTSA8.ps1",
    "COMPROBAR_ESTRUCTURA_LIMPIA_12_5_1.ps1",
    "ABRIR_CONTROLES_AHOOTSA.ps1",
    "ABRIR_CONTROLES_AHOOTSA_COMPROBANDO_PUERTOS.ps1"
)

foreach ($Name in $ObsoleteRootScripts) {
    $Path = Join-Path $ProjectRoot $Name

    if (Test-Path $Path) {
        Move-Item `
            $Path `
            (Join-Path $ObsoleteBackup $Name) `
            -Force
    }
}

$OldServerLauncher = Join-Path `
    $ServerRoot `
    "3_lanzar_ahootsa_server.ps1"

if (Test-Path $OldServerLauncher) {
    Move-Item `
        $OldServerLauncher `
        (Join-Path $ObsoleteBackup "3_lanzar_ahootsa_server.ps1") `
        -Force
}

Copy-Item `
    (Join-Path $PayloadRoot "INICIAR_AHOOTSA.ps1") `
    (Join-Path $ProjectRoot "INICIAR_AHOOTSA.ps1") `
    -Force

Copy-Item `
    (Join-Path $PayloadRoot "FINALIZAR_SESION_AHOOTSA.ps1") `
    (Join-Path $ProjectRoot "FINALIZAR_SESION_AHOOTSA.ps1") `
    -Force

Copy-Item `
    (Join-Path $PayloadRoot "COMPROBAR_AHOOTSA.ps1") `
    (Join-Path $ProjectRoot "COMPROBAR_AHOOTSA.ps1") `
    -Force

Copy-Item `
    (Join-Path $PayloadRoot "LIMPIAR_PROCESOS_AHOOTSA.ps1") `
    (Join-Path $ProjectRoot "LIMPIAR_PROCESOS_AHOOTSA.ps1") `
    -Force

Copy-Item `
    (Join-Path $PayloadRoot "scripts\ahootsa_process_utils.ps1") `
    (Join-Path $ProjectRoot "scripts\ahootsa_process_utils.ps1") `
    -Force

Copy-Item `
    (Join-Path $PayloadRoot "scripts\iniciar_servidor_local.ps1") `
    (Join-Path $ProjectRoot "scripts\iniciar_servidor_local.ps1") `
    -Force

Copy-Item `
    (Join-Path $PayloadRoot "scripts\iniciar_daemon_mujoco.ps1") `
    (Join-Path $ProjectRoot "scripts\iniciar_daemon_mujoco.ps1") `
    -Force

Copy-Item `
    (Join-Path $PayloadRoot "scripts\iniciar_conversation_app.ps1") `
    (Join-Path $ProjectRoot "scripts\iniciar_conversation_app.ps1") `
    -Force

Copy-Item `
    (Join-Path $PayloadRoot "tools\ahootsa_session_report.py") `
    (Join-Path $ServerRoot "tools\ahootsa_session_report.py") `
    -Force

Copy-Item `
    (Join-Path $PayloadRoot "app\panel_mvp.py") `
    (Join-Path $ServerRoot "app\panel_mvp.py") `
    -Force

$Config = Get-Content `
    $ConfigPath `
    -Raw `
    -Encoding UTF8 |
    ConvertFrom-Json

$Config.daemon_script = "../scripts/iniciar_daemon_mujoco.ps1"
$Config.manual_app_script = "../scripts/iniciar_conversation_app.ps1"

$ConfigJson = $Config |
    ConvertTo-Json -Depth 20

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
        $Text = Get-Content `
            $PythonFile `
            -Raw `
            -Encoding UTF8

        $Text = [regex]::Replace(
            $Text,
            '0\.12\.\d+(?:\.\d+)?',
            '0.12.8'
        )

        [System.IO.File]::WriteAllText(
            $PythonFile,
            $Text,
            (New-Object System.Text.UTF8Encoding($false))
        )
    }
}

Copy-Item `
    (Join-Path $SourceRoot "docs\UPDATE_12_8.md") `
    (Join-Path $ServerRoot "docs\UPDATE_12_8.md") `
    -Force

Copy-Item `
    (Join-Path $SourceRoot "docs\ARQUITECTURA_FUNCIONALIDAD.md") `
    (Join-Path $ServerRoot "docs\ARQUITECTURA_FUNCIONALIDAD.md") `
    -Force

Copy-Item `
    (Join-Path $SourceRoot "INSTRUCCIONES_UPDATE_12_8.txt") `
    (Join-Path $ServerRoot "INSTRUCCIONES_UPDATE_12_8.txt") `
    -Force

Get-ChildItem `
    (Join-Path $ServerRoot "app") `
    -Directory `
    -Recurse `
    -Force `
    -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Name -eq "__pycache__"
    } |
    Remove-Item `
        -Recurse `
        -Force `
        -ErrorAction SilentlyContinue

if (Test-Path $PythonExe) {
    & $PythonExe `
        -m py_compile `
        (Join-Path $ServerRoot "app\panel_mvp.py") `
        (Join-Path $ServerRoot "tools\ahootsa_session_report.py")

    if ($LASTEXITCODE -ne 0) {
        throw "Los archivos Python no superan py_compile."
    }

    & $PythonExe `
        -c "import reportlab; print('REPORTLAB_OK', reportlab.Version)"

    if ($LASTEXITCODE -ne 0) {
        throw "ReportLab no está operativo."
    }
}

$ExpectedRootScripts = @(
    "INICIAR_AHOOTSA.ps1",
    "FINALIZAR_SESION_AHOOTSA.ps1",
    "COMPROBAR_AHOOTSA.ps1",
    "LIMPIAR_PROCESOS_AHOOTSA.ps1"
)

foreach ($Name in $ExpectedRootScripts) {
    if (-not (Test-Path (Join-Path $ProjectRoot $Name))) {
        throw "Falta el script operativo: $Name"
    }
}

Write-Host ""
Write-Host "UPDATE 12.8 INSTALADO." -ForegroundColor Green
Write-Host "Versión del servidor: 0.12.8" -ForegroundColor Cyan
Write-Host "Scripts operativos en raíz: 4" -ForegroundColor Cyan
Write-Host "Scripts antiguos archivados en:" -ForegroundColor Gray
Write-Host "  $ObsoleteBackup" -ForegroundColor Gray
Write-Host ""
Write-Host "Arranque completo:" -ForegroundColor Yellow
Write-Host "  cd $ProjectRoot" -ForegroundColor Gray
Write-Host "  .\INICIAR_AHOOTSA.ps1" -ForegroundColor Gray
