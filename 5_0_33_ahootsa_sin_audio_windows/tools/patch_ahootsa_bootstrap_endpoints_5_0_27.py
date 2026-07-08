"""
Ahootsa 5.0.27 - parche robusto de endpoints de compatibilidad.

Corrige 404 repetidos en:
- GET /voices/current
- GET /status
- GET /mic
- GET /voices

Diferencia respecto a 5.0.26:
- No busca literalmente `app = FastAPI(...)`.
- Inserta un bootstrap al principio de `ahootsa_realtime_ollama_desktop_app/__init__.py`.
- Ese bootstrap registra endpoints cuando se cree cualquier instancia FastAPI/Starlette
  dentro del paquete, aunque la app se construya con factory, otro nombre de variable,
  router interno o import indirecto.
"""
from __future__ import annotations

import datetime as _dt
import importlib
import pathlib
import sys

PACKAGE_NAME = "ahootsa_realtime_ollama_desktop_app"
PATCH_MARKER = "Ahootsa 5.0.27 - bootstrap endpoints compatibilidad frontend"

BOOTSTRAP_CODE = r'''
# ============================================================
# Ahootsa 5.0.27 - bootstrap endpoints compatibilidad frontend
# Añadido para evitar 404 repetidos desde el frontend/Desktop:
#   GET /status
#   GET /mic
#   GET /voices/current
#   GET /voices
#
# Este bloque se inserta al comienzo de __init__.py para ejecutarse
# antes de que el paquete cree/import cualquier app FastAPI o Starlette.
# No depende de que exista literalmente `app = FastAPI(...)`.
# ============================================================

def _ahootsa_5027_register_compat_routes(_app):
    """Registra rutas de compatibilidad si el objeto parece ASGI Starlette/FastAPI."""
    try:
        _paths = {getattr(_route, "path", "") for _route in getattr(_app, "routes", [])}
    except Exception:
        _paths = set()

    try:
        from fastapi import Request as _FastAPIRequest
    except Exception:  # pragma: no cover
        _FastAPIRequest = None

    try:
        from starlette.responses import JSONResponse as _JSONResponse
    except Exception:
        _JSONResponse = None

    def _payload_status():
        return {
            "ok": True,
            "status": "running",
            "app": "Ahootsa",
            "version": "5.0.27",
            "backend": "mujoco_web_realtime",
            "compatibility": True,
        }

    def _payload_mic():
        return {
            "ok": True,
            "available": False,
            "enabled": False,
            "recording": False,
            "source": "compatibility_stub",
            "message": "Endpoint disponible para evitar 404. El micro real se gestiona desde navegador/frontend o modulo externo.",
        }

    def _payload_current_voice():
        return {
            "ok": True,
            "voice": {
                "id": "system",
                "name": "Voz del sistema",
                "language": "es-ES",
                "engine": "pyttsx3_or_browser",
            },
        }

    def _payload_voices():
        return {
            "ok": True,
            "voices": [
                {
                    "id": "system",
                    "name": "Voz del sistema",
                    "language": "es-ES",
                    "engine": "pyttsx3_or_browser",
                }
            ],
            "current": "system",
        }

    async def _status_fastapi():
        return _payload_status()

    async def _mic_fastapi():
        return _payload_mic()

    async def _current_voice_fastapi():
        return _payload_current_voice()

    async def _voices_fastapi():
        return _payload_voices()

    async def _status_starlette(request):
        return _JSONResponse(_payload_status())

    async def _mic_starlette(request):
        return _JSONResponse(_payload_mic())

    async def _current_voice_starlette(request):
        return _JSONResponse(_payload_current_voice())

    async def _voices_starlette(request):
        return _JSONResponse(_payload_voices())

    # FastAPI: preferimos add_api_route para que devuelva dicts normalmente.
    if hasattr(_app, "add_api_route"):
        try:
            if "/status" not in _paths:
                _app.add_api_route("/status", _status_fastapi, methods=["GET"], include_in_schema=False)
            if "/mic" not in _paths:
                _app.add_api_route("/mic", _mic_fastapi, methods=["GET"], include_in_schema=False)
            if "/voices/current" not in _paths:
                _app.add_api_route("/voices/current", _current_voice_fastapi, methods=["GET"], include_in_schema=False)
            if "/voices" not in _paths:
                _app.add_api_route("/voices", _voices_fastapi, methods=["GET"], include_in_schema=False)
            setattr(_app, "_ahootsa_5027_compat_routes", True)
            return
        except Exception:
            pass

    # Starlette puro: usamos add_route y JSONResponse.
    if hasattr(_app, "add_route") and _JSONResponse is not None:
        try:
            if "/status" not in _paths:
                _app.add_route("/status", _status_starlette, methods=["GET"])
            if "/mic" not in _paths:
                _app.add_route("/mic", _mic_starlette, methods=["GET"])
            if "/voices/current" not in _paths:
                _app.add_route("/voices/current", _current_voice_starlette, methods=["GET"])
            if "/voices" not in _paths:
                _app.add_route("/voices", _voices_starlette, methods=["GET"])
            setattr(_app, "_ahootsa_5027_compat_routes", True)
        except Exception:
            pass


def _ahootsa_5027_install_fastapi_starlette_hooks():
    """Instala hooks para registrar endpoints en apps creadas despues de este import."""
    try:
        from fastapi import FastAPI as _FastAPI
        if not getattr(_FastAPI, "_ahootsa_5027_hooked", False):
            _orig_fastapi_init = _FastAPI.__init__

            def _ahootsa_fastapi_init(self, *args, **kwargs):
                _orig_fastapi_init(self, *args, **kwargs)
                _ahootsa_5027_register_compat_routes(self)

            _FastAPI.__init__ = _ahootsa_fastapi_init
            setattr(_FastAPI, "_ahootsa_5027_hooked", True)
    except Exception:
        pass

    try:
        from starlette.applications import Starlette as _Starlette
        if not getattr(_Starlette, "_ahootsa_5027_hooked", False):
            _orig_starlette_init = _Starlette.__init__

            def _ahootsa_starlette_init(self, *args, **kwargs):
                _orig_starlette_init(self, *args, **kwargs)
                _ahootsa_5027_register_compat_routes(self)

            _Starlette.__init__ = _ahootsa_starlette_init
            setattr(_Starlette, "_ahootsa_5027_hooked", True)
    except Exception:
        pass


def _ahootsa_5027_patch_already_loaded_apps():
    """Si algun modulo del paquete ya ha cargado una app global, tambien la parchea."""
    try:
        import sys as _sys
        for _name, _module in list(_sys.modules.items()):
            if not _name.startswith("ahootsa_realtime_ollama_desktop_app"):
                continue
            for _value in list(getattr(_module, "__dict__", {}).values()):
                if hasattr(_value, "routes") and (hasattr(_value, "add_api_route") or hasattr(_value, "add_route")):
                    _ahootsa_5027_register_compat_routes(_value)
    except Exception:
        pass


_ahootsa_5027_install_fastapi_starlette_hooks()
_ahootsa_5027_patch_already_loaded_apps()
# ============================================================
# Fin Ahootsa 5.0.27 - bootstrap endpoints compatibilidad frontend
# ============================================================

'''.lstrip()


