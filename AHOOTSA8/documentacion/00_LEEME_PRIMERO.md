# AHOOTSA8 - Documentación principal

**Estado documentado:** Ahootsa Local Server 0.12.8.2  
**Fecha:** 5 de agosto de 2026  
**Sistema objetivo:** Windows 10/11, PowerShell y Python 3.12  
**Ruta recomendada:** `D:\RITXI\AHOOTSA8`

Esta carpeta sustituye la documentación histórica dispersa por un conjunto
reducido de manuales operativos.

## Orden de lectura

1. `01_MANUAL_INSTALACION_PC_NUEVO.md`
2. `02_CONFIGURACION_AHOOTSA.md`
3. `03_PUESTA_EN_MARCHA_Y_OPERACION.md`
4. `04_ARQUITECTURA_Y_FUNCIONALIDAD.md`
5. `05_MANTENIMIENTO_DIAGNOSTICO_Y_BACKUP.md`
6. `06_CONTEXTO_PARA_AGENTE_IA_CHATGPT.md`
7. `07_CHECKLIST_INSTALACION_Y_VALIDACION.md`
8. `08_ESTADO_VERSIONES_Y_REFERENCIAS.md`

También se incluye `MANUAL_COMPLETO_AHOOTSA8.docx`, que reúne el contenido
principal en un único documento imprimible.

## Comandos operativos

### Conversación anónima

```powershell
cd D:\RITXI\AHOOTSA8
.\INICIAR_AHOOTSA_ANONIMO.ps1
```

No utiliza el servidor local ni el panel y no genera un informe personal.

### Sesión identificada

```powershell
cd D:\RITXI\AHOOTSA8
.\INICIAR_AHOOTSA_SESION.ps1
```

Inicia el servidor local, el daemon y el panel. La conversación se inicia desde
el panel después de preparar la persona, la actividad y el nivel.

### Finalización

```powershell
.\FINALIZAR_SESION_AHOOTSA.ps1
```

Para finalizar y detener también todos los servicios:

```powershell
.\FINALIZAR_SESION_AHOOTSA.ps1 -DetenerTodo
```

### Diagnóstico y limpieza

```powershell
.\COMPROBAR_AHOOTSA.ps1
.\LIMPIAR_PROCESOS_AHOOTSA.ps1
```

## Principios que no deben cambiarse sin una actualización específica

- La aplicación oficial es el motor principal de conversación.
- No se modifica `reachy_mini_conversation_app\src`.
- Ahootsa se amplía mediante `external_content`, herramientas externas y el
  servidor local.
- El modo anónimo usa el perfil general `ahootsa`.
- Las sesiones identificadas usan `ahootsa_session`.
- El profesional conserva el control de la evaluación y del cambio de nivel.
- Ahootsa no realiza diagnósticos clínicos.
- Los puertos son 8000, 8100 y 7860.

## Fuentes verificadas

Documentación revisada el 5 de agosto de 2026:

- Repositorio del proyecto: https://github.com/jc-csl/RITXI
- Carpeta actual `AHOOTSA8`: https://github.com/jc-csl/RITXI/tree/main/AHOOTSA8
- Aplicación oficial incluida en el proyecto:
  https://github.com/jc-csl/RITXI/tree/main/AHOOTSA8/reachy_mini_conversation_app
- Aplicación oficial de Pollen Robotics:
  https://github.com/pollen-robotics/reachy_mini_conversation_app
- SDK Reachy Mini:
  https://github.com/pollen-robotics/reachy_mini
- Instalación oficial de `uv`:
  https://docs.astral.sh/uv/getting-started/installation/

La instalación descrita utiliza las versiones fijadas por el repositorio
AHOOTSA8. No debe sustituirse automáticamente por la última versión del
repositorio oficial de Pollen Robotics.
