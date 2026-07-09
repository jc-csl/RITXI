# Fix 5_0_3: la app arrancaba con profile=default

## Qué se ha observado en el log

El modo MuJoCo web arranca bien:

```text
Daemon started successfully.
Uvicorn running on http://127.0.0.1:8000
App ahootsa_realtime_ollama_app is running
Uvicorn running on http://localhost:7860
```

Pero después la app carga herramientas desde:

```text
Loading tools for profile: default
```

Eso provoca que no aparezcan herramientas nuevas de Ahootsa, por ejemplo:

```text
actividades_comunicacion
ask_ollama
camera_pc
```

## Solución

En 5.0.3 el instalador copia el perfil Ahootsa no solo a:

```text
profiles/ahootsa_realtime_es
```

sino también a los perfiles fallback:

```text
reachy_mini_conversation_app/profiles/default
reachy_mini_conversation_app/profiles/starter_profile
reachy_talk_data/profiles/default
reachy_talk_data/profiles/starter_profile
```

Así, aunque la app diga:

```text
Loading tools for profile: default
```

cargará realmente el `tools.txt` y las herramientas de Ahootsa.

## Comando

```powershell
powershell -ExecutionPolicy Bypass -File .\INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1
```

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
