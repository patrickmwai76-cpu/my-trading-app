import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hmac
from datetime import datetime
import pytz

# --- 1. SECURITY & CONFIG ---
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

st.set_page_config(page_title="PATRO AI PRO", layout="wide", initial_sidebar_state="expanded")
if not check_password(): st.stop()

# --- 2. MARKET STATUS & NEWS GUARD DATA ---
def get_market_status():
    ny_tz = pytz.timezone('US/Eastern')
    ny_now = datetime.now(ny_tz)
    if ny_now.weekday() >= 5: return "🔴 MARKET CLOSED (WEEKEND)", "#ff4b4b"
    if ny_now.hour < 9 or (ny_now.hour == 9 and ny_now.minute < 30) or ny_now.hour >= 16:
        return "🟠 MARKET CLOSED (AFTER HOURS)", "#ffa500"
    return "🟢 MARKET LIVE (NEW YORK)", "#00ff00"

news_alerts = [
    {"Day": "Mon Mar 2", "Time": "10:00 AM", "Event": "ISM Manufacturing PMI", "Level": "🔥 HIGH"},
    {"Day": "Wed Mar 4", "Time": "08:15 AM", "Event": "ADP Jobs Report", "Level": "🔥 HIGH"},
    {"Day": "Fri Mar 6", "Time": "08:30 AM", "Event": "Non-Farm Payrolls (NFP)", "Level": "💣 CRITICAL"}
]

# --- 3. THE FIXED HEADER (NEWS GUARD) ---
# This creates a solid block at the top so it's the first thing you see
with st.container():
    st.markdown("<h2 style='color:#00ff00; margin-bottom:5px;'>🛡️ PATRO AI NEWS GUARD</h2>", unsafe_allow_html=True)
    cols = st.columns(len(news_alerts))
    for i, news in enumerate(news_alerts):
        with cols[i]:
            st.success(f"**{news['Day']} @ {news['Time']}**\n\n{news['Event']}")

st.divider()

# --- 4. DATA FETCHING ---
@st.cache_data(ttl=60)
def get_data():
    df = yf.download("^DJI", period="1d", interval="1m")
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    df['Trend'] = 0
    df.loc[df['Close'] > df['SMA20'], 'Trend'] = 1
    df.loc[df['Close'] < df['SMA20'], 'Trend'] = -1
    df['Entry'] = df['Trend'].diff()
    return df

df = get_data()
status_text, status_color = get_market_status()
sig = "BUY" if df['Trend'].iloc[-1] == 1 else "SELL"
sig_c = "#00ff00" if sig == "BUY" else "#ff4b4b"

# LIVE SIGNAL & MARKET STATUS
c1, c2 = st.columns([2, 1])
with c1:
    st.markdown(f"<h1 style='color:{sig_c};'>LIVE SIGNAL: {sig}</h1>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div style='border:2px solid {status_color}; color:{status_color}; padding:10px; border-radius:10px; text-align:center; font-weight:bold;'>{status_text}</div>", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown("<h2 style='color:#00ff00;'>🛠️ CONTROL</h2>", unsafe_allow_html=True)
    if st.button("🔄 REFRESH SYSTEM"): st.rerun()
    st.divider()
    bal = st.number_input("Balance ($)", value=1000)
    risk = st.slider("Risk (%)", 0.5, 5.0, 1.0)
    st.error(f"Trade Risk: ${bal * (risk/100):.2f}")

# CHART
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)
fig.add
