import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hmac
from datetime import datetime
import pytz

# --- 1. PRO CONFIG & SECURITY ---
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
    
    # Professional Login Portal
    st.markdown("<h1 style='text-align:center; color:#00ff00;'>🛡️ PATRO AI PRO</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:grey;'>Institutional Grade Scalping Terminal</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.text_input("Operator ID", key="username")
        st.text_input("Access Key", type="password", key="password")
        st.button("INITIALIZE TERMINAL", on_click=credentials_entered, use_container_width=True)
    return False

if not check_password(): st.stop()

# --- 2. DATA ENGINE ---
@st.cache_data(ttl=60)
def get_institutional_data():
    df = yf.download("^DJI", period="1d", interval="1m", progress=False)
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    
    # Signal Logic
    df['Trend'] = 0
    df.loc[df['Close'] > df['EMA20'], 'Trend'] = 1
    df.loc[df['Close'] < df['EMA20'], 'Trend'] = -1
    df['Entry'] = df['Trend'].diff()
    return df

@st.cache_data(ttl=60)
def get_mtf(ticker, interval):
    data = yf.download(ticker, period="2d", interval=interval, progress=False)
    data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
    return "UP" if data['Close'].iloc[-1] > data['Close'].rolling(20).mean().iloc[-1] else "DOWN"

# --- 3. SYSTEM CORE ---
df = get_institutional_data()
t1, t5, t15 = get_mtf("^DJI", "1m"), get_mtf("^DJI", "5m"), get_mtf("^DJI", "15m")
sig = "BUY" if df['Trend'].iloc[-1] == 1 else "SELL"
sig_color = "#00ff00" if sig == "BUY" else "#ff4b4b"

# --- 4. TOP COMMAND HEADER ---
st.markdown(f"""
    <div style="background-color:#1e2130; padding:20px; border-radius:15px; border-left: 10px solid {sig_color}; margin-bottom:20px;">
        <h1 style="margin:0; color:#ffffff; font-size:32px;">🛡️ PATRO AI PRO <span style="color:{sig_color};">| {sig} MODE</span></h1>
        <p style="margin:0; color:grey; font-size:14px;">Market: Dow Jones Industrial Average (US30) | Status: Operational</p>
    </div>
""", unsafe_allow_html=True)

h1, h2, h3, h4 = st.columns(4)
h1.metric("LIVE PRICE", f"${df['Close'].iloc[-1]:,.2f}")
h2.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.2f}")
h3.metric("MTF TREND", f"{t1}/{t5}/{t15}")
h4.metric("SYSTEM VOL", f"{int(df['Volume'].iloc[-1]):,}")

st.divider()

# --- 5. CHARTING ENGINE ---
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.75, 0.25], vertical_spacing=0.03)

# Main Price & EMA
fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df['EMA20'], name='EMA 20', line=dict(color='orange', width=1.5)), row=1, col=1)

# GainzAlgo Labels
buys = df[df['Entry'] == 2]
fig.add_trace(go.Scatter(x=buys.index, y=buys['Low'] * 0.9998, mode='markers+text', text="BUY", 
                         textposition="bottom center", marker=dict(color='#00ff00', size=12, symbol='triangle-up')), row=1, col=1)

sells = df[df['Entry'] == -2]
fig.add_trace(go.Scatter(x=sells.index, y=sells['High'] * 1.0002, mode='markers+text', text="SELL", 
                         textposition="top center", marker=dict(color='#ff4b4b', size=12, symbol='triangle-down')), row=1, col=1)

# RSI Subplot
fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#9b59b6')), row=2, col=1)
fig.add_hline(y=70, line_dash="dot", line_color="#ff4b4b", row=2, col=1)
fig.add_hline(y=30, line_dash="dot", line_color="#00ff00", row=2, col=1)

fig.update_layout(template='plotly_dark', height=750, xaxis_rangeslider_visible=False, showlegend=False, 
                  margin=dict(l=20, r=20, t=0, b=20))
st.plotly_chart(fig, use_container_width=True)

# --- 6. SIDEBAR INTELLIGENCE ---
with st.sidebar:
    st.markdown("<h3 style='color:#00ff00;'>📊 TREND MATRIX</h3>", unsafe_allow_html=True)
    for l, v in [("1M", t1), ("5M", t5), ("15M", t15)]:
        c = "#00ff00" if v == "UP" else "#ff4b4b"
        st.markdown(f"<div style='border:1px solid {c}; padding:10px; border-radius:5px; margin-bottom:10px;'><h4 style='margin:0; color:{c};'>{l}: {v}</h4></div>", unsafe_allow_html=True)
    
    st.divider()
    st.markdown("### 🛠️ CONTROLS")
    if st.button("🔄 FULL REFRESH"):
        st.cache_data.clear()
        st.rerun()
