$ErrorActionPreference = "Stop"

$projectRoot = "D:\RITXI\AHOOTSA8"
$files = @(
    (Join-Path $projectRoot "scripts\ahootsa_process_utils.ps1"),
    (Join-Path $projectRoot "0_detener_servicios_ahootsa.ps1"),
    (Join-Path $projectRoot "COMPROBAR_SERVICIOS_AHOOTSA.ps1"),
    (Join-Path $projectRoot "1_lanzar_daemon_mujoco.ps1"),
    (Join-Path $projectRoot "2_lanzar_app_ahootsa.ps1"),
    (Join-Path $projectRoot "ahootsa_local_server\3_lanzar_ahootsa_server.ps1")
)

Write-Host "Checking PowerShell syntax..." -ForegroundColor Cyan

foreach ($file in $files) {
    if (-not (Test-Path $file)) {
        throw "Missing file: $file"
    }

    $tokens = $null
    $errors = $null

    [System.Management.Automation.Language.Parser]::ParseFile(
        $file,
        [ref]$tokens,
        [ref]$errors
    ) | Out-Null

    if ($errors.Count -gt 0) {
        $messages = @($errors | ForEach-Object {
            "Line $($_.Extent.StartLineNumber): $($_.Message)"
        })
        throw "Syntax error in $file`r`n$($messages -join "`r`n")"
    }

    Write-Host "  OK: $file" -ForegroundColor Green
}

Write-Host ""
Write-Host "UPDATE 12.3.1 POWERSHELL SYNTAX VALIDATED." -ForegroundColor Green
