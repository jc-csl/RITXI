# CONFIGURAR_RECORDATORIO_IDLE_AHOOTSA.ps1
param([int]$Seconds = 20, [int]$RepeatSeconds = 60, [string]$Text = "Sigo aquí. Cuando quieras, podemos jugar o hacer otra actividad.", [switch]$Disable)
if ($Disable) { [Environment]::SetEnvironmentVariable("AHOOTSA_IDLE_REMINDER_ENABLED", "0", "User"); Write-Host "Recordatorio idle desactivado."; exit 0 }
[Environment]::SetEnvironmentVariable("AHOOTSA_IDLE_REMINDER_ENABLED", "1", "User")
[Environment]::SetEnvironmentVariable("AHOOTSA_IDLE_REMINDER_SECONDS", [string]$Seconds, "User")
[Environment]::SetEnvironmentVariable("AHOOTSA_IDLE_REMINDER_REPEAT_SECONDS", [string]$RepeatSeconds, "User")
[Environment]::SetEnvironmentVariable("AHOOTSA_IDLE_REMINDER_TEXT", $Text, "User")
Write-Host "Recordatorio idle activado. Primer aviso: $Seconds segundos. Repetición: $RepeatSeconds segundos."
Write-Host "Cierra y vuelve a abrir Reachy Mini Desktop."
