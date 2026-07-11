param(
    [string]$LogRoot = "D:\RITXI\logs",
    [int]$TailLines = 180,
    [string]$Session = ""
)
$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null
$NowStamp = Get-Date -Format "yyyyMMdd_HHmmss"
$Out = Join-Path $LogRoot "AHOOTSA7_RESUMEN_$NowStamp.log"

function Add-SafeLine {
    param([string]$Path, [string]$Line)
    try {
        $fs = [System.IO.File]::Open($Path, [System.IO.FileMode]::Append, [System.IO.FileAccess]::Write, [System.IO.FileShare]::ReadWrite)
        try {
            $sw = New-Object System.IO.StreamWriter($fs, [System.Text.UTF8Encoding]::new($false))
            try { $sw.WriteLine($Line) } finally { $sw.Dispose() }
        } finally { $fs.Dispose() }
    } catch {
        Write-Host "[WARN] No se pudo escribir en resumen: $($_.Exception.Message)"
    }
}
function Add-SafeText {
    param([string]$Path, [string[]]$Lines)
    foreach($line in $Lines){ Add-SafeLine -Path $Path -Line $line }
}

# Crear archivo nuevo timestamped. No se reutiliza AHOOTSA7_ULTIMO_RESUMEN.log para evitar bloqueos.
try { "" | Set-Content -Encoding UTF8 -LiteralPath $Out -Force } catch {}

$all = Get-ChildItem -LiteralPath $LogRoot -Filter "ahootsa7_*" -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match '^ahootsa7_(\d{8}_\d{6})_(pantalla|runtime|eventos)\.(log|jsonl)$' }

if (-not $Session) {
    $sessions = $all | ForEach-Object {
        if ($_.Name -match '^ahootsa7_(\d{8}_\d{6})_') {
            [PSCustomObject]@{ Session = $Matches[1]; LastWriteTime = $_.LastWriteTime }
        }
    } | Group-Object Session | ForEach-Object {
        [PSCustomObject]@{ Session = $_.Name; LastWriteTime = ($_.Group | Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime }
    } | Sort-Object LastWriteTime -Descending
    if ($sessions) { $Session = $sessions[0].Session }
}

Add-SafeText -Path $Out -Lines @(
    "Resumen Ahootsa 7",
    "Generado: $(Get-Date -Format o)",
    "LogRoot: $LogRoot",
    "Sesión analizada: $Session",
    "Nota: este archivo tiene timestamp y solo incluye datos de la última ejecución seleccionada.",
    ""
)

if (-not $Session) {
    Add-SafeLine -Path $Out -Line "No se han encontrado logs ahootsa7_YYYYMMDD_HHMMSS en $LogRoot."
    Write-Host "Resumen creado: $Out"
    exit 0
}

$files = $all | Where-Object { $_.Name -like "ahootsa7_$Session*" } | Sort-Object Name
if (-not $files) {
    Add-SafeLine -Path $Out -Line "No se han encontrado archivos para la sesión $Session."
    Write-Host "Resumen creado: $Out"
    exit 0
}

foreach($f in $files){
    Add-SafeText -Path $Out -Lines @(
        "",
        "------------------------------------------------------------",
        "Archivo: $($f.FullName)",
        "Tamaño: $($f.Length) bytes",
        "Últimas $TailLines líneas:"
    )
    try {
        $lines = Get-Content -LiteralPath $f.FullName -Tail $TailLines -Encoding UTF8 -ErrorAction Stop
        Add-SafeText -Path $Out -Lines $lines
    } catch {
        Add-SafeLine -Path $Out -Line "No se pudo leer: $($_.Exception.Message)"
    }
}

Add-SafeText -Path $Out -Lines @("", "==================== FILTRO ÚTIL PARA DEPURAR ====================")
$patterns = "ERROR|WARN|Traceback|Exception|RuntimeError|HTTPError|ModuleNotFound|404|500|timeout|tiempo de espera|pygame|Ollama|camera|cámara|mic|audio|HF_REALTIME|memory|parejas|iframe|choose_memory|connected=False|can_proceed=False"
foreach($f in $files){
    try {
        $matches = Select-String -LiteralPath $f.FullName -Pattern $patterns -CaseSensitive:$false -ErrorAction Stop | Select-Object -Last 120
        foreach($m in $matches){ Add-SafeLine -Path $Out -Line "$($f.Name):$($m.LineNumber): $($m.Line)" }
    } catch {}
}

Add-SafeText -Path $Out -Lines @("", "==================== RESUMEN RÁPIDO ====================")
try {
    $txt = Get-Content -LiteralPath $Out -Encoding UTF8 -ErrorAction Stop
    $errCount = ($txt | Select-String -Pattern "ERROR|Traceback|RuntimeError|Exception|500" -CaseSensitive:$false).Count
    $warnCount = ($txt | Select-String -Pattern "WARN|WARNING|404|timeout|tiempo de espera" -CaseSensitive:$false).Count
    Add-SafeLine -Path $Out -Line "Errores/tracebacks detectados en resumen: $errCount"
    Add-SafeLine -Path $Out -Line "Warnings/404/timeouts detectados en resumen: $warnCount"
} catch {}

# Pointer pequeño con el último resumen; si está bloqueado no afecta al resumen real.
$Pointer = Join-Path $LogRoot "AHOOTSA7_ULTIMO_RESUMEN_POINTER.txt"
try { $Out | Set-Content -Encoding UTF8 -LiteralPath $Pointer -Force } catch {}

Write-Host "Resumen creado: $Out"
Write-Host "Solo incluye la sesión: $Session"
Write-Host "Pointer: $Pointer"
