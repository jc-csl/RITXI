# Ahootsa 6.1.1 — Local Ollama + audio navegador + SDK Reachy Mini sim

Rama limpia 6.x. No depende de `reachy_mini_conversation_app` ni de Hugging Face realtime.

## Cambios frente a 6.0.0

- Añadido panel de micrófono:
  - selector de dispositivo,
  - medidor de nivel de entrada,
  - mensajes de permiso/error de STT.
- Añadida conexión con SDK oficial de Reachy Mini en simulación:
  - usa el daemon oficial en `http://127.0.0.1:8000`,
  - usa el Python de `Reachy Mini Control`,
  - ejecuta movimientos simples con `ReachyMini()` y `goto_target`.
- Añadidos botones:
  - Estado robot,
  - SDK probe,
  - Saludo,
  - Antenas,
  - Cabeza,
  - Mirar lados,
  - Reset.

## Importante sobre el micro

El navegador puede detectar sonido pero no convertirlo a texto si el reconocimiento de voz del navegador falla.  
Por eso esta versión muestra dos cosas separadas:

- **Medidor de micro**: confirma si entra sonido.
- **Reconocimiento de voz**: confirma si Chrome/Edge devuelve texto.

Si el medidor se mueve pero no aparece texto, el micro funciona y falla el STT del navegador. Como solución rápida puedes usar `Win + H` sobre la caja de texto.

## Instalación

```powershell
cd D:\RITXI\6_1_0_ahootsa_local_ollama_audio_sdk_sim
powershell -ExecutionPolicy Bypass -File .\INSTALAR_6_FALLBACK_LOCAL.ps1
```

## Lanzar daemon Reachy Mini en simulación

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_6_DAEMON_SIM_REACHY.ps1
```

## Probar SDK en simulación

```powershell
powershell -ExecutionPolicy Bypass -File .\PROBAR_6_SDK_SIM.ps1
```

## Lanzar Ahootsa 6.1

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_6_FALLBACK_LOCAL.ps1
```

Abre:

```text
http://127.0.0.1:8090
```

## Diagnóstico

```powershell
powershell -ExecutionPolicy Bypass -File .\DIAGNOSTICAR_6_FALLBACK_LOCAL.ps1
```

## Flujo recomendado

1. Lanzar daemon sim.
2. Probar SDK sim.
3. Lanzar Ahootsa 6.1.
4. En la web, comprobar que el medidor de micro se mueve.
5. Pulsar `SDK probe`.
6. Pulsar `Saludo`.
7. Decir o escribir: `Hola Ahootsa`.

## Qué no incluye

- No usa Hugging Face.
- No usa `backend_connected`.
- No usa `voices/current`.
- No usa Sohee/Aiden de la app oficial.
- No usa `reachy_mini_conversation_app`.


## Corrección 6.1.1

Esta versión fuerza no-cache en HTML/JS y carga:

```html
/static/app.js?v=6.1.1
```

Motivo: si el navegador mantiene en caché `app.js` de 6.0.0, la pantalla puede mostrar Ahootsa 6.1 pero los botones SDK no tienen eventos JavaScript.

Comprobación:

```powershell
powershell -ExecutionPolicy Bypass -File .\DIAGNOSTICAR_6_BOTONES_SDK.ps1
```

En la interfaz debe aparecer el saludo inicial:

```text
Hola. Soy Ahootsa 6.1.1...
```

Si no aparece, pulsa Ctrl+F5.
