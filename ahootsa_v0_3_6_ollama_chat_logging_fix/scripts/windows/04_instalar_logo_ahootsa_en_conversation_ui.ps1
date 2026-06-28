$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$Py = Join-Path $env:LOCALAPPDATA "Reachy Mini Control\apps_venv\Scripts\python.exe"
if (!(Test-Path $Py)) { throw "No encuentro apps_venv Python: $Py" }

$pkgDir = & $Py -c "import pathlib, reachy_mini_conversation_app; print(pathlib.Path(reachy_mini_conversation_app.__file__).resolve().parent)"
$pkgDir = $pkgDir.Trim()
$avatarsDir = Join-Path $pkgDir "static\avatars"
$constants = Join-Path $pkgDir "static\js\constants.js"
$logoSrc = Join-Path $ProjectRoot "src\ahootsa_reachy_mini_desktop_app\assets\ahootsa_logo.png"
$logoDst = Join-Path $avatarsDir "ahootsa-logo.png"

if (!(Test-Path $avatarsDir)) { throw "No encuentro avatarsDir: $avatarsDir" }
if (!(Test-Path $constants)) { throw "No encuentro constants.js: $constants" }
if (!(Test-Path $logoSrc)) { throw "No encuentro logo: $logoSrc" }

Copy-Item $logoSrc $logoDst -Force

$text = Get-Content $constants -Raw
if ($text -notmatch "ahootsa_es") {
    $text = $text -replace "export const AVATAR_BY_PROFILE = Object\.freeze\(\{", "export const AVATAR_BY_PROFILE = Object.freeze({`n  ahootsa_es: \"ahootsa-logo.png\"," 
    Set-Content $constants $text -Encoding UTF8
    Write-Host "constants.js actualizado con ahootsa_es." -ForegroundColor Green
} else {
    Write-Host "constants.js ya contiene ahootsa_es." -ForegroundColor Yellow
}
Write-Host "Logo copiado a:" $logoDst -ForegroundColor Green
