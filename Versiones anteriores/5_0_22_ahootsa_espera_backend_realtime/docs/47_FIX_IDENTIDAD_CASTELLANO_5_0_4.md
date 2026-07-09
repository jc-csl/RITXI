# Fix 5_0_4: identidad Ahootsa y castellano

## Problema

En modo daemon web, la app puede arrancar usando valores por defecto del motor oficial:

```text
Hi, I'm Reachy Mini
```

o responder en inglés.

## Causa probable

El motor interno puede cargar `profile=default` o variables por defecto antes de aplicar completamente el perfil Ahootsa.

En los logs anteriores se veía que Ahootsa arrancaba como app, pero después cargaba el perfil `default` y el backend realtime de Hugging Face.

## Solución 5.0.4

Esta versión refuerza tres capas:

1. Perfil:
   - `instructions.txt` dice de forma obligatoria que el nombre es Ahootsa.
   - `greeting.txt` queda en castellano.
   - `voice.txt` queda en Sohee.

2. Instalación:
   - copia Ahootsa sobre `ahootsa_realtime_es`;
   - copia Ahootsa sobre `default`;
   - copia Ahootsa sobre `starter_profile`;
   - copia también en `external_content/external_profiles`.

3. Variables:
   - crea `.env`;
   - fija variables de usuario;
   - fija variables de proceso en el launcher.

## Comandos

```powershell
cd D:\RITXI\5_0_4_ahootsa_mujoco_web_identidad_castellano_fix
powershell -ExecutionPolicy Bypass -File .\INSTALAR_5_AHOOTSA_MUJOCO_WEB.ps1
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_AHOOTSA_MUJOCO_WEB.ps1
```

## Comprobación

```powershell
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_5_AHOOTSA_MUJOCO_WEB.ps1
```

Debe aparecer:

```text
instructions dice Ahootsa = True
instructions no Reachy Mini = True
instructions castellano = True
tools ask_ollama = True
tools actividades = True
```

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
