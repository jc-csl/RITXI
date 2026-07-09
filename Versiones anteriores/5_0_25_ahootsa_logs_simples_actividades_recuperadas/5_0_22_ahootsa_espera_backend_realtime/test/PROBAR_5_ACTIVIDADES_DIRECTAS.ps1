# PROBAR_5_ACTIVIDADES_DIRECTAS.ps1
# Comprueba que las herramientas de comunicacion estan en modo respuesta directa.

$ErrorActionPreference = "Continue"
$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$Profile = Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\ahootsa_realtime_es"

$Files = @(
    "actividades_comunicacion.py",
    "listar_actividades_comunicacion.py",
    "iniciar_actividad_comunicacion.py",
    "list_communication_activity_levels.py",
    "list_communication_activities.py",
    "start_communication_activity.py",
    "start_memory_pairs_game.py",
    "choose_memory_cards.py"
)

foreach ($Name in $Files) {
    $Path = Join-Path $Profile $Name
    if (-not (Test-Path -LiteralPath $Path)) {
        Write-Host "[WARN] No existe $Name"
        continue
    }
    $Txt = Get-Content -Raw -Encoding UTF8 -LiteralPath $Path
    $Direct = ($Txt -match "needs_response\s*=\s*False")
    Write-Host "$Name direct =" $Direct
}
