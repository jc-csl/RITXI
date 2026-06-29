# Ahootsa v0.2.5 — perfiles y logotipos recuperados

Esta versión incluye de nuevo los perfiles originales de `reachy_mini_conversation_app` dentro del wrapper Ahootsa:

- `bored_teenager`
- `captain_circuit`
- `chess_coach`
- `cosmic_kitchen`
- `default`
- `hype_bot`
- `mad_scientist_assistant`
- `mars_rover`
- `nature_documentarian`
- `noir_detective`
- `sorry_bro`
- `tedai` *(perfil de desarrollo, la app oficial lo oculta en la UI)*
- `time_traveler`
- `victorian_butler`
- `ahootsa_es`

El wrapper usa `REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY` apuntando a su carpeta interna `profiles`, ahora con todos los perfiles.

Los logotipos/avatares originales se recuperan automáticamente porque los nombres de perfil coinciden con los que ya conoce la UI oficial (`constants.js`).

Para que `ahootsa_es` use el logo de Ahootsa, ejecuta el script opcional:

```powershell
scripts\windows\04_instalar_logo_ahootsa_en_conversation_ui.ps1
```

Ese script copia `assets/ahootsa_logo.png` al paquete `reachy_mini_conversation_app/static/avatars/` dentro de `apps_venv` y añade la entrada `ahootsa_es: "ahootsa-logo.png"` a `constants.js`.
