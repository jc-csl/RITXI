# Cambios v0.4.16 — Corrección Modelfile Ollama

## Error detectado

En v0.4.15, `ollama create` fallaba con:

```text
Error: (line 8): command must be one of "from", "license", "template", "system", ...
```

La causa era que el instalador generaba el `Modelfile` con comillas escapadas:

```text
SYSTEM \"\"\"
```

Ollama necesita recibir:

```text
SYSTEM """
...
"""
```

sin barras invertidas.

## Corrección

v0.4.16 corrige el instalador y añade:

```text
RECREAR_MODELO_OLLAMA_AHOOTSA.ps1
scripts/windows/12_recrear_modelo_ollama_ahootsa.ps1
```

## Uso rápido

Si ya tienes la carpeta v0.4.16:

```powershell
powershell -ExecutionPolicy Bypass -File .\RECREAR_MODELO_OLLAMA_AHOOTSA.ps1
```

Después puedes relanzar:

```powershell
powershell -ExecutionPolicy Bypass -File .\INSTALAR_AHOOTSA_COMPLETO.ps1
```
