"""List panel-like dances/activities with Spanish names and availability."""
from __future__ import annotations
import importlib.util, os, sys
from pathlib import Path
from typing import Any
from reachy_mini_conversation_app.tools.core_tools import Tool, ToolDependencies

def _profile_name() -> str:
    return (os.getenv("AHOOTSA_PROFILE") or os.getenv("REACHY_MINI_PROFILE") or "ahootsa7_realtime_es").strip() or "ahootsa7_realtime_es"

def _load_local_play_emotion():
    root = Path(__file__).resolve().parents[1]
    profile = _profile_name()
    for path in [root / "profiles" / profile / "play_emotion.py", root / "profiles" / "ahootsa7_realtime_es" / "play_emotion.py"]:
        if path.exists():
            name = f"ahootsa_profile_list_play_emotion_{int(path.stat().st_mtime_ns)}"
            if name in sys.modules:
                return sys.modules[name]
            spec = importlib.util.spec_from_file_location(name, path)
            if not (spec and spec.loader):
                continue
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            spec.loader.exec_module(mod)
            return mod
    raise ModuleNotFoundError("No se puede cargar play_emotion.py desde los perfiles Ahootsa")

class ListPanelDancesActivities(Tool):
    name = "list_panel_dances_activities"
    description = "Lista bailes y emociones disponibles con nombres en español y el identificador técnico interno."
    needs_response = True
    parameters_schema = {"type": "object", "properties": {"only_available": {"type":"boolean", "default": True}}, "required": []}
    async def __call__(self, deps: ToolDependencies, **kwargs: Any) -> dict[str, Any]:
        mod = _load_local_play_emotion()
        moves = list(mod.list_moves())
        moves_set = set(moves)
        display = getattr(mod, "display_name_for_move", lambda x: x)
        preferred = ["dance1", "dance2", "dance3", "success1", "welcoming2", "calming1", "electric1", "thoughtful1", "amazed1", "laughing2", "yes1", "no1", "sleep1"]
        items = []
        for mid in preferred:
            if mid in moves_set:
                items.append({"nombre_es": display(mid), "technical_id": mid, "ejemplo": f"haz {display(mid)}", "available": True})
        for mid in moves:
            if mid not in preferred and len(items) < 80:
                items.append({"nombre_es": display(mid), "technical_id": mid, "ejemplo": f"haz {display(mid)}", "available": True})
        return {"ok": True, "count": len(moves), "items": items, "bailes_principales": [x for x in items if x["technical_id"] in {"dance1", "dance2", "dance3"}], "nombres_recomendados": ["baile uno", "baile dos", "baile tres", "saludo", "celebración", "calma", "eléctrico"], "message_for_user": "Bailes principales disponibles: baile uno, baile dos y baile tres. También puedo hacer saludo, celebración, calma y eléctrico."}
