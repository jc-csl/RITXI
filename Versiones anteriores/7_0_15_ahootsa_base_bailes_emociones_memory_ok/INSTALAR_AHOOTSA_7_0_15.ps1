param(
    [string]$AppVenv = "$env:LOCALAPPDATA\Reachy Mini Control\apps_venv",
    [switch]$SkipMujoco,
    [switch]$SkipPygame,
    [switch]$SkipOpenCV,
    [switch]$SkipEmotionLibraryDownload,
    [switch]$NoClean
)
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Py = Join-Path $AppVenv "Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Py)) { throw "No encuentro python.exe en $Py. Instala primero Reachy Mini Control/Desktop Control." }

New-Item -ItemType Directory -Force -Path "D:\RITXI\logs" | Out-Null
New-Item -ItemType Directory -Force -Path "D:\RITXI\fotos" | Out-Null

function Invoke-PythonSafe {
    param(
        [Parameter(Mandatory=$true)][string[]]$ArgsList,
        [string]$ErrorMessage = "Comando Python fallido",
        [switch]$AllowFail
    )
    $old = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    & $Py @ArgsList
    $code = $LASTEXITCODE
    $ErrorActionPreference = $old
    if (($code -ne 0) -and (-not $AllowFail)) {
        throw "$ErrorMessage. ExitCode=$code"
    }
    return $code
}

Write-Host "============================================================"
Write-Host "Instalando Ahootsa 7.0.15"
Write-Host "============================================================"
Write-Host "Root:    $Root"
Write-Host "AppVenv: $AppVenv"
Write-Host "Python:  $Py"
Write-Host ""

Write-Host "[INFO] Actualizando pip/setuptools/wheel..."
Invoke-PythonSafe -ArgsList @('-m','pip','install','--upgrade','pip','setuptools','wheel') -ErrorMessage "No se pudo actualizar pip/setuptools/wheel" | Out-Null

Write-Host "[INFO] Localizando site-packages de apps_venv..."
$SitePackages = & $Py -c "import sysconfig; print(sysconfig.get_paths()['purelib'])"
if (-not (Test-Path -LiteralPath $SitePackages)) { throw "No encuentro site-packages: $SitePackages" }
Write-Host "site-packages: $SitePackages"

