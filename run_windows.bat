@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
    py -3 -m venv .venv
    if errorlevel 1 goto :fail
)
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto :fail
.venv\Scripts\python.exe -m yangdongi
if errorlevel 1 goto :fail
exit /b 0
:fail
 echo Setup or launch failed. Install Python 3.11 or newer and try again.
pause
exit /b 1
