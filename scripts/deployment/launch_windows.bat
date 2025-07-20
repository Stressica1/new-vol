@echo off
REM 🏔️ Alpine Trading Bot - Windows Launcher
REM Simple batch script for Windows users

echo 🏔️ Alpine Trading Bot - Windows Launcher
echo =====================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.9+ and add it to PATH.
    echo.
    echo Download Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if we're in a virtual environment
if defined VIRTUAL_ENV (
    echo ✅ Virtual environment detected: %VIRTUAL_ENV%
) else (
    echo ℹ️  No virtual environment detected. Consider using one for better isolation.
)

echo.
echo 🚀 Launching Alpine Trading Bot...
echo.

REM Run the Python launcher
python scripts/deployment/launch_alpine.py

echo.
echo 👋 Alpine Trading Bot session ended.
pause
