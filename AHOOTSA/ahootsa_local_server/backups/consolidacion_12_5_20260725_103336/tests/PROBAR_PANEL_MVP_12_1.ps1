$ErrorActionPreference = "Stop"

try {
    [Console]::InputEncoding = New-Object System.Text.UTF8Encoding($false)
    [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
} catch {
    # Console encoding must not stop the functional test.
}

$baseUrl = "http://127.0.0.1:8100"

function Invoke-AhootsaRest {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Uri,

        [ValidateSet("GET", "POST")]
        [string]$Method = "GET",

        [object]$Body = $null
    )

    if ($Method -eq "POST") {
        $json = if ($null -eq $Body) {
            "{}"
        } else {
            $Body | ConvertTo-Json -Depth 20
        }

        $parameters = @{
            Uri = $Uri
            Method = "Post"
            ContentType = "application/json; charset=utf-8"
            Body = [System.Text.Encoding]::UTF8.GetBytes($json)
        }

        return Invoke-RestMethod @parameters
    }

    return Invoke-RestMethod -Uri $Uri -Method Get
}

Write-Host "1. Checking server version..." -ForegroundColor Cyan
$health = Invoke-AhootsaRest -Uri "$baseUrl/health"

if ($health.version -ne "0.12.0") {
    throw "Wrong server version: $($health.version). Expected 0.12.0."
}

Write-Host "   Server version 0.12.0 is correct." -ForegroundColor Green

Write-Host "2. Checking panel HTML..." -ForegroundColor Cyan
$panel = Invoke-WebRequest -Uri "$baseUrl/panel" -UseBasicParsing

if ($panel.StatusCode -ne 200) {
    throw "The panel returned HTTP status $($panel.StatusCode)."
}

if ($panel.Content -notmatch "Panel profesional") {
    throw "The expected panel content was not found."
}

Write-Host "   Panel is available." -ForegroundColor Green

Write-Host "3. Checking configuration and folders..." -ForegroundColor Cyan
$config = Invoke-AhootsaRest -Uri "$baseUrl/panel/api/config/check"

if (-not $config.ok) {
    $failedChecks = @(
        $config.checks.PSObject.Properties |
        Where-Object { -not $_.Value } |
        ForEach-Object { $_.Name }
    )

    throw "Incomplete configuration: $($failedChecks -join ', ')"
}

Write-Host "   Paths, scripts, base profile and runtime are correct." -ForegroundColor Green

Write-Host "4. Checking activities and users..." -ForegroundColor Cyan
$bootstrap = Invoke-AhootsaRest -Uri "$baseUrl/panel/api/bootstrap"
$activities = @($bootstrap.activities)

if (($activities | Measure-Object).Count -lt 1) {
    throw "No activities are configured."
}

$preferencesActivity = $activities | Where-Object {
    $_.key -eq "express_preferences"
}

if ($null -eq $preferencesActivity) {
    throw "Activity express_preferences was not found."
}

$users = @($bootstrap.users)

if (($users | Measure-Object).Count -eq 0) {
    Write-Host "   No users found. Creating an example user..." -ForegroundColor Yellow

    $exampleUser = Invoke-AhootsaRest `
        -Uri "$baseUrl/panel/api/example-user" `
        -Method POST `
        -Body @{}

    $userExternalId = $exampleUser.external_id
} else {
    $userExternalId = $users[0].external_id
}

Write-Host "   Test user: $userExternalId" -ForegroundColor Green

$bootstrap = Invoke-AhootsaRest -Uri "$baseUrl/panel/api/bootstrap"

if ($null -ne $bootstrap.active_session) {
    Write-Host "5. An active session already exists: $($bootstrap.active_session.session_id)." -ForegroundColor Yellow
    Write-Host "   The test will preserve that session." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "UPDATE 12.1 VALIDATED: PANEL AVAILABLE; ACTIVE SESSION PRESERVED." -ForegroundColor Green
    exit 0
}

Write-Host "5. Preparing a test session without launching Reachy..." -ForegroundColor Cyan

$prepareBody = @{
    user_external_id = $userExternalId
    activity = "express_preferences"
    level = "initial"
    started_by = "Update 12.1 test"
}

$prepared = Invoke-AhootsaRest `
    -Uri "$baseUrl/panel/api/session/prepare" `
    -Method POST `
    -Body $prepareBody

if (-not (Test-Path -LiteralPath $prepared.context_file)) {
    throw "session_context.json was not created."
}

if (-not (Test-Path -LiteralPath $prepared.launcher_script)) {
    throw "The session launcher script was not created."
}

if (-not (Test-Path -LiteralPath $prepared.profile_directory)) {
    throw "The temporary profile directory was not created."
}

Write-Host "   Context, temporary profile and launcher were created." -ForegroundColor Green

Write-Host "6. Registering professional test marks..." -ForegroundColor Cyan

foreach ($action in @("adequate", "partial", "hint", "repeat")) {
    $eventBody = @{
        action = $action
        note = "Automatic Update 12.1 test"
    }

    Invoke-AhootsaRest `
        -Uri "$baseUrl/panel/api/session/event" `
        -Method POST `
        -Body $eventBody |
        Out-Null
}

$summary = Invoke-AhootsaRest -Uri "$baseUrl/panel/api/session/summary"

if ([int]$summary.counts.adequate -ne 1) {
    throw "The adequate response counter is incorrect."
}

if ([int]$summary.counts.partial -ne 1) {
    throw "The partial response counter is incorrect."
}

if ([int]$summary.counts.hint -ne 1) {
    throw "The hint counter is incorrect."
}

if ([int]$summary.counts.repeat -ne 1) {
    throw "The repeat counter is incorrect."
}

Write-Host "   Quick professional tracking is correct." -ForegroundColor Green

Write-Host "7. Finishing the test session..." -ForegroundColor Cyan

$finishBody = @{
    note = "Technical validation session for Update 12.1."
    decision = "no_decision"
}

$finished = Invoke-AhootsaRest `
    -Uri "$baseUrl/panel/api/session/finish" `
    -Method POST `
    -Body $finishBody

if ($finished.status -ne "finished") {
    throw "The test session was not finished correctly."
}

Write-Host "   Session was finished and stored." -ForegroundColor Green
Write-Host ""
Write-Host "UPDATE 12.1 VALIDATED: PANEL MVP, TEMPORARY PROFILE AND TRACKING WORK." -ForegroundColor Green
Write-Host "The daemon and Conversation App were not launched by this test." -ForegroundColor Gray
