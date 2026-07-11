# 00 — Índice y lectura rápida

## 1. Documentos de la carpeta

```text
README.md
00_INDICE_Y_LECTURA_RAPIDA.md
01_INSTALACION_EQUIPO_NUEVO.md
02_ARQUITECTURA_GENERAL.md
03_APP_OFICIAL_REACHY_Y_AHOOTSA.md
04_MODELO_CONVERSACIONAL_HUGGINGFACE_Y_OLLAMA.md
05_FLUJOS_COMUNICACION_Y_PUERTOS.md
06_CONFIGURACION_PERFILES_VARIABLES.md
07_HERRAMIENTAS_ACTIVIDADES_MEMORY_CAMARA_AUDIO.md
08_LOGS_DIAGNOSTICO_Y_DEPURACION.md
09_MODIFICAR_CODIGO_Y_MANTENIMIENTO.md
10_VERSIONES_LIMPIEZA_Y_MIGRACION.md
11_ESTADO_ACTUAL_7_0_19_Y_PRUEBAS.md
99_FUENTES_REVISADAS_Y_DUPLICADOS.md
assets/Reachy mini datasheet.pdf
```

## 2. Estado actual resumido

La versión funcional más reciente documentada es:

```text
7.0.19
```

Puntos comprobados:

```text
- Ahootsa instala como paquete propio en apps_venv.
- Entry point activo: ahootsa_realtime_ollama_app.
- Daemon MuJoCo arranca en 127.0.0.1:8000.
- Interfaz Ahootsa arranca en 127.0.0.1:7860.
- Panel principal: http://127.0.0.1:7860/ahootsa.
- Juego de parejas: http://127.0.0.1:7860/memory/page.
- Estado Memory: http://127.0.0.1:7860/memory/state.
- Herramientas Ahootsa cargan desde el perfil externo.
- Recursos dance1, dance2, dance3, welcoming2, success1, calming1 y electric1 existen con .json y .ogg.
- Los bailes ya se reproducen desde panel/prueba directa.
```

Pendiente o a vigilar:

```text
- Confirmar en cada prueba si Hugging Face llama correctamente a las herramientas por voz.
- Corregir definitivamente los logs con caracteres NUL en diagnósticos.
- Reducir los 404 iniciales producidos por sondeos antes de que la app termine de arrancar.
- Seguir puliendo interfaz del juego de parejas dentro del iframe.
```

## 3. Comandos básicos actuales

Instalación limpia de 7.0.19:

```powershell
cd D:\RITXI\7_0_19_ahootsa_base_endpoint_alias_voz_fix
powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_7_0_19.ps1 -ForceInstall -RestartDaemon
```

Ejecución normal:

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_7_0_19.ps1
```

Diagnóstico directo:

```powershell
powershell -ExecutionPolicy Bypass -File .\DIAGNOSTICAR_HERRAMIENTAS_DIRECTO_7_0_19.ps1
```

Traza de voz:

```powershell
powershell -ExecutionPolicy Bypass -File .\TRAZAR_PRUEBA_VOZ_AHOOTSA_7_0_19.ps1 -Seconds 120
```

Frases de prueba recomendadas:

```text
lista de bailes
haz baile uno
haz baile dos
haz baile tres
haz un saludo
abre juego de parejas
```

## 4. Regla de oro

No copiar herramientas Ahootsa dentro de paquetes oficiales como:

```text
reachy_mini_conversation_app/tools
reachy_talk_data/tools
```

Ahootsa debe usar rutas externas:

```text
ahootsa_realtime_ollama_desktop_app/profiles
ahootsa_realtime_ollama_desktop_app/tools
```

Excepción importante:

```text
play_emotion.py de Ahootsa vive dentro del perfil:
profiles/ahootsa7_realtime_es/play_emotion.py
```

No debe existir como:

```text
tools/play_emotion.py
```

porque podría colisionar con la herramienta oficial de Reachy.
