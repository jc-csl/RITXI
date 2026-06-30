# Ahootsa Realtime Ollama — v0.4.44

Corrección del juego Memory.

## Problema corregido

El fallo podía reproducir dos veces el movimiento y el sonido.

## Instalación

```powershell
cd D:\RITXI\ahootsa_v0_4_44_memory_reaccion_unica_secuencia
powershell -ExecutionPolicy Bypass -File .\INSTALAR_AHOOTSA_COMPLETO.ps1
```

## Reparación directa del Memory

```powershell
powershell -ExecutionPolicy Bypass -File .\REPARAR_MEMORY_REACCION_UNICA.ps1
```

## Test

```powershell
powershell -ExecutionPolicy Bypass -File .\test\PROBAR_MEMORY_REACCION_UNICA.ps1
```

## Secuencia esperada

```text
Usuario: uno y tres
1. Las cartas se giran.
2. Se espera un momento.
3. Si falla, hay una sola reacción.
4. No se repite movimiento ni sonido.
```
