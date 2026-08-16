# Update 12.8.2 — Dos modos de arranque

## Modo anónimo

`INICIAR_AHOOTSA_ANONIMO.ps1` inicia únicamente:

- Reachy Mini daemon y MuJoCo, puerto 8000;
- Conversation App, puerto 7860.

No inicia el servidor 8100, no abre el panel, no consulta la API local y no
crea una sesión. Utiliza el perfil general `ahootsa`, nunca
`ahootsa_session`.

## Modo sesión local

`INICIAR_AHOOTSA_SESION.ps1` inicia:

- Ahootsa Local Server, puerto 8100;
- Reachy Mini daemon y MuJoCo, puerto 8000;
- panel profesional.

La Conversation App no se inicia hasta que el profesional crea o selecciona
una persona, elige actividad y nivel, pulsa `Preparar` y después
`Iniciar conversación`.

## Limpieza

El antiguo `INICIAR_AHOOTSA.ps1` se archiva para evitar ambigüedad. El panel
queda configurado para utilizar:

```text
scripts/iniciar_conversation_sesion.ps1
```

## Reparación de la extracción anterior

El instalador archiva `D:\\RITXI\\AHOOTSA8\\payload` cuando reconoce que pertenece al paquete anterior, además de los instaladores 12.8/12.8.1 que pudieran haber quedado en la raíz.
