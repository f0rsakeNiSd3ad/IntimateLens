@echo off
setlocal enabledelayedexpansion
title IntimacyLens Controller

echo ===========================================================
echo                   IntimacyLens Launcher
echo         Local-First Psychological Telemetry System
echo ===========================================================
echo.

set "ROOT_DIR=%~dp0"
set "BACKEND_DIR=%ROOT_DIR%backend"
set "FRONTEND_DIR=%ROOT_DIR%frontend"

:: -------------------------------------------------------------
:: 1. Auto-Detect First-Time Setup
:: -------------------------------------------------------------
if not exist "%FRONTEND_DIR%\node_modules" (
    echo [!] First-time setup detected. Running setup.bat now...
    echo.
    call "%ROOT_DIR%setup.bat"
    if not exist "%FRONTEND_DIR%\node_modules" (
        echo [ERROR] Setup failed to complete. Please check the errors above.
        pause
        exit /b 1
    )
)

:: -------------------------------------------------------------
:: 2. Clean Up Any Lingering Stale Instances
:: -------------------------------------------------------------
call "%ROOT_DIR%stop.bat" >nul 2>nul

:: -------------------------------------------------------------
:: 3. Launch Backend and Frontend in Minimized Windows
:: -------------------------------------------------------------
echo [*] Launching FastAPI Backend on http://127.0.0.1:8001 ...
start "IntimacyLens Backend" /min cmd /c "call "%BACKEND_DIR%\run_server.bat""

echo [*] Launching Next.js Frontend on http://localhost:3000 ...
start "IntimacyLens Frontend" /min cmd /c "cd /d "%FRONTEND_DIR%" && npm run dev"

:: -------------------------------------------------------------
:: 4. Smart Health Polling (Instant & Reliable)
:: -------------------------------------------------------------
echo [*] Waiting for services to become ready...
powershell -NoProfile -Command "$ready = $false; for ($i = 0; $i -lt 30; $i++) { try { $res = Invoke-WebRequest -Uri 'http://127.0.0.1:8001/health' -UseBasicParsing -TimeoutSec 1; if ($res.StatusCode -eq 200) { $ready = $true; break } } catch {}; Start-Sleep -Milliseconds 600 }; exit ($ready ? 0 : 1)"

if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Backend is taking longer than usual to respond.
    echo Please check the minimized 'IntimacyLens Backend' window for details.
) else (
    echo [*] Backend is online!
)

:: -------------------------------------------------------------
:: 5. Open Web App in Browser
:: -------------------------------------------------------------
echo [*] Opening IntimacyLens in your browser...
start http://localhost:3000

:: -------------------------------------------------------------
:: 6. Unified Controller Dashboard
:: -------------------------------------------------------------
cls
echo ===========================================================
echo                   IntimacyLens is Running!
echo        Local-First Relationship Health Telemetry
echo ===========================================================
echo.
echo   • Web Application UI:  http://localhost:3000
echo   • Backend Health API:  http://127.0.0.1:8001/health
echo   • Interactive API Docs: http://127.0.0.1:8001/docs
echo.
echo ===========================================================
echo   STATUS: All services are active and running in the background.
echo.
echo   TO STOP AND EXIT:
echo   Press any key in this window (or close it) to shut down
echo   all IntimacyLens services cleanly.
echo ===========================================================
echo.
pause >nul

echo.
echo Stopping IntimacyLens services...
call "%ROOT_DIR%stop.bat"
exit /b 0
