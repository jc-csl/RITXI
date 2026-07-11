# 05 — Flujos de comunicación y puertos

## 1. Puertos principales

```text
8000  reachy-mini-daemon.exe
7860  app web Ahootsa + app oficial servida internamente
11434 Ollama local
```

Puertos antiguos o evitados:

```text
7870  usado por versiones antiguas del juego Memory; ya no es la vía recomendada
```

## 2. Flujo de arranque 7.0.19

```text
LANZAR_AHOOTSA_7_0_19.ps1
  ↓
localiza apps_venv
  ↓
comprueba versión instalada y entrypoint
  ↓
instala si no coincide o si se usa -ForceInstall
  ↓
comprueba pygame, mujoco, opencv-python y librería de emociones
  ↓
arranca o reinicia reachy-mini-daemon.exe
  ↓
espera http://127.0.0.1:8000/api/daemon/status
  ↓
POST http://127.0.0.1:8000/api/apps/start-app/ahootsa_realtime_ollama_app
  ↓
espera http://127.0.0.1:7860/ahootsa/status o /ahootsa
  ↓
deja disponible el panel
```

## 3. Endpoints Ahootsa actuales

Panel:

```text
GET /ahootsa
GET /ahootsa/status
GET /ahootsa/resolve_activity?activity=baile%20dos
GET /ahootsa/list_activities
GET /ahootsa/play_activity
```

Memory:

```text
GET  /memory/state
GET  /memory/page?game_id=animales&reset=0
GET  /memory/games
POST /memory/reset
POST /memory/choose
```

Configuración:

```text
GET  /config/list
GET  /config/file?id=...
POST /config/save
```

Cámara PC:

```text
GET/POST /camera_pc/...
```

La ruta exacta puede variar por versión, pero el principio actual es que la cámara PC se gestiona en Ahootsa y no mediante la cámara oficial de MuJoCo.

## 4. 404 durante arranque

En logs se han visto muchos:

```text
GET /memory/state 404 Not Found
GET /ahootsa/status 404 Not Found
GET /ahootsa 404 Not Found
```

Si aparecen al principio y luego pasan a:

```text
GET /memory/state 200 OK
GET /ahootsa/status 200 OK
GET /ahootsa 200 OK
```

no indican necesariamente fallo funcional. Significan que el panel o el script estaba sondeando antes de que la app terminara de registrar rutas.

Mejora pendiente: retrasar/reducir sondeos o filtrar estos 404 iniciales en el resumen de logs.

## 5. WebSocket y daemon

El daemon expone WebSocket SDK:

```text
ws://127.0.0.1:8000/ws/sdk
```

En una ejecución correcta puede verse:

```text
WebSocket /ws/sdk accepted
connection open
```

Los mensajes de audio USB no encontrado son esperables en simulación si no hay hardware Reachy Mini conectado:

```text
No Reachy Mini Audio USB device found
No Reachy Mini Audio Source card found
No Reachy Mini Audio Sink card found
```
