"""Explore/describe an image using local Ollama vision when available.

Use this when the user asks to explore an image, look at the webcam/photo, or describe what is visible.
It can capture a webcam photo with camera_pc and then send it to an Ollama vision model.
"""

from __future__ import annotations

import asyncio
import base64
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from reachy_mini_conversation_app.tools.core_tools import Tool, ToolDependencies

try:
    from ahootsa_logging import log_event, runtime_log_path
except Exception:
    def log_event(*a, **k): pass
    def runtime_log_path() -> Path:
        root = Path(os.getenv("AHOOTSA_LOG_DIR", r"D:\RITXI\logs"))
        root.mkdir(parents=True, exist_ok=True)
        sid = os.getenv("AHOOTSA_SESSION_ID", "manual")
        return root / f"ahootsa5_{sid}_runtime.log"


DEFAULT_OLLAMA_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_VISION_MODEL = "llava:latest"


def _base_url() -> str:
    return os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL).rstrip("/")


def _vision_model(model: str | None = None) -> str:
    return (model or os.getenv("OLLAMA_VISION_MODEL", DEFAULT_VISION_MODEL)).strip() or DEFAULT_VISION_MODEL


def _read_image_b64(path: Path) -> str:
    data = path.read_bytes()
    return base64.b64encode(data).decode("ascii")


def _call_ollama_vision(image_path: Path, question: str, model: str | None = None) -> dict[str, Any]:
    prompt = (question or "").strip() or (
        "Describe la imagen en castellano claro y sencillo. "
        "Usa frases cortas. Si hay una persona, describe solo lo visible sin identificarla."
    )
    model_name = _vision_model(model)
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "images": [_read_image_b64(image_path)],
        "options": {
            "temperature": 0.2,
            "num_predict": 160,
        },
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"{_base_url()}/api/generate",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=float(os.getenv("AHOOTSA_IMAGE_TIMEOUT_SECONDS", "60"))) as resp:
        out = json.loads(resp.read().decode("utf-8"))
    answer = str(out.get("response", "")).strip()
    return {
        "ok": True,
        "reply": answer,
        "message_for_user": answer or "He mirado la imagen, pero no he obtenido una descripción clara.",
        "image_path": str(image_path),
        "model": out.get("model", model_name),
        "base_url": _base_url(),
    }


def _capture_pc(camera_index: int = 0) -> dict[str, Any]:
    # Reuse sibling camera_pc without registering another Tool.
    try:
        import importlib.util
        import sys
        path = Path(__file__).resolve().with_name("camera_pc.py")
        name = "ahootsa_camera_pc_for_explore"
        if name in sys.modules:
            mod = sys.modules[name]
        else:
            spec = importlib.util.spec_from_file_location(name, path)
            if not spec or not spec.loader:
                raise RuntimeError("No puedo cargar camera_pc.py")
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            spec.loader.exec_module(mod)
        return mod._capture_with_cv2(int(camera_index), 5)
    except Exception as exc:
        return {
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "message_for_user": "No he podido hacer una foto con la cámara del ordenador.",
        }


class ExploreImage(Tool):
    name = "explore_image"
    description = (
        "Explora o describe una imagen en castellano. "
        "Puede usar una imagen ya guardada o hacer una foto con la webcam del ordenador. "
        "Úsala cuando el usuario diga: explorar imagen, mira la foto, qué ves, describe la imagen o usa la cámara. "
        "Requiere un modelo vision en Ollama, por defecto llava:latest, si se quiere descripción automática."
    )
    needs_response = True

    parameters_schema = {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "Qué debe observar o describir de la imagen.",
                "default": "Describe la imagen en castellano claro y sencillo.",
            },
            "image_path": {
                "type": "string",
                "description": "Ruta local de una imagen ya guardada. Si se omite, puede capturar con la webcam.",
                "default": "",
            },
            "capture_from_pc": {
                "type": "boolean",
                "description": "Si true, hace una foto con la webcam del ordenador antes de analizar.",
                "default": True,
            },
            "camera_index": {
                "type": "integer",
                "description": "Índice de webcam del PC.",
                "default": 0,
            },
            "model": {
                "type": "string",
                "description": "Modelo vision de Ollama. Por defecto OLLAMA_VISION_MODEL o llava:latest.",
                "default": "",
            },
        },
        "required": [],
    }

    async def __call__(
        self,
        deps: ToolDependencies,
        question: str = "Describe la imagen en castellano claro y sencillo.",
        image_path: str = "",
        capture_from_pc: bool = True,
        camera_index: int = 0,
        model: str = "",
        **_: Any,
    ) -> dict[str, Any]:
        log_event("explore_image.start", image_path=image_path, capture_from_pc=capture_from_pc, camera_index=camera_index)
        try:
            path = Path(str(image_path).strip()) if str(image_path).strip() else None
            capture_result: dict[str, Any] | None = None

            if (not path or not path.exists()) and capture_from_pc:
                capture_result = await asyncio.to_thread(_capture_pc, int(camera_index))
                if not capture_result.get("ok"):
                    log_event("explore_image.capture_error", result=capture_result)
                    return capture_result
                path = Path(str(capture_result.get("image_path", "")))

            if not path or not path.exists():
                msg = "No tengo una imagen válida para explorar. Puedo intentar hacer una foto con la webcam del ordenador."
                return {"ok": False, "error": "image_missing", "message_for_user": msg}

            result = await asyncio.to_thread(_call_ollama_vision, path, question, model or None)
            if capture_result:
                result["capture_result"] = {k: v for k, v in capture_result.items() if k != "image_base64"}
            log_event("explore_image.success", image_path=str(path), model=result.get("model"), reply_preview=str(result.get("reply", ""))[:200])
            return result

        except urllib.error.HTTPError as exc:
            msg = (
                f"Ollama ha respondido con error HTTP {exc.code}. "
                "Comprueba que el modelo de visión exista, por ejemplo llava:latest."
            )
            log_event("explore_image.http_error", error=str(exc))
            return {"ok": False, "error": f"HTTPError: {exc}", "message_for_user": msg}

        except urllib.error.URLError as exc:
            msg = (
                f"No puedo conectar con Ollama en {_base_url()}. "
                "Abre Ollama y comprueba el modelo de visión."
            )
            log_event("explore_image.url_error", error=str(exc))
            return {"ok": False, "error": f"URLError: {exc}", "message_for_user": msg}

        except Exception as exc:
            msg = f"No he podido explorar la imagen: {type(exc).__name__}: {exc}"
            log_event("explore_image.exception", error=msg)
            return {"ok": False, "error": msg, "message_for_user": msg, "log_file": str(runtime_log_path())}
