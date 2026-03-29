@echo off
cd /d "%~dp0"

REM Create env if missing
if not exist env (
    echo Creating virtual environment...
    python -m venv env
)

REM Activate env
call env\Scripts\activate

REM Install dependencies
pip install -r requirements.txt

REM Launch console
streamlit run app\streamlit_app.py
