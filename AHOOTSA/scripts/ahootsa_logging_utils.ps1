Set-StrictMode -Version 2.0

function Write-AhootsaUtf8NoBom {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [string]$Text
    )

    $Parent = Split-Path $Path -Parent

    if (
        -not [string]::IsNullOrWhiteSpace($Parent) -and
        -not (Test-Path $Parent)
    ) {
        New-Item `
            -ItemType Directory `
            -Path $Parent `
            -Force |
            Out-Null
    }

    [System.IO.File]::WriteAllText(
        $Path,
        $Text,
        (New-Object System.Text.UTF8Encoding($false))
    )
}

function New-AhootsaAnonymousLogContext {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ProjectRoot
    )

    $Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $RunId = "anonymous_$Timestamp"
    $LogsRoot = Join-Path $ProjectRoot "logs"
    $Directory = Join-Path `
        $LogsRoot `
        ("anonymous\" + $RunId)
    $LogFile = Join-Path `
        $Directory `
        "conversation_app.log"

    New-Item `
        -ItemType Directory `
        -Path $Directory `
        -Force |
        Out-Null

    Write-AhootsaUtf8NoBom `
        -Path (Join-Path $LogsRoot "ULTIMO_ANONIMO.txt") `
        -Text $Directory

    return [PSCustomObject]@{
        RunId = $RunId
        Directory = $Directory
        LogFile = $LogFile
    }
}

function Initialize-AhootsaSessionLogContext {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ProjectRoot,

        [Parameter(Mandatory = $true)]
        [int]$SessionId,

        [Parameter(Mandatory = $true)]
        [string]$SessionDirectory,

        [Parameter(Mandatory = $true)]
        [string]$SessionLogFile
    )

    $LogsRoot = Join-Path $ProjectRoot "logs"
    $Directory = Join-Path `
        $LogsRoot `
        ("sessions\session_{0:D6}" -f $SessionId)
    $CentralLogFile = Join-Path `
        $Directory `
        "conversation_app.log"
    $HardLinkCreated = $false

    New-Item `
        -ItemType Directory `
        -Path $Directory `
        -Force |
        Out-Null

    New-Item `
        -ItemType Directory `
        -Path $SessionDirectory `
        -Force |
        Out-Null

    if (-not (Test-Path $SessionLogFile)) {
        New-Item `
            -ItemType File `
            -Path $SessionLogFile `
            -Force |
            Out-Null
    }

    if (-not (Test-Path $CentralLogFile)) {
        try {
            New-Item `
                -ItemType HardLink `
                -Path $CentralLogFile `
                -Target $SessionLogFile `
                -ErrorAction Stop |
                Out-Null

            $HardLinkCreated = $true
        } catch {
            Copy-Item `
                $SessionLogFile `
                $CentralLogFile `
                -Force
        }
    }

    Write-AhootsaUtf8NoBom `
        -Path (Join-Path $LogsRoot "ULTIMA_SESION.txt") `
        -Text $Directory

    return [PSCustomObject]@{
        Directory = $Directory
        CentralLogFile = $CentralLogFile
        SourceLogFile = $SessionLogFile
        HardLinkCreated = $HardLinkCreated
    }
}

function Sync-AhootsaCentralLog {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceLogFile,

        [Parameter(Mandatory = $true)]
        [string]$CentralLogFile
    )

    if (-not (Test-Path $SourceLogFile)) {
        return
    }

    $CentralDirectory = Split-Path $CentralLogFile -Parent

    New-Item `
        -ItemType Directory `
        -Path $CentralDirectory `
        -Force |
        Out-Null

    if (-not (Test-Path $CentralLogFile)) {
        Copy-Item `
            $SourceLogFile `
            $CentralLogFile `
            -Force

        return
    }

    $SourceLength = (Get-Item $SourceLogFile).Length
    $CentralLength = (Get-Item $CentralLogFile).Length

    if ($SourceLength -ne $CentralLength) {
        try {
            Copy-Item `
                $SourceLogFile `
                $CentralLogFile `
                -Force
        } catch {
            # If both names are hard links to the same file,
            # no copy is required.
        }
    }
}

function Invoke-AhootsaLogDiagnostics {
    param(
        [Parameter(Mandatory = $true)]
        [string]$PythonExe,

        [Parameter(Mandatory = $true)]
        [string]$DiagnosticTool,

        [Parameter(Mandatory = $true)]
        [string]$LogFile,

        [Parameter(Mandatory = $true)]
        [string]$OutputDirectory,

        [Parameter(Mandatory = $true)]
        [ValidateSet("anonymous", "identified_session")]
        [string]$Mode,

        [Parameter(Mandatory = $true)]
        [string]$State,

        [int]$SessionId = 0,

        [string]$RunId = "",

        [string]$Profile = "",

        [string]$Voice = "",

        [string]$SourceSessionDirectory = ""
    )

    if (
        -not (Test-Path $PythonExe) -or
        -not (Test-Path $DiagnosticTool) -or
        -not (Test-Path $LogFile)
    ) {
        return $false
    }

    $Arguments = @(
        $DiagnosticTool,
        "--log",
        $LogFile,
        "--output-dir",
        $OutputDirectory,
        "--mode",
        $Mode,
        "--state",
        $State
    )

    if ($SessionId -gt 0) {
        $Arguments += @(
            "--session-id",
            [string]$SessionId
        )
    }

    if (-not [string]::IsNullOrWhiteSpace($RunId)) {
        $Arguments += @(
            "--run-id",
            $RunId
        )
    }

    if (-not [string]::IsNullOrWhiteSpace($Profile)) {
        $Arguments += @(
            "--profile",
            $Profile
        )
    }

    if (-not [string]::IsNullOrWhiteSpace($Voice)) {
        $Arguments += @(
            "--voice",
            $Voice
        )
    }

    if (
        -not [string]::IsNullOrWhiteSpace(
            $SourceSessionDirectory
        )
    ) {
        $Arguments += @(
            "--source-session-dir",
            $SourceSessionDirectory
        )
    }

    try {
        & $PythonExe @Arguments

        return ($LASTEXITCODE -eq 0)
    } catch {
        Write-Host (
            "No se pudo generar el diagnóstico de logs: " +
            $_.Exception.Message
        ) -ForegroundColor Yellow

        return $false
    }
}
