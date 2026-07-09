
param([string]$LogRoot="D:\RITXI\logs")
$ErrorActionPreference="SilentlyContinue"
$out=Join-Path $LogRoot "ULTIMA_EJECUCION_AHOOTSA_5_0_40_RESUMEN.log"
$patterns="ERROR|WARN|Traceback|Exception|404|timeout|Ollama|ollama|HF|Hugging|camera|camara|getUserMedia|NotAllowedError|NotFoundError|winsound|pygame|pyttsx3|ahootsa-local|llama3.2|llm"
"Resumen Ahootsa 5.0.40 generado: $(Get-Date -Format o)" | Set-Content -LiteralPath $out -Encoding UTF8
Get-ChildItem -LiteralPath $LogRoot -File | Sort-Object LastWriteTime -Descending | Select-Object -First 16 | ForEach-Object {
  "`n------------------------------------------------------------`nArchivo: $($_.FullName)`nLastWrite: $($_.LastWriteTime.ToString('o')) Size: $($_.Length)" | Add-Content -LiteralPath $out -Encoding UTF8
  $rel=(Get-Content -LiteralPath $_.FullName -Tail 400 | Select-String -Pattern $patterns)
  if($rel){$rel | ForEach-Object {$_.Line} | Add-Content -LiteralPath $out -Encoding UTF8} else {"Sin coincidencias relevantes." | Add-Content -LiteralPath $out -Encoding UTF8}
}
Write-Host "Resumen: $out"
