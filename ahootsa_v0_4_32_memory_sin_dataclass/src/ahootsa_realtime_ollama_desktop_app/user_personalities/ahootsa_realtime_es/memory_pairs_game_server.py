"""Robust generic JSON memory-pairs game engine for Ahootsa.

v0.4.32:
- Removes dataclass dependency to avoid importlib/dataclasses crash:
  AttributeError: 'NoneType' object has no attribute '__dict__'
- Guarantees start_server().
- Memory visual style: blue card backs with large white numbers.
- 4 pairs / 8 cards.
- Incorrect pairs remain face-up for 3 seconds and then turn back.
- Hint support with hint_memory_pairs_game.

This module is profile-local and does not modify the official Reachy Mini app.
"""

from __future__ import annotations

import json
import os
import random
import threading
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

DEFAULT_PORT = int(os.getenv("AHOOTSA_MEMORY_GAME_PORT", "7870"))
DEFAULT_GAME_ID = os.getenv("AHOOTSA_MEMORY_GAME_DEFAULT", "animales").strip() or "animales"
REVEAL_SECONDS = float(os.getenv("AHOOTSA_MEMORY_REVEAL_SECONDS", "3"))
EMBEDDED_HTML = '<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>Ahootsa — Memory</title>\n<style>\n:root{\n  --table:#eef2f7;\n  --card-back:#1763c8;\n  --card-back-dark:#0f4d9f;\n  --card-back-border:#0c3f82;\n  --ink:#203048;\n  --white:#ffffff;\n  --shadow:0 18px 38px rgba(25,45,80,.18);\n  --matched:#fff7c9;\n  --matched-border:#f0c63c;\n}\n*{box-sizing:border-box}\nhtml,body{width:100%;height:100%}\nbody{\n  margin:0;\n  background:var(--table);\n  font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;\n  overflow:hidden;\n}\n.screen{\n  width:100vw;\n  height:100vh;\n  padding:clamp(14px,2.5vw,30px);\n  display:grid;\n  place-items:center;\n}\n.board{\n  width:min(96vw,1120px);\n  height:min(94vh,760px);\n  display:grid;\n  grid-template-columns:repeat(4,1fr);\n  grid-template-rows:repeat(2,1fr);\n  gap:clamp(14px,2.4vw,26px);\n}\n.card{\n  position:relative;\n  width:100%;\n  height:100%;\n  border:0;\n  padding:0;\n  background:transparent;\n  perspective:1200px;\n  cursor:pointer;\n}\n.card:disabled{cursor:default}\n.inner{\n  position:relative;\n  width:100%;\n  height:100%;\n  transform-style:preserve-3d;\n  transition:transform .52s ease;\n}\n.card.visible .inner,\n.card.matched .inner{transform:rotateY(180deg)}\n.face{\n  position:absolute;\n  inset:0;\n  border-radius:22px;\n  backface-visibility:hidden;\n  overflow:hidden;\n  box-shadow:var(--shadow);\n}\n.back{\n  display:grid;\n  place-items:center;\n  background:linear-gradient(180deg,var(--card-back),var(--card-back-dark));\n  border:8px solid var(--card-back-border);\n}\n.back::before{\n  content:\'\';\n  position:absolute;\n  inset:10px;\n  border-radius:14px;\n  background:linear-gradient(180deg,rgba(255,255,255,.12),rgba(255,255,255,.04));\n  border:4px solid rgba(255,255,255,.92);\n}\n.num{\n  position:relative;\n  z-index:1;\n  font-weight:1000;\n  color:var(--white);\n  font-size:clamp(6rem,15vw,12rem);\n  line-height:.9;\n  letter-spacing:-.08em;\n  text-shadow:0 8px 24px rgba(0,0,0,.24);\n}\n.front{\n  transform:rotateY(180deg);\n  background:linear-gradient(180deg,var(--front,#ffe5b8),var(--front2,#ffd18a));\n  border:8px solid rgba(255,255,255,.96);\n  display:flex;\n  align-items:center;\n  justify-content:center;\n  padding:14px;\n}\n.front::before{\n  content:\'\';\n  position:absolute;\n  inset:10px;\n  border-radius:14px;\n  border:3px solid rgba(255,255,255,.55);\n  pointer-events:none;\n}\n.card.matched .front{\n  background:linear-gradient(180deg,var(--matched),#ffe58f);\n  border-color:var(--matched-border);\n}\n.content{\n  position:relative;\n  z-index:1;\n  width:100%;\n  height:100%;\n  display:flex;\n  flex-direction:column;\n  justify-content:center;\n  align-items:center;\n  gap:10px;\n  text-align:center;\n}\n.icon{\n  font-size:clamp(4.8rem,10.8vw,8.2rem);\n  line-height:1;\n  filter:drop-shadow(0 3px 3px rgba(0,0,0,.10));\n}\n.label{\n  font-size:clamp(1.55rem,3.9vw,2.6rem);\n  line-height:1;\n  font-weight:1000;\n  color:var(--ink);\n  text-transform:capitalize;\n}\n.kind{\n  font-size:clamp(.85rem,1.6vw,1.1rem);\n  line-height:1.1;\n  font-weight:900;\n  color:rgba(32,48,72,.68);\n  text-transform:uppercase;\n  letter-spacing:.12em;\n}\n.card.temporary .front{\n  animation:shake .32s linear 2;\n  outline:6px solid rgba(84,167,255,.92);\n  outline-offset:-12px;\n}\n.card.matched .icon{animation:bounce .85s ease 2}\n.burst{\n  position:fixed;\n  inset:0;\n  display:none;\n  place-items:center;\n  pointer-events:none;\n  font-size:clamp(5.4rem,15vw,12rem);\n  z-index:10;\n}\n.burst.show{display:grid;animation:pop .95s ease both}\n@keyframes bounce{\n  0%,100%{transform:translateY(0) scale(1)}\n  30%{transform:translateY(-12px) scale(1.05)}\n  60%{transform:translateY(0) scale(.98)}\n}\n@keyframes shake{\n  0%,100%{transform:translateX(0)}\n  20%{transform:translateX(-6px)}\n  40%{transform:translateX(6px)}\n  60%{transform:translateX(-5px)}\n  80%{transform:translateX(5px)}\n}\n@keyframes pop{\n  0%{opacity:0;transform:scale(.38) rotate(-8deg)}\n  35%{opacity:1;transform:scale(1.08) rotate(4deg)}\n  100%{opacity:0;transform:scale(.9) rotate(0)}\n}\n@media(max-width:900px){\n  .board{height:min(94vh,900px);grid-template-columns:repeat(2,1fr);grid-template-rows:repeat(4,1fr)}\n  .num{font-size:clamp(5rem,24vw,9.2rem)}\n  .icon{font-size:clamp(4rem,18vw,7rem)}\n  .label{font-size:clamp(1.4rem,6vw,2.2rem)}\n}\n</style>\n</head>\n<body>\n<div class="screen">\n  <main id="board" class="board" aria-label="cartas de memory"></main>\n</div>\n<div id="burst" class="burst">🎉</div>\n<script>\nconst board = document.getElementById(\'board\');\nconst burst = document.getElementById(\'burst\');\nlet selected = [];\nlet lastMoveId = null;\nconst palette = [\n  [\'#ffd7a7\',\'#ffbf8d\'],\n  [\'#cdecc7\',\'#b7e0ad\'],\n  [\'#ffd1dd\',\'#ffbfd2\'],\n  [\'#d8dcff\',\'#c9cdfa\'],\n  [\'#ffe7a6\',\'#ffd882\'],\n  [\'#d4f3ef\',\'#bce9e0\'],\n  [\'#f6d2ff\',\'#eabcf5\'],\n  [\'#ffe0c9\',\'#ffd2b3\']\n];\nfunction faceColors(card){\n  const idx = ((card.number || 1) - 1) % palette.length;\n  const pair = palette[idx];\n  return \'--front:\' + pair[0] + \';--front2:\' + pair[1] + \';\';\n}\nasync function api(path){\n  const r = await fetch(path,{cache:\'no-store\'});\n  if(!r.ok) throw new Error(await r.text());\n  return await r.json();\n}\nfunction showBurst(text){\n  burst.textContent = text || \'🎉\';\n  burst.classList.remove(\'show\');\n  void burst.offsetWidth;\n  burst.classList.add(\'show\');\n  setTimeout(()=>burst.classList.remove(\'show\'),950);\n}\nfunction escapeHtml(value){\n  return String(value || \'\').replace(/[&<>"\']/g, function(c){\n    return {\'&\':\'&amp;\',\'<\':\'&lt;\',\'>\':\'&gt;\',\'"\':\'&quot;\',"\'":\'&#39;\'}[c];\n  });\n}\nfunction cardHtml(card){\n  const visible = card.visible || card.matched;\n  const cls = [\'card\'];\n  if(visible) cls.push(\'visible\');\n  if(card.matched) cls.push(\'matched\');\n  if(card.temporary) cls.push(\'temporary\');\n  const icon = visible ? escapeHtml(card.icon) : \'\';\n  const label = visible ? escapeHtml(card.label) : \'\';\n  const kind = visible ? escapeHtml(card.kind_label) : \'\';\n  return `\n    <button class="${cls.join(\' \')}" data-number="${card.number}" ${card.matched?\'disabled\':\'\'} aria-label="carta ${card.number}">\n      <div class="inner">\n        <div class="face back"><div class="num">${card.number}</div></div>\n        <div class="face front" style="${faceColors(card)}">\n          <div class="content">\n            <div class="icon">${icon}</div>\n            <div class="label">${label}</div>\n            <div class="kind">${kind}</div>\n          </div>\n        </div>\n      </div>\n    </button>`;\n}\nfunction render(state){\n  board.innerHTML = state.cards.map(cardHtml).join(\'\');\n  for(const btn of board.querySelectorAll(\'button.card\')){\n    btn.addEventListener(\'click\',()=>selectCard(Number(btn.dataset.number)));\n  }\n  if(state.last_move_id !== lastMoveId){\n    lastMoveId = state.last_move_id;\n    if(state.last_result === \'match\') showBurst(state.last_animation || \'🎉\');\n    if(state.finished) showBurst(\'🏆\');\n  }\n}\nasync function refresh(){\n  try{ render(await api(\'/state\')); }\n  catch(e){\n    board.innerHTML = \'<div style="font-weight:800;color:#203048;font-size:2rem">No se pudo cargar el juego.</div>\';\n  }\n}\nasync function selectCard(n){\n  const state = await api(\'/state\');\n  const card = state.cards.find(c=>c.number===n);\n  if(!card || card.matched) return;\n  selected.push(n);\n  if(selected.length===2){\n    const a = selected[0];\n    const b = selected[1];\n    selected=[];\n    await api(\'/choose?first=\' + encodeURIComponent(a) + \'&second=\' + encodeURIComponent(b));\n    await refresh();\n  }\n}\nrefresh();\nsetInterval(refresh,450);\n</script>\n</body>\n</html>\n'
EMBEDDED_GAMES: dict[str, dict[str, Any]] = {'animales': {'id': 'animales', 'title': 'Memory de animales', 'subtitle': 'Busca parejas: animal + grupo.', 'theme': 'Animales', 'left_title': 'animal', 'right_title': 'grupo', 'start_message': 'Vamos a jugar. Di dos números.', 'finish_title': '¡Memory de animales terminado!', 'facts_title': 'Pistas de animales', 'pairs': [{'id': 'frog', 'left': 'rana', 'left_icon': '🐸', 'right': 'anfibio', 'right_icon': '💧', 'hint': 'La rana vive entre agua y tierra.', 'fact': 'Los anfibios suelen vivir una parte de su vida en el agua y otra en tierra.'}, {'id': 'eagle', 'left': 'águila', 'left_icon': '🦅', 'right': 'ave', 'right_icon': '🪶', 'hint': 'El águila tiene plumas.', 'fact': 'Las aves tienen plumas y muchas pueden volar.'}, {'id': 'salmon', 'left': 'salmón', 'left_icon': '🐟', 'right': 'pez', 'right_icon': '🌊', 'hint': 'El salmón vive en el agua.', 'fact': 'Los peces viven en el agua y respiran con branquias.'}, {'id': 'dolphin', 'left': 'delfín', 'left_icon': '🐬', 'right': 'mamífero', 'right_icon': '🍼', 'hint': 'El delfín respira aire.', 'fact': 'Los mamíferos respiran aire y sus crías toman leche.'}]}, 'ciudades': {'id': 'ciudades', 'title': 'Memory de ciudades', 'subtitle': 'Busca parejas: ciudad europea + monumento.', 'theme': 'Ciudades', 'left_title': 'ciudad', 'right_title': 'monumento', 'start_message': 'Vamos a viajar por Europa. Di dos números.', 'finish_title': '¡Viaje por Europa completado!', 'facts_title': 'Pistas de monumentos', 'pairs': [{'id': 'paris', 'left': 'París', 'left_icon': '🇫🇷', 'right': 'Torre Eiffel', 'right_icon': '🗼', 'hint': 'En París hay una torre de hierro muy famosa.', 'fact': 'La Torre Eiffel es uno de los símbolos más conocidos de París.'}, {'id': 'rome', 'left': 'Roma', 'left_icon': '🇮🇹', 'right': 'Coliseo', 'right_icon': '🏛️', 'hint': 'En Roma hay un anfiteatro antiguo muy famoso.', 'fact': 'El Coliseo fue un gran anfiteatro de la antigua Roma.'}, {'id': 'london', 'left': 'Londres', 'left_icon': '🇬🇧', 'right': 'Big Ben', 'right_icon': '🕰️', 'hint': 'En Londres hay un reloj muy conocido.', 'fact': 'Big Ben es el nombre popular de la gran campana del reloj del Parlamento británico.'}, {'id': 'prague', 'left': 'Praga', 'left_icon': '🇨🇿', 'right': 'Puente de Carlos', 'right_icon': '🌉', 'hint': 'En Praga hay un puente histórico sobre el río Moldava.', 'fact': 'El Puente de Carlos es uno de los lugares más visitados de Praga.'}]}, 'alimentos': {'id': 'alimentos', 'title': 'Memory de alimentos', 'subtitle': 'Busca parejas: alimento + grupo alimentario.', 'theme': 'Alimentos', 'left_title': 'alimento', 'right_title': 'grupo', 'start_message': 'Vamos a jugar con alimentos. Di dos números.', 'finish_title': '¡Menú completado!', 'facts_title': 'Pistas de alimentos', 'pairs': [{'id': 'apple', 'left': 'manzana', 'left_icon': '🍎', 'right': 'fruta', 'right_icon': '🌳', 'hint': 'La manzana suele crecer en un árbol.', 'fact': 'Las frutas aportan vitaminas, agua y fibra.'}, {'id': 'carrot', 'left': 'zanahoria', 'left_icon': '🥕', 'right': 'hortaliza', 'right_icon': '🥗', 'hint': 'La zanahoria suele estar en ensaladas y guisos.', 'fact': 'Las hortalizas ayudan a hacer comidas variadas y coloridas.'}, {'id': 'bread', 'left': 'pan', 'left_icon': '🍞', 'right': 'cereal', 'right_icon': '🌾', 'hint': 'El pan se hace con harina de cereales.', 'fact': 'Los cereales aportan energía, sobre todo si son integrales.'}, {'id': 'lentils', 'left': 'lentejas', 'left_icon': '🫘', 'right': 'legumbre', 'right_icon': '🌱', 'hint': 'Las lentejas son semillas que se comen en plato de cuchara.', 'fact': 'Las legumbres aportan fibra y proteína vegetal.'}]}}


