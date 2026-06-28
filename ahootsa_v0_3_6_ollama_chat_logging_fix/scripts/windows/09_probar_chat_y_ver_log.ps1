$ErrorActionPreference = "Continue"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Ahootsa v0.3.6 - probar chat y log" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Asegúrate de que Ahootsa Ollama Local está arrancada en Reachy Mini Desktop." -ForegroundColor Yellow
Write-Host ""

Write-Host "Estado:" -ForegroundColor Cyan
Invoke-RestMethod http://127.0.0.1:7862/api/status | Format-List

Write-Host "Probando /api/chat:" -ForegroundColor Cyan
Invoke-RestMethod `
  -Uri "http://127.0.0.1:7862/api/chat" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"message":"Hola, ¿cómo te llamas?"}' | Format-List

Write-Host "Ruta del log:" -ForegroundColor Cyan
Invoke-RestMethod http://127.0.0.1:7862/api/log-path | Format-List

Write-Host ""
Write-Host "También puedes abrir: http://127.0.0.1:7862/api/log" -ForegroundColor Green
