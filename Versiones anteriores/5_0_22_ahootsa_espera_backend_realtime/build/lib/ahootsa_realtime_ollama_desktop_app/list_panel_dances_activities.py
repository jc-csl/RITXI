"""List panel-like dances/activities available in the local emotions library."""
from __future__ import annotations
import importlib.util, sys
from pathlib import Path
from typing import Any
from reachy_mini_conversation_app.tools.core_tools import Tool, ToolDependencies


def _load_local_play_emotion():
    path = Path(__file__).resolve().with_name("play_emotion.py")
    stamp = str(int(path.stat().st_mtime_ns))
    name = f"ahootsa_panel_list_emotions_{stamp}"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if not (spec and spec.loader):
        raise ModuleNotFoundError("No se puede cargar play_emotion.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

class ListPanelDancesActivities(Tool):
    name = "list_panel_dances_activities"
    description = "Lista bailes y actividades/movimientos disponibles parecidos a los del panel de control."
    needs_response = True
    parameters_schema = {"type": "object", "properties": {}, "required": []}
    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> dict[str, Any]:
        mod = _load_local_play_emotion()
        moves = list(mod.list_moves())
        dances = [m for m in moves if m.startswith("dance")]
        greetings = [m for m in moves if m.startswith(("welcoming", "come"))]
        successes = [m for m in moves if m.startswith(("success", "proud", "grateful"))]
        thinking = [m for m in moves if m.startswith(("thoughtful", "inquiring", "attentive"))]
        other_examples = [m for m in moves if m in {"electric1", "dying1", "sleep1", "amazed1", "laughing2", "calming1"}]
        return {"ok": True, "count": len(moves), "dances": dances, "greetings": greetings, "successes": successes, "thinking": thinking, "other_examples": other_examples, "message_for_user": "Puedo reproducir bailes y actividades del panel. Prueba: dance1, dance2, dance3, welcoming2, success1 o electric1."}
