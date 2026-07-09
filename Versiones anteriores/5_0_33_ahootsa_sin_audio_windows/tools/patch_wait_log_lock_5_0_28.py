"""
Ahootsa 5.0.28 - parche de logs robustos para ESPERAR_5_BACKEND_REALTIME_LISTO.ps1.

Corrige errores del tipo:

    Add-Content : El proceso no puede obtener acceso al archivo ... pantalla.log
    porque esta siendo utilizado en otro proceso.

La correccion sustituye la escritura directa con Add-Content por una funcion tolerante:
- escribe con FileShare.ReadWrite cuando es posible;
- reintenta brevemente;
- si el log sigue bloqueado, no rompe el bucle de espera;
- evita que PowerShell muestre errores no terminantes repetidos.
"""
from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re
import sys

MARKER = "Ahootsa 5.0.28 - escritura robusta de logs"

SAFE_LOG_FUNCTION = r'''
# ============================================================
# Ahootsa 5.0.28 - escritura robusta de logs
# Evita que el arranque falle si pantalla.log esta abierto o
# bloqueado por otro proceso/terminal. Si no puede escribir tras
# unos reintentos breves, descarta solo esa linea de log y sigue.
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
            try {
                $__fs.Write($__bytes, 0, $__bytes.Length)
            } finally {
                $__fs.Dispose()
            }
            return
        } catch {
            Start-Sleep -Milliseconds (80 * $__i)
        }
    }

    # Intencionado: no escribimos errores aqui. El log es auxiliar;
    # no debe romper el arranque ni llenar la pantalla de IOException.
}
# ============================================================
# Fin Ahootsa 5.0.28 - escritura robusta de logs
# ============================================================

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


def find_insert_pos_after_param_block(text: str) -> int:
    """Devuelve una posicion segura para insertar funciones PowerShell."""
    stripped = text.lstrip("\ufeff\r\n\t ")
    offset = len(text) - len(stripped)
    lower = stripped.lower()
    if not lower.startswith("param"):
        return 0

    paren_start = stripped.find("(")
    if paren_start < 0:
        return 0

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
                # Saltar saltos de linea inmediatamente posteriores.
                pos = offset + i + 1
                while pos < len(text) and text[pos] in " \t\r\n":
                    pos += 1
                return pos
    return 0


def patch_wait_script(path: pathlib.Path) -> tuple[bool, str]:
    text = read_text(path)
    original = text

    already_has_func = MARKER in text

    replacements = 0

    # Patron exacto visto en el error:
    # try { $Line | Add-Content -Encoding UTF8 -LiteralPath $Log } catch ...
    pattern_try_pipe = re.compile(
        r"try\s*\{\s*\$Line\s*\|\s*Add-Content\s+-Encoding\s+UTF8\s+-LiteralPath\s+\$Log\s*\}\s*catch\s*\{[^\r\n}]*\}",
        flags=re.IGNORECASE,
    )
    text, n = pattern_try_pipe.subn("Write-AhootsaSafeLog -Path $Log -Line $Line", text)
    replacements += n

    # Variantes posibles sin try/catch.
    variants = [
        (r"\$Line\s*\|\s*Add-Content\s+-Encoding\s+UTF8\s+-LiteralPath\s+\$Log", "Write-AhootsaSafeLog -Path $Log -Line $Line"),
        (r"Add-Content\s+-Encoding\s+UTF8\s+-LiteralPath\s+\$Log\s+-Value\s+\$Line", "Write-AhootsaSafeLog -Path $Log -Line $Line"),
        (r"Add-Content\s+-LiteralPath\s+\$Log\s+-Value\s+\$Line\s+-Encoding\s+UTF8", "Write-AhootsaSafeLog -Path $Log -Line $Line"),
        (r"Add-Content\s+-Path\s+\$Log\s+-Value\s+\$Line\s+-Encoding\s+UTF8", "Write-AhootsaSafeLog -Path $Log -Line $Line"),
    ]
    for pat, repl in variants:
        text, n = re.subn(pat, repl, text, flags=re.IGNORECASE)
        replacements += n

    if replacements > 0 and not already_has_func:
        pos = find_insert_pos_after_param_block(text)
        text = text[:pos] + SAFE_LOG_FUNCTION + text[pos:]

    if text == original:
        if already_has_func:
            return False, "ya estaba parcheado"
        return False, "no encontre patrones Add-Content modificables"

    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = path.with_suffix(path.suffix + f".bak_5_0_28_{ts}")
    write_text(backup, original)
    write_text(path, text)
    return True, f"parcheado; reemplazos={replacements}; backup={backup}"


def find_wait_scripts(target_root: pathlib.Path) -> list[pathlib.Path]:
    if target_root.is_file() and target_root.name.lower() == "esperar_5_backend_realtime_listo.ps1":
        return [target_root]
    if not target_root.exists():
        return []
    return sorted(target_root.rglob("ESPERAR_5_BACKEND_REALTIME_LISTO.ps1"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-root", required=True, help="Carpeta de la version Ahootsa que contiene ESPERAR_5_BACKEND_REALTIME_LISTO.ps1")
    args = parser.parse_args()

    target = pathlib.Path(args.target_root).expanduser().resolve()
    print("============================================================")
    print("Ahootsa 5.0.28 - parche logs robustos")
    print("============================================================")
    print("Target:", target)

    scripts = find_wait_scripts(target)
    if not scripts:
        print("[ERROR] No encuentro ESPERAR_5_BACKEND_REALTIME_LISTO.ps1 en el target.")
        print("Indica la carpeta correcta con -TargetRoot desde PowerShell.")
        return 2

    changed_any = False
    warn_any = False
    for script in scripts:
        print("\nScript:", script)
        try:
            changed, msg = patch_wait_script(script)
            changed_any = changed_any or changed
            if "no encontre" in msg:
                warn_any = True
                print("[AVISO]", msg)
            else:
                print("[OK]", msg)
        except Exception as exc:
            print("[ERROR] No se pudo parchear:", exc)
            return 3

    if warn_any and not changed_any:
        print("\n[AVISO] No se modifico nada. Puede que el script use otra forma de logging.")
        return 4

    print("\n[OK] Parche de logs 5.0.28 terminado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
