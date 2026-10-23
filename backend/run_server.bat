@echo off
title IntimacyLens Backend API
cd /d "%~dp0"
if exist venv\Scripts\activate.bat (
    echo Activating Python virtual environment...
    call venv\Scripts\activate.bat
)
echo Starting FastAPI server on http://127.0.0.1:8001 ...
python -m uvicorn main:app --host 0.0.0.0 --port 8001
pause