if (-not $NoClean) {
    Write-Host "[INFO] Limpieza manual previa de instalaciones Ahootsa antiguas/corruptas..."
    Write-Host "[INFO] No se usa pip uninstall para evitar uninstall-no-record-file."
    $Cleaner = Join-Path $env:TEMP "ahootsa_clean_install_7_0_15.py"
@'
from __future__ import annotations
from pathlib import Path
import os
import shutil
import sys
import time

site = Path(sys.argv[1])
patterns = [
    "ahootsa_realtime_ollama_desktop_app",
    "ahootsa_realtime_ollama_desktop_app-*.dist-info",
    "ahootsa_realtime_ollama_desktop_app-*.egg-info",
    "ahootsa_realtime_ollama_desktop_app*.dist-info",
    "ahootsa_realtime_ollama_desktop_app*.egg-info",
    "ahootsa_realtime_ollama_desktop_app*",
]
extra = []
for pat in patterns:
    extra.extend(site.glob(pat))
# Detectar metadatos corruptos con nombre normalizado del paquete.
for p in list(site.glob("*.dist-info")) + list(site.glob("*.egg-info")):
    low = p.name.lower().replace("-", "_")
    if "ahootsa" in low and ("realtime" in low or "ollama" in low):
        extra.append(p)
    else:
        meta = p / "METADATA"
        pkg = p / "PKG-INFO"
        for mf in (meta, pkg):
            try:
                txt = mf.read_text(encoding="utf-8", errors="ignore").lower()
            except Exception:
                continue
            if "name: ahootsa-realtime-ollama-desktop-app" in txt:
                extra.append(p)
                break

seen = set()
for target in extra:
    target = target.resolve()
    if target in seen or not target.exists():
        continue
    seen.add(target)
    print(f"CLEAN_TARGET {target}")
    for attempt in range(3):
        try:
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
            print(f"REMOVED {target}")
            break
        except Exception as exc:
            print(f"REMOVE_WARN attempt={attempt+1} {target} {type(exc).__name__}: {exc}")
            time.sleep(0.5)
    else:
        # Último recurso: renombrar para que importlib/pip no lo detecten.
        try:
            renamed = target.with_name(target.name + ".old_ahootsa_delete")
            if renamed.exists():
                if renamed.is_dir():
                    shutil.rmtree(renamed, ignore_errors=True)
                else:
                    renamed.unlink(missing_ok=True)
            target.rename(renamed)
            print(f"RENAMED_FOR_IGNORE {target} -> {renamed}")
        except Exception as exc:
            print(f"REMOVE_ERROR {target} {type(exc).__name__}: {exc}")
            raise
print("CLEAN_OK")
'@ | Set-Content -Encoding UTF8 -LiteralPath $Cleaner
    Invoke-PythonSafe -ArgsList @($Cleaner, $SitePackages) -ErrorMessage "La limpieza manual de Ahootsa falló" | Out-Null

    Write-Host "[INFO] Limpiando residuos Ahootsa copiados en paquetes oficiales para evitar colisiones de tools/perfiles..."
    $CollisionCleaner = Join-Path $env:TEMP "ahootsa_clean_collisions_7_0_15.py"
@'
from __future__ import annotations
from pathlib import Path
import shutil
import sys
import time

site = Path(sys.argv[1])

# Estos nombres proceden de versiones anteriores de Ahootsa que copiaban herramientas
# dentro de reachy_mini_conversation_app/tools. La app oficial los detecta como
# built-in y luego choca con la capa externa Ahootsa. Se eliminan solo estos
# residuos Ahootsa; no se borran herramientas oficiales como camera, dance,
# play_emotion, stop_emotion, task_status, etc.
AHOOTSA_TOOL_STEMS = {
    "actividades_comunicacion",
    "ahootsa_debug_logger",
    "ahootsa_logging",
    "ask_ollama",
    "camera_pc",
    "choose_memory_cards",
    "explore_image",
    "hint_memory_pairs_game",
    "list_all_activities",
    "list_communication_activities",
    "list_communication_activity_levels",
    "list_community_dances",
    "list_emotions",
    "list_memory_pairs_games",
    "list_panel_dances_activities",
    "memory_pairs_game_server",
    "memory_pairs_game_status",
    "play_community_dance",
    "play_panel_dance_activity",
    "reset_memory_pairs_game",
    "start_communication_activity",
    "start_memory_pairs_game",
}
AHOOTSA_PROFILE_NAMES = {
    "ahootsa_realtime_es",
    "ahootsa_rapido",
    "ahootsa_actividades",
    "ahootsa_completo",
    "ahootsa5_realtime_es",
    "ahootsa7_realtime_es",  # por si una versión previa lo copió a built-in por error
    "ahootsa7_rapido",
    "ahootsa7_actividades",
    "ahootsa7_completo",
}
TOOL_ROOTS = [
    site / "reachy_mini_conversation_app" / "tools",
    site / "reachy_talk_data" / "tools",
]
PROFILE_ROOTS = [
    site / "reachy_mini_conversation_app" / "profiles",
    site / "reachy_talk_data" / "profiles",
]
SUFFIXES = [".py", ".json", ".txt", ".md", ".html", ".ini", ".cfg", ".yaml", ".yml"]
removed = []

def remove_path(path: Path) -> None:
    if not path.exists():
        return
    for attempt in range(3):
        try:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            removed.append(str(path))
            return
        except Exception as exc:
            print(f"COLLISION_REMOVE_WARN attempt={attempt+1} {path} {type(exc).__name__}: {exc}")
            time.sleep(0.3)
    raise RuntimeError(f"No se pudo eliminar residuo Ahootsa: {path}")

for root in TOOL_ROOTS:
    if not root.exists():
        continue
    for stem in AHOOTSA_TOOL_STEMS:
        for suffix in SUFFIXES:
            remove_path(root / f"{stem}{suffix}")
        # limpiar pycache relacionado
        pycache = root / "__pycache__"
        if pycache.exists():
            for item in pycache.glob(f"{stem}*.pyc"):
                remove_path(item)

for root in PROFILE_ROOTS:
    if not root.exists():
        continue
    for name in AHOOTSA_PROFILE_NAMES:
        remove_path(root / name)
    # eliminar perfiles Ahootsa residuales por patrón, pero solo dentro de roots oficiales
    for item in list(root.glob("ahootsa*")):
        remove_path(item)

print("COLLISION_CLEAN_OK removed_count=", len(removed))
for item in removed[:200]:
    print("REMOVED_AHOOTSA_RESIDUE", item)
'@ | Set-Content -Encoding UTF8 -LiteralPath $CollisionCleaner
    Invoke-PythonSafe -ArgsList @($CollisionCleaner, $SitePackages) -ErrorMessage "La limpieza de colisiones Ahootsa en paquetes oficiales falló" | Out-Null
}

