# LIMPIAR_5_OLLAMA_COMO_CEREBRO.ps1
# Borra variables del enfoque 5.0.8. ask_ollama vuelve a ser actividad opcional.

[Environment]::SetEnvironmentVariable("AHOOTSA_USE_OLLAMA_AS_BRAIN", $null, "User")
Remove-Item -Path "Env:AHOOTSA_USE_OLLAMA_AS_BRAIN" -ErrorAction SilentlyContinue
[Environment]::SetEnvironmentVariable("AHOOTSA_OLLAMA_TIMEOUT_SECONDS", "45", "User")
$env:AHOOTSA_OLLAMA_TIMEOUT_SECONDS = "45"
Write-Host "[OK] ask_ollama queda como actividad opcional. Timeout local IA = 45."
