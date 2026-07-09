# Ahootsa 5.0.44 - base estable instalable

Versión completa nueva. No depende de carpetas 5.0.25, 5.0.40 ni 5.0.43.

## Principios técnicos

- La conversación principal sigue usando `reachy_mini_conversation_app` y su backend Hugging Face Realtime.
- Ahootsa se instala como app Reachy Mini independiente: `ahootsa_realtime_ollama_app`.
- Ollama no sustituye al motor principal: queda como consulta auxiliar de texto y como herramienta `ask_ollama`.
- Las actividades se cargan mediante perfiles externos y herramientas externas, sin machacar perfiles oficiales.
- Se eliminan duplicados de `tools.txt`.

## Instalación

```powershell
cd D:\RITXI\5_0_44_ahootsa_base_estable_instalable
powershell -ExecutionPolicy Bypass -File .\INSTALAR_AHOOTSA_5_0_44.ps1 -InstallMujoco
```

## Lanzamiento

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_5_0_44.ps1
```

Panel: `http://127.0.0.1:7860/ahootsa`

## Perfiles

- `ahootsa_rapido`: conversación + herramientas esenciales.
- `ahootsa_realtime_es`: perfil recomendado con actividades estables.
- `ahootsa_completo`: todas las herramientas estables.
