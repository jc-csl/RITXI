# ARQUITECTURA Y FUNCIONALIDAD — Ahootsa 5.0.20

## Objetivo
Ahootsa es un perfil y conjunto de herramientas sobre la app oficial `reachy_mini_conversation_app`.

La versión 5.0.20 prioriza:
- conversación fluida;
- perfil corto y claro;
- voz Sohee sin BOM;
- actividades guiadas sin bloquear la conversación;
- logs operativos en `D:\RITXI\logs`.

## Estructura de carpetas
- `src/ahootsa_realtime_ollama_desktop_app/`: paquete Python Ahootsa.
- `profiles/ahootsa_realtime_es/`: perfil Ahootsa.
- `tools.txt`: lista de herramientas cargadas.
- `instructions.txt`: perfil conversacional simplificado.
- `docs/`: documentación técnica.
- `test/`: diagnósticos.
- scripts `.ps1`: instalación, arranque y diagnóstico en Windows.

## Qué se reutiliza de la app oficial
Se reutiliza la app oficial de conversación como núcleo:
- backend realtime Hugging Face;
- servidor app en `7860`;
- daemon Reachy Mini en `8000`;
- herramientas oficiales de movimiento, cámara, memoria y emociones;
- gestor de apps de Reachy Mini Desktop.

## Qué carpetas/código son nuevos
Ahootsa añade:
- perfil `ahootsa_realtime_es`;
- herramientas de actividades de comunicación;
- herramientas de Memory visual;
- `ask_ollama.py` como actividad opcional;
- scripts de instalación y diagnóstico;
- limpieza de voz Sohee sin BOM;
- logs en `D:\RITXI\logs`.

## Herramientas activas
Principales:
- `list_communication_activity_levels`
- `list_communication_activities`
- `start_communication_activity`
- `start_memory_pairs_game`
- `choose_memory_cards`
- `list_memory_pairs_games`
- `play_emotion`
- `play_emotion_with_audio`
- `play_panel_dance_activity`
- `play_community_dance`
- `camera`
- `camera_pc`
- `ask_ollama`

## IA remota
La conversación normal usa el backend realtime de la app oficial, normalmente Hugging Face session proxy.

Uso:
- charla normal;
- guía educativa;
- decisión de si llamar una herramienta.

## IA local Ollama
`ask_ollama` consulta Ollama local.

Regla:
No es el cerebro principal.
Solo se usa si el usuario pide explícitamente:
- usar IA local;
- consultar Ollama;
- preguntar al modelo local;
- usar `ahootsa-local`.

## Cuándo se llama a Ollama
Solo si la petición contiene intención clara de IA local.

Ejemplos:
- "usa la IA local para darme una actividad";
- "consulta Ollama";
- "pregunta al modelo local".

No se llama para:
- conversación normal;
- iniciar actividades;
- movimiento;
- Memory;
- cámara;
- saludos.

## Voz
La voz objetivo es Sohee.

Problema corregido:
`voice.txt` podía tener BOM UTF-8, apareciendo como `ï»¿Sohee`.

Solución:
Los scripts escriben `voice.txt` como UTF-8 sin BOM y el diagnóstico verifica:
- `has_bom=False`
- `value=[Sohee]`
- `/voices/current={"voice":"Sohee"}`

## Logs
Ruta única:
`D:\RITXI\logs`

Logs importantes:
- `ahootsa_ps_*.log`
- `ahootsa_ps_events_*.jsonl`
- `ahootsa_realtime_ollama_v5_0_20.log`
- `ahootsa_5_mujoco_daemon_*.log`
- diagnósticos de voz y conversación.

## Criterio de estabilidad
Si oye audio pero no responde tras varias interacciones:
1. Ejecutar `DIAGNOSTICAR_5_CONVERSACION_FLUIDA.ps1`.
2. Si la sesión parece viva pero no responde, ejecutar `REINICIAR_5_SESION_CONVERSACION.ps1`.
3. Revisar logs recientes de `ahootsa_realtime_ollama_v5_0_20.log`.


## Cambios 5.0.21
Para mejorar la fluidez se reduce la lista de herramientas cargadas por defecto.

Herramientas activas por defecto:
- actividades de comunicación modernas;
- Memory;
- emociones básicas;
- movimiento básico;
- cámara;
- estado/cancelación de tareas.

Herramientas no cargadas por defecto:
- ask_ollama;
- bailes comunitarios;
- listados globales;
- variantes duplicadas antiguas de actividades;
- remember/forget.

Motivo:
cada herramienta añade esquema y aumenta la carga del backend realtime. Menos herramientas favorecen respuestas más rápidas y menos silencios.


## Cambios 5.0.23
La conversación no depende solo de que `/mic` esté en `muted=false`.
También necesita que `/status` indique `backend_connected=true`.

Si aparece:
- `backend_connected=false`
- `backend_connection_state=connecting`

entonces el micro puede estar disponible localmente, pero la sesión realtime no está lista para escuchar/responder.

Se añade:
- `ESPERAR_5_BACKEND_REALTIME_LISTO.ps1`
- diagnóstico mejorado de conversación;
- diagnóstico de conectividad Hugging Face;
- reinicio de sesión que espera backend realtime.
