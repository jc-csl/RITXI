param(
    [string]$LogRoot = "D:\RITXI\logs",
    [int]$TailLines = 120
)
$ErrorActionPreference = "Continue"
$Out = Join-Path $LogRoot "AHOOTSA7_ULTIMO_RESUMEN.log"
New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null
$files = Get-ChildItem -LiteralPath $LogRoot -Filter "ahootsa7_*" -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
"Resumen Ahootsa 7 generado: $(Get-Date -Format o)" | Set-Content -Encoding UTF8 -LiteralPath $Out
foreach($f in $files | Select-Object -First 10){
    "`n------------------------------------------------------------`nArchivo: $($f.FullName)`nTamaño: $($f.Length) bytes`nÚltimas $TailLines líneas:" | Add-Content -Encoding UTF8 -LiteralPath $Out
    try { Get-Content -LiteralPath $f.FullName -Tail $TailLines -Encoding UTF8 | Add-Content -Encoding UTF8 -LiteralPath $Out } catch { "No se pudo leer: $($_.Exception.Message)" | Add-Content -Encoding UTF8 -LiteralPath $Out }
}
"`n==================== FILTRO ERRORES / WARNINGS ====================" | Add-Content -Encoding UTF8 -LiteralPath $Out
foreach($f in $files | Select-Object -First 30){
    try {
        Select-String -LiteralPath $f.FullName -Pattern "ERROR|WARN|Traceback|Exception|HTTPError|ModuleNotFound|404|500|pygame|Ollama|camera|cámara|mic|audio|HF_REALTIME|connected=False|can_proceed=False" -CaseSensitive:$false |
        Select-Object -Last 80 |
        ForEach-Object { "$($f.Name):$($_.LineNumber): $($_.Line)" | Add-Content -Encoding UTF8 -LiteralPath $Out }
    } catch {}
}
Write-Host "Resumen creado: $Out"
