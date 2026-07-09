param(
    [string]$LogRoot = "D:\RITXI\logs",
    [int]$TailLines = 260
)

$ErrorActionPreference = "Continue"

if (-not (Test-Path -LiteralPath $LogRoot)) {
    throw "No existe la carpeta de logs: $LogRoot"
}

$patterns = @(
    "ERROR", "WARN", "Traceback", "Exception", "ParserError", "IOException",
    "ModuleNotFound", "No module named", "No se", "no puede", "no pudo",
    "404", "Not Found", "failed", "fallo", "timeout", "Add-Content",
    "connected=False", "can_proceed=False", "backend_status_ok=false",
    "La expresion de asignacion no es valida", "InvalidLeftHandSide"
)
$regex = ($patterns | ForEach-Object { [regex]::Escape($_) }) -join "|"

$info = Join-Path $LogRoot "ULTIMA_EJECUCION_AHOOTSA_INFO.txt"
$session = "sin_session"
if (Test-Path -LiteralPath $info) {
    $m = Select-String -LiteralPath $info -Pattern "^timestamp=(\d{8}_\d{6})" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($m -and $m.Matches.Count -gt 0) { $session = $m.Matches[0].Groups[1].Value }
}
if ($session -eq "sin_session") {
    $latestPantalla = Get-ChildItem -LiteralPath $LogRoot -Filter "ahootsa5_*_pantalla.log" -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latestPantalla -and $latestPantalla.Name -match "ahootsa5_(\d{8}_\d{6})_pantalla\.log") { $session = $Matches[1] }
}

$candidates = @()
if ($session -ne "sin_session") {
    $candidates += Get-ChildItem -LiteralPath $LogRoot -Filter "ahootsa5_${session}_*" -File -ErrorAction SilentlyContinue
} else {
    $candidates += Get-ChildItem -LiteralPath $LogRoot -Filter "ahootsa5_*" -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 5
}

$outLatest = Join-Path $LogRoot "ULTIMA_EJECUCION_AHOOTSA_CORRECCION.log"
$outTimestamp = Join-Path $LogRoot "ahootsa5_${session}_diagnostico_resumen.log"

$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("============================================================")
$lines.Add("Ahootsa 5.0.32 - resumen util para corregir codigo")
$lines.Add("============================================================")
$lines.Add("generado=$(Get-Date -Format o)")
$lines.Add("session=$session")
$lines.Add("log_root=$LogRoot")
$lines.Add("criterio=errores/avisos/patrones relevantes + cola final")
$lines.Add("")

if (Test-Path -LiteralPath $info) {
    $lines.Add("[INFO_ULTIMA_EJECUCION]")
    foreach ($l in (Get-Content -LiteralPath $info -ErrorAction SilentlyContinue)) { $lines.Add($l) }
    $lines.Add("")
}

foreach ($file in ($candidates | Sort-Object Name)) {
    $lines.Add("------------------------------------------------------------")
    $lines.Add("ARCHIVO: $($file.FullName)")
    $lines.Add("last_write=$($file.LastWriteTime.ToString('o')) size_bytes=$($file.Length)")
    $lines.Add("------------------------------------------------------------")
    try {
        $content = Get-Content -LiteralPath $file.FullName -Tail $TailLines -ErrorAction SilentlyContinue
        $interesting = $content | Where-Object { $_ -match $regex }
        if ($interesting.Count -gt 0) {
            $lines.Add("[LINEAS_RELEVANTES]")
            foreach ($l in $interesting) { $lines.Add($l) }
        } else {
            $lines.Add("[LINEAS_RELEVANTES] sin coincidencias en las ultimas $TailLines lineas")
        }
        $lines.Add("")
        $lines.Add("[COLA_FINAL]")
        foreach ($l in ($content | Select-Object -Last 80)) { $lines.Add($l) }
    } catch {
        $lines.Add("[ERROR_LEYENDO] $($_.Exception.Message)")
    }
    $lines.Add("")
}

$lines | Set-Content -Encoding UTF8 -LiteralPath $outLatest
$lines | Set-Content -Encoding UTF8 -LiteralPath $outTimestamp

Write-Host "Resumen actualizado: $outLatest"
Write-Host "Copia timestamp:     $outTimestamp"
