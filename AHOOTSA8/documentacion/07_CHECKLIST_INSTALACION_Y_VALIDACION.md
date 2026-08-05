# Checklist de instalación y validación

## A. Preparación del PC

- [ ] Windows 10/11 de 64 bits.
- [ ] Micrófono y altavoces configurados.
- [ ] Reachy Mini Desktop Control cerrado durante las pruebas.
- [ ] Git instalado.
- [ ] `git --version` funciona.
- [ ] `uv` instalado.
- [ ] `uv --version` funciona.
- [ ] Python 3.12 instalado con `uv`.
- [ ] `uv run --python 3.12 python --version` muestra 3.12.

## B. Repositorio

- [ ] Se ha clonado `https://github.com/jc-csl/RITXI.git`.
- [ ] Existe `D:\RITXI\AHOOTSA8`.
- [ ] No se han ejecutado carpetas históricas `AHOOTSA_UPDATE_*`.
- [ ] Existen los cinco scripts operativos.

## C. Aplicación

- [ ] Existe `reachy_mini_conversation_app\.venv`.
- [ ] `uv sync --frozen` terminó sin errores.
- [ ] App 0.9.0.
- [ ] SDK 1.9.0.
- [ ] MuJoCo 3.3.0.
- [ ] `.env` usa español y `deployed`.
- [ ] Perfil inicial `ahootsa`.
- [ ] Existen perfiles y herramientas externas.

## D. Servidor local

- [ ] Existe `ahootsa_local_server\.venv`.
- [ ] FastAPI instalado.
- [ ] Uvicorn instalado.
- [ ] SQLAlchemy instalado.
- [ ] ReportLab instalado.
- [ ] Existe `data\ahootsa.db` después del primer arranque.
- [ ] `/health` devuelve `ok`.

## E. Modo anónimo

- [ ] Ejecutado `INICIAR_AHOOTSA_ANONIMO.ps1`.
- [ ] 8000 activo.
- [ ] 7860 activo.
- [ ] 8100 detenido.
- [ ] Perfil `ahootsa`.
- [ ] Conversación en español.
- [ ] No se crea sesión identificada.
- [ ] No se crea informe personal.

## F. Modo sesión local

- [ ] Ejecutado `INICIAR_AHOOTSA_SESION.ps1`.
- [ ] 8100 activo.
- [ ] 8000 activo.
- [ ] Panel visible.
- [ ] Persona nueva creada.
- [ ] Ficha editada.
- [ ] Actividad y nivel seleccionados.
- [ ] Sesión preparada.
- [ ] 7860 se inicia después de preparar.
- [ ] Perfil `ahootsa_session`.
- [ ] Marcas profesionales registradas.

## G. Finalización

- [ ] Conversation App se cierra.
- [ ] No queda sesión activa.
- [ ] `active_session.json` no bloquea la siguiente sesión.
- [ ] Existe `informe_sesion.pdf`.
- [ ] Existe `informe_sesion.html`.
- [ ] Existe `informe_sesion.json`.
- [ ] Existe `transcripcion_sesion.txt`.
- [ ] El PDF se abre.
- [ ] Se puede preparar otra sesión.

## H. Cierre

- [ ] Ejecutado `LIMPIAR_PROCESOS_AHOOTSA.ps1`.
- [ ] 8000 libre.
- [ ] 8100 libre.
- [ ] 7860 libre.
- [ ] Copia de seguridad inicial realizada.
