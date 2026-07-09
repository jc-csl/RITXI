param(
    [string]$Profile = "ahootsa7_realtime_es",
    [switch]$TestMemoryActions,
    [switch]$DeepLogs
)

$ErrorActionPreference = "Continue"
$LogRoot = "D:\RITXI\logs"
New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$OutFile = Join-Path $LogRoot "AHOOTSA_DIAGNOSTICO_PROVISIONAL_${Stamp}.log"

function W($Text = "") { $Text | Tee-Object -FilePath $OutFile -Append }
function Section($Title) { W ""; W ("=" * 78); W $Title; W ("=" * 78) }
function Try-Web($Name, $Url) {
    W "--- $Name : $Url"
    try {
        $r = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 5
        W ("HTTP " + [int]$r.StatusCode + " length=" + $r.Content.Length)
        $txt = $r.Content
        if ($txt.Length -gt 1200) { $txt = $txt.Substring(0,1200) + " ...[recortado]" }
        W $txt
    } catch {
        W ("ERROR: " + $_.Exception.Message)
    }
}

Section "DIAGNOSTICO PROVISIONAL AHOOTSA 7.0.15"
W "Generado: $(Get-Date -Format o)"
W "Equipo: $env:COMPUTERNAME"
W "Usuario: $env:USERNAME"
W "Perfil solicitado: $Profile"
W "Salida: $OutFile"

$AppVenv = Join-Path $env:LOCALAPPDATA "Reachy Mini Control\apps_venv"
$Python = Join-Path $AppVenv "Scripts\python.exe"
Section "PYTHON / ENTORNO"
W "AppVenv: $AppVenv"
W "Python:  $Python"
if (!(Test-Path $Python)) {
    W "ERROR: No existe python.exe del apps_venv. No se puede continuar con la parte Python."
} else {
    try { & $Python --version 2>&1 | Tee-Object -FilePath $OutFile -Append } catch { W $_.Exception.Message }
}

Section "PUERTOS Y PROCESOS"
try {
    Get-NetTCPConnection -LocalPort 8000,7860 -ErrorAction SilentlyContinue |
        Select-Object LocalAddress,LocalPort,State,OwningProcess |
        ForEach-Object {
            $pn = ""
            try { $pn = (Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue).ProcessName } catch {}
            W ("port={0} state={1} pid={2} process={3}" -f $_.LocalPort,$_.State,$_.OwningProcess,$pn)
        }
} catch { W ("Get-NetTCPConnection error: " + $_.Exception.Message) }

Section "ENDPOINTS HTTP ACTIVOS"
Try-Web "Daemon check-updates" "http://127.0.0.1:8000/api/apps/check-updates"
Try-Web "Panel /ahootsa" "http://127.0.0.1:7860/ahootsa"
Try-Web "Memory games" "http://127.0.0.1:7860/memory/games"
Try-Web "Memory state" "http://127.0.0.1:7860/memory/state"
Try-Web "Memory page" "http://127.0.0.1:7860/memory/page?game_id=animales&reset=0"
Try-Web "Voz actual" "http://127.0.0.1:7860/voices/current"
Try-Web "Audio status" "http://127.0.0.1:7860/audio/status"
Try-Web "Ollama status" "http://127.0.0.1:7860/ollama/status"

