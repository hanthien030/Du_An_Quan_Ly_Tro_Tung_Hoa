@echo off
setlocal

cd /d "%~dp0"
title DuAnQuanLyTro - Setup

call :find_python
if errorlevel 1 (
    echo.
    echo [ERROR] Khong tim thay Python 3.
    echo Hay cai Python 3 va nho tick them tuy chon Add Python to PATH.
    pause
    exit /b 1
)

echo.
echo [1/4] Dang kiem tra virtual environment...
if not exist "venv\Scripts\python.exe" (
    echo     Tao moi thu muc venv...
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 (
        echo [ERROR] Tao virtual environment that bai.
        pause
        exit /b 1
    )
) else (
    echo     Da co san venv, bo qua buoc tao moi.
)

set "VENV_PY=%CD%\venv\Scripts\python.exe"

echo.
echo [2/4] Dang cai dependencies...
"%VENV_PY%" -m pip install --disable-pip-version-check -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Cai dependencies that bai.
    pause
    exit /b 1
)

echo.
echo [3/4] Dang seed du lieu demo...
"%VENV_PY%" seed.py
if errorlevel 1 (
    echo [ERROR] Seed du lieu that bai.
    pause
    exit /b 1
)

echo.
echo [4/4] Hoan tat setup.
echo Ban co the chay run.bat de mo ung dung web.
echo URL mac dinh: http://127.0.0.1:5000
echo.
pause
exit /b 0

:find_python
set "PYTHON_CMD="

where py >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_CMD=py -3"
    exit /b 0
)

where python >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_CMD=python"
    exit /b 0
)

exit /b 1
