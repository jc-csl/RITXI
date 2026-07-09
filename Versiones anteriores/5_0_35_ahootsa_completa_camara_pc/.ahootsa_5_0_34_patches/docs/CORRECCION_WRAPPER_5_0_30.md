# Ahootsa 5.0.30 - corrección del wrapper PowerShell

## Problema corregido

Al ejecutar:

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_0_29_AHOOTSA_MUJOCO_WEB.ps1
```

podía aparecer:

```text
No se puede procesar la transformación del argumento del parámetro 'InstallMujoco'.
No se puede convertir el valor "System.String" al tipo "System.Management.Automation.SwitchParameter".
```

## Causa

El lanzador 5.0.29 ejecutaba otro proceso PowerShell pasando el switch así:

```powershell
-InstallMujoco:$InstallMujoco
```

En algunas ejecuciones, ese valor no llegaba como booleano, sino como texto, por ejemplo `System.Management.Automation.SwitchParameter`. PowerShell no puede convertir ese texto al tipo `SwitchParameter`, y por eso abortaba antes de aplicar las correcciones.

## Solución aplicada

En 5.0.30 el wrapper construye una lista de argumentos y solo añade `-InstallMujoco` cuando el usuario lo solicita explícitamente:

```powershell
$ApplyArgs = @(
    "-ExecutionPolicy", "Bypass",
    "-File", $Apply,
    "-AppRoot", $AppRoot
)

if ($InstallMujoco.IsPresent) {
    $ApplyArgs += "-InstallMujoco"
}

& powershell @ApplyArgs
```

## Uso

Normal:

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_0_30_AHOOTSA_MUJOCO_WEB.ps1
```

Si falta MuJoCo:

```powershell
powershell -ExecutionPolicy Bypass -File .\LANZAR_5_0_30_AHOOTSA_MUJOCO_WEB.ps1 -InstallMujoco
```

## Correcciones acumuladas

- 5.0.27: endpoints de compatibilidad `/status`, `/mic`, `/voices/current`, `/voices`.
- 5.0.28: escritura robusta de logs para evitar bloqueo de `pantalla.log`.
- 5.0.29: audio único Ahootsa, bloqueo de voz Windows/navegador.
- 5.0.30: wrapper PowerShell corregido para `SwitchParameter`.
