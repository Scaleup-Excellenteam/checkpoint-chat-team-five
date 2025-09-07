# TSPO Chat Backend - Start Socket Server Only
# Run this script to start only the socket server for real-time chat

Write-Host "Starting TSPO Socket Server..." -ForegroundColor Green
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

Write-Host "Getting your IP address..." -ForegroundColor Cyan
try {
    $ipAddress = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "192.168.*" -or $_.IPAddress -like "10.*" -or $_.IPAddress -like "172.*"} | Select-Object -First 1).IPAddress
    if ($ipAddress) {
        Write-Host "Your IP address: $ipAddress" -ForegroundColor Green
    } else {
        Write-Host "Your IP address: localhost" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Your IP address: localhost" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Starting socket server..." -ForegroundColor Green
Write-Host "Server will be available at: 0.0.0.0:8888" -ForegroundColor Cyan
Write-Host ""
Write-Host "To connect from another computer:" -ForegroundColor Yellow
Write-Host "   1. Make sure both computers are on the same network" -ForegroundColor White
Write-Host "   2. On the other computer, run:" -ForegroundColor White
if ($ipAddress) {
    Write-Host "      python socket_client_standalone.py --host $ipAddress --port 8888 --room general --sender YourName" -ForegroundColor Cyan
} else {
    Write-Host "      python socket_client_standalone.py --host YOUR_IP --port 8888 --room general --sender YourName" -ForegroundColor Cyan
}
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the socket server
python socket_server_standalone.py

Write-Host ""
Write-Host "Socket server stopped" -ForegroundColor Yellow
Read-Host "Press Enter to exit"
