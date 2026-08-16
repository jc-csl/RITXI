param(
    [switch]$NoAbrirNavegador,

    [switch]$LiberarPuerto
)

$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$UtilsPath = Join-Path $ProjectRoot "scripts\ahootsa_process_utils.ps1"
$ServerScript = Join-Path $ProjectRoot "scripts\iniciar_servidor_local.ps1"
$ServerRoot = Join-Path $ProjectRoot "ahootsa_local_server"
$PythonExe = Join-Path $ServerRoot ".venv\Scripts\python.exe"
$PanelUrl = "http://127.0.0.1:8100/panel-12-8-5"
$ApiDocsUrl = "http://127.0.0.1:8100/docs"
$HealthUrl = "http://127.0.0.1:8100/health"
$BootstrapUrl = "http://127.0.0.1:8100/panel/api/bootstrap"

foreach ($Required in @(
    $UtilsPath,
    $ServerScript
)) {
    if (-not (Test-Path $Required)) {
        throw "Falta un archivo necesario: $Required"
    }
}

if (-not (Test-Path $PythonExe)) {
    throw @(
        "No se encuentra el entorno virtual del servidor local:",
        $PythonExe,
        "",
        "Crea el entorno en ahootsa_local_server e instala dependencias:",
        "  python -m venv .venv",
        "  .\.venv\Scripts\pip install -r requirements.txt"
    ) -join [Environment]::NewLine
}

. $UtilsPath

function Get-AhootsaServerStatus {
    if (-not (Test-AhootsaPort -Port 8100)) {
        return @{
            Running = $false
            Version = $null
        }
    }

    try {
        $Health = Invoke-RestMethod `
            -Uri $HealthUrl `
            -Method Get `
            -TimeoutSec 5

        return @{
            Running = $true
            Version = [string]$Health.version
        }
    } catch {
        return @{
            Running = $true
            Version = $null
        }
    }
}

Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host " AHOOTSA - SERVIDOR LOCAL INDEPENDIENTE" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host (
    "Este modo arranca únicamente Ahootsa Local Server en el puerto 8100."
) -ForegroundColor Yellow
Write-Host (
    "No inicia el daemon (8000) ni la Conversation App (7860)."
) -ForegroundColor Yellow
Write-Host ""

$Status = Get-AhootsaServerStatus

if ($Status.Running) {
    if ($Status.Version) {
        Write-Host (
            "El servidor local ya responde en 8100 (versión $($Status.Version))."
        ) -ForegroundColor Green
    } else {
        Write-Host (
            "El puerto 8100 está abierto, pero /health no respondió aún."
        ) -ForegroundColor Yellow
    }

    if (-not $NoAbrirNavegador) {
        Start-Process $PanelUrl
    }

    Write-Host ""
    Write-Host "Panel: $PanelUrl" -ForegroundColor Gray
    Write-Host "API:   $ApiDocsUrl" -ForegroundColor Gray
    exit 0
}

if (Test-AhootsaPort -Port 8100) {
    if (-not $LiberarPuerto) {
        throw @(
            "El puerto 8100 está ocupado por otro proceso.",
            "Vuelve a ejecutar el script con -LiberarPuerto para cerrarlo."
        ) -join " "
    }

    Write-Host "Liberando el puerto 8100..." -ForegroundColor Cyan

    Stop-AhootsaPortProcess `
        -Port 8100 `
        -ServiceName "Ahootsa Local Server" |
        Out-Null

    Stop-AhootsaCommandProcesses `
        -Patterns @("uvicorn", "app\.main:app", "iniciar_servidor_local\.ps1") `
        -ServiceName "Ahootsa Local Server"

    if (-not (Wait-AhootsaPortClosed -Port 8100 -TimeoutSeconds 15)) {
        throw "No se pudo liberar el puerto 8100."
    }

    Write-Host "Puerto 8100 libre." -ForegroundColor Green
    Write-Host ""
}

Write-Host "Arrancando servidor local..." -ForegroundColor Cyan

Start-Process `
    powershell.exe `
    -WorkingDirectory $ProjectRoot `
    -ArgumentList @(
        "-NoExit",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        $ServerScript
    )

if (-not (Wait-AhootsaPortOpen -Port 8100 -TimeoutSeconds 60)) {
    throw "El servidor local no responde en el puerto 8100."
}

try {
    $Bootstrap = Invoke-RestMethod `
        -Uri $BootstrapUrl `
        -Method Get `
        -TimeoutSec 10

    Write-Host (
        "Servidor local activo en 8100 (versión $($Bootstrap.version))."
    ) -ForegroundColor Green
} catch {
    Write-Host "Servidor local activo en 8100." -ForegroundColor Green
}

Write-Host ""
Write-Host "Panel: $PanelUrl" -ForegroundColor Gray
Write-Host "API:   $ApiDocsUrl" -ForegroundColor Gray
Write-Host ""
Write-Host "Modo independiente:" -ForegroundColor Yellow
Write-Host "  - Puedes usar el panel sin arrancar el robot." -ForegroundColor Gray
Write-Host "  - Para sesión completa usa INICIAR_AHOOTSA_SESION.ps1." -ForegroundColor Gray
Write-Host "  - Para conversación anónima usa INICIAR_AHOOTSA_ANONIMO.ps1." -ForegroundColor Gray

if (-not $NoAbrirNavegador) {
    Start-Process $PanelUrl
}
