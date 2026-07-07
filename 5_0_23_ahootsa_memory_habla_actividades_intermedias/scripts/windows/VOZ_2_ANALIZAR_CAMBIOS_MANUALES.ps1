# VOZ_2_ANALIZAR_CAMBIOS_MANUALES.ps1
# Ahootsa 5.0.23
# Analiza cambios de voz SIN snapshot previo grande.
# Busca solo archivos modificados despues del marcador, y solo candidatos razonables de configuracion/voz.

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$LogRoot = "D:\RITXI\logs"
if (-not (Test-Path -LiteralPath $LogRoot)) {
    New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null
}

# Preferir marcador ligero. Si no existe, intentar marcador antiguo para compatibilidad.
$Marker = Get-ChildItem -LiteralPath $LogRoot -Filter "voice_probe_marker_light_*.json" -File -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (-not $Marker) {
    $Marker = Get-ChildItem -LiteralPath $LogRoot -Filter "voice_probe_marker_*.json" -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
}

if (-not $Marker) {
    Write-Host "[ERROR] No encuentro marker. Ejecuta primero VOZ_1_INICIAR_MONITORIZACION_CAMBIO_MANUAL.ps1"
    exit 1
}

$MarkerData = Get-Content -Raw -Encoding UTF8 -LiteralPath $Marker.FullName | ConvertFrom-Json
$Session = [string]$MarkerData.session

if ($MarkerData.marker_time_utc) {
    $StartUtc = [datetime]$MarkerData.marker_time_utc
} else {
    $StartUtc = $Marker.LastWriteTimeUtc
}

$StartLocal = $StartUtc.ToLocalTime().AddSeconds(-2)

$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$SitePackages = Join-Path $DesktopDir "apps_venv\Lib\site-packages"

$Roots = @(
    $DesktopDir,
    (Join-Path $SitePackages "reachy_mini_conversation_app"),
    (Join-Path $SitePackages "reachy_talk_data"),
    (Join-Path $SitePackages "ahootsa_realtime_ollama_desktop_app")
) | Select-Object -Unique

$AllowedExtensions = @(".json", ".txt", ".env", ".ini", ".yaml", ".yml", ".toml", ".cfg", ".log")
$NamePattern = "voice|voices|audio|speaker|tts|settings|setting|config|profile|personality|prefs|preference|current"

$Candidates = @()

foreach ($Root in $Roots) {
    if (-not (Test-Path -LiteralPath $Root)) { continue }

    $Candidates += Get-ChildItem -LiteralPath $Root -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object {
            $_.LastWriteTime -ge $StartLocal -and
            $_.Length -lt 2MB -and
            (
                $AllowedExtensions -contains $_.Extension.ToLowerInvariant() -or
                $_.Name -match $NamePattern
            ) -and
            $_.FullName -notmatch "\\__pycache__\\" -and
            $_.FullName -notmatch "\\\.venv\\" -and
            $_.FullName -notmatch "\\node_modules\\"
        }
}

# Añadir siempre archivos de voz conocidos aunque no hayan cambiado, para comparacion.
$KnownVoiceFiles = @(
    (Join-Path $SitePackages "reachy_mini_conversation_app\profiles\ahootsa_realtime_es\voice.txt"),
    (Join-Path $SitePackages "reachy_mini_conversation_app\profiles\default\voice.txt"),
    (Join-Path $SitePackages "reachy_mini_conversation_app\profiles\starter_profile\voice.txt"),
    (Join-Path $SitePackages "reachy_talk_data\profiles\ahootsa_realtime_es\voice.txt"),
    (Join-Path $SitePackages "reachy_talk_data\profiles\default\voice.txt"),
    (Join-Path $SitePackages "ahootsa_realtime_ollama_desktop_app\profiles\ahootsa_realtime_es\voice.txt"),
    (Join-Path $SitePackages "ahootsa_realtime_ollama_desktop_app\profiles\default\voice.txt")
)

foreach ($F in $KnownVoiceFiles) {
    if (Test-Path -LiteralPath $F) {
        $Candidates += Get-Item -LiteralPath $F
    }
}

$Candidates = $Candidates | Sort-Object FullName -Unique

$Hits = @()
foreach ($F in ($Candidates | Sort-Object LastWriteTime -Descending | Select-Object -First 300)) {
    $ContainsSohee = $false
    $ContainsAiden = $false
    $ContainsVoice = $false
    $Excerpt = ""

    try {
        $Txt = Get-Content -Raw -Encoding UTF8 -LiteralPath $F.FullName -ErrorAction Stop
        $ContainsSohee = ($Txt -match "Sohee")
        $ContainsAiden = ($Txt -match "Aiden")
        $ContainsVoice = ($Txt -match "voice|Voice|VOICE|voices|audio|tts|speaker")

        if ($ContainsSohee -or $ContainsAiden -or $ContainsVoice -or $F.Name -match $NamePattern) {
            $Line = ($Txt -split "`r?`n" | Where-Object { $_ -match "Sohee|Aiden|voice|Voice|VOICE|voices|audio|tts|speaker" } | Select-Object -First 3) -join " | "
            if ($Line.Length -gt 500) { $Line = $Line.Substring(0, 500) }
            $Excerpt = $Line
        }
    } catch {}

    if ($ContainsSohee -or $ContainsAiden -or $ContainsVoice -or $F.Name -match $NamePattern) {
        $Hits += [pscustomobject]@{
            FullName = $F.FullName
            LastWriteTime = $F.LastWriteTime
            Length = $F.Length
            ChangedAfterMarker = ($F.LastWriteTime -ge $StartLocal)
            ContainsSohee = $ContainsSohee
            ContainsAiden = $ContainsAiden
            ContainsVoice = $ContainsVoice
            Excerpt = $Excerpt
        }
    }
}

$Report = Join-Path $LogRoot ("voice_probe_report_light_" + $Session + ".txt")
$Json = Join-Path $LogRoot ("voice_probe_report_light_" + $Session + ".json")

$Lines = @()
$Lines += "VOICE PROBE LIGHT REPORT $Session"
$Lines += "Marker: $($Marker.FullName)"
$Lines += "StartUtc: $($StartUtc.ToString("o"))"
$Lines += "StartLocalMinus2s: $($StartLocal.ToString("o"))"
$Lines += "Mode: no full snapshot"
$Lines += ""
$Lines += "Candidate count: $($Candidates.Count)"
$Lines += "Hit count: $($Hits.Count)"
$Lines += ""
$Lines += "Hits:"
$Lines += ($Hits | Sort-Object LastWriteTime -Descending | Format-Table -AutoSize | Out-String)

$Lines | Set-Content -Encoding UTF8 -LiteralPath $Report

[pscustomobject]@{
    session = $Session
    marker = $Marker.FullName
    start_utc = $StartUtc.ToString("o")
    mode = "light_no_snapshot"
    candidate_count = $Candidates.Count
    hit_count = $Hits.Count
    hits = $Hits
} | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 -LiteralPath $Json

Write-Host ""
Write-Host "============================================================"
Write-Host "Analisis ligero de cambio manual de voz"
Write-Host "============================================================"
Write-Host "Report TXT:  $Report"
Write-Host "Report JSON: $Json"
Write-Host ""
Write-Host "Archivos candidatos:"
Write-Host "  $($Candidates.Count)"
Write-Host "Coincidencias:"
$Hits | Sort-Object LastWriteTime -Descending | Format-Table -AutoSize
