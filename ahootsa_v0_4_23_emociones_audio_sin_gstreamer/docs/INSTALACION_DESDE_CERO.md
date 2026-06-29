# Ahootsa Realtime Ollama — Instalación desde cero en una máquina nueva

**Versión:** v0.4.23 `base_instalacion_desde_cero_completa`  
**Objetivo:** instalar Ahootsa Realtime Ollama en un PC nuevo sin perder ningún paso.  
**Sistema objetivo:** Windows 11 + Reachy Mini Desktop + Ollama.

---

## 1. Qué se va a instalar

Ahootsa Realtime Ollama es una app adicional para Reachy Mini Desktop.

La arquitectura es:

```text
Reachy Mini Desktop
│
├─ App oficial Reachy Mini Conversation App
│  ├─ micrófono
│  ├─ voz realtime
│  ├─ perfiles
│  ├─ movimientos
│  ├─ emociones
│  ├─ bailes
│  ├─ cámara
│  └─ memoria
│
└─ Ahootsa Realtime Ollama
   ├─ usa la app oficial sin modificarla
   ├─ añade perfil Ahootsa en español
   ├─ mantiene herramientas originales
   └─ añade ask_ollama para consultar Ollama local
```

La versión base **no sustituye** la IA realtime remota de la app oficial.

La herramienta `ask_ollama` solo se usa cuando el usuario pide explícitamente:

```text
usa la IA local
consulta Ollama
pregunta al modelo local
usa ahootsa-local
hazlo con la IA local
```

---

## 2. Requisitos previos

Antes de instalar Ahootsa en un equipo nuevo hay que tener:

```text
1. Windows 11.
2. Reachy Mini Desktop App instalada.
3. App oficial Reachy Mini Conversation App instalada o descargada desde Desktop.
4. Ollama instalado.
5. Conexión a Internet al menos para descargar el modelo base una vez.
6. Carpeta de Ahootsa descomprimida en cualquier ruta local.
```

Ejemplo de ruta recomendada:

```powershell
D:\RITXI\ahootsa_v0_4_11_base_instalacion_desde_cero_completa
```

También puede estar en otra carpeta. El instalador debe funcionar desde la carpeta donde esté copiado.

---

## 3. Instalar Reachy Mini Desktop App

En una máquina nueva:

```text
1. Instala Reachy Mini Desktop App.
2. Ábrela una vez.
3. Comprueba que aparece el panel general.
4. Cierra Reachy Mini Desktop App.
```

Esto es importante porque la Desktop crea sus carpetas internas en:

```powershell
%LOCALAPPDATA%\Reachy Mini Control
```

Ruta típica:

```powershell
C:\Users\Alumno\AppData\Local\Reachy Mini Control
```

---

## 4. Instalar o preparar la app oficial

Ahootsa necesita que exista la app oficial de conversación.

Desde Reachy Mini Desktop:

```text
1. Abre Reachy Mini Desktop.
2. Ve a Applications.
3. Instala o descarga Reachy Mini Conversation App.
4. Arráncala al menos una vez si es posible.
5. Comprueba que abre su panel.
6. Cierra Reachy Mini Desktop.
```

La app oficial es la que aporta:

```text
micro
voz realtime
herramientas originales
emociones
bailes
cámara
memoria
```

Ahootsa no debe alterar estos recursos.

---

## 5. Instalar Ollama

Instala Ollama para Windows.

Después abre PowerShell y comprueba:

```powershell
ollama --version
```

También comprueba que el servicio responde:

```powershell
ollama list
```

En una máquina nueva puede aparecer una lista vacía. Eso es normal.

---

## 6. Modelo local usado por Ahootsa

Ahootsa usará este modelo local:

```text
ahootsa-local:latest
```

Ese modelo se crea a partir de este modelo base:

```text
hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest
```

La idea es:

```text
modelo base descargado con Ollama
→ archivo Modelfile con personalidad Ahootsa
→ modelo nuevo ahootsa-local:latest
```

---

## 7. Crear el modelo local manualmente

