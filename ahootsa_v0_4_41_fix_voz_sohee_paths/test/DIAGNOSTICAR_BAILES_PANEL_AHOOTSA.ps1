# DIAGNOSTICAR_BAILES_PANEL_AHOOTSA.ps1
# Lista movimientos/bailes disponibles en la librería local de emociones.

function Join-Many([string[]]$Parts) {
    if ($Parts.Count -eq 0) { return "" }
    $p = $Parts[0]
    for ($i = 1; $i -lt $Parts.Count; $i++) {
        $p = Join-Path $p $Parts[$i]
    }
    return $p
}

$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$Python = Join-Many @($DesktopDir, "apps_venv", "Scripts", "python.exe")
$ToolPy = Join-Many @($DesktopDir, "apps_venv", "Lib", "site-packages", "reachy_mini_conversation_app", "profiles", "ahootsa_realtime_es", "play_emotion.py")

if (-not (Test-Path -LiteralPath $Python)) { Write-Host "No existe Python: $Python"; exit 1 }
if (-not (Test-Path -LiteralPath $ToolPy)) { Write-Host "No existe play_emotion.py: $ToolPy"; exit 2 }

$tmp = Join-Path $env:TEMP "diag_bailes_panel_ahootsa.py"
@'
import importlib.util, sys
from pathlib import Path

tool_py = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("diag_panel_play_emotion", tool_py)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

moves = list(mod.list_moves())
print("dataset_dir=", mod.get_dataset_dir())
print("count=", len(moves))
print("dances=", [m for m in moves if m.startswith("dance")])
print("greetings=", [m for m in moves if m.startswith(("welcoming","come"))])
print("successes=", [m for m in moves if m.startswith(("success","proud","grateful"))])
print("examples=", [m for m in moves if m in {"electric1","dying1","sleep1","amazed1","laughing2","calming1","thoughtful1"}])
'@ | Set-Content -Encoding UTF8 $tmp

& $Python $tmp $ToolPy
Remove-Item $tmp -Force -ErrorAction SilentlyContinue
