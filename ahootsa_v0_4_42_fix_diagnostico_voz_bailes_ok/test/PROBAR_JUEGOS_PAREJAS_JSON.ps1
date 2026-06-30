# PROBAR_JUEGOS_PAREJAS_JSON.ps1
# Ubicación actual: subcarpeta test.
# Ejecutar desde la raíz con: powershell -ExecutionPolicy Bypass -File .\test\PROBAR_JUEGOS_PAREJAS_JSON.ps1

# Prueba el motor JSON de juegos de parejas sin abrir Reachy Mini Desktop.

$ErrorActionPreference = "Continue"

function Header($Text) {
    Write-Host ""
    Write-Host "============================================"
    Write-Host " $Text"
    Write-Host "============================================"
}
function Fail($Text) { Write-Host "[ERROR] $Text" -ForegroundColor Red; exit 1 }

Header "Probar motor JSON de juegos de parejas"

$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$Python = Join-Path $DesktopDir "apps_venv\Scripts\python.exe"
if (-not (Test-Path $Python)) { Fail "No existe apps_venv Python: $Python" }

$Profile = Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\ahootsa_realtime_es"
$ServerPy = Join-Path $Profile "memory_pairs_game_server.py"
if (-not (Test-Path $ServerPy)) { Fail "No existe memory_pairs_game_server.py. Instala primero v0.4.42." }

$tmp = Join-Path $env:TEMP "probar_juegos_parejas_json_ahootsa.py"

@'
from pathlib import Path
import importlib.util, sys, time, urllib.request, json

server_py = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("ahootsa_memory_pairs_json_test", server_py)
mod = importlib.util.module_from_spec(spec)
sys.modules["ahootsa_memory_pairs_json_test"] = mod
spec.loader.exec_module(mod)

r = mod.start_server(port=7870, open_browser=True, reset=True, game_id="animales")
print("start=", json.dumps(r, ensure_ascii=False)[:700])
if not r.get("ok"):
    sys.exit(2)

url = r["url"]
games = json.loads(urllib.request.urlopen(url + "games", timeout=5).read().decode("utf-8"))
print("games=", json.dumps(games, ensure_ascii=False, indent=2))

for gid in ["animales", "ciudades", "alimentos"]:
    state = json.loads(urllib.request.urlopen(url + "select_game?game_id=" + gid, timeout=5).read().decode("utf-8"))
    current = json.loads(urllib.request.urlopen(url + "state", timeout=5).read().decode("utf-8"))
    print("game=", gid, "title=", current["title"], "cards=", len(current["cards"]), "pairs=", current["total_pairs"])

print("Servidor activo 25 segundos.")
print(url)
time.sleep(25)
'@ | Set-Content -Encoding UTF8 $tmp

& $Python $tmp $ServerPy
Remove-Item $tmp -Force -ErrorAction SilentlyContinue

Header "Final"
Write-Host "Si se abrió el navegador, prueba el selector de juegos: animales, ciudades, alimentos."
