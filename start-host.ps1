# TSPO Chat - Host Server
# Run this script on the machine that will host the backend server

Write-Host "Starting TSPO Chat Host Server..." -ForegroundColor Green
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Get IP address
Write-Host "Getting your IP address..." -ForegroundColor Cyan
try {
    # Get all IPv4 addresses and prioritize 10.x.x.x networks
    $allIPs = Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "192.168.*" -or $_.IPAddress -like "10.*" -or $_.IPAddress -like "172.*"}
    
    # Prioritize 10.x.x.x addresses first
    $ipAddress = ($allIPs | Where-Object {$_.IPAddress -like "10.*"} | Select-Object -First 1).IPAddress
    if (-not $ipAddress) {
        # Fallback to other private networks
        $ipAddress = ($allIPs | Select-Object -First 1).IPAddress
    }
    
    if ($ipAddress) {
        Write-Host "Your IP address: $ipAddress" -ForegroundColor Green
    } else {
        Write-Host "Your IP address: localhost" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Your IP address: localhost" -ForegroundColor Yellow
}

# Check if Node.js is installed
try {
    $nodeVersion = node --version 2>&1
    Write-Host "Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Node.js and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Installing backend dependencies..." -ForegroundColor Cyan
cd Backend
try {
    python -m pip install fastapi uvicorn aiohttp requests
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to install backend dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} catch {
    Write-Host "Error: Failed to install backend dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
cd ..\Frontend\tspo
try {
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to install frontend dependencies" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} catch {
    Write-Host "Error: Failed to install frontend dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Setting up frontend environment..." -ForegroundColor Cyan
if ($ipAddress) {
    $apiUrl = "http://$ipAddress`:8000"
} else {
    $apiUrl = "http://localhost:8000"
}

"VITE_API_URL=$apiUrl" | Out-File -FilePath ".env" -Encoding UTF8
Write-Host "Frontend will connect to: $apiUrl" -ForegroundColor Cyan

Write-Host ""
Write-Host "Starting backend server..." -ForegroundColor Green
Write-Host "Backend will be available at: http://$ipAddress`:8000" -ForegroundColor Cyan
Write-Host "API Documentation: http://$ipAddress`:8000/docs" -ForegroundColor Cyan
Write-Host ""

# Start backend in background
cd ..\..\Backend
Start-Process -FilePath "python" -ArgumentList "run_server.py", "--mode", "both", "--host", "0.0.0.0", "--port", "8000", "--socket-port", "8888" -WindowStyle Minimized

# Wait a moment for backend to start
Start-Sleep -Seconds 3

Write-Host "Starting frontend..." -ForegroundColor Green
Write-Host "Frontend will be available at: http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "Share this information with other users:" -ForegroundColor Yellow
Write-Host "  - Backend API: http://$ipAddress`:8000" -ForegroundColor White
Write-Host "  - Frontend: http://$ipAddress`:5173 (if you run with --host)" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host ""

# Start frontend
cd ..\Frontend\tspo
npm run dev

Write-Host ""
Write-Host "Stopping services..." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
