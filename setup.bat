@echo off
REM Local Data Studio - Windows setup (탐색기에서 더블클릭)
setlocal
cd /d "%~dp0"
title Local Data Studio - 설치

echo ================================================
echo   Local Data Studio 설치를 시작합니다
echo ================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo [오류] Python 이 설치되어 있지 않습니다.
    echo   https://www.python.org/downloads/ 에서 Python 3.10+ 설치 후
    echo   설치 화면에서 "Add python.exe to PATH" 를 체크하세요.
    echo.
    pause
    exit /b 1
)

echo [1/3] 가상환경(.venv) 준비...
if not exist ".venv" (
    python -m venv .venv
)

echo [2/3] pip 업그레이드...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip

echo [3/3] 패키지 설치 (수 분 걸릴 수 있습니다)...
pip install -r requirements.txt

echo.
echo ================================================
echo   설치 완료!  이제 run.bat 을 더블클릭하세요.
echo   (앱 화면의 "API 설정"에 회사가 준 주소/키 입력)
echo ================================================
echo.
pause
endlocal