if (Test-Path $Python) {
    Section "INSPECCION PYTHON: PAQUETE, PERFIL, REGISTRO DE TOOLS, BAILES, MEMORY"
    $env:AHOOTSA_DIAG_PROFILE = $Profile
    if ($TestMemoryActions) { $env:AHOOTSA_DIAG_TEST_MEMORY_ACTIONS = "1" } else { $env:AHOOTSA_DIAG_TEST_MEMORY_ACTIONS = "0" }
    $py = @'
import os, sys, json, importlib, importlib.util, site, traceback, asyncio
from pathlib import Path

profile = os.environ.get("AHOOTSA_DIAG_PROFILE") or "ahootsa7_realtime_es"

def j(title, data):
    print("\n### " + title)
    try:
        print(json.dumps(data, ensure_ascii=False, indent=2, default=str))
    except Exception:
        print(repr(data))

def load_file_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"No se puede cargar {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

try:
    import ahootsa_realtime_ollama_desktop_app as pkg
    package_root = Path(pkg.__file__).resolve().parent
    j("Ahootsa instalado", {"package_file": str(pkg.__file__), "package_root": str(package_root), "version": getattr(pkg, "__version__", None)})
except Exception as e:
    j("ERROR importando Ahootsa", {"error": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc()})
    raise SystemExit(1)

profiles_dir = package_root / "profiles"
tools_dir = package_root / "tools"
os.environ["REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY"] = str(profiles_dir)
os.environ["REACHY_MINI_EXTERNAL_TOOLS_DIRECTORY"] = str(tools_dir)
os.environ["REACHY_MINI_CUSTOM_PROFILE"] = profile
os.environ["REACHY_MINI_PROFILE"] = profile
os.environ["AHOOTSA_PROFILE"] = profile
os.environ.setdefault("AHOOTSA_APP_BASE_URL", "http://127.0.0.1:7860")
os.environ.setdefault("AHOOTSA_MEMORY_INTEGRATED", "1")
os.environ.setdefault("AHOOTSA_EMOTION_AUDIO_BACKEND", "pygame")
os.environ.setdefault("AHOOTSA_DISABLE_EMOTION_AUDIO", "0")
os.environ.setdefault("AHOOTSA_PHOTOS_DIR", r"D:\RITXI\fotos")

profile_dir = profiles_dir / profile
tools_txt = profile_dir / "tools.txt"
instructions_txt = profile_dir / "instructions.txt"
j("Rutas Ahootsa", {
    "profiles_dir": str(profiles_dir), "profiles_exists": profiles_dir.exists(),
    "tools_dir": str(tools_dir), "tools_exists": tools_dir.exists(),
    "profile_dir": str(profile_dir), "profile_exists": profile_dir.exists(),
    "tools_txt": str(tools_txt), "tools_txt_exists": tools_txt.exists(),
    "instructions_txt_exists": instructions_txt.exists(),
})
if tools_txt.exists():
    enabled = [x.strip() for x in tools_txt.read_text(encoding="utf-8").splitlines() if x.strip() and not x.strip().startswith("#")]
    j("Tools habilitadas en tools.txt", enabled)
if instructions_txt.exists():
    j("Primeras líneas de instructions.txt", instructions_txt.read_text(encoding="utf-8").splitlines()[:30])

try:
    from reachy_mini_conversation_app.config import refresh_runtime_config_from_env, config, DEFAULT_PROFILES_DIRECTORY
    refresh_runtime_config_from_env()
    j("Config oficial tras refresh_runtime_config_from_env", {
        "REACHY_MINI_CUSTOM_PROFILE": getattr(config, "REACHY_MINI_CUSTOM_PROFILE", None),
        "PROFILES_DIRECTORY": str(getattr(config, "PROFILES_DIRECTORY", None)),
        "TOOLS_DIRECTORY": str(getattr(config, "TOOLS_DIRECTORY", None)),
        "AUTOLOAD_EXTERNAL_TOOLS": getattr(config, "AUTOLOAD_EXTERNAL_TOOLS", None),
        "DEFAULT_PROFILES_DIRECTORY": str(DEFAULT_PROFILES_DIRECTORY),
    })
except Exception as e:
    j("ERROR config oficial", {"error": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc()})

try:
    from reachy_mini_conversation_app.tools import core_tools
    core_tools.initialize_tools(force=True)
    registry = {}
    for name, tool in sorted(core_tools.ALL_TOOLS.items()):
        registry[name] = {
            "class": tool.__class__.__name__,
            "module": tool.__class__.__module__,
            "needs_response": getattr(tool, "needs_response", None),
            "description_start": (getattr(tool, "description", "") or "")[:180],
        }
    wanted = ["list_panel_dances_activities", "play_panel_dance_activity", "play_emotion", "list_emotions", "start_memory_pairs_game", "choose_memory_cards", "memory_pairs_game_status", "reset_memory_pairs_game", "dance"]
    j("Registro oficial de herramientas: resumen", {"count": len(registry), "tool_names": sorted(registry.keys()), "wanted_present": {w: w in registry for w in wanted}})
    j("Registro oficial de herramientas: detalle herramientas Ahootsa/interesantes", {k:v for k,v in registry.items() if k in wanted or k.startswith("list_") or "memory" in k or "dance" in k or "emotion" in k})
except Exception as e:
    j("ERROR inicializando registro de tools", {"error": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc()})

try:
    pe_path = profile_dir / "play_emotion.py"
    pe = load_file_module("diag_profile_play_emotion", pe_path)
    dataset_dir = pe.get_dataset_dir() if hasattr(pe, "get_dataset_dir") else None
    moves = pe.list_moves() if hasattr(pe, "list_moves") else []
    wanted_moves = ["dance1", "dance2", "dance3", "welcoming2", "welcoming1", "success1", "calming1", "electric1", "laughing2", "yes1", "no1"]
    file_checks = {}
    if dataset_dir:
        dp = Path(dataset_dir)
        for mid in wanted_moves:
            file_checks[mid] = {"json": (dp / f"{mid}.json").exists(), "ogg": (dp / f"{mid}.ogg").exists()}
    aliases = ["baile uno", "baile dos", "baile número dos", "dos", "baile tres", "tres", "saludo", "saludo ahootsa", "sludo", "sluod", "celebración", "calma", "eléctrico", "risa", "sí", "no"]
    resolved = {}
    for a in aliases:
        try: resolved[a] = pe.resolve_emotion_name(a)
        except Exception as e: resolved[a] = f"ERROR {type(e).__name__}: {e}"
    j("Bailes/emociones: dataset, ficheros y resolución de aliases", {
        "dataset_dir": str(dataset_dir) if dataset_dir else None,
        "moves_count": len(moves),
        "wanted_in_list_moves": {m: m in set(moves) for m in wanted_moves},
        "file_checks": file_checks,
        "resolved_aliases": resolved,
        "available_examples_es": pe.available_examples_es() if hasattr(pe, "available_examples_es") else None,
    })
except Exception as e:
    j("ERROR inspeccionando play_emotion.py", {"error": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc()})

try:
    lp_path = tools_dir / "list_panel_dances_activities.py"
    lp = load_file_module("diag_list_panel_dances_activities", lp_path)
    result = asyncio.run(lp.ListPanelDancesActivities()(None))
    j("Ejecución directa list_panel_dances_activities", result)
except Exception as e:
    j("ERROR ejecutando list_panel_dances_activities", {"error": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc()})

try:
    mem_path = tools_dir / "memory_pairs_game_server.py"
    mem = load_file_module("ahootsa_shared_tool_memory_pairs_game_server", mem_path)
    info = {"available_games": mem.available_games(), "status_before": mem.status()}
    if os.environ.get("AHOOTSA_DIAG_TEST_MEMORY_ACTIONS") == "1":
        info["reset_animales"] = mem.reset_game("animales")
        info["status_after_reset"] = mem.status()
        info["choose_1_2"] = mem.choose_cards(1, 2)
        info["status_after_choose"] = mem.status()
    j("Memory interno directo", info)
except Exception as e:
    j("ERROR inspeccionando memory_pairs_game_server", {"error": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc()})

try:
    sm_path = tools_dir / "start_memory_pairs_game.py"
    sm = load_file_module("diag_start_memory_pairs_game", sm_path)
    result = asyncio.run(sm.StartMemoryPairsGame()(None, game_id="animales", reset=False, open_browser=False))
    j("Ejecución directa start_memory_pairs_game(reset=False)", result)
except Exception as e:
    j("ERROR ejecutando start_memory_pairs_game", {"error": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc()})

try:
    # Revisa contaminación Ahootsa en paquetes oficiales que podría provocar que el modelo vea herramientas duplicadas o equivocadas.
    spaths = []
    try: spaths += site.getsitepackages()
    except Exception: pass
    try: spaths.append(site.getusersitepackages())
    except Exception: pass
    ahootsa_stems = {"actividades_comunicacion","ahootsa_debug_logger","ahootsa_logging","ask_ollama","camera_pc","choose_memory_cards","explore_image","hint_memory_pairs_game","list_all_activities","list_communication_activities","list_communication_activity_levels","list_community_dances","list_emotions","list_memory_pairs_games","list_panel_dances_activities","memory_pairs_game_server","memory_pairs_game_status","play_community_dance","play_panel_dance_activity","reset_memory_pairs_game","start_communication_activity","start_memory_pairs_game"}
    residues = []
    for sp in spaths:
        if not sp: continue
        root = Path(sp)
        for rel in ["reachy_mini_conversation_app/tools", "reachy_talk_data/tools", "reachy_mini_conversation_app/profiles", "reachy_talk_data/profiles"]:
            p = root / rel
            if not p.exists(): continue
            for child in p.iterdir():
                stem = child.stem if child.is_file() else child.name
                if stem in ahootsa_stems or stem.lower().startswith("ahootsa"):
                    residues.append(str(child))
    j("Residuos Ahootsa en rutas oficiales", {"count": len(residues), "items": residues[:200]})
except Exception as e:
    j("ERROR comprobando residuos", {"error": f"{type(e).__name__}: {e}", "traceback": traceback.format_exc()})
'@
    try {
        $py | & $Python - 2>&1 | Tee-Object -FilePath $OutFile -Append
    } catch {
        W ("ERROR ejecutando bloque Python: " + $_.Exception.Message)
    }
}

