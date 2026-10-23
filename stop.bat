@echo off
title IntimacyLens Shutdown
echo ===========================================================
echo               Stopping IntimacyLens Servers
echo ===========================================================

:: 1. Terminate titled server command windows
taskkill /FI "WINDOWTITLE eq IntimacyLens Backend*" /F /T >nul 2>nul
taskkill /FI "WINDOWTITLE eq IntimacyLens Frontend*" /F /T >nul 2>nul

:: 2. Terminate any remaining process bound to port 8001
powershell -NoProfile -Command "$p = (Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique); foreach ($id in $p) { if ($id -gt 4) { Stop-Process -Id $id -Force -ErrorAction SilentlyContinue } }"

:: 3. Terminate Next.js dev server on port 3000 if running from IntimacyLens
powershell -NoProfile -Command "$p = (Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique); foreach ($id in $p) { if ($id -gt 4) { $proc = Get-CimInstance Win32_Process -Filter \"ProcessId = $id\"; if ($proc -and $proc.CommandLine -match 'IntimacyLens') { Stop-Process -Id $id -Force -ErrorAction SilentlyContinue } } }"

echo.
echo All IntimacyLens servers have been shut down cleanly.
timeout /t 2 >nul
