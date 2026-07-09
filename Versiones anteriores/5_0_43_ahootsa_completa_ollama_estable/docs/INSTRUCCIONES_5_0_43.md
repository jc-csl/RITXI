# Instrucciones Ahootsa 5.0.43

1. Descomprimir en `D:\RITXI\5_0_43_ahootsa_completa_ollama_estable`.
2. Ejecutar:

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_5_0_43.ps1 -Provider ollama -OllamaModel llama3.2:3b
```

3. Probar IA local desde el panel Ahootsa 5.0.43 o con:

```powershell
powershell -ExecutionPolicy Bypass -File .\1_COMPROBAR_IA_CAMARA_5_0_43.ps1
```

4. Probar cámara PC:

```text
http://127.0.0.1:7860/camera/page
```

5. Si funciona todo, archivar versiones antiguas:

```powershell
powershell -ExecutionPolicy Bypass -File .\3_ARCHIVAR_VERSIONES_ANTIGUAS.ps1 -Confirmar SI
```
