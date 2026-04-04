@echo off
cd /d "%~dp0"
echo Starting NetAcad Ethereal...
python start_app.py
if errorlevel 1 pause
