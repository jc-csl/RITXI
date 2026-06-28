# Ahootsa Realtime Ollama v0.4.10 — Instalación desde cero en otra máquina

Este documento explica el proceso completo para instalar Ahootsa en un ordenador nuevo.

La regla de esta versión base es:

```text
Ahootsa = app oficial intacta + perfil Ahootsa + herramienta ask_ollama
```

No se modifican los recursos de la app oficial.

---

## 1. Qué se instala

En una máquina nueva hay que instalar tres piezas:

```text
1. Reachy Mini Desktop App
2. App oficial Reachy Mini Conversation App
3. Ahootsa Realtime Ollama
```

Además, para la IA local:

```text
4. Ollama
5. Modelo local ahootsa-local:latest
```

---

## 2. Qué NO hace Ahootsa

Ahootsa no debe sustituir ni modificar:

```text
- interfaz oficial
- micrófono oficial
- voz realtime oficial
- perfiles oficiales
- herramientas oficiales
- emociones oficiales
- bailes oficiales
- cámara
- memoria
- cola de movimientos
```

Las herramientas oficiales siguen siendo:

```text
dance
stop_dance
play_emotion
stop_emotion
camera
idle_do_nothing
move_head
sweep_look
remember
forget
```

Ahootsa solo añade:

```text
ask_ollama
```

---

## 3. Requisitos previos

### 3.1. Sistema

Recomendado:

```text
Windows 11
PowerShell
Conexión a Internet durante la primera instalación
```

### 3.2. Reachy Mini Desktop

Instalar Reachy Mini Desktop App.

Después:

```text
1. Abrir Reachy Mini Desktop App una vez.
2. Dejar que cree su carpeta interna:
   %LOCALAPPDATA%\Reachy Mini Control
3. Instalar o abrir la app oficial Reachy Mini Conversation App.
4. Cerrar Reachy Mini Desktop App antes de instalar Ahootsa.
```

La carpeta esperada es:

```powershell
$env:LOCALAPPDATA\Reachy Mini Control
```

### 3.3. Ollama

Instalar Ollama.

Comprobar en PowerShell:

```powershell
ollama list
```

Si `ollama list` no responde, abrir Ollama o reiniciar el servicio de Ollama.

---

## 4. Copiar Ahootsa a la máquina nueva

Descomprimir el ZIP en cualquier carpeta.

Ejemplos válidos:

```text
D:\RITXI\ahootsa_v0_4_10_base_instalacion_desde_cero
C:\Ahootsa\ahootsa_v0_4_10_base_instalacion_desde_cero
C:\Users\Alumno\Desktop\ahootsa_v0_4_10_base_instalacion_desde_cero
```

La instalación ya no depende de estar en `D:\RITXI`.

---

## 5. Instalación recomendada con un único PS1

Abrir PowerShell en la carpeta raíz de Ahootsa y ejecutar:

```powershell
.\INSTALAR_AHOOTSA_COMPLETO.ps1
```

Si Windows bloquea scripts, usar:

```powershell
powershell -ExecutionPolicy Bypass -File .\INSTALAR_AHOOTSA_COMPLETO.ps1
```

Ese script ejecuta todos los pasos:

```text
1. Comprueba Reachy Mini Desktop.
2. Comprueba los Python internos de Desktop.
3. Comprueba que la app oficial reachy_mini_conversation_app existe.
4. Comprueba Ollama.
5. Libera puertos 7860/7861/7862.
6. Limpia variables antiguas de emociones locales.
7. Crea/verifica el modelo ahootsa-local.
8. Instala Ahootsa en los Python internos de Desktop.
9. Registra la metadata para que aparezca en Applications.
10. Comprueba entry-points y API de Ollama.
```

---

## 6. Instalación manual paso a paso

Si se prefiere instalar paso a paso:

```powershell
cd C:\RUTA\A\ahootsa_v0_4_10_base_instalacion_desde_cero

.\scripts\windows\08_liberar_puertos_ahootsa.ps1
.\scripts\windows\04_limpiar_variables_emociones_locales.ps1
.\scripts\windows\00_crear_modelo_ollama_ahootsa.ps1
.\scripts\windows\01_instalar_ahootsa_realtime_ollama_en_desktop.ps1
.\scripts\windows\05_instalar_metadata_desktop.ps1
.\scripts\windows\02_comprobar_ahootsa_realtime_ollama.ps1
.\scripts\windows\09_probar_ollama_api_ahootsa.ps1
```

---

## 7. Modelo Ollama creado

El instalador crea el modelo:

```text
ahootsa-local:latest
```

A partir del modelo base:

```text
hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF:latest
```

El `Modelfile` se guarda de forma portable en:

```powershell
$env:LOCALAPPDATA\Ahootsa\ollama_ahootsa\Modelfile
```

No depende de `D:\RITXI`.

---

## 8. Arranque después de instalar

Después de instalar:

```text
1. Abrir Reachy Mini Desktop App.
2. Ir a Applications.
3. Buscar Ahootsa Realtime Ollama.
4. Pulsar Start.
5. Abrir http://127.0.0.1:7860
```

---

## 9. Pruebas básicas

Primero probar herramientas originales:

```text
baila
saluda
haz una emoción alegre
mira a la izquierda
mueve la cabeza
para
```

Después probar Ollama local:

```text
usa la IA local para darme una actividad sencilla
consulta Ollama y dime quién eres
pregunta al modelo local una idea para practicar memoria
```

---

## 10. Cuándo se usa ask_ollama

`ask_ollama` no se activa por defecto para todo.

Se activa con órdenes explícitas:

```text
usa la IA local
consulta Ollama
pregunta al modelo local
usa ahootsa-local
hazlo con la IA local
```

No se usa para movimientos:

```text
baila                  → dance
saluda                 → play_emotion
mira a la izquierda    → move_head
usa la cámara          → camera
recuerda esto          → remember
```

---

## 11. Archivos importantes

```text
INSTALAR_AHOOTSA_COMPLETO.ps1
scripts/windows/00_INSTALACION_COMPLETA_DESDE_CERO.ps1
docs/INSTALACION_DESDE_CERO.md
docs/ARQUITECTURA_FUNCIONALIDAD.md
docs/ARQUITECTURA_BASE_ESTABLE_ASK_OLLAMA.md
```

---

## 12. Regla para futuras versiones

Cada nueva versión debe incluir siempre:

```text
1. Un instalador completo PS1.
2. Documentación de instalación desde cero.
3. Documentación de arquitectura y funcionalidad.
4. Separación clara entre IA remota y ask_ollama local.
```

El comando recomendado debe ser siempre:

```powershell
.\INSTALAR_AHOOTSA_COMPLETO.ps1
```
