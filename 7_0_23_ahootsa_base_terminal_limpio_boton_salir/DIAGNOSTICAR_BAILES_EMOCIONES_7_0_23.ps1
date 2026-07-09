param(
    [string]$AppVenv = "$env:LOCALAPPDATA\Reachy Mini Control\apps_venv"
)
$ErrorActionPreference = "Continue"
$Py = Join-Path $AppVenv "Scripts\python.exe"
Write-Host "============================================================"
Write-Host "Diagnóstico bailes/emociones Ahootsa 7.0.23"
Write-Host "============================================================"
Write-Host "Python: $Py"
$code = @"
import importlib, pathlib, os, importlib.util
pkg = importlib.import_module('ahootsa_realtime_ollama_desktop_app')
root = pathlib.Path(pkg.__file__).parent
print('PACKAGE_ROOT', root)
print('VERSION', getattr(pkg, '__version__', '?'))
profile = os.environ.get('AHOOTSA_PROFILE','ahootsa7_realtime_es')
path = root/'profiles'/profile/'play_emotion.py'
if not path.exists(): path = root/'profiles'/'ahootsa7_realtime_es'/'play_emotion.py'
print('PLAY_EMOTION_FILE', path)
spec = importlib.util.spec_from_file_location('diag_play_emotion', path)
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
print('DATASET_DIR', mod.get_dataset_dir())
moves = set(mod.list_moves())
print('COUNT_MOVES', len(moves))
for mid in ['dance1','dance2','dance3','success1','welcoming2','calming1','electric1']:
    ds = mod.get_dataset_dir()
    print('RESOURCE', mid, 'json=', bool(ds and (ds/(mid+'.json')).exists()), 'ogg=', bool(ds and (ds/(mid+'.ogg')).exists()), 'display=', mod.display_name_for_move(mid), 'available=', mid in moves)
for text in ['baile uno','baile dos','baile número dos','dos','baile tres','baile número tres','tres','celebración','saludo','saludo ahootsa','sludo','sluod','calma','eléctrico','dance1','dance2','dance3']:
    print('RESOLVE', text, '=>', mod.resolve_emotion_name(text))
"@
& $Py -c $code
