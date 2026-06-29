## Novedad v0.4.32

Corrige el fallo del servidor Memory al importar el módulo:

```text
AttributeError: 'NoneType' object has no attribute '__dict__'
```

La solución elimina `@dataclass` del servidor y mantiene `start_server()`.

## Novedad v0.4.32

Corrige el fallo del juego Memory:

```text
AttributeError: module 'ahootsa_memory_pairs_game_server' has no attribute 'start_server'
```

Scripts nuevos:

```text
REPARAR_MEMORY_START_SERVER.ps1
PROBAR_MEMORY_START_SERVER.ps1
```

## Novedad v0.4.32

Esta versión mejora el diseño visual del juego Memory: dorso azul homogéneo con números grandes, cartas más visuales y estilo más cercano a un Memory infantil.

# Ahootsa Realtime Ollama v0.4.32

Base estable portable con documento completo de instalación desde cero.

Instalación rápida en una máquina nueva, desde la raíz de esta carpeta:

```powershell
powershell -ExecutionPolicy Bypass -File .\INSTALAR_AHOOTSA_COMPLETO.ps1
```

Documentación principal:

```text
docs/INSTALACION_DESDE_CERO.md
docs/CREAR_MODELO_OLLAMA_DESDE_CERO.md
docs/ARQUITECTURA_FUNCIONALIDAD.md
docs/ARQUITECTURA_BASE_ESTABLE_ASK_OLLAMA.md
```

Esta versión mantiene:

```text
- app oficial intacta
- herramientas originales del robot
- perfil Ahootsa en español
- ask_ollama como única herramienta nueva
- creación completa del modelo ahootsa-local:latest
```


## Diagnóstico ask_ollama

Si la app no responde al pedir IA local:

```powershell
powershell -ExecutionPolicy Bypass -File .\DIAGNOSTICAR_ASK_OLLAMA.ps1
```

Log:

```text
%LOCALAPPDATA%\Reachy Mini Control\ahootsa_logs\ask_ollama.log
```


## Reparar perfil ask_ollama

Si el diagnóstico dice que no encuentra `ask_ollama.py` en perfiles de Desktop:

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_PERFIL_ASK_OLLAMA.ps1
```


## v0.4.32

Esta versión fuerza el perfil Ahootsa al arranque:

```text
REACHY_MINI_CUSTOM_PROFILE=ahootsa_realtime_es
```

y copia el perfil a las rutas donde la app oficial puede cargar herramientas al iniciar.

Después de instalar:

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_PERFIL_ASK_OLLAMA.ps1
powershell -ExecutionPolicy Bypass -File .\DIAGNOSTICAR_ASK_OLLAMA.ps1
```


## v0.4.32

Esta versión corrige instalación incompleta en el Python embebido de Desktop.

Ejecutar con Reachy Mini Desktop cerrado:

```powershell
powershell -ExecutionPolicy Bypass -File .\INSTALAR_AHOOTSA_COMPLETO.ps1
```

Al final debe mostrar `version= 0.4.15` en los Python internos.


## v0.4.32

Corrige el error de `ollama create` por sintaxis incorrecta del `Modelfile`.

Para recrear solo el modelo:

```powershell
powershell -ExecutionPolicy Bypass -File .\RECREAR_MODELO_OLLAMA_AHOOTSA.ps1
```

Para instalación completa:

```powershell
powershell -ExecutionPolicy Bypass -File .\INSTALAR_AHOOTSA_COMPLETO.ps1
```


## v0.4.32 — Integración en Desktop

La app debe usarse desde Reachy Mini Desktop.  
No hace falta abrir `http://127.0.0.1:7860` en otra ventana.

Flujo recomendado:

```text
Reachy Mini Desktop → Applications → Ahootsa Realtime Ollama → Start
```

El panel de voz debe aparecer integrado a la derecha, igual que en la app oficial.

`http://127.0.0.1:7860` queda solo como prueba técnica si algo no carga.

También se ajusta `ask_ollama` para respuestas más breves y adecuadas para voz.


