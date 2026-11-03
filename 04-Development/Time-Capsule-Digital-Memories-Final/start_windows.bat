@echo off
setlocal
cd /d "%~dp0"
if exist .venv\Scripts\python.exe goto dependencies
where py >nul 2>nul
if not errorlevel 1 (
    py -3 -m venv .venv
    goto checkenv
)
where python >nul 2>nul
if not errorlevel 1 (
    python -m venv .venv
    goto checkenv
)
echo Python was not found. Install Python 3.11 or newer and enable Add Python to PATH.
pause
exit /b 1
:checkenv
if not exist .venv\Scripts\python.exe (
    echo Could not create the environment. Check your Python installation.
    pause
    exit /b 1
)
:dependencies
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
    echo Dependency installation failed. Check your internet connection.
    pause
    exit /b 1
)
echo Open http://127.0.0.1:5000 in your browser.
echo Keep this window open. Press Ctrl+C to stop the app.
.venv\Scripts\python.exe app.py
pause
