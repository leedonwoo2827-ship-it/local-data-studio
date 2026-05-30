@echo off
REM Local Data Studio - Windows run
cd /d "%~dp0"
call .venv\Scripts\activate.bat
streamlit run app.py
