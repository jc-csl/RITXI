$ErrorActionPreference = "Stop"

$Root = "D:\RITXI\AHOOTSA_LOCAL"
$ProfileFile = Join-Path $Root "reachy_mini_conversation_app\profiles\ahootsa_realtime_es\profile.md"

Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host " AHOOTSA - CORREGIR VOZ KOKORO" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $ProfileFile)) {
    throw "No existe el perfil: $ProfileFile"
}

$content = [System.IO.File]::ReadAllText($ProfileFile)

# Sustituye una voz existente o inserta ef_dora tras schema_version.
if ($content -match '(?m)^voice\s*=\s*".*"\s*$') {
    $content = [regex]::Replace(
        $content,
        '(?m)^voice\s*=\s*".*"\s*$',
        'voice = "ef_dora"'
    )
} elseif ($content -match '(?m)^schema_version\s*=\s*1\s*$') {
    $content = [regex]::Replace(
        $content,
        '(?m)^(schema_version\s*=\s*1\s*)$',
        '$1' + "`r`n" + 'voice = "ef_dora"',
        1
    )
} else {
    throw "El profile.md no contiene schema_version = 1."
}

$Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($ProfileFile, $content, $Utf8NoBom)

Write-Host "OK - voz del perfil cambiada a ef_dora." -ForegroundColor Green
Write-Host ""
Write-Host "Perfil:" -ForegroundColor Yellow
Write-Host $ProfileFile
Write-Host ""

Select-String -Path $ProfileFile -Pattern 'schema_version|voice|greeting' |
    ForEach-Object { Write-Host $_.Line }

Write-Host ""
Write-Host "IMPORTANTE:" -ForegroundColor Cyan
Write-Host "Cierra y vuelve a arrancar la Conversation App para que recargue profile.md."
Write-Host ""
