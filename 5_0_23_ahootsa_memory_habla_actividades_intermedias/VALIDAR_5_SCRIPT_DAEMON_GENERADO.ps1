# VALIDAR_5_SCRIPT_DAEMON_GENERADO.ps1
# Ahootsa 5.0.23
# Comprueba que el lanzador ya no usa redireccion nativa que genera NativeCommandError en PowerShell 5.

$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Launcher = Join-Path $Root "LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1"

if (-not (Test-Path -LiteralPath $Launcher)) {
    Write-Host "[ERROR] No existe launcher: $Launcher"
    exit 1
}

$Txt = Get-Content -Raw -Encoding UTF8 -LiteralPath $Launcher

$Checks = [ordered]@{
    "usa Start-Process daemon" = ($Txt -match 'Start-Process -FilePath \$Daemon')
    "no direct native stderr redirect" = (-not ($Txt -match '& \$Daemon @ArgsList 1>>'))
    "no RedirectStandardOutput" = (-not ($Txt -match 'RedirectStandardOutput'))
    "daemon log-file activo" = ($Txt -match '"--log-file", \$DaemonLog')
}

$Ok = $true
foreach ($K in $Checks.Keys) {
    Write-Host "$K =" $Checks[$K]
    if (-not $Checks[$K]) { $Ok = $false }
}

if (-not $Ok) {
    Write-Host "[ERROR] Launcher no supera validacion."
    exit 1
}

Write-Host "[OK] Launcher sin redireccion nativa problemática."
