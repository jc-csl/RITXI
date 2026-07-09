$LogRoot = "D:\RITXI\logs"
$out = Join-Path $LogRoot "ULTIMA_EJECUCION_AHOOTSA_5_0_44_RESUMEN.txt"
$files = Get-ChildItem $LogRoot -Filter "ahootsa5_*" -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 6
"Resumen generado: $(Get-Date -Format o)" | Set-Content -Encoding UTF8 -LiteralPath $out
foreach ($f in $files) {
    "`n------------------------------------------------------------" | Add-Content -Encoding UTF8 -LiteralPath $out
    "Archivo: $($f.FullName)" | Add-Content -Encoding UTF8 -LiteralPath $out
    "Tamaño: $($f.Length) bytes" | Add-Content -Encoding UTF8 -LiteralPath $out
    Get-Content -LiteralPath $f.FullName -Tail 120 | Where-Object { $_ -match "ERROR|WARN|Traceback|Exception|404|timeout|Ollama|camera|HF|backend|tool_result|tool_start|failed|no responde" } | Add-Content -Encoding UTF8 -LiteralPath $out
}
Write-Host $out
