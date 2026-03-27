import streamlit as st
import html
import requests
import time
import datetime
import pandas as pd
from PIL import Image
import json
import os
from pathlib import Path
BASE_PATH = Path(__file__).resolve().parent

CONFIG_PATH = BASE_PATH / "console_config.json"

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(cfg, f)
    except:
        pass


# -----------------------------
# Page config (must be first)
# -----------------------------
st.set_page_config(
    page_title="Bot Console",
    page_icon="assets/Aleph.png",  # or .ico
    layout="centered"
)

# -----------------------------
# Session State Initialization
# -----------------------------
if "connected" not in st.session_state:
    st.session_state.connected = False

if "last_fail" not in st.session_state:
    st.session_state.last_fail = 0

if "force_refresh" not in st.session_state:
    st.session_state.force_refresh = 0

config_local = load_config()
access_key = config_local.get("access_key", None)

# -----------------------------
# Sidebar branding
# -----------------------------
hide_sidebar_fullscreen = """
<style>
button[title="View fullscreen"] {display: none !important;}
</style>
"""
st.markdown(hide_sidebar_fullscreen, unsafe_allow_html=True)

nutcracker_img = Image.open("assets/nutcracker.png")

st.sidebar.image(
    nutcracker_img,
    caption="Nutcracker — Aleph Strategy",
    width="stretch"
)
# -----------------------------
# Sidebar: Update Access Key
# -----------------------------
if access_key:
    with st.sidebar.expander("Update Access Key"):
        st.caption("If you received a new Access Key, you can update it here.")

        if st.button("Clear Stored Access Key"):
            st.warning("This will delete your current Access Key from the console. "
                       "Make sure you have your new key ready.")

            if st.button("Confirm Update Access Key"):
                # Clear from disk
                config_local["access_key"] = None
                save_config(config_local)

                # Clear from memory
                access_key = None

                # Clear from session state
                st.session_state.connected = False

                st.success("Access Key cleared. Please enter your new key.")
                st.rerun()


API_URL = "https://nutcrackerbot.com/api"

hide_deploy = """
<style>
button[kind="header"] {display: none !important;}
</style>
"""
st.markdown(hide_deploy, unsafe_allow_html=True)

# -----------------------------
# Safe Request Wrapper
# -----------------------------
def safe_request(method, url, **kwargs):
    try:
        kwargs["timeout"] = 3

        # Inject access key into headers
        headers = kwargs.get("headers", {})
        headers["X-Access-Key"] = access_key
        kwargs["headers"] = headers

        return method(url, **kwargs)
    except Exception:
        return None

# -----------------------------
# API Helpers
# -----------------------------
def fetch_status():
    r = safe_request(requests.get, f"{API_URL}/status")
    if r is None:
        return {"bot_state": "offline", "bot_attached": False}

    try:
        return r.json()
    except Exception:
        return {"bot_state": "offline", "bot_attached": False}


def fetch_config():
    r = safe_request(requests.get, f"{API_URL}/config")
    if r is None:
        return {}
    try:
        return r.json()
    except Exception:
        return {}

# -----------------------------
# UI: Connect Gate
# -----------------------------
st.title("Bot Control Console")

# -----------------------------
# Access Key Gate (first run)
# -----------------------------
if not access_key:
    st.warning("Enter your Access Key to continue.")

    entered_key = st.text_input("Access Key", type="password")

    if st.button("Save Access Key"):
        if entered_key.strip():
            config_local["access_key"] = entered_key.strip()
            save_config(config_local)
            st.success("Access Key saved. Restarting...")
            st.rerun()
        else:
            st.error("Access Key cannot be empty.")

    st.stop()

if not st.session_state.connected:
    st.warning("Not connected to bot server.")
    if st.button("Connect to Bot Server", key="btn_connect"):
        st.session_state.connected = True
        st.rerun()
    st.stop()
# -----------------------------
# Fetch Data (only when connected)
# -----------------------------
status = fetch_status()   # {"bot_state": "...", "bot_attached": ...}
bot_state = status.get("bot_state", "offline")
bot_attached = status.get("bot_attached", False)
# ---------------------------------------------
# Auto-initialize bot if keys exist but bot is uninitialized
# ---------------------------------------------
if bot_state == "uninitialized":
    r = safe_request(requests.get, f"{API_URL}/exchange_status")
    if r:
        ex = r.json()
        if ex.get("keys_loaded"):
            # Keys exist → initialize bot automatically
            init = safe_request(requests.post, f"{API_URL}/initialize_bot")
            if init and init.status_code == 200:
                st.rerun()


