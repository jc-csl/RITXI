param()

$ErrorActionPreference = "Continue"

$ProjectRoot = $PSScriptRoot
$UtilsPath = Join-Path `
    $ProjectRoot `
    "scripts\ahootsa_process_utils.ps1"

if (-not (Test-Path $UtilsPath)) {
    throw "No se encuentra la utilidad de procesos: $UtilsPath"
}

. $UtilsPath

Write-Host ""
Write-Host "LIMPIEZA DE PROCESOS AHOOTSA" -ForegroundColor Cyan
Write-Host "Puertos: 7860, 8100 y 8000" -ForegroundColor Gray
Write-Host ""

Stop-AhootsaConversationAppGracefully | Out-Null

Stop-AhootsaPortProcess `
    -Port 7860 `
    -ServiceName "Conversation App" |
    Out-Null

Stop-AhootsaPortProcess `
    -Port 8100 `
    -ServiceName "Ahootsa Local Server" |
    Out-Null

Stop-AhootsaPortProcess `
    -Port 8000 `
    -ServiceName "Reachy Mini daemon" |
    Out-Null

$ProcessRules = @(
    @{
        Patterns = @("reachy-mini-conversation-app")
        Name = "Conversation App"
    },
    @{
        Patterns = @("reachy-mini-daemon")
        Name = "Reachy Mini daemon"
    },
    @{
        Patterns = @("uvicorn", "app\.main:app")
        Name = "Ahootsa Local Server"
    },
    @{
        Patterns = @("iniciar_conversation_app\.ps1")
        Name = "Consola Conversation App"
    },
    @{
        Patterns = @("iniciar_daemon_mujoco\.ps1")
        Name = "Consola daemon"
    },
    @{
        Patterns = @("iniciar_servidor_local\.ps1")
        Name = "Consola servidor"
    },
    @{
        Patterns = @("1_lanzar_daemon_mujoco\.ps1")
        Name = "Lanzador antiguo daemon"
    },
    @{
        Patterns = @("2_lanzar_app_ahootsa\.ps1")
        Name = "Lanzador antiguo Conversation App"
    },
    @{
        Patterns = @("3_lanzar_ahootsa_server\.ps1")
        Name = "Lanzador antiguo servidor"
    }
)

foreach ($Rule in $ProcessRules) {
    Stop-AhootsaCommandProcesses `
        -Patterns $Rule.Patterns `
        -ServiceName $Rule.Name
}

Start-Sleep -Milliseconds 700

$Occupied = @()

foreach ($Port in @(7860, 8100, 8000)) {
    if (Test-AhootsaPort -Port $Port) {
        $Occupied += $Port
    }
}

Write-Host ""

if ($Occupied.Count -eq 0) {
    Write-Host (
        "PROCESOS AHOOTSA CERRADOS. LOS TRES PUERTOS ESTÁN LIBRES."
    ) -ForegroundColor Green

    exit 0
}

Write-Host (
    "Siguen ocupados estos puertos: " +
    ($Occupied -join ", ")
) -ForegroundColor Red

exit 1
