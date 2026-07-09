param(
    [string]$LogRoot = "D:\RITXI\logs"
)
$ErrorActionPreference = "Continue"
$Out = Join-Path $LogRoot "ULTIMA_EJECUCION_AHOOTSA_CORRECCION.log"
$Info = Join-Path $LogRoot "ULTIMA_EJECUCION_AHOOTSA_INFO.txt"
$Session = $null
if (Test-Path -LiteralPath $Info) {
    $m = Select-String -LiteralPath $Info -Pattern '^timestamp=(.+)$' | Select-Object -First 1
    if ($m) { $Session = $m.Matches[0].Groups[1].Value.Trim() }
}
if (-not $Session) {
    $last = Get-ChildItem -LiteralPath $LogRoot -Filter "ahootsa5_*_pantalla.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($last -and $last.Name -match 'ahootsa5_(\d{8}_\d{6})_') { $Session = $Matches[1] }
}
if (-not $Session) { throw "No encuentro ultima sesion en $LogRoot" }
$files = Get-ChildItem -LiteralPath $LogRoot -Filter "ahootsa5_${Session}_*" | Sort-Object Name
$patterns = 'ERROR|WARN|Traceback|Exception|404|Not Found|timeout|connected=False|can_proceed=False|Add-Content|ParserError|InvalidLeftHandSide|ModuleNotFoundError|No module named|audio|speech|pyttsx3|SAPI|voice|voices/current'
@("Ahootsa 5.0.34 - resumen ultima ejecucion", "session=$Session", "fecha=$(Get-Date -Format o)", "archivos=$($files.Count)", "") | Set-Content -Encoding UTF8 -LiteralPath $Out
foreach ($f in $files) {
    Add-Content -Encoding UTF8 -LiteralPath $Out -Value "============================================================"
    Add-Content -Encoding UTF8 -LiteralPath $Out -Value $f.FullName
    Add-Content -Encoding UTF8 -LiteralPath $Out -Value "============================================================"
    try {
        Select-String -LiteralPath $f.FullName -Pattern $patterns -CaseSensitive:$false | Select-Object -Last 200 | ForEach-Object {
            Add-Content -Encoding UTF8 -LiteralPath $Out -Value $_.Line
        }
    } catch {
        Add-Content -Encoding UTF8 -LiteralPath $Out -Value "[WARN] No se pudo leer: $($_.Exception.Message)"
    }
    Add-Content -Encoding UTF8 -LiteralPath $Out -Value ""
}
Write-Host "Resumen creado: $Out"
