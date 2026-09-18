@echo off
chcp 65001 >nul
REM Сборка Windows-установщика. Запускать из корня проекта на Windows:
REM   packaging\windows\build.bat
REM Нужны: Python 3.11+, Inno Setup 6 (https://jrsoftware.org/isdl.php)

setlocal
cd /d "%~dp0\..\.."

if not exist .venv (
    echo [1/4] Создаю виртуальное окружение...
    py -3 -m venv .venv || goto :fail
)
call .venv\Scripts\activate.bat

echo [2/4] Устанавливаю зависимости...
python -m pip install -q --upgrade pip || goto :fail
python -m pip install -q -r requirements.txt -r requirements-build.txt || goto :fail

echo [3/4] PyInstaller...
pyinstaller packaging\cryptovisor.spec --noconfirm --clean || goto :fail

echo [4/4] Inno Setup...
set ISCC="%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist %ISCC% set ISCC="%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not exist %ISCC% (
    echo Inno Setup не найден. Установите с https://jrsoftware.org/isdl.php
    echo Портативная сборка готова: dist\CryptoVisor\CryptoVisor.exe
    goto :end
)
%ISCC% packaging\windows\setup.iss || goto :fail

echo.
echo Готово: dist\CryptoVisor-Setup-*.exe
goto :end

:fail
echo.
echo Сборка прервана с ошибкой.
exit /b 1

:end
endlocal
