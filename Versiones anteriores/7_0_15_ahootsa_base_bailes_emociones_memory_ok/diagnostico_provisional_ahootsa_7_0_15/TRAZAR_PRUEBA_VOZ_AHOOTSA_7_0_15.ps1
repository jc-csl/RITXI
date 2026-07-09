param(
    [int]$Seconds = 90
)
$ErrorActionPreference = "Continue"
$LogRoot = "D:\RITXI\logs"
New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$OutFile = Join-Path $LogRoot "AHOOTSA_TRAZA_VOZ_${Stamp}.log"
function W($Text = "") { $Text | Tee-Object -FilePath $OutFile -Append }
W "Traza de prueba de voz Ahootsa: $(Get-Date -Format o)"
W "Durante los próximos $Seconds segundos prueba por voz:"
W "  1) lista de bailes"
W "  2) haz baile dos"
W "  3) haz un saludo"
W "  4) abre juego de parejas"
W ""
$start = Get-Date
while (((Get-Date) - $start).TotalSeconds -lt $Seconds) {
    Start-Sleep -Seconds 5
    W ""; W ("---- snapshot " + (Get-Date -Format o))
    try {
        Get-ChildItem $LogRoot -File -ErrorAction SilentlyContinue |
            Where-Object { $_.LastWriteTime -gt $start.AddSeconds(-10) } |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 8 |
            ForEach-Object {
                W ("FILE {0} size={1} last={2}" -f $_.FullName,$_.Length,$_.LastWriteTime.ToString('o'))
                Select-String -Path $_.FullName -Pattern "tool_start|tool_result|play_panel|play_emotion|memory|parejas|dance|baile|saludo|unknown tool|error|no he podido|transcript|function" -CaseSensitive:$false -ErrorAction SilentlyContinue |
                    Select-Object -Last 30 | ForEach-Object { W ("{0}:{1}: {2}" -f $_.Path,$_.LineNumber,$_.Line) }
            }
        $extra = Join-Path $env:LOCALAPPDATA "Reachy Mini Control\ahootsa_logs\play_emotion_audio.log"
        if (Test-Path $extra) {
            W "EXTRA $extra"
            Get-Content $extra -Tail 50 -ErrorAction SilentlyContinue | Tee-Object -FilePath $OutFile -Append
        }
    } catch { W ("ERROR snapshot: " + $_.Exception.Message) }
}
W ""; W "Traza guardada en: $OutFile"
Write-Host "Traza guardada en: $OutFile" -ForegroundColor Green
