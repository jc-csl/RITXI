# CORREGIR_5_NOAPI_DUPLICADO.ps1
# Ahootsa 5.0.22
# Repara llamadas duplicadas a -NoApi en los scripts de instalacion, por si se edito una copia anterior.

$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Targets = @(
    (Join-Path $Root "INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1"),
    (Join-Path $Root "INSTALAR_5_COMPLETO_SOBRE_CONVERSATION_APP.ps1"),
    (Join-Path $Root "scripts\windows\INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1"),
    (Join-Path $Root "scripts\windows\INSTALAR_5_COMPLETO_SOBRE_CONVERSATION_APP.ps1")
)

foreach ($Path in $Targets) {
    if (-not (Test-Path -LiteralPath $Path)) { continue }
    $Txt = Get-Content -Raw -Encoding UTF8 -LiteralPath $Path
    $New = $Txt -replace '(\s-NoApi)(\s+-NoApi)+', '$1'
    if ($New -ne $Txt) {
        $New | Set-Content -Encoding UTF8 -LiteralPath $Path
        Write-Host "[OK] reparado $Path"
    } else {
        Write-Host "[OK] sin duplicados $Path"
    }
}

Write-Host "Comprobacion:"
Select-String -Path $Targets -Pattern "FORZAR_5_VOZ_SOHEE_COMPLETA.ps1" -ErrorAction SilentlyContinue
