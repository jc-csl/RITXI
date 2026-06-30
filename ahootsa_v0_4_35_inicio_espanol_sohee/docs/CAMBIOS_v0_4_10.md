# Cambios v0.4.35 — Base instalación desde cero

Esta versión mantiene la base estable v0.4.35 y añade documentación e instalación portable.

## Cambios

```text
- Añadido INSTALAR_AHOOTSA_COMPLETO.ps1 en la raíz.
- Añadido scripts/windows/00_INSTALACION_COMPLETA_DESDE_CERO.ps1.
- Añadido docs/INSTALACION_DESDE_CERO.md.
- El script de creación de modelo Ollama ya no depende de D:\RITXI.
- El Modelfile se crea en %LOCALAPPDATA%\Ahootsa\ollama_ahootsa.
- El instalador completo comprueba Reachy Mini Desktop, app oficial, Python internos y Ollama.
- Se mantiene intacta la app oficial y solo se añade ask_ollama.
```

## Instalación recomendada

```powershell
.\INSTALAR_AHOOTSA_COMPLETO.ps1
```

Si PowerShell bloquea scripts:

```powershell
powershell -ExecutionPolicy Bypass -File .\INSTALAR_AHOOTSA_COMPLETO.ps1
```
