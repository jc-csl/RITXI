# Pestaña Config v5.9.73

La pestaña Config permite editar todos los archivos permitidos por el backend.

## Archivos nuevos incluidos

```text
app/config/interaction_policy.json
app/config/ritxi_constants.py
```

## Accesos especiales

```text
Lista local_activity_ids
Lista ollama_activity_ids
```

Ambos abren `interaction_policy.json`, porque esas listas son campos internos del mismo JSON.

## Funcionamiento

La lista `Todos los archivos editables` se carga desde:

```text
GET /api/config/files
```

Por tanto, cualquier archivo añadido a `CONFIG_FILE_MAP` aparece en la pestaña Config.