## v0.4.32 — Cámara PC en simulación

Se añade una herramienta nueva `camera_pc` para usar la webcam del ordenador en modo SIM.

La herramienta oficial `camera` no se modifica.

Scripts añadidos:

```text
INSTALAR_CAMARA_PC.ps1
PROBAR_CAMARA_PC.ps1
```

Prueba:

```powershell
powershell -ExecutionPolicy Bypass -File .\PROBAR_CAMARA_PC.ps1
```


## v0.4.32 — Reparar panel integrado de Desktop

Si Ahootsa aparece en verde como `App Running`, pero Desktop sigue mostrando `Applications`, ejecuta con Desktop cerrado:

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_PANEL_INTEGRADO_DESKTOP.ps1
```

Esta corrección cambia la URL embebida de `0.0.0.0:7860` a `localhost:7860`.


## v0.4.32 — Voz más natural

Voz por defecto del perfil Ahootsa:

```text
Coral
```

Cambiar voz:

```powershell
powershell -ExecutionPolicy Bypass -File .\CAMBIAR_VOZ_AHOOTSA.ps1
```

Ver voz activa:

```powershell
powershell -ExecutionPolicy Bypass -File .\VER_VOZ_AHOOTSA.ps1
```


## v0.4.32 — Emociones con sonido y movimiento

Se añade un `play_emotion.py` propio en el perfil Ahootsa.

No modifica la app original.  
Solo hace que, en Ahootsa, `play_emotion` intente reproducir movimiento + sonido OGG oficial.

Diagnóstico:

```powershell
powershell -ExecutionPolicy Bypass -File .\DIAGNOSTICAR_EMOCIONES_AUDIO.ps1
```


## v0.4.32 — Emociones con audio sin GStreamer

El sonido de las emociones de Ahootsa usa pygame/SDL para evitar errores `GstWasapi2Sink Failed to write to device`.

Scripts:

```text
INSTALAR_AUDIO_EMOCIONES_PYGAME.ps1
PROBAR_AUDIO_EMOCION_PYGAME.ps1
```


## v0.4.32 — Juego de parejas de animales

Nueva actividad guiada por el robot:

```text
Juego de parejas de animales
```

Incluye:

```text
- HTML + JavaScript autocontenido.
- Puerto local http://localhost:7870
- 8 parejas / 16 cartas.
- Cartas numeradas.
- Control por voz mediante el robot.
```

Herramientas añadidas:

```text
start_memory_pairs_game
choose_memory_cards
reset_memory_pairs_game
memory_pairs_game_status
```

Prueba sin Desktop:

```powershell
powershell -ExecutionPolicy Bypass -File .\PROBAR_JUEGO_PAREJAS_ANIMALES.ps1
```


## v0.4.32 — Corrección HTML del juego

Si aparece `No se encontró el HTML del juego`, ejecutar:

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_HTML_JUEGO_PAREJAS.ps1
```

La versión v0.4.32 instala el HTML también dentro del perfil Ahootsa.


## v0.4.32 — Motor JSON de juegos de parejas

Se añaden tres juegos:

```text
animales
ciudades
alimentos
```

Los contenidos están en archivos JSON:

```text
animales.json
ciudades.json
alimentos.json
```

Prueba:

```powershell
powershell -ExecutionPolicy Bypass -File .\PROBAR_JUEGOS_PAREJAS_JSON.ps1
```


## v0.4.32 — Juegos visuales simples

Los juegos de parejas ahora tienen:

```text
- 4 parejas / 8 cartas
- cartas grandes
- número grande en el dorso
- pantalla solo con cartas
```

El robot lleva las instrucciones, los ánimos, los aciertos y el final.


## v0.4.32 — Memory visual con ritmo del robot

```text
- Dorso azul.
- Número blanco grande.
- Solo cartas en pantalla.
- Si no acierta, las cartas quedan visibles 3 segundos.
- El robot puede dar pistas con hint_memory_pairs_game.
```
