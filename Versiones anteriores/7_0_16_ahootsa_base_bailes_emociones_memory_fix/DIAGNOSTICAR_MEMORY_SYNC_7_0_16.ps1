param(
    [string]$AppVenv = "$env:LOCALAPPDATA\Reachy Mini Control\apps_venv"
)
$ErrorActionPreference = 'Continue'
$Py = Join-Path $AppVenv 'Scripts\python.exe'
Write-Host '============================================================'
Write-Host 'Diagnostico Memory Sync Ahootsa 7.0.16'
Write-Host '============================================================'
$Code = @'
import importlib, sys, pathlib
print('Python OK')
try:
    from ahootsa_realtime_ollama_desktop_app import __version__
    print('version', __version__)
except Exception as e:
    print('version error', repr(e))
try:
    import ahootsa_realtime_ollama_desktop_app.ahootsa_routes as r
    m1 = r._memory_mod()
    print('routes memory module', m1.__name__, id(m1), 'game id', id(getattr(m1, '_GAME', None)))
except Exception as e:
    print('routes error', repr(e))
try:
    import importlib.util
    import ahootsa_realtime_ollama_desktop_app as pkg
    tool = pathlib.Path(pkg.__file__).parent / 'tools' / 'choose_memory_cards.py'
    spec = importlib.util.spec_from_file_location('diag_choose_memory_cards', tool)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    m2 = mod._game()
    print('voice memory module', m2.__name__, id(m2), 'game id', id(getattr(m2, '_GAME', None)))
except Exception as e:
    print('voice error', repr(e))
print('shared keys', [k for k in sys.modules if 'ahootsa_shared_tool_memory_pairs_game_server' in k])
'@
$Tmp = Join-Path $env:TEMP 'ahootsa_memory_sync_7_0_16.py'
$Code | Set-Content -Encoding UTF8 -LiteralPath $Tmp
& $Py $Tmp
Write-Host ''
Write-Host '[HTTP] Probando endpoints si la app esta arrancada:'
foreach($u in @('http://127.0.0.1:7860/memory/state','http://127.0.0.1:7860/memory/page')){
  try { $r=Invoke-WebRequest -Uri $u -UseBasicParsing -TimeoutSec 4; Write-Host "$u -> $($r.StatusCode)" }
  catch { Write-Host "$u -> ERROR $($_.Exception.Message)" }
}
