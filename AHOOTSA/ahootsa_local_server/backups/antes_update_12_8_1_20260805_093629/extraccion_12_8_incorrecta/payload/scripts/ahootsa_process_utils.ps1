Set-StrictMode -Version 2.0

function Test-AhootsaPort {
    param(
        [Parameter(Mandatory = $true)]
        [int]$Port,

        [string]$HostName = "127.0.0.1",

        [int]$TimeoutMilliseconds = 500
    )

    $Client = New-Object System.Net.Sockets.TcpClient

    try {
        $Async = $Client.BeginConnect(
            $HostName,
            $Port,
            $null,
            $null
        )

        $Connected = $Async.AsyncWaitHandle.WaitOne(
            $TimeoutMilliseconds,
            $false
        )

        if (-not $Connected) {
            return $false
        }

        $Client.EndConnect($Async)
        return $true
    } catch {
        return $false
    } finally {
        $Client.Close()
    }
}


function Wait-AhootsaPortOpen {
    param(
        [Parameter(Mandatory = $true)]
        [int]$Port,

        [int]$TimeoutSeconds = 45
    )

    $Deadline = (Get-Date).AddSeconds($TimeoutSeconds)

    while ((Get-Date) -lt $Deadline) {
        if (Test-AhootsaPort -Port $Port) {
            return $true
        }

        Start-Sleep -Milliseconds 500
    }

    return (Test-AhootsaPort -Port $Port)
}


function Wait-AhootsaPortClosed {
    param(
        [Parameter(Mandatory = $true)]
        [int]$Port,

        [int]$TimeoutSeconds = 15
    )

    $Deadline = (Get-Date).AddSeconds($TimeoutSeconds)

    while ((Get-Date) -lt $Deadline) {
        if (-not (Test-AhootsaPort -Port $Port)) {
            return $true
        }

        Start-Sleep -Milliseconds 350
    }

    return (-not (Test-AhootsaPort -Port $Port))
}


function Get-AhootsaPortProcessIds {
    param(
        [Parameter(Mandatory = $true)]
        [int]$Port
    )

    $Result = New-Object System.Collections.Generic.List[int]

    try {
        $Connections = Get-NetTCPConnection `
            -LocalPort $Port `
            -State Listen `
            -ErrorAction Stop

        foreach ($Connection in $Connections) {
            $ProcessId = [int]$Connection.OwningProcess

            if (
                $ProcessId -gt 4 -and
                -not $Result.Contains($ProcessId)
            ) {
                $Result.Add($ProcessId)
            }
        }
    } catch {
        $Lines = netstat -ano -p tcp 2>$null

        foreach ($Line in $Lines) {
            if ($Line -notmatch "LISTENING") {
                continue
            }

            $Parts = $Line.Trim() -split "\s+"

            if ($Parts.Count -lt 5) {
                continue
            }

            $LocalAddress = [string]$Parts[1]
            $PidText = [string]$Parts[-1]
            $PortPattern = ":" + [regex]::Escape([string]$Port) + "$"

            if ($LocalAddress -notmatch $PortPattern) {
                continue
            }

            $ParsedPid = 0

            if ([int]::TryParse($PidText, [ref]$ParsedPid)) {
                if (
                    $ParsedPid -gt 4 -and
                    -not $Result.Contains($ParsedPid)
                ) {
                    $Result.Add($ParsedPid)
                }
            }
        }
    }

    return @($Result)
}


function Get-AhootsaProcessDescription {
    param(
        [Parameter(Mandatory = $true)]
        [int]$ProcessId
    )

    try {
        $Process = Get-CimInstance `
            Win32_Process `
            -Filter "ProcessId=$ProcessId" `
            -ErrorAction Stop

        return [pscustomobject]@{
            ProcessId = [int]$Process.ProcessId
            Name = [string]$Process.Name
            CommandLine = [string]$Process.CommandLine
        }
    } catch {
        try {
            $Process = Get-Process `
                -Id $ProcessId `
                -ErrorAction Stop

            return [pscustomobject]@{
                ProcessId = [int]$Process.Id
                Name = [string]$Process.ProcessName
                CommandLine = ""
            }
        } catch {
            return [pscustomobject]@{
                ProcessId = $ProcessId
                Name = "desconocido"
                CommandLine = ""
            }
        }
    }
}


