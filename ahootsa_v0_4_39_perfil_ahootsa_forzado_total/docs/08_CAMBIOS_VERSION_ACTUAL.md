# 08 — Cambios versión actual v0.4.39

## Limpieza de documentación

```text
- Se elimina documentación antigua de cambios parciales.
- Se crea una documentación nueva orientada a entender el código actual.
- Se documentan estructura, flujos, configuración y tests.
```

## Organización de tests

```text
- Los scripts PROBAR_*.ps1 pasan a /test.
- Los scripts DIAGNOSTICAR_*.ps1 pasan a /test.
- VER_VOZ_AHOOTSA.ps1 pasa a /test.
- Los scripts de instalación, reparación y configuración se mantienen en raíz.
```

## Egg-info

```text
- Se revisa ahootsa_realtime_ollama_desktop_app.egg-info.
- No es necesaria en el ZIP fuente.
- Si aparece, se elimina.
```

Carpetas egg-info eliminadas en esta limpieza:

```text
ninguna encontrada
```

## Voz e inicio

```text
- Voz esperada: Sohee
- Saludo esperado: castellano, como Ahootsa.
```

## Comandos principales

```powershell
powershell -ExecutionPolicy Bypass -File .\INSTALAR_AHOOTSA_COMPLETO.ps1
powershell -ExecutionPolicy Bypass -File .\FORZAR_INICIO_CASTELLANO_SOHEE.ps1
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_INICIO_AHOOTSA.ps1
powershell -ExecutionPolicy Bypass -File .\test\PROBAR_MEMORY_START_SERVER.ps1
```
