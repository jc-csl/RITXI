# ARQUITECTURA Y FUNCIONALIDAD — AHOOTSA 0.12.8.1

## Arquitectura principal

```text
reachy_mini_conversation_app
  conversación, audio, modelo realtime, voz, movimientos y herramientas

ahootsa_local_server
  personas, perfiles, actividades, sesiones, eventos, panel e informes
```

El directorio oficial `reachy_mini_conversation_app/src` no se modifica.

## Puertos

```text
8000  Reachy Mini daemon y MuJoCo
8100  Ahootsa Local Server y panel profesional
7860  Reachy Mini Conversation App
```

## Flujo de arranque

```text
INICIAR_AHOOTSA.ps1
→ limpiar puertos y procesos
→ iniciar 8100
→ iniciar 8000
→ abrir panel
→ detectar o esperar sesión
→ iniciar 7860
→ comprobar servicios
```

## Modos

### Sesión identificada

```text
persona + actividad + nivel
→ perfil ahootsa_session
→ log dentro de session_XXXXXX
→ informe PDF, HTML, JSON y TXT
```

### Conversación anónima

```text
sin identificación
→ perfil ahootsa
→ log técnico anónimo
→ sin informe personal
```

## Finalización

`FINALIZAR_SESION_AHOOTSA.ps1` es el cierre operativo principal.

El panel también puede finalizar. Se utilizan archivos marcadores para que
solo un componente genere el informe y no exista una doble finalización.

## Scripts

Solo cuatro scripts quedan visibles en la raíz. Los lanzadores técnicos se
mantienen dentro de `scripts` porque el panel necesita rutas estables para
arrancar el daemon y la Conversation App.

## Datos

La limpieza de procesos no elimina:

- base de datos SQLite;
- usuarios;
- perfiles;
- sesiones;
- informes;
- logs;
- actividades.


## Procedimiento de actualización

La carpeta `payload` pertenece exclusivamente al paquete de actualización.
Nunca debe copiarse ni ejecutarse manualmente desde la raíz del proyecto.

El único punto de entrada de instalación es:

```text
APLICAR_UPDATE_12_8_1.ps1
```

La estructura final operativa no contiene una carpeta `payload` en
`D:\RITXI\AHOOTSA8`.
