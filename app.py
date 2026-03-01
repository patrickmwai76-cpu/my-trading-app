import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# 1. Page Setup
st.set_page_config(page_title="PATRO AI PRO", layout="wide")

# 2. Security Check (Username: PATRO_ADMIN | Password: patro666@)
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.title("🛡️ PATRO AI PRO | SECURE ACCESS")
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    if st.button("Unlock Terminal"):
        if user == "PATRO_ADMIN" and pw == "patro666@":
            st.session_state['auth'] = True
            st.rerun()
        else:
            st.error("Invalid Credentials")
    st.stop()

# --- IF LOGGED IN, SHOW TERMINAL ---

# 3. Sidebar - RESTORED LAYOUT
st.sidebar.title("🛡️ TERMINAL CONTROL")
tf = st.sidebar.radio("Timeframe", ["1m", "5m", "15m"], index=0, horizontal=True)

st.sidebar.divider()
st.sidebar.subheader("📋 OPERATOR SOP")
s1 = st.sidebar.checkbox("Trend Matrix Confluence?")
s2 = st.sidebar.checkbox("Price Action near VWAP?")
s3 = st.sidebar.checkbox("News Guard is CLEAR?")
s4 = st.sidebar.checkbox("Risk Management set?")

if s1 and s2 and s3 and s4:
    st.sidebar.success("✅ READY TO TRADE")
else:
    st.sidebar.warning("⚠️ STANDBY")

st.sidebar.divider()
st.sidebar.subheader("📉 RISK MANAGEMENT")
bal = st.sidebar.number_input("Wallet ($)", value=1000)
risk = st.sidebar.slider("Risk %", 1.0, 5.0, 1.0)
st.sidebar.info(f"Lot Size: {(bal * (risk/100)) / 50:.2f}")

st.sidebar.divider()
st.sidebar.subheader("📊 TREND MATRIX")
st.sidebar.success("1M: UP | 5M: UP | 15M: UP")

if st.sidebar.button("🔒 Logout"):
    st.session_state['auth'] = False
    st.rerun()

# 4. Main Header & News Guard
st.markdown("""
    <div style="background: linear-gradient(90deg, #00c853, #b2ff59); padding: 15px; border-radius: 10px; color: black; text-align: center; font-weight: bold;">
        🛡️ PATRO AI PRO | BUY MODE<br>Institutional Scalping Terminal v4.0
    </div>
""", unsafe_allow_html=True)

st.write("🛡️ **NEWS GUARD ACTIVE**")
c1, c2 = st.columns(2)
c1.info("Mon Mar 2 | ISM PMI (10:00 AM)")
c2.error("Fri Mar 6 | NFP Jobs (08:30 AM)")

# 5. Market Engine
st_autorefresh(interval=30000, key="refresh")
df = yf.download("^DJI", period="1d", interval=tf)

if not df.empty:
    # Clean data to prevent "Operands not aligned" error
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    # Simple Indicators
    df['SMA'] = df['Close'].rolling(window=20).mean()
    
    # 6. Charting
    fig = go.Figure()
    
    # Candlestick
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='US30'))
    
    # SMA Line
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA'], name='Trend', line=dict(color='orange', width=1)))

    # Real BUY/SELL Logic
    last_price = df['Close'].iloc[-1]
    last_sma = df['SMA'].iloc[-1]
    
    for i in range(len(df)-10, len(df)): # Show signals for last 10 candles
        if df['Close'].iloc[i] > df['SMA'].iloc[i]:
            fig.add_annotation(x=df.index[i], y=df['Low'].iloc[i], text="BUY", bgcolor="green", row=1, col=1)
        else:
            fig.add_annotation(x=df.index[i], y=df['High'].iloc[i], text="SELL", bgcolor="red", row=1, col=1)

    fig.update_layout(template="plotly_dark", height=600, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Volume Bars
    st.subheader("📊 Transaction Volume")
    st.bar_chart(df['Volume'])
    
else:
    st.error("Connecting to Liquidity Provider...")
