@echo off
echo ========================================================
echo   Inicializando y sincronizando con GitHub...
echo ========================================================

:: 1. Inicializar el repositorio si no existe
if not exist .git (
    echo Inicializando repositorio local...
    git init
    git branch -M main
)

:: 2. Configurar perfil de usuario de Git para este proyecto
echo Configurando el perfíl de Git...
git config user.name "jc-csl"
git config user.email "jcsanroman@centrosanluis.com"

:: 3. Configurar el origen remoto
:: Se elimina el antiguo por si estaba mal configurado y se añade el nuevo
git remote remove origin 2>nul
git remote add origin https://github.com/jc-csl/ollama.git

:: 4. Añadir todos los archivos ignorando los pesados (gracias al .gitignore)
echo.
echo Anadiendo archivos...
git add .

:: 5. Crear el commit
echo Creando copia de seguridad...
git commit -m "Actualizacion del entorno del robot interactivo"

:: 6. Subir (Push) los cambios a la rama principal (main)
echo.
echo Subiendo el codigo a GitHub...
git push -u origin main

echo.
echo ========================================================
echo   ¡Sincronizacion completada!
echo ========================================================
pause
