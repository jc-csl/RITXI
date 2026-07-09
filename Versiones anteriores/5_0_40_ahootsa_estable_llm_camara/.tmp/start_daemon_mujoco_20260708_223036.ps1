# start_daemon_mujoco.ps1 generado por Ahootsa 5.0.34
$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$env:AHOOTSA_LOG_DIR = "D:\RITXI\logs"
$env:AHOOTSA_SESSION_ID = "20260708_223036"
$env:AHOOTSA_LOG_FILE_SCREEN = "__SCREENLOG__"
$env:AHOOTSA_LOG_FILE_EVENTS = "__EVENTLOG__"
$env:AHOOTSA_LOG_FILE_RUNTIME = "__RUNTIMELOG__"
$env:REACHY_MINI_CUSTOM_PROFILE = "ahootsa_realtime_es"
$env:REACHY_MINI_PROFILE = "ahootsa_realtime_es"
$env:REACHY_MINI_PERSONALITY = "ahootsa_realtime_es"
$env:REACHY_MINI_USER_PERSONALITY = "ahootsa_realtime_es"
$env:AHOOTSA_NAME = "Ahootsa"
$env:ASSISTANT_NAME = "Ahootsa"
$env:ROBOT_NAME = "Ahootsa"
$env:PROJECT_NAME = "Ahootsa"
$env:AHOOTSA_LANGUAGE = "es"
$env:REACHY_MINI_LANGUAGE = "es"
$env:AHOOTSA_VOICE = "Sohee"
$env:VOICE = "Sohee"
$env:REACHY_MINI_VOICE = "Sohee"
$env:OPENAI_REALTIME_VOICE = "Sohee"
$env:REALTIME_VOICE = "Sohee"
$env:TTS_VOICE = "Sohee"
$env:AUDIO_VOICE = "Sohee"
$env:OLLAMA_BASE_URL = "http://127.0.0.1:11434"
$env:OLLAMA_MODEL = "ahootsa-local:latest"

$Daemon = "C:\Users\Alumno\AppData\Local\Reachy Mini Control\apps_venv\Scripts\reachy-mini-daemon.exe"
$DaemonLog = "D:\RITXI\logs\ahootsa5_20260708_223036_runtime.log"
$DaemonTranscriptLog = "D:\RITXI\logs\ahootsa_5_mujoco_daemon_transcript_20260708_223036.log"
$Port = 8000
$HostAddress = "127.0.0.1"
$HeadlessArg = ""

"START_DAEMON $(Get-Date -Format o)" | Add-Content -Encoding UTF8 -LiteralPath $DaemonLog
"Daemon=$Daemon" | Add-Content -Encoding UTF8 -LiteralPath $DaemonLog
"Port=$Port" | Add-Content -Encoding UTF8 -LiteralPath $DaemonLog
"LogRoot=$env:AHOOTSA_LOG_DIR" | Add-Content -Encoding UTF8 -LiteralPath $DaemonLog
"Voice=$env:AHOOTSA_VOICE" | Add-Content -Encoding UTF8 -LiteralPath $DaemonLog
$ArgsList = @(
    "--sim",
    "--fastapi-host", $HostAddress,
    "--fastapi-port", "$Port",
    "--no-goto-sleep-on-stop",
    "--dataset-update-interval", "0",
    "--no-preload-datasets",
    "--log-file", $DaemonLog
)

if ($HeadlessArg -eq "--headless") {
    $ArgsList += "--headless"
}

"ARGS=$($ArgsList -join ' ')" | Add-Content -Encoding UTF8 -LiteralPath $DaemonLog
try {
    # No usamos redireccion de stderr/stdout con & porque PowerShell 5 lo muestra como NativeCommandError.
    # El propio daemon escribe su log en --log-file=$DaemonLog.
    $Proc = Start-Process -FilePath $Daemon -ArgumentList $ArgsList -NoNewWindow -PassThru
    "DAEMON_PROCESS_STARTED pid=$($Proc.Id) $(Get-Date -Format o)" | Add-Content -Encoding UTF8 -LiteralPath $DaemonLog
    $Proc.WaitForExit()
    "DAEMON_EXIT_CODE=$($Proc.ExitCode) $(Get-Date -Format o)" | Add-Content -Encoding UTF8 -LiteralPath $DaemonLog
} catch {
    "DAEMON_EXCEPTION=$($_.Exception.Message) $(Get-Date -Format o)" | Add-Content -Encoding UTF8 -LiteralPath $DaemonLog
}
