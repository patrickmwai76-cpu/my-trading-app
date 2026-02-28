import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hmac
from datetime import datetime
import pytz

# --- 1. SECURITY ---
def check_password():
    def credentials_entered():
        if (st.session_state["username"] == st.secrets["username"] and 
            hmac.compare_digest(st.session_state["password"], st.secrets["password"])):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else: st.session_state["password_correct"] = False
    if st.session_state.get("password_correct", False): return True
    st.markdown('<h1 style="color:#00ff00; text-align:center;">🛡️ PATRO AI PRO</h1>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.text_input("User Identity", key="username")
        st.text_input("Command Key", type="password", key="password")
        st.button("INITIALIZE SYSTEM", on_click=credentials_entered, use_container_width=True)
    return False

st.set_page_config(page_title="PATRO AI PRO", layout="wide")
if not check_password(): st.stop()

# --- 2. DATA ENGINE ---
@st.cache_data(ttl=60)
def get_mtf_trend(ticker, interval):
    data = yf.download(ticker, period="2d", interval=interval, progress=False)
    data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
    sma = data['Close'].rolling(window=20).mean()
    curr_close = data['Close'].iloc[-1]
    curr_sma = sma.iloc[-1]
    return "UP" if curr_close > curr_sma else "DOWN"

@st.cache_data(ttl=60)
def get_main_data():
    df = yf.download("^DJI", period="1d", interval="1m", progress=False)
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    df['Trend'] = 0
    df.loc[df['Close'] > df['SMA20'], 'Trend'] = 1
    df.loc[df['Close'] < df['SMA20'], 'Trend'] = -1
    df['Entry'] = df['Trend'].diff()
    return df

# --- 3. MARKET STATUS & NEWS ---
news_alerts = [
    {"Day": "Mon Mar 2", "Time": "10:00 AM", "Event": "ISM PMI", "Lvl": "🔥 HIGH"},
    {"Day": "Fri Mar 6", "Time": "08:30 AM", "Event": "NFP Jobs", "Lvl": "💣 CRITICAL"}
]

# --- 4. UI BUILDING ---
# NEWS GUARD TOP BANNER
with st.container():
    st.markdown("<h3 style='color:#00ff00;'>🛡️ NEWS GUARD ALERTS</h3>", unsafe_allow_html=True)
    cols = st.columns(len(news_alerts))
    for i, n in enumerate(news_alerts):
        cols[i].warning(f"**{n['Day']} @ {n['Time']}**\n\n{n['Event']} ({n['Lvl']})")

st.divider()

# SIDEBAR: TREND MATRIX & RISK
with st.sidebar:
    st.markdown("<h2 style='color:#00ff00;'>📊 TREND MATRIX</h2>", unsafe_allow_html=True)
    t1 = get_mtf_trend("^DJI", "1m")
    t5 = get_mtf_trend("^DJI", "5m")
    t15
