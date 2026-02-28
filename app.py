import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hmac

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

# --- 2. DATA ENGINE (CLEAN) ---
@st.cache_data(ttl=60)
def get_clean_data():
    df = yf.download("^DJI", period="1d", interval="1m", progress=False)
    # Fix multi-index columns if they exist
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    # EMA 20 Calculation
    df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
    # RSI Calculation
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    return df

df = get_clean_data()

# --- 3. SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("<h2 style='color:#00ff00;'>📊 TERMINAL</h2>", unsafe_allow_html=True)
    st.info("Market: US30 (DJI)")
    st.divider()
    if st.button("🔄 REFRESH SYSTEM"):
        st.cache_data.clear()
        st.rerun()

# --- 4. TOP METRICS ---
# Logic for the big Signal header
last_price = df['Close'].iloc[-1]
last_ema = df['EMA20'].iloc[-1]
sig = "BUY" if last_price > last_ema else "SELL"
sig_color = "#00ff00" if sig == "BUY" else "#ff4b4b"

st.markdown(f"<h1 style='text-align:center; color:{sig_color};'>SIGNAL: {sig}</h1>", unsafe_allow_html=True)

m1, m2, m3 = st.columns(3)
m1.metric("US30 PRICE", f"${last_price:,.2f}")
m2.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.2f}")
m3.metric("EMA 20", f"${last_ema:,.2f}")

# --- 5. THE CHART (REBUILT FOR STABILITY) ---
# Create a 2-row layout: Price on top, RSI on bottom
fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)

# Main Candlestick Chart
fig.add_trace(go.Candlestick(
    x=df.index, 
    open=df['Open'], 
    high=df['High'], 
    low=df['Low'], 
    close=df['Close'], 
    name='Price'
), row=1, col=1)

# EMA 20 Overlay
fig.add_trace(go.Scatter(
    x=df.index, 
    y=df['EMA20'], 
    name='EMA 20', 
    line=dict(color='orange', width=2)
), row=1, col=1)

# RSI Indicator
fig.add_trace(go.Scatter(
    x=df.index, 
    y=df['RSI'], 
    name='RSI', 
    line=dict(color='purple', width=1)
), row=2, col=1)

# Add RSI Overbought/Oversold levels
fig.add_hline(y=70, line_dash="dot", line_
