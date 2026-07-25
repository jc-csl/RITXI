$ErrorActionPreference = "Stop"
$baseUrl = "http://127.0.0.1:8100"
$timeoutSeconds = 90

try {
    $serverHealth = Invoke-RestMethod "http://127.0.0.1:8100/health" -TimeoutSec 3
} catch {
    throw "Ahootsa Local Server is not running on port 8100. Run .\3_lanzar_ahootsa_server.ps1 first."
}

if ($serverHealth.version -ne "0.12.3") {
    throw "Expected Ahootsa Local Server 0.12.3, found $($serverHealth.version)."
}

function Invoke-AhootsaRest {
    param(
        [Parameter(Mandatory = $true)][string]$Uri,
        [ValidateSet("GET", "POST")][string]$Method = "GET",
        [object]$Body = $null
    )
    if ($Method -eq "POST") {
        $json = if ($null -eq $Body) { "{}" } else { $Body | ConvertTo-Json -Depth 20 }
        return Invoke-RestMethod `
            -Uri $Uri `
            -Method Post `
            -ContentType "application/json; charset=utf-8" `
            -Body ([System.Text.Encoding]::UTF8.GetBytes($json))
    }
    return Invoke-RestMethod -Uri $Uri -Method Get
}

Write-Host "1. Checking prerequisites..." -ForegroundColor Cyan
$bootstrap = Invoke-AhootsaRest "$baseUrl/panel/api/bootstrap"
if ($null -eq $bootstrap.active_session) {
    throw "Prepare a session from the panel before running this test."
}
if (-not $bootstrap.active_session.profile_prepared) {
    throw "The active fixed profile is not prepared for this session."
}
if (-not $bootstrap.services.daemon.running) {
    throw "Start the daemon or MuJoCo before running this test."
}
if ($bootstrap.services.conversation_app.running) {
    throw "Close the Conversation App before running this test."
}

Write-Host "2. Launching the official Conversation App..." -ForegroundColor Cyan
$result = Invoke-AhootsaRest `
    -Uri "$baseUrl/panel/api/launch/conversation-app" `
    -Method POST `
    -Body @{}
Write-Host "   $($result.message)" -ForegroundColor Gray

Write-Host "3. Waiting for port 7860..." -ForegroundColor Cyan
$deadline = (Get-Date).AddSeconds($timeoutSeconds)
$running = $false
while ((Get-Date) -lt $deadline) {
    Start-Sleep -Seconds 2
    try {
        $profile = Invoke-AhootsaRest "$baseUrl/panel/api/conversation-profile"
        if ($profile.available) {
            $running = $true
            break
        }
    } catch {}
}
if (-not $running) {
    throw "The Conversation App did not become available in $timeoutSeconds seconds."
}

Write-Host "4. Verifying the profile actually loaded..." -ForegroundColor Cyan
if ($profile.current -ne "ahootsa_session") {
    throw "Wrong profile loaded: $($profile.current). Expected ahootsa_session."
}
if (-not $profile.matches) {
    throw "The official app does not report the expected profile."
}

$active = Invoke-AhootsaRest "$baseUrl/panel/api/bootstrap"
$sessionId = $active.active_session.session_id
$sessionRoot = "D:\RITXI\AHOOTSA8\ahootsa_local_server\data\sessions\session_{0:D6}" -f [int]$sessionId
$context = Get-Content (Join-Path $sessionRoot "session_context.json") -Raw -Encoding UTF8 | ConvertFrom-Json
$loaded = Invoke-RestMethod `
    -Uri ("http://127.0.0.1:7860/personalities/load?name=ahootsa_session") `
    -Method Get

if ($loaded.greeting -notmatch [regex]::Escape($context.user.preferred_name)) {
    throw "The official app did not load the personalized greeting."
}

Write-Host ""
Write-Host "UPDATE 12.3 OFFICIAL STARTUP VALIDATED." -ForegroundColor Green
Write-Host "Current profile: $($profile.current)" -ForegroundColor Green
Write-Host "Personalized user: $($context.user.preferred_name)" -ForegroundColor Green
Write-Host "The Conversation App remains open for the manual conversation test." -ForegroundColor Yellow
