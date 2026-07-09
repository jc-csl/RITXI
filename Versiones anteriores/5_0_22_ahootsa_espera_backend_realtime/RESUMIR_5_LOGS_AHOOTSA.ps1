# RESUMIR_5_LOGS_AHOOTSA.ps1
# Genera un resumen diagnostico de los ultimos logs de D:\RITXI\logs.

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$LogRoot = "D:\RITXI\logs"
if (-not (Test-Path -LiteralPath $LogRoot)) {
    Write-Host "[ERROR] No existe $LogRoot"
    exit 1
}

$Out = Join-Path $LogRoot ("ahootsa_resumen_logs_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".txt")

$Lines = @()
$Lines += "Ahootsa resumen logs $(Get-Date -Format o)"
$Lines += "LogRoot: $LogRoot"
$Lines += ""

$Files = Get-ChildItem -LiteralPath $LogRoot -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
$Lines += "Ultimos archivos:"
$Lines += ($Files | Select-Object -First 40 FullName, LastWriteTime, Length | Format-Table -AutoSize | Out-String)

$Patterns = @(
    "ERROR",
    "WARN",
    "Not Found",
    "voices/current",
    "voices/apply",
    "App ahootsa_realtime_ollama_app is running",
    "Uvicorn running on http://localhost:7860",
    "Loading tools for profile",
    "Found 33 tools",
    "Aiden",
    "Sohee"
)

$Lines += ""
$Lines += "Coincidencias relevantes:"
foreach ($Pattern in $Patterns) {
    $Lines += ""
    $Lines += "----- $Pattern -----"
    foreach ($F in ($Files | Select-Object -First 80)) {
        try {
            $Matches = Select-String -LiteralPath $F.FullName -Pattern $Pattern -SimpleMatch -ErrorAction SilentlyContinue | Select-Object -First 20
            foreach ($M in $Matches) {
                $Lines += "$($F.Name):$($M.LineNumber): $($M.Line)"
            }
        } catch {}
    }
}

$Lines | Set-Content -Encoding UTF8 -LiteralPath $Out
Write-Host "Resumen creado: $Out"
