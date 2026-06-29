# Cambios v0.4.7 - Original Robot Tools Recovery

- Se eliminan las herramientas experimentales de control local JSON/OGG.
- Se vuelve a usar únicamente la librería de herramientas original de la app de conversación:
  - dance
  - stop_dance
  - play_emotion
  - stop_emotion
  - camera
  - idle_do_nothing
  - move_head
  - sweep_look
  - remember
  - forget
- Se mantiene ask_ollama como herramienta añadida.
- Se actualizan instrucciones para que Ahootsa celebre logros con play_emotion(success) y dance cuando proceda.
- No se llama a media.play_sound ni a GStreamer.
- No se configura D:\RITXI\reachy-mini-emotions-library desde la app.
