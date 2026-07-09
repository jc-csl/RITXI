param(
    [int]$Seconds = 120,
    [string]$LogRoot = "D:\RITXI\logs"
)
$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$Out = Join-Path $LogRoot "AHOOTSA_TRAZA_COMUNICACION_VOZ_7_0_23_$Stamp.log"
function Add-Line([string]$Text = "") { Add-Content -LiteralPath $Out -Encoding UTF8 -Value $Text }
Add-Line "Ahootsa traza comunicacion voz 7.0.23 - actividades 3 niveles"
Add-Line "Inicio: $(Get-Date -Format o)"
Add-Line "Duracion_segundos: $Seconds"
Add-Line ""
Add-Line "Durante esta ventana di exactamente:"
Add-Line "1) actividades de comunicacion"
Add-Line "2) actividades faciles"
Add-Line "3) quiero practicar pedir comida"
Add-Line "4) vamos a mantener turnos"
Add-Line "5) quiero conversar"
Add-Line ""
Add-Line "El script recogera eventos recientes de D:\RITXI\logs relacionados con comunicacion y Ollama. Estas actividades NO deben llamar a Ollama."
Write-Host "Habla ahora con Ahootsa durante $Seconds segundos..."
Start-Sleep -Seconds $Seconds
Add-Line "Fin captura: $(Get-Date -Format o)"
Add-Line ""
Add-Line "===== EVENTOS RECIENTES FILTRADOS ====="
$cut = (Get-Date).AddMinutes(-20)
$files = Get-ChildItem -Path $LogRoot -File -ErrorAction SilentlyContinue | Where-Object { $_.LastWriteTime -ge $cut -and ($_.Name -like "ahootsa7_*" -or $_.Name -like "AHOOTSA*") } | Sort-Object LastWriteTime
$patterns = "communication|comunicacion|list_communication|start_communication|saludar|pedir_comida|pedir comida|mantener_turnos|mantener turnos|conversar|ask_ollama|tool_start|tool_result|duration_ms|conversation_events"
foreach ($f in $files) {
    try {
        $hits = Select-String -LiteralPath $f.FullName -Pattern $patterns -Encoding UTF8 -SimpleMatch:$false -ErrorAction SilentlyContinue
        if ($hits) {
            Add-Line ""
            Add-Line "--- $($f.Name) ---"
            foreach ($h in $hits) { Add-Line ("{0}:{1}: {2}" -f $f.Name, $h.LineNumber, $h.Line) }
        }
    } catch {}
}
Add-Line ""
Add-Line "Interpretacion: si no aparecen tool_start de list_communication_activities/start_communication_activity, HF no ha llamado a la herramienta. Si aparecen con duration_ms bajo, la demora no esta dentro de la herramienta."
Write-Host "Traza de voz guardada en $Out"