def _read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _write(path: pathlib.Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> int:
    print("============================================================")
    print("Ahootsa 5.0.27 - bootstrap endpoints compatibilidad")
    print("============================================================")
    print("Python:", sys.executable)

    try:
        package = importlib.import_module(PACKAGE_NAME)
    except Exception as exc:
        print(f"[ERROR] No se puede importar {PACKAGE_NAME}: {exc}")
        print("Ejecuta este parche con el python.exe de apps_venv de Reachy Mini Control.")
        return 2

    root = pathlib.Path(package.__file__).resolve().parent
    init_file = pathlib.Path(package.__file__).resolve()

    print("Paquete:", root)
    print("__init__.py:", init_file)

    if init_file.name != "__init__.py":
        print("[ERROR] El paquete no apunta a un __init__.py normal. No modifico nada.")
        return 3

    text = _read(init_file)

    if PATCH_MARKER in text:
        print("[OK] El bootstrap 5.0.27 ya estaba aplicado. No se modifica nada.")
        return 0

    ts = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = init_file.with_suffix(init_file.suffix + f".bak_5_0_27_{ts}")
    _write(backup, text)
    print("Backup:", backup)

    patched = BOOTSTRAP_CODE + text

    try:
        compile(patched, str(init_file), "exec")
    except SyntaxError as exc:
        print("[ERROR] El bootstrap no compila. No se ha modificado nada.")
        print(exc)
        return 4

    _write(init_file, patched)
    print("[OK] Bootstrap aplicado al principio de __init__.py")
    print("[OK] Ya no se necesita encontrar literalmente app = FastAPI(...).")
    print("[OK] Reinicia Ahootsa/Desktop Control y comprueba /status, /mic, /voices/current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
