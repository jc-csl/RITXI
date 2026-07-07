# DIAGNOSTICAR_5_MEMORY_ACTIVIDADES_FLUIDEZ.ps1
# Ahootsa 5.0.24: comprueba cambios de Memory hablado y actividades intermedias.

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Py = Join-Path $env:LOCALAPPDATA "Reachy Mini Control\apps_venv\Scripts\python.exe"
$Src = Join-Path $Root "src"

Write-Host "============================================================"
Write-Host "Diagnóstico Ahootsa 5.0.24 Memory + actividades"
Write-Host "============================================================"

if (-not (Test-Path $Py)) {
  Write-Host "[ERROR] No existe Python de Reachy Mini Control: $Py"
  exit 1
}

$env:PYTHONPATH = $Src

& $Py - <<'PY'
import json, pathlib, sys
base = pathlib.Path(r"/mnt/data/5_0_24_ahootsa_memory_habla_actividades_intermedias") / "src" / "ahootsa_realtime_ollama_desktop_app"
print("base =", base)
for name in ["choose_memory_cards.py","start_memory_pairs_game.py","list_communication_activity_levels.py","list_communication_activities.py","start_communication_activity.py"]:
    text = (base/name).read_text(encoding="utf-8")
    print(name, "needs_response=True", "needs_response = True" in text)
cat = json.loads((base/"communication_activities_catalog.json").read_text(encoding="utf-8"))
print("intro_question =", cat.get("intro_question"))
print("nivel interno normal label =", cat["levels"]["normal"]["label"])
seq = json.loads((base/"memory_sequence_config.json").read_text(encoding="utf-8"))
print("idle_prompt_seconds =", seq.get("idle_prompt_seconds"))
print("idle_prompt_text =", seq.get("idle_prompt_text"))
print("OK")
PY
