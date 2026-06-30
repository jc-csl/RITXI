# PROBAR_MEMORY_MODULO_DIRECTO.ps1
# Prueba solo importación del módulo memory_pairs_game_server.py.

$ErrorActionPreference = "Continue"

$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$Python = Join-Path $DesktopDir "apps_venv\Scripts\python.exe"
$ServerPy = Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\ahootsa_realtime_es\memory_pairs_game_server.py"

$tmp = Join-Path $env:TEMP "test_memory_module_direct_ahootsa.py"

@'
import importlib.util, sys, json
from pathlib import Path

server_py = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("memory_pairs_direct_test", server_py)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

print("has_start_server=", hasattr(mod, "start_server"))
print("self_test=", json.dumps(mod._self_test(), ensure_ascii=False))
'@ | Set-Content -Encoding UTF8 $tmp

& $Python $tmp $ServerPy
Remove-Item $tmp -Force -ErrorAction SilentlyContinue
