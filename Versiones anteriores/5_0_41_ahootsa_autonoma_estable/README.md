# Ahootsa 5.0.41 autónoma estable

Versión pensada para quedarse como única carpeta de trabajo y poder archivar/borrar las versiones anteriores.

No copia desde `5_0_25`, `5_0_35` ni otras carpetas antiguas. Usa la aplicación instalada en el entorno oficial de Reachy Mini Control:

```text
%LOCALAPPDATA%\Reachy Mini Control\apps_venv
```

y aplica un parche autónomo sobre el paquete instalado `ahootsa_realtime_ollama_desktop_app`.

## Lanzamiento recomendado con Ollama

```powershell
cd D:\RITXI\5_0_41_ahootsa_autonoma_estable
powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_5_0_41.ps1 -Provider ollama -OllamaModel llama3.2:3b
```

También puedes usar el `.cmd`:

```bat
LANZAR_AHOOTSA_OLLAMA_5_0_41.cmd
```

## Hugging Face local

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_5_0_41.ps1 -Provider hf_local -HFModelPath "D:\RITXI\models\TU_MODELO_HF"
```

Si faltan dependencias:

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_5_0_41.ps1 -Provider hf_local -HFModelPath "D:\RITXI\models\TU_MODELO_HF" -InstallHFDeps SI
```

## Cámara PC

Abrir:

```text
http://127.0.0.1:7860/camera/page
```

Las fotos se guardan en:

```text
D:\RITXI\logs\camera
```

## Comprobación

```powershell
powershell -ExecutionPolicy Bypass -File .\1_COMPROBAR_5_0_41.ps1
```

## Resumen de logs

```powershell
powershell -ExecutionPolicy Bypass -File .\2_RESUMIR_LOGS_5_0_41.ps1
```

## Archivar versiones antiguas

Solo después de comprobar que la 5.0.41 funciona:

```powershell
powershell -ExecutionPolicy Bypass -File .\3_ARCHIVAR_VERSIONES_ANTIGUAS.ps1 -Confirmar SI
```

Esto mueve carpetas antiguas a:

```text
D:\RITXI\_versiones_antiguas_ahootsa
```

No borra definitivamente. Cuando confirmes que todo funciona, podrás borrar esa carpeta manualmente.
