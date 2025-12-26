@echo off
echo ========================================
echo   Optik Form Backend Baslatiliyor
echo ========================================
echo.

cd /d "%~dp0backend"

if not exist "venv" (
    echo Python sanal ortam olusturuluyor...
    python -m venv venv
)

echo Sanal ortam aktif ediliyor...
call venv\Scripts\activate

echo Gerekli paketler yukleniyor...
pip install -r requirements.txt --quiet

echo.
echo Backend baslatiliyor...
python app.py

pause
