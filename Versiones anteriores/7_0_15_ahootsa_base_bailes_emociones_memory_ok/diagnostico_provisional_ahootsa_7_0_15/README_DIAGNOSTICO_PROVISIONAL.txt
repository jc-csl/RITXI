DIAGNOSTICO PROVISIONAL AHOOTSA 7.0.15
======================================

Estos scripts NO modifican la instalación. Solo leen el estado, prueban endpoints y guardan logs con timestamp en:

D:\RITXI\logs

Uso recomendado:

1) Con Ahootsa 7.0.15 abierto, ejecuta:

powershell -ExecutionPolicy Bypass -File .\DIAGNOSTICO_PROVISIONAL_AHOOTSA_7_0_15.ps1 -DeepLogs

2) Para comprobar solo el juego de parejas integrado:

powershell -ExecutionPolicy Bypass -File .\PROBAR_MEMORY_ENDPOINTS_AHOOTSA_7_0_15.ps1

Si quieres reiniciar el tablero durante la prueba:

powershell -ExecutionPolicy Bypass -File .\PROBAR_MEMORY_ENDPOINTS_AHOOTSA_7_0_15.ps1 -Reset

3) Para hacer una prueba de voz controlada y capturar trazas:

powershell -ExecutionPolicy Bypass -File .\TRAZAR_PRUEBA_VOZ_AHOOTSA_7_0_15.ps1 -Seconds 120

Durante esa ventana di exactamente:
- lista de bailes
- haz baile dos
- haz un saludo
- abre juego de parejas

Después envía los ficheros generados:
- D:\RITXI\logs\AHOOTSA_DIAGNOSTICO_PROVISIONAL_YYYYMMDD_HHMMSS.log
- D:\RITXI\logs\AHOOTSA_MEMORY_ENDPOINTS_YYYYMMDD_HHMMSS.log
- D:\RITXI\logs\AHOOTSA_TRAZA_VOZ_YYYYMMDD_HHMMSS.log

Qué busca este diagnóstico:
- Si el perfil activo es realmente ahootsa7_realtime_es.
- Si el tools.txt activo contiene play_panel_dance_activity, list_panel_dances_activities y start_memory_pairs_game.
- Si el registro real de herramientas del motor oficial contiene las herramientas Ahootsa.
- Si dance2/dance3/welcoming2 existen en D:\RITXI\reachy-mini-emotions-library.
- Si los alias en español resuelven correctamente: baile dos => dance2, baile tres => dance3, saludo => welcoming2.
- Si /memory/page, /memory/state y /memory/games están vivos en el puerto 7860.
- Si hay residuos Ahootsa dentro de rutas oficiales que puedan provocar colisiones o confusión.
