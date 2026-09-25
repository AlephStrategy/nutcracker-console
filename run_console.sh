#!/bin/bash
# Lock working directory to the script's folder
cd "$(dirname "$0")"

# Create virtualenv and install dependencies only on first run
if [ ! -d "env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv env

    echo "Activating environment and installing dependencies..."
    source env/bin/activate
    python3 -m pip install --upgrade pip
    pip install -r requirements.txt
else
    # Activate existing environment
    source env/bin/activate
fi
echo [INFO] Running Nutcracker Console under MIT License. Provided AS-IS without warranty.
# Launch Streamlit using the virtualenv python executable
python3 -m streamlit run app/streamlit_app.py

# Keep terminal open if Streamlit crashes or exits
echo ""
read -p "Press [Enter] to exit..."