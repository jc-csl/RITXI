"""
Ahootsa 5.0.33 - reparacion del lanzador PowerShell + logs por ejecucion.

Corrige el problema observado tras 5.0.31:

    LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1: [int]$Port = 8000,
    La expresion de asignacion no es valida.

Causa: el script principal quedo con codigo ejecutable antes del bloque param(...).
En PowerShell, param(...) debe ser el primer bloque efectivo del archivo. Si se inserta
un if/variable antes, PowerShell interpreta las lineas [int]$Port = 8000, como codigo normal.

La reparacion:
- elimina bloques inyectados 5.0.31/5.0.33 que puedan estar antes de param(...);
- NO vuelve a insertar codigo antes de param(...);
- reemplaza asignaciones $Session = ... por una expresion que respeta $env:AHOOTSA_SESSION;
- reconstruye ESPERAR_5_BACKEND_REALTIME_LISTO.ps1 con una version segura;
- protege Add-Content contra $Log sin romper el arranque;
- genera backup antes de tocar scripts.
"""
from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re
import sys

MARKER = "Ahootsa 5.0.33 - reparacion launcher param"

WAIT_SCRIPT = r'''
param(
    [string]$Url = "",
    [string]$BaseUrl = "",
    [string]$StatusUrl = "",
    [string]$ApiBaseUrl = "",
    [string]$RealtimeUrl = "",
    [string]$HostName = "127.0.0.1",
    [int]$Port = 7860,
    [string]$Log = "",
    [string]$LogPath = "",
    [string]$PantallaLog = "",
    [int]$TimeoutSeconds = 120,
    [int]$IntervalSeconds = 3,
    [int]$MaxAttempts = 0,
    [int]$SleepSeconds = 0
)

$ErrorActionPreference = "Continue"

# ============================================================
# Ahootsa 5.0.33 - espera backend segura
# Reemplaza versiones parcheadas que podian quedar con param() roto.
# No debe bloquear el arranque por problemas de log ni por timeout.
# ============================================================

function Write-AhootsaSafeLog {
    param(
        [Parameter(Mandatory=$false)][string]$Path,
        [Parameter(Mandatory=$false)][string]$Line
    )

    if ([string]::IsNullOrWhiteSpace($Path)) { return }

    for ($__i = 1; $__i -le 3; $__i++) {
        try {
            $__dir = Split-Path -Parent $Path
            if ($__dir -and -not (Test-Path -LiteralPath $__dir)) {
                New-Item -ItemType Directory -Force -Path $__dir | Out-Null
            }
            $__text = [string]$Line + [Environment]::NewLine
            $__bytes = [System.Text.Encoding]::UTF8.GetBytes($__text)
            $__fs = [System.IO.File]::Open(
                $Path,
                [System.IO.FileMode]::Append,
                [System.IO.FileAccess]::Write,
                [System.IO.FileShare]::ReadWrite
            )
            try { $__fs.Write($__bytes, 0, $__bytes.Length) }
            finally { $__fs.Dispose() }
            return
        } catch {
            Start-Sleep -Milliseconds (80 * $__i)
        }
    }
}

function Resolve-AhootsaBaseUrl {
    if (-not [string]::IsNullOrWhiteSpace($StatusUrl)) {
        $u = $StatusUrl.Trim()
        if ($u.EndsWith('/status')) { return $u.Substring(0, $u.Length - 7).TrimEnd('/') }
        return $u.TrimEnd('/')
    }
    foreach ($candidate in @($BaseUrl, $ApiBaseUrl, $RealtimeUrl, $Url)) {
        if (-not [string]::IsNullOrWhiteSpace($candidate)) {
            return $candidate.TrimEnd('/')
        }
    }
    return "http://$HostName`:$Port"
}

if ([string]::IsNullOrWhiteSpace($Log)) {
    if (-not [string]::IsNullOrWhiteSpace($LogPath)) { $Log = $LogPath }
    elseif (-not [string]::IsNullOrWhiteSpace($PantallaLog)) { $Log = $PantallaLog }
}

if ($SleepSeconds -gt 0) { $IntervalSeconds = $SleepSeconds }
if ($MaxAttempts -gt 0 -and $TimeoutSeconds -le 0) { $TimeoutSeconds = $MaxAttempts * $IntervalSeconds }
if ($TimeoutSeconds -le 0) { $TimeoutSeconds = 120 }
if ($IntervalSeconds -le 0) { $IntervalSeconds = 3 }

$Base = Resolve-AhootsaBaseUrl
$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
$attempt = 0

Write-Host "[INFO] Esperando backend realtime en $Base/status ..."
Write-AhootsaSafeLog -Path $Log -Line "$(Get-Date -Format o) espera_backend_inicio url=$Base/status timeout=$TimeoutSeconds interval=$IntervalSeconds"

while ((Get-Date) -lt $deadline) {
    $attempt += 1
    try {
        $resp = Invoke-WebRequest -Uri ($Base + "/status") -UseBasicParsing -TimeoutSec 4 -ErrorAction Stop
        $line = "$(Get-Date -Format o) intento=$attempt http=$($resp.StatusCode) backend_status_ok=true"
        Write-Host $line
        Write-AhootsaSafeLog -Path $Log -Line $line
        exit 0
    } catch {
        $msg = $_.Exception.Message -replace "`r|`n", " "
        $line = "$(Get-Date -Format o) intento=$attempt backend_status_ok=false url=$Base/status error=$msg"
        Write-Host $line
        Write-AhootsaSafeLog -Path $Log -Line $line
        Start-Sleep -Seconds $IntervalSeconds
    }
}

$warn = "$(Get-Date -Format o) warn=timeout_esperando_backend_realtime url=$Base/status timeout=$TimeoutSeconds continua_arranque=true"
Write-Host "[WARN] Timeout esperando backend realtime; se continua el arranque para no bloquear la app."
Write-AhootsaSafeLog -Path $Log -Line $warn
exit 0
'''.lstrip()


