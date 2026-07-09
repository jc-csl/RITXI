# Instrucciones rápidas Ahootsa 5.0.42

1. Descomprimir en `D:\RITXI\5_0_42_ahootsa_autonoma_estable`.
2. Ejecutar:

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_5_0_42.ps1 -Provider ollama -OllamaModel llama3.2:3b
```

3. Abrir cámara PC:

```text
http://127.0.0.1:7860/camera/page
```

4. Ver estado Ollama:

```text
http://127.0.0.1:7860/ollama/status
```

5. Tras validar, archivar anteriores:

```powershell
powershell -ExecutionPolicy Bypass -File .\3_ARCHIVAR_VERSIONES_ANTIGUAS.ps1 -Confirmar SI
```