def _now() -> float:
    return time.time()


def _candidate_dirs() -> list[Path]:
    here = Path(__file__).resolve().parent
    dirs = [here, here / "games"]
    try:
        dirs.append(Path(__file__).resolve().parents[2] / "games")
        dirs.append(Path(__file__).resolve().parents[1] / "games")
    except Exception:
        pass
    return dirs


def _load_html() -> str:
    for base in _candidate_dirs():
        for name in ("memory_pairs_generic.html", "memory_pairs_animales.html"):
            path = base / name
            try:
                if path.exists():
                    text = path.read_text(encoding="utf-8")
                    if "cartas de memory" in text or "Ahootsa" in text:
                        return text
            except Exception:
                pass
    return EMBEDDED_HTML


def _load_games() -> dict[str, dict[str, Any]]:
    loaded = dict(EMBEDDED_GAMES)
    for base in _candidate_dirs():
        try:
            if not base.exists():
                continue
            for path in sorted(base.glob("*.json")):
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    gid = str(data.get("id") or path.stem).strip()
                    if gid and isinstance(data.get("pairs"), list):
                        data["id"] = gid
                        data["pairs"] = list(data["pairs"])[:4]
                        loaded[gid] = data
                except Exception:
                    pass
        except Exception:
            pass
    return loaded


