# Ahootsa Reachy Mini Desktop Local v0.3.6

Esta versión añade dos apps locales a Reachy Mini Desktop:

- **Ahootsa!**: app clásica con perfil español y backend Hugging Face Hosted. Panel: `http://127.0.0.1:7860`
- **Ahootsa Ollama Local**: chat local por texto usando Ollama. Panel: `http://127.0.0.1:7862`

## Instalación rápida

Cierra primero **Reachy Mini Desktop App**.

```powershell
cd D:\RITXI\ahootsa_v0_3_6_ollama_chat_logging_fix
.\scripts\windows\08_liberar_puertos_ahootsa.ps1
.\scripts\windows\00_crear_modelo_ollama_ahootsa.ps1
.\scripts\windows\01_instalar_ahootsa_en_desktop_python.ps1
.\scripts\windows\05_instalar_metadata_ahootsa_desktop.ps1
```

Después abre Reachy Mini Desktop App y pulsa **Start** en **Ahootsa Ollama Local**.

Abre:

```text
http://127.0.0.1:7862
```

## Nota sobre v0.3.1

Si veías `{"detail":"Not Found"}` en `7861` y el log mostraba `WinError 10048`, había un proceso viejo usando ese puerto. Esta versión usa `7862` y añade un script para liberar puertos antiguos.


## Nota v0.3.3

Corrige el error `ModuleNotFoundError: No module named reachy_mini` cuando la Desktop arranca Ahootsa Ollama Local con su CPython interno. El chat local sigue en `http://127.0.0.1:7862`.


## v0.3.5 - reparación de rutas del chat Ollama

Esta versión corrige el caso en que `http://127.0.0.1:7862` devolvía `{"detail":"Not Found"}` y `/docs` aparecía sin operaciones.

La causa era que Reachy Mini Desktop podía arrancar un webserver vacío por defecto antes del servidor propio de Ahootsa. Ahora `AhootsaOllamaLocalApp` usa `dont_start_webserver=True` y registra sus rutas propias.

Instala con:

```powershell
cd D:\RITXI\ahootsa_v0_3_4_ollama_chat_ui_fix_routes
.\scripts\windows\08_liberar_puertos_ahootsa.ps1
.\scripts\windows\00_crear_modelo_ollama_ahootsa.ps1
.\scripts\windows\01_instalar_ahootsa_en_desktop_python.ps1
.\scripts\windows\05_instalar_metadata_ahootsa_desktop.ps1
```

Luego abre `http://127.0.0.1:7862`.


## Cambio v0.3.5

- La app Ollama acepta `ahootsa-local` y `ahootsa-local:latest`.
- Por defecto usa `ahootsa-local:latest`, que es el nombre que muestra `ollama list`.
- Corregido el script `08_liberar_puertos_ahootsa.ps1` por el error de variable `$Port:` en PowerShell.


## v0.3.6 - corrección /api/chat y logs

Corrige el error de FastAPI:

```text
{"detail":[{"type":"missing","loc":["query","req"],"msg":"Field required"}]}
```

Ahora `/api/chat` acepta JSON normal:

```json
{"message":"Hola"}
```

También crea un log por sesión en:

```text
%LOCALAPPDATA%\Reachy Mini Control\ahootsa_logs\ahootsa_ollama_YYYYMMDD_HHMMSS.log
```

Desde el panel puedes pulsar **Ver log**, o abrir:

```text
http://127.0.0.1:7862/api/log
```
