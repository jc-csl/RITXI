$ErrorActionPreference = "Stop"
$baseUrl = "http://127.0.0.1:8100"
$projectRoot = "D:\RITXI\AHOOTSA8"
$serverRoot = Join-Path $projectRoot "ahootsa_local_server"
$appRoot = Join-Path $projectRoot "reachy_mini_conversation_app"

Write-Host "1. Checking version..." -ForegroundColor Cyan
$health = Invoke-RestMethod "$baseUrl/health"
if ($health.version -ne "0.12.2") {
    throw "Expected version 0.12.2, found $($health.version)."
}
Write-Host "   Version 0.12.2 is correct." -ForegroundColor Green

Write-Host "2. Checking simplified configuration..." -ForegroundColor Cyan
$config = Invoke-RestMethod "$baseUrl/panel/api/config/check"
if (-not $config.ok) {
    $failed = @(
        $config.checks.PSObject.Properties |
        Where-Object { -not $_.Value } |
        ForEach-Object { $_.Name }
    )
    throw "Failed checks: $($failed -join ', ')"
}
if ($config.active_profile_name -ne "ahootsa_session") {
    throw "The fixed active profile is not ahootsa_session."
}
Write-Host "   Simplified configuration is correct." -ForegroundColor Green

Write-Host "3. Checking profile directories..." -ForegroundColor Cyan
$defaultProfile = Join-Path $appRoot "external_content\profile_defaults\ahootsa_default"
$activeProfile = Join-Path $appRoot "external_content\external_profiles\ahootsa_session"
foreach ($profile in @($defaultProfile, $activeProfile)) {
    foreach ($name in @("instructions.txt", "greeting.txt", "tools.txt", "voice.txt")) {
        if (-not (Test-Path (Join-Path $profile $name))) {
            throw "Missing $name in $profile"
        }
    }
}
Write-Host "   Default and active profiles are complete." -ForegroundColor Green

Write-Host "4. Checking .env and stable launcher..." -ForegroundColor Cyan
$envPath = Join-Path $appRoot ".env"
$envText = Get-Content $envPath -Raw
if ($envText -notmatch '(?m)^\s*REACHY_MINI_CUSTOM_PROFILE\s*=\s*ahootsa_session\s*$') {
    throw ".env does not select ahootsa_session."
}
$launcher = Join-Path $projectRoot "2_lanzar_app_ahootsa.ps1"
if (-not (Test-Path $launcher)) {
    throw "Stable launcher not found."
}
Write-Host "   .env and launcher are correct." -ForegroundColor Green

Write-Host "5. Checking simplified storage..." -ForegroundColor Cyan
if (-not (Test-Path (Join-Path $serverRoot "data\sessions"))) {
    throw "data\sessions was not created."
}
$panelConfig = Get-Content (Join-Path $serverRoot "config\panel_config.json") -Raw
if ($panelConfig -match '"runtime_directory"') {
    throw "runtime_directory is still configured."
}
Write-Host "   Storage is under ahootsa_local_server\data\sessions." -ForegroundColor Green

Write-Host ""
Write-Host "UPDATE 12.2 STRUCTURE VALIDATED." -ForegroundColor Green
