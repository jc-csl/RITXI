# v0.4.34 — Reparación del panel integrado de Reachy Mini Desktop

## Problema

La app aparece en verde como `App Running`, pero Reachy Mini Desktop sigue mostrando la pantalla de `Applications` y no cambia al panel integrado de conversación.

La app sí puede estar corriendo en:

```text
http://localhost:7860
```

pero Desktop no la incrusta en el panel derecho.

## Causa probable

En versiones anteriores el wrapper usaba:

```text
http://0.0.0.0:7860
```

como `custom_app_url`.

`0.0.0.0` sirve para escuchar conexiones, pero no es una URL adecuada para incrustar en un WebView de escritorio.

La app debe escuchar en todas las interfaces si lo necesita, pero la URL embebida para Desktop debe ser:

```text
http://localhost:7860
```

## Corrección

v0.4.34 cambia:

```text
custom_app_url = "http://localhost:7860/"
```

y actualiza la metadata local con:

```text
host = "http://localhost:7860"
url = "http://localhost:7860"
app_url = "http://localhost:7860"
custom_app_url = "http://localhost:7860/"
```

## Reparación rápida

Con Desktop cerrado:

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_PANEL_INTEGRADO_DESKTOP.ps1
```

Después:

```text
1. Abrir Reachy Mini Desktop.
2. Pulsar Start en Ahootsa Realtime Ollama.
3. Si no cambia solo, hacer doble clic en la tarjeta verde de Ahootsa.
```

## Diagnóstico

Si esto funciona en navegador:

```text
http://localhost:7860
```

pero no aparece integrado, el problema ya no está en Ahootsa sino en cómo Desktop decide mostrar el WebView embebido de apps locales.
