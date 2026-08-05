$ErrorActionPreference = "SilentlyContinue"

$servicios = @(
    @{ Nombre = "Panel profesional Ahootsa"; Url = "http://127.0.0.1:8100/panel"; Puerto = 8100 },
    @{ Nombre = "API Ahootsa Local Server"; Url = "http://127.0.0.1:8100/docs"; Puerto = 8100 },
    @{ Nombre = "Reachy Mini Conversation App"; Url = "http://127.0.0.1:7860"; Puerto = 7860 },
    @{ Nombre = "API Conversation App"; Url = "http://127.0.0.1:7860/docs"; Puerto = 7860 },
    @{ Nombre = "API daemon Reachy"; Url = "http://127.0.0.1:8000/docs"; Puerto = 8000 }
)

foreach ($servicio in $servicios) {
    $disponible = Test-NetConnection `
        -ComputerName 127.0.0.1 `
        -Port $servicio.Puerto `
        -InformationLevel Quiet `
        -WarningAction SilentlyContinue

    if ($disponible) {
        Write-Host "Abriendo: $($servicio.Nombre)" -ForegroundColor Green
        Start-Process $servicio.Url
    } else {
        Write-Host "No disponible: $($servicio.Nombre) (puerto $($servicio.Puerto))" -ForegroundColor Yellow
    }
}
