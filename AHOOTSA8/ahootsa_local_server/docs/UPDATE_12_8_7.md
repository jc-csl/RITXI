# Update 12.8.7 — Continuidad de audio y recuperación

## Incidencia observada en la sesión 23

Tras un turno largo de Aocha, el log dejó de registrar:

- `User intervention`;
- `role=user_partial`;
- `role=user`.

No apareció una excepción ni una desconexión explícita. La aplicación continuó
abierta hasta el cierre manual.

## Medidas instaladas

### Respuestas más cortas

Los perfiles `ahootsa`, `ahootsa_default` y `ahootsa_session` reciben un bloque
que limita relatos y explicaciones a partes breves. Incluso cuando la persona
pide «cuenta todo», Aocha debe contar una parte, formular una pregunta y
esperar.

### Recuperación sin perder la sesión

Nuevo script en la raíz:

```powershell
.\RECUPERAR_AUDIO_SESION.ps1
```

El script:

1. crea un marcador para impedir que el cierre temporal genere el informe;
2. detiene únicamente Conversation App;
3. conserva servidor, daemon, usuario, actividad y sesión;
4. espera el cierre limpio del transcript;
5. vuelve a iniciar `ahootsa_session`;
6. continúa escribiendo en el mismo log.

### Informes

El informe versión 1.2:

- elimina mensajes internos de herramientas;
- detecta un intervalo largo entre el último turno de Aocha y el cierre;
- muestra una observación de posible incidencia de escucha;
- no afirma automáticamente que haya un fallo: también puede ser silencio
  voluntario.
