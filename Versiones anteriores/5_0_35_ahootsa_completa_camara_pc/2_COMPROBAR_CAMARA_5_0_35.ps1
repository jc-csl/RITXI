param(
    [string]$BaseUrl = "http://127.0.0.1:8000"
)
$ErrorActionPreference = "Continue"
Write-Host "Comprobando endpoints de camara en $BaseUrl"
try {
    $latest = Invoke-RestMethod -Uri "$BaseUrl/camera/latest" -Method Get -TimeoutSec 5
    $latest | ConvertTo-Json -Depth 5
} catch {
    Write-Host "[WARN] /camera/latest no responde todavia. Arranca Ahootsa y prueba de nuevo."
    Write-Host $_.Exception.Message
}
