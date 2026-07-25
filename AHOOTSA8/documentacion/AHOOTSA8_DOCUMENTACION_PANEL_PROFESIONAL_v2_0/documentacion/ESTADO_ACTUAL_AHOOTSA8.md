# Estado actual de Ahootsa 8 — 25/07/2026

## Línea técnica vigente

- Base: `reachy_mini_conversation_app` oficial.
- `src/` oficial: sin modificaciones.
- Conversación: backend realtime oficial en modo `deployed`.
- Idioma de transcripción: español.
- Perfil externo: `ahootsa`.
- Tool propia: `external_tools/ahootsa_dances.py`.
- Actividad operativa: «Vamos a bailar».
- Ollama: no utilizado.

## Servidor local

- Ruta: `D:\RITXI\AHOOTSA8\ahootsa_local_server`.
- Versión validada: 0.11.1.
- Stack: FastAPI + SQLAlchemy + SQLite.
- Funciones existentes: usuarios, perfiles, sesiones, eventos, memoria,
  resúmenes, actividades prototipo, contexto y snapshots.

## Decisión

El servidor será el backend del panel profesional y del seguimiento. No
sustituirá la conversación oficial.

## Próxima línea de desarrollo

1. Actividades y niveles.
2. Progreso por usuario y actividad.
3. Actividades dentro de una sesión.
4. Observaciones profesionales.
5. Panel básico.
6. Contexto temporal.
7. Lanzador de la app oficial.
8. Importación de logs.
9. Análisis posterior.
10. Recomendación de nivel confirmada por el profesional.
