# PROBAR_MEMORY_START_SERVER.ps1
# Prueba directa del servidor Memory sin Reachy Mini Desktop.
# Sirve para comprobar que http://localhost:7870/ funciona.

$ErrorActionPreference = "Continue"

function Header($Text) {
    Write-Host ""
    Write-Host "============================================"
    Write-Host " $Text"
    Write-Host "============================================"
}
function Fail($Text) { Write-Host "[ERROR] $Text" -ForegroundColor Red; exit 1 }

Header "Probar Memory start_server"

$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$Python = Join-Path $DesktopDir "apps_venv\Scripts\python.exe"
$ServerPy = Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\ahootsa_realtime_es\memory_pairs_game_server.py"

if (-not (Test-Path $Python)) { Fail "No existe Python apps_venv: $Python" }
if (-not (Test-Path $ServerPy)) { Fail "No existe memory_pairs_game_server.py instalado: $ServerPy" }

$tmp = Join-Path $env:TEMP "test_memory_start_server_ahootsa.py"

@'
import importlib.util, sys, time, urllib.request, json
from pathlib import Path

server_py = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("test_memory_pairs_game_server", server_py)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

print("has_start_server=", hasattr(mod, "start_server"))
if not hasattr(mod, "start_server"):
    sys.exit(2)

r = mod.start_server(port=7870, open_browser=True, reset=True, game_id="animales")
print("start=", json.dumps(r, ensure_ascii=False)[:800])

url = r["url"]
html = urllib.request.urlopen(url, timeout=5).read().decode("utf-8")
print("html_ok=", "card-back" in html or "Memory" in html)
state = json.loads(urllib.request.urlopen(url + "state", timeout=5).read().decode("utf-8"))
print("cards=", len(state["cards"]), "pairs=", state["total_pairs"], "title=", state["title"])
print("Servidor activo 25 segundos:", url)
time.sleep(25)
'@ | Set-Content -Encoding UTF8 $tmp

& $Python $tmp $ServerPy
Remove-Item $tmp -Force -ErrorAction SilentlyContinue

Header "Final"
Write-Host "Si se ha abierto el navegador con cartas azules, está corregido."