def read_text(path: pathlib.Path) -> str:
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="ignore")


def write_text(path: pathlib.Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def backup(path: pathlib.Path, original: str) -> pathlib.Path:
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    b = path.with_suffix(path.suffix + f".bak_5_0_33_{ts}")
    write_text(b, original)
    return b


def remove_ahootsa_injected_blocks(text: str) -> tuple[str, int]:
    """Elimina bloques de inyeccion que podian romper param(...)."""
    original = text
    patterns = [
        # Bloque completo con cabeceras de separadores de 5.0.31/5.0.33.
        r"(?ms)^# =+\s*\n# Ahootsa 5\.0\.31 - logs por ejecucion.*?# Fin Ahootsa 5\.0\.31 - logs por ejecucion\s*\n# =+\s*\n",
        r"(?ms)^# =+\s*\n# Ahootsa 5\.0\.32 - .*?# Fin Ahootsa 5\.0\.32 - .*?\s*\n# =+\s*\n",
        # Version menos estricta por si el bloque quedo sin las lineas finales exactas.
        r"(?ms)^# Ahootsa 5\.0\.31 - logs por ejecucion.*?\$env:AHOOTSA_LAST_SESSION\s*=\s*\$env:AHOOTSA_SESSION\s*\n",
        r"(?ms)^# Ahootsa 5\.0\.32 - .*?\$env:AHOOTSA_LAST_SESSION\s*=\s*\$env:AHOOTSA_SESSION\s*\n",
    ]
    for pat in patterns:
        text = re.sub(pat, "", text, flags=0)
    return text, 0 if text == original else 1


def starts_with_valid_param(text: str) -> bool:
    stripped = text.lstrip("\ufeff\r\n\t ")
    # Comentarios iniciales son aceptables, pero simplificamos: si despues de quitar espacios/comentarios
    # aparece param, lo damos por bueno.
    lines = stripped.splitlines(True)
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if s == "" or s.startswith("#"):
            i += 1
            continue
        return s.lower().startswith("param")
    return False


def find_first_param_start(text: str) -> int | None:
    m = re.search(r"(?im)^\s*param\s*\(", text)
    return m.start() if m else None


def move_param_to_start_if_needed(text: str) -> tuple[str, int]:
    """Si hay basura antes de param(...) y no son solo comentarios, la elimina/mueve para que param sea primero."""
    if starts_with_valid_param(text):
        return text, 0
    pos = find_first_param_start(text)
    if pos is None:
        return text, 0
    prefix = text[:pos]
    # Conserva comentarios utiles del prefijo, pero elimina instrucciones ejecutables.
    comments = []
    for line in prefix.splitlines():
        if line.strip().startswith("#"):
            comments.append(line)
    new_prefix = ""
    if comments:
        new_prefix = "\n".join(comments[-6:]) + "\n"
    return new_prefix + text[pos:].lstrip("\r\n"), 1


def patch_session_assignments(text: str) -> tuple[str, int]:
    """Hace que el lanzador original use el timestamp del wrapper si existe."""
    session_line = '$Session = if ($env:AHOOTSA_SESSION) { $env:AHOOTSA_SESSION } else { Get-Date -Format "yyyyMMdd_HHmmss" }'
    # No tocar asignaciones que ya usan AHOOTSA_SESSION.
    changes = 0
    new_lines = []
    for line in text.splitlines(True):
        if re.match(r"^\s*\$Session\s*=", line, flags=re.IGNORECASE) and "AHOOTSA_SESSION" not in line:
            newline = "\r\n" if line.endswith("\r\n") else "\n"
            new_lines.append(session_line + newline)
            changes += 1
        else:
            new_lines.append(line)
    return "".join(new_lines), changes


def patch_add_content_error_action(text: str) -> tuple[str, int]:
    count = 0

    def repl_segment(match: re.Match) -> str:
        nonlocal count
        seg = match.group(0)
        if "-ErrorAction" in seg:
            return seg
        count += 1
        return seg + " -ErrorAction SilentlyContinue"

    pattern = re.compile(r"Add-Content\b(?=[^\r\n{}]*\$Log)(?:(?![\r\n{}]).)*", re.IGNORECASE)
    text2 = pattern.sub(repl_segment, text)
    return text2, count


def patch_ps1_add_content(path: pathlib.Path) -> tuple[bool, str]:
    original = read_text(path)
    text, n = patch_add_content_error_action(original)
    if text == original:
        return False, "sin Add-Content contra $Log modificable"
    b = backup(path, original)
    write_text(path, text)
    return True, f"Add-Content protegido; cambios={n}; backup={b.name}"


def patch_wait_script(path: pathlib.Path) -> tuple[bool, str]:
    original = read_text(path) if path.exists() else ""
    if "Ahootsa 5.0.33 - espera backend segura" in original:
        return False, "ESPERAR ya estaba en formato 5.0.33"
    b = backup(path, original) if path.exists() else None
    write_text(path, WAIT_SCRIPT)
    return True, f"ESPERAR reemplazado por version canonica 5.0.33; backup={b.name if b else 'no_existia'}"


def patch_launcher(path: pathlib.Path) -> tuple[bool, str]:
    original = read_text(path)
    text = original
    notes = []

    text, removed = remove_ahootsa_injected_blocks(text)
    if removed:
        notes.append("bloques_inyectados_eliminados")

    text, moved = move_param_to_start_if_needed(text)
    if moved:
        notes.append("param_recolocado_al_inicio")

    text, nsession = patch_session_assignments(text)
    if nsession:
        notes.append(f"session_assignments={nsession}")

    if text == original:
        return False, "LANZAR ya estaba reparado o no requeria cambios"

    b = backup(path, original)
    write_text(path, text)
    return True, f"LANZAR reparado para no romper param(...); {', '.join(notes) if notes else 'cambios menores'}; backup={b.name}"


def find_one(root: pathlib.Path, name: str) -> pathlib.Path | None:
    direct = root / name
    if direct.is_file():
        return direct
    for p in sorted(root.rglob(name)):
        if p.is_file():
            return p
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-root", required=True)
    args = parser.parse_args()

    root = pathlib.Path(args.target_root).expanduser().resolve()
    print("============================================================")
    print("Ahootsa 5.0.33 - reparacion launcher param + logs limpios")
    print("============================================================")
    print("Target:", root)

    if not root.exists():
        print("[ERROR] No existe target-root:", root)
        return 2

    wait = find_one(root, "ESPERAR_5_BACKEND_REALTIME_LISTO.ps1")
    if wait:
        changed, msg = patch_wait_script(wait)
        print("[OK]", wait)
        print("     ", msg)
    else:
        print("[WARN] No encuentro ESPERAR_5_BACKEND_REALTIME_LISTO.ps1")

    launcher = find_one(root, "LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1")
    if launcher:
        changed, msg = patch_launcher(launcher)
        print("[OK]", launcher)
        print("     ", msg)
    else:
        print("[WARN] No encuentro LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1")

    print("\n[INFO] Protegiendo Add-Content contra $Log en todos los .ps1...")
    for ps1 in sorted(root.rglob("*.ps1")):
        try:
            changed, msg = patch_ps1_add_content(ps1)
            if changed:
                print("[OK]", ps1.name, "-", msg)
        except Exception as exc:
            print("[WARN] No se pudo revisar", ps1, exc)

    print("\n[OK] Correccion 5.0.33 de launcher/logs terminada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
