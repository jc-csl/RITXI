# v0.4.35 — Inicio en castellano y voz Sohee

## Problema

Aunque `voice.txt` decía `Sohee`, el instalador anterior ejecutaba:

```powershell
CAMBIAR_VOZ_AHOOTSA.ps1 -Voice Sohee
```

Además, algunas versiones de la app oficial pueden lanzar primero su saludo por defecto:

```text
Hi there, I'm Reachy Mini
```

antes de aplicar del todo el perfil Ahootsa.

## Corrección

```text
- El instalador fuerza Sohee.
- Sohee aparece primera en el selector.
- greeting.txt dice: ¡Hola! Soy Ahootsa...
- Se añade FORZAR_INICIO_CASTELLANO_SOHEE.ps1.
- Se hace backup del greeting default oficial antes de cambiarlo.
```

## Uso

Con Reachy Mini Desktop cerrado:

```powershell
powershell -ExecutionPolicy Bypass -File .\FORZAR_INICIO_CASTELLANO_SOHEE.ps1
```

Luego abrir Ahootsa de nuevo.
