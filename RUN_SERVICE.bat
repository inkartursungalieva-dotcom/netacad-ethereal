@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ===================================================
echo           Computer Networks - Startup
echo ===================================================
echo.
echo [INFO] Current directory: %CD%
echo [INFO] Python version:
python --version
echo.

:: Проверка наличия venv (опционально)
if exist venv (
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate
)

echo [INFO] Starting application...
python start_app.py

if errorlevel 1 (
    echo.
    echo [ERROR] Application failed to start.
    echo [TIP] Check if MySQL is running and port 8000 is free.
    pause
)