El instalador automático lo hace, pero estos son los pasos completos.

### 7.1. Comprobar modelos disponibles

En PowerShell:

```powershell
ollama list
```

Si `ahootsa-local:latest` no aparece, hay que crearlo.

---

### 7.2. Descargar el modelo base

Ejecuta:

```powershell
ollama pull hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest
```

Cuando termine, comprueba:

```powershell
ollama list
```

Debe aparecer algo parecido a:

```text
hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest
```

---

### 7.3. Crear carpeta local para el Modelfile

Ruta recomendada portable:

```powershell
$ModelDir = "$env:LOCALAPPDATA\Ahootsa\ollama_ahootsa"
New-Item -ItemType Directory -Force -Path $ModelDir | Out-Null
```

Esa ruta normalmente será:

```powershell
C:\Users\Alumno\AppData\Local\Ahootsa\ollama_ahootsa
```

---

### 7.4. Crear el archivo Modelfile

Crea el archivo:

```powershell
$Modelfile = Join-Path $ModelDir "Modelfile"
```

Contenido recomendado:

```powershell
@'
FROM hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest

PARAMETER temperature 0.6
PARAMETER top_p 0.9
PARAMETER num_ctx 2048

SYSTEM """
Eres Ahootsa, un asistente educativo amable, claro y paciente.
Respondes siempre en español.
Usas frases cortas.
Das instrucciones sencillas.
Eres positivo y animas al usuario.
No dices que eres ChatGPT.
No controlas directamente el robot.
Si te consultan desde Reachy Mini, ayudas con explicaciones, ideas, actividades y reformulaciones sencillas.
"""
'@ | Set-Content -Encoding UTF8 $Modelfile
```

Comprueba que existe:

```powershell
Get-Content $Modelfile
```

---

### 7.5. Crear el modelo Ahootsa

Ejecuta:

```powershell
ollama create ahootsa-local -f $Modelfile
```

Después comprueba:

```powershell
ollama list
```

Debe aparecer:

```text
ahootsa-local:latest
```

---

### 7.6. Probar el modelo local

Prueba rápida:

```powershell
ollama run ahootsa-local
```

Escribe:

```text
Hola, ¿quién eres?
```

Debe responder en español como Ahootsa.

Para salir de `ollama run`, usa:

```text
/bye
```

---

### 7.7. Probar la API local de Ollama

Ahootsa no usa `ollama run`, usa la API HTTP local.

Prueba:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:11434/api/chat" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{
    "model": "ahootsa-local:latest",
    "stream": false,
    "messages": [
      {
        "role": "user",
        "content": "Hola Ahootsa, ¿me respondes en español?"
      }
    ]
  }'
