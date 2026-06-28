# v5.9.93: política configurable de animaciones

## Archivo nuevo

```text
app/config/robot_motion_policy.json
```

## Pestaña Config

```text
Política robot / animaciones
```

## Regla

```text
Texto + IA conversacional → sin animación automática
Fichas / actividades / juegos / emociones → inicio y final con animación visible
```

## Animaciones por defecto

```text
start_positive: dance1, dance2, dance3, cheerful1
end_positive: dance1, dance2, dance3, cheerful1, success1, yes1
```

## Diagnóstico

Si en logs aparece una versión anterior, por ejemplo:

```text
Ritxi v5.9.91 iniciado
```

no se está ejecutando esta versión.
