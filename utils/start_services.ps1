# PowerShell script to start Frank's Candidate Concierge Services
Write-Host "Starting Frank's Candidate Concierge..." -ForegroundColor Yellow
Write-Host ""

Write-Host "=== Pre-flight checks ===" -ForegroundColor Cyan

# Function to check if a port is in use
function Test-PortInUse {
    param([int]$Port, [string]$ServiceName)
    
    Write-Host "Checking if port $Port is available for $ServiceName..." -ForegroundColor Gray
    
    try {
        $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
        if ($connections) {
            Write-Host "⚠ Port $Port is already in use by another process" -ForegroundColor Red
            return $true
        } else {
            Write-Host "✓ Port $Port is available" -ForegroundColor Green
            return $false
        }
    }
    catch {
        Write-Host "✓ Port $Port is available" -ForegroundColor Green
        return $false
    }
}

# Check if ports are available
$port8000InUse = Test-PortInUse -Port 8000 -ServiceName "FastAPI Backend"
$port8501InUse = Test-PortInUse -Port 8501 -ServiceName "Streamlit Frontend"

if ($port8000InUse -or $port8501InUse) {
    Write-Host ""
    Write-Host "⚠ Warning: Some ports are already in use!" -ForegroundColor Yellow
    Write-Host "You may want to run stop_services.ps1 first to clean up existing processes." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Do you want to continue anyway? (y/N): " -NoNewline -ForegroundColor White
    $response = Read-Host
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "Operation cancelled." -ForegroundColor Red
        Write-Host "Press any key to exit..." -ForegroundColor Gray
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit
    }
}

Write-Host ""
Write-Host "=== Starting services ===" -ForegroundColor Cyan

# Start FastAPI Backend
Write-Host "Starting FastAPI Backend Server..." -ForegroundColor White
try {
    $backendProcess = Start-Process -FilePath "cmd" -ArgumentList "/k", "uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000" -WindowStyle Normal -PassThru
    Write-Host "✓ FastAPI Backend started (PID: $($backendProcess.Id))" -ForegroundColor Green
}
catch {
    Write-Host "✗ Failed to start FastAPI Backend: $_" -ForegroundColor Red
}

# Wait for backend to initialize
Write-Host "Waiting 5 seconds for backend to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# Start Streamlit Frontend
Write-Host "Starting Streamlit Frontend..." -ForegroundColor White
try {
    $frontendProcess = Start-Process -FilePath "cmd" -ArgumentList "/k", "streamlit run app/streamlit_app.py" -WindowStyle Normal -PassThru
    Write-Host "✓ Streamlit Frontend started (PID: $($frontendProcess.Id))" -ForegroundColor Green
}
catch {
    Write-Host "✗ Failed to start Streamlit Frontend: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Service Information ===" -ForegroundColor Cyan
Write-Host "Services are starting up!" -ForegroundColor White
Write-Host "- FastAPI Backend: http://localhost:8000" -ForegroundColor White
Write-Host "- Streamlit Frontend: http://localhost:8501" -ForegroundColor White
Write-Host ""
Write-Host "Both services will open in separate command windows." -ForegroundColor White

Write-Host ""
Write-Host "✅ Startup sequence complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 