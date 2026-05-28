@echo off
for /f "tokens=5" %%p in ('netstat -ano ^| findstr :5757 ^| findstr LISTENING') do (
    taskkill /PID %%p /F >nul 2>&1
    echo Workflow Link Organizer stopped.
    exit /b 0
)
echo Workflow Link Organizer was not running.
