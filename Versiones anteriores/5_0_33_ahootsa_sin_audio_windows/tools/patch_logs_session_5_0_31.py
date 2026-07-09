"""
Ahootsa 5.0.31 - logs por ejecucion y scripts PowerShell tolerantes.

Corrige tres problemas observados en 5.0.30:
1) FORZAR_5_VOZ_SOHEE_COMPLETA.ps1 seguia usando Add-Content directo contra pantalla.log.
2) ESPERAR_5_BACKEND_REALTIME_LISTO.ps1 podia quedar con un param() roto tras parches previos.
3) El lanzador podia reutilizar un timestamp antiguo, mezclando varias ejecuciones en el mismo log.

La correccion:
- reemplaza ESPERAR_5_BACKEND_REALTIME_LISTO.ps1 por una version canonica y segura;
- añade -ErrorAction SilentlyContinue a Add-Content que escribe en $Log en todos los .ps1;
- fuerza una nueva sesion timestamp en LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1;
- crea copias .bak_5_0_31_YYYYMMDD_HHMMSS antes de modificar.
"""
from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re
import sys

MARKER = "Ahootsa 5.0.31 - logs por ejecucion"

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
# Ahootsa 5.0.31 - logs por ejecucion / espera robusta
# Este script reemplaza versiones parcheadas que podian quedar
# con param() roto. No debe bloquear el arranque por problemas
# de log ni por timeouts de diagnostico.
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
        $body = ""
        try { $body = [string]$resp.Content } catch { $body = "" }
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
    b = path.with_suffix(path.suffix + f".bak_5_0_31_{ts}")
    write_text(b, original)
    return b


def find_insert_pos_after_param_block(text: str) -> int:
    stripped = text.lstrip("\ufeff\r\n\t ")
    offset = len(text) - len(stripped)
    if not stripped.lower().startswith("param"):
        return offset
    paren_start = stripped.find("(")
    if paren_start < 0:
        return offset
    depth = 0
    in_single = False
    in_double = False
    escape = False
    for i, ch in enumerate(stripped[paren_start:], start=paren_start):
        if escape:
            escape = False
            continue
        if ch == "`":
            escape = True
            continue
        if ch == "'" and not in_double:
            in_single = not in_single
            continue
        if ch == '"' and not in_single:
            in_double = not in_double
            continue
        if in_single or in_double:
            continue
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                pos = offset + i + 1
                while pos < len(text) and text[pos] in " \t\r\n":
                    pos += 1
                return pos
    return offset


def patch_add_content_error_action(text: str) -> tuple[str, int]:
    """Añade -ErrorAction SilentlyContinue a Add-Content que escribe en $Log."""
    count = 0

    def repl_segment(match: re.Match) -> str:
        nonlocal count
        seg = match.group(0)
        if "-ErrorAction" in seg:
            return seg
        count += 1
        return seg + " -ErrorAction SilentlyContinue"

    # Sustituye solo el comando hasta antes de } o fin de linea. Cubre la forma del error:
    # "..." | Add-Content -Encoding UTF8 -LiteralPath $Log } catch {}
    pattern = re.compile(r"Add-Content\b(?=[^\r\n{}]*\$Log)(?:(?![\r\n{}]).)*", re.IGNORECASE)
    text = pattern.sub(repl_segment, text)
    return text, count


def patch_script_add_content(path: pathlib.Path) -> tuple[bool, str]:
    original = read_text(path)
    text, n = patch_add_content_error_action(original)
    if text == original:
        return False, "sin Add-Content contra $Log modificable"
    b = backup(path, original)
    write_text(path, text)
    return True, f"Add-Content protegido; cambios={n}; backup={b.name}"


def patch_wait_script(path: pathlib.Path) -> tuple[bool, str]:
    original = read_text(path) if path.exists() else ""
    if MARKER in original and "Resolve-AhootsaBaseUrl" in original:
        return False, "ESPERAR ya estaba en formato 5.0.31"
    b = backup(path, original) if path.exists() else None
    write_text(path, WAIT_SCRIPT)
    return True, f"ESPERAR reemplazado por version canonica 5.0.31; backup={b.name if b else 'no_existia'}"


def patch_launcher(path: pathlib.Path) -> tuple[bool, str]:
    original = read_text(path)
    text = original
    changes = 0

    session_line = '$Session = if ($env:AHOOTSA_SESSION) { $env:AHOOTSA_SESSION } else { Get-Date -Format "yyyyMMdd_HHmmss" }'

    # Reemplaza asignaciones directas a $Session para evitar reutilizar timestamps antiguos.
    text2, n = re.subn(r'(?im)^\s*\$Session\s*=\s*.*$', session_line, text)
    text = text2
    changes += n

    injection = r'''
# ============================================================
# Ahootsa 5.0.31 - logs por ejecucion
# Cada lanzamiento debe crear un ID nuevo para que pantalla/runtime/eventos
# no mezclen varias pruebas. Si el wrapper ya puso AHOOTSA_SESSION, se respeta.
# ============================================================
if ([string]::IsNullOrWhiteSpace($env:AHOOTSA_SESSION)) {
    $env:AHOOTSA_SESSION = Get-Date -Format "yyyyMMdd_HHmmss"
}
$env:AHOOTSA_LAST_SESSION = $env:AHOOTSA_SESSION
# ============================================================
# Fin Ahootsa 5.0.31 - logs por ejecucion
# ============================================================

'''.lstrip()
    if MARKER not in text:
        pos = find_insert_pos_after_param_block(text)
        text = text[:pos] + injection + text[pos:]
        changes += 1

    if text == original:
        return False, "LANZAR ya estaba actualizado"
    b = backup(path, original)
    write_text(path, text)
    return True, f"LANZAR actualizado para nueva sesion por ejecucion; cambios={changes}; backup={b.name}"


def find_one(root: pathlib.Path, name: str) -> pathlib.Path | None:
    if root.is_file() and root.name.lower() == name.lower():
        return root
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
    print("Ahootsa 5.0.31 - logs por ejecucion")
    print("============================================================")
    print("Target:", root)

    if not root.exists():
        print("[ERROR] No existe target-root:", root)
        return 2

    changed_any = False

    wait = find_one(root, "ESPERAR_5_BACKEND_REALTIME_LISTO.ps1")
    if wait:
        changed, msg = patch_wait_script(wait)
        changed_any = changed_any or changed
        print("[OK]", wait)
        print("     ", msg)
    else:
        print("[WARN] No encuentro ESPERAR_5_BACKEND_REALTIME_LISTO.ps1")

    launcher = find_one(root, "LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1")
    if launcher:
        changed, msg = patch_launcher(launcher)
        changed_any = changed_any or changed
        print("[OK]", launcher)
        print("     ", msg)
    else:
        print("[WARN] No encuentro LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1")

    print("\n[INFO] Protegiendo Add-Content contra $Log en todos los .ps1...")
    for ps1 in sorted(root.rglob("*.ps1")):
        # El wait ya se ha reemplazado y ya es seguro; aun asi no molesta parchearlo.
        try:
            changed, msg = patch_script_add_content(ps1)
            if changed:
                changed_any = True
                print("[OK]", ps1.name, "-", msg)
        except Exception as exc:
            print("[WARN] No se pudo revisar", ps1, exc)

    print("\n[OK] Correccion 5.0.31 de logs terminada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
