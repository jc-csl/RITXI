param([int]$AppPort = 7860, [string]$OllamaModel = "llama3.2:3b")
$ErrorActionPreference = "Continue"
Write-Host "== Comprobacion Ahootsa 5.0.41 =="
Write-Host "Ollama list:"
try { ollama list } catch { Write-Host "Ollama CLI no responde: $($_.Exception.Message)" }
Write-Host "`n/status:"
try { Invoke-RestMethod "http://127.0.0.1:$AppPort/status" | ConvertTo-Json -Depth 6 } catch { Write-Host $_.Exception.Message }
Write-Host "`n/ollama/status:"
try { Invoke-RestMethod "http://127.0.0.1:$AppPort/ollama/status" | ConvertTo-Json -Depth 6 } catch { Write-Host $_.Exception.Message }
Write-Host "`n/camera/health:"
try { Invoke-RestMethod "http://127.0.0.1:$AppPort/camera/health" | ConvertTo-Json -Depth 6 } catch { Write-Host $_.Exception.Message }
Write-Host "`nPrueba camara en: http://127.0.0.1:$AppPort/camera/page"
