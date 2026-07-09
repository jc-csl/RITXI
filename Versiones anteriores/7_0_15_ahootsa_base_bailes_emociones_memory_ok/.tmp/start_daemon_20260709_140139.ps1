$env:AHOOTSA_SESSION_ID='20260709_140139'
$env:AHOOTSA_LOG_DIR='D:\RITXI\logs'
$env:AHOOTSA_LOG_FILE_RUNTIME='D:\RITXI\logs\ahootsa7_20260709_140139_runtime.log'
& 'C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Scripts\reachy-mini-daemon.exe' --sim --fastapi-host 127.0.0.1 --fastapi-port 8000 --no-goto-sleep-on-stop --dataset-update-interval 0 --no-preload-datasets --log-file 'D:\RITXI\logs\ahootsa7_20260709_140139_runtime.log'