def _safe_game_id(game_id: object | None) -> str:
    requested = str(game_id or DEFAULT_GAME_ID).strip().lower()
    games = _load_games()
    if requested in games:
        return requested
    aliases = {
        "animals": "animales", "animal": "animales",
        "ciudad": "ciudades", "cities": "ciudades", "monumentos": "ciudades",
        "food": "alimentos", "foods": "alimentos", "comida": "alimentos", "alimento": "alimentos",
    }
    if aliases.get(requested) in games:
        return aliases[requested]
    return "animales" if "animales" in games else sorted(games)[0]


class MemoryPairsGame:
    def __init__(self, game_id: str = DEFAULT_GAME_ID) -> None:
        self.game_id = game_id
        self.game_data: dict[str, Any] = {}
        self.cards: list[dict[str, Any]] = []
        self.matched_numbers: set[int] = set()
        self.revealed_numbers: set[int] = set()
        self.reveal_until: float = 0.0
        self.found_pair_ids: list[str] = []
        self.moves: int = 0
        self.start_time: float = _now()
        self.finished_at: float | None = None
        self.message: str = "Di dos números."
        self.last_result: str = "ready"
        self.last_move_id: int = 0
        self.last_animation: str = "🎉"
        self.last_hint_pair_id: str | None = None
        self.lock = threading.RLock()

    def reset(self, game_id: object | None = None) -> dict[str, Any]:
        with self.lock:
            self.game_id = _safe_game_id(game_id or self.game_id)
            self.game_data = _load_games()[self.game_id]
            pairs = list(self.game_data.get("pairs", []))[:4]

            raw: list[dict[str, Any]] = []
            for pair in pairs:
                pid = str(pair["id"])
                raw.append({
                    "pair_id": pid,
                    "kind": "left",
                    "kind_label": self.game_data.get("left_title", "elemento"),
                    "label": pair["left"],
                    "icon": pair["left_icon"],
                    "left": pair["left"],
                    "left_icon": pair["left_icon"],
                    "right": pair["right"],
                    "right_icon": pair["right_icon"],
                })
                raw.append({
                    "pair_id": pid,
                    "kind": "right",
                    "kind_label": self.game_data.get("right_title", "pareja"),
                    "label": pair["right"],
                    "icon": pair["right_icon"],
                    "left": pair["left"],
                    "left_icon": pair["left_icon"],
                    "right": pair["right"],
                    "right_icon": pair["right_icon"],
                })
            random.shuffle(raw)
            self.cards = []
            for i, card in enumerate(raw, start=1):
                c = dict(card)
                c["number"] = i
                self.cards.append(c)

            self.matched_numbers = set()
            self.revealed_numbers = set()
            self.reveal_until = 0.0
            self.found_pair_ids = []
            self.moves = 0
            self.start_time = _now()
            self.finished_at = None
            self.message = self.game_data.get("start_message", "Elige dos cartas. Di dos números.")
            self.last_result = "ready"
            self.last_move_id += 1
            self.last_animation = "🤖"
            self.last_hint_pair_id = None
            return self.public_state()

    def select_game(self, game_id: object) -> dict[str, Any]:
        return self.reset(game_id)

    def elapsed_seconds(self) -> int:
        end = self.finished_at if self.finished_at is not None else _now()
        return int(max(0, end - self.start_time))

    def _card_by_number(self, n: int) -> dict[str, Any] | None:
        for card in self.cards:
            if card["number"] == n:
                return card
        return None

    def _cleanup_revealed_if_needed(self) -> None:
        if self.revealed_numbers and self.reveal_until and _now() >= self.reveal_until:
            self.revealed_numbers = set()
            self.reveal_until = 0.0
            if self.last_result == "miss":
                self.message = "Las cartas se han girado. Di otros dos números."

    def choose(self, first: int, second: int) -> dict[str, Any]:
        with self.lock:
            if not self.cards:
                self.reset(self.game_id)

            self._cleanup_revealed_if_needed()
            self.last_move_id += 1

            if self.finished_at is not None:
                self.message = "El juego ya ha terminado. Puedes jugar otra vez."
                self.last_result = "finished"
                return {"ok": False, "result": "finished", "message_for_user": self.message, "state": self.public_state()}

            if first == second:
                self.message = "Elige dos cartas diferentes."
                self.last_result = "invalid"
                return {"ok": False, "result": "invalid", "message_for_user": self.message, "state": self.public_state()}

            c1 = self._card_by_number(int(first))
            c2 = self._card_by_number(int(second))
            if not c1 or not c2:
                self.message = f"Esos números no existen. Usa números del 1 al {len(self.cards)}."
                self.last_result = "invalid"
                return {"ok": False, "result": "invalid", "message_for_user": self.message, "state": self.public_state()}

            if c1["number"] in self.matched_numbers or c2["number"] in self.matched_numbers:
                self.message = "Una carta ya está emparejada. Prueba con otras."
                self.last_result = "invalid"
                return {"ok": False, "result": "invalid", "message_for_user": self.message, "state": self.public_state()}

            self.moves += 1
            self.revealed_numbers = {c1["number"], c2["number"]}
            self.reveal_until = _now() + REVEAL_SECONDS

            is_match = c1["pair_id"] == c2["pair_id"] and c1["kind"] != c2["kind"]
            pair = next(p for p in self.game_data["pairs"] if str(p["id"]) == c1["pair_id"])

            if is_match:
                self.matched_numbers.update({c1["number"], c2["number"]})
                self.revealed_numbers = set()
                self.reveal_until = 0.0
                if str(pair["id"]) not in self.found_pair_ids:
                    self.found_pair_ids.append(str(pair["id"]))
                self.last_result = "match"
                self.last_animation = f"{pair['left_icon']}🎉"
                self.message = f"¡Muy bien! {pair['left']} va con {pair['right']}."
                result = "match"

                if len(self.found_pair_ids) == len(self.game_data["pairs"]):
                    self.finished_at = _now()
                    self.last_result = "final"
                    self.last_animation = "🏆"
                    self.message = f"¡Juego terminado! Todas las parejas en {self.moves} movimientos."
                    result = "final"

                return {
                    "ok": True, "result": result, "matched": True,
                    "left": pair["left"], "right": pair["right"],
                    "message_for_user": self.message,
                    "robot_say": self.message + (" Fin del juego. ¡Lo has conseguido!" if result == "final" else " Dime otros dos números."),
                    "state": self.public_state(),
                }

            self.last_result = "miss"
            self.last_animation = "💪"
            self.message = f"Casi. {c1['label']} y {c2['label']} no son pareja. Míralas tres segundos."
            return {
                "ok": True, "result": "miss", "matched": False,
                "first_label": c1["label"], "second_label": c2["label"],
                "message_for_user": self.message,
                "robot_say": self.message + " Luego probamos otra vez.",
                "state": self.public_state(),
            }

    def hint(self) -> dict[str, Any]:
        with self.lock:
            if self.finished_at is not None:
                msg = "Ya has terminado el juego. ¡Muy bien!"
                return {"ok": True, "message_for_user": msg, "hint": msg, "state": self.public_state()}

            remaining = [p for p in self.game_data["pairs"] if str(p["id"]) not in self.found_pair_ids]
            if not remaining:
                msg = "No quedan pistas. Ya casi está."
                return {"ok": True, "message_for_user": msg, "hint": msg, "state": self.public_state()}

            choices = [p for p in remaining if str(p["id"]) != self.last_hint_pair_id] or remaining
            pair = random.choice(choices)
            self.last_hint_pair_id = str(pair["id"])
            msg = pair.get("hint") or f"Busca la pareja de {pair['left']}."
            self.message = msg
            self.last_result = "hint"
            self.last_animation = "💡"
            self.last_move_id += 1
            return {
                "ok": True,
                "result": "hint",
                "hint": msg,
                "message_for_user": msg,
                "robot_say": msg + " Mira las cartas con calma y dime dos números.",
                "state": self.public_state(),
            }

    def public_state(self) -> dict[str, Any]:
        with self.lock:
            self._cleanup_revealed_if_needed()
            if not self.game_data:
                self.game_id = _safe_game_id(self.game_id)
                self.game_data = _load_games()[self.game_id]

            visible_numbers = self.matched_numbers | self.revealed_numbers
            cards = []
            for card in self.cards:
                n = card["number"]
                visible = n in visible_numbers
                matched = n in self.matched_numbers
                cards.append({
                    "number": n, "visible": visible, "matched": matched,
                    "temporary": (n in self.revealed_numbers and n not in self.matched_numbers),
                    "kind": card["kind"] if visible else "",
                    "kind_label": card["kind_label"] if visible else "",
                    "label": card["label"] if visible else "",
                    "icon": card["icon"] if visible else "",
                })

            found_pairs = []
            for pid in self.found_pair_ids:
                pair = next(p for p in self.game_data["pairs"] if str(p["id"]) == pid)
                found_pairs.append(pair)

            return {
                "game_id": self.game_id,
                "game_label": self.game_data.get("theme", self.game_id),
                "title": self.game_data.get("title", "Memory"),
                "subtitle": self.game_data.get("subtitle", "Di dos números."),
                "finish_title": self.game_data.get("finish_title", "¡Juego terminado!"),
                "cards": cards,
                "moves": self.moves,
                "matches": len(self.found_pair_ids),
                "total_pairs": len(self.game_data["pairs"]),
                "elapsed_seconds": self.elapsed_seconds(),
                "finished": self.finished_at is not None,
                "message": self.message,
                "last_result": self.last_result,
                "last_move_id": self.last_move_id,
                "last_animation": self.last_animation,
                "found_pairs": found_pairs,
                "reveal_seconds": REVEAL_SECONDS,
            }


