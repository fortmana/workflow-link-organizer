@echo off
setlocal enabledelayedexpansion

REM Already running? Just open the browser.
curl -s --max-time 2 "http://127.0.0.1:5757/health" >nul 2>&1
if !errorlevel! equ 0 goto :open

REM Find pythonw.exe (sits next to python.exe) so no console window appears.
for /f "usebackq delims=" %%i in (`python -c "import os,sys; print(os.path.join(os.path.dirname(sys.executable),'pythonw.exe'))"`) do set "PYW=%%i"
if not exist "!PYW!" set "PYW=python"

REM Start the tray app (server + system-tray icon).
set WLO_DEV=0
start "" /D "%~dp0src" "!PYW!" -m wlo.tray.tray_app

REM Wait up to 15 seconds for the server to come up.
for /l %%i in (1,1,15) do (
    timeout /t 1 /nobreak >nul
    curl -s --max-time 1 "http://127.0.0.1:5757/health" >nul 2>&1
    if !errorlevel! equ 0 goto :open
)

:open
start "" "http://127.0.0.1:5757"
endlocal

