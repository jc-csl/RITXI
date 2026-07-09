"""camera_pc tool for Ahootsa.

Additional fallback tool for SIM / mockup-sim mode:
- official `camera` remains available for the real robot camera;
- `camera_pc` uses the computer webcam through OpenCV when the robot is simulated.
"""

from __future__ import annotations

import os
import json
import time
import datetime
from pathlib import Path
from typing import Any

from reachy_mini_conversation_app.tools.core_tools import Tool, ToolDependencies


def _base_dir() -> Path:
    base = os.getenv("LOCALAPPDATA") or os.getenv("TEMP") or "."
    d = Path(base) / "Reachy Mini Control" / "ahootsa_captures"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _log_dir() -> Path:
    base = os.getenv("LOCALAPPDATA") or os.getenv("TEMP") or "."
    d = Path(base) / "Reachy Mini Control" / "ahootsa_logs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _log_event(event: str, data: dict[str, Any] | None = None) -> None:
    payload = {
        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
        "event": event,
        "data": data or {},
    }
    try:
        with (_log_dir() / "camera_pc.log").open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass


def _capture_with_cv2(camera_index: int, warmup_frames: int) -> dict[str, Any]:
    try:
        import cv2  # type: ignore
    except Exception as exc:
        return {
            "ok": False,
            "error": f"opencv-python no está instalado o no se puede importar: {type(exc).__name__}: {exc}",
            "message_for_user": (
                "No puedo usar la cámara del ordenador porque falta OpenCV. "
                "Ejecuta INSTALAR_CAMARA_PC.ps1 y vuelve a probar."
            ),
        }

    backends = []
    if os.name == "nt" and hasattr(cv2, "CAP_DSHOW"):
        backends.append(cv2.CAP_DSHOW)
    backends.append(0)

    last_error = ""
    cap = None

    for backend in backends:
        try:
            if backend == 0:
                cap = cv2.VideoCapture(camera_index)
            else:
                cap = cv2.VideoCapture(camera_index, backend)

            if cap is None or not cap.isOpened():
                last_error = f"No se pudo abrir cámara índice {camera_index} con backend {backend}."
                try:
                    if cap is not None:
                        cap.release()
                except Exception:
                    pass
                continue

            try:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            except Exception:
                pass

            frame = None
            for _ in range(max(1, warmup_frames)):
                ok, frame = cap.read()
                if ok and frame is not None:
                    time.sleep(0.05)

            ok, frame = cap.read()
            if not ok or frame is None:
                last_error = "La cámara se abrió, pero no devolvió imagen."
                cap.release()
                continue

            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            out = _base_dir() / f"camera_pc_{ts}.jpg"
            written = cv2.imwrite(str(out), frame)
            cap.release()

            if not written:
                return {
                    "ok": False,
                    "error": f"No se pudo guardar la imagen en {out}",
                    "message_for_user": "He podido acceder a la cámara, pero no he podido guardar la foto.",
                }

            return {
                "ok": True,
                "image_path": str(out),
                "capture_dir": str(_base_dir()),
                "message_for_user": "He hecho una foto con la cámara del ordenador.",
            }

        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            try:
                if cap is not None:
                    cap.release()
            except Exception:
                pass

    return {
        "ok": False,
        "error": last_error or "No se pudo abrir la cámara del ordenador.",
        "message_for_user": (
            "No puedo acceder a la cámara del ordenador. "
            "Comprueba permisos de cámara de Windows y que otra aplicación no la esté usando."
        ),
    }


class CameraPcTool(Tool):
    """Capture an image from the computer webcam in SIM mode."""

    name = "camera_pc"
    description = (
        "Hace una foto usando la webcam del ordenador. "
        "Úsala en modo simulación/SIM o mockup-sim cuando el usuario pida cámara/foto "
        "y la cámara real de Reachy Mini no esté disponible. "
        "No sustituye a la herramienta oficial camera cuando hay robot real."
    )

    parameters_schema = {
        "type": "object",
        "properties": {
            "camera_index": {
                "type": "integer",
                "description": "Índice de cámara del ordenador. Normalmente 0.",
                "default": 0,
            },
            "warmup_frames": {
                "type": "integer",
                "description": "Fotogramas de calentamiento antes de guardar la foto.",
                "default": 5,
            },
        },
        "required": [],
    }

    async def __call__(
        self,
        deps: ToolDependencies,
        camera_index: int = 0,
        warmup_frames: int = 5,
        **_: Any,
    ) -> dict[str, Any]:
        _log_event("call_start", {"camera_index": camera_index, "warmup_frames": warmup_frames})
        result = _capture_with_cv2(int(camera_index), int(warmup_frames))
        _log_event("call_result", result)
        return result
