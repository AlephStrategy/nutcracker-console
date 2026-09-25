@echo off
cd /d "%~dp0"

REM Create env and install dependencies if missing
if not exist env (
    echo Creating virtual environment...
    python -m venv env
    
    echo Activating environment and installing dependencies...
    call env\Scripts\activate
    pip install --upgrade pip
    pip install -r requirements.txt
) else (
    REM Activate existing env
    call env\Scripts\activate
)
echo [INFO] Running Nutcracker Console under MIT License. Provided AS-IS without warranty.
REM Launch console
streamlit run app\streamlit_app.py

REM Keep window open if Streamlit exits or crashes
pause