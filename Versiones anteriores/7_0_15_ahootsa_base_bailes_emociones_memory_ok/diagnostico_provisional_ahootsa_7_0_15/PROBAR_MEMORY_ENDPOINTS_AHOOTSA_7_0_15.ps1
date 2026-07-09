param(
    [string]$BaseUrl = "http://127.0.0.1:7860",
    [switch]$Reset,
    [switch]$Choose
)
$ErrorActionPreference = "Continue"
$LogRoot = "D:\RITXI\logs"
New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$OutFile = Join-Path $LogRoot "AHOOTSA_MEMORY_ENDPOINTS_${Stamp}.log"
function W($Text = "") { $Text | Tee-Object -FilePath $OutFile -Append }
function Call($Name, $Url) {
    W ""; W "--- $Name"; W $Url
    try {
        $r = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 8
        W ("HTTP " + [int]$r.StatusCode + " length=" + $r.Content.Length)
        $txt = $r.Content
        if ($txt.Length -gt 2500) { $txt = $txt.Substring(0,2500) + " ...[recortado]" }
        W $txt
    } catch { W ("ERROR: " + $_.Exception.Message) }
}
W "Prueba endpoints Memory Ahootsa: $(Get-Date -Format o)"
$BaseUrl = $BaseUrl.TrimEnd('/')
Call "Panel" "$BaseUrl/ahootsa"
Call "Juegos" "$BaseUrl/memory/games"
Call "Estado inicial" "$BaseUrl/memory/state"
Call "Pagina HTML juego" "$BaseUrl/memory/page?game_id=animales&reset=0"
if ($Reset) { Call "Reset animales" "$BaseUrl/memory/reset?game_id=animales"; Call "Estado tras reset" "$BaseUrl/memory/state" }
if ($Choose) { Call "Elegir cartas 1 y 2" "$BaseUrl/memory/choose?first=1&second=2"; Call "Estado tras elegir" "$BaseUrl/memory/state" }
W ""; W "Guardado en: $OutFile"
Write-Host "Guardado en: $OutFile" -ForegroundColor Green
