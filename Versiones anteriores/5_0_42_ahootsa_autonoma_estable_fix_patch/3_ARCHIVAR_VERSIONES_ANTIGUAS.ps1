param([string]$Confirmar = "NO")
$ErrorActionPreference = "Stop"
if ($Confirmar.ToUpperInvariant() -ne "SI") {
    Write-Host "Este script mueve versiones antiguas a D:\RITXI\_versiones_antiguas_ahootsa."
    Write-Host "Ejecuta: powershell -ExecutionPolicy Bypass -File .\3_ARCHIVAR_VERSIONES_ANTIGUAS.ps1 -Confirmar SI"
    exit 0
}
$Archive = "D:\RITXI\_versiones_antiguas_ahootsa"
New-Item -ItemType Directory -Force -Path $Archive | Out-Null
$keep = @('5_0_42_ahootsa_autonoma_estable')
Get-ChildItem "D:\RITXI" -Directory -Filter "5_0_*ahootsa*" | Where-Object { $keep -notcontains $_.Name } | ForEach-Object {
    $dest = Join-Path $Archive $_.Name
    Write-Host "Moviendo $($_.FullName) -> $dest"
    if (Test-Path $dest) { Remove-Item -LiteralPath $dest -Recurse -Force }
    Move-Item -LiteralPath $_.FullName -Destination $dest
}
Write-Host "Versiones antiguas archivadas en $Archive. Prueba 5.0.42 antes de borrar definitivamente."
