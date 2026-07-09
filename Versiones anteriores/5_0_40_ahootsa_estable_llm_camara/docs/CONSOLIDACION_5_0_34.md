# Ahootsa 5.0.34 — versión completa consolidada

Esta versión sirve para crear una carpeta nueva independiente:

```text
D:\RITXI\5_0_34_ahootsa_completa_consolidada
```

La carpeta se construye copiando una vez la base funcional 5.0.25 y aplicando dentro todas las correcciones acumuladas hasta 5.0.33.
Después de probar que la 5.0.34 arranca correctamente, las carpetas antiguas 5.0.25, 5.0.26, ..., 5.0.33 pueden archivarse o borrarse.

## Qué consolida

- Base completa de la app desde 5.0.25.
- Endpoints de compatibilidad: `/status`, `/mic`, `/voices/current`, `/voices`.
- Logs por ejecución con timestamp.
- Escritura de logs tolerante a bloqueos de `pantalla.log`.
- Reparación de scripts PowerShell con `param(...)` al inicio.
- Bloqueo de audio Windows/navegador/pyttsx3/SAPI para que solo hable Ahootsa.
- Documentación técnica actualizada.

## Flujo recomendado

Desde esta carpeta de distribución:

```powershell
powershell -ExecutionPolicy Bypass -File .\0_CREAR_VERSION_COMPLETA_5_0_34.ps1
```

Luego entra en:

```text
D:\RITXI\5_0_34_ahootsa_completa_consolidada
```

y lanza:

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_AHOOTSA.ps1
```

## Cuándo borrar carpetas antiguas

Solo después de comprobar:

1. Arranca el daemon.
2. Arranca la app.
3. No aparecen 404 de `/status`, `/mic`, `/voices/current`.
4. Cada ejecución crea logs nuevos.
5. En actividades no suena la voz Windows/navegador.
6. El juego de parejas y las actividades principales funcionan.

Entonces puedes dejar únicamente:

```text
D:\RITXI\5_0_34_ahootsa_completa_consolidada
D:\RITXI\logs
```
