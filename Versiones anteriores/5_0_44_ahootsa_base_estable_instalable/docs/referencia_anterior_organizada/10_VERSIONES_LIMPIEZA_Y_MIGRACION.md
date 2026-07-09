# 10 — Versiones, limpieza y migración

## 1. Problema histórico

Las versiones 5.0.26 a 5.0.33 fueron parches sobre 5.0.25. Eso generó dependencia de carpetas antiguas.

La regla actual es:

```text
Cada versión nueva debe ser completa.
No debe depender de 5_0_25 ni de carpetas intermedias.
Debe incluir scripts de instalación y lanzamiento.
```

## 2. Versión base histórica

```text
5_0_25_ahootsa_logs_simples_actividades_recuperadas
```

Aportaba:

```text
- app Ahootsa sobre app oficial
- perfil Ahootsa
- ask_ollama
- Memory
- instalación sobre conversation app
- logs simples
- MuJoCo web
```

## 3. Correcciones históricas importantes

```text
5.0.27 -> endpoints /status, /mic, /voices/current, /voices
5.0.28 -> logs robustos contra Add-Content bloqueado
5.0.29 -> audio único Ahootsa, bloqueo speechSynthesis
5.0.30 -> wrapper PowerShell corregido
5.0.31 -> logs por ejecución y resumen
5.0.32 -> reparación param(...) del lanzador
5.0.33 -> bloqueo más agresivo audio Windows
5.0.34 -> intento de consolidación
5.0.35 -> cámara PC
5.0.36 -> diagnóstico Ollama/cámara
5.0.37 -> llama3.2:3b por defecto
5.0.38 -> proveedor dual HF local/Ollama
5.0.39/40 -> correcciones de ejecutables PowerShell
5.0.41/42 -> enfoque autónomo
5.0.43 -> versión completa Ollama estable
```

## 4. Qué conservar

En una instalación limpia, conservar:

```text
D:\RITXI\5_0_43_ahootsa_completa_ollama_estable
D:\RITXI\logs
D:\RITXI\reachy-mini-dances-library, si se usa
D:\RITXI\reachy-mini-emotions-library, si se usa
D:\RITXI\models, si se usan modelos HF locales
```

## 5. Qué archivar

Después de comprobar la versión completa actual:

```text
5_0_25_...
5_0_26_...
5_0_27_...
...
5_0_42_...
```

Primero mover, no borrar:

```powershell
mkdir D:\RITXI\_versiones_antiguas_ahootsa
Move-Item D:\RITXI\5_0_25_* D:\RITXI\_versiones_antiguas_ahootsa\
```

Después probar de nuevo la versión actual.

## 6. Cuándo borrar definitivamente

Solo borrar `_versiones_antiguas_ahootsa` si:

```text
[ ] Ahootsa arranca.
[ ] Se abre 127.0.0.1:7860.
[ ] El daemon responde en 8000.
[ ] La conversación principal responde.
[ ] Preguntar IA local funciona con llama3.2:3b.
[ ] Cámara PC funciona o el fallo está documentado.
[ ] Memory funciona.
[ ] No hay audio Windows solapado.
[ ] Logs por ejecución se generan correctamente.
```

## 7. Migración a otro PC

Copiar:

```text
D:\RITXI\5_0_43_ahootsa_completa_ollama_estable
```

No basta con copiar esa carpeta si el PC no tiene:

```text
Reachy Mini Control
apps_venv
Ollama
modelo llama3.2:3b
```

En equipo nuevo, seguir `01_INSTALACION_EQUIPO_NUEVO.md`.

## 8. Documentación

La documentación activa queda en esta carpeta organizada. No mantener documentos históricos duplicados salvo que estén archivados como referencia externa.
