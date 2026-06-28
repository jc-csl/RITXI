# Explicación técnica

La Desktop App usa su propio Python interno:

```text
%LOCALAPPDATA%\Reachy Mini Control\cpython-3.12-windows-x86_64-none\python.exe
```

Por eso una app instalada solo en `.venv` no aparece en Desktop.

Esta versión registra únicamente un nuevo entry-point `reachy_mini_apps` en el Python de la Desktop. No reemplaza la distribución oficial.

Entry point:

```toml
[project.entry-points."reachy_mini_apps"]
ahootsa_reachy_mini_conversation_app = "ahootsa_reachy_mini_desktop_app.main:AhootsaReachyMiniConversationApp"
```

El wrapper configura el entorno en español y delega la ejecución en la app oficial:

```python
from reachy_mini_conversation_app.main import run
```
