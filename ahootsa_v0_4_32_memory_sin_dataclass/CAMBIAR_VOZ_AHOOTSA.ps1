# CAMBIAR_VOZ_AHOOTSA.ps1
# Cambia la voz del perfil Ahootsa sin modificar el código original de la app oficial.
# Escribe voice.txt en el perfil fuente y en las copias usadas por Reachy Mini Desktop.
#
# Uso:
#   powershell -ExecutionPolicy Bypass -File .\CAMBIAR_VOZ_AHOOTSA.ps1
#   powershell -ExecutionPolicy Bypass -File .\CAMBIAR_VOZ_AHOOTSA.ps1 -Voice Coral

param(
    [string]$Voice = ""
)

$ErrorActionPreference = "Continue"

function Header($Text) {
    Write-Host ""
    Write-Host "============================================"
    Write-Host " $Text"
    Write-Host "============================================"
}
function Info($Text) { Write-Host "[INFO] $Text" }
function Warn($Text) { Write-Host "[AVISO] $Text" -ForegroundColor Yellow }
function Fail($Text) { Write-Host "[ERROR] $Text" -ForegroundColor Red; exit 1 }

Header "Cambiar voz Ahootsa"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProfileName = "ahootsa_realtime_es"
$DesktopDir = Join-Path $env:LOCALAPPDATA "Reachy Mini Control"
$SourceProfile = Join-Path $Root "src\ahootsa_realtime_ollama_desktop_app\profiles\$ProfileName"

# Voces candidatas. La disponibilidad exacta depende del backend realtime que use la app oficial.
# Si una voz no está soportada, la app puede volver a una voz por defecto.
$voices = @(
    @{Name="Coral";    Note="Recomendada para probar español natural, voz clara"},
    @{Name="Sage";     Note="Alternativa suave y clara"},
    @{Name="Shimmer";  Note="Voz suave"},
    @{Name="Alloy";    Note="Voz neutra, menos expresiva"},
    @{Name="Ash";      Note="Alternativa natural si está disponible"},
    @{Name="Ballad";   Note="Alternativa expresiva si está disponible"},
    @{Name="Verse";    Note="Alternativa si está disponible"},
    @{Name="Serena";   Note="Voz anterior/base"}
)

if (-not $Voice) {
    Write-Host "Elige una voz:"
    for ($i=0; $i -lt $voices.Count; $i++) {
        $n = $i + 1
        Write-Host ("[{0}] {1} - {2}" -f $n, $voices[$i].Name, $voices[$i].Note)
    }
    $choice = Read-Host "Número"
    if ($choice -notmatch "^\d+$") { Fail "Opción no válida." }
    $idx = [int]$choice - 1
    if ($idx -lt 0 -or $idx -ge $voices.Count) { Fail "Número fuera de rango." }
    $Voice = $voices[$idx].Name
}

$Voice = $Voice.Trim()
if (-not $Voice) { Fail "Voz vacía." }

Info "Voz seleccionada: $Voice"

$destinations = New-Object System.Collections.Generic.List[string]

if (Test-Path $SourceProfile) {
    $destinations.Add((Join-Path $SourceProfile "voice.txt"))
} else {
    Warn "No existe perfil fuente: $SourceProfile"
}

if (Test-Path $DesktopDir) {
    $destinations.Add((Join-Path $DesktopDir "user_personalities\$ProfileName\voice.txt"))
    $destinations.Add((Join-Path $DesktopDir "profiles\$ProfileName\voice.txt"))
    $destinations.Add((Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_mini_conversation_app\profiles\$ProfileName\voice.txt"))
    $destinations.Add((Join-Path $DesktopDir "apps_venv\Lib\site-packages\reachy_talk_data\profiles\$ProfileName\voice.txt"))
}

$unique = $destinations | Sort-Object -Unique

foreach ($file in $unique) {
    $dir = Split-Path -Parent $file
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
    Set-Content -Encoding UTF8 -Path $file -Value $Voice
    Info "voice.txt actualizado: $file"
}

# Variable de apoyo, por si el backend la lee en algún punto.
[Environment]::SetEnvironmentVariable("AHOOTSA_VOICE", $Voice, "User")
Info "Variable de usuario AHOOTSA_VOICE=$Voice"

Header "Comprobación"
foreach ($file in $unique) {
    if (Test-Path $file) {
        Write-Host "$file -> $(Get-Content $file -Raw -Encoding UTF8)"
    }
}

Header "Final"
Write-Host "Cierra completamente Reachy Mini Desktop y vuelve a abrir Ahootsa."
Write-Host "Prueba una frase corta para comparar la voz."
Write-Host "Si la voz no cambia, puede que el backend realtime no soporte ese nombre de voz. Prueba otra, por ejemplo Sage o Shimmer."
