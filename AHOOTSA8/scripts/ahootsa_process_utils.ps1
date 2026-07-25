Set-StrictMode -Version 2.0

function Get-AhootsaPortProcessIds {
    param(
        [Parameter(Mandatory = $true)]
        [int]$Port
    )

    $result = New-Object System.Collections.Generic.List[int]

    try {
        $connections = Get-NetTCPConnection `
            -LocalPort $Port `
            -State Listen `
            -ErrorAction Stop

        foreach ($connection in $connections) {
            $pidValue = [int]$connection.OwningProcess
            if ($pidValue -gt 4 -and -not $result.Contains($pidValue)) {
                $result.Add($pidValue)
            }
        }
    } catch {
        $lines = netstat -ano -p tcp 2>$null
        foreach ($line in $lines) {
            if ($line -notmatch 'LISTENING') {
                continue
            }

            $parts = ($line.Trim() -split '\s+')
            if ($parts.Count -lt 5) {
                continue
            }

            $localAddress = [string]$parts[1]
            $pidText = [string]$parts[-1]

            if ($localAddress -match (':' + [regex]::Escape([string]$Port) + '$')) {
                $parsedPid = 0
                if ([int]::TryParse($pidText, [ref]$parsedPid)) {
                    if ($parsedPid -gt 4 -and -not $result.Contains($parsedPid)) {
                        $result.Add($parsedPid)
                    }
                }
            }
        }
    }

    return @($result)
}

function Test-AhootsaPort {
    param(
        [Parameter(Mandatory = $true)]
        [int]$Port,
        [string]$HostName = "127.0.0.1",
        [int]$TimeoutMilliseconds = 500
    )

    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $async = $client.BeginConnect($HostName, $Port, $null, $null)
        $connected = $async.AsyncWaitHandle.WaitOne($TimeoutMilliseconds, $false)

        if (-not $connected) {
            return $false
        }

        $client.EndConnect($async)
        return $true
    } catch {
        return $false
    } finally {
        $client.Close()
    }
}

function Wait-AhootsaPortClosed {
    param(
        [Parameter(Mandatory = $true)]
        [int]$Port,
        [int]$TimeoutSeconds = 10
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (-not (Test-AhootsaPort -Port $Port)) {
            return $true
        }
        Start-Sleep -Milliseconds 300
    }

    return (-not (Test-AhootsaPort -Port $Port))
}

function Wait-AhootsaPortOpen {
    param(
        [Parameter(Mandatory = $true)]
        [int]$Port,
        [int]$TimeoutSeconds = 30
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-AhootsaPort -Port $Port) {
            return $true
        }
        Start-Sleep -Milliseconds 500
    }

    return (Test-AhootsaPort -Port $Port)
}

function Stop-AhootsaPortProcess {
    param(
        [Parameter(Mandatory = $true)]
        [int]$Port,

        [Parameter(Mandatory = $true)]
        [string]$ServiceName,

        [int]$WaitSeconds = 10
    )

    $processIds = @(Get-AhootsaPortProcessIds -Port $Port)

    if ($processIds.Count -eq 0) {
        Write-Host ("{0}: port {1} is free." -f $ServiceName, $Port) -ForegroundColor DarkGray
        return $false
    }

    foreach ($processId in $processIds) {
        if ($processId -eq $PID -or $processId -le 4) {
            continue
        }

        try {
            $process = Get-Process -Id $processId -ErrorAction Stop
            Write-Host (
                ("{0}: stopping previous process PID " -f $ServiceName) +
                "$processId ($($process.ProcessName)) on port $Port..."
            ) -ForegroundColor Yellow

            Stop-Process -Id $processId -Force -ErrorAction Stop
        } catch {
            Write-Host (
                ("{0}: could not stop PID {1}: " -f $ServiceName, $processId) +
                $_.Exception.Message
            ) -ForegroundColor Yellow
        }
    }

    if (-not (Wait-AhootsaPortClosed -Port $Port -TimeoutSeconds $WaitSeconds)) {
        throw "$ServiceName still occupies port $Port after cleanup."
    }

    Write-Host ("{0}: previous listener removed." -f $ServiceName) -ForegroundColor Green
    return $true
}

function Stop-AhootsaCommandProcesses {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Patterns,

        [string]$ServiceName = "Ahootsa service"
    )

    try {
        $processes = Get-CimInstance Win32_Process -ErrorAction Stop
    } catch {
        return
    }

    foreach ($process in $processes) {
        $processId = [int]$process.ProcessId
        if ($processId -eq $PID -or $processId -le 4) {
            continue
        }

        $commandLine = [string]$process.CommandLine
        if ([string]::IsNullOrWhiteSpace($commandLine)) {
            continue
        }

        $matchesAll = $true
        foreach ($pattern in $Patterns) {
            if ($commandLine -notmatch $pattern) {
                $matchesAll = $false
                break
            }
        }

        if (-not $matchesAll) {
            continue
        }

        try {
            Write-Host (
                ("{0}: stopping stale process PID {1}..." -f $ServiceName, $processId)
            ) -ForegroundColor Yellow
            Stop-Process -Id $processId -Force -ErrorAction Stop
        } catch {
            Write-Host (
                ("{0}: could not stop stale PID {1}." -f $ServiceName, $processId)
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
        return $false
    }

    if (Test-AhootsaPort -Port $DaemonPort) {
        try {
            Invoke-RestMethod `
                -Uri "http://127.0.0.1:$DaemonPort/api/apps/stop-current-app" `
                -Method Post `
                -ContentType "application/json" `
                -Body "{}" `
                -TimeoutSec 3 |
                Out-Null

            Start-Sleep -Seconds 2
            if (-not (Test-AhootsaPort -Port $ConversationPort)) {
                Write-Host "Conversation App: stopped through the daemon API." -ForegroundColor Green
                return $true
            }
        } catch {
            Write-Host (
                "Conversation App: graceful stop was not accepted; " +
                "forced cleanup will be used."
            ) -ForegroundColor DarkYellow
        }
    }

    return $false
}
