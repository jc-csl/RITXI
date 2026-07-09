param([string]$InstallMujoco="NO", [string]$InstallHFDeps="NO")
$ErrorActionPreference="Stop"
$Root=Split-Path -Parent $MyInvocation.MyCommand.Path
$Py="$env:LOCALAPPDATA\Reachy Mini Control\apps_venv\Scripts\python.exe"
if (!(Test-Path $Py)) { throw "No existe apps_venv de Reachy Mini Control: $Py" }
if ($InstallMujoco.ToUpperInvariant() -eq "SI") { & $Py -m pip install -U mujoco }
if ($InstallHFDeps.ToUpperInvariant() -eq "SI") { & $Py -m pip install -U transformers accelerate sentencepiece safetensors }
& $Py (Join-Path $Root "tools\patch_ahootsa_5_0_43.py")
if ($LASTEXITCODE -ne 0) { throw "No se pudo aplicar el parche 5.0.43" }
Write-Host "Ahootsa 5.0.43 instalado/actualizado correctamente."
