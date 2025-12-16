@echo off
echo ================================================
echo   VERITABANI YONETIM ARACI
echo ================================================
echo.

cd backend

echo Sanal ortam aktive ediliyor...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate
) else (
    echo UYARI: Sanal ortam bulunamadi!
    echo Once 'start_backend.bat' calistirin.
    pause
    exit
)

echo.
python db_manager.py

pause
