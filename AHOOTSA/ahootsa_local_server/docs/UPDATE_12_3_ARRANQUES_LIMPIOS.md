# Update 12.3 — Arranques limpios

## Motivo

Los procesos anteriores podían conservar abiertos los puertos:

- `8000`: daemon Reachy/MuJoCo;
- `7860`: Conversation App;
- `8100`: Ahootsa Local Server.

Al volver a ejecutar un lanzador, la instancia anterior podía permanecer activa,
impedir un nuevo arranque o hacer que una prueba se conectase a la versión
equivocada.

El error `No es posible conectar con el servidor remoto` del test de arranque
indica específicamente que el servidor local no estaba disponible en el puerto
8100. No lo provoca directamente una Conversation App antigua, pero la limpieza
automática evita que queden instancias anteriores de cualquiera de los tres
servicios.

## Solución

Los tres lanzadores utilizan una utilidad común:

```text
D:\RITXI\AHOOTSA8\scripts\ahootsa_process_utils.ps1
```

Antes de arrancar:

1. localizan el PID que escucha en el puerto;
2. detienen el proceso anterior;
3. esperan a que el puerto quede libre;
4. eliminan procesos huérfanos con la línea de comandos correspondiente;
5. inician la nueva instancia.

La Conversation App intenta primero un cierre ordenado mediante la API del
daemon y recurre al cierre forzado si no funciona.

## Scripts

```text
0_detener_servicios_ahootsa.ps1
COMPROBAR_SERVICIOS_AHOOTSA.ps1
1_lanzar_daemon_mujoco.ps1
2_lanzar_app_ahootsa.ps1
ahootsa_local_server\3_lanzar_ahootsa_server.ps1
```

El parámetro `-KeepExisting` evita la limpieza automática cuando se necesite
hacer una prueba especial.

## Pruebas

- `COMPROBAR_ARRANQUES_12_3.ps1`
- `PROBAR_REARRANQUE_SERVIDOR_12_3.ps1`
- `PROBAR_ARRANQUE_OFICIAL_12_3.ps1`
