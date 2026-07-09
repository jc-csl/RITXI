# Ahootsa 5.0.38 — HF local + Ollama

Crea una versión completa nueva con proveedor LLM dual:

- Hugging Face local descargado en disco.
- Ollama como fallback o modo directo.
- Cámara PC por `/camera/page`.
- Audio único Ahootsa, sin voz/beep Windows.

Uso básico con Ollama:

```powershell
powershell -ExecutionPolicy Bypass -File .\0_CREAR_VERSION_ESTABLE_5_0_38.ps1 -Force
cd D:\RITXI\5_0_38_ahootsa_llm_dual_hf_ollama
powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_5_0_38.ps1
```

Uso con Hugging Face local:

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_5_0_38.ps1 -Provider hf_local -HFModelPath "D:\RITXI\models\TU_MODELO_HF"
```
