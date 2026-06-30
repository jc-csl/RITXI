# v0.4.35 — Voz española más natural

## Objetivo

Probar una voz más natural sin modificar el código original de la app oficial.

La versión cambia el perfil Ahootsa para usar por defecto:

```text
Coral
```

También añade instrucciones de pronunciación:

```text
- español natural y claro;
- pronunciación lo más neutra posible;
- evitar acento inglés;
- frases cortas;
- ritmo amable.
```

## Cambiar voz manualmente

Con Reachy Mini Desktop cerrado:

```powershell
powershell -ExecutionPolicy Bypass -File .\CAMBIAR_VOZ_AHOOTSA.ps1
```

O directamente:

```powershell
powershell -ExecutionPolicy Bypass -File .\CAMBIAR_VOZ_AHOOTSA.ps1 -Voice Sohee
powershell -ExecutionPolicy Bypass -File .\CAMBIAR_VOZ_AHOOTSA.ps1 -Voice Sage
powershell -ExecutionPolicy Bypass -File .\CAMBIAR_VOZ_AHOOTSA.ps1 -Voice Shimmer
powershell -ExecutionPolicy Bypass -File .\CAMBIAR_VOZ_AHOOTSA.ps1 -Voice Alloy
```

## Ver voz activa

```powershell
powershell -ExecutionPolicy Bypass -File .\VER_VOZ_AHOOTSA.ps1
```

## Nota

La disponibilidad real de cada voz depende del backend realtime de la app oficial.
Si una voz no cambia o no está soportada, probar otra.

Recomendación de prueba:

```text
1. Coral
2. Sage
3. Shimmer
4. Alloy
```