config = fetch_config()
symbols = config.get("symbols", [])
amounts_by_symbol = config.get("amounts_by_symbol", {})
raw_pnl = config.get("pnl_perc", 0.001)

try:
    raw_pnl = float(raw_pnl)
except Exception:
    raw_pnl = 0.001

safe_pnl = max(0.001, min(raw_pnl, 1.0))


# -----------------------------
# STATUS + MANUAL REFRESH
# -----------------------------
st.subheader("Bot Status")

resp = safe_request(requests.get, f"{API_URL}/status")

if not resp:
    bot_state = "offline"
    bot_attached = False
    raw_status = None
else:
    raw_status = resp.json()
    bot_state = raw_status.get("bot_state", "unknown")
    bot_attached = raw_status.get("bot_attached", False)

# Debug: show raw status so we see exactly what backend returns
with st.expander("Raw status (debug)", expanded=False):
    st.write(raw_status)

if bot_state == "running":
    st.success("🟢 Bot is running")
elif bot_state == "stopped":
    st.warning("🔴 Bot is stopped")
elif bot_state == "ready":
    st.info("🟡 Bot is initialized and ready to start")
elif bot_state == "uninitialized":
    st.info("⚪ Bot not initialized yet")
elif bot_state == "offline":
    st.error("⚠️ Bot server offline or unreachable")
else:
    st.error(f"⚠️ Bot status unknown: {bot_state}")

if st.button("Refresh Data", key="btn_refresh"):
    st.rerun()

# -----------------------------
# Bot Control
# -----------------------------
st.markdown("---")
st.subheader("Bot Control")

col1, col2, col3 = st.columns(3)

with col1:
    start_disabled = bot_state in ["uninitialized", "running", "offline", "unknown"]
    if st.button("Start Bot", key="start_bot", disabled=start_disabled):
        r = safe_request(requests.post, f"{API_URL}/start")
        if r:
            st.success(r.json().get("message", "No response"))
        else:
            st.error("Failed to reach server.")
        st.rerun()

with col2:
    stop_disabled = bot_state in ["uninitialized", "stopped", "offline", "unknown"]
    if st.button("Stop Bot", key="stop_bot", disabled=stop_disabled):
        r = safe_request(requests.post, f"{API_URL}/stop")
        if r:
            st.success(r.json().get("message", "No response"))
        else:
            st.error("Failed to reach server.")
        st.rerun()

with col3:
    restart_disabled = bot_state in ["offline", "unknown", "uninitialized"]
    if st.button("Restart Bot", key="restart_bot", disabled=restart_disabled):
        r = safe_request(requests.post, f"{API_URL}/restart")
        if r:
            st.success(r.json().get("message", "No response"))
        else:
            st.error("Failed to reach server.")
        st.rerun()

# -----------------------------
# Exchange Setup
# -----------------------------
st.markdown("---")

# Query backend for real key status
r = safe_request(requests.get, f"{API_URL}/exchange_status")
keys_loaded = False
exchange_name = None

if r:
    data = r.json()
    keys_loaded = data.get("keys_loaded", False)
    exchange_name = data.get("exchange")

with st.expander(
    "🔧 Exchange Setup and Keys",
    expanded=not keys_loaded
):
    if not keys_loaded:
        # Show input fields only when keys are NOT saved
        exchange = st.selectbox(
            "Exchange",
            ["binance", "bitget", "okx", "kucoin", "gateio", "mexc", "bybit"],
            key="exchange_select"
        )
        api_key = st.text_input("API Key", type="password", key="api_key")
        api_secret = st.text_input("API Secret", type="password", key="api_secret")
        api_password = st.text_input("API Password / Passphrase (optional)", type="password", key="api_password")

        if st.button("Save Exchange Settings", key="save_exchange"):
            payload = {
                "exchange": exchange,
                "api_key": api_key,
                "api_secret": api_secret,
                "api_password": api_password
            }
            r = safe_request(requests.post, f"{API_URL}/update_exchange_keys", json=payload)
            if r and r.status_code == 200:
                st.success("Exchange settings saved.")

                # Initialize bot
                r2 = safe_request(requests.post, f"{API_URL}/initialize_bot")
                if r2 and r2.status_code == 200:
                    st.success("Bot initialized. You can now start it.")
                else:
                    st.error("Failed to initialize bot. Check backend logs.")

                st.rerun()
            else:
                st.error("Failed to save exchange settings or reach server.")

    else:
        st.success(f"Exchange keys loaded and secured ({exchange_name}).")

        if st.button("Reset Keys", key="reset_exchange"):
            # Clear keys on backend
            payload = {
                "exchange": "",
                "api_key": "",
                "api_secret": "",
                "api_password": ""
            }
            safe_request(requests.post, f"{API_URL}/update_exchange_keys", json=payload)
            st.rerun()

