param([int]$AppPort=7860, [string]$OllamaModel="llama3.2:3b")
$ErrorActionPreference="Continue"
Write-Host "== Comprobacion Ahootsa 5.0.43 =="
Write-Host "`nOllama list:"
try { ollama list } catch { Write-Host "Ollama CLI no responde: $($_.Exception.Message)" }
Write-Host "`nOllama API tags:"
try { Invoke-RestMethod "http://127.0.0.1:11434/api/tags" -TimeoutSec 5 | ConvertTo-Json -Depth 6 } catch { Write-Host $_.Exception.Message }
Write-Host "`nOllama generate directo:"
try { $body=@{model=$OllamaModel;prompt='Responde solo OK';stream=$false;options=@{num_predict=8}}|ConvertTo-Json -Compress -Depth 5; Invoke-RestMethod -Method POST "http://127.0.0.1:11434/api/generate" -Body $body -ContentType "application/json" -TimeoutSec 20 | ConvertTo-Json -Depth 6 } catch { Write-Host $_.Exception.Message }
Write-Host "`nAhootsa /status:"
try { Invoke-RestMethod "http://127.0.0.1:$AppPort/status" -TimeoutSec 5 | ConvertTo-Json -Depth 6 } catch { Write-Host $_.Exception.Message }
Write-Host "`nAhootsa /ollama/status:"
try { Invoke-RestMethod "http://127.0.0.1:$AppPort/ollama/status" -TimeoutSec 5 | ConvertTo-Json -Depth 6 } catch { Write-Host $_.Exception.Message }
Write-Host "`nAhootsa /ollama/ask:"
try { $body=@{prompt='Di hola de forma breve'}|ConvertTo-Json -Compress; Invoke-RestMethod -Method POST "http://127.0.0.1:$AppPort/ollama/ask" -Body $body -ContentType "application/json" -TimeoutSec 35 | ConvertTo-Json -Depth 6 } catch { Write-Host $_.Exception.Message }
Write-Host "`nAhootsa /ask_ollama alias:"
try { $body=@{prompt='Di OK si escuchas'}|ConvertTo-Json -Compress; Invoke-RestMethod -Method POST "http://127.0.0.1:$AppPort/ask_ollama" -Body $body -ContentType "application/json" -TimeoutSec 35 | ConvertTo-Json -Depth 6 } catch { Write-Host $_.Exception.Message }
Write-Host "`nCamera health:"
try { Invoke-RestMethod "http://127.0.0.1:$AppPort/camera/health" -TimeoutSec 5 | ConvertTo-Json -Depth 6 } catch { Write-Host $_.Exception.Message }
Write-Host "`nPrueba camara en: http://127.0.0.1:$AppPort/camera/page"
