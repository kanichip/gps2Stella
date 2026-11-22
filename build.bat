
@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo  GPS2STELLA EXE Build
echo ========================================

REM 仮想環境があれば使用
if exist ".venv\Scripts\python.exe" (
    set "PYTHON=.venv\Scripts\python.exe"
) else (
    set "PYTHON=python"
)

REM 必要なライブラリをインストール
"%PYTHON%" -m pip install --upgrade pyinstaller requests

if errorlevel 1 goto ERROR

REM EXE作成
"%PYTHON%" -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --console ^
    --name GPS2STELLA ^
    main.py

if errorlevel 1 goto ERROR

echo.
echo ========================================
echo  Build SUCCESS!
echo  dist\GPS2STELLA.exe
echo ========================================
pause
exit /b 0

:ERROR
echo.
echo ========================================
echo  Build FAILED!
echo ========================================
pause
exit /b 1
