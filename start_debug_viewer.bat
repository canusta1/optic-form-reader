@echo off
echo ========================================
echo   OMR Debug Goruntuleyici Baslatiliyor
echo ========================================
echo.
cd /d "%~dp0backend"
echo Port: 5001
echo URL: http://localhost:5001
echo.
python debug_viewer.py
pause
