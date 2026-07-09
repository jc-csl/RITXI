# RESUMIR_5_LOGS_AHOOTSA.ps1
# Resume la última ejecución simple Ahootsa 5.

param(
    [string]$Session = ""
)

$ErrorActionPreference = "Continue"
$LogRoot = "D:\RITXI\logs"

if (-not (Test-Path -LiteralPath $LogRoot)) {
    Write-Host "[ERROR] No existe $LogRoot"
    exit 1
}

if (-not $Session) {
    $last = Get-ChildItem -LiteralPath $LogRoot -File -Filter "ahootsa5_*_eventos.jsonl" -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if (-not $last) {
        Write-Host "[WARN] No encuentro eventos ahootsa5."
        exit 0
    }
    if ($last.Name -match "^ahootsa5_(.*)_eventos\.jsonl$") { $Session = $Matches[1] }
}

$screen = Join-Path $LogRoot ("ahootsa5_" + $Session + "_pantalla.log")
$events = Join-Path $LogRoot ("ahootsa5_" + $Session + "_eventos.jsonl")
$runtime = Join-Path $LogRoot ("ahootsa5_" + $Session + "_runtime.log")
$out = Join-Path $LogRoot ("ahootsa5_" + $Session + "_RESUMEN.txt")

$lines = @()
$lines += "Resumen Ahootsa 5 sesión $Session"
$lines += "Generado: $(Get-Date -Format o)"
$lines += ""
foreach ($f in @($screen, $events, $runtime)) {
    if (Test-Path $f) {
        $item = Get-Item $f
        $lines += "Archivo: $f"
        $lines += "Tamaño: $($item.Length) bytes"
        $lines += "Últimas 80 líneas:"
        $lines += (Get-Content -LiteralPath $f -Tail 80 -ErrorAction SilentlyContinue)
        $lines += ""
        $lines += "------------------------------------------------------------"
    } else {
        $lines += "Falta: $f"
    }
}
$lines | Set-Content -Encoding UTF8 -LiteralPath $out
Write-Host "[OK] Resumen creado: $out"
