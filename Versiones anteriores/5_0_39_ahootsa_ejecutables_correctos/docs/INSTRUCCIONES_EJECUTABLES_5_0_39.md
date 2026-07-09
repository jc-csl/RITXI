
# Ejecutables correctos 5.0.39

## Opción normal: Ollama

Desde la carpeta descomprimida:

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_OLLAMA_5_0_39.ps1
```

Usa `llama3.2:3b` por defecto.

## Opción Hugging Face local

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_HF_LOCAL_5_0_39.ps1 -HFModelPath "D:\RITXI\models\TU_MODELO"
```

## Por qué se corrige el error anterior

La 5.0.38 intentaba borrar la misma carpeta desde la que se ejecutaba cuando se usaba `-Force`. La 5.0.39 usa una carpeta destino distinta:

```text
D:\RITXI\5_0_39_ahootsa_estable_llm_camara
```

Por tanto, puedes descomprimir la carpeta y lanzar desde ella sin que intente eliminarse a sí misma.
