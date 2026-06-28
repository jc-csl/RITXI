Write-Host "============================================" -ForegroundColor Cyan
Write-Host " Ahootsa v0.4.9 - limpiar variables antiguas" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

$names = @("AHOOTSA_EMOTIONS_LIBRARY_DIR", "REACHY_MINI_EMOTIONS_LIBRARY_DIR")
foreach ($name in $names) {
  try {
    [Environment]::SetEnvironmentVariable($name, $null, "User")
    [Environment]::SetEnvironmentVariable($name, $null, "Process")
    Write-Host "Variable limpiada: $name" -ForegroundColor Green
  } catch {
    Write-Host "No se pudo limpiar ${name}: $_" -ForegroundColor Yellow
  }
}

Write-Host "No se borra D:\RITXI\reachy-mini-emotions-library; solo se evita forzarla en esta version." -ForegroundColor Yellow
Write-Host "Cierra y abre Reachy Mini Desktop para recargar el entorno." -ForegroundColor Yellow
