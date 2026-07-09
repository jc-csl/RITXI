
# Ahootsa 5.0.40 - ejecutables corregidos

Esta versión corrige el problema de la 5.0.38: no se debe crear la versión completa sobre la misma carpeta desde la que se está ejecutando el script.

## Uso recomendado

Descomprimir en `D:\RITXI\5_0_40_ahootsa_ejecutables_correctos` y ejecutar:

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_OLLAMA_5_0_40.ps1
```

Esto crea, si no existe, la carpeta completa:

```text
D:\RITXI\5_0_40_ahootsa_estable_llm_camara
```

y después lanza Ahootsa usando Ollama con:

```text
llama3.2:3b
```

## Importante

No se borra la carpeta desde la que estás ejecutando el script. El destino completo es otra carpeta.
