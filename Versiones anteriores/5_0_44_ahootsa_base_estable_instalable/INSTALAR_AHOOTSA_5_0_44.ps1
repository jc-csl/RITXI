param(
    [string]$AppVenv = "$env:LOCALAPPDATA\Reachy Mini Control\apps_venv",
    [switch]$InstallMujoco,
    [switch]$InstallOpenCV,
    [switch]$InstallEmotionAudio
)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Py = Join-Path $AppVenv "Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Py)) { throw "No encuentro python.exe en $Py. Instala primero Reachy Mini Control/Desktop Control." }
Write-Host "[INFO] Instalando Ahootsa 5.0.44 en apps_venv: $AppVenv"
& $Py -m pip install --upgrade pip setuptools wheel
& $Py -m pip install --no-deps --force-reinstall $Root
if ($InstallMujoco) { & $Py -m pip install mujoco }
if ($InstallOpenCV) { & $Py -m pip install opencv-python }
if ($InstallEmotionAudio) { & $Py -m pip install pygame }
& $Py -c "import ahootsa_realtime_ollama_desktop_app as a; print('AHOOTSA_IMPORT_OK', a.__version__)"
& $Py -c "import importlib.metadata as m; eps=[e for e in m.entry_points(group='reachy_mini_apps') if e.name=='ahootsa_realtime_ollama_app']; print('ENTRYPOINTS', [e.name for e in eps]); raise SystemExit(0 if eps else 1)"
Write-Host "[OK] Ahootsa 5.0.44 instalada."
