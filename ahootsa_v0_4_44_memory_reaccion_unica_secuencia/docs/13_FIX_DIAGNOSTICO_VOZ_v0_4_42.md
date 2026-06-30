# 13 — Fix diagnóstico de voz v0.4.44

## Problema

El script de diagnóstico de voz tenía saltos de línea dentro de rutas como:

```text
site-packages
eachy_mini_conversation_app
```

Eso producía en PowerShell:

```text
Test-Path : Caracteres no válidos en la ruta de acceso
```

## Corrección

```text
- DIAGNOSTICAR_VOZ_SOHEE_TOTAL.ps1 usa Join-Many para construir rutas.
- FORZAR_VOZ_SOHEE_TOTAL.ps1 usa Join-Many y LiteralPath.
- El diagnóstico ya no busca Aiden dentro de instructions.txt.
```

## Importante

Si aparece Aiden dentro de esta frase:

```text
Si el sistema ofrece una lista y aparece Aiden...
```

no significa que Aiden sea la voz activa. Es solo texto de instrucciones.

## Comandos

```powershell
powershell -ExecutionPolicy Bypass -File .\FORZAR_VOZ_SOHEE_TOTAL.ps1
powershell -ExecutionPolicy Bypass -File .\test\DIAGNOSTICAR_VOZ_SOHEE_TOTAL.ps1
```
