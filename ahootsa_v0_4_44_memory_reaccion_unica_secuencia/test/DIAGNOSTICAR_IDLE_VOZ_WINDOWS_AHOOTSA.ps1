# DIAGNOSTICAR_IDLE_VOZ_WINDOWS_AHOOTSA.ps1
# Comprueba si está activo el recordatorio hablado con voz de Windows.

Write-Host "Variables de recordatorio idle:"
foreach ($name in @(
    "AHOOTSA_IDLE_REMINDER_ENABLED",
    "AHOOTSA_IDLE_REMINDER_SECONDS",
    "AHOOTSA_IDLE_REMINDER_REPEAT_SECONDS",
    "AHOOTSA_IDLE_REMINDER_TEXT"
)) {
    Write-Host "$name=" ([Environment]::GetEnvironmentVariable($name, "User"))
}

Write-Host ""
if ([Environment]::GetEnvironmentVariable("AHOOTSA_IDLE_REMINDER_ENABLED", "User") -eq "1") {
    Write-Host "AVISO: el recordatorio idle hablado está ACTIVO." -ForegroundColor Yellow
    Write-Host "Usa voz de Windows y puede mezclarse con la voz de Reachy."
    Write-Host "Para desactivarlo:"
    Write-Host "powershell -ExecutionPolicy Bypass -File .\DESACTIVAR_VOZ_WINDOWS_IDLE_AHOOTSA.ps1"
} else {
    Write-Host "OK: el recordatorio idle hablado está desactivado."
}