_GAME = MemoryPairsGame()
_GAME.reset(DEFAULT_GAME_ID)
_SERVER: ThreadingHTTPServer | None = None
_SERVER_THREAD: threading.Thread | None = None
_SERVER_PORT: int | None = None


class _Handler(BaseHTTPRequestHandler):
    server_version = "AhootsaMemoryVisual/0.4.32"

    def _send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _send_html(self, html: str) -> None:
        raw = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, fmt: str, *args: Any) -> None:
        return

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        path = parsed.path.rstrip("/") or "/"

        if path == "/":
            self._send_html(_load_html())
            return
        if path == "/games":
            games = _load_games()
            self._send_json({"ok": True, "games": [
                {"id": gid, "title": data.get("title", gid), "theme": data.get("theme", gid)}
                for gid, data in sorted(games.items())
            ]})
            return
        if path == "/state":
            self._send_json(_GAME.public_state())
            return
        if path == "/select_game":
            game_id = (qs.get("game_id") or qs.get("id") or [""])[0]
            self._send_json({"ok": True, "state": _GAME.select_game(game_id)})
            return
        if path == "/reset":
            self._send_json({"ok": True, "message_for_user": "Juego reiniciado.", "state": _GAME.reset()})
            return
        if path == "/hint":
            self._send_json(_GAME.hint())
            return
        if path == "/choose":
            try:
                first = int((qs.get("first") or qs.get("a") or [""])[0])
                second = int((qs.get("second") or qs.get("b") or [""])[0])
            except Exception:
                self._send_json({"ok": False, "error": "first and second must be numbers"}, status=400)
                return
            self._send_json(_GAME.choose(first, second))
            return
        self._send_json({"ok": False, "error": "not found"}, status=404)