Section "ULTIMOS LOGS DE LA ULTIMA SESION"
try {
    $logs = Get-ChildItem $LogRoot -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -like "ahootsa7_*" } | Sort-Object LastWriteTime -Descending | Select-Object -First 8
    foreach ($lf in $logs) {
        W "--- $($lf.FullName)  size=$($lf.Length)  lastwrite=$($lf.LastWriteTime.ToString('o'))"
        try { Get-Content $lf.FullName -Tail 80 -ErrorAction SilentlyContinue | Tee-Object -FilePath $OutFile -Append } catch { W $_.Exception.Message }
    }
} catch { W ("ERROR leyendo logs: " + $_.Exception.Message) }

if ($DeepLogs) {
    Section "BUSQUEDA PROFUNDA EN LOGS"
    try {
        $patterns = "tool_start|tool_result|play_panel|play_emotion|list_panel|memory|parejas|dance|baile|emotion|saludo|unknown tool|no he podido|error|traceback|exception"
        Get-ChildItem $LogRoot -File -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -gt (Get-Date).AddHours(-6) } | ForEach-Object {
            $file = $_.FullName
            Select-String -Path $file -Pattern $patterns -CaseSensitive:$false -ErrorAction SilentlyContinue | Select-Object -First 200 | ForEach-Object {
                W ("{0}:{1}: {2}" -f $_.Path,$_.LineNumber,$_.Line)
            }
        }
        $extra = Join-Path $env:LOCALAPPDATA "Reachy Mini Control\ahootsa_logs\play_emotion_audio.log"
        if (Test-Path $extra) {
            W "--- $extra"
            Get-Content $extra -Tail 200 -ErrorAction SilentlyContinue | Tee-Object -FilePath $OutFile -Append
        }
    } catch { W ("ERROR busqueda profunda: " + $_.Exception.Message) }
}

Section "FIN"
W "Diagnostico guardado en: $OutFile"
W "Pasa este archivo para revisar la causa exacta."
Write-Host "`nDiagnostico guardado en: $OutFile" -ForegroundColor Green