# -----------------------------
# Trading Setup (Symbols, Amounts, PnL)
# -----------------------------
st.markdown("---")
st.subheader("Trading Setup")

with st.expander("⚙️ Symbols, Amounts & PnL", expanded=False):

    MAX_SLOTS = 9
    symbol_slots = []
    amount_slots = []

    # -----------------------------------------
    # Prefill symbols + amounts from backend
    # -----------------------------------------
    for i in range(MAX_SLOTS):
        default_symbol = symbols[i] if i < len(symbols) else ""
        default_amount = (
            amounts_by_symbol.get(default_symbol, 0.0)
            if default_symbol else 0.0
        )

        cols = st.columns([2, 1])

        with cols[0]:
            symbol = st.text_input(
                f"Symbol {i+1}",
                value=default_symbol,
                key=f"symbol_{i}",
                disabled=(bot_state == "running"),
                help="Format: BTC/USDT, BTCUSDT, BTC-USDT"
            )

        with cols[1]:
            amount = st.number_input(
                f"Amount {i+1}",
                min_value=0.0001,
                value=float(default_amount or 1.0),
                step=0.001,
                format="%.3f",
                key=f"amount_{i}",
                disabled=(bot_state == "running"),
                help="Amount in base currency (e.g., BTC for BTC/USDT)"
            )

        symbol_slots.append(symbol.strip().upper())
        amount_slots.append(amount)

    # -----------------------------------------
    # PnL percentage handling (backend → UI → backend)
    # -----------------------------------------

    # 1. Load backend value safely
    raw_pnl = config.get("pnl_perc", 0.02)

    try:
        raw_pnl = float(raw_pnl)
    except Exception:
        raw_pnl = 0.02  # fallback

    # 2. Validate range (decimal form)
    if raw_pnl < 0.001 or raw_pnl > 0.20:
        raw_pnl = 0.02  # default to 2%

    # 3. Convert to percentage for UI
    pnl_percent = raw_pnl * 100.0

    # 4. User input (percentage)
    new_pnl_percent = st.number_input(
        "PnL threshold (%)",
        min_value=0.1,
        max_value=20.0,
        step=0.1,
        format="%.1f",
        value=pnl_percent,
        key="pnl_input",
        disabled=(bot_state == "running")
    )

    st.caption(
        "Minimal profit per trade. Must cover exchange fees. "
        "Typical range: 1%–4%."
    )

    # 5. Convert back to decimal for backend
    new_pnl_decimal = round(new_pnl_percent / 100.0, 6)


    # -----------------------------------------
    # Save buttons
    # -----------------------------------------

    if bot_state == "running":
        st.caption("PnL and trading pairs are locked while the bot is running.")

    else:
        col_cfg1, col_cfg2 = st.columns(2)

        # ---- Save Symbols + Amounts ----
        with col_cfg1:
            if st.button("Save All Trading Pairs", key="save_pairs"):
                valid_pairs = [
                    (s, a) for s, a in zip(symbol_slots, amount_slots)
                    if s != ""
                ]

                if not valid_pairs:
                    st.warning("At least one valid trading pair is required.")
                else:
                    payload = {
                        "symbols": [s for s, _ in valid_pairs],
                        "amounts_by_symbol": {s: a for s, a in valid_pairs}
                    }

                    r = safe_request(
                        requests.post,
                        f"{API_URL}/update_all_symbols",
                        json=payload
                    )

                    if r:
                        try:
                            msg = r.json().get("message", "Symbols updated.")
                        except Exception:
                            msg = "Symbols updated."
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error("Failed to reach server while updating symbols.")

        # ---- Save PnL ----
        with col_cfg2:
            if st.button("Update PnL percentage", key="update_pnl_btn"):
                r = safe_request(
                    requests.post,
                    f"{API_URL}/update_pnl",
                    json={"pnl_perc": new_pnl_decimal}
                )

                if r:
                    try:
                        msg = r.json().get("message", "PnL updated.")
                    except Exception:
                        msg = "PnL updated."
                    st.success(msg)
                else:
                    st.error("Failed to reach server while updating PnL.")