function Stop-AhootsaPortProcess {
    param(
        [Parameter(Mandatory = $true)]
        [int]$Port,

        [Parameter(Mandatory = $true)]
        [string]$ServiceName,

        [int]$WaitSeconds = 15
    )

    $ProcessIds = @(Get-AhootsaPortProcessIds -Port $Port)

    if ($ProcessIds.Count -eq 0) {
        Write-Host (
            "$ServiceName: puerto $Port libre."
        ) -ForegroundColor DarkGray

        return $false
    }

    foreach ($ProcessId in $ProcessIds) {
        if ($ProcessId -le 4 -or $ProcessId -eq $PID) {
            continue
        }

        $Description = Get-AhootsaProcessDescription `
            -ProcessId $ProcessId

        Write-Host (
            "$ServiceName: cerrando PID $ProcessId " +
            "($($Description.Name)) en el puerto $Port..."
        ) -ForegroundColor Yellow

        try {
            Stop-Process `
                -Id $ProcessId `
                -Force `
                -ErrorAction Stop
        } catch {
            Write-Host (
                "$ServiceName: no se pudo cerrar el PID $ProcessId."
            ) -ForegroundColor Yellow
        }
    }

    if (
        -not (
            Wait-AhootsaPortClosed `
                -Port $Port `
                -TimeoutSeconds $WaitSeconds
        )
    ) {
        throw "$ServiceName sigue ocupando el puerto $Port."
    }

    Write-Host (
        "$ServiceName: puerto $Port liberado."
    ) -ForegroundColor Green

    return $true
}


function Stop-AhootsaCommandProcesses {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Patterns,

        [string]$ServiceName = "Proceso Ahootsa"
    )

    try {
        $Processes = Get-CimInstance `
            Win32_Process `
            -ErrorAction Stop
    } catch {
        return
    }

    foreach ($Process in $Processes) {
        $ProcessId = [int]$Process.ProcessId

        if ($ProcessId -le 4 -or $ProcessId -eq $PID) {
            continue
        }

        $CommandLine = [string]$Process.CommandLine

        if ([string]::IsNullOrWhiteSpace($CommandLine)) {
            continue
        }

        $MatchesAll = $true

        foreach ($Pattern in $Patterns) {
            if ($CommandLine -notmatch $Pattern) {
                $MatchesAll = $false
                break
            }
        }

        if (-not $MatchesAll) {
            continue
        }

        Write-Host (
            "$ServiceName: cerrando proceso residual PID $ProcessId..."
        ) -ForegroundColor Yellow

        try {
            Stop-Process `
                -Id $ProcessId `
                -Force `
                -ErrorAction Stop
        } catch {
            Write-Host (
                "$ServiceName: no se pudo cerrar el PID $ProcessId."
            ) -ForegroundColor Yellow
        }
    }
}


function Stop-AhootsaConversationAppGracefully {
    param(
        [int]$ConversationPort = 7860,

        [int]$DaemonPort = 8000
    )

    if (-not (Test-AhootsaPort -Port $ConversationPort)) {
        return $true
    }

    if (-not (Test-AhootsaPort -Port $DaemonPort)) {
        return $false
    }

    try {
        Invoke-RestMethod `
            -Uri "http://127.0.0.1:$DaemonPort/api/apps/stop-current-app" `
            -Method Post `
            -ContentType "application/json" `
            -Body "{}" `
            -TimeoutSec 10 |
            Out-Null
    } catch {
        return $false
    }

    return (
        Wait-AhootsaPortClosed `
            -Port $ConversationPort `
            -TimeoutSeconds 20
    )
}


function Wait-AhootsaFileStable {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [int]$TimeoutSeconds = 15
    )

    $Deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $PreviousLength = -1
    $StableChecks = 0

    while ((Get-Date) -lt $Deadline) {
        if (Test-Path $Path) {
            $CurrentLength = (Get-Item $Path).Length

            if ($CurrentLength -eq $PreviousLength) {
                $StableChecks += 1
            } else {
                $PreviousLength = $CurrentLength
                $StableChecks = 0
            }

            if ($StableChecks -ge 3) {
                return $true
            }
        }

        Start-Sleep -Milliseconds 750
    }

    return (Test-Path $Path)
}


function Set-AhootsaDotEnvProfile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$DotEnvPath,

        [Parameter(Mandatory = $true)]
        [string]$ProfileName
    )

    $Lines = @()

    if (Test-Path $DotEnvPath) {
        $Lines = @(Get-Content $DotEnvPath -Encoding UTF8)
    }

    $Name = "REACHY_MINI_CUSTOM_PROFILE"
    $Pattern = "^\s*#?\s*" + [regex]::Escape($Name) + "\s*="
    $Replacement = "$Name=$ProfileName"
    $Found = $false
    $Result = New-Object System.Collections.Generic.List[string]

    foreach ($Line in $Lines) {
        if ($Line -match $Pattern) {
            if (-not $Found) {
                $Result.Add($Replacement)
                $Found = $true
            }
        } else {
            $Result.Add($Line)
        }
    }

    if (-not $Found) {
        $Result.Add($Replacement)
    }

    [System.IO.File]::WriteAllLines(
        $DotEnvPath,
        $Result.ToArray(),
        (New-Object System.Text.UTF8Encoding($false))
    )
}
