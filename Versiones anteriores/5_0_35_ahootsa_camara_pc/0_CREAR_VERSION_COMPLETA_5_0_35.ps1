param(
    [string]$SourceRoot = "D:\RITXI\5_0_34_ahootsa_completa_consolidada",
    [string]$TargetRoot = "D:\RITXI\5_0_35_ahootsa_completa_camara_pc",
    [switch]$Force,
    [switch]$InstallMujoco
)

$ErrorActionPreference = "Stop"

Write-Host "============================================================"
Write-Host "Ahootsa 5.0.35 - version completa con camara PC"
Write-Host "============================================================"
Write-Host "Origen:  $SourceRoot"
Write-Host "Destino: $TargetRoot"

if (!(Test-Path -LiteralPath $SourceRoot)) {
    throw "No existe la version origen $SourceRoot. Primero crea/prueba la 5.0.34 o indica -SourceRoot."
}

if (Test-Path -LiteralPath $TargetRoot) {
    if ($Force) {
        Write-Host "[WARN] Eliminando version destino existente..."
        Remove-Item -LiteralPath $TargetRoot -Recurse -Force
    } else {
        throw "Ya existe $TargetRoot. Ejecuta con -Force para sustituirla o cambia -TargetRoot."
    }
}

Write-Host "[INFO] Copiando version completa base..."
Copy-Item -LiteralPath $SourceRoot -Destination $TargetRoot -Recurse -Force

$ToolsDir = Join-Path $TargetRoot "tools"
$DocsDir = Join-Path $TargetRoot "docs"
New-Item -ItemType Directory -Force -Path $ToolsDir | Out-Null
New-Item -ItemType Directory -Force -Path $DocsDir | Out-Null

Copy-Item -LiteralPath (Join-Path $PSScriptRoot "tools\patch_camera_pc_5_0_35.py") -Destination (Join-Path $ToolsDir "patch_camera_pc_5_0_35.py") -Force
Copy-Item -LiteralPath (Join-Path $PSScriptRoot "docs\CAMARA_PC_5_0_35.md") -Destination (Join-Path $DocsDir "CAMARA_PC_5_0_35.md") -Force
Copy-Item -LiteralPath (Join-Path $PSScriptRoot "README.md") -Destination (Join-Path $TargetRoot "README_5_0_35.md") -Force

# Wrapper propio de la version 5.0.35.
@'
param(
    [switch]$InstallMujoco
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Py = "C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Scripts\python.exe"
$Patch = Join-Path $Root "tools\patch_camera_pc_5_0_35.py"
$OriginalLauncher = Join-Path $Root "LANZAR_AHOOTSA.ps1"

Write-Host "============================================================"
Write-Host "Ahootsa 5.0.35 - Camara PC + version consolidada"
Write-Host "============================================================"
Write-Host "Root: $Root"

if (!(Test-Path -LiteralPath $Py)) {
    throw "No encuentro python.exe del apps_venv: $Py"
}

if ($InstallMujoco) {
    & $Py -m pip install mujoco
    if ($LASTEXITCODE -ne 0) { throw "No se pudo instalar mujoco." }
}

Write-Host "[INFO] Aplicando soporte de camara PC..."
& $Py $Patch $Root
if ($LASTEXITCODE -ne 0) { throw "No se pudo aplicar soporte de camara PC." }

if (!(Test-Path -LiteralPath $OriginalLauncher)) {
    throw "No encuentro LANZAR_AHOOTSA.ps1 dentro de esta version: $OriginalLauncher"
}

Write-Host "[INFO] Lanzando Ahootsa 5.0.35..."
if ($InstallMujoco) {
    & powershell -ExecutionPolicy Bypass -File $OriginalLauncher -InstallMujoco
} else {
    & powershell -ExecutionPolicy Bypass -File $OriginalLauncher
}
'@ | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $TargetRoot "LANZAR_AHOOTSA_5_0_35.ps1")

# Comprobador de endpoints de camara.
@'
param(
    [string]$BaseUrl = "http://127.0.0.1:8000"
)
$ErrorActionPreference = "Continue"
Write-Host "Comprobando endpoints de camara en $BaseUrl"
try {
    $latest = Invoke-RestMethod -Uri "$BaseUrl/camera/latest" -Method Get -TimeoutSec 5
    $latest | ConvertTo-Json -Depth 5
} catch {
    Write-Host "[WARN] /camera/latest no responde todavia. Arranca Ahootsa y prueba de nuevo."
    Write-Host $_.Exception.Message
}
'@ | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $TargetRoot "2_COMPROBAR_CAMARA_5_0_35.ps1")

# Nota en instrucciones.
$Instr = Join-Path $TargetRoot "instrucciones.txt"
$Add = @"

============================================================
Ahootsa 5.0.35 - Camara PC
============================================================
Esta version añade control de camara del PC desde la interfaz web.
Uso recomendado:
  powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_5_0_35.ps1

Al abrir la app aparecera un panel flotante "Camara PC".
Pulsa Abrir > Activar > acepta permisos del navegador > Hacer foto.
Las fotos se guardan en:
  D:\RITXI\logs\camera

Endpoints añadidos:
  GET  /camera/latest
  POST /camera/upload
"@
Add-Content -Encoding UTF8 -LiteralPath $Instr -Value $Add

Write-Host "============================================================"
Write-Host "Version 5.0.35 creada"
Write-Host "============================================================"
Write-Host "Ejecuta:"
Write-Host "cd $TargetRoot"
Write-Host "powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_5_0_35.ps1"
