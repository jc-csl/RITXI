@echo off
echo =========================================
echo   Iniciando Chatbot ReachyMini Local...
echo =========================================

echo 1. Comprobando instalacion de Ollama...
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Ollama no esta instalado. Descargando e instalando...
    winget --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo Winget no detectado. Descargando instalador web...
        curl -L https://ollama.com/download/OllamaSetup.exe -o OllamaSetup.exe
        start /wait OllamaSetup.exe /quiet
    ) else (
        echo Winget detectado. Usando winget...
        winget install --id Ollama.Ollama -e --source winget --accept-source-agreements --accept-package-agreements
    )
    echo Esperando 10 segundos para que Ollama inicie en segundo plano...
    timeout /t 10 /nobreak
) else (
    echo Ollama detectado correctamente.
)

echo.
echo 2. Comprobando modelos de IA locales...
ollama list | findstr "llama3.2:3b" >nul
if %errorlevel% neq 0 (
    echo Descargando modelo de lenguaje llama3.2:3b...
    ollama pull llama3.2:3b
)
ollama list | findstr "nomic-embed-text:latest" >nul
if %errorlevel% neq 0 (
    echo Descargando modelo de embeddings nomic-embed-text:latest...
    ollama pull nomic-embed-text:latest
)

echo.
echo 3. Comprobando/Activando el entorno virtual de Python...
IF NOT EXIST "venv\Scripts\activate.bat" (
    echo No se encontro 'venv'. Creando entorno virtual...
    python -m venv venv
    call venv\Scripts\activate
    echo Instalando dependencias desde requirements.txt...
    pip install -r requirements.txt
) ELSE (
    call venv\Scripts\activate
    echo Verificando dependencias en requirements.txt...
    pip install -r requirements.txt
)

echo.
echo 4. Arrancando la aplicacion con Streamlit...
streamlit run app.py

pause