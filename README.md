# Nutcracker Pilot Console

A cross‑platform control console for managing your assigned Nutcracker trading bot instance during the Early Pilot phase.

This console **does not run a bot locally**.  
It connects securely to your dedicated backend instance hosted on Aleph Strategy’s VPS.

---

## 🚧 Pilot Requirements

Before using the console, testers must:

1. Sign the **Nutcracker Early Pilot & Sandbox Agreement**
2. Receive their **unique Access Key** from the developer
3. Provide their **static IP address** for backend whitelisting
4. Provide **No‑Withdrawal, Spot‑Only API keys** for their exchange

The console will not function without these steps.

---

## 🧭 What the Console Allows You to Do

- Connect to your assigned backend instance  
- Enter or update your Access Key  
- Configure exchange API keys  
- Initialize, start, stop, and restart your bot  
- Manage trading pairs and PnL parameters  
- View live logs and performance metrics  

All trading logic runs on the VPS — the console is your control panel.

---

## ▶️ Running the Console

### **Windows**
Double‑click:

```
run_console.bat
```

The launcher will:
- Create a virtual environment (first run only)
- Install dependencies
- Launch the Streamlit interface

---

### **macOS**
Double‑click:

```
run_console.command
```

If macOS blocks it, right‑click → **Open** → confirm.

---

### **Linux**
1. Right‑click `run_console.sh` → **Properties** → allow executing as program  
2. Then run:

```
./run_console.sh
```

---

## 🔑 Access Key

You will receive a unique Access Key after signing the Pilot Agreement.  
Enter it on first launch to connect to your backend instance.

To update your key later, use **Update Access Key** in the sidebar.

---

## 📦 Requirements

- Python 3.9+ (macOS/Linux only)  
- Internet connection  
- Valid Access Key  
- Whitelisted IP address  

Windows users do **not** need Python installed — the launcher handles everything.

---

## 📚 Documentation

See the `/docs` folder for:

- **Nutcracker Early Pilot & Sandbox Agreement**  
- **Nutcracker Pilot Onboarding & Strategy Guide**

---

## 🛠 Support

If you encounter issues, contact the developer with:

- Your OS version  
- Console logs  
- Steps to reproduce the issue  