# -----------------------------
# Live Bot Log
# -----------------------------
st.markdown("---")
st.subheader("📜 Bot Log")

# Initialize session state for bot log
if "bot_log_text" not in st.session_state:
    st.session_state.bot_log_text = ""

def refresh_bot_log():
    log_response = safe_request(requests.get, f"{API_URL}/logs?lines=100")
    if log_response:
        st.session_state.bot_log_text = log_response.json().get("logs", "")
    else:
        st.session_state.bot_log_text = "Unable to fetch logs."

# Load initial log only once
if st.session_state.bot_log_text == "":
    refresh_bot_log()

log_key = f"log_display_{st.session_state.force_refresh}"

# Display the text area (created ONCE)
st.text_area(
    "Bot Output",
    st.session_state.bot_log_text,
    height=300,
    key=log_key
)


# Refresh button (updates session_state only)
if st.button("🔄 Refresh Bot Log", key="refresh_bot_log"):
    refresh_bot_log()
    st.session_state.force_refresh += 1
    st.rerun()


# -----------------------------
# PnL Trigger
# -----------------------------
st.markdown("---")
st.subheader("PnL Trigger")

lookback_days = st.number_input(
    "Lookback days",
    min_value=7,
    max_value=365,
    value=30,
    step=1,
    key="lookback_days"
)

if st.button("Run PnL Job", key="run_pnl_job"):
    r = safe_request(
        requests.post,
        f"{API_URL}/run_pnl",
        json={"lookback_days": int(lookback_days)}
    )
    if r:
        st.success(r.json().get("message", "No response"))
    else:
        st.error("Failed to reach server.")

    st.caption(
        "PnL generation may take several minutes depending on exchange response times. "
        "If the PnL log does not update for more than 10 minutes, you may safely terminate the job."
    )

if st.button("Terminate PnL Job"):
    requests.post(API_URL + "/stop_pnl")
    st.success("PnL stop requested.")

# Last PnL log update timestamp
resp = safe_request(requests.get, f"{API_URL}/pnl_last_update")
if resp and resp.json().get("timestamp"):
    ts = resp.json()["timestamp"]
    dt = datetime.datetime.fromtimestamp(ts)
    st.write(f"**Last PnL log update:** {dt.strftime('%Y-%m-%d %H:%M:%S')}")
else:
    st.write("No PnL logs found.")

# -----------------------------
# PnL Snapshot
# -----------------------------
st.markdown("---")
st.subheader("PnL Snapshot (latest log)")

if "pnl_snapshot_text" not in st.session_state:
    st.session_state.pnl_snapshot_text = ""

if "pnl_last_ts" not in st.session_state:
    st.session_state.pnl_last_ts = None


def check_pnl_finished():
    r = safe_request(requests.get, f"{API_URL}/pnl_last_update")
    if not r:
        return None
    return r.json().get("timestamp", None)


def refresh_pnl_snapshot():
    r = safe_request(requests.get, f"{API_URL}/pnl_snapshot")
    if r:
        st.session_state.pnl_snapshot_text = r.json().get("log", "")
    else:
        st.session_state.pnl_snapshot_text = "Failed to load PnL snapshot."


# -----------------------------
# Auto-check if PnL finished
# -----------------------------
if st.session_state.pnl_last_ts is None:
    ts = check_pnl_finished()
    if ts:
        st.session_state.pnl_last_ts = ts
        refresh_pnl_snapshot()


# -----------------------------
# Display snapshot
# -----------------------------
st.text_area(
    "PnL Snapshot Output",
    st.session_state.pnl_snapshot_text,
    height=300,
    key="pnl_snapshot_display"
)

# Manual refresh
if st.button("🔄 Refresh PnL Snapshot", key="refresh_pnl_snapshot"):
    refresh_pnl_snapshot()

st.caption(
    "Start balances are reconstructed from trade history. Futures, options, and exchange-run trading bots "
    "are not included. Deposits and withdrawals are shown as flows and do not reflect margin transfers "
    "or collateral movements between wallets."
)



# -----------------------------
# Footer
# -----------------------------
st.markdown(
    """
    <hr>
    <div style='text-align:center; padding-top:10px; font-size:14px; opacity:0.7;'>
        Mutual AI–Human Collaboration • 
        <a href="https://alephstrategy.net" target="_blank">Aleph Strategy</a>
    </div>
    """,
    unsafe_allow_html=True
)
