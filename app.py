import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hmac
from datetime import datetime

# --- 1. SYSTEM CONFIG & SECURITY ---
st.set_page_config(page_title="PATRO AI PRO", layout="wide", initial_sidebar_state="expanded")

def check_password():
    def credentials_entered():
        if (st.session_state["username"] == st.secrets["username"] and 
            hmac.compare_digest(st.session_state["password"], st.secrets["password"])):
            st.session_state["password_correct"] = True
            del st.session_state["username"]
            del st.session_state["password"]
        else: st.session_state["password_correct"] = False
    
    if st.session_state.get("password_correct", False): return True
    st.markdown("<h1 style='text-align:center; color:#00ff00;'>🛡️ PATRO AI PRO</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.text_input("Operator ID", key="username")
        st.text_input("Access Key", type="password", key="password")
        st.button("INITIALIZE TERMINAL", on_click=credentials_entered, use_container_width=True)
    return False

if not check_password(): st.stop()
# 1. Add the Selection Buttons in the sidebar
st.sidebar.divider()
st.sidebar.subheader("Select Timeframe")
# This creates a row of 3 buttons: 1m, 5m, and 15m
timeframe = st.sidebar.radio(
    "Chart Interval", 
    ["1m", "5m", "15m"], 
    index=2,      # Defaults to 15m
    horizontal=True
)

# 2. Tell the AI to download data based on your choice
df = yf.download("^DJI", period="1d", interval=timeframe)
def get_master_data():
    df = yf.download("^DJI", period="1d", interval="1m", progress=False)
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    
    # Technicals
    df['TP'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['PV'] = df['TP'] * df['Volume']
    df['VWAP'] = df['PV'].cumsum() / df['Volume'].cumsum()
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    
    # Signals
    df['Trend'] = 0
    df.loc[df['Close'] > df['EMA20'], 'Trend'] = 1
    df.loc[df['Close'] < df['EMA20'], 'Trend'] = -1
    df['Entry'] = df['Trend'].diff()
    return df

@st.cache_data(ttl=60)
def get_mtf(ticker, interval):
    try:
        data = yf.download(ticker, period="2d", interval=interval, progress=False)
        data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
        sma = data['Close'].rolling(window=20).mean()
        return "UP" if data['Close'].iloc[-1] > sma.iloc[-1] else "DOWN"
    except: return "N/A"

df = get_master_data()
t1, t5, t15 = get_mtf("^DJI", "1m"), get_mtf("^DJI", "5m"), get_mtf("^DJI", "15m")
sig = "BUY" if df['Trend'].iloc[-1] == 1 else "SELL"
sig_color = "#00ff00" if sig == "BUY" else "#ff4b4b"

# --- 3. HEADER & NEWS ---
st.markdown(f"""<div style="background-color:#1e2130; padding:15px; border-radius:10px; border-left: 10px solid {sig_color};">
    <h1 style="margin:0; color:#ffffff; font-size:28px;">🛡️ PATRO AI PRO <span style="color:{sig_color};">| {sig} MODE</span></h1>
    <p style="margin:0; color:grey; font-size:12px;">Institutional Scalping Terminal v4.0</p></div>""", unsafe_allow_html=True)

st.markdown("<p style='margin-top:10px; color:#00ff00; font-weight:bold; font-size:12px;'>🛡️ NEWS GUARD ACTIVE</p>", unsafe_allow_html=True)
n1, n2 = st.columns(2)
n1.info("**Mon Mar 2** | ISM PMI (10:00 AM)")
n2.error("**Fri Mar 6** | NFP Jobs (08:30 AM)")
st.divider()

# --- 4. THE 3-LAYER CHART ---
fig = make_subplots(
    rows=3, cols=1, 
    shared_xaxes=True, 
    row_heights=[0.6, 0.2, 0.2], # Main Chart, Volume, RSI
    vertical_spacing=0.03
)

# LAYER 1: Main Chart
fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name='EMA 20', line=dict(color='orange', width=1.2)), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], name='VWAP', line=dict(color='#00d4ff', width=2, dash='dash')), row=1, col=1)

# Entry Tags
buys = df[df['Entry'] == 2]
fig.add_trace(go.Scatter(x=buys.index, y=buys['Low']*0.9998, mode='markers+text', text="BUY", marker=dict(color='#00ff00', size=12, symbol='triangle-up')), row=1, col=1)
sells = df[df['Entry'] == -2]
fig.add_trace(go.Scatter(x=sells.index, y=sells['High']*1.0002, mode='markers+text', text="SELL", marker=dict(color='#ff4b4b', size=12, symbol='triangle-down')), row=1, col=1)

# LAYER 2: Volume (Color-coded)
v_colors = ['#00ff00' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#ff4b4b' for i in range(len(df))]
fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color=v_colors, opacity=0.8), row=2, col=1)

# LAYER 3: RSI
fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#9b59b6')), row=3, col=1)
fig.add_hline(y=70, line_dash="dot", line_color="#ff4b4b", row=3, col=1)
fig.add_hline(y=30, line_dash="dot", line_color="#00ff00", row=3, col=1)

fig.update_layout(template='plotly_dark', height=800, xaxis_rangeslider_visible=False, showlegend=False, margin=dict(l=10,r=10,t=10,b=10))
st.plotly_chart(fig, use_container_width=True)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color:#00ff00;'>🛡️ OPERATOR SOP</h2>", unsafe_allow_html=True)
    c1 = st.checkbox("Trend Matrix Confluence?")
    c2 = st.checkbox("Price Action near VWAP?")
    c3 = st.checkbox("News Guard is CLEAR?")
    c4 = st.checkbox("Risk Management set?")
    
    if all([c1, c2, c3, c4]): st.success("✅ READY TO TRADE")
    else: st.warning("⚠️ STANDBY")

    st.divider()
    st.markdown("### 📊 TREND MATRIX")
    for l, v in [("1M", t1), ("5M", t5), ("15M", t15)]:
        col_code = "#00ff00" if v == "UP" else "#ff4b4b"
        st.markdown(f"<div style='border:1px solid {col_code}; padding:8px; border-radius:5px; margin-bottom:5px; color:{col_code}; font-size:12px;'><strong>{l}: {v}</strong></div>", unsafe_allow_html=True)
    
    if st.button("🔄 FULL REFRESH"):
        st.cache_data.clear()
        st.rerun()
