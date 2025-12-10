@echo off
echo ================================================
echo   OPTIK FORM OKUYUCU - BACKEND BASLATMA
echo ================================================
echo.

cd backend

echo [1/3] Sanal ortam kontrol ediliyor...
if not exist "venv\" (
    echo Sanal ortam bulunamadi. Olusturuluyor...
    python -m venv venv
    echo Sanal ortam olusturuldu.
) else (
    echo Sanal ortam mevcut.
)

echo.
echo [2/3] Sanal ortam aktive ediliyor...
call venv\Scripts\activate

echo.
echo [3/3] Bagimliliklar kontrol ediliyor...
pip install -r requirements.txt --quiet

echo.
echo ================================================
echo   BACKEND BASLATILIYOR...
echo   URL: http://127.0.0.1:5000
echo ================================================
echo.

python app.py

pause
