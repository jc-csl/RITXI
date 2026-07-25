param(
    [string]$ProjectRoot = "D:\RITXI\AHOOTSA8"
)

$ErrorActionPreference = "Stop"

$ServerRoot = Join-Path $ProjectRoot "ahootsa_local_server"
$PanelPath = Join-Path $ServerRoot "app\static\panel\panel_inline_12_7_2.html"
$ApiPath = Join-Path $ServerRoot "app\panel_mvp.py"

foreach ($Path in @($PanelPath, $ApiPath)) {
    if (-not (Test-Path $Path)) {
        throw "Falta: $Path"
    }
}

$Html = Get-Content $PanelPath -Raw -Encoding UTF8
$Api = Get-Content $ApiPath -Raw -Encoding UTF8

if ($Html -notmatch 'id="ahootsa-panel-style"') {
    throw "No se encuentra el CSS integrado."
}

if ($Html -notmatch 'id="ahootsa-panel-script"') {
    throw "No se encuentra el JavaScript integrado."
}

if ($Html -notmatch 'grid-template-columns') {
    throw "No se encuentra el diseño de tres columnas."
}

if ($Html -notmatch 'newUserPanel') {
    throw "No se encuentra el formulario de alta de personas."
}

if ($Html -match 'src="/panel-static/' -or $Html -match 'href="/panel-static/') {
    throw "El panel aún depende de recursos visuales externos."
}

if ($Api -notmatch '/panel-12-7-2') {
    throw "No se encuentra la URL nueva del panel."
}

Write-Host ""
Write-Host "PANEL 12.7.2 CORRECTAMENTE INSTALADO." -ForegroundColor Green
Write-Host "HTML único: OK" -ForegroundColor Green
Write-Host "CSS integrado: OK" -ForegroundColor Green
Write-Host "JavaScript integrado: OK" -ForegroundColor Green
Write-Host "Alta de personas: PRESENTE" -ForegroundColor Green
Write-Host "Tres columnas: PRESENTE" -ForegroundColor Green
Write-Host "URL nueva: http://127.0.0.1:8100/panel-12-7-2" -ForegroundColor Cyan
