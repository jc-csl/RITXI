# Config con rutas relativas v5.9.78

## Problema

Algunos botones de Config usaban claves internas como:

```text
stt_vocab_activity_mapping
```

Si había un error HTTP, el editor mostraba solo:

```text
TypeError: Failed to fetch
```

## Corrección

Ahora `/api/config/file` acepta:

```text
stt_vocab_activity_mapping
app/config/stt_vocabularies/activity_mapping.json
```

La pestaña Config usa preferentemente `real_path`, es decir rutas relativas reales.

## Diagnóstico

Endpoint nuevo:

```text
GET /api/config/selftest
```

Comprueba que todas las rutas permitidas sean seguras y relativas al proyecto.
