@echo off
echo ===========================================
echo   CareerAssistant Dashboard Launcher
echo ===========================================
echo.

cd /d "C:\Users\Laptop K1\Downloads\Prototype"

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python and try again.
    pause
    exit /b 1
)

:: Check if server is already running
powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://127.0.0.1:5000' -TimeoutSec 2 -UseBasicParsing; exit 0 } catch { exit 1 }"
if %errorlevel% == 0 (
    echo Dashboard is already running!
    echo Opening browser...
    start http://127.0.0.1:5000
    echo.
    echo To stop the server, find the Python window and press Ctrl+C.
    pause
    exit /b 0
)

echo Starting CareerAssistant server...
echo.

:: Start the Flask server in a new window
start "CareerAssistant Server" cmd /k "cd /d C:\Users\Laptop K1\Downloads\Prototype && echo Starting server... && python src\dashboard_server.py"

:: Wait for server to start
echo Waiting for server to start...
timeout /t 4 /nobreak >nul

:: Open browser
echo Opening dashboard in your browser...
start http://127.0.0.1:5000

echo.
echo ===========================================
echo   Dashboard is live at:
echo   http://127.0.0.1:5000
echo ===========================================
echo.
echo IMPORTANT: Keep the 'CareerAssistant Server'
echo window open. If you close it, the dashboard
echo will stop working.
echo.
pause
