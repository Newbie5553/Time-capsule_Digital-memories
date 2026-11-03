@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Python virtual environment missing. Run start_windows.bat first.
  exit /b 1
)
.venv\Scripts\python.exe -m flask --app app:create_app send-notifications
exit /b %errorlevel%
