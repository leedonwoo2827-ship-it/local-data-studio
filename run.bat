@echo off
REM Local Data Studio - Windows run (탐색기에서 더블클릭)
cd /d "%~dp0"
title Local Data Studio

if not exist ".venv\Scripts\activate.bat" (
    echo [오류] 먼저 setup.bat 을 더블클릭해 설치하세요.
    echo.
    pause
    exit /b 1
)

echo 브라우저에서 대시보드가 열립니다. 이 창은 닫지 마세요.
echo (종료하려면 이 창에서 Ctrl+C)
echo.
call .venv\Scripts\activate.bat
streamlit run app.py
pause
