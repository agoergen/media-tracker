@echo off
cd /d "%~dp0"
echo Starting LeisureLedger Database Backup Utility...
echo.
.venv\Scripts\python.exe backup_db.py %*
echo.
pause

