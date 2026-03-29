#!/bin/bash
cd "$(dirname "$0")"

# Create env if missing
if [ ! -d "env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv env
fi

# Activate env
source env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Launch console
streamlit run app/streamlit_app.py
