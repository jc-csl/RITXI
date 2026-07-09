$ErrorActionPreference = "Continue"
$Py = "C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Scripts\python.exe"
Write-Host "============================================================"
Write-Host "Diagnóstico Memory timing Ahootsa 7.0.22"
Write-Host "============================================================"
& $Py - <<'PY'
import importlib, json, pathlib
pkg = importlib.import_module('ahootsa_realtime_ollama_desktop_app')
root = pathlib.Path(pkg.__file__).parent
cfg = root / 'tools' / 'memory_timing_config.json'
print('package_root=', root)
print('config=', cfg)
print('config_exists=', cfg.exists())
if cfg.exists():
    print(cfg.read_text(encoding='utf-8'))
try:
    import importlib.util, sys
    path = root / 'tools' / 'memory_pairs_game_server.py'
    spec = importlib.util.spec_from_file_location('diag_memory_pairs_game_server', path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules['diag_memory_pairs_game_server'] = mod
    spec.loader.exec_module(mod)
    print('self_test=', json.dumps(mod._self_test(), ensure_ascii=False, indent=2))
except Exception as e:
    print('ERROR:', repr(e))
PY
try {
    Write-Host "`nEndpoint /memory/state:"
    Invoke-RestMethod -Uri "http://127.0.0.1:7860/memory/state" -TimeoutSec 5 | ConvertTo-Json -Depth 8
} catch { Write-Host "No responde /memory/state: $($_.Exception.Message)" }
