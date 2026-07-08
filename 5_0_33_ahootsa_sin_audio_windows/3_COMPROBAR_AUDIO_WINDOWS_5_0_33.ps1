param()
$ErrorActionPreference = "Stop"
$Py = Join-Path $env:LOCALAPPDATA "Reachy Mini Control\apps_venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Py)) { throw "No encuentro Python apps_venv: $Py" }
$env:AHOOTSA_DISABLE_WINDOWS_TTS = "1"
$env:AHOOTSA_ALLOW_WINDOWS_TTS = "0"
& $Py -c "import os; print('AHOOTSA_DISABLE_WINDOWS_TTS=', os.environ.get('AHOOTSA_DISABLE_WINDOWS_TTS')); import pyttsx3; e=pyttsx3.init(); print('pyttsx3_disabled=', getattr(pyttsx3,'__ahootsa_5033_disabled__',False)); print('engine=', type(e).__name__); e.say('ESTO NO DEBE SONAR'); e.runAndWait(); print('OK_NO_DEBERIA_HABER_SONADO_AUDIO_WINDOWS')"
