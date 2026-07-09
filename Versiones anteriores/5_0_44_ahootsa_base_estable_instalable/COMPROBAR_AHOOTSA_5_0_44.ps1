param([string]$OllamaBaseUrl = "http://127.0.0.1:11434", [string]$OllamaModel = "llama3.2:3b")
$ErrorActionPreference = "Continue"
$Py = "$env:LOCALAPPDATA\Reachy Mini Control\apps_venv\Scripts\python.exe"
Write-Host "[1] Ahootsa import"; & $Py -c "import ahootsa_realtime_ollama_desktop_app as a; print(a.__version__)"
Write-Host "[2] Ollama tags"; try { Invoke-RestMethod -Uri "$OllamaBaseUrl/api/tags" -Method Get -TimeoutSec 5 | ConvertTo-Json -Depth 5 } catch { Write-Host $_.Exception.Message }
Write-Host "[3] Ollama chat test"; try { Invoke-RestMethod -Uri "$OllamaBaseUrl/api/chat" -Method Post -ContentType 'application/json' -Body (@{model=$OllamaModel;stream=$false;messages=@(@{role='user';content='Di hola en una frase.'})} | ConvertTo-Json -Depth 5) -TimeoutSec 25 | ConvertTo-Json -Depth 6 } catch { Write-Host $_.Exception.Message }
Write-Host "[4] Ahootsa web status"; try { Invoke-RestMethod -Uri "http://127.0.0.1:7860/ahootsa/status" -TimeoutSec 5 | ConvertTo-Json -Depth 6 } catch { Write-Host $_.Exception.Message }
