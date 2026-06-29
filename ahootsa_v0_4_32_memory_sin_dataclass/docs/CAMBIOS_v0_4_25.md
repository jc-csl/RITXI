# v0.4.25 — Fix HTML del juego de parejas

## Problema

Al abrir el juego aparecía:

```text
Ahootsa Memory Game
No se encontró el HTML del juego.
```

## Causa

El servidor del juego se ejecuta desde el perfil copiado dentro de Reachy Mini Desktop:

```text
%LOCALAPPDATA%\Reachy Mini Control\...\profiles\ahootsa_realtime_es
```

Pero en v0.4.24 el HTML estaba en el paquete:

```text
src/ahootsa_realtime_ollama_desktop_app/games/memory_pairs_animales.html
```

Al ejecutarse desde el perfil copiado, no siempre encontraba esa ruta.

## Corrección

v0.4.25 hace tres cosas:

```text
1. Copia memory_pairs_animales.html también dentro del perfil Ahootsa.
2. memory_pairs_game_server.py busca primero el HTML junto a sí mismo.
3. memory_pairs_game_server.py incorpora el HTML como fallback interno.
```

## Reparación rápida

Con Ahootsa cerrado:

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_HTML_JUEGO_PAREJAS.ps1
```

## Instalación completa

```powershell
powershell -ExecutionPolicy Bypass -File .\INSTALAR_AHOOTSA_COMPLETO.ps1
```

## Prueba

```powershell
powershell -ExecutionPolicy Bypass -File .\PROBAR_JUEGO_PAREJAS_ANIMALES.ps1
```
