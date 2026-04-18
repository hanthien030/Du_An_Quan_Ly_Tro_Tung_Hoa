@echo off
setlocal

cd /d "%~dp0"
title DuAnQuanLyTro - Run

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Chua tim thay venv.
    echo Hay chay setup.bat truoc.
    echo.
    pause
    exit /b 1
)

echo Dang khoi dong web app...
start "DuAnQuanLyTro Web" cmd /k ""%CD%\venv\Scripts\python.exe" run.py"

echo Dang mo trinh duyet...
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:5000"

echo Da gui lenh khoi dong server.
echo Neu trinh duyet chua vao duoc ngay, hay doi vai giay roi refresh lai trang.
echo.
pause
exit /b 0
