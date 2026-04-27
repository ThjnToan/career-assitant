$serverPath = "C:\Users\Laptop K1\Downloads\Prototype\src\dashboard_server.py"
$workingDir = "C:\Users\Laptop K1\Downloads\Prototype"

Write-Host "Starting CareerAssistant Dashboard Server..." -ForegroundColor Green

# Start the server in a hidden/minimized window
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = "python"
$psi.Arguments = "$serverPath"
$psi.WorkingDirectory = $workingDir
$psi.WindowStyle = "Minimized"
$psi.UseShellExecute = $true

$process = [System.Diagnostics.Process]::Start($psi)

# Wait for server to initialize
Start-Sleep -Seconds 3

# Open browser
Write-Host "Opening dashboard in your default browser..." -ForegroundColor Cyan
Start-Process "http://127.0.0.1:5000"

Write-Host ""
Write-Host "Dashboard is live at: http://127.0.0.1:5000" -ForegroundColor Yellow
Write-Host "Server is running in the background (PID: $($process.Id))" -ForegroundColor Gray
Write-Host "To stop the server, run: Stop-Process -Id $($process.Id)" -ForegroundColor Gray
