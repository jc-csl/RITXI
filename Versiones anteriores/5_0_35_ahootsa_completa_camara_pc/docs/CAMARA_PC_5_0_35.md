# Ahootsa 5.0.35 — Control de cámara del PC

## Objetivo

La versión 5.0.35 añade una función que faltaba en la versión consolidada: poder usar la cámara del ordenador para hacer una foto desde la propia interfaz de Ahootsa.

La solución evita depender de una API nativa de Windows. Usa la API estándar del navegador:

```text
navigator.mediaDevices.getUserMedia({ video: true, audio: false })
```

Esto es lo más adecuado porque Ahootsa se ejecuta como aplicación web dentro del entorno Reachy Mini Desktop Control.

## Qué se añade

### Frontend

Se añade un panel flotante llamado **Cámara PC**.

Funciones:

- Abrir/ocultar panel.
- Activar cámara.
- Ver previsualización.
- Hacer foto.
- Guardar la imagen localmente si el backend no está disponible.
- Enviar la foto al backend mediante `/camera/upload`.

La foto queda también disponible en JavaScript como:

```javascript
window.AHOOTSA_LAST_CAMERA_PHOTO
window.AHOOTSA_CAMERA.getLastPhoto()
```

Y se emite un evento:

```javascript
window.addEventListener('ahootsa:camera-photo', (ev) => {
  console.log(ev.detail.image_data);
});
```

Esto permite conectar después la foto con actividades como **explorar imagen**, **descripción guiada**, **preguntas sobre imagen** o **tareas educativas visuales**.

### Backend

Se añaden endpoints de compatibilidad:

```text
GET  /camera/latest
POST /camera/upload
```

`POST /camera/upload` recibe una imagen en formato data URL:

```json
{
  "image_data": "data:image/png;base64,..."
}
```

Y la guarda en:

```text
D:\RITXI\logs\camera
```

También se crea un `latest.json` con la última captura.

## Seguridad y permisos

La cámara solo se activa cuando la persona pulsa **Activar** y acepta el permiso del navegador.

No se activa de forma automática.

El audio se solicita como `audio: false`, por tanto esta función no abre micrófono.

## Cómo probar

Ejecutar:

```powershell
cd D:\RITXI\5_0_35_ahootsa_completa_camara_pc
powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA_5_0_35.ps1
```

En la interfaz:

1. Abrir el panel **Cámara PC**.
2. Pulsar **Activar**.
3. Aceptar permisos de cámara.
4. Pulsar **Hacer foto**.
5. Comprobar que aparece una imagen de previsualización.
6. Comprobar que se guarda en `D:\RITXI\logs\camera`.

Para comprobar endpoint:

```powershell
powershell -ExecutionPolicy Bypass -File .\2_COMPROBAR_CAMARA_5_0_35.ps1
```

## Posibles problemas

### No aparece el permiso de cámara

Cerrar y abrir de nuevo Desktop Control. Puede haber caché del frontend.

### El navegador dice que no puede acceder a la cámara

Revisar privacidad de Windows:

```text
Configuración > Privacidad y seguridad > Cámara
```

Debe estar permitido el acceso a cámara para aplicaciones de escritorio.

### La cámara se activa pero no guarda la foto

La foto debería seguir disponible con el botón **Guardar**. Si falla el backend, revisar:

```text
/camera/latest
/camera/upload
D:\RITXI\logs\camera
```

## Modificación futura recomendada

Conectar `window.AHOOTSA_LAST_CAMERA_PHOTO` con la actividad **explorar imagen** para que la persona usuaria pueda hacer una foto y pedir a la IA local/Ollama que la describa.

