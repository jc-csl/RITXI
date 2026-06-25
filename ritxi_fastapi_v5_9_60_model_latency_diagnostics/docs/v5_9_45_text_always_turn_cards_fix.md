# v5.9.45 · Texto siempre aceptado y turnos abiertos

## Problema corregido

En juegos y actividades con turno, cuando el micro quedaba esperando, el envío por texto podía no entrar.
Además, algunas actividades que terminaban con "ahora te toca a ti" no estaban marcadas como actividades con turno.

## Cambios

- `sendTurn()` acepta siempre texto manual.
- Envío manual cancela STT/micro pendiente.
- `activityNeedsMicroPrompt()` detecta más actividades abiertas.
- Actividades de historia/cuento/ritmo/bailes/eco pasan a `awaitUser`.
- Pasos internos con "tu turno" activan micro y texto.
- Baja el timeout cliente de Ollama a 14 s.
- Baja `llm_max_tokens` a 35 y `max_history_messages` a 4.

## Actividades revisadas

- `historia_turnos`
- `cuento_interactivo`
- `cuento_corto`
- `final_historia`
- `personajes`
- `recordar_historia`
- `ritmo_palmas`
- `palmas_lentas`
- `palmas_rapidas`
- `cantar_saludo`
- `baile_suave`
- `baile_divertido`
- `imitame`
- `eco_ritxi`
