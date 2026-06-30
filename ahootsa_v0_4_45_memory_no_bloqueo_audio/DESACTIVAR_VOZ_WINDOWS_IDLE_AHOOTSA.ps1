# DESACTIVAR_VOZ_WINDOWS_IDLE_AHOOTSA.ps1
# Desactiva el recordatorio de presencia hablado con la voz de Windows.
# Motivo: esa voz se mezcla con la voz seleccionada en Reachy Desktop.

$ErrorActionPreference = "Continue"

function Header($Text) {
    Write-Host ""
    Write-Host "============================================"
    Write-Host " $Text"
    Write-Host "============================================"
}
function Info($Text) { Write-Host "[INFO] $Text" }

Header "Desactivar voz Windows idle Ahootsa"

$names = @(
    "AHOOTSA_IDLE_REMINDER_ENABLED",
    "AHOOTSA_IDLE_REMINDER_SECONDS",
    "AHOOTSA_IDLE_REMINDER_REPEAT_SECONDS",
    "AHOOTSA_IDLE_REMINDER_TEXT"
)

[Environment]::SetEnvironmentVariable("AHOOTSA_IDLE_REMINDER_ENABLED", "0", "User")
[Environment]::SetEnvironmentVariable("AHOOTSA_IDLE_REMINDER_ENABLED", "0", "Process")

foreach ($name in @(
    "AHOOTSA_IDLE_REMINDER_SECONDS",
    "AHOOTSA_IDLE_REMINDER_REPEAT_SECONDS",
    "AHOOTSA_IDLE_REMINDER_TEXT"
)) {
    [Environment]::SetEnvironmentVariable($name, $null, "User")
    [Environment]::SetEnvironmentVariable($name, $null, "Process")
}

Info "AHOOTSA_IDLE_REMINDER_ENABLED=0"
Info "El recordatorio hablado con voz de Windows queda desactivado."

Header "Final"
Write-Host "Cierra completamente Reachy Mini Desktop y vuelve a abrir Ahootsa."
Write-Host "Así solo debería escucharse la voz seleccionada por la app."
