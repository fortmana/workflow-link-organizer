@echo off
setlocal enabledelayedexpansion

REM Stop the process on port 5757.
for /f "tokens=5" %%p in ('netstat -ano ^| findstr :5757 ^| findstr LISTENING') do (
    taskkill /PID %%p /F >nul 2>&1
)

timeout /t 1 /nobreak >nul

for /f "usebackq delims=" %%i in (`python -c "import os,sys; print(os.path.join(os.path.dirname(sys.executable),'pythonw.exe'))"`) do set "PYW=%%i"
if not exist "!PYW!" set "PYW=python"

set WLO_DEV=0
start "" /D "%~dp0src" "!PYW!" -m wlo.tray.tray_app

endlocal

