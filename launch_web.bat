@echo off
echo ===========================================
echo   CareerAssistant Pro - Web App
echo ===========================================
echo.

cd /d "C:\Users\Laptop K1\Downloads\Prototype"

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python.
    pause
    exit /b 1
)

:: Check if already running
powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:5000' -TimeoutSec 2 -UseBasicParsing; exit 0 } catch { exit 1 }"
if %errorlevel% == 0 (
    echo Server is already running!
    echo Opening browser...
    start http://127.0.0.1:5000
    pause
    exit /b 0
)

echo Starting server...
start "CareerAssistant Server" cmd /k "cd /d C:\Users\Laptop K1\Downloads\Prototype && python run.py"

echo Waiting for server to start...
timeout /t 4 /nobreak >nul

echo Opening browser...
start http://127.0.0.1:5000

echo.
echo ===========================================
echo   Dashboard: http://127.0.0.1:5000
echo ===========================================
echo.
echo Keep this window open while using the app.
echo Press Ctrl+C in the server window to stop.
pause
