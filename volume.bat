@echo off
cd /d "%~dp0"
echo Starting LeisureLedger Volume Management Utility...
echo.
.venv\Scripts\python.exe manage_volume.py %*
echo.
pause
