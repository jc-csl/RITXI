# Ahootsa Realtime Ollama v0.4.21

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


## v0.4.21

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


## v0.4.21

Esta versión corrige instalación incompleta en el Python embebido de Desktop.

Ejecutar con Reachy Mini Desktop cerrado:

```powershell
powershell -ExecutionPolicy Bypass -File .\INSTALAR_AHOOTSA_COMPLETO.ps1
```

Al final debe mostrar `version= 0.4.15` en los Python internos.


## v0.4.21

Corrige el error de `ollama create` por sintaxis incorrecta del `Modelfile`.

Para recrear solo el modelo:

```powershell
powershell -ExecutionPolicy Bypass -File .\RECREAR_MODELO_OLLAMA_AHOOTSA.ps1
```

Para instalación completa:

```powershell
powershell -ExecutionPolicy Bypass -File .\INSTALAR_AHOOTSA_COMPLETO.ps1
```


## v0.4.21 — Integración en Desktop

La app debe usarse desde Reachy Mini Desktop.  
No hace falta abrir `http://127.0.0.1:7860` en otra ventana.

Flujo recomendado:

```text
Reachy Mini Desktop → Applications → Ahootsa Realtime Ollama → Start
```

El panel de voz debe aparecer integrado a la derecha, igual que en la app oficial.

`http://127.0.0.1:7860` queda solo como prueba técnica si algo no carga.

También se ajusta `ask_ollama` para respuestas más breves y adecuadas para voz.


## v0.4.21 — Cámara PC en simulación

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


## v0.4.21 — Reparar panel integrado de Desktop

Si Ahootsa aparece en verde como `App Running`, pero Desktop sigue mostrando `Applications`, ejecuta con Desktop cerrado:

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_PANEL_INTEGRADO_DESKTOP.ps1
```

Esta corrección cambia la URL embebida de `0.0.0.0:7860` a `localhost:7860`.


## v0.4.21 — Voz más natural

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


## v0.4.21 — Recuperar IA local

Si la app dice que no tiene IA local conectada, ejecuta:

```powershell
powershell -ExecutionPolicy Bypass -File .\PROBAR_IA_LOCAL_AHOOTSA.ps1
```

Frase de prueba dentro de Ahootsa:

```text
comprueba la IA local con ask_ollama
```

Esta versión refuerza que cualquier mención a IA local, Ollama o modelo local debe usar `ask_ollama`.
