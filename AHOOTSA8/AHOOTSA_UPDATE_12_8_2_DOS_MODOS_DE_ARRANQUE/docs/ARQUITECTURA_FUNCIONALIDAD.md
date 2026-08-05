# ARQUITECTURA Y FUNCIONALIDAD — AHOOTSA 0.12.8.2

## Componentes

```text
reachy_mini_conversation_app
  conversación, audio, modelo realtime, voz y movimientos

ahootsa_local_server
  personas, perfiles, actividades, sesiones, eventos e informes
```

## Puertos

```text
8000 daemon y MuJoCo
8100 servidor local y panel
7860 Conversation App
```

## Arranque anónimo

```text
INICIAR_AHOOTSA_ANONIMO.ps1
→ limpiar procesos
→ iniciar 8000
→ usar perfil general ahootsa
→ iniciar 7860
```

El servidor 8100 permanece detenido. No existe usuario identificado ni
informe personal.

## Arranque de sesión local

```text
INICIAR_AHOOTSA_SESION.ps1
→ limpiar procesos
→ iniciar 8100
→ iniciar 8000
→ abrir panel
→ preparar persona, actividad y nivel
→ iniciar 7860 desde el panel
→ usar ahootsa_session
```

## Scripts visibles

```text
INICIAR_AHOOTSA_ANONIMO.ps1
INICIAR_AHOOTSA_SESION.ps1
FINALIZAR_SESION_AHOOTSA.ps1
COMPROBAR_AHOOTSA.ps1
LIMPIAR_PROCESOS_AHOOTSA.ps1
```

## Finalización

El finalizador detecta el modo:

- sin servidor ni `active_session.json`: cierre anónimo sin informe;
- con sesión local: cierre, importación y generación de PDF, HTML, JSON y TXT.
