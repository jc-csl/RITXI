# Update 12.8.1 — Corrección de instalación

## Errores corregidos

1. El ZIP anterior se entregó sin una carpeta contenedora y podía extraerse
   directamente como `D:\RITXI\AHOOTSA8\payload`.
2. Se podía interpretar erróneamente que los scripts de `payload` eran
   ejecutables para el usuario.
3. Windows PowerShell interpretaba `$ServiceName:` como una referencia de
   unidad no válida.
4. La comprobación del paquete no se ejecutaba automáticamente antes de
   modificar la instalación.

## Corrección PowerShell

Se sustituye:

```powershell
"$ServiceName: puerto $Port libre."
```

por:

```powershell
"${ServiceName}: puerto $Port libre."
```

## Instalación segura

El instalador:

- analiza todos los scripts con el parser real de Windows PowerShell;
- detiene los procesos de los puertos 7860, 8100 y 8000;
- crea un backup;
- archiva la carpeta `payload` extraída por error;
- archiva scripts antiguos;
- instala únicamente cuatro scripts visibles;
- vuelve a comprobar los scripts ya instalados.
