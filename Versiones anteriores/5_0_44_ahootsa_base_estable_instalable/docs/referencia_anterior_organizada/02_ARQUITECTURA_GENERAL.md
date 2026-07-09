# 02 — Arquitectura general

## 1. Capas del sistema

```text
Usuario
  ↓
Interfaz web de Ahootsa / Desktop Control
  ↓
App activa: ahootsa_realtime_ollama_app
  ↓
Código Ahootsa + lógica heredada de reachy_mini_conversation_app
  ↓
reachy-mini-daemon.exe
  ↓
Robot Reachy Mini real o simulación MuJoCo
```

En paralelo:

```text
Ahootsa
  ├─ IA principal conversacional → Hugging Face Realtime
  ├─ IA auxiliar local           → Ollama en 127.0.0.1:11434
  ├─ Cámara oficial              → Reachy/MuJoCo media.get_frame()
  ├─ Cámara PC                   → navegador/WebView + getUserMedia
  ├─ Actividades                 → herramientas Python
  └─ Logs                        → D:\RITXI\logs
```

## 2. Qué se lanza realmente

La app que lanza el script no es la oficial con nombre `reachy_mini_conversation_app`, sino la app Ahootsa registrada:

```text
ahootsa_realtime_ollama_app
```

El launcher hace una llamada equivalente a pulsar Start en Desktop Control:

```text
POST http://127.0.0.1:8000/api/apps/start-app/ahootsa_realtime_ollama_app
```

La app oficial puede estar instalada y ser usada como base de código o dependencia, pero no se lanza como app activa salvo que se arranque explícitamente.

## 3. Papel de Reachy Mini Control

Reachy Mini Control aporta:

```text
- apps_venv
- reachy-mini-daemon.exe
- gestor de apps
- API /api/apps/start-app/...
- integración robot/MuJoCo
- media/cámara oficial
- ejecución de apps web
```

Ahootsa aporta:

```text
- perfil Ahootsa
- herramientas educativas
- ask_ollama
- juegos Memory
- cámara PC
- logs de diagnóstico
- control de voz/audio Windows
- scripts de arranque y comprobación
```

## 4. Puertos principales

```text
8000  → daemon oficial Reachy Mini
7860  → interfaz web Ahootsa / app web
7870  → juego Memory en algunas versiones
11434 → API local de Ollama
8765  → posible backend Hugging Face local compatible Realtime
```

## 5. Diferencia entre app, paquete y backend

```text
App activa:
  ahootsa_realtime_ollama_app

Paquete propio:
  ahootsa_realtime_ollama_desktop_app

Paquete oficial reutilizado:
  reachy_mini_conversation_app

Backend conversacional principal:
  Hugging Face Realtime, deployed o local

Backend IA auxiliar:
  Ollama local
```

## 6. Arquitectura conceptual estable recomendada

```text
Conversación natural principal
  -> Hugging Face Realtime oficial
  -> online por defecto o local si hay backend Realtime en 8765

Pregunta puntual a IA local
  -> herramienta ask_ollama
  -> Ollama /api/generate
  -> llama3.2:3b

Actividades educativas
  -> herramientas Python
  -> posible respuesta hablada por Ahootsa
  -> movimiento/emoción del robot si procede

Cámara
  -> cámara oficial Reachy/MuJoCo para herramienta oficial camera
  -> cámara PC independiente para fotos desde el portátil
```

## 7. Principio de diseño

Ahootsa no debe mezclar sin control varios motores de voz o IA. La regla recomendada es:

```text
Una conversación principal.
Una IA local auxiliar explícita.
Un único canal de habla audible.
Logs separados por ejecución.
```
