# 11 — Perfil Ahootsa forzado total v0.4.39

## Problema

En algunas pruebas, aunque se instalaba Ahootsa, la app arrancaba como el perfil original:

```text
Hi there, I'm Reachy Mini
```

o decía que era Reachy Mini y no conocía el juego de parejas.

Eso significa que Reachy Mini Desktop estaba cargando el perfil `default` o `starter_profile`, no `ahootsa_realtime_es`.

## Solución v0.4.39

Se añade un mecanismo más fuerte:

```text
- Copia Ahootsa como perfil ahootsa_realtime_es.
- También copia Ahootsa sobre los perfiles default/starter con backup.
- Fuerza variables de entorno de perfil.
- Comprueba que start_memory_pairs_game y choose_memory_cards estén en tools.txt.
```

## Script principal

Ejecutar con Reachy Mini Desktop cerrado:

```powershell
powershell -ExecutionPolicy Bypass -File .\FORZAR_PERFIL_AHOOTSA_TOTAL.ps1
```

## Diagnóstico

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_PERFIL_AHOOTSA_TOTAL.ps1
```

## Resultado esperado

Al abrir Ahootsa:

```text
¡Hola! Soy Ahootsa. Estoy lista para ayudarte. ¿Qué quieres hacer?
```

Y debe conocer:

```text
juego de animales
juego de ciudades
juego de alimentos
```

## Backup

Si existían perfiles default/starter originales, el script crea carpetas:

```text
default.ahootsa_backup
starter_profile.ahootsa_backup
```

antes de sobrescribir.
