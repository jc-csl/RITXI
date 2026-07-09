param([string]$Confirmar = "NO")
if ($Confirmar -ne "SI") { Write-Host "No hago nada. Ejecuta con -Confirmar SI para archivar versiones antiguas."; exit 0 }
$dest = "D:\RITXI\_versiones_antiguas_ahootsa"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Get-ChildItem "D:\RITXI" -Directory -Filter "5_0_*ahootsa*" | Where-Object { $_.Name -ne "5_0_44_ahootsa_base_estable_instalable" } | ForEach-Object { Move-Item -LiteralPath $_.FullName -Destination $dest -Force }
