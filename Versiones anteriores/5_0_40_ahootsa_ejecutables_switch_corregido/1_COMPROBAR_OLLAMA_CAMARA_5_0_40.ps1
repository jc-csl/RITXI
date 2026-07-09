
param([string]$OllamaModel="llama3.2:3b")
$ErrorActionPreference="Continue"
Write-Host "=== Ollama list ==="
try { & ollama list } catch { Write-Host "ERROR ollama list: $($_.Exception.Message)" }
Write-Host "`n=== Ollama API tags ==="
try { (Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 5).Content } catch { Write-Host "ERROR /api/tags: $($_.Exception.Message)" }
Write-Host "`n=== Ahootsa endpoints si esta abierta ==="
foreach($u in @("http://127.0.0.1:7860/status","http://127.0.0.1:7860/ollama/status","http://127.0.0.1:7860/llm/status","http://127.0.0.1:7860/camera/health","http://127.0.0.1:7860/camera/page")){
  Write-Host "--- $u"
  try { $r=(Invoke-WebRequest -UseBasicParsing -Uri $u -TimeoutSec 6); $r.StatusCode; $r.Content.Substring(0,[Math]::Min(600,$r.Content.Length)) } catch { Write-Host "ERROR: $($_.Exception.Message)" }
}
