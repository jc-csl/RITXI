# CONFIGURAR_RECORDATORIO_IDLE_AHOOTSA.ps1
# Configura el recordatorio de presencia.
#
# IMPORTANTE v0.4.44:
# El recordatorio hablado usa la voz SAPI de Windows, no la voz seleccionada de Reachy Desktop.
# Por eso está desactivado por defecto.
#
# Para activar expresamente:
#   powershell -ExecutionPolicy Bypass -File .\CONFIGURAR_RECORDATORIO_IDLE_AHOOTSA.ps1 -Enable -Seconds 20 -RepeatSeconds 60
#
# Para desactivar:
#   powershell -ExecutionPolicy Bypass -File .\CONFIGURAR_RECORDATORIO_IDLE_AHOOTSA.ps1 -Disable

param(
    [switch]$Enable,
    [switch]$Disable,
    [int]$Seconds = 20,
    [int]$RepeatSeconds = 60,
    [string]$Text = "Sigo aquí. Cuando quieras, podemos jugar o hacer otra actividad."
)

if ($Disable -or -not $Enable) {
    [Environment]::SetEnvironmentVariable("AHOOTSA_IDLE_REMINDER_ENABLED", "0", "User")
    [Environment]::SetEnvironmentVariable("AHOOTSA_IDLE_REMINDER_SECONDS", $null, "User")
    [Environment]::SetEnvironmentVariable("AHOOTSA_IDLE_REMINDER_REPEAT_SECONDS", $null, "User")
    [Environment]::SetEnvironmentVariable("AHOOTSA_IDLE_REMINDER_TEXT", $null, "User")
    Write-Host "Recordatorio idle hablado desactivado."
    Write-Host "Motivo: usa voz de Windows y puede mezclarse con la voz de Reachy."
    exit 0
}

[Environment]::SetEnvironmentVariable("AHOOTSA_IDLE_REMINDER_ENABLED", "1", "User")
[Environment]::SetEnvironmentVariable("AHOOTSA_IDLE_REMINDER_SECONDS", [string]$Seconds, "User")
[Environment]::SetEnvironmentVariable("AHOOTSA_IDLE_REMINDER_REPEAT_SECONDS", [string]$RepeatSeconds, "User")
[Environment]::SetEnvironmentVariable("AHOOTSA_IDLE_REMINDER_TEXT", $Text, "User")

Write-Host "Recordatorio idle hablado activado."
Write-Host "Primer aviso: $Seconds segundos."
Write-Host "Repetición: $RepeatSeconds segundos."
Write-Host "Texto: $Text"
Write-Host "Aviso: se escuchará con voz de Windows, no con la voz de Reachy Desktop."
Write-Host "Cierra y vuelve a abrir Reachy Mini Desktop."
