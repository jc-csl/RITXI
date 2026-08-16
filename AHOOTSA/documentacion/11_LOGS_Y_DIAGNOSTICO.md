# Logs y diagnóstico de AHOOTSA

Desde la versión 0.12.8.8, todas las conversaciones se registran en:

```text
D:\RITXI\AHOOTSA8\logs
```

## Modo anónimo

```text
logs\anonymous\anonymous_AAAAMMDD_HHMMSS
├── conversation_app.log
├── interacciones.txt
└── diagnostico.json
```

`logs\ULTIMO_ANONIMO.txt` contiene la ruta más reciente.

## Sesión identificada

```text
logs\sessions\session_000023
├── conversation_app.log
├── interacciones.txt
└── diagnostico.json
```

`logs\ULTIMA_SESION.txt` contiene la ruta más reciente.

El original para los informes continúa en:

```text
ahootsa_local_server\data\sessions\session_000023\conversation_app.log
```

## Archivos

- `conversation_app.log`: registro técnico completo.
- `interacciones.txt`: conversación final legible.
- `diagnostico.json`: perfil, voz, audio, errores, avisos, herramientas,
  latencias y posible bloqueo de escucha.

Los mensajes técnicos de herramientas se mantienen en el log completo, pero
no aparecen como conversación de Aocha en `interacciones.txt`.

## Privacidad

Los logs pueden contener nombres, intereses y la conversación completa.
Deben mantenerse en un equipo protegido.
