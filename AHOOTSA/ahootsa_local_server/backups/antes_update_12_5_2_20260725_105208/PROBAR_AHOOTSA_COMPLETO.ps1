param(
    [int]$TimeoutConversacion = 180,
    [switch]$MantenerAppAbierta
)

$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$ServerRoot = Join-Path $ProjectRoot "ahootsa_local_server"
$PythonExe = Join-Path $ServerRoot ".venv\Scripts\python.exe"
$SmokeTest = Join-Path $ServerRoot "tools\ahootsa_smoke_test.py"

if (-not (Test-Path $PythonExe)) {
    throw "No se encuentra el Python de ahootsa_local_server: $PythonExe"
}

if (-not (Test-Path $SmokeTest)) {
    throw "No se encuentra la prueba final: $SmokeTest"
}

$Arguments = @(
    $SmokeTest,
    "--timeout-conversation",
    [string]$TimeoutConversacion
)

if ($MantenerAppAbierta) {
    $Arguments += "--keep-app-running"
}

& $PythonExe @Arguments
exit $LASTEXITCODE
