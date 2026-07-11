param([string]$Confirmar = "NO")
$ErrorActionPreference = "Stop"
if ($Confirmar -ne "SI") { throw "Ejecuta con -Confirmar SI para archivar versiones antiguas." }
$dest = "D:\RITXI\_versiones_antiguas_ahootsa"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Get-ChildItem "D:\RITXI" -Directory -Filter "5_0_*" -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "Archivando $($_.FullName)"
    Move-Item -LiteralPath $_.FullName -Destination $dest -Force
}
Write-Host "Versiones antiguas movidas a $dest"
