@echo off
echo.
echo ===========================================
echo   CareerAssistant - Morning Digest
echo ===========================================
echo.

cd /d "C:\Users\Laptop K1\Downloads\Prototype"

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found.
    pause
    exit /b 1
)

:: Show the daily dashboard
python career.py

echo.
echo ===========================================
echo   Reminders:
echo   - Log every application you submit today
echo   - Check followups: python career.py followups
echo   - Update statuses when you hear back
echo ===========================================
echo.

pause
