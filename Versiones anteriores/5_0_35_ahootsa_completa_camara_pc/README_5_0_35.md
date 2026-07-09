# Ahootsa 5.0.35 — Versión completa con cámara PC

Esta versión crea una carpeta completa nueva basada en la 5.0.34 y añade control de cámara del PC.

## Crear versión completa

```powershell
powershell -ExecutionPolicy Bypass -File .\0_CREAR_VERSION_COMPLETA_5_0_35.ps1
```

Si ya existe:

```powershell
powershell -ExecutionPolicy Bypass -File .\0_CREAR_VERSION_COMPLETA_5_0_35.ps1 -Force
```

## Lanzar

```powershell
cd D:\RITXI\5_0_35_ahootsa_completa_camara_pc
powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_5_0_35.ps1
```

## Qué añade

- Panel flotante **Cámara PC**.
- Activación manual de cámara.
- Captura de foto desde el navegador.
- Guardado de foto en `D:\RITXI\logs\camera`.
- Endpoints:
  - `GET /camera/latest`
  - `POST /camera/upload`

## Mantiene

- Versión consolidada 5.0.34.
- Audio único Ahootsa.
- Bloqueo de voz Windows/navegador/pyttsx3/SAPI.
- Logs por ejecución con timestamp.
- Endpoints de compatibilidad anteriores.
