# Puesta en marcha y operación diaria

## 1. Antes de empezar

1. Cerrar Reachy Mini Desktop Control.
2. Comprobar micrófono y altavoces.
3. Abrir PowerShell.
4. Ejecutar:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
cd D:\RITXI\AHOOTSA8
.\COMPROBAR_AHOOTSA.ps1
```

Si quedan procesos anteriores:

```powershell
.\LIMPIAR_PROCESOS_AHOOTSA.ps1
```

## 2. Elegir el modo correcto

### Modo anónimo

Usar cuando se desea una conversación general sin identificar a la persona:

```powershell
.\INICIAR_AHOOTSA_ANONIMO.ps1
```

Servicios:

```text
8000 daemon       activo
7860 conversación activa
8100 servidor     detenido
```

Características:

- perfil `ahootsa`;
- sin panel;
- sin usuario;
- sin sesión;
- sin informe personal;
- log técnico en `logs\anonymous`.

### Modo sesión local

Usar cuando el profesional necesita identificar a la persona y guardar una
sesión:

```powershell
.\INICIAR_AHOOTSA_SESION.ps1
```

El script:

1. cierra procesos anteriores;
2. inicia el servidor local 8100;
3. inicia el daemon y MuJoCo 8000;
4. abre el panel;
5. deja 7860 detenido hasta preparar la sesión.

Panel:

```text
http://127.0.0.1:8100/panel-12-8-5
```

## 3. Preparar una sesión

En el panel:

1. pulsar `Nuevo` o seleccionar una persona existente;
2. revisar o editar la ficha;
3. elegir actividad;
4. elegir nivel;
5. escribir el nombre del profesional;
6. pulsar `Preparar`;
7. pulsar `Iniciar conversación`.

La aplicación cambia al perfil `ahootsa_session` y abre:

```text
http://127.0.0.1:7860
```

## 4. Comprobar el saludo personalizado

Después de pulsar `Preparar`, puede revisarse antes de iniciar:

```powershell
Get-Content `
    D:\RITXI\AHOOTSA8\reachy_mini_conversation_app\external_content\external_profiles\ahootsa_session\greeting.txt `
    -Raw
```

El texto debe ordenar decir el nombre completo. Si la ficha contiene
intereses, también debe mencionarlos y ofrecer hablar de ellos.

## 5. Seguimiento durante la sesión

Utilizar las marcas profesionales cuando corresponda:

```text
Adecuada
Parcial
Incorrecta
Sin respuesta
Pista
Repetir
Ejemplo
```

Las marcas no se deducen clínicamente de la conversación. Son observaciones
del profesional.

## 6. Finalizar desde el panel

El botón de cierre debe:

```text
cerrar Conversation App
→ cerrar el log
→ importar turnos
→ finalizar sesión
→ generar informes
→ restaurar perfil ahootsa
→ liberar la siguiente sesión
```

## 7. Finalizar mediante script

Método operativo alternativo:

```powershell
cd D:\RITXI\AHOOTSA8
.\FINALIZAR_SESION_AHOOTSA.ps1
```

Para detener también servidor y daemon:

```powershell
.\FINALIZAR_SESION_AHOOTSA.ps1 -DetenerTodo
```

El script detecta si se trata de una conversación anónima o de una sesión
identificada.

## 8. Comprobar el resultado

```powershell
.\COMPROBAR_AHOOTSA.ps1
```

En una sesión terminada no debe quedar otra sesión activa ni un
`active_session.json` bloqueando la siguiente.

Última carpeta de sesión:

```powershell
$sesion = Get-ChildItem `
    D:\RITXI\AHOOTSA8\ahootsa_local_server\data\sessions `
    -Directory |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

$sesion.FullName
Get-ChildItem $sesion.FullName
```

## 9. Abrir el informe

```powershell
Start-Process "$($sesion.FullName)\informe_sesion.pdf"
```

## 10. Cierre de jornada

```powershell
.\LIMPIAR_PROCESOS_AHOOTSA.ps1
.\COMPROBAR_AHOOTSA.ps1
```

Los tres puertos deben aparecer libres.

## 11. Comportamiento esperado al terminar un baile

Al terminar la música y el movimiento, Aocha debe detener automáticamente el
baile y continuar hablando sin esperar una nueva intervención de la persona.

Respuesta esperada aproximada:

```text
Ya hemos terminado el baile. ¿Te ha gustado?
```

En el log debe aparecer:

```text
Ahootsa local dance completed and auto-stopped
status": "completed"
```

## 12. Advertencias normales en simulación

Pueden aparecer avisos como:

```text
No Reachy Mini Audio USB device found
using default audio source
Cannot change resolution of Mujoco simulated camera
```

En un PC sin el dispositivo de audio de Reachy estos avisos pueden ser
normales si la aplicación utiliza correctamente el micrófono y el altavoz
predeterminados del ordenador.

No son normales:

```text
puerto 8000 ocupado por otro daemon
servidor 8100 no responde
Conversation App 7860 no arranca
ModuleNotFoundError
ReportLab no instalado
otra sesión activa
```

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
