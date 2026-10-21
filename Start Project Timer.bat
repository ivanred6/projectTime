@echo off
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
    py -3 project_timer_v2.py
    if errorlevel 1 pause
    exit /b
)
where python >nul 2>nul
if not errorlevel 1 (
    python project_timer_v2.py
    if errorlevel 1 pause
    exit /b
)
echo Python 3 is required. Install Python for Windows with Tcl/Tk support.
pause
