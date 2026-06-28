$ErrorActionPreference = "Stop"
$body = @{
    model = "ahootsa-local"
    stream = $false
    messages = @(@{ role = "user"; content = "Hola Ahootsa, ¿quién eres?" })
} | ConvertTo-Json -Depth 10

Invoke-RestMethod `
  -Uri "http://127.0.0.1:11434/api/chat" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body | ConvertTo-Json -Depth 10
