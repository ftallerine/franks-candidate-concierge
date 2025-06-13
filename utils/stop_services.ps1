# PowerShell script to stop Frank's Candidate Concierge Services
Write-Host "Stopping Frank's Candidate Concierge Services..." -ForegroundColor Yellow
Write-Host ""

Write-Host "=== Checking for running services ===" -ForegroundColor Cyan

# Function to stop processes on a specific port
function Stop-ProcessOnPort {
    param([int]$Port, [string]$ServiceName)
    
    Write-Host "Searching for $ServiceName (Port $Port)..." -ForegroundColor Gray
    
    try {
        $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        if ($connections) {
            foreach ($conn in $connections) {
                $processId = $conn.OwningProcess
                $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
                if ($process) {
                    Write-Host "Found process $($process.Name) (PID: $processId) on port $Port, terminating..." -ForegroundColor Yellow
                    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
                    Write-Host "✓ $ServiceName stopped successfully" -ForegroundColor Green
                }
            }
        } else {
            Write-Host "ℹ No processes found on port $Port" -ForegroundColor Gray
        }
    }
    catch {
        Write-Host "⚠ Error checking port $Port`: $_" -ForegroundColor Red
    }
}

# Stop FastAPI Backend (Port 8000)
Stop-ProcessOnPort -Port 8000 -ServiceName "FastAPI Backend"

# Stop Streamlit Frontend (Port 8501)  
Stop-ProcessOnPort -Port 8501 -ServiceName "Streamlit Frontend"

Write-Host ""
Write-Host "=== Cleaning up Python processes ===" -ForegroundColor Cyan

# Stop Python processes with Streamlit in command line
Write-Host "Stopping any remaining Streamlit processes..." -ForegroundColor Gray
try {
    $streamlitProcesses = Get-WmiObject Win32_Process | Where-Object { 
        $_.Name -eq "python.exe" -and $_.CommandLine -like "*streamlit*" 
    }
    
    if ($streamlitProcesses) {
        foreach ($proc in $streamlitProcesses) {
            Write-Host "Stopping Streamlit process (PID: $($proc.ProcessId))..." -ForegroundColor Yellow
            Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
        }
        Write-Host "✓ Streamlit processes stopped" -ForegroundColor Green
    } else {
        Write-Host "ℹ No Streamlit processes found" -ForegroundColor Gray
    }
}
catch {
    Write-Host "⚠ Error stopping Streamlit processes: $_" -ForegroundColor Red
}

# Stop Python processes with Uvicorn in command line
Write-Host "Stopping any remaining Uvicorn processes..." -ForegroundColor Gray
try {
    $uvicornProcesses = Get-WmiObject Win32_Process | Where-Object { 
        $_.Name -eq "python.exe" -and $_.CommandLine -like "*uvicorn*" 
    }
    
    if ($uvicornProcesses) {
        foreach ($proc in $uvicornProcesses) {
            Write-Host "Stopping Uvicorn process (PID: $($proc.ProcessId))..." -ForegroundColor Yellow
            Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
        }
        Write-Host "✓ Uvicorn processes stopped" -ForegroundColor Green
    } else {
        Write-Host "ℹ No Uvicorn processes found" -ForegroundColor Gray
    }
}
catch {
    Write-Host "⚠ Error stopping Uvicorn processes: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Port verification ===" -ForegroundColor Cyan

# Check if ports are now free
Write-Host "Checking if ports are now free..." -ForegroundColor Gray

try {
    $port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
    if (-not $port8000) {
        Write-Host "✓ Port 8000 is now free" -ForegroundColor Green
    } else {
        Write-Host "⚠ Port 8000 may still be in use" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "✓ Port 8000 is now free" -ForegroundColor Green
}

try {
    $port8501 = Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue
    if (-not $port8501) {
        Write-Host "✓ Port 8501 is now free" -ForegroundColor Green
    } else {
        Write-Host "⚠ Port 8501 may still be in use" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "✓ Port 8501 is now free" -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ Service shutdown complete!" -ForegroundColor Green
Write-Host ""
Write-Host "All Frank's Candidate Concierge services have been stopped." -ForegroundColor White
Write-Host "Ports 8000 and 8501 should now be available." -ForegroundColor White
Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 