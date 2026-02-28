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

# --- 2. DEFINE ALL VARIABLES FIRST (PREVENTS ERRORS) ---
# Set defaults so the sidebar doesn't crash
if 'balance' not in st.session_state: st.session_state.balance = 1000.0
if 'risk_pct' not in st.session_state: st.session_state.risk_pct = 1.0

# --- 3. DATA ENGINES ---
@st.cache_data(ttl=60)
def get_mtf_trend(ticker, interval):
    try:
        data = yf.download(ticker, period="2d", interval=interval, progress=False)
        data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
        sma = data['Close'].rolling(window=20).mean()
        return "UP" if data['Close'].iloc[-1] > sma.iloc[-1] else "DOWN"
    except: return "N/A"

@st.cache_data(ttl=60)
def get_main_data():
    df = yf.download("^DJI", period="1d", interval="1m", progress=False)
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    df['SMA20'] = df['Close'].rolling(window=20).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    # Calculate Targets (Institutional 1:2 Ratio)
    last_price = df['Close'].iloc[-1]
    df['TP'] = last_price + 50 if last_price > df['SMA20'].iloc[-1] else last_price - 50
    df['SL'] = last_price - 25 if last_price > df['SMA20'].iloc[-1] else last_price + 25
    return df

# PRE-LOAD DATA
t1, t5, t15 = get_mtf_trend("^DJI", "1m"), get_mtf_trend("^DJI", "5m"), get_mtf_trend("^DJI", "15m")
df = get_main_data()

# --- 4. SIDEBAR (CONTROLS) ---
with st.sidebar:
    st.markdown("<h2 style='color:#00ff00;'>📊 TREND MATRIX</h2>", unsafe_allow_html=True)
    for label, val in [("1 MIN", t1), ("5 MIN", t5), ("15 MIN", t15)]:
        color = "#00ff00" if val == "UP" else "#ff4b4b"
        st.markdown(f"<div style='border:1px solid {color}; padding:8px; border-radius:5px; margin-bottom:5px;'><p style='margin:0; font-size:10px;'>{label}</p><h4 style='margin:0; color:{color};'>{val}</h4></div>", unsafe_allow_html=True)
    
    st.divider()
    bal = st.number_input("Balance ($)", value=st.session_state.balance)
    risk = st.slider("Risk (%)", 0.1, 5.0, st.session_state.risk_pct)
    risk_usd = bal * (risk/100)
    st.error(f"⚠️ Cash Risk: ${risk_usd:.2f}")
    
    if st.button("🔄 REFRESH SYSTEM"):
        st.cache_data.clear()
        st.rerun()

# --- 5. MAIN DASHBOARD ---
st.markdown("<h3 style='color:#00ff00;'>🛡️ NEWS GUARD</h3>", unsafe_allow_html=True)
n1, n2 = st.columns(2)
n1.info("**Mon Mar 2 @ 10:00 AM**\n\nISM Manufacturing PMI")
n2.info("**Fri Mar 6 @ 08:30 AM**\n\nNon-Farm Payrolls (NFP)")
st.divider()

sig = "BUY" if df['Close'].iloc[-1] > df['SMA20'].iloc[-1] else "SELL"
sig_color = "#00ff00" if sig == "BUY" else "#ff4b4b"

st.markdown(f"<h1 style='text-align:center; color:{sig_color};'>SIGNAL: {sig}</h1>", unsafe_allow_html=True)

m1, m2, m3 = st.columns(3)
m1.metric("US30 PRICE", f"${df['Close'].iloc[-1]:,.2f}")
m2.metric("TP (TARGET)", f"${df['TP'].iloc[-1]:,.2f}")
m3.metric("SL (PROTECT)", f"${df['SL'].iloc[-1]:,.2f}")

# CHART
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.8, 0.2])
fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['SMA20'], name='EMA 20', line=dict(color='orange')), row=1, col=1)
# TP/SL Visual Lines
fig.add_hline(y=df['TP'].iloc[-1], line_dash="dot", line_color="green", annotation_text="TAKE PROFIT", row=1, col=1)
fig.add_hline(y=df['SL'].iloc[-1], line_dash="dot", line_color="red", annotation_text="STOP LOSS", row=1, col=1)

fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')), row=2, col=1)
fig.update_layout(template='plotly_dark', height=700, xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)
