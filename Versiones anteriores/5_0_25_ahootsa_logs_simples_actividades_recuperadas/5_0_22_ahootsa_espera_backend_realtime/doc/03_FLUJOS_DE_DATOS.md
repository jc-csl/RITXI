# 03 — Flujos de datos

## Flujo general de conversación

```text
Usuario habla
  ↓
Reachy Mini Desktop / app oficial de conversación
  ↓
Perfil Ahootsa: instructions.txt + greeting.txt + voice.txt + tools.txt
  ↓
Herramientas Ahootsa
  ├─ ask_ollama.py → Ollama local
  ├─ camera_pc.py → webcam del PC en simulación
  ├─ play_emotion.py → emociones/movimiento/sonido
  └─ herramientas Memory → juego de parejas
```

## Flujo con Ollama

```text
Usuario pregunta algo
  ↓
Modelo decide usar ask_ollama
  ↓
ask_ollama.py llama a Ollama local
  ↓
Ollama responde usando el modelo ahootsa-local:latest
  ↓
Reachy habla la respuesta
```

Configuración relacionada:

```text
ask_ollama.py
instructions.txt
RECREAR_MODELO_OLLAMA_AHOOTSA.ps1
```

## Flujo del juego Memory

```text
Usuario: "quiero el juego de animales"
  ↓
start_memory_pairs_game.py
  ↓
memory_pairs_game_server.py
  ↓
http://localhost:7870/
  ↓
HTML visual con cartas azules
```

Después:

```text
Usuario: "uno y siete"
  ↓
Reachy dice: "Vamos a ver la uno y la siete"
  ↓
choose_memory_cards.py espera un poco
  ↓
memory_pairs_game_server.py gira las cartas
  ↓
HTML muestra cartas
  ↓
choose_memory_cards.py espera un poco
  ↓
Reachy reacciona una sola vez
```

Si falla:

```text
cartas visibles 4 segundos
  ↓
vuelven a ocultarse solas
```

Si acierta:

```text
cartas quedan visibles
  ↓
Reachy felicita
```

Al terminar:

```text
última pareja encontrada
  ↓
Reachy celebra
  ↓
espera unos segundos
  ↓
reset_current_game()
  ↓
pregunta si quiere jugar otra vez o hacer otra actividad
```

## Flujo de archivos JSON del juego

```text
animales.json
ciudades.json
alimentos.json
  ↓
memory_pairs_game_server.py carga el JSON
  ↓
crea 8 cartas: 4 parejas
  ↓
HTML muestra las cartas
```

## Flujo de voz y saludo

```text
voice.txt → voz elegida
greeting.txt → saludo inicial
instructions.txt → idioma, identidad y comportamiento
```

Valores actuales:

```text
voice.txt = Sohee
greeting.txt = saludo en castellano como Ahootsa
```

---

## Actualización 5_0: modo MuJoCo web sin Desktop

Esta documentación pertenece ahora al paquete `5_0_ahootsa_mujoco_web_sin_desktop`.

Modo recomendado para esta versión:

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1
```

Reglas de uso:

```text
- No abrir Reachy Mini Desktop en este modo.
- Usar el panel web http://127.0.0.1:8000.
- Mantener ON solo ahotsa_realtime_ollama_app.
- Mantener OFF reachy_mini_conversation_app.
```

Documentos principales añadidos:

```text
39_MODO_MUJOCO_WEB_SIN_DESKTOP_5_0.md
40_COMANDOS_5_AHOOTSA_MUJOCO_WEB.md
41_API_REST_USADA_5_AHOOTSA_MUJOCO_WEB.md
42_NO_USAR_DESKTOP_EN_MODO_MUJOCO_WEB.md
43_CHANGELOG_5_0.md
```

<!-- AHOOTSA_DOC_UPDATED_5_0 -->

---

## Actualización 5_0_1: fix rutas con espacios

Se corrige el error de PowerShell provocado por la ruta:

```text
Reachy Mini Control
```

El script principal `LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1` ahora genera un `.ps1` temporal y llama al daemon mediante variable, no mediante una cadena inline.

Documento nuevo:

```text
44_FIX_RUTAS_CON_ESPACIOS_5_0_1.md
```

<!-- AHOOTSA_DOC_UPDATED_5_0_1 -->

---

## Actualización 5_0_2: limpieza de scripts antiguos

Se han eliminado scripts anteriores que ya no son necesarios para el modo actual.

Scripts actuales:

```text
INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1
LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1
LANZAR_SOLO_DAEMON_5_MUJOCO.ps1
PARAR_5_AHOOTSA_MUJOCO_WEB.ps1
test\DIAGNOSTICAR_5_AHOOTSA_MUJOCO_WEB.ps1
```

Documento nuevo:

```text
45_LIMPIEZA_SCRIPTS_5_0_2.md
```

<!-- AHOOTSA_DOC_UPDATED_5_0_2 -->

---

## Actualización 5_0_3: fix profile=default

En modo daemon web, el log puede mostrar:

```text
Loading tools for profile: default
```

Desde 5.0.3, `INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1` copia el perfil Ahootsa también sobre `default` y `starter_profile`, para que las herramientas de Ahootsa carguen aunque el motor interno use el perfil `default`.

Documento nuevo:

```text
46_FIX_PROFILE_DEFAULT_5_0_3.md
```

<!-- AHOOTSA_DOC_UPDATED_5_0_3 -->

---

## Actualización 5_0_4: identidad Ahootsa y castellano

Se corrige el caso en que la app arranca diciendo que es Reachy Mini o hablando en inglés.

Cambios:
- greeting en castellano;
- instrucciones reforzadas;
- perfil copiado también sobre `default`, `starter_profile` y `external_content/external_profiles`;
- `.env` con identidad Ahootsa;
- variables de proceso en el launcher;
- runtime copy activado en `main.py`.

Documento nuevo:

```text
47_FIX_IDENTIDAD_CASTELLANO_5_0_4.md
```

<!-- AHOOTSA_DOC_UPDATED_5_0_4 -->

---

## Actualización 5_0_5: reinstalación del módulo Python de Ahootsa

Se corrige el error:

```text
No module named 'ahootsa_realtime_ollama_desktop_app'
```

El instalador copia el módulo Python a `apps_venv\Lib\site-packages`, crea un `.pth` y verifica `IMPORT_OK`.

Documento nuevo:

```text
48_FIX_MODULO_APP_NO_IMPORTABLE_5_0_5.md
```

<!-- AHOOTSA_DOC_UPDATED_5_0_5 -->

---

## Actualizacion 5_0_6: instalador PowerShell 5.1 safe

Se corrige el error de parseo del instalador en Windows PowerShell:

```text
Token 'BLOQUE' inesperado
```

El instalador se ha reescrito con codificacion UTF-8 con BOM y cadenas seguras.

Documento nuevo:

```text
49_FIX_INSTALADOR_POWERSHELL51_5_0_6.md
```

<!-- AHOOTSA_DOC_UPDATED_5_0_6 -->

---

## Actualizacion 5_0_7: actividades directas sin bloqueo post-tool

Se corrige el bloqueo al iniciar una actividad de comunicacion. Las herramientas de actividades pasan de `needs_response = True` a `needs_response = False`, para que devuelvan la respuesta directamente sin esperar una segunda generacion del backend realtime.

Documento nuevo:

```text
50_FIX_ACTIVIDADES_DIRECTAS_5_0_7.md
```

<!-- AHOOTSA_DOC_UPDATED_5_0_7 -->
