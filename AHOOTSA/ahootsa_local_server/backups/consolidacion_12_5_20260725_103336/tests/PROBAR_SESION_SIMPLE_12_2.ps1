$ErrorActionPreference = "Stop"
$baseUrl = "http://127.0.0.1:8100"

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

Write-Host "1. Checking that no Conversation App is running..." -ForegroundColor Cyan
$bootstrap = Invoke-AhootsaRest "$baseUrl/panel/api/bootstrap"
if ($bootstrap.services.conversation_app.running) {
    throw "Close the Conversation App before this test."
}
if ($null -ne $bootstrap.active_session) {
    throw "Finish active session $($bootstrap.active_session.session_id) before this test."
}

Write-Host "2. Selecting or creating a test user..." -ForegroundColor Cyan
$users = @($bootstrap.users)
if (($users | Measure-Object).Count -eq 0) {
    $user = Invoke-AhootsaRest `
        -Uri "$baseUrl/panel/api/example-user" `
        -Method POST `
        -Body @{}
    $externalId = $user.external_id
} else {
    $externalId = $users[0].external_id
}
Write-Host "   User: $externalId" -ForegroundColor Green

Write-Host "3. Preparing a session..." -ForegroundColor Cyan
$prepared = Invoke-AhootsaRest `
    -Uri "$baseUrl/panel/api/session/prepare" `
    -Method POST `
    -Body @{
        user_external_id = $externalId
        activity = "express_preferences"
        level = "initial"
        started_by = "Update 12.2 test"
    }

if ($prepared.profile_name -ne "ahootsa_session") {
    throw "Unexpected profile name: $($prepared.profile_name)"
}
if ($prepared.profile_directory -notmatch 'external_profiles\\ahootsa_session$') {
    throw "The active profile is not in external_profiles\ahootsa_session."
}
if ($prepared.session_directory -notmatch 'ahootsa_local_server\\data\\sessions\\session_\d+$') {
    throw "The session is not stored under data\sessions."
}
foreach ($path in @(
    $prepared.context_file,
    $prepared.profile_snapshot,
    $prepared.profile_directory
)) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Missing generated path: $path"
    }
}
Write-Host "   Fixed profile, context and snapshot were created." -ForegroundColor Green

Write-Host "4. Checking personalized content..." -ForegroundColor Cyan
$context = Get-Content $prepared.context_file -Raw -Encoding UTF8 | ConvertFrom-Json
$instructions = Get-Content `
    (Join-Path $prepared.profile_directory "instructions.txt") `
    -Raw `
    -Encoding UTF8
$greeting = Get-Content `
    (Join-Path $prepared.profile_directory "greeting.txt") `
    -Raw `
    -Encoding UTF8

if ($instructions -notmatch "sesión $($prepared.session_id)") {
    throw "The active instructions do not contain the session marker."
}
if ($greeting -notmatch [regex]::Escape($context.user.preferred_name)) {
    throw "The greeting does not contain the preferred name."
}
Write-Host "   Personalized instructions and greeting are correct." -ForegroundColor Green

Write-Host "5. Registering professional marks..." -ForegroundColor Cyan
foreach ($action in @("adequate", "partial", "hint", "repeat")) {
    Invoke-AhootsaRest `
        -Uri "$baseUrl/panel/api/session/event" `
        -Method POST `
        -Body @{ action = $action; note = "Update 12.2 test" } |
        Out-Null
}

Write-Host "6. Finishing and resetting the active profile..." -ForegroundColor Cyan
$finished = Invoke-AhootsaRest `
    -Uri "$baseUrl/panel/api/session/finish" `
    -Method POST `
    -Body @{
        note = "Update 12.2 technical validation."
        decision = "no_decision"
    }

if ($finished.status -ne "finished") {
    throw "The session was not finished."
}
$statusPath = Join-Path $prepared.session_directory "session_status.json"
$summaryPath = Join-Path $prepared.session_directory "summary.json"
if (-not (Test-Path $statusPath) -or -not (Test-Path $summaryPath)) {
    throw "Status or summary file is missing."
}
$status = Get-Content $statusPath -Raw -Encoding UTF8 | ConvertFrom-Json
if (-not $status.active_profile_reset) {
    throw "The active profile was not reset."
}
$resetInstructions = Get-Content `
    (Join-Path $prepared.profile_directory "instructions.txt") `
    -Raw `
    -Encoding UTF8
if ($resetInstructions -match "# CONTEXTO TEMPORAL DE SESIÓN") {
    throw "Temporary context remains in the active profile after finish."
}

Write-Host ""
Write-Host "UPDATE 12.2 SESSION VALIDATED." -ForegroundColor Green
Write-Host "Session duration source: $($finished.duration_source)" -ForegroundColor Gray
