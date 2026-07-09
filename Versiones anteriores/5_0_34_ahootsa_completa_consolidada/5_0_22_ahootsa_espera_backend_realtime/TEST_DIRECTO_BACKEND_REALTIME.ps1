$ErrorActionPreference = "Continue"

Write-Host "============================================================"
Write-Host "TEST DIRECTO BACKEND REALTIME AHOOTSA"
Write-Host "============================================================"

function Show-Status {
    try {
        $s = Invoke-RestMethod http://127.0.0.1:7860/status -TimeoutSec 5
        Write-Host ""
        Write-Host "active_backend          =" $s.active_backend
        Write-Host "backend_provider        =" $s.backend_provider
        Write-Host "backend_connected       =" $s.backend_connected
        Write-Host "backend_state           =" $s.backend_connection_state
        Write-Host "backend_error           =" $s.backend_error
        Write-Host "has_key                 =" $s.has_key
        Write-Host "has_hf_connection       =" $s.has_hf_connection
        Write-Host "hf_connection_mode      =" $s.hf_connection_mode
        Write-Host "can_proceed_with_hf     =" $s.can_proceed_with_hf
        return $s
    } catch {
        Write-Host "[ERROR] No responde http://127.0.0.1:7860/status"
        Write-Host $_.Exception.Message
        return $null
    }
}

function Show-Mic {
    try {
        $m = Invoke-RestMethod http://127.0.0.1:7860/mic -TimeoutSec 5
        Write-Host "mic muted               =" $m.muted
    } catch {
        Write-Host "[WARN] No responde /mic:" $_.Exception.Message
    }
}

function Show-Voice {
    try {
        $v = Invoke-RestMethod http://127.0.0.1:7860/voices/current -TimeoutSec 5
        Write-Host "voice                   =" $v.voice
    } catch {
        Write-Host "[WARN] No responde /voices/current:" $_.Exception.Message
    }
}

function Test-Web {
    Write-Host ""
    Write-Host "Comprobando acceso externo..."
    try {
        $g = Invoke-WebRequest "https://api.gradio.app/gradio-messaging/en" -UseBasicParsing -TimeoutSec 10
        Write-Host "[OK] api.gradio.app ->" $g.StatusCode
    } catch {
        Write-Host "[WARN] api.gradio.app ->" $_.Exception.Message
    }

    try {
        $h = Invoke-WebRequest "https://huggingface.co" -UseBasicParsing -TimeoutSec 10
        Write-Host "[OK] huggingface.co ->" $h.StatusCode
    } catch {
        Write-Host "[WARN] huggingface.co ->" $_.Exception.Message
    }
}

Write-Host ""
Write-Host "Estado inicial:"
$s = Show-Status
Show-Mic
Show-Voice
Test-Web

Write-Host ""
Write-Host "Esperando conexion realtime durante 3 minutos..."
for ($i = 1; $i -le 36; $i++) {
    Start-Sleep -Seconds 5
    $s = Show-Status
    if ($s -ne $null -and $s.backend_connected -eq $true) {
        Write-Host ""
        Write-Host "[OK] BACKEND REALTIME CONECTADO"
        Show-Mic
        Show-Voice
        exit 0
    }

    if ($s -ne $null -and $s.backend_error) {
        Write-Host ""
        Write-Host "[ERROR BACKEND]"
        Write-Host $s.backend_error
    }
}

Write-Host ""
Write-Host "[NO CONECTADO]"
Write-Host "Si aparece 1013 / No pipeline capacity available, el fallo viene del backend realtime remoto."
Write-Host "Si backend_error esta vacio pero sigue connecting, la sesion no ha terminado de abrirse."
