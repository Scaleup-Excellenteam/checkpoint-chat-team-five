# TSPO Chat - Client
# Run this script on machines that will connect to the host server

Write-Host "Starting TSPO Chat Client..." -ForegroundColor Green
Write-Host ""

# Read SYSTEM_IP from root .env if present, otherwise prompt
$serverIP = $null
try {
    if (Test-Path ".env") {
        $envContent = Get-Content ".env" -Raw
        if ($envContent -match "SYSTEM_IP=(.+)") {
            $serverIP = $matches[1].Trim()
        }
    }
    if (-not $serverIP -and (Test-Path "..\.env")) {
        $envContent = Get-Content "..\.env" -Raw
        if ($envContent -match "SYSTEM_IP=(.+)") {
            $serverIP = $matches[1].Trim()
        }
    }
} catch {}

if (-not $serverIP) {
    $serverIP = Read-Host "Enter the host server IP address (e.g., 192.168.1.100)"
}
Write-Host "Connecting to server: $serverIP" -ForegroundColor Cyan
Write-Host ""

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
Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
cd Frontend\tspo
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

Write-Host ""
Write-Host "Testing connection to server..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://$serverIP`:8000/health/" -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "Successfully connected to server!" -ForegroundColor Green
    } else {
        Write-Host "Warning: Server responded with status $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Warning: Could not connect to server. Make sure:" -ForegroundColor Yellow
    Write-Host "  - Server is running and accessible" -ForegroundColor White
    Write-Host "  - IP address is correct: $serverIP" -ForegroundColor White
    Write-Host "  - Firewall allows connections on port 8000" -ForegroundColor White
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 1
    }
}

Write-Host ""
Write-Host "Starting frontend client..." -ForegroundColor Green
Write-Host "Frontend (local):    http://localhost:5173" -ForegroundColor Cyan
Write-Host "Frontend (for LAN):  http://$env:COMPUTERNAME`:5173" -ForegroundColor Cyan
Write-Host "Connecting to server: http://$serverIP`:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the client" -ForegroundColor Yellow
Write-Host ""

# Start frontend with API URL env set for this session only
$env:VITE_API_URL = "http://$serverIP`:8000"

# Open firewall for Vite dev server (port 5173) - will prompt for admin
try {
    Start-Process powershell -Verb runAs -ArgumentList 'netsh advfirewall firewall add rule name="Vite Dev 5173" dir=in action=allow protocol=TCP localport=5173' | Out-Null
} catch {}

# Serve over LAN
npm run dev -- --host

Write-Host ""
Write-Host "Client stopped" -ForegroundColor Yellow
Read-Host "Press Enter to exit"
