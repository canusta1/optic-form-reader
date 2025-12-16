@echo off
echo ================================================
echo   VERITABANI TARAYICI - WEB ARAYUZ
echo ================================================
echo.

cd backend

echo Sanal ortam aktive ediliyor...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate
) else (
    echo UYARI: Sanal ortam bulunamadi!
    pause
    exit
)

echo.
echo Tarayicinizda acin: http://127.0.0.1:5001
echo.

python db_viewer.py

pause
