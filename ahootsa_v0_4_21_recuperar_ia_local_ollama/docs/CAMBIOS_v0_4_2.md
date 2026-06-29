# Cambios v0.4.2 - Performance Audio Library

Esta versión responde a la necesidad de que Ahootsa no solo mueva el robot, sino que pueda acompañar actuaciones con sonido.

## Añadido

- Sonidos WAV locales originales en `assets/sounds/`.
- Herramienta `dance_with_audio`.
- Herramienta `play_emotion_with_audio`.
- `celebrate_user` reproduce ahora un sonido local breve.
- `sing_song` reproduce ahora un sonido local breve.
- Instrucciones del perfil actualizadas para usar herramientas con audio cuando el usuario lo pida o cuando Ahootsa celebre un logro.

## Importante

La librería oficial de bailes y la herramienta oficial `dance` son principalmente movimiento.
La librería oficial de emociones se usa para movimiento expresivo.
El audio de esta versión es una capa propia de Ahootsa con pistas WAV locales.

Si el dispositivo de salida predeterminado de Windows es Reachy Mini, el audio sonará en el robot. Si no, sonará en el PC.
