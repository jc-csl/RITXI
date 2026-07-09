# COMPROBAR_5_SINTAXIS_PS1.ps1
# Comprueba parseo basico de los scripts PowerShell sin ejecutarlos.

$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

$Scripts = @(
    "INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1",
    "LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1",
    "LANZAR_SOLO_DAEMON_5_MUJOCO.ps1",
    "PARAR_5_AHOOTSA_MUJOCO_WEB.ps1",
    "FORZAR_5_IDENTIDAD_CASTELLANO_AHOOTSA.ps1",
    "REINSTALAR_5_MODULO_AHOOTSA_EN_APPS_VENV.ps1",
    "test\DIAGNOSTICAR_5_AHOOTSA_MUJOCO_WEB.ps1",
    "FORZAR_5_VOZ_SOHEE_COMPLETA.ps1",
    "CORREGIR_5_NOAPI_DUPLICADO.ps1",
    "VALIDAR_5_SCRIPT_DAEMON_GENERADO.ps1",
    "VALIDAR_5_VOZ_SESION_SOHEE.ps1",
    "MANTENER_5_VOZ_SOHEE_WATCHER.ps1",
    "test\DIAGNOSTICAR_5_VOZ_SIN_BOM.ps1",
    "LIMPIAR_5_VOZ_SOHEE_SIN_BOM.ps1",
    "REINICIAR_5_SESION_CONVERSACION.ps1",
    "DIAGNOSTICAR_5_CONVERSACION_FLUIDA.ps1",
    "DIAGNOSTICAR_5_HUGGINGFACE_CONEXION.ps1",
    "ESPERAR_5_BACKEND_REALTIME_LISTO.ps1",
    "DIAGNOSTICAR_5_TOOLS_FLUIDEZ.ps1",
    "RESUMIR_5_LOGS_AHOOTSA.ps1",
    "VOZ_2_ANALIZAR_CAMBIOS_MANUALES.ps1",
    "VOZ_1_INICIAR_MONITORIZACION_CAMBIO_MANUAL.ps1",
    "COMPROBAR_5_LOGS_AHOOTSA.ps1"
)

foreach ($Rel in $Scripts) {
    $Path = Join-Path $Root $Rel
    if (-not (Test-Path -LiteralPath $Path)) {
        Write-Host "[WARN] No existe: $Rel"
        continue
    }

    $Errors = $null
    $Tokens = $null
    [System.Management.Automation.Language.Parser]::ParseFile($Path, [ref]$Tokens, [ref]$Errors) | Out-Null

    if ($Errors -and $Errors.Count -gt 0) {
        Write-Host "[ERROR] $Rel"
        $Errors | ForEach-Object { Write-Host "  $($_.Message)" }
    } else {
        Write-Host "[OK] $Rel"
    }
}
