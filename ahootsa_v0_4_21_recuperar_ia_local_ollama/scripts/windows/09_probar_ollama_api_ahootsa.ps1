$ErrorActionPreference = "Stop"
Write-Host "Probando Ollama ahootsa-local:latest..." -ForegroundColor Cyan
Invoke-RestMethod `
  -Uri "http://127.0.0.1:11434/api/chat" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{
    "model": "ahootsa-local:latest",
    "stream": false,
    "messages": [
      {"role": "user", "content": "Hola Ahootsa, responde en español. ¿Quién eres?"}
    ]
  }'