```

Debe devolver algo con:

```text
model: ahootsa-local:latest
message.content: ...
done: True
```

Si esto funciona, Ollama está preparado.

---

## 8. Instalación automática completa de Ahootsa

En la carpeta de Ahootsa hay un instalador único:

```powershell
INSTALAR_AHOOTSA_COMPLETO.ps1
```

Debe ejecutarse desde la raíz de la carpeta.

Ejemplo:

```powershell
cd D:\RITXI\ahootsa_v0_4_11_base_instalacion_desde_cero_completa
powershell -ExecutionPolicy Bypass -File .\INSTALAR_AHOOTSA_COMPLETO.ps1
```

También puede ejecutarse así si PowerShell permite scripts:

```powershell
.\INSTALAR_AHOOTSA_COMPLETO.ps1
```

---

## 9. Qué hace el instalador completo

El instalador completo debe realizar estos pasos:

```text
1. Comprobar que existe Reachy Mini Desktop.
2. Comprobar carpetas internas de Desktop.
3. Comprobar Python interno principal.
4. Comprobar apps_venv.
5. Comprobar que Ollama existe.
6. Descargar modelo base si falta.
7. Crear carpeta %LOCALAPPDATA%\Ahootsa\ollama_ahootsa.
8. Crear Modelfile.
9. Crear modelo ahootsa-local:latest.
10. Probar API de Ollama.
11. Limpiar variables antiguas de emociones locales.
12. Instalar Ahootsa en los Python internos de Desktop.
13. Crear metadata para que aparezca en Applications.
14. Mostrar resumen final.
```

---

## 10. Scripts internos disponibles

Además del instalador completo, existen scripts separados:

```text
scripts/windows/00_crear_modelo_ollama_ahootsa.ps1
scripts/windows/01_instalar_ahootsa_realtime_ollama_en_desktop.ps1
scripts/windows/04_limpiar_variables_emociones_locales.ps1
scripts/windows/05_instalar_metadata_desktop.ps1
scripts/windows/08_liberar_puertos_ahootsa.ps1
scripts/windows/09_probar_ollama_api_ahootsa.ps1
```

Uso manual equivalente:

```powershell
.\scripts\windows\08_liberar_puertos_ahootsa.ps1
.\scripts\windows\04_limpiar_variables_emociones_locales.ps1
.\scripts\windows\00_crear_modelo_ollama_ahootsa.ps1
.\scripts\windows\01_instalar_ahootsa_realtime_ollama_en_desktop.ps1
.\scripts\windows\05_instalar_metadata_desktop.ps1
.\scripts\windows\09_probar_ollama_api_ahootsa.ps1
```

---

## 11. Registrar la app en Reachy Mini Desktop

El script de metadata crea un archivo en:

```powershell
%LOCALAPPDATA%\Reachy Mini Control\.app_metadata
```

Archivo esperado:

```powershell
ahootsa_realtime_ollama_app.json
```

Ese archivo permite que Desktop muestre:

```text
Ahootsa Realtime Ollama
```

en la sección Applications.

Después de instalar:

```text
1. Cierra Reachy Mini Desktop.
2. Vuelve a abrir Reachy Mini Desktop.
3. Ve a Applications.
4. Busca Ahootsa Realtime Ollama.
5. Pulsa Start.
```

---

## 12. Probar Ahootsa

Cuando esté arrancada:

```text
1. Abre el panel de la app si Desktop no lo abre automáticamente.
2. Usa el perfil Ahootsa.
3. Prueba primero herramientas originales.
```

Pruebas recomendadas por voz:

```text
hola
baila
saluda
haz una emoción alegre
mira a la izquierda
mueve la cabeza
usa la cámara
recuerda que me gusta el color verde
```

Después prueba Ollama local:

```text
usa la IA local para darme una actividad sencilla
consulta Ollama y explícame qué eres
pregunta al modelo local una idea para practicar memoria
usa ahootsa-local para crear una pregunta fácil
```

---

## 13. Qué debe funcionar con IA remota

La IA remota de la app oficial sigue siendo responsable de:

```text
- escuchar por micrófono
- hablar con voz realtime
- decidir herramientas
- ejecutar bailes
- ejecutar emociones
- ejecutar movimientos
- usar cámara
- gestionar memoria
```

Ejemplos:

```text
baila                  → dance
saluda                 → play_emotion
mira a la izquierda    → move_head
usa la cámara          → camera
recuerda esto          → remember
olvida eso             → forget
```

---

## 14. Qué debe funcionar con Ollama local

Ollama local solo entra mediante:

```text
ask_ollama
```

Casos:

```text
usa la IA local...
consulta Ollama...
pregunta al modelo local...
usa ahootsa-local...
```

Ejemplo:

```text
Usuario: usa la IA local para darme una actividad sencilla.
→ IA remota llama a ask_ollama.
→ ask_ollama consulta ahootsa-local:latest.
→ Ahootsa dice la respuesta por voz.
```

No usar Ollama para:

```text
bailar
saludar
mover cabeza
cámara
recordar
olvidar
```

---

## 15. Comprobaciones si algo falla

### 15.1. Ollama no aparece

```powershell
ollama --version
ollama list
```

Si no funciona, reinstalar Ollama o abrir Ollama manualmente.

---

### 15.2. No existe `ahootsa-local:latest`

Ejecutar:

```powershell
.\scripts\windows\00_crear_modelo_ollama_ahootsa.ps1
```

O hacerlo manualmente con los pasos de este documento.

---

### 15.3. La API de Ollama no responde

Probar:

```powershell
Invoke-RestMethod http://127.0.0.1:11434/api/tags
```

Si falla, abrir Ollama o reiniciar Windows.

---

### 15.4. Ahootsa no aparece en Desktop

Ejecutar:

```powershell
.\scripts\windows\05_instalar_metadata_desktop.ps1
```

Cerrar y abrir Reachy Mini Desktop.

---

### 15.5. Ahootsa aparece pero no arranca

Ejecutar:

```powershell
.\scripts\windows\01_instalar_ahootsa_realtime_ollama_en_desktop.ps1
```

Cerrar y abrir Desktop.

---

### 15.6. Puerto ocupado

Ejecutar:

```powershell
.\scripts\windows\08_liberar_puertos_ahootsa.ps1
```

---

## 16. Lo que NO debe hacerse en esta base

No hacer en la base estable:

```text
No modificar la app oficial.
No modificar frontend estático.
No duplicar perfiles oficiales.
No usar JSON/OGG locales.
No llamar a media.play_sound.
No crear herramientas alternativas para dance o play_emotion.
No sustituir la IA realtime por Ollama.
```

---

## 17. Resumen de instalación desde cero

Orden completo:

```text
1. Instalar Reachy Mini Desktop.
2. Abrir Reachy Mini Desktop una vez.
3. Instalar/abrir la app oficial Reachy Mini Conversation App.
4. Cerrar Reachy Mini Desktop.
5. Instalar Ollama.
6. Comprobar ollama list.
7. Descomprimir Ahootsa.
8. Ejecutar INSTALAR_AHOOTSA_COMPLETO.ps1.
9. Confirmar que existe ahootsa-local:latest.
10. Abrir Reachy Mini Desktop.
11. Arrancar Ahootsa Realtime Ollama.
12. Probar herramientas originales.
13. Probar “usa la IA local...”.
```

Comando principal:

```powershell
cd RUTA_DE_AHOOTSA
powershell -ExecutionPolicy Bypass -File .\INSTALAR_AHOOTSA_COMPLETO.ps1
```


## Uso integrado en Reachy Mini Desktop

Ahootsa debe arrancarse desde Reachy Mini Desktop.

No hace falta abrir manualmente `http://127.0.0.1:7860` en otra ventana.

