@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
 echo Python was not found. Install Python 3.11 or newer from python.org, then try again.
 pause
 exit /b 1
)
if not exist .venv\Scripts\python.exe py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
 echo Installation failed. Check your internet connection and try again.
 pause
 exit /b 1
)
echo Open http://127.0.0.1:5000 in your browser. Press Ctrl+C here to stop.
.venv\Scripts\python.exe app.py
pause
