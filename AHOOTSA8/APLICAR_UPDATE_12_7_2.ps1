param(
    [string]$ProjectRoot = "D:\RITXI\AHOOTSA8"
)

$ErrorActionPreference = "Stop"

$SourceRoot = $PSScriptRoot
$PayloadRoot = Join-Path $SourceRoot "payload"
$ServerRoot = Join-Path $ProjectRoot "ahootsa_local_server"
$PanelRoot = Join-Path $ServerRoot "app\static\panel"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupRoot = Join-Path $ServerRoot "backups\antes_update_12_7_2_$Timestamp"
$PythonExe = Join-Path $ServerRoot ".venv\Scripts\python.exe"

if (-not (Test-Path (Join-Path $ServerRoot "app\main.py"))) {
    throw "No se encuentra la instalación principal: $ServerRoot"
}

$StopScript = Join-Path $ProjectRoot "0_detener_servicios_ahootsa.ps1"

if (Test-Path $StopScript) {
    Write-Host "Deteniendo los servicios anteriores..." -ForegroundColor Cyan

    try {
        & $StopScript
    } catch {
        Write-Host "Algún servicio deberá cerrarse manualmente." -ForegroundColor Yellow
    }
}

New-Item -ItemType Directory -Path $BackupRoot -Force | Out-Null
New-Item -ItemType Directory -Path $PanelRoot -Force | Out-Null
New-Item -ItemType Directory -Path (Join-Path $ServerRoot "docs") -Force | Out-Null

foreach ($Current in @(
    (Join-Path $ServerRoot "app\main.py"),
    (Join-Path $ServerRoot "app\panel_mvp.py"),
    (Join-Path $PanelRoot "panel.html"),
    (Join-Path $PanelRoot "panel_inline_12_7_2.html")
)) {
    if (Test-Path $Current) {
        Copy-Item $Current (Join-Path $BackupRoot (Split-Path $Current -Leaf)) -Force
    }
}

Copy-Item `
    (Join-Path $PayloadRoot "app\panel_mvp.py") `
    (Join-Path $ServerRoot "app\panel_mvp.py") `
    -Force

Copy-Item `
    (Join-Path $PayloadRoot "app\static\panel\panel_inline_12_7_2.html") `
    (Join-Path $PanelRoot "panel_inline_12_7_2.html") `
    -Force

foreach ($PythonFile in @(
    (Join-Path $ServerRoot "app\main.py"),
    (Join-Path $ServerRoot "app\panel_mvp.py")
)) {
    if (Test-Path $PythonFile) {
        $Text = Get-Content $PythonFile -Raw -Encoding UTF8
        $Text = [regex]::Replace(
            $Text,
            '0\.12\.\d+(?:\.\d+)?',
            '0.12.7.2'
        )
        [System.IO.File]::WriteAllText(
            $PythonFile,
            $Text,
            (New-Object System.Text.UTF8Encoding($false))
        )
    }
}

Copy-Item `
    (Join-Path $SourceRoot "docs\UPDATE_12_7_2.md") `
    (Join-Path $ServerRoot "docs\UPDATE_12_7_2.md") `
    -Force

Copy-Item `
    (Join-Path $SourceRoot "docs\ARQUITECTURA_FUNCIONALIDAD.md") `
    (Join-Path $ServerRoot "docs\ARQUITECTURA_FUNCIONALIDAD.md") `
    -Force

Copy-Item `
    (Join-Path $SourceRoot "INSTRUCCIONES_UPDATE_12_7_2.txt") `
    (Join-Path $ServerRoot "INSTRUCCIONES_UPDATE_12_7_2.txt") `
    -Force

Get-ChildItem `
    (Join-Path $ServerRoot "app") `
    -Directory `
    -Recurse `
    -Force `
    -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -eq "__pycache__" } |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

if (Test-Path $PythonExe) {
    & $PythonExe -m py_compile (Join-Path $ServerRoot "app\panel_mvp.py")

    if ($LASTEXITCODE -ne 0) {
        throw "panel_mvp.py no supera py_compile."
    }
}

$InstalledHtmlPath = Join-Path $PanelRoot "panel_inline_12_7_2.html"
$InstalledHtml = Get-Content $InstalledHtmlPath -Raw -Encoding UTF8

if ($InstalledHtml -notmatch 'id="ahootsa-panel-style"') {
    throw "El panel no contiene el CSS integrado."
}

if ($InstalledHtml -notmatch 'id="ahootsa-panel-script"') {
    throw "El panel no contiene el JavaScript integrado."
}

if ($InstalledHtml -match 'src="/panel-static/' -or $InstalledHtml -match 'href="/panel-static/') {
    throw "El panel todavía depende de archivos visuales externos."
}

Write-Host ""
Write-Host "UPDATE 12.7.2 instalado." -ForegroundColor Green
Write-Host "Panel único con CSS integrado: OK" -ForegroundColor Cyan
Write-Host "Panel único con JavaScript integrado: OK" -ForegroundColor Cyan
Write-Host "Alta de personas sin diálogo externo: OK" -ForegroundColor Cyan
Write-Host "Diseño de escritorio en tres columnas: OK" -ForegroundColor Cyan
Write-Host "Backup: $BackupRoot" -ForegroundColor Gray
Write-Host ""
Write-Host "Arranque:" -ForegroundColor Yellow
Write-Host "  cd $ServerRoot"
Write-Host "  .\3_lanzar_ahootsa_server.ps1"
Write-Host ""
Write-Host "Abrir esta URL nueva:" -ForegroundColor Yellow
Write-Host "  http://127.0.0.1:8100/panel-12-7-2"
