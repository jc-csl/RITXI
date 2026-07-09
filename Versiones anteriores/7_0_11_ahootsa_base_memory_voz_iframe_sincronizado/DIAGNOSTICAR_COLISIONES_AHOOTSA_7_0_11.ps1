param(
    [string]$AppVenv = "$env:LOCALAPPDATA\Reachy Mini Control\apps_venv"
)
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$Py = Join-Path $AppVenv "Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Py)) { throw "No encuentro python.exe en $Py" }
$Tmp = Join-Path $env:TEMP "ahootsa_diag_colisiones_7_0_11.py"
@'
from pathlib import Path
import importlib
import sysconfig
import os

AHOOTSA_TOOL_STEMS = {
    "actividades_comunicacion","ahootsa_debug_logger","ahootsa_logging","ask_ollama","camera_pc",
    "choose_memory_cards","explore_image","hint_memory_pairs_game","list_all_activities",
    "list_communication_activities","list_communication_activity_levels","list_community_dances",
    "list_emotions","list_memory_pairs_games","list_panel_dances_activities","memory_pairs_game_server",
    "memory_pairs_game_status","play_community_dance","play_panel_dance_activity",
    "reset_memory_pairs_game","start_communication_activity","start_memory_pairs_game",
}
PROFILE_PREFIXES = ("ahootsa",)

def dirs(root):
    p=Path(root)
    return {x.name for x in p.iterdir() if x.is_dir()} if p.exists() else set()

def tool_stems(root):
    p=Path(root)
    return {x.stem for x in p.glob("*.py") if x.name != "__init__.py"} if p.exists() else set()

site=Path(sysconfig.get_paths()["purelib"])
print("site-packages:", site)
try:
    a=importlib.import_module('ahootsa_realtime_ollama_desktop_app')
    aroot=Path(a.__file__).parent
    print('Ahootsa:', aroot, 'version=', getattr(a,'__version__','?'))
except Exception as e:
    print('AHOOTSA_IMPORT_ERROR', repr(e)); raise SystemExit(1)

external_profiles = aroot / 'profiles'
external_tools = aroot / 'tools'
builtin_profile_roots = [site/'reachy_talk_data'/'profiles', site/'reachy_mini_conversation_app'/'profiles']
builtin_tool_roots = [site/'reachy_mini_conversation_app'/'tools', site/'reachy_talk_data'/'tools']

print('\n[PERFILES]')
print('External:', external_profiles, sorted(dirs(external_profiles)))
for br in builtin_profile_roots:
    existing=dirs(br)
    ahootsa=[x for x in sorted(existing) if x.lower().startswith(PROFILE_PREFIXES)]
    print('Built-in:', br, 'ahootsa_residuos=', ahootsa)
    print('Collision with external:', sorted(dirs(external_profiles) & existing))

print('\n[TOOLS]')
print('External:', external_tools, 'count=', len(tool_stems(external_tools)))
for br in builtin_tool_roots:
    existing=tool_stems(br)
    bad=sorted(existing & AHOOTSA_TOOL_STEMS)
    print('Built-in:', br)
    print('Ahootsa residues:', bad)
    print('Collision with external:', sorted(tool_stems(external_tools) & existing))

print('\n[CONFIG IMPORT]')
os.environ['REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY'] = str(external_profiles)
os.environ['REACHY_MINI_EXTERNAL_TOOLS_DIRECTORY'] = str(external_tools)
os.environ['REACHY_MINI_CUSTOM_PROFILE'] = 'ahootsa7_realtime_es'
try:
    from reachy_mini_conversation_app.config import Config
    print('Config import OK')
except Exception as e:
    print('Config import ERROR:', type(e).__name__, e)
    raise SystemExit(2)
'@ | Set-Content -Encoding UTF8 -LiteralPath $Tmp
& $Py $Tmp
