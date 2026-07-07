
from __future__ import annotations

import json
import sys
import time
import traceback


def out(**kwargs):
    print(json.dumps(kwargs, ensure_ascii=False))


def connect_mini():
    from reachy_mini import ReachyMini

    attempts = [
        {"connection_mode": "localhost_only", "media_backend": "no_media"},
        {"connection_mode": "localhost_only"},
        {"media_backend": "no_media"},
        {},
    ]
    last_exc = None
    for kwargs in attempts:
        try:
            mini = ReachyMini(**kwargs)
            return mini, kwargs
        except TypeError as exc:
            last_exc = exc
            continue
        except Exception as exc:
            last_exc = exc
            continue
    raise RuntimeError(f"No se pudo crear ReachyMini con ninguna combinación: {last_exc}")


def goto(mini, **kwargs):
    # SDK documented method. Keep target values conservative.
    mini.goto_target(**kwargs)


def action_probe():
    import reachy_mini
    from reachy_mini import ReachyMini

    mini, kwargs = connect_mini()
    with mini:
        attrs = [a for a in dir(mini) if not a.startswith("_")]
        out(
            ok=True,
            command="probe",
            sdk_module=str(getattr(reachy_mini, "__file__", "")),
            connection_kwargs=kwargs,
            public_attrs=attrs[:80],
            has_goto_target=hasattr(mini, "goto_target"),
            has_media=hasattr(mini, "media"),
        )


def action_wiggle():
    mini, kwargs = connect_mini()
    with mini:
        goto(mini, antennas=[0.5, -0.5], duration=0.5)
        goto(mini, antennas=[-0.5, 0.5], duration=0.5)
        goto(mini, antennas=[0, 0], duration=0.5)
        out(ok=True, command="wiggle", connection_kwargs=kwargs, message="Antenas movidas en simulación.")


def action_saludo():
    mini, kwargs = connect_mini()
    with mini:
        goto(mini, antennas=[0.45, -0.45], body_yaw=0.25, duration=0.5)
        goto(mini, antennas=[-0.45, 0.45], body_yaw=-0.25, duration=0.5)
        goto(mini, antennas=[0, 0], body_yaw=0, duration=0.5)
        out(ok=True, command="saludo", connection_kwargs=kwargs, message="Saludo robótico ejecutado.")


def action_nod():
    try:
        from reachy_mini.utils import create_head_pose
    except Exception:
        create_head_pose = None

    mini, kwargs = connect_mini()
    with mini:
        if create_head_pose is not None:
            goto(mini, head=create_head_pose(z=8, mm=True), duration=0.5)
            goto(mini, head=create_head_pose(z=0, mm=True), duration=0.5)
            goto(mini, head=create_head_pose(z=8, mm=True), duration=0.5)
            goto(mini, head=create_head_pose(z=0, mm=True), duration=0.5)
            out(ok=True, command="nod", connection_kwargs=kwargs, message="Movimiento de cabeza ejecutado.")
        else:
            # Fallback: body movement if head pose helper is not importable.
            goto(mini, body_yaw=0.2, duration=0.4)
            goto(mini, body_yaw=-0.2, duration=0.4)
            goto(mini, body_yaw=0, duration=0.4)
            out(ok=True, command="nod_fallback_body", connection_kwargs=kwargs, message="Fallback con cuerpo ejecutado.")


def action_look_left_right():
    mini, kwargs = connect_mini()
    with mini:
        goto(mini, body_yaw=0.35, duration=0.7)
        goto(mini, body_yaw=-0.35, duration=0.7)
        goto(mini, body_yaw=0, duration=0.7)
        out(ok=True, command="look_left_right", connection_kwargs=kwargs, message="Giro izquierda-derecha ejecutado.")


def action_reset():
    mini, kwargs = connect_mini()
    with mini:
        goto(mini, antennas=[0, 0], body_yaw=0, duration=0.7)
        out(ok=True, command="reset", connection_kwargs=kwargs, message="Robot devuelto a posición neutra.")


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else "probe"
    try:
        if command == "probe":
            action_probe()
        elif command == "wiggle":
            action_wiggle()
        elif command == "saludo":
            action_saludo()
        elif command == "nod":
            action_nod()
        elif command == "look_left_right":
            action_look_left_right()
        elif command == "reset":
            action_reset()
        else:
            out(ok=False, error=f"Comando desconocido: {command}")
            sys.exit(2)
    except Exception as exc:
        out(ok=False, command=command, error=str(exc), traceback=traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
