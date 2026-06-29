# Cambio v0.3.2

La app **Ahootsa Ollama Local** pasa a usar el puerto `7862` para evitar conflictos con procesos antiguos que se quedaban escuchando en `7861` y devolvían `{"detail":"Not Found"}`.

Nuevo panel:

```text
http://127.0.0.1:7862
```

Se añade script:

```powershell
.\scripts\windows\08_liberar_puertos_ahootsa.ps1
```

Este script libera `7860`, `7861` y `7862`. No toca Ollama en `11434`.
