# DIAGNOSTICAR_VOZ_SOHEE_TOTAL.ps1
# v0.4.42: diagnóstico corregido sin saltos de línea dentro de rutas.
# Comprueba Sohee en variables y voice.txt.

$ErrorActionPreference = "Continue"

function Join-Many([string[]]$Parts) {
    if ($Parts.Count -eq 0) { return "" }
    $p = $Parts[0]
    for ($i = 1; $i -lt $Parts.Count; $i++) {
        $p = Join-Path $p $Parts[$i]
    }
    return $p
}

function Safe-TestPath([string]$PathValue) {
    try {
        if ([string]::IsNullOrWhiteSpace($PathValue)) { return $false }
        return Test-Path -LiteralPath $PathValue
    } catch {
        Write-Host "[AVISO] Ruta inválida: $PathValue" -ForegroundColor Yellow
        return $false
    }
}

$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$ProfileName = "ahootsa_realtime_es"

Write-Host "Variables de voz:"
foreach ($name in @(
    "AHOOTSA_VOICE",
    "OPENAI_REALTIME_VOICE",
    "REACHY_MINI_VOICE",
    "VOICE",
    "REALTIME_VOICE",
    "TTS_VOICE",
    "AUDIO_VOICE"
)) {
    Write-Host "$name=" ([Environment]::GetEnvironmentVariable($name, "User"))
}

Write-Host ""
Write-Host "voice.txt:"

$profiles = @(
    (Join-Many @($DesktopDir, "user_personalities", $ProfileName)),
    (Join-Many @($DesktopDir, "profiles", $ProfileName)),
    (Join-Many @($DesktopDir, "apps_venv", "Lib", "site-packages", "reachy_mini_conversation_app", "profiles", $ProfileName)),
    (Join-Many @($DesktopDir, "apps_venv", "Lib", "site-packages", "reachy_talk_data", "profiles", $ProfileName)),
    (Join-Many @($DesktopDir, "apps_venv", "Lib", "site-packages", "reachy_mini_conversation_app", "profiles", "default")),
    (Join-Many @($DesktopDir, "apps_venv", "Lib", "site-packages", "reachy_talk_data", "profiles", "default")),
    (Join-Many @($DesktopDir, "apps_venv", "Lib", "site-packages", "reachy_mini_conversation_app", "external_content", "external_profiles", "starter_profile"))
)

foreach ($p in $profiles) {
    $v = Join-Path $p "voice.txt"
    if (Safe-TestPath $v) {
        Write-Host "$v ->" (Get-Content -LiteralPath $v -Raw -Encoding UTF8)
    } else {
        Write-Host "$v -> NO EXISTE"
    }
}

Write-Host ""
Write-Host "Archivos que contienen Aiden como configuración real de voz:"
$roots = @(
    $DesktopDir,
    (Join-Many @($DesktopDir, "apps_venv", "Lib", "site-packages", "reachy_mini_conversation_app")),
    (Join-Many @($DesktopDir, "apps_venv", "Lib", "site-packages", "reachy_talk_data"))
)

foreach ($root in $roots) {
    if (-not (Safe-TestPath $root)) { continue }

    Get-ChildItem -LiteralPath $root -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Extension -match "\.(json|toml|yaml|yml|ini|cfg|env)$" } |
        Select-String -Pattern "Aiden|aiden" -CaseSensitive:$false |
        Select-Object -First 30 |
        ForEach-Object { Write-Host $_.Path ":" $_.Line.Trim() }
}

Write-Host ""
Write-Host "Nota:"
Write-Host "Las apariciones de Aiden dentro de instructions.txt no significan que la voz activa sea Aiden."
Write-Host "En v0.4.42 el diagnóstico ya no cuenta instructions.txt como configuración de voz."
