# Instalación en equipo nuevo

1. Instalar Reachy Mini Control/Desktop Control.
2. Descargar la app oficial `reachy_mini_conversation_app` al menos una vez.
3. Instalar Ollama si se quiere IA local auxiliar.
4. Descargar `llama3.2:3b`:

```powershell
ollama pull llama3.2:3b
```

5. Instalar Ahootsa:

```powershell
powershell -ExecutionPolicy Bypass -File .\INSTALAR_AHOOTSA_5_0_44.ps1 -InstallMujoco
```
