# v0.4.15 — Instalador forzado para los tres Python internos

## Problema detectado en v0.4.13

En el log de instalación se ve:

```text
error: externally-managed-environment
This Python installation is managed by uv and should not be modified.
```

Eso ocurre en:

```text
cpython-3.12-windows-x86_64-none\python.exe
```

Ese Python es importante porque Reachy Mini Desktop puede arrancar apps desde ahí.  
Si ahí queda una versión vieja, Desktop puede seguir ejecutando código antiguo aunque `.venv` y `apps_venv` estén actualizados.

También se ve que la rueda instalada seguía como:

```text
ahootsa-realtime-ollama-desktop-app 0.4.10
```

Por eso se crea v0.4.15.

## Qué corrige

```text
- Fuerza instalación en los tres Python internos.
- Si pip normal falla, reintenta con --break-system-packages.
- Hace uninstall previo del paquete ahootsa-realtime-ollama-desktop-app.
- Verifica la versión instalada con importlib.metadata.
- Ejecuta reparación del perfil.
- Ejecuta diagnóstico final.
```

## Instalación

Con Desktop cerrado:

```powershell
cd D:\RITXI\ahootsa_v0_4_15_instalador_forzado_perfil_ollama
powershell -ExecutionPolicy Bypass -File .\INSTALAR_AHOOTSA_COMPLETO.ps1
```

Al final debe mostrar versión 0.4.15 en los Python internos.