def available_games() -> list[dict[str, str]]:
    return [
        {"id": gid, "title": data.get("title", gid), "theme": data.get("theme", gid)}
        for gid, data in sorted(_load_games().items())
    ]


def start_server(port: int | None = None, open_browser: bool = True, reset: bool = False, game_id: object | None = None) -> dict[str, Any]:
    global _SERVER, _SERVER_THREAD, _SERVER_PORT
    selected = _safe_game_id(game_id or DEFAULT_GAME_ID)
    if reset or selected != _GAME.game_id:
        _GAME.reset(selected)

    if _SERVER is not None and _SERVER_THREAD is not None and _SERVER_THREAD.is_alive():
        url = f"http://localhost:{_SERVER_PORT}/"
        if open_browser:
            try:
                webbrowser.open(url)
            except Exception:
                pass
        return {"ok": True, "url": url, "port": _SERVER_PORT, "already_running": True, "games": available_games(), "state": _GAME.public_state()}

    desired = int(port or DEFAULT_PORT)
    last_error = ""
    for candidate in range(desired, desired + 20):
        try:
            server = ThreadingHTTPServer(("127.0.0.1", candidate), _Handler)
            thread = threading.Thread(target=server.serve_forever, name="AhootsaMemoryVisual", daemon=True)
            thread.start()
            _SERVER = server
            _SERVER_THREAD = thread
            _SERVER_PORT = candidate
            url = f"http://localhost:{candidate}/"
            if open_browser:
                try:
                    webbrowser.open(url)
                except Exception:
                    pass
            return {"ok": True, "url": url, "port": candidate, "already_running": False, "games": available_games(), "state": _GAME.public_state()}
        except OSError as exc:
            last_error = repr(exc)
    return {"ok": False, "error": last_error or "could not start server"}


def reset_game(game_id: object | None = None) -> dict[str, Any]:
    return {"ok": True, "state": _GAME.reset(game_id), "message_for_user": "He reiniciado el memory. Di dos números."}


def select_game(game_id: object) -> dict[str, Any]:
    return {"ok": True, "state": _GAME.select_game(game_id), "message_for_user": "He cambiado el memory. Di dos números."}


def choose_cards(first_card: int, second_card: int) -> dict[str, Any]:
    return _GAME.choose(int(first_card), int(second_card))


def hint() -> dict[str, Any]:
    return _GAME.hint()


def status() -> dict[str, Any]:
    url = f"http://localhost:{_SERVER_PORT}/" if _SERVER_PORT else None
    return {"ok": True, "url": url, "port": _SERVER_PORT, "running": bool(_SERVER_THREAD and _SERVER_THREAD.is_alive()), "games": available_games(), "state": _GAME.public_state()}


def _self_test() -> dict[str, Any]:
    return {
        "has_start_server": callable(start_server),
        "games": available_games(),
        "state_cards": len(_GAME.public_state().get("cards", [])),
    }