Write-Host "[INFO] Instalando paquete Ahootsa 7.0.15 desde esta carpeta..."
Write-Host "[INFO] Se usa --ignore-installed y limpieza previa para evitar instalaciones corruptas sin RECORD."
Invoke-PythonSafe -ArgsList @('-m','pip','install','--no-cache-dir','--ignore-installed','--no-deps',$Root) -ErrorMessage "pip install de Ahootsa 7.0.15 ha fallado" | Out-Null

if (-not $SkipPygame) {
    Write-Host "[INFO] Instalando/comprobando pygame para audio de emociones..."
    Invoke-PythonSafe -ArgsList @('-m','pip','install','--upgrade','pygame') -ErrorMessage "No se pudo instalar pygame" | Out-Null
}
if (-not $SkipMujoco) {
    Write-Host "[INFO] Instalando/comprobando mujoco..."
    Invoke-PythonSafe -ArgsList @('-m','pip','install','--upgrade','mujoco') -ErrorMessage "No se pudo instalar mujoco" | Out-Null
}
if (-not $SkipOpenCV) {
    Write-Host "[INFO] Instalando/comprobando opencv-python para camera_pc..."
    Invoke-PythonSafe -ArgsList @('-m','pip','install','--upgrade','opencv-python') -ErrorMessage "No se pudo instalar opencv-python" | Out-Null
}

Write-Host "[INFO] Comprobando import, versión y entrypoint Reachy..."
Invoke-PythonSafe -ArgsList @('-c', "import ahootsa_realtime_ollama_desktop_app as a; print('AHOOTSA_IMPORT_OK', a.__version__); raise SystemExit(0 if a.__version__=='7.0.15' else 1)") -ErrorMessage "La versión importada no es 7.0.15" | Out-Null
Invoke-PythonSafe -ArgsList @('-c', "import importlib.metadata as m; eps=list(m.entry_points(group='reachy_mini_apps')); print('REACHY_MINI_APPS_ENTRYPOINTS=', [(e.name,e.value) for e in eps]); ok=any(e.name=='ahootsa_realtime_ollama_app' for e in eps); raise SystemExit(0 if ok else 2)") -ErrorMessage "No aparece el entrypoint ahootsa_realtime_ollama_app" | Out-Null
Invoke-PythonSafe -ArgsList @('-c', "from ahootsa_realtime_ollama_desktop_app.main import AhootsaRealtimeOllamaApp; print('AHOOTSA_APP_CLASS_OK', AhootsaRealtimeOllamaApp)") -ErrorMessage "No carga AhootsaRealtimeOllamaApp" | Out-Null

if (-not $SkipPygame) { Invoke-PythonSafe -ArgsList @('-c', "import pygame; print('PYGAME_OK', pygame.version.ver)") -ErrorMessage "pygame no importa" | Out-Null }
if (-not $SkipOpenCV) { Invoke-PythonSafe -ArgsList @('-c', "import cv2; print('OPENCV_OK', cv2.__version__)") -ErrorMessage "opencv-python no importa" | Out-Null }
if (-not $SkipMujoco) { Invoke-PythonSafe -ArgsList @('-c', "import mujoco; print('MUJOCO_OK', mujoco.__version__)") -ErrorMessage "mujoco no importa" | Out-Null }

if (-not $SkipEmotionLibraryDownload) {
    Write-Host "[INFO] Descargando/comprobando librería de emociones en D:\RITXI\reachy-mini-emotions-library..."
    $TmpPy = Join-Path $env:TEMP 'ahootsa_download_emotions_7_0_15.py'
@'
from pathlib import Path
try:
    from huggingface_hub import snapshot_download
    out = Path(r"D:\RITXI\reachy-mini-emotions-library")
    out.mkdir(parents=True, exist_ok=True)
    path = snapshot_download(repo_id="pollen-robotics/reachy-mini-emotions-library", repo_type="dataset", local_dir=str(out))
    print("EMOTIONS_LIBRARY_OK", path)
except Exception as exc:
    print("EMOTIONS_LIBRARY_WARN", type(exc).__name__, exc)
'@ | Set-Content -Encoding UTF8 -LiteralPath $TmpPy
    Invoke-PythonSafe -ArgsList @($TmpPy) -ErrorMessage "Fallo al comprobar/descargar librería de emociones" -AllowFail | Out-Null
}

Write-Host "[OK] Ahootsa 7.0.15 instalada y registrada."
Write-Host "[OK] Si el daemon estaba abierto antes de instalar, reinícialo o lanza con -RestartDaemon."