El puerto `7860` es interno. Desktop lo usa para incrustar la interfaz de voz en el panel derecho, igual que con la app oficial.

Solo abre `http://127.0.0.1:7860` si quieres hacer una prueba técnica o diagnóstico.


## v0.4.23 — Cámara PC en simulación

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


## v0.4.23 — Reparar panel integrado de Desktop

Si Ahootsa aparece en verde como `App Running`, pero Desktop sigue mostrando `Applications`, ejecuta con Desktop cerrado:

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_PANEL_INTEGRADO_DESKTOP.ps1
```

Esta corrección cambia la URL embebida de `0.0.0.0:7860` a `localhost:7860`.


## v0.4.23 — Voz más natural

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


## v0.4.23 — Emociones con sonido y movimiento

Se añade un `play_emotion.py` propio en el perfil Ahootsa.

No modifica la app original.  
Solo hace que, en Ahootsa, `play_emotion` intente reproducir movimiento + sonido OGG oficial.

Diagnóstico:

```powershell
powershell -ExecutionPolicy Bypass -File .\DIAGNOSTICAR_EMOCIONES_AUDIO.ps1
```


## v0.4.23 — Emociones con audio sin GStreamer

El sonido de las emociones de Ahootsa usa pygame/SDL para evitar errores `GstWasapi2Sink Failed to write to device`.

Scripts:

```text
INSTALAR_AUDIO_EMOCIONES_PYGAME.ps1
PROBAR_AUDIO_EMOCION_PYGAME.ps1
```
