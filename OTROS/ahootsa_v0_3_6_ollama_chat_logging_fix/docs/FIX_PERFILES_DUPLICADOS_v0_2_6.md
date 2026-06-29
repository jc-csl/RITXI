# Ahootsa v0.2.6 - Corrección de perfiles duplicados

El error `Ambiguous profile names found` aparece cuando la carpeta externa de perfiles contiene nombres iguales a los perfiles integrados de la app oficial.

Solución aplicada:

- No se define `REACHY_MINI_EXTERNAL_PROFILES_DIRECTORY`.
- Los perfiles originales se cargan desde `reachy_talk_data/profiles`.
- Solo `ahootsa_es` se copia al directorio de usuario `user_personalities/ahootsa_es`.
- El perfil inicial seleccionado es `user_personalities/ahootsa_es`.

Después de instalar, la pantalla de perfiles debe mostrar los perfiles oficiales y Ahootsa.
