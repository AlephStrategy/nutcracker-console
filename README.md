# Nutcracker Bot Console

A cross-platform control console for managing your Nutcracker trading bot instance.

This console allows testers to:
- Connect to their assigned backend instance
- Enter and update their Access Key
- Configure exchange API keys
- Initialize, start, stop, and restart the bot
- Manage trading pairs and PnL settings
- View live bot logs

---

## Installation

### 1. Extract the ZIP
Download and extract the package for your operating system.

### 2. Create a virtual environment

#### Windows:
python -m venv venv
venv\Scripts\activate


#### macOS / Linux:
python3 -m venv venv
source venv/bin/activate


### 3. Install dependencies
pip install -r requirements.txt


### 4. Run the console
streamlit run console.py


---

## Access Key

You will receive a unique Access Key from the developer.  
Enter it on first launch to connect to your backend instance.

To update your key later, use the **Update Access Key** option in the sidebar.

---

## Requirements

- Python 3.9+
- Internet connection
- Valid Access Key

---

## Support

If you encounter issues, contact the developer with:
- Your OS version
- Console logs
- Steps to reproduce the issue
