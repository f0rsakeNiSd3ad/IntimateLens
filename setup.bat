@echo off
setlocal enabledelayedexpansion
title IntimacyLens - First-Time Setup

echo ===========================================================
echo                IntimacyLens First-Time Setup
echo         Local-First Psychological Telemetry System
echo ===========================================================
echo.

set "ROOT_DIR=%~dp0"
set "BACKEND_DIR=%ROOT_DIR%backend"
set "FRONTEND_DIR=%ROOT_DIR%frontend"

:: -------------------------------------------------------------
:: Step 1: Check Python
:: -------------------------------------------------------------
echo [1/4] Checking Python environment...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found in your system PATH.
    echo Please download and install Python 3.10+ from:
    echo   https://www.python.org/downloads/
    echo *Make sure to check "Add Python to PATH" during installation.*
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo       Found %%v

:: -------------------------------------------------------------
:: Step 2: Check Node.js and npm
:: -------------------------------------------------------------
echo.
echo [2/4] Checking Node.js and npm...
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js was not found in your system PATH.
    echo Please download and install Node.js 18+ LTS from:
    echo   https://nodejs.org/
    echo.
    pause
    exit /b 1
)
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] npm was not found in your system PATH.
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('node --version 2^>^&1') do echo       Found Node.js %%v
for /f "tokens=*" %%v in ('npm --version 2^>^&1') do echo       Found npm v%%v

:: -------------------------------------------------------------
:: Step 3: Setup Python Environment & Dependencies
:: -------------------------------------------------------------
echo.
echo [3/4] Installing backend dependencies...
cd /d "%BACKEND_DIR%"
if not exist "venv" (
    echo       Creating Python virtual environment in backend\venv...
    python -m venv venv
)
if exist "venv\Scripts\activate.bat" (
    echo       Activating virtual environment...
    call venv\Scripts\activate.bat
)
echo       Installing core backend packages...
python -m pip install --upgrade pip >nul 2>nul
pip install fastapi uvicorn pydantic python-multipart httpx
if %errorlevel% neq 0 (
    echo [WARNING] Trying direct pip install...
    python -m pip install fastapi uvicorn pydantic python-multipart httpx
)
echo       Backend dependencies installed successfully.
cd /d "%ROOT_DIR%"

:: -------------------------------------------------------------
:: Step 4: Setup Frontend Dependencies
:: -------------------------------------------------------------
echo.
echo [4/4] Installing frontend dependencies and building web app...
cd /d "%FRONTEND_DIR%"
if not exist "node_modules" (
    echo       Installing npm packages (this may take a minute on first run)...
    call npm install
) else (
    echo       Frontend node_modules already found. Verifying...
    call npm install
)

echo       Building optimized production pages...
call npm run build
cd /d "%ROOT_DIR%"

:: -------------------------------------------------------------
:: Setup Complete!
:: -------------------------------------------------------------
echo.
echo ===========================================================
echo           First-Time Setup Completed Successfully!
echo ===========================================================
echo.
echo  IntimacyLens is fully configured on this computer.
echo.
echo  HOW TO START THE APP:
echo    Simply double-click:  start.bat
echo.
echo  It will launch the backend, frontend, and open your browser
echo  automatically in seconds.
echo ===========================================================
echo.
pause
