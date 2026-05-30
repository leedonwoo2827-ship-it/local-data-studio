@echo off
REM Local Data Studio - Windows setup
setlocal

cd /d "%~dp0"

echo [1/3] Creating virtual environment (.venv)...
if not exist ".venv" (
    python -m venv .venv
)

echo [2/3] Activating and upgrading pip...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip

echo [3/3] Installing dependencies...
pip install -r requirements.txt

echo.
echo Done. Next:
echo   1) copy .env.example .env   ^&^&  edit UBION_LITELLM_KEY
echo   2) run.bat
endlocal
