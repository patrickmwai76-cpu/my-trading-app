import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hmac
from datetime import datetime
import pytz

# --- 1. THE GATEKEEPER (SECURITY) ---
def check_password():
    def credentials_entered():
        # Validates against the Secrets you put in Streamlit Cloud
        if (st.session_state["username"] == st.secrets["username"] and 
            hmac.compare_digest(st.session_state["password"], st.secrets["password"])):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    # Dark Login UI
    st.markdown('<h1 style="color:#00ff00; text-align:center;">🛡️ PATRO AI PRO</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:white; text-align:center;">RESTRICTED ACCESS TERMINAL</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.text_input("User Identity", key="username", placeholder="Enter Username")
        st.text_input("Command Key", type="password", key="password", placeholder="Enter Password")
        st.button("INITIALIZE SYSTEM", on_click=credentials_entered, use_container_width=True)
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("🚫 AUTHENTICATION FAILED: INVALID CREDENTIALS")
    return False

# --- 2. CONFIGURATION & THEME ---
st.set_page_config(page_title="PATRO AI PRO | US30", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117 !important; }
    [data-testid="stMetric"] {
        background-color: #1e2130 !important; 
        border: 2px solid #00ff00 !important;
        border-radius: 12px !important;
        padding: 15px !important;
    }
    [data-testid="stMetricValue"] { color: #00ff00 !important; font-size: 28px !important; font-weight: 800 !important; }
    [data-testid="stMetricLabel"] { color: #ffffff !important; }
    .status-live { color: #00ff00; font-weight: bold; border: 1px solid #00ff00; padding: 5px 10px; border-radius: 5px; }
    .status-closed { color: #ff4b4b; font-weight: bold; border: 1px solid #ff4b4b; padding: 5px 10px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# Kill execution if not logged in
if not check_password():
    st.stop()

# --- 3. MARKET STATUS LOGIC ---
def get_market_status():
    now_utc = datetime.now(pytz.utc)
    ny_time = now_utc.astimezone(pytz.timezone('US/Eastern'))
    is_weekend = ny_time.weekday() >= 5
    is_hours = 9 <= ny_time.hour < 16 or (ny_time.hour == 16 and ny_time.minute == 0)
    
    if is_weekend:
        return '<span class="status-closed">🔴 MARKET CLOSED (WEEKEND)</span>'
    elif not is_hours:
        return '<span class="status-closed">🔴 MARKET CLOSED (AFTER HOURS)</span>'
    else:
        return '<span class="status-live">🟢 MARKET LIVE (NEW YORK)</span>'

# --- 4. SIDEBAR (RISK & REFRESH) ---
with st.sidebar:
    st.markdown("<h2 style='color: #00ff00;'>🛠️ CONTROL PANEL</h2>", unsafe_allow_html=True)
    if st.button("🔄 REFRESH DATA", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    st.subheader("💰 Risk Calculator")
    balance = st.number_input("Balance ($)", value=1000, step=100)
    risk_pct = st.slider("Risk per Trade (%)", 0.5, 5.0, 1.0, 0.5)
    risk_amt = balance * (risk_pct / 100)
    st.success(f"Risk Amount: ${risk_amt:.2f}")
    st.divider()
    st.info("Signals are generated on the 1-minute timeframe for high-speed trading.")

# --- 5. THE DATA & RULES ENGINE ---
@st.cache_data(ttl=60)
def get_patro_data():
    # Fetching US30 (Dow Jones)
    df = yf.download("^DJI", period="1d", interval="1m")
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    
    # RULE: SMA 20 Trend
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    
    # RULE: RSI
